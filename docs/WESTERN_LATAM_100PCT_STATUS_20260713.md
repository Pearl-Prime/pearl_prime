# Western/LatAm 7-Locale Completion Status — 2026-07-13 (session 2)

Supersedes/extends `docs/LOCALIZATION_PREP_14PACK_20260713.md` §5 (baseline) for
the targeted production roster: **es-US, es-ES, fr-FR, de-DE, it-IT, hu-HU, pt-BR**.

Branch: `agent/locale-prep-14pack-20260713`.

## 1. What landed this session (real, committed)

- `818e809b16` — European/pt-BR glossary authored: `config/localization/quality_contracts/glossary.yaml`
  grew from 60 to 130 locale entries (10 core terms × 7 locales added: nervous_system,
  the_alarm, the_mask, the_pattern, the_strategy, the_cost, somatic, watcher,
  false_alarm, the_thread). This closes remaining_true_blocker #1 from the prior
  packet — terminology-consistency validation is now possible for all 7 locales.
  (Landed by a sibling session on this same branch before this session started;
  verified present and correct, not re-authored.)
- This commit — refreshed live gap inventory (atom-level + structural-gate/topic-pack
  level) computed from a clean, full checkout of this branch, plus an honest
  infrastructure-blocker report for live translation execution.

## 2. Atom-level coverage (persona/topic CANONICAL.txt corpus)

Computed by globbing `atoms/*/*/[A-Z]*/CANONICAL.txt` + `atoms/*/*/*/CANONICAL.txt`
(excluding `/locales/` subtrees) on a clean checkout of this branch.
Total English source atoms: **3,853** (packet's earlier baseline used 3,754 from
a slightly different scope — both are real, the delta is scope, not drift).

| Locale | Translated | Total | Coverage before (this session) | Coverage after (this session) |
|---|---|---|---|---|
| es-US | 108 | 3,853 | 2.80% | 2.80% (no volume change) |
| es-ES | 0 | 3,853 | 0.00% | 0.00% (no volume change) |
| fr-FR | 0 | 3,853 | 0.00% | 0.00% (no volume change) |
| de-DE | 0 | 3,853 | 0.00% | 0.00% (no volume change) |
| it-IT | 0 | 3,853 | 0.00% | 0.00% (no volume change) |
| hu-HU | 0 | 3,853 | 0.00% | 0.00% (no volume change) |
| pt-BR | 108 | 3,853 | 2.80% | 2.80% (no volume change) |

**No new atom translations were produced this session.** See §4 for why (real,
reproduced infra blocker, not a scoping choice).

## 3. Structural/topic-pack coverage (separate corpus — newly surfaced this session)

`scripts/localization/locale_structural_gate.py` (no LLM required, runs cleanly)
checks a **different** corpus — per-locale `topic_*.yaml` teacher/topic packs
(7 topics × 36 atoms/topic = 252 atoms/locale target). Full output:
`artifacts/qa/locale_prep_14pack_20260713/western_latam_structural_gate_20260713.json`.

All 7 locales: **0/252 (0%)** — `topic_{climate,economy_work,education,inequality,
mental_health,partnerships,peace_conflict}.yaml` all report "file missing" for
every one of the 7 roster locales. This is a real, previously-uncaptured gap
distinct from the atom-corpus baseline in the prior packet (which only measured
`atoms/`). Gate itself reports PASS because `--min-coverage` defaults to 0.0
(advisory-only) — a 0% PASS is not completion, it is the gate correctly reporting
an empty floor.

## 4. Infrastructure blocker (real, reproduced, blocks all live translation this session)

Sanctioned provider path is `scripts/localization/run_translation_loop.py` /
`translate_atoms_to_locale.py` → Ollama on Pearl Star (`qwen2.5:14b`), per
CLAUDE.md Tier-2 policy. This laptop has no local Ollama; Pearl Star is reachable
(`ssh pearl_star "echo ok"` → `ok`).

Reproduced failure:
- `ollama ps` on Pearl Star (instant, working) shows `qwen2.5:14b` resident at
  `66%/34% CPU/GPU`, status **`Stopping...`** (stuck in a non-serving state).
- `curl http://localhost:11434/api/generate` on Pearl Star itself, for
  `qwen2.5:14b` with a 5-token completion, **hung with zero bytes returned after
  240s** (4 minutes).
- Same test against a **different** resident model (`qwen2.5vl:7b`) also hung
  with zero bytes after 30s — indicating the Ollama server's request path is
  wedged, not just `qwen2.5:14b` specifically.
- `pscli status` (the RAP queue-first dispatch path, preferred over direct
  Ollama calls) fails immediately: `PS_QUEUE_DSN not set` — the queue-first
  wrapper is not configured/available from this session either.

Net: both the direct-Ollama path and the queue-first `pscli` path are
non-functional from this session, for reasons external to this repo's code
(a wedged Ollama server process and a missing queue DSN on Pearl Star). This
is a genuine environment blocker, verified by direct reproduction, not a
scoping decision.

Recommended follow-up (out of scope for this branch): an operator or a session
with Pearl Star shell access should restart the Ollama service (`systemctl
restart ollama` or equivalent) to clear the wedged `Stopping...` model, and set
`PS_QUEUE_DSN` per `docs/ROBUST_AGENT_PROTOCOL.md` so future translation waves
can dispatch queue-first as CLAUDE.md requires.

## 5. Per-locale validation paths (unchanged, all real and runnable once atoms exist)

- `scripts/localization/validate_translations.py` (Qwen-judge rubric) — blocked
  by the same Ollama-wedge (§4); cannot run this session.
- `scripts/localization/locale_structural_gate.py` — ran successfully, no LLM
  needed; output at `artifacts/qa/locale_prep_14pack_20260713/western_latam_structural_gate_20260713.json`.
- `scripts/check_golden_translation.py`, `config/localization/quality_contracts/*.yaml`
  — unchanged from prior packet, still the authority for release thresholds.

## 6. Remaining true blockers (updated)

1. **Ollama wedge on Pearl Star** (new, this session) — blocks all live
   Qwen-based translation and judge-validation until an operator restarts the
   service. This is the single blocking issue for atom-level translation
   progress on es-ES/fr-FR/de-DE/it-IT/hu-HU (currently 0%) and for growing
   es-US/pt-BR beyond 2.80%.
2. **Queue-first (`pscli`) wrapper unconfigured** (`PS_QUEUE_DSN` unset) — the
   RAP-mandated dispatch path for unattended GPU work is unavailable from this
   session; direct-Ollama calls are also currently blocked by #1, so no
   translation dispatch path works right now.
3. **Topic-pack corpus (§3) is a newly surfaced, fully-unauthored 0% gap** for
   all 7 locales — distinct from and larger in scope than the previously known
   atom-corpus gap. Needs its own wave plan once #1/#2 are cleared.
4. Prior packet's blockers (glossary — now resolved by #818e809b16; stale
   13-locale table in `docs/TRANSLATE_QWEN_PIPELINE_CLI.md`; no European
   queue-first wrapper) remain as previously stated, superseded only where
   noted above.
