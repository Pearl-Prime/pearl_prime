# LANE 1 — Verify Free/Local Image-Gen Infra (Pearl Star, ComfyUI, LoRA/PuLID)

## EXECUTE

This is a verification smoke test, not a build. Budget: one real GPU dispatch
(a single test image), well under RAP's flux-schnell kill threshold (60s).
Do not stop at "the config looks right" — produce one real rendered file and
byte-verify it exists and is non-trivial size, exactly as the manga doctrine
requires (a claimed render under ~50KB or missing on disk is a stub, not proof
— `scripts/ci/check_render_progress_bytes.py`'s standard applies here even
though this isn't a RENDER_PROGRESS row).

## Read first (subsystem authority)

- `docs/ROBUST_AGENT_PROTOCOL.md` — the mandatory RAP queue-first contract.
  Job sizing rule: one image per queue job. Stall thresholds: flux-schnell
  warn 30s / kill 60s.
- `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` — read the RunComfy row in full
  (currently documented as decommissioned 2026-06-13; confirm this is still
  true, don't assume a memory note is current truth).
- `artifacts/research/pearl_star_capacity_and_queue_20260611/HARDWARE_INVENTORY.md`
  — Pearl Star's Tailscale address and ComfyUI port (previously
  `100.92.68.74:8188` / `pearlstar.tail7fd910.ts.net:8188`; RE-VERIFY, machine
  addressing can drift).
- `config/manga/brand_lora_plans.yaml` — confirms base model must be
  `flux1-schnell-fp8` (Apache-2.0, commercial-clean); `flux1-dev` is
  license-banned per `artifacts/research/license_risk_register_2026-04-29.md`
  — if you find `flux1-dev` resident/default anywhere in a live workflow JSON,
  that is a real finding to report, not something to silently work around.
- `scripts/pearl_star/bin/pscli` — the canonical dispatch CLI. Read `--help`
  and any `status`/`enqueue`/`inspect` subcommand help before using it.

## Steps

1. **Reachability**: `pscli status` (or equivalent health check it exposes).
   Report exact output. If unreachable, STOP and report BLOCKED with the
   error — do not fabricate a "should be reachable" claim. (Known history:
   Pearl Star has been CJK-atom-priority and occasionally unavailable per
   `OPD-20260629-003`; this may still be true.)
2. **Checkpoint audit**: confirm which checkpoint(s) are actually resident on
   the ComfyUI instance (list models via its API or `pscli`, not by reading a
   doc). Report the exact filename(s) found. Flag explicitly if `flux1-dev`
   (banned) is present as default/resident alongside or instead of
   `flux1-schnell-fp8`.
3. **PuLID / LoRA node state**: check whether PuLID custom nodes are installed
   in the ComfyUI instance (`custom_nodes/` listing via the API or however
   `pscli` exposes it), and confirm the actual count of trained LoRA
   `.safetensors` files present anywhere in the manga LoRA directory (research
   this session found zero trained LoRAs repo-wide — confirm whether that is
   still true on the Pearl Star box itself, which may differ from the repo).
4. **One real dispatch, RAP-compliant**: enqueue exactly one T2I job via
   `pscli enqueue` using `flux1-schnell-fp8` explicitly pinned (a trivial,
   brand-neutral test prompt — do not use real character/scene content for
   this smoke test), poll with `pscli inspect`/`pscli status` respecting the
   30s/60s thresholds, and confirm a real output file lands with a real byte
   size (report the path and byte count).
5. **Paid-path negative check**: grep the dispatch path you just exercised
   (and `pscli`'s source) for any RunComfy/cloud-API call it could fall back
   to, and confirm none fired (check for any outbound calls beyond the
   Tailscale ComfyUI endpoint).

## Report back (feeds directly into Lane 2 — be precise, this is load-bearing)

- Pearl Star reachable: yes/no, with raw output.
- Resident checkpoint(s): exact filename(s).
- PuLID installed: yes/no. Trained LoRA count found on the box: exact number.
- Test render: file path, byte size, wall-clock time.
- Any paid-path (RunComfy or other) call observed: yes/no, with evidence
  either way.
- Six-layer-taxonomy label for "Pearl Star free-image-gen path is working":
  CODE-WIRED or EXECUTED-REAL (justify which, based on step 4's actual PNG).

No git changes are required for this lane unless you find something that
needs a doc correction (e.g., a stale IP/port in a checked-in doc) — if so,
make that one small fix, commit it via git plumbing off a fresh
`origin/main` fetch (per the master prompt's dirty-tree guidance), and note
the SHA in your report. Otherwise this lane's output is the report itself,
handed directly to whoever runs Lane 2.
