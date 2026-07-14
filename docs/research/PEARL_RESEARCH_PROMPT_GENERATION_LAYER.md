# Pearl_Research Prompt Generation Layer

**Purpose:** Turn a whole messy Phoenix Omega chat/session into a structured
research brief and provider-specific deep-research prompts before Pearl_Research
does any actual research.

This mirrors the operator workflow:

```text
messy context -> strong research brief -> provider-native deep research prompt -> downstream research engine
```

## Where It Lives

- Builder: `scripts/research/research_prompt_builder.py`
- Runner integration: `scripts/research/run_research.py --prepare-deep-research-prompt`
- Routing config: `config/research/deep_research_prompt_routing.yaml`
- Prompt templates: `research/prompts/meta/deep_research_*_prompt.md`
- Brief-generation reference prompt: `research/prompts/meta/research_brief_generation_prompt.md`
- Evaluation harness: `scripts/research/evaluate_prompt_generation.py`
- Evaluation cases: `scripts/research/examples/prompt_generation_cases.yaml`
- Generated examples: `artifacts/research/prompt_generation_examples/`

## What The Brief Extracts

The builder reads the full transcript/context plus optional issue text,
failing outputs, relevant repo files, and market/platform hints. It emits a
YAML research brief with:

- what is broken
- the decision to make
- unknowns and missing evidence
- exact questions to answer
- hypotheses to test
- constraints and explicit exclusions
- markets, locales, and platforms
- source rules
- Phoenix Omega implementation context
- routing preview

The builder is deterministic and offline; it does not perform downstream
research and does not call an LLM.

## Production Contract

Pearl_Research must generate a prompt package before downstream research when
the input is messy, implementation-adjacent, regional, or decision-oriented.
Do not paste a raw chat/session directly into a generic research prompt.

The only direct `run_research.py` execution path that may skip the package is
the legacy Pearl News feed-extraction lane, and it must opt in explicitly with
`--allow-legacy-direct-run` or `PEARL_RESEARCH_ALLOW_LEGACY_DIRECT_RUN=1`.

## Routing

Routing is explicit and editable in
`config/research/deep_research_prompt_routing.yaml`.

- China / `zh-CN` / China-native platforms -> Qwen / QuinChat-style prompt.
- Japan / `ja-JP` / Japan-native platforms -> Rakuten Chat AI / Japan-native prompt.
- Global, US, Europe, LATAM, or ambiguous work -> Gemini Deep Research prompt.

Explicit `--brief-market`, `--brief-locale`, and `--brief-platform` hints take
precedence over noisy transcript mentions. If an operator says the market is
Global but the transcript mentions old China/Japan examples, the package should
still recommend Gemini.

The prompt package always includes all variants:

- `master`
- `gemini`
- `qwen_china`
- `rakuten_japan`

The recommended provider is stored separately in `<stem>_routing.yaml` so the
operator can inspect or override it.

## How To Generate A Brief And Prompts

```bash
python3 scripts/research/run_research.py \
  --prompt-id semantic_trend \
  --paste path/to/full_session.txt \
  --prepare-deep-research-prompt \
  --brief-issue "Phoenix Omega needs a decision-grade prompt for the social pipeline." \
  --brief-market Global \
  --brief-locale en-US \
  --brief-platform "YouTube Shorts" \
  --brief-platform Instagram \
  --brief-platform TikTok \
  --brief-source-preference "official platform docs" \
  --brief-exclude "generic content marketing advice" \
  --output-stem global-social-media-pipeline
```

Default output directory:

```text
artifacts/research/prompt_packages/
```

The recommended prompt is listed in the generated `<stem>_INDEX.md`.

## Done Before Research Execution

Before opening Gemini, Qwen/QuinChat, Rakuten, ChatGPT, or Claude, confirm the
package directory contains:

- `<stem>_research_brief.yaml`
- `<stem>_routing.yaml`
- `<stem>_master_prompt.md`
- `<stem>_gemini_prompt.md`
- `<stem>_qwen_china_prompt.md`
- `<stem>_rakuten_japan_prompt.md`
- `<stem>_INDEX.md`

Then open `<stem>_routing.yaml` or `<stem>_INDEX.md`, choose the recommended
compiled prompt, and paste that provider-specific prompt into the downstream
research engine. The prompt package is complete only when the route is
inspectable, the recommended provider is named, and all four prompt variants are
present.

## Evaluation

Run:

```bash
python3 scripts/research/evaluate_prompt_generation.py
```

This creates before/after artifacts for:

- China self-help audio discovery -> Qwen / QuinChat-style prompt
- Japan LINE and Rakuten funnel -> Rakuten/Japan-native prompt
- Global social media pipeline -> Gemini prompt

The generated `SUMMARY.md` reports checklist scores for the old direct runner
prompt vs. the new brief/compiler prompt. It is an evaluation of prompt quality,
not completed research.
