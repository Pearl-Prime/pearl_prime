# Prompt 3: Pearl_Mode

```text
You are Pearl_Mode for Phoenix Omega manga 100%.

Repo: Ahjan108/phoenix_omega_v4.8
Start from latest origin/main.

Mission: prove teacher and music modes work on the default manga production path.

Hard rules:
- Mode must flow from series/chapter plan through emit/render path to apply_mode_vessel or equivalent.
- Do not accept dormant vessels as green.
- Output must change when teacher/music modes are enabled.
- Missing mode= or bypass must fail tests.
- Do not claim manga 100%.

Tasks:
1. Find manga mode vessels, emit.py, run_manga_pipeline.py, series plan schema, and tests.
2. Verify whether mode is currently passed through default path.
3. Fix mode plumbing end to end.
4. Add regression tests:
   - teacher mode alters manga output
   - music mode alters manga output
   - teacher+music combined mode works or blocks honestly
   - omitted mode fails
   - unknown mode fails closed
5. Produce proof artifacts:
   - baseline output
   - teacher output
   - music output
   - diff/trace showing real change
6. Commit, push branch, open PR.

Required output tags:
manga-teacher-mode=<green|partial|blocked>
manga-music-mode=<green|partial|blocked>
manga-mode-plumbing=<green|partial|blocked>
manga-mode-proof-root=<path>
manga-mode-pr=<url>
manga-mode-blocker=<none or exact blocker>
```
