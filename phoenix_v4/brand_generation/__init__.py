"""Teacher-owned and hybrid brand identity generation (deterministic, no LLM)."""

from .teacher_brand_generator import (
    generate_hybrid_brand,
    generate_teacher_owned_brand,
    list_available_hybrid_archetypes,
    load_teacher_originated_registry,
    register_brand,
    token_overlap_ratio,
)

__all__ = [
    "generate_teacher_owned_brand",
    "generate_hybrid_brand",
    "list_available_hybrid_archetypes",
    "load_teacher_originated_registry",
    "register_brand",
    "token_overlap_ratio",
]
