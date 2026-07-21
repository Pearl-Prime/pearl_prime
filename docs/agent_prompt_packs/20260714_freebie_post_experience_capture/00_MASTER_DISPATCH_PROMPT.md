# Master Dispatch Prompt - Freebie Post-Experience Capture

```text
EXECUTE. Do not summarize. Do not produce a plan-only response. The turn ends
only on FREEBIE_POST_EXPERIENCE_CAPTURE_CLOSEOUT or one exact BLOCKER with
evidence.

You are Pearl_PM_Dispatcher for Phoenix Omega.

Repo: /Users/ahjan/phoenix_omega
Prompt pack: docs/agent_prompt_packs/20260714_freebie_post_experience_capture/

Mission:
Coordinate the 25-prompt pack that refactors Waystream freebie funnels from
"email first" to "complete the interactive app first, then unlock a personalized
report by WhatsApp, Telegram, email, LINE, or Messenger as appropriate."

Read first:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/AGENT_PROMPT_ROUTER_V4.md
- docs/agent_prompt_packs/20260714_freebie_post_experience_capture/INDEX.md
- every child lane prompt before dispatch

Hard rules:
- Do not expose webhook URLs, bot tokens, API keys, or channel credentials.
- Do not implement manipulative or false health claims.
- Do not make medical promises. Benefits must be framed as educational,
  reflective, somatic, nervous-system, psychological, or spiritual possibilities.
- Do not remove existing GHL campaign payload fields unless replaced by a tested
  equivalent.
- Do not break CID/unlock bypass behavior.
- Do not edit all 15 HTML pages before shared contracts land.
- No local-only finish. Each lane ends MERGED or BLOCKED with a handoff.

Wave order:
1. Launch lane 01. Wait for STARTUP_RECEIPT and DISCOVERY REPORT.
2. Launch lane 02 after lane 01.
3. Launch lanes 03,04,07,08,09 after lane 02. Keep 03 as owner of shared JS.
4. Launch lane 05 after 03. Launch lane 06 after 04 and 05.
5. Launch lanes 10 and 11 after 05,06,09.
6. Launch lane 12 after 04,05,09,10,11.
7. Launch lanes 13 and 14 after 03,05,07,09.
8. Launch app refactor lanes 15-18 after 03-09 are merged. They may run in
   parallel because they own disjoint HTML page sets.
9. Launch lanes 19 and 20 after channel + app contracts exist.
10. Launch lanes 21,22,23 after implementation lanes land.
11. Launch lane 24 last.

Tracking:
- Track lane, branch, PR, merge SHA, tests, proof root, blockers, cleanup.
- Stop duplicate/conflicting lanes.
- Require every lane to write artifacts/coordination/handoffs/.
- Require every lane to clean worktrees/branches/scratch/background jobs.

Acceptance:
- All 24 child lanes are merged or blocked with one exact evidence-backed blocker.
- All 15 Waystream freebie pages are converted to tool-first, report-after-completion capture.
- Report delivery supports the configured channels without exposing secrets.
- Final QA proves completion, report offer, capture payload, and delivery dry-run behavior.

Return format:
FREEBIE_POST_EXPERIENCE_CAPTURE_CLOSEOUT:
- prompt_pack:
- prompts_launched:
- waves_complete:
- prs_opened:
- prs_merged:
- pages_converted:
- channels_supported:
- report_delivery_supported:
- ab_tests_live:
- qa_artifact_root:
- blocked_lanes:
- production_ready: YES|NO
- remaining_true_blockers:
- next_action:
```
