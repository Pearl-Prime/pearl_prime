# social_mp4_render handoff (Lane 01 — Pearl_Video / Pearl_Animator)

Pack: `docs/agent_prompt_packs/20260718_social_finish_mp4_evergreen/01_Pearl_Video_mp4_render_and_golden.md`

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT=Pearl_Video_lane01
RENDER_PATH=ffmpeg-fixed (ffmpeg 8.1.2, /opt/homebrew/bin/ffmpeg, --enable-libass; verified ffmpeg -version + 3s smoke encode before touching pilot assets)
MP4S_RENDERED=3/3 (validated: play/dims/duration/first-frame)
LOOK_PACKET=artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/LOOK_APPROVAL.md (opened via `open`; also copied to artifacts/qa/social_finish_20260718/lane01/LOOK_APPROVAL.md)
GOLDEN_HARNESS=staged dormant: scripts/ci/check_social_visual_parity.py (verified exit 0/SKIP — no golden yet) + scripts/social/freeze_social_visual_golden.py (verified refuses without --confirm-operator-approved; --dry-run verified) + empty artifacts/qa/snapshots/CANONICAL_SOCIAL_VISUAL/ (README only, no golden bytes)
ACCEPTANCE_LAYER=system working (rendered + validated); "beautiful" PENDING operator look
LANDED=offline/social-mp4-render-20260718@692d8ecf0f7dbca87ac48df8405f7427f7c27722
CLEANUP_COMPLETE=yes
HANDOFF=artifacts/coordination/handoffs/social_mp4_render_2026-07-18.md
SIGNAL=social-mp4-render=692d8ecf0f7dbca87ac48df8405f7427f7c27722
NEXT_ACTION=operator reviews LOOK_APPROVAL.md; on approve -> run scripts/social/freeze_social_visual_golden.py --confirm-operator-approved to populate CANONICAL_SOCIAL_VISUAL golden + flip the parity gate live (emit social-visual-golden-frozen=<sha>); live scheduling stays a separate gated lane
```

## IMPORTANT: LFS transport gap discovered + worked around

`pearlstar_offline` (the SSH bare repo at `pearl_star:~/git/phoenix_omega_offline.git`)
has **no working git-lfs binary transport**: `git-lfs-transfer` (native SSH
protocol) and `git-lfs-authenticate` (legacy SSH-token protocol) are both
"command not found" on that host, and the HTTPS fallback endpoint
(`https://pearl_star/...`) does not resolve (`pearl_star` is an SSH config
alias, not a DNS name). This means **any file matched by `.gitattributes`'
`*.mp4`/`*.jpg` LFS filter will push only as a text pointer to this remote —
the real bytes never transfer**, even though the git ref/commit push itself
succeeds and `ls-remote` looks fine. This was caught by a round-trip check
(pushed pointer commit, then tried to re-fetch the 3 new MP4 OIDs from the
remote with `--include`, got nothing back) rather than assumed from a clean
push.

**Fix applied:** re-added the 3 MP4s to the temp index with the LFS clean
filter explicitly disabled (`git -c filter.lfs.clean= -c filter.lfs.smudge=
-c filter.lfs.process= -c filter.lfs.required=false add -f`), so they commit
as **raw git blobs** (`Bin 0 -> N bytes` in `git diff --stat`, not 3-line LFS
pointers). Re-committed and force-pushed (safe: this is our own new branch,
not main) to `offline/social-mp4-render-20260718`. **Verified durably present**
by SSH-ing into `pearl_star` and running `git cat-file -p <blob-sha>` directly
against the bare repo for all 3 MP4s — byte counts and sha256 both match the
local files exactly (e.g. `tt_anxiety_faceless.mp4`: 1,115,123 bytes,
`sha256:1e21cf91d29e...` — identical on both sides). This is a stronger proof
than a re-fetch would have been, since it reads the remote's stored git object
directly with no client-side caching involved.

**Consequence for future lanes:** any lane that lands MP4/image binaries
>lfs-threshold onto `pearlstar_offline` must either (a) verify with this same
direct round-trip check before claiming LANDED, or (b) bypass the LFS clean
filter for small (~single-digit-MB) binaries like this lane did, or (c) fix
`git-lfs-transfer`/`git-lfs-authenticate` on the `pearl_star` host if larger
binaries need this path routinely. Flagging in case another agent hits the
same silent-pointer-only-push trap.

## Discovery / reconcile

- Verified preserve base `a842e73e854547e43267933a342d638dc5857ebd` on
  `pearlstar_offline` contains the full pilot packet (storyboards, frames,
  first-frames, concat helpers) but no MP4s and no golden — confirmed via
  `git ls-tree` against that commit before starting, matching the live
  discovery in the prompt.
- Checked `artifacts/qa/snapshots/` and handoffs for any prior MP4 render or
  golden freeze — **none found**. No stale claim; proceeded fresh.
- The working tree on the local branch (`codex/realist-social-samples-20260718`)
  did not have the `lane05_pearl_animator_rebuild/shortform_frames/`,
  `shortform_first_frames/`, `lane04_static_carousel_rebuild/`, and
  `lane07_pilot_packet/` assets checked out (LFS pointers only, and some paths
  were entirely absent locally). Pulled them from the preserve ref/commit via
  `git checkout a842e73e -- <paths>` + `git lfs fetch pearlstar_offline
  a842e73e` + `git lfs checkout <files>` (per-file; directory-glob checkout did
  not trigger LFS smudge reliably, files worked individually) before rendering.

## Render-path decision

**(a) Fix local ffmpeg — confirmed already fixed, re-verified.** Host ffmpeg
was already upgraded to 8.1.2 with `--enable-libass` per live discovery before
this session. Independently re-verified: `ffmpeg -version` succeeds and prints
`--enable-libass` in the build config; a 3s test encode to 1080x1920 with
`drawtext`-style filter chain succeeds. No Remotion (b) or RunComfy (c)
fallback needed. **$0 spend.**

## SMOKE -> PILOT -> SCALE

- **SMOKE:** rendered `tt_anxiety_faceless.mp4` from its concat file (5 frames,
  1.8s each + held last frame, 1080x1920 pad/scale, libx264 crf20, 30fps).
  Validated: `ffprobe` shows 1080x1920, 30fps, 10.77s duration; full decode via
  `ffmpeg -f null -` completes with zero errors; extracted frame 1 vs.
  `shortform_frames/tt_anxiety_faceless/frame_01.jpg` — mean abs pixel diff
  2.35/255, 1.1% of pixels differ by >10 (JPEG/h264 encode noise, not a wrong
  frame). PASS.
- **PILOT:** rendered the remaining 2 pilot MP4s
  (`tt_burnout_faceless`, `yt_overthinking_faceless`) with the identical
  filter chain. Both validated the same way (dims/fps/duration/full-decode/
  first-frame-diff) — see
  `artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/shortform_mp4_render_validation_receipts.jsonl`
  for full per-asset receipts (sha256, bytes, all checks). 3/3 pilot storyboards
  rendered and validated.
- **SCALE:** `shortform_publishable_storyboards.json` contains exactly 3
  entries (the pilot set). **SCALE=pilot-only** — there is no additional scale
  set to render; nothing was left behind.
- Wall-clock render time for all 3 MP4s: well under the 5-minute checkpoint
  window (each single-encode completed in under a minute; no wedged process,
  no batch reduction needed).

## Honest framing (no self-certified "beautiful")

Each MP4 is a validated **v1 first-frame-accurate 5-image slideshow**
(1.8s/frame), not the full beat-driven motion/caption/sound edit described in
each storyboard's `beats[]` array (hook/recognition/mechanism/practice/payoff,
27s target, on-screen captions, per-beat motion + sound cues). That fuller
Remotion/Pearl Animator cut is a follow-on if the operator wants it — flagged
explicitly in `LOOK_APPROVAL.md` so nobody mistakes the slideshow MP4 for the
final animated cut. Acceptance layer for this lane: **system working**
(rendered + validated). "Beautiful"/"shippable" is the operator's read via the
look-approval checklist, never a machine claim here.

## Operator look packet

- Canonical: `artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/LOOK_APPROVAL.md`
- Lane01 proof-root copy: `artifacts/qa/social_finish_20260718/lane01/LOOK_APPROVAL.md`
- Lane01 summary/pointer index: `artifacts/qa/social_finish_20260718/lane01/LANE01_SUMMARY.md`
- Contains: per-family approve/reject checklist (shortform MP4 vs. static/
  carousel, unchanged from the prior look gate), pointers to all 3 MP4s + the
  12 static + 3 carousel winners + the 3 contact sheets, the validation summary
  table, and an explicit "what happens on approval" section describing the
  golden freeze (staged, not fired).
- Opened via macOS `open` at the end of this session (both the MD file and the
  MP4 folder) — see CLOSEOUT_RECEIPT.

## Golden-freeze harness (staged dormant — verified, not fired)

- `scripts/ci/check_social_visual_parity.py` — mirrors
  `scripts/ci/check_pearl_news_sidebar_parity.py`'s capture-once-defend-forever
  pattern. Run and confirmed: **exit 0, prints SKIP** (no
  `CANONICAL_SOCIAL_VISUAL_METADATA.json` exists yet).
- `scripts/social/freeze_social_visual_golden.py` — populate-only tool. Run and
  confirmed: refuses with exit 2 when `--confirm-operator-approved` is
  omitted; with `--dry-run --confirm-operator-approved` it correctly lists the
  3 pilot MP4s it would freeze and writes nothing.
- `artifacts/qa/snapshots/CANONICAL_SOCIAL_VISUAL/` — created with a `README.md`
  only. **No golden bytes, no metadata file.** Confirmed empty of anything but
  the README after all dry-run testing.
- Nothing in this lane flips the gate live. That is explicitly the operator's
  post-approval step (one command, documented in the README and in
  `LOOK_APPROVAL.md`).

## LANDING + CLEANUP LEDGER

| Item | State |
|---|---|
| Render scratch (`/tmp/mp4_validation/`) | removed |
| Leftover pre-session smoke file (`/tmp/ffmpeg_smoke_test.mp4`) | removed |
| Orphan ffmpeg/git-lfs PIDs | none found (`ps aux \| grep ffmpeg` empty after renders) |
| Temp git index (`GIT_INDEX_FILE`) used for offline landing | unset after commit-tree (see recipe below) |
| `git lfs checkout` per-file loop for preserve-ref assets | completed; no dangling LFS fetch processes |
| Working-tree-only files pulled from preserve ref for local rendering (frames, first-frames, static/carousel samples, pilot packet) | left in the working tree (needed to render/validate); NOT re-committed to this lane's offline push except where explicitly listed below — they already exist in the preserve ref base, so the diff-stat gate should show them as unchanged/absent from this commit's diff unless explicitly added |

Explicit paths added to the offline commit (see landing recipe): the 3
rendered MP4s, the validation receipts (2 copies), `LOOK_APPROVAL.md` (2
copies), the lane01 summary, the 2 golden-harness scripts, the empty golden
dir's README, and this handoff. No `git add -A` was used at any point.

## LANDED_SHA

See the parent-agent final message for the resolved full commit SHA pushed to
`pearlstar_offline` `refs/heads/offline/social-mp4-render-20260718` (filled in
after the landing recipe runs, per the mandatory offline-landing protocol).
