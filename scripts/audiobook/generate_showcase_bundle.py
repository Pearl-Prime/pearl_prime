#!/usr/bin/env python3
"""
Audiobook showcase bundle — Pearl Star only ($0).

- Prose: Qwen3:14b via Ollama OpenAI-compatible API (native language per teacher lane).
- TTS: CosyVoice2 (built-in preset or zero-shot from voice_clone_reference_library.yaml).
- No ElevenLabs, no Anthropic/DashScope for this script.

Env (defaults assume LAN Pearl Star):
  PEARL_STAR_IP=192.168.1.112
  QWEN_BASE_URL=http://$PEARL_STAR_IP:11434/v1
  COSYVOICE_URL=http://$PEARL_STAR_IP:9880
  QWEN_MODEL=qwen3:14b
  Authorization header uses api key \"ollama\" per operator convention.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

PERSONA = "gen_z_professionals"

# Brands aligned to config/catalog_planning/teacher_brand_lane_assignments.yaml → english_global.
# Locale = native language for showcase sample (Pearl Star generation); see ADDENDUM 2026.
TEACHER_ROWS: list[dict[str, str]] = [
    {"id": "ahjan", "topic": "anxiety", "brand": "stillness_press", "name": "Ahjan", "locale": "en-US", "cv_builtin": "english_male"},
    {"id": "joshin", "topic": "anxiety", "brand": "cognitive_clarity", "name": "Joshin", "locale": "en-US", "cv_builtin": "english_male"},
    {"id": "ajahn_x", "topic": "boundaries", "brand": "norcal_dharma", "name": "Ajahn X", "locale": "en-US", "cv_builtin": "english_male"},
    {"id": "pamela_fellows", "topic": "burnout", "brand": "somatic_wisdom", "name": "Pamela Fellows", "locale": "en-US", "cv_builtin": "english_female"},
    {"id": "master_wu", "topic": "courage", "brand": "warrior_calm", "name": "Master Wu", "locale": "zh-CN", "cv_builtin": "chinese_male"},
    {"id": "miki", "topic": "imposter_syndrome", "brand": "digital_ground", "name": "Miki", "locale": "ja-JP", "cv_builtin": "ja_m_calm_01"},
    {"id": "junko", "topic": "overthinking", "brand": "relational_calm", "name": "Junko", "locale": "ja-JP", "cv_builtin": "ja_female_warm"},
    {"id": "master_sha", "topic": "grief", "brand": "sleep_restoration", "name": "Master Sha", "locale": "zh-CN", "cv_builtin": "chinese_male"},
    {"id": "ra", "topic": "self_worth", "brand": "solar_return", "name": "Ra", "locale": "en-US", "cv_builtin": "english_male"},
    {"id": "sai_ma", "topic": "grief", "brand": "devotion_path", "name": "Sai Ma", "locale": "zh-CN", "cv_builtin": "chinese_female"},
    {"id": "adi_da", "topic": "self_worth", "brand": "heart_balance", "name": "Adi Da", "locale": "en-US", "cv_builtin": "english_male"},
    {"id": "omote", "topic": "sleep_anxiety", "brand": "body_memory", "name": "Omote", "locale": "ko-KR", "cv_builtin": "ko_female_gentle"},
    {"id": "master_feung", "topic": "burnout", "brand": "qi_foundation", "name": "Master Feung", "locale": "zh-CN", "cv_builtin": "chinese_male"},
]

TOPIC_LABEL = {
    "anxiety": "Anxiety",
    "boundaries": "Boundaries",
    "burnout": "Burnout",
    "compassion_fatigue": "Compassion Fatigue",
    "courage": "Courage",
    "depression": "Depression",
    "financial_anxiety": "Financial Anxiety",
    "financial_stress": "Financial Stress",
    "grief": "Grief",
    "imposter_syndrome": "Imposter Syndrome",
    "overthinking": "Overthinking",
    "self_worth": "Self-Worth",
    "sleep_anxiety": "Sleep Anxiety",
    "social_anxiety": "Social Anxiety",
    "somatic_healing": "Somatic Healing",
}

TOPIC_MOOD = {
    "anxiety": "#3B82F6",
    "grief": "#F59E0B",
    "burnout": "#EA580C",
    "sleep_anxiety": "#7E22CE",
    "courage": "#C9A227",
    "boundaries": "#64748B",
    "self_worth": "#C47A8A",
    "imposter_syndrome": "#818CF8",
    "overthinking": "#22D3EE",
    "depression": "#1E3A5F",
    "compassion_fatigue": "#A3785E",
    "financial_anxiety": "#134E4A",
    "social_anxiety": "#A78BFA",
    "somatic_healing": "#86EFAC",
    "financial_stress": "#134E4A",
}

BRAND_AUTHOR_COUNT: dict[str, int] = {
    "stillness_press": 7,
    "cognitive_clarity": 6,
    "norcal_dharma": 7,
    "somatic_wisdom": 7,
    "qi_foundation": 7,
    "digital_ground": 6,
    "heart_balance": 6,
    "relational_calm": 5,
    "warrior_calm": 7,
    "sleep_restoration": 6,
    "body_memory": 6,
    "solar_return": 6,
    "devotion_path": 6,
}

# CosyVoice built-in fallback when narrator+yaml clip lookup fails (ADDENDUM presets).
# When narrator_voice_assignments has no teacher+brand row, use row["cv_builtin"] if set, else locale default.
LOCALE_BUILTIN_FALLBACK: dict[str, str] = {
    "en-US": "english_male",
    "ja-JP": "ja_m_calm_01",
    "zh-CN": "chinese_male",
    "ko-KR": "ko_female_gentle",
}

LANG_NAMES: dict[str, str] = {
    "en-US": "English (US)",
    "ja-JP": "Japanese",
    "zh-CN": "Simplified Chinese",
    "ko-KR": "Korean",
}

_narrator_authors_cache: dict[str, Any] | None = None
_clone_library_cache: dict[str, str] | None = None


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or not yaml:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def pearl_star_urls() -> tuple[str, str]:
    """(qwen_chat_completions_base, cosyvoice_base) — no trailing slash."""
    ip = (os.environ.get("PEARL_STAR_IP") or "192.168.1.112").strip()
    qwen = (os.environ.get("QWEN_BASE_URL") or "").strip().rstrip("/")
    if not qwen:
        qwen = f"http://{ip}:11434/v1"
    cosy = (os.environ.get("COSYVOICE_URL") or "").strip().rstrip("/")
    if not cosy:
        cosy = f"http://{ip}:9880"
    return qwen, cosy


def first_arc(topic: str) -> Path | None:
    root = REPO_ROOT / "config/source_of_truth/master_arcs"
    matches = sorted(root.glob(f"{PERSONA}__{topic}__*.yaml"))
    return matches[0] if matches else None


def arc_engine(arc_path: Path) -> str:
    data = _load_yaml(arc_path)
    return str(data.get("engine") or "shame")


def brand_display_name(brand_key: str) -> str:
    bi = _load_yaml(REPO_ROOT / "config/catalog_planning/brand_identity_system.yaml")
    row = (bi.get("teacher_brands") or {}).get(brand_key)
    if isinstance(row, dict):
        return str(row.get("display_name") or brand_key)
    return brand_key


def _normalize_teacher_id(raw: str) -> str:
    r = raw.strip()
    if r.startswith("teacher_"):
        r = r[8:]
    return r


def load_narrator_authors() -> dict[str, Any]:
    global _narrator_authors_cache
    if _narrator_authors_cache is not None:
        return _narrator_authors_cache
    data = _load_yaml(REPO_ROOT / "config/tts/narrator_voice_assignments.yaml")
    _narrator_authors_cache = data.get("authors") if isinstance(data.get("authors"), dict) else {}
    return _narrator_authors_cache


def find_author_entry(teacher_id: str, brand_id: str) -> dict[str, Any] | None:
    authors = load_narrator_authors()
    for _k, entry in authors.items():
        if not isinstance(entry, dict):
            continue
        tid = _normalize_teacher_id(str(entry.get("teacher_id") or ""))
        br = str(entry.get("brand") or "")
        if tid == teacher_id and br == brand_id:
            return entry
    return None


def load_clone_paths() -> dict[str, str]:
    """reference_id -> repo-relative wav path."""
    global _clone_library_cache
    if _clone_library_cache is not None:
        return _clone_library_cache
    out: dict[str, str] = {}
    lib = _load_yaml(REPO_ROOT / "config/tts/voice_clone_reference_library.yaml")
    for section in lib.values():
        if not isinstance(section, list):
            continue
        for row in section:
            if not isinstance(row, dict):
                continue
            rid = str(row.get("reference_id") or "")
            lp = str(row.get("local_path") or "")
            if rid and lp:
                out[rid] = lp
    _clone_library_cache = out
    return out


def builtin_for_row(row: dict[str, str]) -> str:
    return str(row.get("cv_builtin") or LOCALE_BUILTIN_FALLBACK.get(row.get("locale", ""), "english_male"))


def resolve_cosyvoice_speaker(
    teacher_id: str,
    brand_id: str,
    locale: str,
    *,
    row: dict[str, str] | None = None,
) -> tuple[str, Path | None, str]:
    """
    Returns (speaker_id_for_builtin_OR_reference_id, reference_wav_path_or_None, source_note).
    """
    entry = find_author_entry(teacher_id, brand_id)
    voices = (entry or {}).get("voices") if entry else None
    if isinstance(voices, dict) and locale in voices:
        ab = voices[locale]
        if isinstance(ab, dict):
            audiobook = ab.get("audiobook")
            if isinstance(audiobook, dict):
                if str(audiobook.get("provider") or "").lower() in ("cosyvoice2", "cosyvoice"):
                    rid = str(audiobook.get("reference_id") or "").strip()
                    if rid:
                        paths = load_clone_paths()
                        rel = paths.get(rid)
                        wav = (REPO_ROOT / rel) if rel else None
                        if wav and wav.is_file():
                            return rid, wav, "narrator_voice_assignments+yaml_clip"
                        return rid, None, "narrator_voice_assignments_builtin_or_server_clip"
    fb = builtin_for_row(row or {"locale": locale, "cv_builtin": ""})
    return fb, None, "teacher_row_cv_builtin"


def call_qwen_native_chapter(
    *,
    teacher_name: str,
    brand_name: str,
    topic_key: str,
    topic_english_hint: str,
    positioning: str,
    locale: str,
) -> str:
    """Generate ~700–900 words of audiobook prose in target language (no translate step)."""
    qwen_base, _ = pearl_star_urls()
    url = f"{qwen_base.rstrip('/')}/chat/completions"
    lang = LANG_NAMES.get(locale, locale)
    system = (
        f"You write in native {lang}. Do not translate from English. "
        f"Write as a {positioning} author for the imprint \"{brand_name}\". "
        f"Use natural {lang} prose conventions, not translated English sentence structure. "
        f"Avoid rhetorical questions with question marks—prefer direct statements (TTS-friendly). "
        f"Short to medium sentences. Concrete body/sensory anchors where emotion appears."
    )
    user = (
        f"Teacher / public name: {teacher_name}\n"
        f"Canonical topic id: {topic_key}\n"
        f"Topic focus (for you, in any language): {topic_english_hint}\n\n"
        "Write Chapter 1 sample prose for an audiobook, approximately 700 to 900 words in the target language. "
        "Second person or direct address where it fits the tradition. "
        "No bullet lists. No meta commentary. Output prose only."
    )
    model = (os.environ.get("QWEN_MODEL") or "qwen3:14b").strip()
    api_key = (os.environ.get("OLLAMA_API_KEY") or "ollama").strip()
    body: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "temperature": 0.65,
    }
    # Ollama / Qwen3: disable thinking when supported
    body["think"] = False
    raw = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=raw,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        choice0 = (payload.get("choices") or [{}])[0]
        msg = choice0.get("message") or {}
        text = str(msg.get("content") or "").strip()
        if len(text.split()) < 120 and len(text) < 400:
            raise ValueError("qwen response too short")
        return text
    except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError, IndexError, TypeError) as e:
        raise RuntimeError(f"Pearl Star Qwen failed ({e!s}). Check Ollama on Pearl Star and model {model}.") from e


def cosyvoice_builtin_tts(text: str, speaker: str, out_mp3: Path, cosy_base: str) -> bool:
    payload = json.dumps({"text": text[:5000], "speaker": speaker}).encode("utf-8")
    req = urllib.request.Request(
        f"{cosy_base.rstrip('/')}/api/v1/tts",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = resp.read()
        if len(data) < 1000:
            return False
        out_mp3.parent.mkdir(parents=True, exist_ok=True)
        out_mp3.write_bytes(data)
        return True
    except (urllib.error.URLError, OSError):
        return False


def cosyvoice_cross_lingual_wav(text: str, reference_wav: Path, language: str, out_wav: Path, cosy_base: str) -> bool:
    """POST multipart to /api/v3/cross-lingual/with-cache when server supports it."""
    try:
        boundary = "----phoenixOmegaBoundary"
        crlf = "\r\n"
        parts: list[bytes] = []

        def add_field(name: str, value: str) -> None:
            parts.append(f"--{boundary}{crlf}".encode())
            parts.append(f'Content-Disposition: form-data; name="{name}"{crlf}{crlf}'.encode())
            parts.append(value.encode("utf-8"))
            parts.append(crlf.encode())

        add_field("text", text[:5000])
        add_field("language", language)
        wav_bytes = reference_wav.read_bytes()
        parts.append(f"--{boundary}{crlf}".encode())
        parts.append(
            f'Content-Disposition: form-data; name="reference_audio"; filename="ref.wav"{crlf}'.encode()
        )
        parts.append(b"Content-Type: audio/wav\r\n\r\n")
        parts.append(wav_bytes)
        parts.append(crlf.encode())
        parts.append(f"--{boundary}--{crlf}".encode())
        body = b"".join(parts)
        req = urllib.request.Request(
            f"{cosy_base.rstrip('/')}/api/v3/cross-lingual/with-cache",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = resp.read()
        if len(data) < 1000:
            return False
        out_wav.parent.mkdir(parents=True, exist_ok=True)
        # Response may be WAV or MP3 depending on server
        if data[:4] == b"RIFF":
            out_wav.write_bytes(data)
        else:
            tmp = out_wav.with_suffix(".raw.bin")
            tmp.write_bytes(data)
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(tmp), str(out_wav)],
                check=False,
                capture_output=True,
            )
            tmp.unlink(missing_ok=True)
        return out_wav.exists() and out_wav.stat().st_size > 1000
    except Exception:
        return False


def wav_to_mp3(wav: Path, mp3: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-i", str(wav), str(mp3)], check=True, capture_output=True)


def ff_probe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True,
        text=True,
    )
    return float(r.stdout.strip() or 0)


def ffmpeg_finalize(in_audio: Path, out_mp3: Path, title: str, artist: str, album: str) -> None:
    """Loudnorm, 2s silence pre-roll, 3s fade-out tail."""
    norm = in_audio.with_suffix(".norm.mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(in_audio), "-af", "loudnorm=I=-16:TP=-1.0:LRA=11", str(norm)],
        check=True,
        capture_output=True,
    )
    dur = ff_probe_duration(norm)
    fade_start = max(0.0, 2.0 + dur - 3.0)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=44100:cl=stereo:d=2",
            "-i",
            str(norm),
            "-filter_complex",
            f"[0:a][1:a]concat=n=2:v=0:a=1,afade=t=out:st={fade_start}:d=3",
            "-metadata",
            f"title={title}",
            "-metadata",
            f"artist={artist}",
            "-metadata",
            f"album={album}",
            str(out_mp3),
        ],
        check=True,
        capture_output=True,
    )
    norm.unlink(missing_ok=True)


def positioning_for_brand(brand: str) -> str:
    mp = _load_yaml(REPO_ROOT / "config/tts/brand_narrator_voice_map.yaml")
    row = (mp.get("en_us") or {}).get(brand) or {}
    return str(row.get("positioning") or "somatic_companion")


def _strip_atom_file_prose(raw: str) -> str:
    blocks: list[str] = []
    for part in re.split(r"\n---\n", raw):
        part = part.strip()
        if not part or part.startswith("path:") or part.startswith("BAND:"):
            continue
        lines = part.splitlines()
        if lines and re.match(r"^##\s+\w+", lines[0]):
            part = "\n".join(lines[1:]).strip()
        blocks.append(part)
    return "\n\n".join(blocks)


def assemble_canonical_atoms(topic: str, engine: str, max_words: int = 850) -> str:
    base = REPO_ROOT / f"atoms/{PERSONA}/{topic}"
    chunks: list[str] = []
    scene_p = base / "SCENE/CANONICAL.txt"
    if scene_p.exists():
        chunks.append(_strip_atom_file_prose(scene_p.read_text(encoding="utf-8")))
    story_p = base / engine / "CANONICAL.txt"
    if story_p.exists():
        chunks.append(_strip_atom_file_prose(story_p.read_text(encoding="utf-8")))
    text = "\n\n".join(chunks).strip()
    words = text.split()
    if len(words) > max_words:
        text = " ".join(words[:max_words])
    return text


def assemble_teacher_bank(teacher_id: str, max_words: int = 850) -> str:
    root = REPO_ROOT / f"SOURCE_OF_TRUTH/teacher_banks/{teacher_id}/approved_atoms"
    if not root.exists():
        return ""
    order = ("HOOK", "SCENE", "STORY", "REFLECTION", "TEACHING", "INTEGRATION", "EXERCISE", "PIVOT", "THREAD", "TAKEAWAY")
    bodies: list[str] = []
    for typ in order:
        d = root / typ
        if not d.exists():
            continue
        for p in sorted(d.glob("*.yaml")):
            data = _load_yaml(p)
            body = str(data.get("body") or "").strip()
            if len(body.split()) < 8:
                continue
            bodies.append(body)
    text = "\n\n".join(bodies)
    words = text.split()
    if len(words) > max_words:
        text = " ".join(words[:max_words])
    return text


def run_generate_prose() -> list[dict[str, Any]]:
    pdir = REPO_ROOT / "artifacts/audiobook_samples/_prose"
    pdir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    frag: dict[str, str] = {}
    for row in TEACHER_ROWS:
        tid = row["id"]
        topic = row["topic"]
        brand = row["brand"]
        locale = row["locale"]
        arc = first_arc(topic)
        if not arc:
            raise RuntimeError(f"no arc for {topic}")
        pos = positioning_for_brand(brand)
        bname = brand_display_name(brand)
        tlabel = TOPIC_LABEL.get(topic, topic)
        provenance = "qwen3_pearl_star_native"
        try:
            text = call_qwen_native_chapter(
                teacher_name=row["name"],
                brand_name=bname,
                topic_key=topic,
                topic_english_hint=tlabel,
                positioning=pos,
                locale=locale,
            )
        except RuntimeError:
            # Offline / CI: fall back to English atoms or teacher bank (documented).
            eng = arc_engine(arc)
            if tid == "ajahn_x":
                text = assemble_canonical_atoms(topic, eng)
                provenance = "fallback_canonical_atoms_en:no_qwen"
            else:
                bt = assemble_teacher_bank(tid)
                if bt:
                    text = bt
                    provenance = "fallback_teacher_bank_en:no_qwen"
                else:
                    text = assemble_canonical_atoms(topic, eng)
                    provenance = f"fallback_canonical_atoms_en:{topic}:{eng}:no_qwen"
        pf = pdir / f"{tid}_{topic}_ch1.txt"
        pf.write_text(text, encoding="utf-8")
        spk, refp, sp_src = resolve_cosyvoice_speaker(tid, brand, locale, row=row)
        rows.append(
            {
                "teacher_id": tid,
                "topic": topic,
                "brand_key": brand,
                "brand_display": bname,
                "display_name": row["name"],
                "topic_label": tlabel,
                "locale": locale,
                "arc_path": str(arc.relative_to(REPO_ROOT)),
                "prose_path": str(pf.relative_to(REPO_ROOT)),
                "provenance": provenance,
                "cosyvoice_speaker": spk,
                "cosyvoice_voice_source": sp_src,
                "reference_wav": str(refp.relative_to(REPO_ROOT)) if refp else None,
                "authors_in_brand": BRAND_AUTHOR_COUNT.get(brand, 6),
                "positioning": pos,
            }
        )
        frag[f"{tid}__{topic}"] = provenance
    (pdir / "frag.json").write_text(json.dumps(frag, indent=2), encoding="utf-8")
    (pdir / "rows.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return rows


def run_tts_all() -> None:
    _, cosy = pearl_star_urls()
    for row in TEACHER_ROWS:
        tid = row["id"]
        topic = row["topic"]
        brand = row["brand"]
        locale = row["locale"]
        pf = REPO_ROOT / "artifacts/audiobook_samples/_prose" / f"{tid}_{topic}_ch1.txt"
        if not pf.exists():
            raise FileNotFoundError(pf)
        text = pf.read_text(encoding="utf-8")
        speaker, ref_wav, _src = resolve_cosyvoice_speaker(tid, brand, locale, row=row)
        builtin = builtin_for_row(row)
        raw = REPO_ROOT / "artifacts/audiobook_samples" / f"_{tid}_{topic}_raw.mp3"
        final = REPO_ROOT / "artifacts/audiobook_samples" / f"{tid}_{topic}_ch1.mp3"
        ok = False
        if ref_wav and ref_wav.is_file():
            tmp_wav = raw.with_suffix(".cv.wav")
            lang_code = {"en-US": "en", "ja-JP": "ja", "zh-CN": "zh", "ko-KR": "ko"}.get(locale, "en")
            if cosyvoice_cross_lingual_wav(text, ref_wav, lang_code, tmp_wav, cosy):
                wav_to_mp3(tmp_wav, raw)
                tmp_wav.unlink(missing_ok=True)
                ok = raw.exists()
        if not ok:
            ok = cosyvoice_builtin_tts(text, builtin, raw, cosy)
        if not ok and speaker != builtin:
            ok = cosyvoice_builtin_tts(text, speaker, raw, cosy)
        if not ok:
            raise RuntimeError(f"CosyVoice2 failed for {tid} (tried builtin={builtin!r}, alt={speaker!r}). COSYVOICE_URL={cosy}")
        print(final.name)
        ffmpeg_finalize(
            raw,
            final,
            f"Chapter 1: {TOPIC_LABEL.get(topic, topic)}",
            row["name"],
            brand_display_name(brand),
        )
        raw.unlink(missing_ok=True)


def load_brand_colors() -> dict[str, tuple[str, str, str]]:
    bi = _load_yaml(REPO_ROOT / "config/catalog_planning/brand_identity_system.yaml")
    out: dict[str, tuple[str, str, str]] = {}
    for key, row in (bi.get("teacher_brands") or {}).items():
        if not isinstance(row, dict):
            continue
        b = row.get("brand_identity") or {}
        if not isinstance(b, dict):
            continue
        prim = b.get("primary_colors") or ["#111111", "#222222"]
        acc = str(b.get("accent_color") or "#6366F1")
        c1 = str(prim[0]) if prim else "#111111"
        c2 = str(prim[1]) if len(prim) > 1 else c1
        out[key] = (c1, c2, acc)
    return out


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def render_cover_png(
    path: Path,
    *,
    w: int,
    h: int,
    title: str,
    author: str,
    brand_name: str,
    colors: tuple[str, str, str],
    mood_hex: str,
    audiobook_badge: bool,
) -> None:
    from PIL import Image, ImageDraw, ImageFont

    path.parent.mkdir(parents=True, exist_ok=True)
    c1, _c2, acc = colors
    r1, g1, b1 = hex_rgb(c1)
    r2, g2, b2 = hex_rgb(mood_hex)
    img = Image.new("RGB", (w, h))
    dr = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(r1 * (1 - t) + r2 * t)
        g = int(g1 * (1 - t) + g2 * t)
        b = int(b1 * (1 - t) + b2 * t)
        dr.line([(0, y), (w, y)], fill=(r, g, b))

    def load_font(size: int) -> ImageFont.ImageFont:
        for p in (
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ):
            if Path(p).exists():
                return ImageFont.truetype(p, size)
        return ImageFont.load_default()

    ft = load_font(72 if w >= 3000 else 48)
    fa = load_font(38 if w >= 3000 else 26)
    fs = load_font(28 if w >= 3000 else 18)
    ar, ag, ab = hex_rgb(acc)
    _, th = dr.textbbox((0, 0), title, font=ft)[2:]
    tw, _ = dr.textbbox((0, 0), title, font=ft)[2:]
    dr.text(((w - tw) // 2, int(h * 0.30)), title, font=ft, fill=(252, 252, 250))
    aw, ah = dr.textbbox((0, 0), author, font=fa)[2:]
    dr.text(((w - aw) // 2, int(h * 0.30) + th + 24), author, font=fa, fill=(235, 235, 235))
    sub = f"An audiobook — {brand_name}" if audiobook_badge else brand_name
    sw, _ = dr.textbbox((0, 0), sub, font=fs)[2:]
    dr.text(((w - sw) // 2, int(h * 0.70)), sub, font=fs, fill=(ar, ag, ab))
    if audiobook_badge:
        badge = "AUDIOBOOK"
        bx = int(w * 0.04)
        by = h - int(h * 0.08)
        dr.rectangle([bx - 12, by - 8, bx + dr.textbbox((0, 0), badge, font=fs)[2] + 12, by + 28], outline=(252, 252, 250), width=2)
        dr.text((bx, by), badge, font=fs, fill=(252, 252, 250))
    img.save(path, "PNG", optimize=True)


def run_covers(signature_only: bool) -> None:
    colors = load_brand_colors()
    topics = list(TOPIC_LABEL.keys()) if not signature_only else []
    sig_dir = REPO_ROOT / "brand-wizard-app/public/assets/covers/audiobook"
    cat_dir = REPO_ROOT / "brand-wizard-app/public/assets/covers/audiobook/catalog"
    for row in TEACHER_ROWS:
        tid = row["id"]
        topic = row["topic"]
        brand = row["brand"]
        mood = TOPIC_MOOD.get(topic, "#6366F1")
        col = colors.get(brand, ("#1e1b4b", "#312e81", "#6366F1"))
        title = TOPIC_LABEL.get(topic, topic)
        author = row["name"]
        bn = brand_display_name(brand)
        render_cover_png(
            sig_dir / f"cover_{tid}_{topic}_audiobook.png",
            w=3200,
            h=3200,
            title=title,
            author=author,
            brand_name=bn,
            colors=col,
            mood_hex=mood,
            audiobook_badge=True,
        )
        render_cover_png(
            sig_dir / f"cover_{tid}_{topic}_ebook.png",
            w=1600,
            h=2560,
            title=title,
            author=author,
            brand_name=bn,
            colors=col,
            mood_hex=mood,
            audiobook_badge=False,
        )
    if signature_only:
        return
    if not topics:
        bi = _load_yaml(REPO_ROOT / "config/catalog_planning/canonical_topics.yaml")
        topics = [str(x) for x in (bi.get("topics") or [])]
    for row in TEACHER_ROWS:
        tid = row["id"]
        brand = row["brand"]
        col = colors.get(brand, ("#1e1b4b", "#312e81", "#6366F1"))
        bn = brand_display_name(brand)
        for topic in topics:
            mood = TOPIC_MOOD.get(topic, "#6366F1")
            title = TOPIC_LABEL.get(topic, topic.replace("_", " ").title())
            render_cover_png(
                cat_dir / f"cover_{tid}_{topic}_audiobook.png",
                w=3200,
                h=3200,
                title=title,
                author=row["name"],
                brand_name=bn,
                colors=col,
                mood_hex=mood,
                audiobook_badge=True,
            )


def run_investor() -> None:
    base = REPO_ROOT / "artifacts/audiobook_samples"
    demo = REPO_ROOT / "brand-wizard-app/public/assets/audio/investor_demo"
    demo.mkdir(parents=True, exist_ok=True)
    for row in TEACHER_ROWS:
        tid = row["id"]
        topic = row["topic"]
        src = base / f"{tid}_{topic}_ch1.mp3"
        if not src.exists():
            continue
        dst = demo / f"investor_{tid}_60s.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(src), "-ss", "45", "-t", "60", "-af", "loudnorm=I=-16:TP=-1.0:LRA=11", str(dst)],
            check=True,
            capture_output=True,
        )
    clips = sorted(demo.glob("investor_*_60s.mp3"))
    if len(clips) < 2:
        return
    concat_parts: list[Path] = []
    for i, p in enumerate(clips[:13]):
        seg = demo / f"_sizzle_part_{i:02d}.mp3"
        subprocess.run(["ffmpeg", "-y", "-i", str(p), "-t", "10", str(seg)], check=True, capture_output=True)
        concat_parts.append(seg)
    list_file = demo / "_sizzle_list.txt"
    list_file.write_text("\n".join(f"file '{p.name}'" for p in concat_parts), encoding="utf-8")
    pre = demo / "_sizzle_pre.mp3"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(pre)], cwd=str(demo), check=True, capture_output=True)
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(pre), "-af", "loudnorm=I=-16:TP=-1.0:LRA=11", str(demo / "investor_sizzle_reel.mp3")],
        check=True,
        capture_output=True,
    )
    for p in concat_parts + [pre, list_file]:
        p.unlink(missing_ok=True)


def build_manifest_rows() -> None:
    prof_path = REPO_ROOT / "config/authoring/pen_name_teacher_profiles_full.json"
    n_authors = 480
    if prof_path.exists():
        try:
            n_authors = len(json.loads(prof_path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            pass
    ecapa_max = 0.0
    ecapa_p = REPO_ROOT / "artifacts/tts/ecapa_pairwise_scores.yaml"
    if yaml and ecapa_p.exists():
        data = yaml.safe_load(ecapa_p.read_text(encoding="utf-8"))
        if isinstance(data, list):
            for row in data:
                if isinstance(row, dict) and "cosine" in row:
                    ecapa_max = max(ecapa_max, float(row["cosine"]))
    base = REPO_ROOT / "artifacts/audiobook_samples"
    frag_path = base / "_prose/frag.json"
    frag_d: dict[str, str] = {}
    if frag_path.exists():
        try:
            frag_d = json.loads(frag_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    rows_out: list[dict[str, Any]] = []
    qwen_base, cosy_base = pearl_star_urls()
    for row in TEACHER_ROWS:
        tid = row["id"]
        topic = row["topic"]
        brand = row["brand"]
        locale = row["locale"]
        mp3 = base / f"{tid}_{topic}_ch1.mp3"
        pr = base / "_prose" / f"{tid}_{topic}_ch1.txt"
        spk, refp, vsrc = resolve_cosyvoice_speaker(tid, brand, locale, row=row)
        rows_out.append(
            {
                "teacher_id": tid,
                "topic": topic,
                "brand_key": brand,
                "display_name": row["name"],
                "locale": locale,
                "topic_label": TOPIC_LABEL.get(topic, topic),
                "brand_display": brand_display_name(brand),
                "positioning": positioning_for_brand(brand),
                "provenance": frag_d.get(f"{tid}__{topic}"),
                "llm": {"provider": "ollama_qwen_pearl_star", "base_url": qwen_base},
                "tts": {
                    "provider": "cosyvoice2_pearl_star",
                    "base_url": cosy_base,
                    "speaker_or_reference_id": spk,
                    "voice_resolution": vsrc,
                    "reference_wav_repo_rel": str(refp.relative_to(REPO_ROOT)) if refp and refp.is_file() else None,
                },
                "audio_rel": f"artifacts/audiobook_samples/{tid}_{topic}_ch1.mp3" if mp3.exists() else None,
                "prose_rel": str(pr.relative_to(REPO_ROOT)) if pr.exists() else None,
                "cover_audiobook_rel": f"brand-wizard-app/public/assets/covers/audiobook/cover_{tid}_{topic}_audiobook.png",
                "n_pen_name_authors_repo": n_authors,
                "ecapa_pairwise_max_repo": round(ecapa_max, 4),
            }
        )
    manifest = {
        "schema": "audiobook_showcase_manifest_v2_pearl_star",
        "persona": PERSONA,
        "teachers": rows_out,
        "cost": "0USD_all_on_pearl_star",
        "metrics": {"target_lufs": -16, "true_peak_dbtp": -1.0},
    }
    (base / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Audiobook showcase — Pearl Star Qwen + CosyVoice2")
    ap.add_argument(
        "command",
        choices=["prose", "tts", "tts-en", "covers", "covers-catalog", "investor", "manifest", "all"],
    )
    ap.add_argument(
        "--workspace",
        type=Path,
        default=None,
        help="Directory containing job.json (default: artifacts/audiobook_samples)",
    )
    ap.add_argument(
        "--no-job-check",
        dest="no_job_check",
        action="store_true",
        help="Skip job.json enforcement (CI only)",
    )
    args = ap.parse_args()
    if args.no_job_check:
        print(
            "WARNING: --no-job-check: pipeline job enforcement disabled (CI/testing only).",
            file=sys.stderr,
        )
    ab_ws = (args.workspace or (REPO_ROOT / "artifacts/audiobook_samples")).resolve()
    cmd = args.command
    from scripts.pipeline.advance_stage import mark_complete, mark_pipeline_finished
    from scripts.pipeline.check_job import require_stage

    if not args.no_job_check:
        _require = {
            "prose": "prose_gen",
            "tts": "tts_render",
            "tts-en": "tts_render",
            "covers": "cover_gen",
            "covers-catalog": "cover_gen",
            "manifest": "manifest",
            "all": "prose_gen",
        }
        rs = _require.get(cmd)
        if rs:
            require_stage(rs, ab_ws)
    if cmd == "tts-en":
        cmd = "tts"
    if cmd == "prose":
        run_generate_prose()
    elif cmd == "tts":
        run_tts_all()
    elif cmd == "covers":
        run_covers(signature_only=True)
    elif cmd == "covers-catalog":
        run_covers(signature_only=False)
    elif cmd == "investor":
        run_investor()
    elif cmd == "manifest":
        build_manifest_rows()
        if not args.no_job_check:
            mark_complete(ab_ws, "manifest", output="manifest.json")
        return 0
    elif cmd == "all":
        run_generate_prose()
        run_covers(signature_only=True)
        run_covers(signature_only=False)
        try:
            run_tts_all()
        except Exception as e:
            print(f"TTS skipped/failed: {e}", file=sys.stderr)
        try:
            run_investor()
        except Exception as e:
            print(f"investor clips skipped: {e}", file=sys.stderr)
        build_manifest_rows()
        if not args.no_job_check:
            mark_pipeline_finished(ab_ws, "audiobook")
        return 0
    if cmd in ("prose", "tts", "covers", "covers-catalog", "investor"):
        build_manifest_rows()
    if not args.no_job_check:
        fin = {
            "prose": "prose_gen",
            "tts": "tts_render",
            "tts-en": "tts_render",
            "covers": "cover_gen",
            "covers-catalog": "cover_gen",
        }.get(cmd)
        if fin:
            mark_complete(ab_ws, fin, output=cmd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
