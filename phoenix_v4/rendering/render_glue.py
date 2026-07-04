"""Master render-glue kill-switch (de-injection 2026-07-05, Part A).

Production spine path default: glue OFF. Set ``PHOENIX_ENABLE_RENDER_GLUE=1`` to
re-enable template bridge/mechanism/exercise-wrapper families and component
template stacking for A/B or legacy tests.
"""
from __future__ import annotations

import os


def render_glue_enabled() -> bool:
    env = os.environ.get("PHOENIX_ENABLE_RENDER_GLUE")
    if env is not None:
        return env.strip().lower() not in ("0", "false", "no", "")
    return False
