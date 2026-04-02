# Colab And Browser Verification Runbook

Purpose: give agents a safe, repeatable way to handle browser-assisted Colab work without guessing, overclaiming, or confusing keystroke automation with verified notebook completion.

## Use this runbook when

- A task involves Google Colab, browser automation, or a notebook already open in a browser
- An agent needs to confirm whether a notebook really finished
- A user says "you do it" for a browser task and the agent has limited browser read/control
- The repo state and the browser state may have drifted apart

## Rule 1: verify real state first

Before acting, verify the repo and file state locally:

```bash
git branch --show-current
git status --short --branch
ls -l scripts/manga/colab_manga_test.ipynb
```

If the task is GitHub-related, also follow Pearl_GitHub preflight from [ps.txt](./../ps.txt), [CLAUDE.md](./../CLAUDE.md), and [docs/PEARL_GITHUB_ONBOARDING.md](./PEARL_GITHUB_ONBOARDING.md).

Do not rely on pasted thread history alone. Re-check the current branch, working tree, and target file on disk.

## Rule 2: know what local automation can and cannot prove

This repo includes:

- [`run_colab_cells.applescript`](/Users/ahjan/phoenix_omega/scripts/manga/run_colab_cells.applescript)
- [`run_colab_cells.sh`](/Users/ahjan/phoenix_omega/scripts/manga/run_colab_cells.sh)

These scripts only send `Shift+Enter` to the active browser tab. They do not read notebook output, detect Python tracebacks, confirm downloads, or prove that later cells succeeded.

So:

- "keystrokes sent" is not the same as "notebook finished"
- "browser tab was active" is not the same as "cells passed"
- completion must be confirmed from visible notebook output or resulting files

## Rule 3: browser control prerequisites

For macOS keystroke automation:

1. The notebook must already be open in a supported browser.
2. The terminal/Codex app must have macOS Accessibility permission.
3. The correct browser tab must be frontmost.

If Accessibility is missing, the likely error is:

```text
osascript is not allowed to send keystrokes. (1002)
```

Fix by enabling Accessibility for the controlling app, then retry.

## Rule 4: explicit Colab completion criteria

For [`colab_manga_test.ipynb`](/Users/ahjan/phoenix_omega/scripts/manga/colab_manga_test.ipynb), do not say it is done until these are confirmed:

- Step 10 prints `PDF saved:` and either `Download started.` or a visible local path
- Step 11 prints `Manifest saved:` and `Panels tracked: 10`
- Step 12 renders the style-comparison image
- Step 13 prints `PASS: Deterministic rendering confirmed.` or explicitly reports the non-determinism warning

If only Steps 1-9 are confirmed, say exactly that: rendering and page assembly worked, but export/provenance/style-comparison/determinism still need confirmation.

## Rule 5: retry loop

If a Colab cell is incomplete or unverified:

1. Identify the last confirmed completed cell.
2. Run only the next pending cell.
3. Inspect its output.
4. If it fails, capture the actual traceback or message.
5. Fix the specific failure.
6. Re-run that cell.
7. Continue one cell at a time until all required outputs are confirmed.

Do not mark the notebook complete based only on elapsed time.

## Rule 6: when browser connection is limited

If the agent cannot read/control the browser directly:

- say that limitation plainly
- use local repo verification plus any visible user-provided outputs
- ask for the exact output of the next pending cell, not a vague status update
- keep the user on the smallest next action

Good prompt:

```text
Run Step 10 and paste the printed lines under the cell.
```

Bad prompt:

```text
Tell me if it worked.
```

## Current repo-specific notes

As of the March 20, 2026 verification pass:

- [`ps.txt`](/Users/ahjan/phoenix_omega/ps.txt) is wired to Pearl_GitHub for Git/GitHub/branch/PR/repo-health tasks
- [`scripts/manga/colab_manga_test.ipynb`](/Users/ahjan/phoenix_omega/scripts/manga/colab_manga_test.ipynb) exists on `main`
- local `main` may still contain an extra autobackup commit or other local-only changes, so always check `git status --short --branch` before assuming parity with `origin/main`

## Suggested response pattern

Use this structure for similar tasks:

1. State what is confirmed from disk/browser output.
2. State what is not yet confirmed.
3. State the exact next action.
4. Only declare success after the required outputs are visible.
