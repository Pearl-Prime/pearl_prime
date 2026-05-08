# qi_foundation → qi_foundation_cultivation YAML reconciliation (Direction B) — Pearl_Dev closeout

**Date:** 2026-05-08  
**Owner:** Pearl_Dev  
**Architectural gate:** PR **#944** merged (cap **QI-FOUNDATION-CANONICAL-RECONCILIATION-01**); merge commit referenced in routing: **`7e8009e78e`**. Direction **B**: align consumers to canonical slug `qi_foundation_cultivation` (no 38ᵗʰ alias brand).

**Authority narrative:** [`artifacts/qa/qi_foundation_canonical_reconciliation_2026-05-08.md`](qi_foundation_canonical_reconciliation_2026-05-08.md) (Pearl_Architect audit, §4).

---

## Deliverables

| Artifact | Detail |
|---------|--------|
| **Branch** | `agent/qi-foundation-yaml-direction-b-20260508` |
| **Commits** | `52f193b34f` — YAML reconciliation (`fix(manga): align qi foundation ids…`); `dc9b225c7c` — this closeout doc (`docs(qa): closeout for qi foundation YAML Direction B`) |
| **Pull request** | https://github.com/Ahjan108/phoenix_omega_v4.8/pull/952 |

---

## WRITE_SCOPE (inventory-matched YAML)

All edits were confined to reconciliation-audit §2 manga config call sites plus the Direction B §4 **`brand_lora_plans`** minimum:

| Path | Change summary |
|------|----------------|
| `config/manga/brand_lora_plans.yaml` | `brand_suffixes`, `character_loras.master_feung.style_ref`, `brand_style_loras` keys → `qi_foundation_cultivation` (`qf` / trigger tokens unchanged). |
| `config/manga/brand_genre_allocation.yaml` | Tentpole map and locale matrices: key `qi_foundation` → `qi_foundation_cultivation`. |
| `config/manga/brand_illustration_styles.yaml` | Top-level block key → `qi_foundation_cultivation`. |
| `config/manga/character_brand_registry.yaml` | Entry key and inner `brand_id` → `qi_foundation_cultivation`. |
| `config/manga/japan_dual_track_config.yaml` | `primary_brands` list entry → `qi_foundation_cultivation`. |
| `config/manga/manga_brand_series_plan.yaml` | Brand pacing block key → `qi_foundation_cultivation`. |

No changes to **`config/manga/canonical_brand_list.yaml`** (37-brand Path X authority unchanged).

---

## Verification performed

### Preflight / governance

Executed on the **`phoenix_omega_qi_foundation_recon_wt`** git worktree (canonical repo: `Ahjan108/phoenix_omega_v4.8`), after fast-forward to then-current **`origin/main`**:

- `git branch --show-current`
- `git status --short`
- `git fetch origin`
- `git rev-list --left-right --count origin/main...HEAD`
- `PYTHONPATH=. python3 scripts/git/push_guard.py` → OK
- `scripts/ci/preflight_push.sh` → OK
- `bash scripts/git/health_check.sh` → observed only expected warnings (primary worktree **`main`** stale vs **`origin/main`**; not blocking this branch)

### Grep sweep

After edits: **`config/manga/*.yaml`** swept for dangling alias slug `qi_foundation` (standalone / non-`qi_foundation_cultivation`). No offending matches remained.

---

## Operational notes (for future Pearl_Dev runs)

- **Large repo + Cursor:** concurrent `git` operations can race on **`.git/index.lock`** / worktree **`index.lock`**. Symptom: `fatal: Unable to create ... index.lock`. Mitigation: `lsof` on the lock file, terminate the holding PID, remove stale lock **only after** verifying no legitimate git process remains.
- **Worktree isolation:** Work completed in **`/Users/ahjan/phoenix_omega_qi_foundation_recon_wt`** to avoid long full working-tree checkouts on the primary IDE checkout when locks flapped.
- **Remote ref repair (one-off):** Stale **`refs/remotes/origin/main`** was reconciled with `rm` + `git fetch` from the primary repo when fetch reported “cannot lock ref … expected … but …”.

---

## Post-merge checklist (operator)

- [ ] Merge PR **#952** after governance checks pass.
- [ ] Optional follow-up (Pearl_DevOps + Pearl_Dev, per audit §5): CI invariant that `brand_lora_plans` keys / `style_ref` values ⊆ `canonical_brand_list.brands`.

---

## References

- Audit + cap: [`qi_foundation_canonical_reconciliation_2026-05-08.md`](qi_foundation_canonical_reconciliation_2026-05-08.md)
- PR #952: https://github.com/Ahjan108/phoenix_omega_v4.8/pull/952
