# Method + capture notes (Q10–Q11)

**Date:** 2026-07-24 | **Leads:** `old_chat_specs/Untitled 411.txt` (not truth)

## Q10 — Cross-clip identity

| Method | Drift | Pose-bank role |
|--------|-------|----------------|
| t2v per clip | High | Style smoke only |
| Same-anchor i2v | Low within clip; cross-clip OK if same URL reused | **Pilot primary** |
| first+last i2v | Locks comic keys | A→B arcs |
| continuation | Temporal glue; burns seconds | Use sparingly |
| cloud r2v | Purpose-built refs; not guaranteed | Defer until free s proven |
| VACE R2V+pose | Strong open identity+control | **Scale primary** |

Untitled 411 survivors: clothing continuity via temporal bank = YES; video replaces LoRA = NO; hybrid bank+assemble = YES.

## Q11 — Capture program

Comic keys per clip: rest, anticipation, impact, follow-through, 3⁄4+profile, occlusion stress.

Sampling (start): 5s clip → extract 8–12 keyed candidates → keep 4–6 after QA (not uniform every-Nth dump).

Failure modes to reject: hands, occlusion-reveal hallucination, clothing mutation across cuts, background bleed, mid-clip identity morph.

Program: Star canonical still → cloud i2v families → matte → bank INTERIM → later VACE scale.
