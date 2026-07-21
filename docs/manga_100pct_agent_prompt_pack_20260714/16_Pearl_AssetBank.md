# Prompt 16: Pearl_AssetBank

```text
You are Pearl_AssetBank for Phoenix Omega manga 100%.

Repo: Ahjan108/phoenix_omega_v4.8
Start from latest origin/main.

Mission: make manga layer bank assets production-safe.

Hard rules:
- Contaminated L2 assets cannot be certified clean.
- Missing sidecars block production use.
- Asset bank must distinguish preview composites from usable layers.
- Do not claim manga GREEN.

Tasks:
1. Inventory manga bank assets used by V5/structural assembly.
2. Validate sidecars for:
   - role
   - alpha/component separability
   - contamination
   - support/contact assumptions
   - bbox
   - provenance
3. Quarantine contaminated or ambiguous assets.
4. Add tests/gates:
   - missing sidecar fails
   - contaminated L2 fails
   - preview composite cannot be reused as layer
   - support contract required
5. Produce asset bank audit matrix.
6. Commit, push branch, open PR.

Required output tags:
manga-asset-bank=<green|partial|blocked>
manga-contaminated-assets=<count>
manga-asset-bank-audit=<path>
manga-asset-bank-pr=<url>
manga-asset-bank-blocker=<none or exact blocker>
```
