"""Identity-stages check used by the spine pipeline's book_pass gate.

OPD-20260518-002 / ws_flow_glue_selector_cap_enforcement_20260517
------------------------------------------------------------------
Prior to this module, the inline check in ``scripts/run_pipeline.py`` keyed
the recognition / mechanism / integration coverage entirely on
``enrichment_audit.depth_modules_added``. Depth-modules are word-budget side
effects — they fire only when chapters fall short of their per-chapter word
budget. Standard_book renders that meet word targets without depth
enrichment never emit ``recognition_depth`` or ``integration_landing``
modules, so the check spuriously FAILed on Junko + Miyuki standard_book
smokes (2026-05-19) even though all 12 identity-stage chapter roles
(``recognition``, ``mechanism``, ``integration``, ...) were present.

The fix: read identity-stage coverage from the chapter ROLES that the
spine planner emits (already collected for ``band_distribution``). The
depth-module signal remains as a secondary fallback so that deep_book
renders, which lean heavily on depth-modules, continue to pass.

The function lives in its own module to keep the inline pipeline block
small and to expose a unit-test surface. The pipeline imports it through
the in-line ``compute_identity_stages`` symbol so the change is otherwise
invisible to callers.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

# Role markers correspond to spine-planner chapter ``role`` values that
# directly encode each identity stage. Depth-module names are folded in
# as a secondary signal so the existing behaviour for deep_book_6h /
# deep_book_4h renders is preserved.
RECOGNITION_ROLE_MARKERS: Tuple[str, ...] = (
    "recognition", "destabilization", "pattern_mapping",
    "origin", "destabilize",
)
MECHANISM_ROLE_MARKERS: Tuple[str, ...] = (
    "mechanism", "cost_exposure", "identity_fracture",
    "somatic_legitimacy",
)
INTEGRATION_ROLE_MARKERS: Tuple[str, ...] = (
    "integration", "reframe", "practical_interruption",
    "practice_under_pressure", "practice",
)


def _hits_any(markers: Iterable[str], haystacks: Iterable[str]) -> bool:
    """Return True iff any haystack string contains any marker substring."""
    markers_t = tuple(markers)
    for h in haystacks:
        if not h:
            continue
        h_low = str(h).strip().lower()
        if any(m in h_low for m in markers_t):
            return True
    return False


def compute_identity_stages(
    chapter_roles: List[str],
    depth_modules: List[str],
) -> Tuple[Dict[str, bool], int, bool]:
    """Compute the identity-stages tags + summary scalars for a render.

    Parameters
    ----------
    chapter_roles
        ``EnrichedChapter.role`` values for every chapter that has a non-
        empty role. Case is normalised inside the helper; callers can pass
        raw role strings.
    depth_modules
        ``enrichment_audit.depth_modules_added[*].module`` values. Empty
        is fine — recognition / integration are still covered by roles.

    Returns
    -------
    (stages_dict, stage_count, identity_ok)
        ``stages_dict`` has keys ``recognition`` / ``mechanism`` /
        ``integration``. ``identity_ok`` mirrors the gate threshold
        (``stage_count >= 2``).
    """
    roles_norm = [str(r or "").strip().lower() for r in chapter_roles]
    modules_norm = [str(m or "").strip().lower() for m in depth_modules]

    stages = {
        "recognition": _hits_any(RECOGNITION_ROLE_MARKERS, roles_norm)
        or _hits_any(RECOGNITION_ROLE_MARKERS, modules_norm),
        "mechanism": _hits_any(MECHANISM_ROLE_MARKERS, roles_norm)
        or _hits_any(MECHANISM_ROLE_MARKERS, modules_norm),
        "integration": _hits_any(INTEGRATION_ROLE_MARKERS, roles_norm)
        or _hits_any(INTEGRATION_ROLE_MARKERS, modules_norm),
    }
    stage_count = sum(1 for v in stages.values() if v)
    identity_ok = stage_count >= 2
    return stages, stage_count, identity_ok
