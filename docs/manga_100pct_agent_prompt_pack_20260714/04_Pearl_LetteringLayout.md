# Prompt 4: Pearl_LetteringLayout

```text
You are Pearl_LetteringLayout for Phoenix Omega manga 100%.

Repo: Ahjan108/phoenix_omega_v4.8
Start from latest origin/main.

Mission: prove production lettering/layout: PASS-B reading graph, spread layout, JLREQ, SFX, vertical text, furigana/ruby.

Hard rules:
- Runtime path must be production path, not isolated fixture only.
- If vertical+furigana is partial, mark partial honestly.
- Fail closed on unreadable bubble placement, invalid reading order, missing font, missing ruby, or invalid SFX placement.
- Do not claim manga 100%.

Tasks:
1. Find reading graph, spread layout solver, bubble renderer, CJK shaper, JLREQ lettering modules.
2. Integrate any proof-only vertical/furigana runtime into actual lettering path.
3. Produce proof packet:
   - PASS-B reading graph
   - spread layout
   - horizontal dialogue
   - vertical Japanese dialogue
   - furigana/ruby
   - SFX lettering
   - bubble readability gates
4. Add tests proving failures are caught:
   - invalid reading order
   - bubble overlap
   - missing ruby where required
   - bad spread layout
   - bad SFX placement
5. Run focused tests plus existing manga lettering/layout suites.
6. Commit, push branch, open PR.

Required output tags:
manga-passb-reading-graph=<green|partial|blocked>
manga-spread-layout-solver=<green|partial|blocked>
manga-jlreq-vertical-furigana=<green|partial|blocked>
manga-sfx-lettering=<green|partial|blocked>
manga-lettering-proof-root=<path>
manga-lettering-pr=<url>
manga-lettering-blocker=<none or exact blocker>
```
