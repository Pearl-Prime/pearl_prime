# Manga Font Registry

**Status:** v2 (PR #631 Decision 3 — CJK-first rebuild).
**Authority:** [`fonts/manga/FONT_REGISTRY.yaml`](../fonts/manga/FONT_REGISTRY.yaml).
**CI:** [`scripts/manga/check_font_registry.py`](../scripts/manga/check_font_registry.py).

## Why this exists

PR #631 (WEBTOON master reference) found that the v1 registry had **4 fonts, all status `pending`**, and only `noto_sans_jp_body` covered any CJK glyph set. With 90 of the 132 series_plans on `main` targeting non-en_US locales, **CJK font absence is a production blocker**: ja_JP / zh_TW / zh_CN renders would emit missing-glyph boxes for every dialogue line.

v2 fixes this with the standard OFL CJK + Latin-manga set used across the AI-manga industry.

## What's registered

### CJK body (Source Han Sans family, OFL)

| ID | Locale | Path | Source |
|---|---|---|---|
| `source_han_sans_jp` | ja_JP | `otf/SourceHanSansJP-Regular.otf` | [Adobe Fonts release v2.004](https://github.com/adobe-fonts/source-han-sans/releases) |
| `source_han_sans_tc` | zh_TW | `otf/SourceHanSansTC-Regular.otf` | same release |
| `source_han_sans_sc` | zh_CN | `otf/SourceHanSansSC-Regular.otf` | same release |
| `source_han_sans_kr` | ko_KR | `otf/SourceHanSansKR-Regular.otf` | same release |

### CJK display / handwritten (OFL)

| ID | Locale | Path | Source |
|---|---|---|---|
| `klee_one_jp` | ja_JP | `ttf/KleeOne-Regular.ttf` | [Google Fonts](https://fonts.google.com/specimen/Klee+One) |
| `lxgw_wenkai` | zh_TW + zh_CN | `ttf/LXGWWenKai-Regular.ttf` | [LXGW WenKai releases](https://github.com/lxgw/LxgwWenKai/releases) |

### Latin (Anime Ace + Badaboom + Google Fonts)

| ID | Role | License |
|---|---|---|
| `anime_ace_dialogue` | dialogue (en_US) | Free for commercial (Blambot) |
| `badaboom_sfx` | SFX/impact (en_US, zh_TW, zh_CN) | Free for commercial (Blambot) |
| `bangers_display` | display | OFL |
| `patrick_hand_handwritten` | handwritten | OFL |
| `architects_daughter_note` | handwritten note | OFL |
| `noto_sans_jp_body` | ja_JP fallback | OFL |

## Locale coverage requirement

Every locale in the catalog (en_US, ja_JP, zh_TW, zh_CN) **must** have at least a `body` role registered. CI (`check_font_registry.py`) enforces this — a PR that breaks coverage fails the gate.

ko_KR is registered for future use but isn't currently in `MANGA_FULL_CATALOG_PLAN.md`; Naver Webtoon Korea connector ships in Phase 2 per PR #631.

## How to install

### From a Codespace (or anywhere with network)

```bash
bash scripts/manga/install_manga_fonts.sh
```

The script:
- Downloads OFL fonts (Source Han Sans, Klee One, LXGW WenKai, Bangers, Patrick Hand, Architects Daughter, Noto Sans JP) from canonical sources via `curl`/`wget`
- Skips fonts already present at their declared path (idempotent)
- Prints **manual download instructions** for Anime Ace 2.0 BB + Badaboom BB (Blambot's free-for-commercial fonts require checkout — they're not directly hot-linkable)

### After install

```bash
python3 scripts/manga/check_font_registry.py
```

Validates registry schema + locale coverage. Lists any fonts still `status: pending` and points at the install script.

For strict CI mode (fails when any font is still pending):

```bash
python3 scripts/manga/check_font_registry.py --strict
```

## Why fonts aren't committed to the repo

- **License variance** — OFL fonts are free to redistribute, but Blambot's free-for-commercial fonts have terms that make repo-redistribution risky to interpret. Safer to fetch.
- **Repo size** — Source Han Sans alone is ~150 MB; full set ~600 MB. Layer 2 (R2 + no-binary-blobs CI) explicitly rejects this kind of binary commit.
- **Update path** — fetching at install time means we always grab the latest minor revision; committed binaries would freeze.

For Pearl Star where renders run unattended, install once at provisioning time. For Codespaces, the post-create script can opt-in via `bash scripts/manga/install_manga_fonts.sh` once R2 secrets are present (see Layer 2/3 docs).

## Status field semantics

| Status | Meaning |
|---|---|
| `pending` | Declared in registry, file not yet downloaded |
| `installed` | File present at path; sha256 not yet verified |
| `verified` | File present + sha256 matches `expected_sha256` |
| `blocked` | License issue — do not use |

The install script doesn't auto-update `status` (that's an out-of-scope follow-up). For now, `pending` after install just means "we haven't run a verification pass yet" — the actual file is there if `install_manga_fonts.sh` ran cleanly.

## Schema rules (enforced by `check_font_registry.py`)

- Every font has unique `id` and `path`
- Every font's `status` ∈ `{pending, installed, verified, blocked}`
- Every `locale_target` ∈ `{en_US, ja_JP, ko_KR, zh_TW, zh_CN}`
- Every `locale_coverage_required[<locale>].<role>` references an `id` that exists in `fonts[]`
- Every catalog locale has a `body` role assigned

## Related

- `CLAUDE.md` § LLM Tier Policy (this PR ships infra, no LLM calls)
- `docs/CLOUD_NATIVE_AGENTS.md` (Layer 1) — Codespaces post-create can call install script
- `phoenix_v4/manga/chapter/locale_resolver.py` — looks up `font_override_by_locale` per dialogue line
- `schemas/manga/lettering_spec.schema.json` v3 — `font_override_by_locale` field
- PR #631 master reference Decision 3 — the why
