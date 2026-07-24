# EXECUTE — Lane 05 (Pearl_Prime/Pearl_Prez): Brand-wizard regression repair

This is an execution prompt, not a planning request. End state: **locale-routing
tests 7/7 green, the unintended #166 losses restored, the #58 bug resolved — all
MERGED; deploy verified live or BLOCKED solely on operator item B.**

## Contract (in-band)
- STARTUP_RECEIPT: branch, HEAD SHA, `git status --short | head`, `gh auth status`,
  `git fetch origin && git log origin/main -1 --oneline`.
- Claims below are from 2026-07-24 authoring — re-verify: run the failing test
  yourself first (`pytest tests/test_wizard_locale_routing.py -v`); a sibling
  "sys-tester" session was mid-fix at last handoff and may have landed something.
  Search open+merged PRs for overlap before authoring (sibling-collision rule).
- **Drift recovery is git-first:** restore lost functionality with
  `git checkout <good-sha> -- <path>` from the pre-#166 tree — NEVER fresh-rewrite
  a page that git already has. #166 merged at `d50416009065`; the deleted
  `pearl_prime_entry.html` exists at `d50416009065^`.
- GOTCHA (repo memory): `brand_admin_weekly_os.html` is SYNCED FROM repo root —
  edit the root copy, not the synced one. Check whether entry pages share this
  root-sync pattern before editing.
- Branch off origin/main; preflight (push_guard, preflight_push, health_check);
  merge rules (Rule-0, pre_merge_check with live CI gate — wait for
  `PIPER100-L02-MAIN-GREEN`, governance review). Squash-merge pre-authorized when green.
- Layer-honest closeout; verify in the browser where observable (preview the built
  page; keystroke/API claims alone are not proof).

## Authority reads
`artifacts/coordination/handoffs/brand_wizard_entry_split_2026-07-23.md` (the
regression's own handoff — read FIRST), `docs/` brand-admin canonical package docs,
`tests/test_wizard_locale_routing.py` (what the contract actually asserts),
PR #166 diff (`gh api .../pulls/166/files`), closed PR #58 diff.
DISCOVERY REPORT before edits: which #166 deletions were INTENTIONAL (operator-
instructed drops per the handoff) vs UNINTENDED (Brazil/pt_BR lane, weekly-ops
link) — do not resurrect intentionally-dropped scope.

## Work items
1. **Restore unintended losses:** pt_BR/Brazil routing lane + weekly-ops link,
   recovered from `d50416009065^` (git-first), grafted into the new split-entry
   structure (don't revert the split itself — it was intentional).
2. **Fix `test_wizard_locale_routing.py` to 7/7.** If any failing assertion covers
   INTENTIONALLY-dropped scope, update the test with a comment naming the operator
   decision + handoff doc — that's a contract change, not a gate-weakening.
3. **#58 (assignment.js: canonical `brand_admin_brands.json` must win over R2
   live):** closed-unmerged. Reproduce the bug on main first; if live, re-land the
   fix on a fresh branch (cherry-pick from #58's head if clean); if already fixed
   elsewhere, document where and close the thread in your receipt.
4. **Deploy:** after merge, trigger the Pages deploy. Expected to fail until
   operator sets `CLOUDFLARE_API_TOKEN` (OPERATOR_ACTIONS.md item B). If the
   operator has said "CF token set", verify the deployed page live in a browser
   (locale lanes present, weekly-ops link resolves). Note: CF Pages deploys go via
   GH Actions; local tokens auth-fail on the Pages REST API — don't chase that path.

## Closeout
```
CLOSEOUT_RECEIPT: PIPER100-L05-DONE
tests: <7/7 or failures + why>
restored: <files + source SHA>
pr58_resolution: <re-landed PR# / already-fixed-at <ref> / not-reproducible>
prs_merged: <#s + SHAs>
deploy: <verified-live URL / BLOCKED-on-operator-item-B>
acceptance_layer: system working (routing restored) — brand content unchanged
NEXT_ACTION: <...>
```
Append a dated note to this pack's INDEX.md.
