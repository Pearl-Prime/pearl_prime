# Prompt 20: Pearl_Runbook

```text
You are Pearl_Runbook for Phoenix Omega manga 100%.

Repo: Ahjan108/phoenix_omega_v4.8
Start from latest origin/main.

Mission: write the operator runbook so manga can be rerun by a human without tribal knowledge.

Hard rules:
- Runbook must match actual scripts and paths.
- Every command must be verified or marked unverified.
- Do not claim manga GREEN.

Tasks:
1. Document the exact production run sequence:
   - story
   - render
   - layer assembly
   - lettering/layout
   - proof packet
   - blind-read
   - truth audit
2. Include required secrets/access:
   - Pearl Star
   - GitHub
   - queue/worker
   - storage
3. Include failure recovery:
   - queue stuck
   - bad layer
   - bad lettering
   - truth audit fail
   - rollback
4. Add a runbook validation checklist.
5. Commit, push branch, open PR.

Required output tags:
manga-runbook=<green|partial|blocked>
manga-runbook-path=<path>
manga-runbook-pr=<url>
manga-runbook-blocker=<none or exact blocker>
```
