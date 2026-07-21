#!/usr/bin/env python3
"""Social media atom → CosyVoice MP3 bank (Wave 2).

NEW-ARTIFACT-JUSTIFIED: composes ratified voice matrix + CosyVoice on-box synth +
existing R2 push patterns into one idempotent batch driver. Does not fork a new
uploader — uses the same boto3/R2 contract as scripts/artifacts/r2_push_helper.py.

RAP note: pscli enqueue has no tts_cosyvoice2 task yet. Default --synth-mode=ssh-onbox
runs synthesis on Pearl Star against 127.0.0.1:9880 (service must be active).

Usage:
  python3 scripts/social_media/generate_voice_bank.py --smoke
  python3 scripts/social_media/generate_voice_bank.py --pilot
  python3 scripts/social_media/generate_voice_bank.py --scale --batch-size 50
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
ATOMS = REPO / "SOURCE_OF_TRUTH" / "social_media_atoms" / "evergreen_en_us_atoms.jsonl"
MATRIX = REPO / "config" / "tts" / "social_media_voice_matrix.yaml"
OUT_ROOT = REPO / "artifacts" / "social_media_voice_bank_2026-07-19"
MANIFEST = OUT_ROOT / "MANIFEST.tsv"
LOCAL_MP3 = OUT_ROOT / "mp3"
HEARTBEAT = REPO / "artifacts" / "coordination" / "heartbeats" / "social_media_mp3_bank_2026-07-19.md"
R2_PREFIX = "social_media/voice_bank/20260719/"
BUCKET_DEFAULT = "phoenix-omega-artifacts"
MANIFEST_HEADER = (
    "atom_id\tpersona\ttopic\tlocale\tvoice_id\tparams_hash\tchar_count\t"
    "r2_key\tbytes\tsha256\tstatus\n"
)


def _load_matrix() -> dict[str, Any]:
    data = yaml.safe_load(MATRIX.read_text(encoding="utf-8")) or {}
    status = ((data.get("ratification") or {}).get("status") or "").upper()
    if status != "RATIFIED":
        raise SystemExit(
            f"GATE: matrix not RATIFIED (status={status!r}). "
            "Stand down until social-media-voice-matrix-ratified=<sha>."
        )
    return data


def _params_hash(voice_id: str, params: dict[str, Any]) -> str:
    blob = json.dumps({"voice_id": voice_id, **params}, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def resolve_voice(matrix: dict[str, Any], persona: str, topic: str) -> tuple[str, dict[str, Any]]:
    pv = (matrix.get("persona_voices") or {})[persona]
    voice_id = str(pv["voice_id"])
    params = dict(pv.get("base") or {})
    topic_mod = (matrix.get("topic_modulation") or {}).get(topic) or {}
    params.update(topic_mod)
    overrides = ((matrix.get("persona_topic_overrides") or {}).get(persona) or {}).get(topic)
    if overrides:
        params.update(overrides)
    return voice_id, params


def load_atoms() -> list[dict[str, Any]]:
    rows = []
    with ATOMS.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_manifest() -> dict[str, dict[str, str]]:
    if not MANIFEST.exists():
        return {}
    out: dict[str, dict[str, str]] = {}
    with MANIFEST.open(encoding="utf-8") as f:
        header = f.readline()
        cols = header.rstrip("\n").split("\t")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < len(cols):
                continue
            row = dict(zip(cols, parts))
            out[row["atom_id"]] = row
    return out


def write_manifest_row(row: dict[str, str]) -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    if not MANIFEST.exists():
        MANIFEST.write_text(MANIFEST_HEADER, encoding="utf-8")
    # rewrite if updating existing atom_id
    existing = read_manifest()
    existing[row["atom_id"]] = row
    with MANIFEST.open("w", encoding="utf-8") as f:
        f.write(MANIFEST_HEADER)
        for aid in sorted(existing):
            r = existing[aid]
            f.write(
                "\t".join(
                    [
                        r.get("atom_id", ""),
                        r.get("persona", ""),
                        r.get("topic", ""),
                        r.get("locale", ""),
                        r.get("voice_id", ""),
                        r.get("params_hash", ""),
                        r.get("char_count", ""),
                        r.get("r2_key", ""),
                        r.get("bytes", ""),
                        r.get("sha256", ""),
                        r.get("status", ""),
                    ]
                )
                + "\n"
            )


def update_heartbeat(step: str, done: int, total: int, signal: str, blocker: str = "") -> None:
    HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT.write_text(
        f"""# Heartbeat — social media MP3 bank

- updated_utc: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
- step: {step}
- done/total: {done}/{total}
- last_signal: {signal}
- blocker: {blocker or 'none'}
- resume: {MANIFEST}
""",
        encoding="utf-8",
    )


def synth_ssh_onbox(text: str, speaker: str, out_mp3: Path) -> int:
    """Synthesize on Pearl Star via SSH; CosyVoice returns WAV bytes — ffmpeg to mp3."""
    remote_raw = f"/tmp/smv_bank_{hashlib.sha256((speaker+text).encode()).hexdigest()[:12]}.bin"
    payload = json.dumps({"text": text[:5000], "speaker": speaker})
    # Write payload remotely and curl localhost
    cmd = (
        f"python3 - <<'PY'\n"
        f"import json,urllib.request,pathlib\n"
        f"payload={payload!r}\n"
        f"req=urllib.request.Request('http://127.0.0.1:9880/api/v1/tts',"
        f" data=payload.encode(), headers={{'Content-Type':'application/json'}}, method='POST')\n"
        f"with urllib.request.urlopen(req, timeout=180) as r: data=r.read()\n"
        f"pathlib.Path({remote_raw!r}).write_bytes(data)\n"
        f"print(len(data))\n"
        f"PY"
    )
    proc = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "pearl_star", cmd],
        capture_output=True,
        text=True,
        timeout=240,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ssh synth failed: {proc.stderr[-400:]}")
    local_raw = out_mp3.with_suffix(".raw.bin")
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["scp", "-o", "BatchMode=yes", f"pearl_star:{remote_raw}", str(local_raw)],
        check=True,
        capture_output=True,
        timeout=120,
    )
    subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "pearl_star", f"rm -f {remote_raw}"],
        capture_output=True,
        timeout=30,
    )
    # CosyVoice returns WAV; convert to mp3
    if local_raw.read_bytes()[:4] == b"RIFF":
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(local_raw), "-codec:a", "libmp3lame", "-qscale:a", "4", str(out_mp3)],
            check=True,
            capture_output=True,
            timeout=60,
        )
        local_raw.unlink(missing_ok=True)
    else:
        local_raw.rename(out_mp3)
    return out_mp3.stat().st_size


def _r2_client():
    import boto3
    from botocore.config import Config

    key = os.environ.get("R2_ACCESS_KEY_ID")
    secret = os.environ.get("R2_SECRET_ACCESS_KEY")
    bucket = (
        os.environ.get("R2_BUCKET_OVERRIDE")
        or os.environ.get("R2_BUCKET")
        or BUCKET_DEFAULT
    )
    endpoint = (os.environ.get("R2_ENDPOINT") or "").strip()
    if not endpoint:
        account = os.environ.get("CLOUDFLARE_ACCOUNT_ID") or os.environ.get("R2_ACCOUNT_ID")
        if not account:
            raise RuntimeError("missing R2_ENDPOINT or account id")
        endpoint = f"https://{account}.r2.cloudflarestorage.com"
    if not endpoint.startswith("http"):
        endpoint = "https://" + endpoint
    if not all([key, secret]):
        raise RuntimeError("missing R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY")
    try:
        import certifi

        os.environ.setdefault("SSL_CERT_FILE", certifi.where())
        os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
    except ImportError:
        pass
    return boto3.client(
        "s3",
        endpoint_url=endpoint.rstrip("/"),
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        region_name="auto",
        config=Config(signature_version="s3v4", retries={"max_attempts": 3}),
    ), bucket


def upload_r2(local: Path, r2_key: str) -> None:
    client, bucket = _r2_client()
    sha = hashlib.sha256(local.read_bytes()).hexdigest()
    with local.open("rb") as fh:
        client.put_object(
            Bucket=bucket,
            Key=r2_key,
            Body=fh,
            ContentType="audio/mpeg",
            Metadata={"sha256": sha},
        )


def r2_head_ok(r2_key: str) -> bool:
    client, bucket = _r2_client()
    try:
        client.head_object(Bucket=bucket, Key=r2_key)
        return True
    except Exception:
        return False


def process_atom(
    atom: dict[str, Any],
    matrix: dict[str, Any],
    *,
    skip_upload: bool = False,
    force: bool = False,
) -> dict[str, str]:
    persona = atom["persona"]
    topic = atom["topic"]
    locale = atom.get("locale") or "en-US"
    atom_id = atom["atom_id"]
    text = atom["text"]
    voice_id, params = resolve_voice(matrix, persona, topic)
    ph = _params_hash(voice_id, params)
    r2_key = f"{R2_PREFIX}mp3/{locale}/{persona}/{topic}/{atom_id}.mp3"
    prior = read_manifest().get(atom_id)
    if (
        not force
        and prior
        and prior.get("params_hash") == ph
        and prior.get("status") == "ok"
        and prior.get("r2_key") == r2_key
    ):
        return {**prior, "status": "skipped-idempotent"}

    rel = Path("mp3") / locale / persona / topic / f"{atom_id}.mp3"
    local = LOCAL_MP3 / locale / persona / topic / f"{atom_id}.mp3"
    nbytes = synth_ssh_onbox(text, voice_id, local)
    if nbytes < 10_000:
        raise RuntimeError(f"synth too small: {nbytes} bytes for {atom_id}")
    sha = hashlib.sha256(local.read_bytes()).hexdigest()
    if not skip_upload:
        upload_r2(local, r2_key)
    row = {
        "atom_id": atom_id,
        "persona": persona,
        "topic": topic,
        "locale": locale,
        "voice_id": voice_id,
        "params_hash": ph,
        "char_count": str(atom.get("char_count") or len(text)),
        "r2_key": r2_key,
        "bytes": str(nbytes),
        "sha256": sha,
        "status": "ok" if not skip_upload else "local-only",
    }
    write_manifest_row(row)
    return row


def select_smoke(atoms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for a in atoms:
        if a["persona"] == "corporate_managers" and a["topic"] == "anxiety" and a["atom_family"] == "SOMATIC_SETUP":
            return [a]
    return atoms[:1]


def select_pilot(atoms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    want = [
        ("corporate_managers", "anxiety", "SOMATIC_SETUP"),
        ("gen_z_professionals", "anxiety", "SOMATIC_SETUP"),
        ("healthcare_rns", "compassion_fatigue", "SOMATIC_SETUP"),
        ("corporate_managers", "burnout", "SOMATIC_SETUP"),
        ("gen_z_professionals", "courage", "SOMATIC_SETUP"),
    ]
    found = []
    for persona, topic, fam in want:
        for a in atoms:
            if a["persona"] == persona and a["topic"] == topic and a.get("atom_family") == fam:
                found.append(a)
                break
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--scale", action="store_true")
    ap.add_argument("--batch-size", type=int, default=50)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--skip-upload", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--verify-r2-get", action="store_true")
    args = ap.parse_args()

    matrix = _load_matrix()
    atoms = load_atoms()
    if args.smoke:
        batch = select_smoke(atoms)
        step = "smoke"
    elif args.pilot:
        batch = select_pilot(atoms)
        step = "pilot"
    elif args.scale:
        batch = atoms
        step = "scale"
    else:
        ap.error("pass --smoke, --pilot, or --scale")

    if args.limit:
        batch = batch[: args.limit]

    ok = skip = fail = 0
    total = len(batch)
    update_heartbeat(step, 0, total, "start")
    for i, atom in enumerate(batch, 1):
        try:
            row = process_atom(atom, matrix, skip_upload=args.skip_upload, force=args.force)
            if row.get("status") == "skipped-idempotent":
                skip += 1
                signal = f"skip {atom['atom_id']}"
            else:
                ok += 1
                signal = f"ok {atom['atom_id']} bytes={row['bytes']}"
                if args.verify_r2_get and not args.skip_upload:
                    if not r2_head_ok(row["r2_key"]):
                        raise RuntimeError(f"R2 HEAD miss after upload: {row['r2_key']}")
                    signal += " r2_head=200"
            print(f"[{i}/{total}] {signal}")
        except Exception as e:
            fail += 1
            print(f"[{i}/{total}] FAIL {atom.get('atom_id')}: {e}", file=sys.stderr)
            write_manifest_row(
                {
                    "atom_id": atom["atom_id"],
                    "persona": atom["persona"],
                    "topic": atom["topic"],
                    "locale": atom.get("locale") or "en-US",
                    "voice_id": "",
                    "params_hash": "",
                    "char_count": str(atom.get("char_count") or ""),
                    "r2_key": "",
                    "bytes": "0",
                    "sha256": "",
                    "status": f"fail:{e}",
                }
            )
            signal = f"fail {atom['atom_id']}"
        if i % 5 == 0 or i == total:
            update_heartbeat(step, ok + skip, total, signal, blocker=f"fail={fail}")
        # micro-batch pause marker for scale
        if args.scale and i % args.batch_size == 0:
            update_heartbeat(step, ok + skip, total, f"batch-boundary-{i}", blocker=f"fail={fail}")
            print(f"--- batch boundary {i}/{total} ok={ok} skip={skip} fail={fail} ---")

    print(f"DONE step={step} ok={ok} skipped-idempotent={skip} failed={fail} total={total}")
    print(f"manifest={MANIFEST}")
    return 1 if fail and ok == 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
