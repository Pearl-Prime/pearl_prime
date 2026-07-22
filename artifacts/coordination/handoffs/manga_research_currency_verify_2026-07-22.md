# Handoff — manga_research_currency_verify_20260722

**From:** Pearl_QA
**Full audit:** `artifacts/qa/manga_research_currency_audit_2026-07-22.md`

## What this lane found (short version)

1. The premise that `genre_prompt_cookbook_v2.yaml` might be a stale predecessor
   of `genre_prompt_cookbook.yaml` (v3) is **incorrect** — they cover different
   domains. v3 = manga panels (research-backed, LIVE everywhere in the canonical
   chapter DAG). v2 = KDP self-help book covers (FLUX, LIVE for covers only).
   Nothing needs to change about which cookbook the manga render path reads —
   it already reads v3 exclusively, confirmed by full import trace.

2. `scripts/manga/cookbook_v2_compose_prompt.py` (the compose **script**, not
   the YAML) is confirmed **dead code** — zero reachable callsites outside its
   own test. Header marker added this lane. Not deleted (needs operator
   sign-off per lane's DO NOT instructions).

3. **Real content gap found, not actioned here:** 11 of 26 genres in
   `config/manga/drawing_tradition_per_genre.yaml` (`battle`, `sports`, `horror`,
   `essay`, `food`, `family`, `cultivation`, `sci_fi_cyberpunk`, `school`,
   `memoir`, `battle_internal`) have only a single-engine `H_token_mapping`
   stub (`animagine_starter` or `flux_schnell_starter`) with **no `qwen_image`
   key**, even though `genre_prompt_cookbook.yaml` (v3) explicitly declares
   `preferred_model: qwen_image` for all 11. At render time this silently
   falls through to generic-synthesis tokens instead of curated ones — a live
   quality degradation for those 11 genres on every panel rendered.

## Next action for whoever picks this up

Author `qwen_image` `H_token_mapping.positive` / `.negative` entries for the
11 genres listed above in `config/manga/drawing_tradition_per_genre.yaml`,
matching the curated quality of the 8 genres that already carry all three
engine keys (`healing`, `dark_fantasy`, `psychological_horror`, `mecha`,
`romance`, `slice_of_life`, `fantasy_adventure`, `comedy`). This is prompt-craft
authoring (per-genre operator-curated strings), not a mechanical fix — route
to a Tier-1 Claude Code session with manga genre-prompt context, not an
automated pass.

Secondary/low-priority: `artifacts/research/MANGA_GENRE_PROMPTING_SYSTEM_RESEARCH_2026-07-10.md`
line 71 says `genre_prompt_cookbook.yaml` "does not exist on origin/main" — it
exists today (dated one day before that research doc). One-line doc
correction, no render-path impact.

## Cleanup ledger

- Read-only trace lane; no destructive changes made.
- One header-comment edit: `scripts/manga/cookbook_v2_compose_prompt.py`
  (STATUS marker only, verified `pytest tests/test_cookbook_v2_loader.py` still
  passes 10/10 after the edit).
- No config YAML files edited (deliberately — `genre_prompt_cookbook_v2.yaml`
  has a genuine live consumer and marking it unwired would be false; see audit
  §"Callsite trace: genre_prompt_cookbook_v2.yaml").
- Two new files added: the audit artifact and this handoff doc.
