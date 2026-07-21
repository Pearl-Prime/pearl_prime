#!/usr/bin/env python3
"""On-box CosyVoice synth + R2 upload (gender-only stock voices + text prep, NO SSML).

Runs on Pearl Star. Contract: config/tts/social_media_voice_matrix.yaml v2 +
config/tts/social_media_tts_text_prep.yaml (OPD-SMV-03).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

# Allow importing sibling tts_text_prep when both live in scripts/social_media/
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tts_text_prep import apply_text_prep, load_prep  # noqa: E402

R2_PREFIX_DEFAULT = "social_media/voice_bank/20260719b/"


def load_matrix(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise SystemExit("PyYAML required on pearlstar")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    status = ((data.get("ratification") or {}).get("status") or "").upper()
    if status != "RATIFIED":
        raise SystemExit(f"matrix not RATIFIED (status={status!r})")
    return data


def resolve_voice(matrix: dict[str, Any], persona: str) -> str:
    return str(matrix["persona_voices"][persona]["voice_id"])


def content_hash(voice_id: str, speakable: str, prep_ver: str) -> str:
    blob = json.dumps(
        {"voice_id": voice_id, "speakable": speakable, "prep": prep_ver},
        sort_keys=True,
    ).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def synth(text: str, speaker: str, out_mp3: Path, cosy: str) -> int:
    payload = json.dumps({"text": text[:5000], "speaker": speaker}).encode()
    req = urllib.request.Request(
        f"{cosy.rstrip('/')}/api/v1/tts",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = resp.read()
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    raw = out_mp3.with_suffix(".bin")
    raw.write_bytes(data)
    if data[:4] == b"RIFF":
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(raw), "-codec:a", "libmp3lame", "-qscale:a", "4", str(out_mp3)],
            check=True,
            capture_output=True,
        )
        raw.unlink(missing_ok=True)
    else:
        raw.rename(out_mp3)
    return out_mp3.stat().st_size


def r2_client():
    import boto3
    from botocore.config import Config

    endpoint = (os.environ.get("R2_ENDPOINT") or "").strip()
    if not endpoint:
        account = os.environ.get("CLOUDFLARE_ACCOUNT_ID") or os.environ.get("R2_ACCOUNT_ID")
        endpoint = f"https://{account}.r2.cloudflarestorage.com"
    if not endpoint.startswith("http"):
        endpoint = "https://" + endpoint
    return boto3.client(
        "s3",
        endpoint_url=endpoint.rstrip("/"),
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(signature_version="s3v4", retries={"max_attempts": 3}),
    ), os.environ.get("R2_BUCKET") or "phoenix-omega-artifacts"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--atoms", type=Path, required=True)
    ap.add_argument("--matrix", type=Path, required=True)
    ap.add_argument("--text-prep", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--r2-prefix", default=R2_PREFIX_DEFAULT)
    ap.add_argument("--cosy", default="http://127.0.0.1:9880")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--skip-upload", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    matrix = load_matrix(args.matrix)
    prep = load_prep(args.text_prep)
    prep_ver = str(prep.get("schema_version") or "1")
    atoms = [json.loads(l) for l in args.atoms.read_text().splitlines() if l.strip()]
    atoms = atoms[args.offset :]
    if args.limit:
        atoms = atoms[: args.limit]

    prior: dict[str, dict[str, str]] = {}
    if args.manifest.exists():
        lines = args.manifest.read_text().splitlines()
        if lines:
            cols = lines[0].split("\t")
            for line in lines[1:]:
                parts = line.split("\t")
                if len(parts) >= len(cols):
                    row = dict(zip(cols, parts))
                    prior[row["atom_id"]] = row

    header = (
        "atom_id\tpersona\ttopic\tlocale\tvoice_id\tparams_hash\tchar_count\t"
        "r2_key\tbytes\tsha256\tstatus\tspeakable_preview\tspeakable_text\n"
    )
    ok = skip = fail = 0
    client = bucket = None
    if not args.skip_upload:
        client, bucket = r2_client()

    for i, atom in enumerate(atoms, 1):
        aid = atom["atom_id"]
        persona, topic = atom["persona"], atom["topic"]
        locale = atom.get("locale") or "en-US"
        voice_id = resolve_voice(matrix, persona)
        speakable = apply_text_prep(atom["text"], prep)
        ph = content_hash(voice_id, speakable, prep_ver)
        r2_key = f"{args.r2_prefix}mp3/{locale}/{persona}/{topic}/{aid}.mp3"
        if (
            not args.force
            and aid in prior
            and prior[aid].get("params_hash") == ph
            and prior[aid].get("status") == "ok"
        ):
            skip += 1
            print(f"[{i}/{len(atoms)}] skip {aid}")
            continue
        local = args.out / "mp3" / locale / persona / topic / f"{aid}.mp3"
        try:
            nbytes = synth(speakable, voice_id, local, args.cosy)
            if nbytes < 10_000:
                raise RuntimeError(f"too small {nbytes}")
            sha = hashlib.sha256(local.read_bytes()).hexdigest()
            if not args.skip_upload:
                assert client is not None
                with local.open("rb") as fh:
                    client.put_object(
                        Bucket=bucket,
                        Key=r2_key,
                        Body=fh,
                        ContentType="audio/mpeg",
                        Metadata={"sha256": sha, "voice_id": voice_id},
                    )
            prior[aid] = {
                "atom_id": aid,
                "persona": persona,
                "topic": topic,
                "locale": locale,
                "voice_id": voice_id,
                "params_hash": ph,
                "char_count": str(len(speakable)),
                "r2_key": r2_key,
                "bytes": str(nbytes),
                "sha256": sha,
                "status": "ok",
                "speakable_preview": speakable[:80].replace("\t", " ").replace("\n", " "),
                "speakable_text": speakable.replace("\t", " ").replace("\n", " "),
            }
            ok += 1
            print(f"[{i}/{len(atoms)}] ok {aid} voice={voice_id} bytes={nbytes}")
        except Exception as e:
            fail += 1
            prior[aid] = {
                "atom_id": aid,
                "persona": persona,
                "topic": topic,
                "locale": locale,
                "voice_id": voice_id,
                "params_hash": ph,
                "char_count": str(len(speakable)),
                "r2_key": r2_key,
                "bytes": "0",
                "sha256": "",
                "status": f"fail:{e}",
                "speakable_preview": speakable[:80].replace("\t", " ").replace("\n", " "),
                "speakable_text": speakable.replace("\t", " ").replace("\n", " "),
            }
            print(f"[{i}/{len(atoms)}] FAIL {aid}: {e}", file=sys.stderr)
        if i % 10 == 0 or i == len(atoms):
            args.manifest.parent.mkdir(parents=True, exist_ok=True)
            with args.manifest.open("w", encoding="utf-8") as f:
                f.write(header)
                for k in sorted(prior):
                    r = prior[k]
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
                                r.get("speakable_preview", ""),
                                r.get("speakable_text", ""),
                            ]
                        )
                        + "\n"
                    )
            print(f"--- checkpoint i={i} ok={ok} skip={skip} fail={fail} ---")

    print(f"DONE ok={ok} skip={skip} fail={fail}")
    return 0 if ok or skip else 1


if __name__ == "__main__":
    raise SystemExit(main())
