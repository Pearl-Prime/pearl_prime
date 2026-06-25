"""Pearl Star Job Queue V1 — Qwen-Image manga panel worker (Phase B stub).

Registered so the worker app imports cleanly. Full Qwen graph dispatch lands in a
follow-up once model-readiness gate G3 is green on Pearl Star.
"""

from __future__ import annotations

from app import app


@app.task(name="t2i_qwen_image", queue="t2i", retry=1)
def t2i_qwen_image(
    prompt: str,
    negative: str = "",
    width: int = 1080,
    height: int = 1920,
    seed: int = 42,
    panel_id: str = "",
    output_basename: str = "",
    dest_path: str = "",
) -> dict:
    raise RuntimeError(
        "t2i_qwen_image queue worker not implemented yet; "
        "use queue_panel_renders.py without --via-queue for Qwen workflows, "
        "or complete Pearl_Int Qwen model install per MANGA_PRODUCTION_OPERATIONAL_V1_SPEC §4"
    )
