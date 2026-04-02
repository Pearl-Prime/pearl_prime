# Pearl_GitHub — ps.txt Patch Instructions

**Purpose:** Apply these changes to `ps.txt` on the `codex/runtime-consolidation` branch to wire Pearl_GitHub into the agent protocol.

---

## Patch 1: Add Pearl_GitHub to SPECIALIZED AGENTS section

**Find this text:**
```
This repo has two specialized agents. Use them instead of working as a general agent:
```

**Replace with:**
```
This repo has four specialized agents. Use them instead of working as a general agent:
```

**Then after the Pearl_Editor entry, add:**
```
  Pearl_GitHub — GitHub operations agent (branching, pushing, PRs, CI workflows, push-guard,
                 branch protection, repo health, drift prevention)
                 Skill: skills/pearl-github/SKILL.md
                 Onboarding: docs/PEARL_GITHUB_ONBOARDING.md
```

**And update the routing block to:**
```
All agents score themselves via EI v2 and auto-block on drift.
If your task is CODE/ENGINEERING → use Pearl_Dev.
If your task is CONTENT/WRITING → use Pearl_Writer.
If your task is EDITORIAL/QUALITY → use Pearl_Editor.
If your task is GIT/GITHUB/PUSH/PR/BRANCH → use Pearl_GitHub.
If unsure → read the onboarding guides, then decide.
```

## Patch 2: Add Pearl_GitHub onboarding to STEP 1 read list

**After line 9 (`docs/PEARL_EDITOR_ONBOARDING.md`):**
```
10. docs/PEARL_GITHUB_ONBOARDING.md   — Pearl_GitHub agent guide (if doing git/GitHub)
```

## Patch 3: Update BRANCHING section

The branching section should already have the push-guard rules from the earlier edit session. If not, the full updated BRANCHING section is in `skills/pearl-github/SKILL.md` §STEP 1 and should be copied into ps.txt's STEP 4 (BRANCHING) section.

---

**These patches are ready to apply on `codex/runtime-consolidation` where ps.txt exists.**
