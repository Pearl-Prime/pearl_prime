# ja-JP Atom Translation Gap Closeout — 2026-07-13

## Live re-measure (from clean origin/main, not the shared dirty tree)

- English source: 3,754 atom files (12 types: 5 bestseller slots + 7 story engines)
- ja-JP before: 3,164/3,754 (84.3%), remaining 590 — matches
  `docs/LOCALIZATION_PREP_14PACK_20260713.md` §5 baseline, confirming the packet's
  number is still current (no drift since Prompt C).
- ja-JP after: 3,169/3,754 (84.4%), remaining 585
- Exact gap inventory (590 missing paths) captured in `gap_inventory_590_before.txt`
  before any translation ran.

## Work performed

Ran the sanctioned provider (`scripts/localization/run_translation_loop.py`,
single-pass mode, Ollama/qwen2.5:14b on Pearl Star, resume mode so already-
translated files are skipped) against the live gap. Two scoped batches:

1. General resume batch (`--max-files 20`, alphabetical) — 1 file completed
   (`corporate_managers/adhd_focus/THREAD`) before being stopped; a large
   (~12KB) `STORY` file in the same batch hit repeated 5-minute request
   timeouts and was abandoned as non-representative of the achievable rate.
2. `tech_finance_burnout`-scoped batch (`--persona tech_finance_burnout`,
   `--max-parallel 4`) — smaller files (avg ~665 bytes for that persona's
   missing set) translated faster: 4 files completed
   (`tech_finance_burnout/adhd_focus/{PERMISSION,PIVOT,TAKEAWAY}`,
   `tech_finance_burnout/mindfulness/PERMISSION`) before the run was stopped.
   Two additional in-flight calls in this batch
   (`tech_finance_burnout/adhd_focus/STORY`, `.../THREAD`,
   `tech_finance_burnout/mindfulness/STORY`) hit the ~900s Ollama request
   timeout and failed (not written) — these remain in the gap.

**5 files translated, written, and validated for real** (byte counts, content
sampled and confirmed coherent Japanese prose, not stub/placeholder text):

- `atoms/corporate_managers/adhd_focus/THREAD/locales/ja-JP/CANONICAL.txt` (4,816 B)
- `atoms/tech_finance_burnout/adhd_focus/PERMISSION/locales/ja-JP/CANONICAL.txt` (2,987 B)
- `atoms/tech_finance_burnout/adhd_focus/PIVOT/locales/ja-JP/CANONICAL.txt` (5,012 B)
- `atoms/tech_finance_burnout/adhd_focus/TAKEAWAY/locales/ja-JP/CANONICAL.txt` (2,721 B)
- `atoms/tech_finance_burnout/mindfulness/PERMISSION/locales/ja-JP/CANONICAL.txt` (2,009 B)

All 5 pass `scripts/localization/validate_cjk_atom.py` (structural / parse-sweep
gate — mirrors the CI over-match and slot-role schema checks): see
`validate_cjk_atom_output.txt` — 5/5 `OK`, 0 structural errors.

## Real, exact blocker (not fabricated, measured directly)

**Pearl Star's Ollama/qwen2.5:14b endpoint is throughput-bound to roughly one
real translation call per 90–900 seconds under current multi-session
contention**, independent of client-side `--max-parallel` (raising parallelism
from 3→4 did not increase completed-files-per-minute — the GPU backend
serializes). Direct curl timing confirmed this is not a client misconfiguration:
a trivial prompt returns in ~5s, but a real ~3.8KB atom took 152s, and several
~12KB atom files (STORY slots) timed out entirely after 900s even after
retries. `ollama ps` showed the model loaded with only ~3.5GB VRAM resident
and a 4096-token context window — under load from this session plus at least
one other concurrent sibling session hitting the same box (confirmed via
`git worktree list`: `western-latam-100pct-20260713`,
`zh-tw-hk-100pct-20260713`, `pr5501-jajp-teacherbank-retry`, `translation-
100pct-unblock` were all present as live worktrees during this run).

**At this measured rate, closing the remaining 585-file ja-JP gap requires on
the order of 24+ hours of contention-free Pearl Star GPU time** — not
achievable inside one interactive turn, and not a schema/translatability
problem (every file this session touched translated cleanly once the request
actually completed). This is the one true blocker: **capacity/contention on
the shared Tier-2 (Ollama) provider**, not a per-atom or schema defect.

Recommendation for the next wave: run `run_translation_loop.py --locale ja-JP
--resume` as an unattended, long-running background job (hours, not an
interactive turn) with `--max-parallel` kept low (2–3) since higher
parallelism does not help when the backend is GPU-serialized, and prioritize
the 585 remaining files by size (small-file-first) to maximize completed-count
per unit of contended GPU time — a sorted-by-size driver would materially
outperform the alphabetical default manifest order used by the script today.
