# PR Backlog Clear — Prompt Pack

## Program

- Goal: drive the open-PR count on `Ahjan108/phoenix_omega_v4.8` from **1,609 open** toward zero, safely — merge everything mergeable, reconcile everything stale, escalate only genuine conflicts.
- Source request: operator invoked the Phoenix Omega agent prompt router in PROMPT-PACK MODE ("clear the PR backlog") — 2026-07-14.
- Router date: 2026-07-14
- Live origin/main anchor at pack authoring time: verify live with `git rev-parse origin/main` — treat any SHA quoted in this pack as stale the moment you read it (Router Operating Principles v3 §10/§11). `docs/PROGRAM_STATE.md` last-verified anchor at authoring time was `d8532d2d43874051b90201bda8b07eab5c1ce817` (2026-07-11) — three days stale relative to this pack; re-verify.
- Prompt count: **17** (1 master dispatcher + 16 lane prompts: 01 foundation, 11 catalog-locale merge sweeps covering 13 locale-scopes, 16 Enhancement Contract V2.1 chain, 17 mergeable-singles sweep, 18 stale/conflicting reconciliation, 19 final auditor)
- Master dispatcher: [00_MASTER_DISPATCH_PROMPT.md](00_MASTER_DISPATCH_PROMPT.md)

## Backlog Shape (verified via `gh api search/issues`, 2026-07-14)

- **Total open PRs: 1,609**
- **Catalog skeleton batch PRs: ~1,577** — `feat(catalog): <locale> skeletons <topic> batch <N>` — additive-only YAML under `config/source_of_truth/book_plans_<locale>/`, one file set per topic per batch, **no cross-PR file overlap within or across locales**. Breakdown by locale (title-substring count, re-verify live — this is a snapshot):
  | Locale | Open batch PRs (snapshot) | Lane |
  | --- | --- | --- |
  | it_IT | 374 | 09 |
  | pt_BR | 240 | 08 |
  | es_US | 208 | 12 |
  | hu_HU | 169 | 07 |
  | de_DE | 89 | 13 |
  | zh_CN | 77 | 02 |
  | zh_SG | 72 | 03 |
  | zh_HK | 72 | 04 |
  | zh_TW | 72 | 05 |
  | ja_JP | 72 | 06 |
  | ko_KR | 72 | 06 (combined — see lane 06 note) |
  | fr_FR | 44 | 14 |
  | en_US | 6 | 08 (combined — see lane 08 note) |
  | es_ES | 6 | 12 (combined — see lane 12 note) |

  (Lane numbering below is the authoritative mapping — the table above is grouped for readability; each locale still gets its own PRE-REQUISITE gate and its own CLOSEOUT_RECEIPT inside a shared lane file where two locales are combined for very small counts.)
- **Non-catalog PRs: 32** — split three ways:
  - **9 clean/MERGEABLE, self-contained** (small, real work, no conflicts per live `mergeable` field at authoring time): #4502, #4565, #4641, #4669, #4724, #4744, #4861, #5612, and the sequential Enhancement Contract V2.1 chain #5581→#5585→#5595 (3 of these 4 are MERGEABLE; #5596 is CONFLICTING — see below).
  - **1 sequential feature chain**: #5581 → #5585 → #5595 → #5596 (Enhancement Contract V2.1 — writer refit → AUTHOR_DISCLOSURE overlay → golden-scope fix → trace-audit fix). Must land in order; #5596 is CONFLICTING and needs a rebase as part of the lane.
  - **~21 CONFLICTING/UNKNOWN, several very old** (#1276 from 2026-05, #1429, #1536, #1628, #1778, #1796 explicitly marked `[PR-NOT-MERGE: review]`, #1812, #1874, #1878, #2792, #3097, #3166 explicitly marked `[DO NOT MERGE until Jul 1 reset]`, #3533, #4573, #4643, #4723, #5206, #5237, #5295, #5518) — likely partially superseded by main; needs git-first stale reconciliation (§6/§11), not fresh conflict resolution.

## Wave Order

- **Wave 0** — Foundation & Triage (lane 01): live PR census, disk/push-guard/governance precheck, sibling-agent collision check, confirms the counts above are still accurate before anything merges.
- **Wave 1** — Independent parallel lanes (lanes 02–14, 16, 17): 14 catalog-locale merge sweeps + the Enhancement Contract V2.1 chain + the mergeable-substantive sweep. No two lanes share a hot file (locale directories are disjoint; #5581/#5585/#5595/#5596 touch `config/authoring/`, `SOURCE_OF_TRUTH/accent_banks/`, `phoenix_v4/planning/accent_planner.py` — disjoint from all catalog lanes and from lane 17's PR set).
- **Wave 2** — Stale/Conflicting reconciliation (lane 18): runs after Wave 1 lands so it diffs against a settled `origin/main`, not a moving target. Every one of the ~21 old PRs gets a verdict: MERGE (rebased), CLOSE-AS-SUPERSEDED (with the supplanting SHA cited), or ESCALATE (genuine operator-tier call, e.g. #3166's Jul-1 budget gate, #1796's explicit review-hold).
- **Wave 4** — Final auditor (`19_Pearl_PM_final_auditor.md`): re-count open PRs live, update `docs/PROGRAM_STATE.md` and `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`, produce the program closeout.

(No Wave 1.5 or Wave 3 — this program has no visual/render/QA-coverage lanes; it is pure git-ops.)

## Lane Matrix

| Prompt | Agent | Lane | Owner | Substrate | Depends on | Output tags | Hot files |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | Pearl_GitHub | Foundation & Triage | Pearl_PM | github_actions | none | triage report, gate signals | none (read-only) |
| 02 | Pearl_GitHub | zh_CN catalog merge sweep | Pearl_GitHub | github_actions | 01 | merged PR list | `config/source_of_truth/book_plans_zh_cn/**` |
| 03 | Pearl_GitHub | zh_SG catalog merge sweep | Pearl_GitHub | github_actions | 01 | merged PR list | `config/source_of_truth/book_plans_zh_sg/**` |
| 04 | Pearl_GitHub | zh_HK catalog merge sweep | Pearl_GitHub | github_actions | 01 | merged PR list | `config/source_of_truth/book_plans_zh_hk/**` |
| 05 | Pearl_GitHub | zh_TW catalog merge sweep | Pearl_GitHub | github_actions | 01 | merged PR list | `config/source_of_truth/book_plans_zh_tw/**` |
| 06 | Pearl_GitHub | ja_JP + ko_KR catalog merge sweep | Pearl_GitHub | github_actions | 01 | merged PR list | `config/source_of_truth/book_plans_{ja_jp,ko_kr}/**` |
| 07 | Pearl_GitHub | hu_HU catalog merge sweep | Pearl_GitHub | github_actions | 01 | merged PR list | `config/source_of_truth/book_plans_hu_hu/**` |
| 08 | Pearl_GitHub | pt_BR + en_US catalog merge sweep | Pearl_GitHub | github_actions | 01 | merged PR list | `config/source_of_truth/book_plans_{pt_br,en_us}/**` |
| 09 | Pearl_GitHub | it_IT catalog merge sweep | Pearl_GitHub | github_actions | 01 | merged PR list | `config/source_of_truth/book_plans_it_it/**` |
| 12 | Pearl_GitHub | es_US + es_ES catalog merge sweep | Pearl_GitHub | github_actions | 01 | merged PR list | `config/source_of_truth/book_plans_{es_us,es_es}/**` |
| 13 | Pearl_GitHub | de_DE catalog merge sweep | Pearl_GitHub | github_actions | 01 | merged PR list | `config/source_of_truth/book_plans_de_de/**` |
| 14 | Pearl_GitHub | fr_FR catalog merge sweep | Pearl_GitHub | github_actions | 01 | merged PR list | `config/source_of_truth/book_plans_fr_fr/**` |
| 16 | Pearl_Dev | Enhancement Contract V2.1 chain (#5581→5585→5595→5596) | Pearl_Dev | github_actions | 01 | 4 merge SHAs | `config/authoring/**`, `SOURCE_OF_TRUTH/accent_banks/**`, `phoenix_v4/planning/accent_planner.py`, `docs/ENHANCEMENT_CONTRACT_V2_WORKING_PRIORS_2026-07-13.md` |
| 17 | Pearl_GitHub | Mergeable substantive singles (#4502,#4565,#4641,#4669,#4724,#4744,#4861,#5612) | Pearl_GitHub | github_actions | 01 | 8 merge SHAs or BLOCKED verdicts | varies per PR — see lane file |
| 18 | Pearl_GitHub | Stale/conflicting reconciliation (~21 PRs) | Pearl_Architect | github_actions | 02–14, 16, 17 all landed | per-PR verdict table | varies per PR — see lane file |
| 19 | Pearl_PM | Final auditor + PROGRAM_STATE update | Pearl_PM | github_actions | 18 | closeout packet | `docs/PROGRAM_STATE.md`, `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` |

## Deconfliction

- Open PRs checked: `gh api search/issues?q=repo:Ahjan108/phoenix_omega_v4.8+is:pr+is:open` → 1,609 total, live at authoring time; re-verify at Wave 0.
- Active workstreams checked: `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` — no existing row claims a locale catalog merge sweep or this PR-backlog program; lane 01 registers a new row before Wave 1 launches.
- Shared files: none across catalog lanes (disjoint locale directories). Lane 16 and lane 17 touch disjoint subsystems from all catalog lanes. `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` and `docs/PROGRAM_STATE.md` are the two hot coordination files every lane appends to — serialize writes to these per §"Serial lane on hot governance file" (one lane commits, the next rebases before writing, never concurrent edits).
- Serialization rules: catalog lanes (02–14) run fully in parallel — zero shared files. Lane 16 (Enhancement Contract chain) is internally sequential (#5581 must merge before #5585 rebases on it, etc.) but is independent of every other Wave 1 lane. Lane 18 must not start until every Wave 1 lane reports MERGED or BLOCKED, because it diffs stale PRs against `origin/main` and a moving target invalidates its verdicts.

## Evidence Requirements

- Tests: each catalog batch PR's own CI (`Verify governance`, `Drift detectors`, catalog schema checks) must be green before merge — no bypass, no `--no-verify` push, no admin-merge override.
- Proof roots: `gh pr view <n> --json statusCheckRollup` captured per merged PR; full before/after open-PR counts captured in lane 01 and lane 19.
- PR/merge signals: `catalog-merge-sweep-<locale>=<count merged>/<count total>` per catalog lane; `enhancement-contract-v21-landed=<4 merge SHAs>` for lane 16; `pr-backlog-clear=<final open count>` for lane 19.
- Operator approvals: any PR lane 18 cannot resolve to MERGE or CLOSE-AS-SUPERSEDED with confidence (e.g. #3166's budget-gate condition, #1796's explicit hold, #4573's peak-requirements SSOT which per project memory "lives on OPEN #4573" and may be intentionally unmerged) escalates via Q-<TAG>-NN with a recommended default — never force-closed or force-merged.
- Final audit: lane 19 re-runs the same `gh api search/issues` census used to open this pack and reports the delta.

## Cleanup Requirements

Every lane must report:

- worktree removed or HOLD path/reason (most lanes here are pure `gh pr merge` calls and need no worktree at all — declare `worktree: none-needed` where true);
- local branch deleted or HOLD reason (n/a for lanes that only merge/close PRs via `gh`, never checking out locally);
- remote branch deleted after merge (`gh pr merge --delete-branch` is the default for every catalog batch merge — 1,577 stale `ci/catalog-*` branches must not survive this program);
- scratch files removed (`/tmp` triage lists, PR-list dumps);
- background jobs stopped or declared (none expected — this program is `gh`-CLI driven, not long-running compute);
- handoff file path per lane under `artifacts/coordination/handoffs/`.

## Final Status

- Status: **prompt pack prepared, not yet executed.** No lane has been dispatched by the router.
- Blockers: none at authoring time — all 19 lanes are ready to launch pending operator paste into the lead cloud agent.
- Next action: paste `00_MASTER_DISPATCH_PROMPT.md` into the lead cloud chat.
