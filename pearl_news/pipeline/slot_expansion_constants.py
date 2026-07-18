"""v5.2 slot template constants shared by Claude/Qwen slot expansion paths."""
from __future__ import annotations

STANDARD_V52_SLOTS: tuple[str, ...] = (
    "headline_layer_1",
    "headline_layer_2",
    "hook_personal",
    "hook_big_picture",
    "news_peg",
    "teacher_intro",
    "youth_somatic",
    "teacher_witness",
    "body_data",
    "turnaround",
    "bridge",
    "teacher_perspective",
    "practice_announce",
    "forward_look",
)

TEMPLATE_SLOTS: dict[str, tuple[str, ...]] = {
    "hard_news_spiritual_response": (
        "headline",
        "news_summary",
        "youth_impact",
        "teacher_perspective",
        "sdg_un_tie",
        "forward_look",
    ),
    "commentary": (
        "headline",
        "thesis",
        "teaching_interpretation",
        "civic_recommendation",
        "sdg_reference",
    ),
    "interfaith_dialogue_report": (
        "headline",
        "event_summary",
        "leaders_present",
        "themes_discussed",
        "youth_commitments",
        "sdg_alignment",
        "next_steps",
    ),
    "explainer_context": (
        "headline",
        "what_happened",
        "historical_background",
        "ethical_spiritual_dimension",
        "youth_implications",
        "sdg_policy_tie",
        "future_outlook",
    ),
    "youth_feature": (
        "headline",
        "youth_narrative",
        "data_research",
        "teacher_reflection",
        "sdg_framework",
        "solutions",
    ),
}

V52_SLOT_MAP: dict[str, dict[str, str]] = {
    "hard_news_spiritual_response": {
        "headline": "headline",
        "news_summary": "news_summary",
        "youth_impact": "youth_impact",
        "teacher_perspective": "teacher_perspective",
        "sdg_un_tie": "sdg_un_tie",
        "forward_look": "forward_look",
    },
    "commentary": {
        "headline": "headline",
        "thesis": "news_summary",
        "teaching_interpretation": "teacher_perspective",
        "civic_recommendation": "forward_look",
        "sdg_reference": "sdg_un_tie",
    },
    "interfaith_dialogue_report": {
        "headline": "headline",
        "event_summary": "news_summary",
        "themes_discussed": "teacher_perspective",
        "youth_commitments": "youth_impact",
        "sdg_alignment": "sdg_un_tie",
        "next_steps": "forward_look",
    },
    "explainer_context": {
        "headline": "headline",
        "what_happened": "news_summary",
        "ethical_spiritual_dimension": "teacher_perspective",
        "youth_implications": "youth_impact",
        "sdg_policy_tie": "sdg_un_tie",
        "future_outlook": "forward_look",
    },
    "youth_feature": {
        "headline": "headline",
        "youth_narrative": "news_summary",
        "data_research": "youth_impact",
        "teacher_reflection": "teacher_perspective",
        "sdg_framework": "sdg_un_tie",
        "solutions": "forward_look",
    },
}

INTERFAITH_SLOTS: tuple[str, ...] = (
    "headline_layer_1",
    "event_summary",
    "leaders_present",
    "themes_discussed",
    "youth_commitments",
    "sdg_alignment",
    "convergence",
    "distinction",
    "next_steps",
)

EXPLAINER_V52_SLOTS: tuple[str, ...] = (
    "headline_layer_1",
    "headline_layer_2",
    "hook_personal",
    "news_peg",
    "youth_somatic",
    "body_data",
    "teacher_intro",
    "teacher_witness",
    "turnaround",
    "bridge",
    "teacher_perspective",
    "practice_announce",
    "forward_look",
)

EXPLAINER_OPTIONAL_V52_SLOTS: tuple[str, ...] = (
    "what_happened",
    "historical_background",
    "ethical_spiritual_dimension",
    "youth_implications",
    "future_outlook",
    "sdg_policy_tie",
    "sdg_un_tie",
)

TEMPLATE_SLOTS_V52: dict[str, tuple[str, ...]] = {
    "hard_news_spiritual_response": STANDARD_V52_SLOTS,
    "commentary": STANDARD_V52_SLOTS,
    "interfaith_dialogue_report": INTERFAITH_SLOTS,
    "explainer_context": EXPLAINER_V52_SLOTS,
    "youth_feature": STANDARD_V52_SLOTS,
}

V52_TO_LEGACY_MAP = {
    "headline_layer_1": "headline",
    "headline_layer_2": "headline_layer_2",
    "hook_personal": "hook_personal",
    "hook_big_picture": "hook_big_picture",
    "news_peg": "news_peg",
    "teacher_intro": "teacher_intro",
    "youth_somatic": "youth_somatic",
    "teacher_witness": "teacher_witness",
    "body_data": "body_data",
    "turnaround": "turnaround",
    "bridge": "bridge",
    "teacher_perspective": "teacher_perspective",
    "practice_announce": "practice_announce",
    "forward_look": "forward_look",
}

OPTIONAL_V52_SLOTS: dict[str, tuple[str, ...]] = {
    "hard_news_spiritual_response": ("sdg_un_tie",),
    "commentary": ("sdg_un_tie",),
    "interfaith_dialogue_report": ("sdg_un_tie",),
    "explainer_context": EXPLAINER_OPTIONAL_V52_SLOTS,
    "youth_feature": ("sdg_un_tie",),
}
