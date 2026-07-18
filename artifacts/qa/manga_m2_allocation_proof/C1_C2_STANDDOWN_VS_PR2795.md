# C-1 / C-2 Stand-Down vs PR #2795

**M2 item 3** (Roadmap §2): fix registry flags C-1/C-2 — add zh_TW + fr_FR manga
tracks to `config/catalog/market_catalog_registry.yaml` per
`docs/specs/MANGA_MARKET_INTEGRATION_V1_SPEC.md` §C.

**Decision:** STAND DOWN on item 3 only. Items 1/2/4 ship in this PR.

## Collision

| Field | Value |
|---|---|
| PR | [#2795](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/2795) |
| Branch | `agent/manga-registry-tw-fr-20260628` |
| Title | feat(catalog): Taiwan/France manga registry lines (Prompt 6) |
| State (checked 2026-07-04) | **OPEN** |
| Touches | `config/catalog/market_catalog_registry.yaml` (+ other files) |
| Last updated | 2026-06-28T19:28:43Z |

PR #2795 sits on the **same resource** as C-1/C-2. One actor per resource —
M2 does not double-drive those rows.

## Follow-up (cold-start)

1. `gh pr view 2795 --json state,mergeable,files`
2. If #2795 merges and lands C-1/C-2 → verify §C closed; no M2 follow-up needed.
3. If #2795 closes without the fix → open a tiny PR adding manga tracks for
   zh_TW + fr_FR only, citing MANGA_MARKET_INTEGRATION_V1_SPEC §C.
4. Until resolved, Taiwan/France manga fan-out remains
   `status: blocked_open_flag` / `registry_no_manga_track` per the integration spec.

Logged in OPD-20260703-102.
