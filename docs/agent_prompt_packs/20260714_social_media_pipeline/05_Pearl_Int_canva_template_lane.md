# L4 — Pearl_Int — Canva template lane (Wave 1, look-gated, credential-graceful)

Paste this whole block into the lane agent chat.

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Int for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Int
- LANE=social-L4-canva
- EXECUTION_MODE=cloudflare_deploy_or_storage / external-API (Canva Connect) — credential-gated
- BACKGROUND_SAFE=yes (code + mock); live export needs credential
- RUNTIME_HOST=cloud
- PERSISTENCE_SURFACES=branch/pr/artifact
- RESUME_SURFACE=phoenix_v4/social/canva_render.py

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/specs/SOCIAL_MEDIA_PIPELINE_MASTER_SPEC.md
- schemas/social/social_media_asset.schema.json + example manifest fixture
- docs/INTEGRATION_CREDENTIALS_REGISTRY.md (Canva Connect credential location, if present)

LIVE STATE RECONCILIATION:
- verify social-arch-merged=<sha>.
- CREDENTIAL CHECK FIRST: determine whether a Canva Connect API credential is available in
  this run environment (Keychain/Codespace secret/registry). Interactively-authenticated MCP
  servers may be ABSENT in headless/cloud runs — assume they are, and design for it.
  * If NO credential: you build CODE + config + MOCK-driven tests and land them, then report
    `social-canva-lane-blocked=<missing: canva-connect-credential>` for the LIVE-export step.
    That is a VALID terminal state — do not fake an export, do not hang.
  * If credential present: additionally run a live smoke (1 autofill → 1 export) and byte-verify.

PRE-REQUISITE CHECKS:
- social-arch-merged=<sha>  → if missing, STOP BLOCKED.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- Canva credential present? (yes/no — drives the two paths above);
- proposed brand-template mapping: which Canva brand templates back which asset families
  (quote card, teaching carousel slide, Pinterest Pin, LinkedIn cover), and which fields are
  autofill variables (headline, body, brand color token, accent, image slot) — this is the
  "deterministic, change-colors/swap-elements, many unique variants" mechanism the operator asked for.

PROVENANCE:
- research: docs/research_social_media.txt (Part 6 — static/quote/carousel design) + operator's "Canva templates" request
- documents: SOCIAL_MEDIA_PIPELINE_MASTER_SPEC
- builds_on: L0 schemas; Canva Connect "create-design-from-brand-template" + autofill dataset + export
- inventory: EXTENDS (new canva_render module); UNCHANGED elsewhere. This lane is an ENHANCEMENT that must degrade gracefully — it never blocks the CI-safe L3 path.

MISSION (narrow):
Build the DETERMINISTIC Canva-template renderer: map asset families → Canva brand templates,
express per-asset variation as an autofill dataset (color token, headline, body, image slot),
and export finished PNG/PDF variants. Prove that ONE template + a variation dataset yields many
visually-distinct-but-on-brand variants (the operator's "thousands of unique posts" mechanism —
proven at PILOT scale here, not actually mass-produced). Degrade to CODE+MOCK if no credential.

DELIVERABLES:
- phoenix_v4/social/canva_render.py — given an asset + a variation row, call Canva Connect
  (create-from-brand-template → autofill → export) OR the mock path; return the exported file path.
  Credential read at runtime only; never hardcoded.
- config/social/canva_templates.yaml — brand-template registry: family → template_id, autofill
  field map, variation-axis definitions (palette tokens, layout swaps). (L4's file.)
- tests/test_social_canva_render.py — MOCK-driven (stub the Canva client): assert autofill payload
  shape, variation determinism (same seed → same dataset), and export-path handling. CI-safe, no network.
- artifacts/social/pilot/<book_id>/canva/ — PILOT exports IF credential present (proof root); else a
  MANIFEST of the payloads that WOULD be sent (canva_payloads_sample.json).

SMALLEST SAFE BATCH:
- smoke: build ONE autofill dataset for ONE quote card from the example manifest; assert payload shape.
  If credential present, do ONE live export and byte-verify.
- pilot: ONE template × 5 variation rows → 5 distinct datasets (and 5 exports if credential). `open` the folder.
- scale: HOLD until `social-look-approved=<sha>`. Do NOT mass-generate variants.

HANG PREVENTION:
- poll interval: API export status every 2 min (if live).
- no-progress rule: after two unchanged polls, inspect the API response/logs.
- hard stall: after three, mark live export BLOCKED, keep the CODE+MOCK landing.
- max window: 60 min. HARD RULE: never block waiting on a credential you don't have — detect absence FAST and take the mock path.

TESTS/PROOFS:
- pytest tests/test_social_canva_render.py -x  (mock, CI-safe)
- if live: byte-verify each pilot export (>0 bytes, correct dimensions).
- proof root: artifacts/social/pilot/<book_id>/canva/

DO NOT:
- do NOT hardcode/print the Canva credential;
- do NOT fake a live export or claim exports exist when they don't (mock outputs must be labelled MOCK);
- do NOT scale variant volume before look-approval;
- do NOT edit 48_SOCIAL / ghl docs or coordination TSVs;
- do NOT let this lane block L3 — it is an independent enhancement that degrades gracefully;
- no fake proof; no local-only finish.

LANDING CONTRACT:
- MERGED: PR (canva_render.py + config + mock tests + pilot exports OR payload manifest), checks green,
  squash-merged, `social-canva-lane-merged=<full-sha>` emitted.
- BLOCKED (credential-absent LIVE step): land the CODE+MOCK PR MERGED, and separately emit
  `social-canva-lane-blocked=<missing: canva-connect-credential>` with the exact credential name
  the operator must provide. The code lands either way.

CLEANUP LEDGER REQUIRED:
- worktree / local+remote branch / scratch files / background jobs / held artifacts
  (declare artifacts/social/pilot/<book_id>/canva/).

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/social-L4-canva_2026-07-14.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Int
- LANE: social-L4-canva
- STATUS=MERGED|BLOCKED
- BRANCH / PR / MERGE_SHA:
- SIGNAL: social-canva-lane-merged=<full-sha>  (and/or social-canva-lane-blocked=<reason>)
- ACCEPTANCE_LAYER: CODE-WIRED (mock) or EXECUTED-REAL (if live exports byte-verified); NOT PROVEN-AT-BAR (needs look-approval)
- CREDENTIAL_STATUS: present|absent (name)
- PROOF_ROOT / TESTS / CLEANUP / HANDOFF / NEXT_ACTION:
- TOKEN: CLOSEOUT_RECEIPT::social-L4-canva
~~~
