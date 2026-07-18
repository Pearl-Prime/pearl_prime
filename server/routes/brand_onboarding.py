"""
Brand Onboarding Submit API — the brand wizard's "Activate" lands the signup in Pearl Prime.

Powers brand-wizard-app BrandWizard Activate. The wizard matches the admin's choices to a
unified brand (config/brand_management/global_brand_registry_unified.yaml — 39×14) and POSTs
the generated YAML here. This endpoint LOGS the submission and ASSIGNS it to the brand.

Endpoint:
  POST /api/v1/onboarding/submit  — {brand_id, lane, publication_corp, brand_email, contact,
                                      wizard_yaml, match_score, match_basis}

Persistence (ALL under artifacts/onboarding/, ALL gitignored — these carry the admin's email;
emails never enter committed files, per the brand-wizard privacy discipline):
  - submissions/<YYYY-MM-DD>/<brand_id>__<email-slug>.yaml   the full submission (logged)
  - submissions_log.tsv                                      append-only index
  - roster_assignments.yaml                                  the assignment overlay (status:
        assigned + admin name/email), keyed by brand_id. The committed roster template
        config/brand_management/brand_admin_users.yaml is NOT mutated (preserves its comments
        + keeps PII out of git); the backend reads this overlay for live assignment state.
"""
from __future__ import annotations

import logging
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])

REPO_ROOT = Path(__file__).resolve().parents[2]
UNIFIED_REGISTRY = REPO_ROOT / "config" / "brand_management" / "global_brand_registry_unified.yaml"
# Generated SSOT the wizard's client matcher (brand-wizard-app/src/brandMatch.js) reads:
# per brand_id it carries arch (archetype base), lane, and buildable (catalog-bearing?).
# A brand is "catalog-bearing" iff its entry here has buildable != false — the SAME signal
# the client matcher gates on (brandMatch.js: `b.buildable !== false`), so server == client.
BRANDS_INDEX_JSON = REPO_ROOT / "brand-wizard-app" / "public" / "brand_admin_brands.json"
BRAND_DIRECTOR_ASSIGNMENTS_YAML = (
    REPO_ROOT / "config" / "brand_management" / "brand_director_assignments.yaml"
)
ONBOARDING_DIR = REPO_ROOT / "artifacts" / "onboarding"
SUBMISSIONS_DIR = ONBOARDING_DIR / "submissions"
LOG_TSV = ONBOARDING_DIR / "submissions_log.tsv"
ASSIGNMENTS_YAML = ONBOARDING_DIR / "roster_assignments.yaml"
# Teacher 1:1 exclusivity ledger (gitignored, alongside the other onboarding overlays).
# A teacher brand is a real person's voice — only ONE admin may claim it. Keyed by
# "<lane>__<teacher_tid>" so the claim survives even if the same teacher slug appears in
# multiple lanes (each lane is its own brand). The committed roster is never mutated.
TEACHER_CLAIMS_YAML = ONBOARDING_DIR / "teacher_claims.yaml"

_BRAND_RE = re.compile(r"^[a-z0-9][a-z0-9_]{0,127}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.replace(tmp, str(path))
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise


def _valid_brand_ids() -> set[str]:
    try:
        import yaml
        data = yaml.safe_load(UNIFIED_REGISTRY.read_text(encoding="utf-8")) or {}
        return set((data.get("brands") or {}).keys())
    except Exception as e:  # registry missing in some envs → skip strict check, log
        logger.warning("unified registry unavailable for validation: %s", e)
        return set()


def _brands_index() -> Dict[str, dict]:
    """The generated brand_id -> {arch, lane, buildable, ...} map (same SSOT the client matcher uses).

    Fail-open: returns {} if the file is missing/unparseable, so the buildability gate and the
    archetype fallback simply no-op in stripped-down envs (mirrors _valid_brand_ids' tolerance).
    """
    try:
        import json
        data = json.loads(BRANDS_INDEX_JSON.read_text(encoding="utf-8")) or {}
        return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.warning("brands index unavailable for buildability gate: %s", e)
        return {}


def _is_catalog_bearing(brand_id: str, index: Dict[str, dict]) -> bool:
    """A brand is catalog-bearing iff its index entry has buildable != false.

    Unknown brand_id (no entry) → False (fail-closed). Catalog membership alone must not
    imply shippable/available books; only an explicit buildable entry may pass.
    Empty index (stripped env) → False so availability never invents phantom catalogs.
    """
    if not index:
        return False
    entry = index.get(brand_id)
    if not isinstance(entry, dict):
        return False
    return entry.get("buildable") is not False


def available_downloadable_assets(delivery: Optional[dict]) -> list:
    """Return ONLY real downloadable production assets from a brand_deliveries payload.

    Catalog metadata / planned titles / production-pending scaffolds are excluded.
    A missing or empty delivery → []. Callers must treat [] as the empty state
    ("no titles available yet"), never invent placeholder book counts.
    """
    if not isinstance(delivery, dict):
        return []
    if delivery.get("production_files_ready") is False:
        return []
    status = str(delivery.get("delivery_status") or "").strip().lower()
    if status == "catalog_ready_production_files_pending" or "production_files_pending" in status.replace(
        " ", "_"
    ):
        return []
    weeks = delivery.get("weeks")
    if not isinstance(weeks, dict) or not weeks:
        return []
    out: list = []
    for week in sorted(weeks.keys()):
        platforms = weeks.get(week) or {}
        if not isinstance(platforms, dict):
            continue
        for platform, files in platforms.items():
            if platform == "catalog_metadata":
                continue
            if not isinstance(files, list):
                continue
            for item in files:
                if not isinstance(item, dict):
                    continue
                if item.get("production_files_ready") is False:
                    continue
                url = str(item.get("url") or "").strip()
                filename = str(item.get("file") or "").strip()
                if not url or not filename:
                    continue
                if filename.lower().endswith((".md", ".cue")):
                    continue
                out.append(
                    {
                        "week": week,
                        "platform": platform,
                        "file": filename,
                        "url": url,
                        "kb": item.get("kb"),
                    }
                )
    return out


def _assignment_records(path: Path) -> Dict[str, dict]:
    try:
        import yaml
        if not path.exists():
            return {}
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        records = data.get("assignments") if isinstance(data, dict) else None
        return records if isinstance(records, dict) else {}
    except Exception as e:
        logger.warning("assignment overlay unreadable (%s): %s", path, e)
        return {}


def _is_assigned_record(record: object) -> bool:
    if not isinstance(record, dict):
        return False
    status = str(record.get("brand_director_status") or record.get("status") or "").strip().lower()
    return (
        status in {"assigned", "claimed"}
        or bool(str(record.get("brand_director_name") or record.get("admin_name") or "").strip())
        or bool(str(record.get("brand_director_id") or "").strip())
        or bool(str(record.get("admin_email") or "").strip())
    )


def _assignment_conflict(brand_id: str, index: Dict[str, dict]) -> Optional[dict]:
    """Return a public-safe conflict record if brand_id is already assigned.

    Checks every assignment source the local wizard can see: the generated public brand
    index, committed operator assignments, and gitignored live local onboarding overlay.
    """
    index_entry = index.get(brand_id)
    if _is_assigned_record(index_entry):
        return {
            "source": "brand_admin_brands",
            "brand_id": brand_id,
            "assigned_to": (index_entry or {}).get("brand_director_name"),
        }
    for source, path in [
        ("brand_director_assignments", BRAND_DIRECTOR_ASSIGNMENTS_YAML),
        ("local_roster_assignments", ASSIGNMENTS_YAML),
    ]:
        record = _assignment_records(path).get(brand_id)
        if _is_assigned_record(record):
            return {
                "source": source,
                "brand_id": brand_id,
                "assigned_to": (record or {}).get("brand_director_name") or (record or {}).get("admin_name"),
            }
    return None


def _teacher_identity(brand_id: str, index: Dict[str, dict]) -> Optional[tuple[str, str]]:
    """If brand_id is a teacher brand, return (lane, teacher_tid); else None.

    Derived server-side from the SAME index the client matcher reads — the server is
    authoritative, so the client does not need to send is_teacher/teacher_tid (and an
    older/forged client cannot bypass the 1:1 rule). Unknown brand -> None (no claim).
    """
    entry = index.get(brand_id)
    if not isinstance(entry, dict) or not entry.get("is_teacher"):
        return None
    tid = str(entry.get("tid") or "").strip()
    lane = str(entry.get("lane") or "").strip()
    if not tid:
        return None
    return (lane or "unknown_lane", tid)


def _teacher_claims() -> Dict[str, dict]:
    """Load the gitignored teacher-claim ledger ({claims: {"<lane>__<tid>": {...}}}).

    FAIL-OPEN by contract: any read/parse error returns {} so a legitimate sign-up is
    never blocked on a missing/corrupt ledger — the caller treats {} as "no prior claim".
    """
    try:
        import yaml
        if not TEACHER_CLAIMS_YAML.exists():
            return {}
        data = yaml.safe_load(TEACHER_CLAIMS_YAML.read_text(encoding="utf-8")) or {}
        claims = data.get("claims") if isinstance(data, dict) else None
        return claims if isinstance(claims, dict) else {}
    except Exception as e:
        logger.error("teacher-claim ledger unreadable (fail-open, allowing submit): %s", e)
        return {}


def _record_teacher_claim(key: str, brand_id: str, email: str, ts: str) -> None:
    """Upsert a teacher claim. Best-effort: a write failure must not break the submit
    (the submission itself is already persisted by the caller); log and move on."""
    try:
        import yaml
        overlay: Dict[str, dict] = {}
        if TEACHER_CLAIMS_YAML.exists():
            try:
                overlay = yaml.safe_load(TEACHER_CLAIMS_YAML.read_text(encoding="utf-8")) or {}
            except Exception:
                overlay = {}
        if not isinstance(overlay, dict):
            overlay = {}
        overlay.setdefault("claims", {})
        overlay["claims"][key] = {
            "brand_id": brand_id, "email": email or None, "ts": ts,
        }
        _atomic_write(TEACHER_CLAIMS_YAML, yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True))
    except Exception as e:
        logger.error("failed to record teacher claim %s for %s: %s", key, brand_id, e)


def _resolve_archetype_to_brand(token: str, lane: Optional[str], index: Dict[str, dict]) -> Optional[str]:
    """Fallback: resolve a bare archetype base (e.g. 'stillness_press') to a concrete,
    catalog-bearing brand_id, preferring the requested lane.

    Returns None if no catalog-bearing brand carries that archetype. Used only when the posted
    brand_id is not itself a direct registry key (so an archetype-only input still lands a signup
    on a real, buildable brand instead of 422-failing).
    """
    if not token or not index:
        return None
    want_lane = (lane or "").strip()
    matches = [
        (bid, entry) for bid, entry in index.items()
        if isinstance(entry, dict)
        and entry.get("arch") == token
        and entry.get("buildable") is not False
    ]
    if not matches:
        return None
    # Prefer an exact lane match, then fall back to the first catalog-bearing brand (sorted = stable).
    if want_lane:
        for bid, entry in sorted(matches):
            if (entry.get("lane") or "") == want_lane:
                return bid
    return sorted(matches)[0][0]


def _email_slug(email: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (email or "anon").lower()).strip("_")[:48] or "anon"


def _director_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (name or "").lower()).strip("_")[:80] or "brand_director"


def _base_brand_from_id(brand_id: str) -> str:
    return re.sub(r"_(en_us|es_us|es_es|fr_fr|de_de|it_it|hu_hu|pt_br|zh_tw|zh_hk|zh_cn|zh_sg|ja_jp|ko_kr)$", "", brand_id)


class OnboardingSubmission(BaseModel):
    brand_id: str = Field(..., min_length=1)        # matched unified brand_id, e.g. stillness_press_en_us
    lane: Optional[str] = None
    publication_corp: Optional[str] = None          # imprint name, e.g. "Stillness Press"
    base_brand: Optional[str] = None
    display_brand: Optional[str] = None
    brand_director_name: Optional[str] = None
    brand_director_id: Optional[str] = None
    brand_director_status: Optional[str] = None
    brand_email: Optional[str] = None
    contact: Optional[Dict[str, str]] = None        # first_name/last_name/phone/...
    wizard_yaml: str = Field(..., min_length=1)      # the generated brand-config YAML (text)
    match_score: Optional[float] = None
    match_basis: Optional[str] = None


@router.post("/submit")
def submit_onboarding(req: OnboardingSubmission) -> dict:
    """Log the wizard submission + assign it to the matched brand (gitignored overlay)."""
    brand_id = (req.brand_id or "").strip()
    if not _BRAND_RE.fullmatch(brand_id):
        raise HTTPException(status_code=422, detail="invalid brand_id")
    valid = _valid_brand_ids()
    index = _brands_index()
    # Archetype -> brand fallback: if the posted brand_id is NOT a concrete registry key, treat it
    # as a bare archetype base and resolve it to a real, catalog-bearing brand (preferring req.lane).
    # This keeps an archetype-only input from 422-failing; it lands on a buildable brand instead.
    if valid and brand_id not in valid:
        resolved = _resolve_archetype_to_brand(brand_id, req.lane, index)
        if resolved:
            logger.info("onboarding: archetype %r resolved to brand %s (lane=%s)", brand_id, resolved, req.lane)
            brand_id = resolved
        else:
            raise HTTPException(status_code=422, detail=f"brand_id not in unified registry: {brand_id}")
    # Catalog-bearing gate: never assign a signup to a brand that ships 0 items (buildable == false),
    # even on a direct POST. Same signal the client matcher gates on (brandMatch.js buildable != false).
    if not _is_catalog_bearing(brand_id, index):
        raise HTTPException(status_code=422, detail=f"brand_not_buildable: {brand_id}")
    conflict = _assignment_conflict(brand_id, index)
    if conflict:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "brand_claimed",
                "brand_id": brand_id,
                "assigned_to": conflict.get("assigned_to"),
                "source": conflict.get("source"),
            },
        )
    if len(req.wizard_yaml) > 200_000:
        raise HTTPException(status_code=422, detail="wizard_yaml too large")
    email = (req.brand_email or "").strip()
    if email and not _EMAIL_RE.fullmatch(email):
        raise HTTPException(status_code=422, detail="invalid brand_email")

    try:
        import yaml
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"pyyaml unavailable: {e}") from e

    now = datetime.now(timezone.utc)
    day = now.strftime("%Y-%m-%d")
    ts = now.isoformat(timespec="seconds")
    contact = req.contact or {}
    name = " ".join(x for x in [contact.get("first_name"), contact.get("last_name")] if x).strip()
    index_entry = index.get(brand_id) if isinstance(index.get(brand_id), dict) else {}
    director_name = (req.brand_director_name or name).strip()
    director_id = (req.brand_director_id or _director_slug(director_name)).strip()
    base_brand = (
        (req.base_brand or "").strip()
        or str(index_entry.get("arch") or "").strip()
        or _base_brand_from_id(brand_id)
    )
    display_brand = (
        (req.display_brand or "").strip()
        or (req.publication_corp or "").strip()
        or str(index_entry.get("d") or "").strip()
        or brand_id
    )
    director_status = (req.brand_director_status or "assigned").strip() or "assigned"
    public_assignment = {
        "brand_id": brand_id,
        "base_brand": base_brand,
        "display_brand": display_brand,
        "brand_director_name": director_name or None,
        "brand_director_id": director_id if director_name else None,
        "brand_director_status": director_status,
        "assigned_at": ts,
        "assignment_source": "brand_onboarding_wizard",
    }

    # 0. TEACHER 1:1 EXCLUSIVITY — a teacher brand is a real person's voice; only ONE admin
    # may claim it. The teacher identity (lane, tid) is derived server-side from the brands
    # index (authoritative; the client need not send it). If a claim already exists for this
    # teacher, return 409 — the client auto-falls back to a composite brand. FAIL-OPEN: any
    # ledger-read error allows the submit (never block a legitimate sign-up on infra errors).
    teacher = _teacher_identity(brand_id, index)
    teacher_claim_key: Optional[str] = None
    if teacher is not None:
        t_lane, t_tid = teacher
        teacher_claim_key = f"{t_lane}__{t_tid}"
        existing = _teacher_claims().get(teacher_claim_key)
        if isinstance(existing, dict) and existing.get("brand_id"):
            existing_email = (existing.get("email") or "").strip().lower()
            # Idempotent re-submit by the SAME admin -> not a conflict; fall through and re-log.
            if not (email and existing_email and email.lower() == existing_email):
                logger.info("teacher already claimed: key=%s brand=%s by=%s",
                            teacher_claim_key, existing.get("brand_id"), existing_email or "?")
                raise HTTPException(
                    status_code=409,
                    detail={"error": "teacher_claimed", "brand_id": existing.get("brand_id")},
                )

    # 1. LOG — write the full submission YAML (gitignored)
    sub_path = SUBMISSIONS_DIR / day / f"{brand_id}__{_email_slug(email)}.yaml"
    record = {
        "submitted_at": ts, "brand_id": brand_id, "lane": req.lane,
        "publication_corp": req.publication_corp, "brand_email": email,
        "contact": contact, "match_score": req.match_score, "match_basis": req.match_basis,
        "brand_assignment": public_assignment,
        "source": "brand_onboarding_wizard",
    }
    _atomic_write(sub_path, yaml.safe_dump(record, sort_keys=False, allow_unicode=True)
                  + "\n# ── wizard YAML ──\n" + req.wizard_yaml)

    # 2. LOG INDEX — append a TSV row (gitignored)
    if not LOG_TSV.exists():
        _atomic_write(LOG_TSV, "submitted_at\tbrand_id\tpublication_corp\temail\tname\tmatch_score\n")
    with LOG_TSV.open("a", encoding="utf-8") as fh:
        fh.write(f"{ts}\t{brand_id}\t{req.publication_corp or ''}\t{email}\t{name}\t{req.match_score or ''}\n")

    # 3. ASSIGN — upsert the gitignored roster-assignment overlay (committed roster untouched)
    overlay = {}
    if ASSIGNMENTS_YAML.exists():
        try:
            overlay = yaml.safe_load(ASSIGNMENTS_YAML.read_text(encoding="utf-8")) or {}
        except Exception:
            overlay = {}
    overlay.setdefault("assignments", {})
    overlay["assignments"][brand_id] = {
        "status": "assigned", "admin_name": name or None, "admin_email": email or None,
        "publication_corp": req.publication_corp, "assigned_at": ts,
        "brand_id": brand_id, "base_brand": base_brand, "display_brand": display_brand,
        "brand_director_name": director_name or None,
        "brand_director_id": director_id if director_name else None,
        "brand_director_status": director_status,
        "assigned_via": "brand_onboarding_wizard",
    }
    _atomic_write(ASSIGNMENTS_YAML, yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True))

    # 4. CLAIM — record the teacher claim AFTER the submission is durably persisted, so the
    # 1:1 lock reflects a real, logged sign-up. No-op for composite brands (teacher is None).
    if teacher_claim_key is not None:
        _record_teacher_claim(teacher_claim_key, brand_id, email, ts)

    logger.info("onboarding submit: brand=%s assigned=%s", brand_id, bool(name or email))
    return {
        "status": "submitted", "brand_id": brand_id, "assigned": True,
        "submission_path": str(sub_path.relative_to(REPO_ROOT)),
        "next": f"brand_admin.html?phase=3&brand={brand_id}",
    }
