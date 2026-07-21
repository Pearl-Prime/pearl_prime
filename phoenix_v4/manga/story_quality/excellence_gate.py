"""Story excellence realization gate — runtime proof of doctrine on the page.

Authority: docs/specs/MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md

Deterministic, no LLM, no network. Fail closed when production=True and
required doctrine is missing.
"""

from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any, Mapping

from phoenix_v4.manga.modern_reader_context import (
    canonical_genre_ids,
    load_modern_reader_doctrine,
    resolve_relevance_genre,
    validate_modern_reader_doctrine,
)
from phoenix_v4.manga.story_quality.text_extract import (
    full_script_text,
    metadata_only_blob,
    opening_pages_text,
    panel_reader_and_action_text,
)

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

REPO = Path(__file__).resolve().parents[3]
DEFAULT_GATES_CFG = REPO / "config" / "manga" / "story_excellence_gates.yaml"
DEFAULT_ALIAS_CFG = REPO / "config" / "manga" / "story_genre_alias_coherence.yaml"
DEFAULT_INTERACTION = REPO / "config" / "manga" / "main_character_interaction_grammar.yaml"
STRATEGY_DIR = REPO / "config" / "source_of_truth" / "manga_story_strategies"
CHAPTER_WRITER_PROMPT = REPO / "phoenix_v4" / "manga" / "prompts" / "chapter_writer_prompt.txt"

GATE_RESEARCH = "MANGA.STORY.RESEARCH_DOCTRINE_COVERAGE"
GATE_ARCHITECT = "MANGA.STORY.ARCHITECT_CONTEXT"
GATE_ALIAS = "MANGA.STORY.ALIAS_COHERENCE"
GATE_MODERN = "MANGA.STORY.MODERN_READER_REALIZATION"
GATE_GENRE = "MANGA.STORY.GENRE_CORE_PLEASURE"
GATE_INTERACT = "MANGA.STORY.INTERACTION_REALIZATION"
GATE_HOOK = "MANGA.STORY.PAGE_ONE_HOOK"
GATE_MARKET = "MANGA.STORY.MARKET_NATIVE_SURFACE"
GATE_BLAND = "MANGA.STORY.BLAND_FALLBACK_LINT"
GATE_REPAIR = "MANGA.STORY.REPAIR_PACKET"


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML required for story excellence gate")
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace("-", "_").replace(" ", "_")


def _contains_any(blob: str, needles: list[str] | tuple[str, ...]) -> list[str]:
    low = blob.lower()
    hits: list[str] = []
    for n in needles:
        if n is None:
            continue
        if not isinstance(n, str):
            n = str(n)
        if not n:
            continue
        if n.lower() in low:
            hits.append(n)
    return hits


def _gate(
    gate_id: str,
    *,
    status: str,
    score: int,
    threshold: int,
    blocking: bool,
    issues: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "status": status,
        "score": score,
        "threshold": threshold,
        "blocking": blocking,
        "issues": issues,
        "evidence": evidence,
    }


def _issue(code: str, message: str, **extra: Any) -> dict[str, Any]:
    out = {"code": code, "message": message}
    out.update(extra)
    return out


def _resolve_modern_context(
    story_handoff: Mapping[str, Any],
    writer_handoff: Mapping[str, Any],
    internal_record: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    for src in (
        writer_handoff.get("modern_reader_context"),
        story_handoff.get("modern_reader_context"),
        (internal_record or {}).get("modern_reader_context"),
    ):
        if isinstance(src, dict) and src:
            return dict(src)
    # chapter-level story_craft fallback
    chapters = story_handoff.get("chapters") or []
    if isinstance(chapters, list) and chapters and isinstance(chapters[0], dict):
        craft = chapters[0].get("story_craft") or {}
        mrc = craft.get("modern_reader_context")
        if isinstance(mrc, dict) and mrc:
            return dict(mrc)
    return None


def _identity_fields(
    story_handoff: Mapping[str, Any],
    writer_handoff: Mapping[str, Any],
    mrc: Mapping[str, Any] | None,
) -> dict[str, Any]:
    genre_id = _norm(
        str(
            (mrc or {}).get("genre_id")
            or writer_handoff.get("genre_id")
            or story_handoff.get("genre_id")
            or story_handoff.get("genre_family")
            or ""
        )
    )
    strategy_genre = _norm(
        str(
            (mrc or {}).get("strategy_genre")
            or writer_handoff.get("story_strategy_genre")
            or story_handoff.get("story_strategy_genre")
            or genre_id
        )
    )
    relevance = _norm(
        str(
            (mrc or {}).get("relevance_genre")
            or resolve_relevance_genre(genre_id, strategy_genre=strategy_genre)
        )
    )
    market = str(
        (mrc or {}).get("target_market")
        or story_handoff.get("reader_market")
        or writer_handoff.get("reader_market")
        or "en_US"
    )
    audience = str(
        (mrc or {}).get("target_audience")
        or story_handoff.get("reader_audience")
        or writer_handoff.get("reader_audience")
        or "gen_z"
    )
    return {
        "genre_id": genre_id,
        "strategy_genre": strategy_genre,
        "relevance_genre": relevance,
        "target_market": market,
        "target_audience": audience,
        "series_id": str(writer_handoff.get("series_id") or story_handoff.get("series_id") or ""),
        "chapter_id": str(writer_handoff.get("chapter_id") or ""),
        "chapter_number": int(writer_handoff.get("chapter_number") or story_handoff.get("chapter_number") or 1),
    }


def _check_research(
    *,
    ids: dict[str, Any],
    cfg: Mapping[str, Any],
    production: bool,
    repo_root: Path,
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    try:
        doctrine = load_modern_reader_doctrine()
        doc_errors = validate_modern_reader_doctrine(doctrine)
    except Exception as exc:  # fail closed
        doc_errors = [f"malformed_doctrine: {exc}"]
        doctrine = {}
    if doc_errors:
        issues.append(_issue("malformed_doctrine", "; ".join(doc_errors)))

    canonical = set(canonical_genre_ids())
    relevance = ids["relevance_genre"]
    if relevance not in canonical:
        issues.append(
            _issue(
                "missing_modern_reader_genre_row",
                f"relevance_genre {relevance!r} not in canonical 25",
            )
        )
    else:
        evidence.append({"path": "config/manga/canonical_genre_list.yaml", "text": relevance, "reason": "canonical genre"})

    markets = set(cfg.get("reader_markets") or ["en_US", "ja_JP", "zh_CN", "fr_FR"])
    audiences = set(cfg.get("reader_audiences") or ["gen_z", "gen_alpha"])
    if ids["target_market"] not in markets:
        issues.append(_issue("invalid_reader_market", f"market {ids['target_market']!r}"))
    if ids["target_audience"] not in audiences:
        issues.append(_issue("invalid_reader_audience", f"audience {ids['target_audience']!r}"))

    genre_row = (doctrine.get("genres") or {}).get(relevance) if doctrine else None
    if not isinstance(genre_row, dict):
        issues.append(_issue("missing_modern_reader_genre_row", f"no doctrine row for {relevance}"))
    else:
        catalysts = genre_row.get("catalysts") or []
        if len(catalysts) < 2:
            issues.append(_issue("missing_catalysts", "need >=2 catalysts"))
        for key in ("relevance_rule",):
            if not genre_row.get(key):
                issues.append(_issue("missing_relevance_rule", key))
        if catalysts and isinstance(catalysts[0], dict):
            for key in ("ordinary_world_objects", "genre_transmutation", "avoid"):
                if not catalysts[0].get(key):
                    issues.append(_issue(f"missing_{key}", f"catalyst missing {key}"))

    bank_map = cfg.get("strategy_bank_by_genre") or {}
    bank_name = bank_map.get(relevance) or bank_map.get(ids["genre_id"])
    bank_path = (repo_root / "config/source_of_truth/manga_story_strategies" / bank_name) if bank_name else None
    if not bank_path or not bank_path.is_file():
        issues.append(_issue("missing_strategy_bank_or_alias", f"no strategy bank for {relevance}"))
    else:
        evidence.append({"path": str(bank_path.relative_to(repo_root)), "text": bank_name, "reason": "strategy bank"})

    ig_path = repo_root / "config/manga/main_character_interaction_grammar.yaml"
    try:
        ig = _load_yaml(ig_path)
        if relevance not in (ig.get("genres") or {}):
            issues.append(_issue("missing_interaction_grammar", f"no grammar for {relevance}"))
        else:
            evidence.append({"path": "config/manga/main_character_interaction_grammar.yaml", "text": relevance, "reason": "interaction grammar"})
    except Exception as exc:
        issues.append(_issue("missing_interaction_grammar", str(exc)))

    status = "PASS" if not issues else "BLOCKED"
    if not production and status == "BLOCKED":
        # research coverage still hard — production flag only softens architect-less smoke
        pass
    return _gate(
        GATE_RESEARCH,
        status=status,
        score=100 if status == "PASS" else 0,
        threshold=100,
        blocking=True,
        issues=issues,
        evidence=evidence,
    )


def _check_architect(
    story_handoff: Mapping[str, Any],
    writer_handoff: Mapping[str, Any],
    mrc: Mapping[str, Any] | None,
    *,
    production: bool,
    repo_root: Path,
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    if not isinstance(story_handoff.get("modern_reader_context"), dict):
        issues.append(_issue("missing_modern_reader_context", "story_architecture_handoff.modern_reader_context missing"))
    else:
        evidence.append({"path": "story_architecture_handoff.modern_reader_context", "text": "present", "reason": "architect context"})

    chapters = story_handoff.get("chapters") or []
    if isinstance(chapters, list) and chapters:
        for i, ch in enumerate(chapters):
            if not isinstance(ch, dict):
                continue
            craft = ch.get("story_craft")
            if not isinstance(craft, dict):
                issues.append(_issue("missing_story_craft", f"chapters[{i}].story_craft missing"))
                continue
            if not isinstance(craft.get("modern_reader_context"), dict):
                issues.append(
                    _issue(
                        "missing_modern_reader_context",
                        f"chapters[{i}].story_craft.modern_reader_context missing",
                    )
                )
    elif production:
        # some fixtures are chapter-only; require mrc on handoff or writer
        if mrc is None:
            issues.append(_issue("missing_story_craft", "no chapters and no modern_reader_context"))

    if mrc is None and not isinstance(writer_handoff.get("modern_reader_context"), dict):
        issues.append(_issue("missing_modern_reader_context", "no modern_reader_context on writer or story"))

    # market/audience preserved
    sm = story_handoff.get("reader_market") or (story_handoff.get("modern_reader_context") or {}).get("target_market")
    sa = story_handoff.get("reader_audience") or (story_handoff.get("modern_reader_context") or {}).get("target_audience")
    if mrc and sm and str(sm) != str(mrc.get("target_market")):
        issues.append(_issue("reader_market_dropped_in_transmission", f"{sm} vs {mrc.get('target_market')}"))
    if mrc and sa and str(sa) != str(mrc.get("target_audience")):
        issues.append(_issue("reader_audience_dropped_in_transmission", f"{sa} vs {mrc.get('target_audience')}"))

    prompt_path = repo_root / "phoenix_v4/manga/prompts/chapter_writer_prompt.txt"
    if prompt_path.is_file():
        prompt = prompt_path.read_text(encoding="utf-8")
        if "modern_reader_context" not in prompt:
            issues.append(_issue("chapter_writer_prompt_missing_doctrine", "prompt lacks modern_reader_context"))
        else:
            evidence.append({"path": "phoenix_v4/manga/prompts/chapter_writer_prompt.txt", "text": "modern_reader_context", "reason": "prompt doctrine"})
    elif production:
        issues.append(_issue("chapter_writer_prompt_missing_doctrine", "prompt file missing"))

    status = "PASS" if not issues else "BLOCKED"
    return _gate(GATE_ARCHITECT, status=status, score=100 if status == "PASS" else 0, threshold=100, blocking=True, issues=issues, evidence=evidence)


def _check_alias(ids: dict[str, Any], alias_cfg: Mapping[str, Any], writer_handoff: Mapping[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    rows = alias_cfg.get("aliases") or []
    match = None
    for row in rows:
        if _norm(str(row.get("canonical_genre") or "")) == ids["relevance_genre"] or _norm(
            str(row.get("canonical_genre") or "")
        ) == ids["genre_id"]:
            match = row
            break
    if match is None:
        issues.append(_issue("unresolved_alias", f"no alias row for {ids['genre_id']}/{ids['relevance_genre']}"))
    else:
        strat_ok = ids["strategy_genre"] in {_norm(x) for x in (match.get("allowed_strategy_genres") or [])}
        rel_ok = ids["relevance_genre"] in {_norm(x) for x in (match.get("allowed_relevance_genres") or [])}
        if not strat_ok or not rel_ok:
            issues.append(
                _issue(
                    "alias_mismatch",
                    f"({ids['genre_id']}, {ids['strategy_genre']}, {ids['relevance_genre']}) not allowed",
                )
            )
        else:
            evidence.append(
                {
                    "path": "config/manga/story_genre_alias_coherence.yaml",
                    "text": ids["relevance_genre"],
                    "reason": "alias coherence",
                }
            )
        vessel = _norm(str(writer_handoff.get("vessel_genre") or writer_handoff.get("mode_vessel_genre") or ""))
        if vessel:
            allowed_v = {_norm(x) for x in (match.get("allowed_vessel_genres") or [])}
            if vessel not in allowed_v:
                issues.append(_issue("vessel_alias_mismatch", f"vessel {vessel!r} not allowed"))

    status = "PASS" if not issues else "BLOCKED"
    return _gate(GATE_ALIAS, status=status, score=100 if status == "PASS" else 0, threshold=100, blocking=True, issues=issues, evidence=evidence)


def _check_modern_realization(
    writer_handoff: Mapping[str, Any],
    mrc: Mapping[str, Any] | None,
    cfg: Mapping[str, Any],
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    opening, opening_ev = opening_pages_text(writer_handoff, max_pages=2)
    opening_low = opening.lower()
    meta = metadata_only_blob(writer_handoff).lower()
    full = full_script_text(writer_handoff).lower()

    if mrc is None:
        issues.append(_issue("missing_modern_reader_context", "cannot realize catalyst without context"))
        return _gate(GATE_MODERN, status="BLOCKED", score=0, threshold=100, blocking=True, issues=issues, evidence=evidence)

    catalyst = mrc.get("catalyst") if isinstance(mrc.get("catalyst"), dict) else {}
    objects = [str(o) for o in (catalyst.get("ordinary_world_objects") or []) if o]
    # also accept market touchpoints as approved surfaces
    touch = [str(t) for t in (mrc.get("market_touchpoints") or []) if t]
    candidates = objects + touch
    # normalize multiword + simple tokens
    object_hits: list[tuple[str, dict[str, Any]]] = []
    for obj in candidates:
        token = str(obj).lower().replace("_", " ")
        # also try last word (app, phone, train)
        alts = {token, token.split()[-1] if token.split() else token}
        for alt in alts:
            if len(alt) < 3:
                continue
            if alt in opening_low:
                # must not be metadata-only: require panel path evidence
                for ev in opening_ev:
                    if alt in ev["text"].lower():
                        object_hits.append((alt, ev))
                        break
                break

    if not object_hits:
        issues.append(
            _issue(
                "modern_object_absent_from_opening",
                f"no catalyst/touchpoint object in first 1-2 pages; looked for {candidates[:6]}",
            )
        )
    else:
        for alt, ev in object_hits[:3]:
            evidence.append({**ev, "reason": f"selected catalyst object appears in page-one action ({alt})"})

    # Object must change conflict — conflict signals near opening text
    conflict_signals = list(cfg.get("conflict_change_signals") or [])
    conflict_hits = _contains_any(opening, conflict_signals)
    # Shallow mention patterns that must fail even if object present
    shallow_patterns = [
        r"looked at (her|his|their) phone\.?\s+something shifted",
        r"the train arrived and .+ adventure began",
        r"opened an app and entered",
        r"a group chat existed",
    ]
    shallow = False
    for pat in shallow_patterns:
        if re.search(pat, opening_low):
            shallow = True
            issues.append(_issue("shallow_modern_mention", f"shallow pattern matched: {pat}"))
            break

    if object_hits and not conflict_hits and not shallow:
        issues.append(
            _issue(
                "modern_object_does_not_change_conflict",
                "ordinary-world object appears but does not create pressure/choice/cost/rule/reversal",
            )
        )
    elif object_hits and conflict_hits:
        evidence.append(
            {
                "path": "pages[0:2]",
                "text": ", ".join(conflict_hits[:5]),
                "reason": "object creates conflict-change pressure",
            }
        )

    # genre_transmutation visible
    transmutation = str(catalyst.get("genre_transmutation") or "").lower()
    trans_tokens = [t for t in re.split(r"[^a-z0-9_]+", transmutation) if len(t) >= 5][:8]
    if trans_tokens and not _contains_any(opening + " " + full, trans_tokens):
        # softer: look for debt/oath/rule/wound family if dark fantasy etc.
        if not conflict_hits:
            issues.append(
                _issue(
                    "genre_transmutation_absent",
                    "genre_transmutation not visible as action/dialogue/consequence",
                )
            )

    # Metadata-only failure: catalyst objects appear in craft/meta text but none
    # of them (or their significant tokens) appear in opening panel action.
    if objects and not object_hits:
        issues.append(
            _issue(
                "modern_object_metadata_only",
                "catalyst objects present in metadata/title/prompt but not in page action",
            )
        )

    desire_hits = _contains_any(opening, list(cfg.get("desire_signals") or []))
    if not desire_hits:
        issues.append(_issue("protagonist_desire_missing", "no visible protagonist desire before heavy lore"))
    else:
        evidence.append({"path": "pages[0:2]", "text": desire_hits[0], "reason": "protagonist desire visible"})

    cost_hits = _contains_any(opening, list(cfg.get("cost_signals") or []))
    if not cost_hits:
        issues.append(_issue("cost_missing_by_page_two", "no social/system/body/relationship cost by page two"))
    else:
        evidence.append({"path": "pages[0:2]", "text": cost_hits[0], "reason": "cost by page two"})

    status = "PASS" if not issues else "BLOCKED"
    return _gate(GATE_MODERN, status=status, score=100 if status == "PASS" else 0, threshold=100, blocking=True, issues=issues, evidence=evidence)


def _check_genre_core(
    writer_handoff: Mapping[str, Any],
    ids: dict[str, Any],
    mrc: Mapping[str, Any] | None,
    cfg: Mapping[str, Any],
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    opening, _ = opening_pages_text(writer_handoff, max_pages=2)
    full = full_script_text(writer_handoff)
    blob = (opening + " " + full).lower()
    genre = ids["relevance_genre"] or ids["genre_id"]
    core_map = (cfg.get("genre_core_evidence") or {}).get(genre) or {}
    hit_classes: list[str] = []
    for class_name, needles in core_map.items():
        hits = _contains_any(blob, list(needles))
        if hits:
            hit_classes.append(class_name)
            evidence.append(
                {
                    "path": "pages[*]",
                    "text": hits[0],
                    "reason": f"genre-core class {class_name}",
                }
            )
    if len(hit_classes) < 2:
        issues.append(
            _issue(
                "genre_core_insufficient",
                f"{genre} needs >=2 evidence classes; found {hit_classes}",
                required=list(core_map.keys()),
                found=hit_classes,
            )
        )

    forbidden = (cfg.get("forbidden_replacements") or {}).get(genre) or []
    for phrase in forbidden:
        if phrase.lower() in blob:
            issues.append(_issue("forbidden_genre_replacement", f"{phrase!r} present"))

    avoid = []
    if mrc and isinstance(mrc.get("catalyst"), dict):
        avoid = [str(a) for a in (mrc["catalyst"].get("avoid") or []) if a]
    for a in avoid:
        token = a.lower().replace("_", " ")
        if token and token in blob:
            issues.append(_issue("catalyst_avoid_present", f"avoid item {a!r} appears in script"))

    status = "PASS" if not issues else "BLOCKED"
    return _gate(GATE_GENRE, status=status, score=100 if status == "PASS" else max(0, len(hit_classes) * 40), threshold=100, blocking=True, issues=issues, evidence=evidence)


def _check_interaction(
    writer_handoff: Mapping[str, Any],
    ids: dict[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    ig = _load_yaml(repo_root / "config/manga/main_character_interaction_grammar.yaml")
    genre = ids["relevance_genre"] or ids["genre_id"]
    row = (ig.get("genres") or {}).get(genre) or {}
    blob = full_script_text(writer_handoff).lower()
    opening, _ = opening_pages_text(writer_handoff, max_pages=2)

    # interaction targets
    targets = {
        "dyad": ["you", "we", "her", "him", "them", "together", "beside"],
        "rival": ["rival", "opponent", "against"],
        "group": ["team", "class", "group", "club", "crowd"],
        "authority": ["boss", "coach", "teacher", "commander", "elder", "manager"],
        "family": ["mother", "father", "sister", "brother", "family", "parent"],
        "machine": ["cockpit", "machine", "interface", "ai", "system", "app"],
        "self": ["mirror", "memory", "my body", "myself", "shadow"],
        "care": ["patient", "nurse", "doctor", "caregiver"],
    }
    found_targets = [name for name, needles in targets.items() if _contains_any(blob, needles)]
    solo_only_genres = {"essay", "memoir", "battle_internal", "healing", "slice_of_life"}
    if not found_targets:
        issues.append(_issue("main_character_never_interacts", "no interaction target evidence"))
    else:
        evidence.append({"path": "pages[*]", "text": ",".join(found_targets[:4]), "reason": "interaction targets"})

    # genre-specific hard fails
    if genre == "romance" and "dyad" not in found_targets:
        issues.append(_issue("romance_no_dyad_pressure", "romance requires dyad pressure"))
    if genre == "sports" and not ({"rival", "group"} & set(found_targets)):
        issues.append(_issue("sports_no_team_or_rival_axis", "sports needs team/rival axis"))
    if genre == "mecha" and "machine" not in found_targets and "authority" not in found_targets:
        issues.append(_issue("mecha_no_machine_or_command_interaction", "mecha needs machine/command"))
    if genre == "social_issue" and "family" not in found_targets and "care" not in found_targets and "authority" not in found_targets:
        issues.append(_issue("social_issue_no_named_relationship", "social issue needs named relationship/power axis"))

    # solo narration without compensating artifact
    multi_speaker = False
    for page in writer_handoff.get("pages") or []:
        if not isinstance(page, dict):
            continue
        for panel in page.get("panels") or []:
            if not isinstance(panel, dict):
                continue
            speakers = set()
            for line in panel.get("dialogue_lines") or []:
                if isinstance(line, dict) and line.get("speaker"):
                    speakers.add(str(line["speaker"]))
            dlg = panel.get("dialogue")
            if isinstance(dlg, list):
                for d in dlg:
                    if isinstance(d, dict) and d.get("speaker"):
                        speakers.add(str(d["speaker"]))
            if len(speakers) >= 2:
                multi_speaker = True
    if not multi_speaker and genre not in solo_only_genres:
        # allow if machine/system/self interaction present
        if not ({"machine", "self", "authority", "group", "rival"} & set(found_targets)):
            issues.append(_issue("main_character_never_interacts", "only solo narration without compensating interaction"))

    # quality_gate_checks from grammar if present
    for check in row.get("quality_gate_checks") or []:
        if isinstance(check, str) and len(check) > 3:
            # soft: record as evidence expectation; hard only if clearly interaction-related keywords absent
            pass

    # declare multi-character panels when present
    for page_i, page in enumerate(writer_handoff.get("pages") or []):
        if not isinstance(page, dict):
            continue
        for panel_i, panel in enumerate(page.get("panels") or []):
            if not isinstance(panel, dict):
                continue
            chars = panel.get("characters") or panel.get("character_ids") or []
            if isinstance(chars, list) and len(chars) >= 2:
                evidence.append(
                    {
                        "path": f"pages[{page_i}].panels[{panel_i}]",
                        "text": ",".join(str(c) for c in chars[:4]),
                        "reason": "multi-character interaction scene declared",
                    }
                )

    # ensure opening had some relational pressure for non-solo genres
    if genre not in solo_only_genres and not _contains_any(opening.lower(), ["you", "we", "rival", "team", "boss", "app", "debt", "chat"]):
        if "dyad" not in found_targets and "group" not in found_targets:
            issues.append(_issue("interaction_pressure_missing_opening", "opening lacks relational/system pressure"))

    status = "PASS" if not issues else "BLOCKED"
    return _gate(GATE_INTERACT, status=status, score=100 if status == "PASS" else 0, threshold=100, blocking=True, issues=issues, evidence=evidence)


def _check_page_one_hook(writer_handoff: Mapping[str, Any], cfg: Mapping[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    opening, opening_ev = opening_pages_text(writer_handoff, max_pages=2)
    pages = list(writer_handoff.get("pages") or [])
    page1 = " "
    page2 = " "
    if pages:
        p0 = pages[0] if isinstance(pages[0], dict) else {}
        page1 = " ".join(panel_reader_and_action_text(p) for p in (p0.get("panels") or []) if isinstance(p, dict))
    if len(pages) > 1 and isinstance(pages[1], dict):
        page2 = " ".join(
            panel_reader_and_action_text(p) for p in (pages[1].get("panels") or []) if isinstance(p, dict)
        )

    mood_only = re.fullmatch(
        r"[\s\w,.'\"]*(sky|rain|wind|morning|evening|quiet|stillness|atmosphere)[\s\w,.'\"]*",
        page1.lower(),
    )
    abstract_only = len(re.findall(r"\b(feel|feeling|emotion|theme|destiny|fate)\b", page1.lower())) >= 2 and len(
        page1.split()
    ) < 25
    if not page1.strip():
        issues.append(_issue("page_one_empty", "page one has no concrete text"))
    elif mood_only or abstract_only:
        issues.append(_issue("page_one_mood_only", "opening is only mood/weather/abstract theme"))
    else:
        # concrete image/pressure/question/contradiction/action
        concrete = bool(
            re.search(r"\b(phone|app|train|door|desk|seat|blood|message|feed|ticket|rival|debt|chat)\b", page1.lower())
            or "?" in page1
            or _contains_any(page1, list(cfg.get("conflict_change_signals") or [])[:20])
        )
        if not concrete and len(page1.split()) < 8:
            issues.append(_issue("page_one_no_concrete_hook", "page one lacks concrete image/pressure/question"))
        else:
            evidence.append({"path": "pages[0]", "text": page1[:200], "reason": "page-one concrete hook"})

    turn_signals = list(cfg.get("hook_signals") or [])
    if page2.strip() and not _contains_any(page2, turn_signals) and "?" not in page2:
        # allow conflict signals as turn reason
        if not _contains_any(page2, list(cfg.get("conflict_change_signals") or [])):
            issues.append(
                _issue(
                    "page_two_no_turn_reason",
                    "page two lacks reversal/discovery/promise/threat/misread/challenge",
                )
            )
    elif page2.strip():
        evidence.append({"path": "pages[1]", "text": page2[:200], "reason": "page-two turn reason"})
    elif len(pages) < 2:
        issues.append(_issue("page_two_missing", "need page two for turn/discovery"))

    status = "PASS" if not issues else "BLOCKED"
    return _gate(GATE_HOOK, status=status, score=100 if status == "PASS" else 0, threshold=100, blocking=True, issues=issues, evidence=evidence)


def _check_market(writer_handoff: Mapping[str, Any], ids: dict[str, Any], mrc: Mapping[str, Any] | None) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    blob = full_script_text(writer_handoff).lower()
    market = ids["target_market"]
    touch = [str(t).lower().replace("_", " ") for t in ((mrc or {}).get("market_touchpoints") or [])]
    surface_hits = _contains_any(blob, touch) if touch else []
    # market keyword fallbacks
    market_defaults = {
        "en_US": ["bus", "group chat", "locker", "parking", "suburb", "mall", "phone", "app", "ranking"],
        "ja_JP": ["train", "station", "convenience", "line", "platform", "last train", "vending", "app"],
        "zh_CN": ["feed", "recommend", "subway", "wechat", "gaokao", "community", "interface", "score"],
        "fr_FR": ["métro", "metro", "lycée", "lycee", "banlieue", "café", "cafe", "bac", "group chat", "seating"],
    }
    if not surface_hits:
        surface_hits = _contains_any(blob, market_defaults.get(market, []))
    if not surface_hits:
        issues.append(_issue("market_surface_absent", f"no concrete {market} surface/object/pressure"))
    else:
        evidence.append({"path": "pages[*]", "text": surface_hits[0], "reason": f"{market} market surface"})

    # guardrail violations
    if market == "zh_CN":
        if re.search(r"\b(overthrow|party central|political system allegory|regime)\b", blob):
            issues.append(_issue("zh_cn_system_allegory", "unsafe direct political-system allegory"))
    if market == "fr_FR":
        if re.search(r"\b(homecoming|prom king|varsity jacket|pep rally)\b", blob) and not _contains_any(
            blob, ["lycée", "lycee", "métro", "metro", "bac"]
        ):
            issues.append(_issue("fr_flat_us_school_import", "France market with flat U.S. high-school import"))
    if market == "ja_JP":
        if re.search(r"\b(mount fuji|geisha|samurai cosplay|tourist)\b", blob) and "train" not in blob:
            issues.append(_issue("ja_tourist_default", "Japan market tourist-Japan default"))
    if market == "en_US":
        if re.search(r"\b(sakura petals|anime club only|honorific -san)\b", blob) and "locker" not in blob:
            issues.append(_issue("en_fake_japan_surface", "U.S. market with fake-Japan surface"))

    status = "PASS" if not issues else "BLOCKED"
    return _gate(GATE_MARKET, status=status, score=100 if status == "PASS" else 0, threshold=100, blocking=True, issues=issues, evidence=evidence)


def _check_bland(writer_handoff: Mapping[str, Any], cfg: Mapping[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    full = full_script_text(writer_handoff)
    low = full.lower()
    for marker in cfg.get("stub_dialogue_markers") or []:
        if marker.lower() in low or marker in full:
            issues.append(_issue("canned_stub_dialogue", f"stub marker {marker!r}"))

    phrases = list(cfg.get("generic_phrases") or [])
    conflict = list(cfg.get("conflict_change_signals") or [])
    for phrase in phrases:
        if phrase.lower() not in low:
            continue
        # fatal when surrounding panel lacks concrete object/choice/consequence
        # approximate: if phrase present and few conflict signals overall
        if len(_contains_any(full, conflict)) < 2:
            issues.append(
                _issue(
                    "generic_fallback_fatal",
                    f"{phrase!r} without surrounding concrete action/choice/consequence",
                )
            )
        else:
            evidence.append({"path": "pages[*]", "text": phrase, "reason": "generic phrase surrounded by concrete action (warn-only)"})

    desire = _contains_any(full, list(cfg.get("desire_signals") or []))
    cost = _contains_any(full, list(cfg.get("cost_signals") or []))
    if not desire and not cost:
        issues.append(_issue("no_desire_choice_or_cost", "protagonist has no specific desire, choice, or cost"))

    # mostly generic emotional summary heuristic
    words = re.findall(r"[a-z']+", low)
    if words:
        abstract = sum(1 for w in words if w in {"feel", "feeling", "emotion", "heart", "soul", "journey", "heal", "healing", "changed", "shifted"})
        if abstract / max(len(words), 1) > 0.12 and len(_contains_any(full, conflict)) < 2:
            issues.append(_issue("mostly_generic_emotional_summary", "panel text mostly generic emotional summary"))

    if not issues:
        evidence.append({"path": "pages[*]", "text": "specificity ok", "reason": "anti-blandness"})

    status = "PASS" if not issues else "BLOCKED"
    return _gate(GATE_BLAND, status=status, score=100 if status == "PASS" else 0, threshold=100, blocking=True, issues=issues, evidence=evidence)


def _score_report(gates: list[dict[str, Any]], cfg: Mapping[str, Any]) -> int:
    weights = cfg.get("weights") or {}
    mapping = {
        GATE_MODERN: "modern_reader_realization",
        GATE_GENRE: "genre_core_pleasure",
        GATE_INTERACT: "interaction_realization",
        GATE_HOOK: "page_one_hook",
        GATE_MARKET: "market_native_surface",
        GATE_BLAND: "anti_blandness",
    }
    # desire/cost folded into modern gate score contribution
    total_w = 0
    acc = 0.0
    for g in gates:
        key = mapping.get(g["gate_id"])
        if not key:
            continue
        w = int(weights.get(key) or 0)
        total_w += w
        acc += w * (float(g.get("score") or 0) / 100.0)
    # protagonist desire/cost weight from modern gate
    w_des = int(weights.get("protagonist_desire_cost") or 0)
    modern = next((g for g in gates if g["gate_id"] == GATE_MODERN), None)
    if modern:
        total_w += w_des
        acc += w_des * (float(modern.get("score") or 0) / 100.0)
    if total_w <= 0:
        return 0
    return int(round(100.0 * acc / total_w))


def _repair_packet(
    gates: list[dict[str, Any]],
    ids: dict[str, Any],
    mrc: Mapping[str, Any] | None,
) -> dict[str, Any]:
    failed = [g["gate_id"] for g in gates if g.get("status") == "BLOCKED"]
    failed_set = set(failed)
    if failed_set & {GATE_RESEARCH, GATE_ARCHITECT, GATE_ALIAS}:
        scope = "regenerate_architecture"
    elif failed_set & {GATE_GENRE, GATE_INTERACT}:
        scope = "rewrite_chapter"
    else:
        scope = "rewrite_opening_pages"

    missing: list[str] = []
    locations: list[str] = []
    for g in gates:
        if g.get("status") != "BLOCKED":
            continue
        for iss in g.get("issues") or []:
            missing.append(str(iss.get("code") or iss.get("message")))
        for ev in g.get("evidence") or []:
            if ev.get("path"):
                locations.append(str(ev["path"]))

    catalyst = (mrc or {}).get("catalyst") if mrc else None
    instruction = (
        f"Rewrite so the selected ordinary-world catalyst becomes story action that changes "
        f"conflict (pressure/choice/cost/rule), prove genre-core pleasure for "
        f"{ids.get('relevance_genre')}, keep market={ids.get('target_market')} surfaces concrete, "
        f"and remove generic fallback lines. Failed gates: {', '.join(failed)}."
    )
    return {
        "failed_gate_ids": failed,
        "exact_paths": locations[:20],
        "missing_required_evidence": missing[:30],
        "selected_catalyst": catalyst,
        "genre_core_requirements": ids.get("relevance_genre"),
        "repair_instruction": instruction,
        "repair_scope": scope,
        "genre_id": ids.get("genre_id"),
        "strategy_genre": ids.get("strategy_genre"),
        "relevance_genre": ids.get("relevance_genre"),
        "reader_market": ids.get("target_market"),
        "reader_audience": ids.get("target_audience"),
    }


def evaluate_story_excellence(
    *,
    story_handoff: Mapping[str, Any],
    writer_handoff: Mapping[str, Any],
    internal_record: Mapping[str, Any] | None = None,
    production: bool = True,
    config_path: Path | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Return a serializable excellence realization report. Never mutates inputs."""
    # Freeze copies so callers can trust immutability even if we nest-read.
    story = copy.deepcopy(dict(story_handoff))
    writer = copy.deepcopy(dict(writer_handoff))
    internal = copy.deepcopy(dict(internal_record)) if internal_record else None
    root = repo_root or REPO
    cfg = _load_yaml(config_path or (root / "config/manga/story_excellence_gates.yaml"))
    alias_cfg = _load_yaml(root / "config/manga/story_genre_alias_coherence.yaml")

    mrc = _resolve_modern_context(story, writer, internal)
    ids = _identity_fields(story, writer, mrc)

    gates = [
        _check_research(ids=ids, cfg=cfg, production=production, repo_root=root),
        _check_architect(story, writer, mrc, production=production, repo_root=root),
        _check_alias(ids, alias_cfg, writer),
        _check_modern_realization(writer, mrc, cfg),
        _check_genre_core(writer, ids, mrc, cfg),
        _check_interaction(writer, ids, root),
        _check_page_one_hook(writer, cfg),
        _check_market(writer, ids, mrc),
        _check_bland(writer, cfg),
    ]

    hard_failed = [g for g in gates if g.get("status") == "BLOCKED" and g.get("blocking")]
    score = _score_report(gates, cfg)
    threshold = int(cfg.get("production_score_threshold") or 85)

    if hard_failed:
        status = "BLOCKED"
    elif score < threshold and production:
        status = "BLOCKED"
        gates.append(
            _gate(
                "MANGA.STORY.SCORE_THRESHOLD",
                status="BLOCKED",
                score=score,
                threshold=threshold,
                blocking=True,
                issues=[_issue("score_below_threshold", f"score {score} < {threshold}")],
                evidence=[],
            )
        )
        hard_failed = [gates[-1]]
    elif not production and score < threshold:
        status = "WARN"
    else:
        status = "PASS"

    repair = _repair_packet(gates, ids, mrc) if status == "BLOCKED" else None
    # Attach repair gate row for registry visibility (informational when blocked)
    if repair:
        gates.append(
            _gate(
                GATE_REPAIR,
                status="PASS",
                score=100,
                threshold=100,
                blocking=False,
                issues=[],
                evidence=[{"path": "repair_packet", "text": repair["repair_scope"], "reason": "repair packet emitted"}],
            )
        )

    return {
        "schema_version": "1.0.0",
        "artifact_type": "manga_story_excellence_realization_report",
        "status": status,
        "production_blocking": bool(production and status == "BLOCKED"),
        "series_id": ids["series_id"],
        "chapter_id": ids["chapter_id"],
        "chapter_number": ids["chapter_number"],
        "genre_id": ids["genre_id"],
        "strategy_genre": ids["strategy_genre"],
        "relevance_genre": ids["relevance_genre"],
        "target_market": ids["target_market"],
        "target_audience": ids["target_audience"],
        "score": score,
        "threshold": threshold,
        "gates": gates,
        "repair_packet": repair,
    }
