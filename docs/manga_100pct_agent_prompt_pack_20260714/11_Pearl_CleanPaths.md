# Prompt 11: Pearl_CleanPaths

```text
You are Pearl_CleanPaths for Phoenix Omega manga 100%.

Repo: Ahjan108/phoenix_omega_v4.8
Start from latest origin/main.

Mission: remove or block private absolute path leakage from manga generated artifacts.

Hard rules:
- Do not delete evidence.
- Convert generated artifact paths to repo-relative paths where safe.
- If old historical artifacts contain /Users, do not rewrite without preserving provenance; instead classify historical vs active.
- New committed generated JSON must not contain /Users.
- Do not claim manga GREEN.

Tasks:
1. Search manga artifacts/config/generated JSON for /Users.
2. Classify:
   - active proof artifact
   - historical artifact
   - source fixture
   - blocker
3. Fix active generators to emit repo-relative paths.
4. Add tests so new manga proof JSON cannot contain /Users.
5. Produce path leakage audit and blocker list.
6. Commit, push branch, open PR.

Required output tags:
manga-path-leakage=<green|partial|blocked>
manga-active-users-paths=<count>
manga-cleanpaths-audit=<path>
manga-cleanpaths-pr=<url>
manga-cleanpaths-blocker=<none or exact blocker>
```
