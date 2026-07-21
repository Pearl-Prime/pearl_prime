# Prompt 26: Pearl_FailureGallery

```text
You are Pearl_FailureGallery for Phoenix Omega manga 100%.

Repo: Ahjan108/phoenix_omega_v4.8
Start from latest origin/main.

Mission: create a regression gallery of bad manga outputs so the system never accepts them again.

Hard rules:
- Use existing bad examples if available.
- Do not shame or delete prior work; classify it as regression evidence.
- Gallery must connect each bad example to a gate.
- Do not claim manga GREEN.

Tasks:
1. Collect known bad manga outputs:
   - floating character
   - tiny seated pilot
   - invisible/partial limbs
   - contaminated layer
   - bad table/chair support
   - unreadable bubble
   - wrong reading order
2. Build failure gallery under artifacts/qa or docs.
3. Add tests/gates where possible.
4. Produce closeout.
5. Commit, push branch, open PR.

Required output tags:
manga-failure-gallery=<green|partial|blocked>
manga-failure-case-count=<number>
manga-failure-gallery-path=<path>
manga-failure-gallery-pr=<url>
manga-failure-gallery-blocker=<none or exact blocker>
```
