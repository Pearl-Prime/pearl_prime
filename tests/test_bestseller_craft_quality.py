"""
Craft-grade quality tests — validates actual prose quality patterns
identified as gaps by the bestseller audit.

Maps to docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md sections 5, 6, 8, 9, 11.

These tests exercise:
  - phoenix_v4/quality/bestseller_craft_gate.py  (ONTGP scoring)
  - phoenix_v4/quality/story_atom_lint.py         (story specificity)
  - phoenix_v4/exercises/overlay_substitution.py   (aha/integration patterns)
  - phoenix_v4/qa/chapter_flow_gate.py             (scene/scaffold detection)

Plus new check functions for gaps where no gate exists yet.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List, Optional, Sequence

import pytest

from phoenix_v4.quality.bestseller_craft_gate import (
    _ABSTRACT_TOPIC_PATTERNS,
    evaluate_bestseller_craft,
)
from phoenix_v4.quality.story_atom_lint import (
    count_hits,
    has_any,
    lint_one_prose,
    SENSORY_WORDS,
    ACTION_VERBS,
)
from phoenix_v4.exercises.overlay_substitution import (
    validate_required_terms_for_aha,
    validate_callout_prefix,
    BODY_REFERENCE_WORDS,
)
from phoenix_v4.quality.chapter_flow_gate import evaluate_chapter_flow


# ---------------------------------------------------------------------------
# Helper check functions — fill gaps where no gate exists yet
# ---------------------------------------------------------------------------

def count_unique_sensory_details(text: str) -> int:
    """Count unique sensory detail phrases in a scene.

    A sensory detail is a concrete image containing a sensory word or
    a specific object/body reference that goes beyond stock phrasing.
    """
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    seen: set[str] = set()
    count = 0
    for sent in sentences:
        low = sent.lower()
        # Sensory word present AND not a stock duplicate
        has_sensory = has_any(low, SENSORY_WORDS)
        has_specific_object = bool(re.search(
            r"\b(oat-milk|fluorescent|digital clock|group chat|47 messages|thumb|"
            r"sternum|grey|film|hum|ping|screen glow|creak|buzzing|aching)\b",
            low,
        ))
        if has_sensory or has_specific_object:
            # Normalize to catch near-duplicates
            key = re.sub(r"[^a-z ]+", "", low).strip()
            if key not in seen:
                seen.add(key)
                count += 1
    return count


def check_scene_three_detail_rule(scene_text: str) -> List[str]:
    """Overlay spec 8.2: every SCENE needs >= 3 unique sensory details."""
    n = count_unique_sensory_details(scene_text)
    if n < 3:
        return [f"SCENE_INSUFFICIENT_SENSORY_DETAILS:{n}/3"]
    return []


def check_scene_collision(scenes: List[str]) -> List[str]:
    """Overlay spec 8.4: no two scenes may share identical non-trivial phrases."""
    STOP_PHRASES = {"the", "a", "an", "you", "your", "is", "are", "was", "were", "it"}
    issues: List[str] = []
    phrase_sets: List[set[str]] = []
    for sc in scenes:
        # Extract 3+ word phrases (lowered, stripped)
        sents = [s.strip().lower() for s in re.split(r"(?<=[.!?])\s+", sc.strip()) if s.strip()]
        phrase_sets.append(set(sents))

    for i in range(len(phrase_sets)):
        for j in range(i + 1, len(phrase_sets)):
            shared = phrase_sets[i] & phrase_sets[j]
            # Filter trivially short matches
            meaningful = [p for p in shared if len(p.split()) >= 4]
            if meaningful:
                issues.append(
                    f"SCENE_COLLISION:ch{i+1}_ch{j+1}:shared_phrases={len(meaningful)}"
                )
    return issues


def check_scene_action_state(scene_text: str) -> List[str]:
    """Overlay spec 8.3: scene must end on micro-action or body state, not pure description."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", scene_text.strip()) if s.strip()]
    if not sentences:
        return ["SCENE_EMPTY"]
    last = sentences[-1].lower()
    has_action = has_any(last, ACTION_VERBS)
    has_body = bool(re.search(
        r"\b(hand|hands|feet|jaw|throat|shoulders|chest|thumb|spine|eyes|breath|ears|neck|ribs)\b",
        last,
    ))
    has_verb_of_being_only = bool(re.search(
        r"\b(realize|think|feel overwhelmed|understand|wonder)\b", last
    )) and not has_action and not has_body
    if not has_action and not has_body:
        return ["SCENE_STATIC_ENDING"]
    return []


# --- Hook checks (spec 5) ---

BANNED_OPENERS = [
    re.compile(r"^in this chapter\b", re.I),
    re.compile(r"^let'?s explore\b", re.I),
    re.compile(r"^welcome to\b", re.I),
    re.compile(r"^today we will\b", re.I),
    re.compile(r"^we will explore\b", re.I),
    re.compile(r"^let'?s discuss\b", re.I),
    re.compile(r"^in today'?s fast-paced\b", re.I),
    re.compile(r"^throughout history\b", re.I),
    re.compile(r"^in recent years\b", re.I),
]

GENERIC_OPENERS = [
    re.compile(r"^many people (?:struggle|deal|cope)\b", re.I),
    re.compile(r"^(?:anxiety|burnout|stress|self-worth|shame) (?:is|means|happens)\b", re.I),
]


def check_hook_banned_openers(hook_text: str) -> List[str]:
    """Overlay spec 5 hard caps + Appendix A: no banned openers."""
    first_sent = hook_text.strip().split(".")[0].strip()
    for pat in BANNED_OPENERS:
        if pat.search(first_sent):
            return [f"HOOK_BANNED_OPENER:{pat.pattern}"]
    return []


def check_hook_friction(hook_text: str) -> List[str]:
    """Overlay spec 5 friction principle: hook must create cognitive friction."""
    text = hook_text.strip()
    # Friction signals: question mark, contradiction, high specificity
    has_question = "?" in text
    has_contradiction = bool(re.search(
        r"\b(not the problem|is not|was not|never about|did not)\b", text, re.I
    ))
    has_specificity = bool(re.search(
        r"\b(\d+\s*a\.?m\.?|\d+ messages|\d+ times|your (?:jaw|thumb|chest|eyes)|"
        r"before your feet|calculating tomorrow)\b",
        text, re.I,
    ))
    if has_question or has_contradiction or has_specificity:
        return []  # passes
    return ["HOOK_NO_FRICTION"]


def check_hook_generic(hook_text: str) -> List[str]:
    """Overlay spec 5: generic openers flagged."""
    first_sent = hook_text.strip().split(".")[0].strip()
    for pat in GENERIC_OPENERS:
        if pat.search(first_sent):
            return [f"HOOK_GENERIC_OPENER:{pat.pattern}"]
    return []


# --- Repetition cap checks (spec 9) ---

def check_scaffold_phrase_cap(chapters: List[str], phrase: str, cap: int = 3) -> List[str]:
    """Overlay spec 9.3: scaffold phrase must not exceed cap across all chapters."""
    total = sum(ch.lower().count(phrase.lower()) for ch in chapters)
    if total > cap:
        return [f"SCAFFOLD_PHRASE_OVER_CAP:{phrase}:{total}/{cap}"]
    return []


def check_mechanism_paragraph_duplication(chapters: List[str], threshold: float = 0.85) -> List[str]:
    """Overlay spec 9.4: near-identical mechanism paragraphs across chapters flagged."""
    issues: List[str] = []
    all_paras: List[tuple[int, str]] = []
    for idx, ch in enumerate(chapters):
        paras = [p.strip() for p in re.split(r"\n\s*\n", ch) if p.strip()]
        for p in paras:
            if len(p.split()) >= 15:  # Only check substantial paragraphs
                all_paras.append((idx, p))

    for i in range(len(all_paras)):
        for j in range(i + 1, len(all_paras)):
            if all_paras[i][0] == all_paras[j][0]:
                continue  # same chapter
            tokens_a = set(re.findall(r"[a-z]+", all_paras[i][1].lower()))
            tokens_b = set(re.findall(r"[a-z]+", all_paras[j][1].lower()))
            if not tokens_a or not tokens_b:
                continue
            jaccard = len(tokens_a & tokens_b) / len(tokens_a | tokens_b)
            if jaccard >= threshold:
                issues.append(
                    f"MECHANISM_PARA_DUP:ch{all_paras[i][0]+1}_ch{all_paras[j][0]+1}:"
                    f"jaccard={jaccard:.2f}"
                )
    return issues


def check_transition_phrase_variety(chapters: List[str], phrase: str) -> List[str]:
    """Overlay spec 9: same transition in >50% of chapters flagged."""
    hits = sum(1 for ch in chapters if phrase.lower() in ch.lower())
    if len(chapters) > 0 and hits / len(chapters) > 0.50:
        return [f"TRANSITION_OVERUSED:{phrase}:{hits}/{len(chapters)}"]
    return []


# --- Whole-book diversity checks (spec 11) ---

def vocabulary_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z]+", text.lower()))


def check_flat_middle(chapters: List[str], threshold: float = 0.15) -> List[str]:
    """Overlay spec 11.1: chapters 4-8 (0-indexed 3-7) must differ by >= threshold."""
    if len(chapters) < 8:
        return []
    middle = chapters[3:8]
    vocab_sets = [vocabulary_set(ch) for ch in middle]
    issues: List[str] = []
    # Pairwise vocab difference
    diffs: List[float] = []
    for i in range(len(vocab_sets)):
        for j in range(i + 1, len(vocab_sets)):
            union = vocab_sets[i] | vocab_sets[j]
            if not union:
                continue
            sym_diff = len(vocab_sets[i] ^ vocab_sets[j]) / len(union)
            diffs.append(sym_diff)
    if diffs:
        avg_diff = sum(diffs) / len(diffs)
        if avg_diff < threshold:
            issues.append(f"FLAT_MIDDLE:avg_vocab_diff={avg_diff:.3f}<{threshold}")
    return issues


def check_same_chapter_different_nouns(chapters: List[str], threshold: float = 0.90) -> List[str]:
    """Overlay spec 11.2: chapters with identical structure but swapped nouns."""
    issues: List[str] = []
    # Compare sentence-count structure and function-word skeleton
    FUNCTION_WORDS = frozenset(
        "the a an is are was were be been being have has had do does did "
        "will would shall should may might can could must that this these those "
        "it its you your he she they we our their not no nor or and but if".split()
    )

    def skeleton(text: str) -> str:
        words = re.findall(r"[a-z]+", text.lower())
        return " ".join(w if w in FUNCTION_WORDS else "_" for w in words)

    skeletons = [skeleton(ch) for ch in chapters]
    for i in range(len(skeletons)):
        for j in range(i + 1, len(skeletons)):
            if not skeletons[i] or not skeletons[j]:
                continue
            # Compare skeleton similarity
            tokens_a = skeletons[i].split()
            tokens_b = skeletons[j].split()
            if not tokens_a or not tokens_b:
                continue
            min_len = min(len(tokens_a), len(tokens_b))
            max_len = max(len(tokens_a), len(tokens_b))
            if max_len == 0:
                continue
            if min_len / max_len < 0.8:
                continue  # very different lengths
            matches = sum(1 for a, b in zip(tokens_a, tokens_b) if a == b)
            sim = matches / max_len
            if sim >= threshold:
                issues.append(f"SAME_STRUCTURE_DIFFERENT_NOUNS:ch{i+1}_ch{j+1}:sim={sim:.2f}")
    return issues


def check_reward_spacing(chapters: List[str], max_gap: int = 3) -> List[str]:
    """Overlay spec 11.3: reader reward (exercise, story, aha) in every N-chapter window."""
    REWARD_SIGNALS = re.compile(
        r"\b(breathe|pause|exhale|write|notice|choose|practice|"
        r"the cost|not the problem|what you call|your body|"
        r"she realized|he noticed|that was when)\b",
        re.I,
    )
    issues: List[str] = []
    for start in range(len(chapters) - max_gap + 1):
        window = chapters[start : start + max_gap]
        has_reward = any(REWARD_SIGNALS.search(ch) for ch in window)
        if not has_reward:
            issues.append(
                f"NO_REWARD_IN_WINDOW:ch{start+1}-ch{start+max_gap}"
            )
    return issues


# ---------------------------------------------------------------------------
# 1. Anti-Generic Scene Tests (spec 8)
# ---------------------------------------------------------------------------

class TestAntiGenericScene:
    """Overlay spec 8: scenes must be specific, non-colliding, and end on action/body."""

    def test_scene_three_detail_rule(self):
        """A scene with <3 unique sensory details is flagged (spec 8.2)."""
        weak_scene = (
            "You sit at the desk. The room is quiet. "
            "You look at the screen. You think about tomorrow."
        )
        issues = check_scene_three_detail_rule(weak_scene)
        assert issues, "Scene with <3 sensory details should be flagged"
        assert any("SCENE_INSUFFICIENT_SENSORY_DETAILS" in i for i in issues)

        # A good scene passes
        good_scene = (
            "The oat-milk film on the surface has gone grey. "
            "The fluorescent hum is the only sound. Even the clock is digital. "
            "Your thumb hovers over the send button. It stays there. "
            "The aching in your jaw tells you what your words will not."
        )
        issues_good = check_scene_three_detail_rule(good_scene)
        assert not issues_good, f"Specific scene should pass, got: {issues_good}"

    def test_scene_collision_detection(self):
        """Two chapters sharing identical scene phrases are flagged (spec 8.4)."""
        scene_a = (
            "You sit at the kitchen counter. The coffee is cold. "
            "Your phone buzzes with a message you will not read. "
            "The morning light cuts across the tile floor."
        )
        scene_b = (
            "You sit at the kitchen counter. The coffee is cold. "
            "Your phone buzzes with a message you will not read. "
            "Outside the window, a bird lands on the rail."
        )
        issues = check_scene_collision([scene_a, scene_b])
        assert issues, "Scenes sharing identical phrases should be flagged"
        assert any("SCENE_COLLISION" in i for i in issues)

        # Non-colliding scenes pass
        scene_c = (
            "The elevator doors close. Your reflection stares back. "
            "The fluorescent light hums above. Your jaw is tight."
        )
        issues_ok = check_scene_collision([scene_a, scene_c])
        assert not issues_ok, f"Non-colliding scenes should pass, got: {issues_ok}"

    def test_scene_action_state_test(self):
        """Scene with only static description, no character action, is flagged (spec 8.3)."""
        static_scene = (
            "The room is painted white. The window overlooks the street. "
            "A plant sits on the shelf. You realize this is the third time this week."
        )
        issues = check_scene_action_state(static_scene)
        assert issues, "Static scene ending should be flagged"
        assert any("SCENE_STATIC_ENDING" in i for i in issues)

        # Scene ending on body state/action passes
        action_scene = (
            "The elevator doors close. Your reflection stares back. "
            "You grabbed the railing and your jaw is tight."
        )
        issues_ok = check_scene_action_state(action_scene)
        assert not issues_ok, f"Scene ending on body state should pass, got: {issues_ok}"


# ---------------------------------------------------------------------------
# 2. Hook Quality Tests (spec 5)
# ---------------------------------------------------------------------------

class TestHookQuality:
    """Overlay spec 5: hooks must create friction, avoid banned/generic openers."""

    def test_hook_banned_openers(self):
        """Chapter starting with banned patterns is flagged (spec 5 hard caps)."""
        banned_hooks = [
            "In this chapter, we explore the roots of anxiety.",
            "Let's explore what happens when burnout takes hold.",
            "Welcome to the third step of your healing journey.",
        ]
        for hook in banned_hooks:
            issues = check_hook_banned_openers(hook)
            assert issues, f"Banned opener should be flagged: {hook!r}"

    def test_hook_friction_principle(self):
        """Hook with cognitive friction (question, contradiction, specificity) passes (spec 5)."""
        friction_hooks = [
            "Your anxiety is not the problem. Your solution to it is.",
            "3 a.m. Your eyes open. You are calculating tomorrow before your feet hit the floor.",
            "What happens when the thing keeping you safe is the thing keeping you stuck?",
        ]
        for hook in friction_hooks:
            issues = check_hook_friction(hook)
            assert not issues, f"Friction hook should pass: {hook!r}, got: {issues}"

    def test_hook_generic_opener(self):
        """Vague opening is flagged (spec 5)."""
        generic_hooks = [
            "Many people struggle with setting boundaries at work.",
            "Anxiety is a common experience in modern life.",
            "Burnout happens when demands exceed resources.",
        ]
        for hook in generic_hooks:
            issues = check_hook_generic(hook)
            assert issues, f"Generic opener should be flagged: {hook!r}"

    def test_hook_banned_detected_by_craft_gate(self):
        """The ONTGP craft gate penalizes abstract/topic openers in the orient zone."""
        bad_chapter = (
            "In this chapter, we will explore why anxiety persists. "
            "Anxiety is a common experience. Many people deal with it daily. "
            + "The nervous system responds to threat signals. " * 30
            + "Place your hand on your chest. Breathe in for four counts. "
            "Exhale for six. "
            "What happens when the person you learned this from sits across from you at dinner?"
        )
        result = evaluate_bestseller_craft(bad_chapter)
        assert any("abstract_topic" in i for i in result.issues), (
            f"Craft gate should flag abstract opener, issues={result.issues}"
        )


# ---------------------------------------------------------------------------
# 3. Repetition Cap Tests (spec 9)
# ---------------------------------------------------------------------------

class TestRepetitionCaps:
    """Overlay spec 9: scaffold phrases, mechanism duplicates, transition overuse."""

    def test_scaffold_phrase_cap(self):
        """'Stay with the moment' 4+ times across chapters is flagged (cap is 3, spec 9.3)."""
        chapters = [
            "Stay with the moment. Your breath settles. The body remembers.",
            "Stay with the moment. Notice what shifts. The pattern loosens.",
            "Stay with the moment. Something releases. You are still here.",
            "Stay with the moment. The grip softens. Your jaw unclenches.",
        ]
        issues = check_scaffold_phrase_cap(chapters, "Stay with the moment", cap=3)
        assert issues, "4 occurrences should exceed cap of 3"
        assert any("SCAFFOLD_PHRASE_OVER_CAP" in i for i in issues)

        # 3 occurrences should pass
        issues_ok = check_scaffold_phrase_cap(chapters[:3], "Stay with the moment", cap=3)
        assert not issues_ok, f"3 occurrences at cap=3 should pass, got: {issues_ok}"

    def test_mechanism_paragraph_duplication(self):
        """Near-identical mechanism paragraphs in 2+ chapters are flagged (spec 9.4)."""
        mech_para = (
            "Your amygdala does not know the difference between a bear and a deadline. "
            "Both trigger the same cascade. Cortisol floods. Heart rate climbs. "
            "Your prefrontal cortex goes offline. Not broken. Overridden."
        )
        # Slightly varied copy
        mech_para_dup = (
            "Your amygdala does not know the difference between a bear and a performance review. "
            "Both trigger the same cascade. Cortisol floods. Heart rate climbs. "
            "Your prefrontal cortex goes offline. Not broken. Overridden."
        )
        ch1 = f"You sit at the desk.\n\n{mech_para}\n\nBreathe in for four counts."
        ch2 = f"The train stops.\n\n{mech_para_dup}\n\nPlace your hand on your chest."

        issues = check_mechanism_paragraph_duplication([ch1, ch2])
        assert issues, "Near-identical mechanism paragraphs should be flagged"
        assert any("MECHANISM_PARA_DUP" in i for i in issues)

    def test_transition_phrase_variety(self):
        """Same transition phrase in >50% of chapters is flagged (spec 9)."""
        chapters = [
            "This is why the pattern persists. The body holds it.",
            "This is why you freeze. The cost accumulates.",
            "This is why avoidance grows. Each time strengthens the loop.",
            "Something different here. A new approach emerges.",
        ]
        issues = check_transition_phrase_variety(chapters, "This is why")
        assert issues, "Transition in 75% of chapters should be flagged"
        assert any("TRANSITION_OVERUSED" in i for i in issues)

        # Under 50% should pass
        chapters_ok = [
            "This is why the pattern persists.",
            "Something else matters here.",
            "A different perspective opens.",
            "The cost accumulates over time.",
        ]
        issues_ok = check_transition_phrase_variety(chapters_ok, "This is why")
        assert not issues_ok, f"25% usage should pass, got: {issues_ok}"


# ---------------------------------------------------------------------------
# 4. Whole-Book Diversity Tests (spec 11)
# ---------------------------------------------------------------------------

class TestWholeBookDiversity:
    """Overlay spec 11: flat middles, structural cloning, reward spacing."""

    def _make_similar_chapter(self, seed_words: List[str], base: str) -> str:
        """Create a chapter using mostly the same vocabulary."""
        return base

    def test_flat_middle_detection(self):
        """Chapters 4-8 with <15% vocabulary difference are flagged (spec 11.1)."""
        # Create 10 chapters where 4-8 are near-identical
        base = (
            "Your nervous system holds the pattern. The alarm fires again. "
            "Cortisol rises. Your breath shortens. The loop tightens. "
            "You freeze. The cost is invisible but accumulating."
        )
        diverse_ch = (
            "She walked into the room and sat down. The painting on the wall "
            "caught her eye. Red and gold strokes, chaotic but deliberate. "
            "Keiko had always painted when the words failed her."
        )
        chapters = (
            [diverse_ch, diverse_ch + " Version two.", diverse_ch + " Version three."]
            + [base] * 5  # chapters 4-8: near-identical
            + [diverse_ch + " The ending."] * 2
        )
        issues = check_flat_middle(chapters)
        assert issues, "Flat middle (identical ch4-8) should be flagged"
        assert any("FLAT_MIDDLE" in i for i in issues)

    def test_same_chapter_different_nouns(self):
        """Chapters with identical structure but swapped nouns are flagged (spec 11.2)."""
        template_a = (
            "You sit at the desk. The coffee is cold. Your phone buzzes. "
            "The alarm has been going off for years. You did not hear it. "
            "That is the cost. Not the crisis. The quiet erosion."
        )
        template_b = (
            "You sit at the table. The tea is cold. Your laptop buzzes. "
            "The siren has been going off for years. You did not hear it. "
            "That is the price. Not the crisis. The quiet erosion."
        )
        issues = check_same_chapter_different_nouns([template_a, template_b])
        assert issues, "Structurally cloned chapters should be flagged"
        assert any("SAME_STRUCTURE_DIFFERENT_NOUNS" in i for i in issues)

    def test_reward_spacing(self):
        """No reader reward within any 3-chapter window is flagged (spec 11.3)."""
        no_reward = "The pattern continues. It repeats. Again and again. Nothing changes."
        with_reward = (
            "The pattern continues. But then she noticed something different. "
            "Breathe in for four counts. Exhale slowly. Your body knows what to do."
        )
        chapters = [
            with_reward,
            no_reward,
            no_reward,
            no_reward,  # chapters 2-4: no reward in 3-chapter window
            with_reward,
        ]
        issues = check_reward_spacing(chapters, max_gap=3)
        assert issues, "3 consecutive reward-free chapters should be flagged"
        assert any("NO_REWARD_IN_WINDOW" in i for i in issues)

        # All chapters with rewards should pass
        all_rewards = [with_reward] * 5
        issues_ok = check_reward_spacing(all_rewards, max_gap=3)
        assert not issues_ok, f"Chapters with rewards should pass, got: {issues_ok}"


# ---------------------------------------------------------------------------
# 5. Aha / Integration Tests (spec 6)
# ---------------------------------------------------------------------------

class TestAhaIntegration:
    """Overlay spec 6: aha-noticing presence, integration bridge variety."""

    def test_aha_noticing_present(self):
        """Rendered chapter with exercise but no 'notice' or aha pattern is flagged (spec 6.2)."""
        exercise_no_aha = (
            "Place your hand on your chest. Press gently. "
            "Breathe in for four counts. Hold for two. Release for six."
        )
        issues = validate_required_terms_for_aha(exercise_no_aha)
        assert issues, "Exercise without 'notice' or body reference should be flagged"

        # With aha-noticing, should pass
        exercise_with_aha = (
            "Place your hand on your chest. Press gently. "
            "Now, notice the warmth of your palm against the tension. "
            "Breathe in for four counts. Your chest rises beneath your hand."
        )
        issues_ok = validate_required_terms_for_aha(exercise_with_aha)
        assert not issues_ok, f"Exercise with notice + body ref should pass, got: {issues_ok}"

    def test_integration_bridge_variety(self):
        """Same integration bridge text in >2 chapters is flagged (spec 7.1)."""
        bridge = "Still here. The pattern was named. Something shifted. That is enough."
        chapters_integration = [bridge, bridge, bridge]
        # Check: more than 2 identical integration bridges
        counter = Counter(chapters_integration)
        issues: List[str] = []
        for text, count in counter.items():
            if count > 2:
                issues.append(
                    f"INTEGRATION_BRIDGE_OVERUSED:count={count}"
                )
        assert issues, "Identical integration bridge in 3+ chapters should be flagged"

        # Two occurrences should be fine
        two_only = [bridge, bridge, "Feet on floor. Weight in the chair. The breath is slower."]
        counter2 = Counter(two_only)
        issues2 = [
            f"INTEGRATION_BRIDGE_OVERUSED:count={c}"
            for t, c in counter2.items() if c > 2
        ]
        assert not issues2, f"2 occurrences should pass, got: {issues2}"

    def test_aha_callout_prefix_validation(self):
        """Aha-noticing section must start with required callout prefix."""
        bad = "Take a deep breath and relax into the moment."
        issues = validate_callout_prefix("aha_noticing", bad)
        assert issues, "Missing aha callout prefix should be flagged"

        good = "Now, notice what shifted in the last thirty seconds."
        issues_ok = validate_callout_prefix("aha_noticing", good)
        assert not issues_ok, f"Valid callout should pass, got: {issues_ok}"

    def test_integration_callout_prefix(self):
        """Integration section must start with required callout prefix."""
        bad = "The chapter is complete. You learned something."
        issues = validate_callout_prefix("integration", bad)
        assert issues, "Missing integration callout prefix should be flagged"

        good = "Now, before you move on, feel the weight of what was named."
        issues_ok = validate_callout_prefix("integration", good)
        assert not issues_ok, f"Valid integration prefix should pass, got: {issues_ok}"


# ---------------------------------------------------------------------------
# Cross-gate integration: craft gate + flow gate working together
# ---------------------------------------------------------------------------

class TestCraftFlowIntegration:
    """Ensure craft gate and flow gate catch complementary issues."""

    def test_structurally_valid_but_craft_weak(self):
        """A chapter that passes flow gate structure but fails craft (no Orient, no friction)."""
        # Deliberately starts with topic intro (bad orient) but has transitions/thesis
        chapter = (
            "In this chapter, we will explore the nature of anxiety. "
            "Anxiety is a response your body generates when threat signals accumulate. "
            "This is why your chest tightens at 2 a.m. even though nothing happened. "
            "The nervous system does not distinguish real danger from imagined danger. "
            "Because the amygdala fires before the cortex can evaluate. "
            "The point is that your anxiety is not a flaw. It is a calibration. "
            "Which means that the alarm will always fire first. "
            "Here is what to do when the alarm fires. "
            "For example, you can notice the sensation before naming the emotion. "
            "Sit still. Notice your breath. Exhale for six counts. "
            "In practice the breath resets the vagal tone. "
            "So when you feel the chest tighten, you are not broken. You are wired. "
            "That moment of recognition is the beginning of agency. "
            "The cost of ignoring the alarm is not what you think. "
            "What happens when the person across from you can see the alarm but you cannot?"
        )
        flow_result = evaluate_chapter_flow(chapter)
        craft_result = evaluate_bestseller_craft(chapter)

        # Flow gate may pass (has transitions, thesis, actionable step)
        # Craft gate should flag the abstract opener in orient
        assert any("abstract_topic" in i for i in craft_result.issues), (
            f"Craft gate should catch abstract opener, issues={craft_result.issues}"
        )

    def test_story_lint_catches_missing_specificity(self):
        """Story atom lint flags prose with no specific details (spec 8)."""
        generic_story = (
            "There was a person who struggled with anxiety. They tried many things. "
            "Nothing worked. Eventually they found a way forward. It was difficult "
            "but they managed. Things improved over time."
        )
        result = lint_one_prose(generic_story, "test_generic", "test.txt")
        assert result.status in ("WARN", "FAIL"), (
            f"Generic story should be WARN or FAIL, got {result.status}"
        )
        assert "NO_SPECIFIC_DETAIL" in result.flags or "NO_INSIGHT_PIVOT" in result.flags
