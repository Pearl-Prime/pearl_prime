#!/usr/bin/env bash
# Phoenix Omega — Install all fonts from fonts/manga/FONT_REGISTRY.yaml.
# Idempotent: skips fonts already present at their declared path.
#
# Run from a Codespace OR Pearl Star OR locally — needs network access to
# canonical font sources. Does NOT commit downloaded fonts to git (license
# requirements vary; see docs/MANGA_FONT_REGISTRY.md).
#
# Usage:
#   bash scripts/manga/install_manga_fonts.sh
#
# To verify after install:
#   python3 scripts/manga/check_font_registry.py

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FONTS_DIR="${REPO}/fonts/manga"
TTF_DIR="${FONTS_DIR}/ttf"
OTF_DIR="${FONTS_DIR}/otf"

mkdir -p "${TTF_DIR}" "${OTF_DIR}"

echo "═══ Phoenix Omega — Manga font installer ═══"
echo "Target: ${FONTS_DIR}"
echo ""

download_if_missing() {
  local target="$1" url="$2" id="$3"
  if [ -f "${target}" ]; then
    echo "✓ ${id}: already present (${target##${REPO}/})"
    return 0
  fi
  echo "↓ ${id}: downloading from ${url}"
  if command -v curl >/dev/null 2>&1; then
    curl -sSL --fail -o "${target}.partial" "${url}" && mv "${target}.partial" "${target}"
  elif command -v wget >/dev/null 2>&1; then
    wget -q -O "${target}.partial" "${url}" && mv "${target}.partial" "${target}"
  else
    echo "❌ neither curl nor wget available — install one and re-run"
    return 1
  fi
  echo "  ✓ wrote ${target##${REPO}/}"
}

# ── CJK BODY: Source Han Sans family (via Noto Sans CJK OTF mirrors) ────
# Same outlines/typeface family Source Han Sans / Noto Sans CJK (see
# FONT_REGISTRY + Adobe/Google pairing docs).

NOTO_SANS_CJK_OTF="https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF"

download_if_missing "${OTF_DIR}/SourceHanSansJP-Regular.otf" \
  "${NOTO_SANS_CJK_OTF}/Japanese/NotoSansCJKjp-Regular.otf" \
  source_han_sans_jp

download_if_missing "${OTF_DIR}/SourceHanSansTC-Regular.otf" \
  "${NOTO_SANS_CJK_OTF}/TraditionalChinese/NotoSansCJKtc-Regular.otf" \
  source_han_sans_tc

download_if_missing "${OTF_DIR}/SourceHanSansSC-Regular.otf" \
  "${NOTO_SANS_CJK_OTF}/SimplifiedChinese/NotoSansCJKsc-Regular.otf" \
  source_han_sans_sc

download_if_missing "${OTF_DIR}/SourceHanSansKR-Regular.otf" \
  "${NOTO_SANS_CJK_OTF}/Korean/NotoSansCJKkr-Regular.otf" \
  source_han_sans_kr

# Flat FONT_REGISTRY paths under fonts/manga/
download_if_missing "${FONTS_DIR}/source_han_sans_jp.otf" \
  "${NOTO_SANS_CJK_OTF}/Japanese/NotoSansCJKjp-Regular.otf" \
  source_han_jp_flat
download_if_missing "${FONTS_DIR}/source_han_sans_tc.otf" \
  "${NOTO_SANS_CJK_OTF}/TraditionalChinese/NotoSansCJKtc-Regular.otf" \
  source_han_tc_flat
download_if_missing "${FONTS_DIR}/source_han_sans_sc.otf" \
  "${NOTO_SANS_CJK_OTF}/SimplifiedChinese/NotoSansCJKsc-Regular.otf" \
  source_han_sc_flat
download_if_missing "${FONTS_DIR}/source_han_sans_kr.otf" \
  "${NOTO_SANS_CJK_OTF}/Korean/NotoSansCJKkr-Regular.otf" \
  source_han_kr_flat

# ── CJK DISPLAY: Klee One JP, LXGW WenKai ───────────────────────────────
# Klee One via Google Fonts API
download_if_missing "${TTF_DIR}/KleeOne-Regular.ttf" \
  "https://github.com/google/fonts/raw/main/ofl/kleeone/KleeOne-Regular.ttf" \
  klee_one_jp

# LXGW WenKai — direct release asset
download_if_missing "${TTF_DIR}/LXGWWenKai-Regular.ttf" \
  "https://github.com/lxgw/LxgwWenKai/releases/latest/download/LXGWWenKai-Regular.ttf" \
  lxgw_wenkai

# ── Latin: Bangers, Patrick Hand, Architects Daughter, Noto Sans JP ─────
download_if_missing "${TTF_DIR}/Bangers-Regular.ttf" \
  "https://github.com/google/fonts/raw/main/ofl/bangers/Bangers-Regular.ttf" \
  bangers_display

download_if_missing "${TTF_DIR}/PatrickHand-Regular.ttf" \
  "https://github.com/google/fonts/raw/main/ofl/patrickhand/PatrickHand-Regular.ttf" \
  patrick_hand_handwritten

download_if_missing "${TTF_DIR}/ArchitectsDaughter-Regular.ttf" \
  "https://github.com/google/fonts/raw/main/ofl/architectsdaughter/ArchitectsDaughter-Regular.ttf" \
  architects_daughter_note

download_if_missing "${TTF_DIR}/NotoSansJP-Regular.otf" \
  "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf" \
  noto_sans_jp_body

# ── Comic Neue — bundled OFL substitute for Anime Ace 2.0 (Blambot) ──────
# Blambot's Anime Ace cannot be fetched non-interactively, so en_US dialogue
# would otherwise fall back to ImageFont.load_default() (ugly bitmap) on a
# clean box. Comic Neue is an OFL-licensed, redistributable manga-style
# dialogue face registered as the en_US body/dialogue fallback in
# FONT_REGISTRY.yaml so production NEVER hits the default bitmap font.
download_if_missing "${TTF_DIR}/ComicNeue-Regular.ttf" \
  "https://github.com/google/fonts/raw/main/ofl/comicneue/ComicNeue-Regular.ttf" \
  comic_neue_dialogue
download_if_missing "${TTF_DIR}/ComicNeue-Bold.ttf" \
  "https://github.com/google/fonts/raw/main/ofl/comicneue/ComicNeue-Bold.ttf" \
  comic_neue_dialogue_bold

# ── Anime Ace 2.0 + Badaboom (Blambot) — OPTIONAL upgrade ───────────────
# Blambot's free fonts are hosted on their site behind an interactive cart;
# direct download URLs are not stable, so they cannot be fetched here.
# These are an OPTIONAL aesthetic upgrade — the OFL substitutes already
# registered (Comic Neue for dialogue, Bangers for SFX) guarantee a real
# font is always available. Install Blambot fonts only if you want the
# canonical look; the registry will prefer them automatically when present.
echo ""
echo "── Optional manual upgrade (OFL substitutes already cover these) ──"
echo "Anime Ace 2.0 BB (preferred en_US dialogue; substitute = Comic Neue):"
echo "  1. https://blambot.com/products/anime-ace-2-0-bb"
echo "  2. Click 'Add to cart' (free), checkout, get download link"
echo "  3. Place AnimeAce2.0BB.ttf at: ${TTF_DIR}/AnimeAce2.0BB.ttf"
echo ""
echo "Badaboom BB (preferred en_US SFX; substitute = Bangers):"
echo "  1. https://blambot.com/products/badaboom-bb"
echo "  2. Same checkout flow"
echo "  3. Place BadaboomBB.ttf at: ${TTF_DIR}/BadaboomBB.ttf"
echo ""

# ── Final report ────────────────────────────────────────────────────────
echo ""
echo "═══ Install summary ═══"
echo "OTF dir: ${OTF_DIR}"
ls -la "${OTF_DIR}" 2>/dev/null | tail -n +2 || echo "  (empty)"
echo ""
echo "TTF dir: ${TTF_DIR}"
ls -la "${TTF_DIR}" 2>/dev/null | tail -n +2 || echo "  (empty)"
echo ""
echo "Run check_font_registry.py to verify coverage:"
echo "  python3 scripts/manga/check_font_registry.py"
