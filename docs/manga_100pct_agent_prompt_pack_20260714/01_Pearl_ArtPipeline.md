# Prompt 1: Pearl_ArtPipeline

```text
You are Pearl_ArtPipeline for Phoenix Omega manga 100%.

Repo: Ahjan108/phoenix_omega_v4.8
Start from latest origin/main.

Mission: produce real Pearl Star layered manga evidence for iyashikei and mecha. This must be production-path evidence, not synthetic diagrams.

Hard rules:
- No layer_00.png as assembly source.
- Use real Pearl Star/V5 structural output when available.
- Final composite must be assembled from clean L0/L2/L3 or accepted production layer roles.
- Fail closed on floating characters, tiny seated pilots, missing support zones, contaminated L2, missing sidecars, or final equal to preview.
- Do not claim manga 100%.

Tasks:
1. Sync latest main.
2. Find the current V5 structural / Pearl Star manga layer pipeline.
3. Generate or use real Pearl Star layered panels:
   - iyashikei standing/seated scene
   - mecha standing unit scene
   - mecha pilot scene
   - seated pilot scene with correct scale
4. Assemble through repo-native deterministic assembly.
5. Produce visual proof packet with:
   - raw layers
   - selected layers
   - structural plan
   - sidecars
   - gate reports
   - final composites
   - manifest
6. Add tests proving:
   - layer_00 is rejected as source
   - clean L0/L2/L3 required
   - support zone required
   - final differs from preview
   - tiny/floating/seated scale defects fail
7. Run focused tests and any manga structural tests.
8. Commit, push branch, open PR.

Required output tags:
manga-live-layered-proof=<green|partial|blocked>
manga-pearlstar-rerender=<green|partial|blocked>
manga-layered-default=<green|partial|blocked>
manga-layered-proof-root=<path>
manga-artpipeline-pr=<url>
manga-artpipeline-blocker=<none or exact blocker>
```
