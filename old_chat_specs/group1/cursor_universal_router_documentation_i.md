# Universal router documentation in protocol
_Exported on 4/16/2026 at 19:26:30 GMT+8 from Cursor (3.1.15)_

---

**User**

Pearl_PM + Pearl_GitHub — document the universal router in-protocol

1) Read docs/agent_brief.txt (or wherever the canonical router already lives).
2) Edit docs/SESSION_UNITY_PROTOCOL.md: after “Quick Reference” (or new appendix), add section
   “Universal router prompt (prompt-building chats)” with 2–3 lines of when to use it + either
   the full paste-ready template OR a single line: “Canonical full text: docs/agent_brief.txt §X.”
3) If you duplicate text, keep one source of truth and link the other—avoid drift.
4) Small commit; PR; docs/DOCS_INDEX.md only if index requires new anchor.
5) CLOSEOUT_RECEIPT with file path + SHA.

Pearl_PM + Pearl_GitHub — document the universal router in-protocol

1) Read docs/agent_brief.txt (or wherever the canonical router already lives).
2) Edit docs/SESSION_UNITY_PROTOCOL.md: after “Quick Reference” (or new appendix), add section
   “Universal router prompt (prompt-building chats)” with 2–3 lines of when to use it + either
   the full paste-ready template OR a single line: “Canonical full text: docs/agent_brief.txt §X.”
3) If you duplicate text, keep one source of truth and link the other—avoid drift.
4) Small commit; PR; docs/DOCS_INDEX.md only if index requires new anchor.
5) CLOSEOUT_RECEIPT with file path + SHA.

---

**Cursor**

Locating the canonical router text and SESSION_UNITY_PROTOCOL structure, then adding the documented section with a single source of truth.



Adding the section after Quick Reference, pointing to `docs/agent_brief.txt` as the single source of truth (no duplicated template). Branching from `origin/main`, committing, and opening a PR.



Stashing local changes (including `scripts/run_pipeline.py`), creating a docs-only branch from `origin/main`, and restoring only `docs/SESSION_UNITY_PROTOCOL.md` from the stash.



Using a separate git worktree to avoid switching branches in a heavily dirty working tree.



---

**User**

what are you doing exactly?

---

**Cursor**

Here’s what was going on, in plain terms.

**What you asked for**  
Document the “universal router” in `docs/SESSION_UNITY_PROTOCOL.md`: add a short “when to use it” blurb and point at **`docs/agent_brief.txt`** as the single paste-ready source (no second copy of the prompt text).

**What I actually did in the repo**  
I updated `docs/SESSION_UNITY_PROTOCOL.md` in your main workspace: bumped “Last updated” to 2026-04-15 and appended **“Universal router prompt (prompt-building chats)”** right after the Quick Reference table, with a link to `./agent_brief.txt` so the instructions don’t drift.

**Why git got messy**  
Your instructions also asked for a small commit + PR from **`origin/main`**. Your checkout was on another branch with lots of local changes (and a huge dirty tree), so switching branches failed. I tried:

1. **Stash** — to free the tree; that partially ran and left things confusing.  
2. **`git worktree add /tmp/phoenix-docs-clean origin/main`** — a standard way to commit from a clean copy of `main` without touching your dirty tree. That was still checking out tens of thousands of files when things dragged on.

**What I did *not* finish**  
I did **not** reliably complete: clean branch from `main`, `push_guard` / preflight, push, `gh pr create`, or a final **CLOSEOUT_RECEIPT** with a real commit SHA — because the git/worktree path was interrupted and messy.

**Bottom line**  
The **doc edit** in your workspace is the real deliverable for “document the router in-protocol”; the **PR** part stalled on repo hygiene (dirty worktree + slow worktree checkout), not on the wording of the section.

If you want, I can pick up from here in one of two ways: commit **only** `docs/SESSION_UNITY_PROTOCOL.md` from a clean path you prefer (e.g. fresh worktree once it finishes, or you temporarily stashing/moving blockers), or you merge the file change manually and I’ll only help with the exact PR commands once the tree is clean.

