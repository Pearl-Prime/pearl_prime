# Agent File Persistence Protocol

**Purpose:** Prevent agent-written files from being lost when the agent
environment (Cowork sandbox, Codex sandbox, Claude Code session) lacks
git credentials, network access, or persistent disk.

**Authority:** This protocol is mandatory for every Pearl agent that creates or
modifies files: Pearl_Writer, Pearl_Editor, Pearl_Dev, Pearl_Research.

**Last updated:** 2026-03-30

---

## The Problem

Agent sandboxes are ephemeral. Files written to a sandbox may not persist to
the user's local machine. Git push may fail (no credentials, no network,
`index.lock` stuck). When the agent session ends, uncommitted work vanishes.

**Lost work incidents (2026-03-30):**
- D1 voice re-localization (4 files, 120 scenes) — lost
- D3 voice re-localization (4 files, 120 scenes) — lost
- Pearl_Research deep-research skill files — lost 3 times
- Root cause: sandbox wrote files, git was blocked, session ended

---

## The Protocol

### Rule 1: Always attempt a local commit

After writing files, always try to commit locally — even if you cannot push.
A local commit survives `index.lock` issues and accidental `git checkout`.

```bash
rm -f .git/index.lock
git add <files>
git commit -m "wip(<lane>): <task summary> — sandbox commit, needs push"
```

If the commit succeeds, report the SHA in CLOSEOUT_RECEIPT. Pearl_GitHub
on a credentialed machine can then push and PR from this commit.

### Rule 2: If git is completely blocked, dump file contents

If `git add` or `git commit` fails for any reason (lock file that cannot be
removed, corrupt index, permission denied), you MUST include the **full
content** of every file you created or modified in your CLOSEOUT_RECEIPT.

Use this format:

```
── FILE DUMP (git blocked) ──

### FILE: atoms/working_parents/burnout/SCENE/CANONICAL.txt
```
[full file content here]
```

### FILE: atoms/working_parents/financial_anxiety/SCENE/CANONICAL.txt
```
[full file content here]
```
```

This ensures the content can be recovered by copy-pasting into the correct
paths on the user's machine.

### Rule 3: Run the persistence guard before reporting done

Run the persistence guard script at the end of every file-writing session:

```bash
bash scripts/agent/persist_or_dump.sh <file1> <file2> ...
```

This script:
1. Checks if each file exists on disk
2. Attempts `git add` + `git commit` for all files
3. If commit fails, prints full file contents to stdout for recovery
4. Exits with code 0 (committed) or 1 (dumped to stdout)

### Rule 4: Never report "done" without proof of persistence

Your CLOSEOUT_RECEIPT must include ONE of these:

| Proof type | What to include |
|------------|----------------|
| **Commit SHA** | `Commit: abc1234 on branch agent/d4-thin-compression` |
| **Push confirmed** | `Pushed to origin/agent/d4-thin-compression` |
| **File dump** | Full content of every file in fenced code blocks |

If your receipt has none of these three → the work is considered **not done**.

---

## Template: Persistence Block for Agent Prompts

Copy this block into every Pearl_Writer / Pearl_Editor / Pearl_Dev prompt:

```
── FILE PERSISTENCE (mandatory) ──
After writing all files, run:
  rm -f .git/index.lock
  bash scripts/agent/persist_or_dump.sh <list of files>

If the script is not available, manually:
1. git add <files> && git commit -m "wip(<lane>): <task> — sandbox commit"
2. If git fails: include FULL CONTENT of every modified file in
   CLOSEOUT_RECEIPT inside fenced code blocks.
3. Never report "done" without a commit SHA or file dump.
```

---

## For the Prompt Router (Cowork / Pearl_PM)

When generating prompts for content-writing agents:

1. **Always append** the persistence block above to the prompt
2. **Prefer Option A** (Cowork writes directly to disk) for critical content
   when the Cowork session has workspace access
3. **Option B** (agent writes + persistence guard) for parallelizable work
   where multiple agents run simultaneously
4. After receiving a CLOSEOUT_RECEIPT with file dumps, use the Cowork session
   to write the dumped content to disk before handing off to Pearl_GitHub

---

## For Pearl_GitHub

When receiving work from sandbox agents:

1. Check if the commit SHA exists locally: `git log --oneline <sha>`
2. If it exists → cherry-pick or rebase onto a clean branch from origin/main
3. If it does not exist → check if files are on disk with correct content
4. If files are not on disk → check CLOSEOUT_RECEIPT for file dumps
5. If no file dumps → the work is lost and must be re-done

---

## Integration Checklist

- [ ] `scripts/agent/persist_or_dump.sh` exists and is executable
- [ ] `docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md` (this file) is on main
- [ ] Every Pearl_Writer prompt includes the persistence block
- [ ] Every Pearl_Editor prompt includes the persistence block
- [ ] Pearl_GitHub SKILL.md references this protocol
- [ ] CLAUDE.md "Read First" list includes this file
