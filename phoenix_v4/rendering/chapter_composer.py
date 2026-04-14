"""
Bestseller chapter composer: transforms raw slot prose into thesis-threaded chapters.

Assembly order per chapter:
  HOOK/SCENE → bridge → STORY → PIVOT → bridge → MECHANISM (derived from REFLECTION) →
  REFLECTION (trimmed/warmed) → bridge → EXERCISE → COMPRESSION →
  PERMISSION (high-cost chapters only) → INTEGRATION → TAKEAWAY → THREAD

Bridge sentences create argument flow between slots so chapters
make argued points rather than presenting disconnected slot sequences.

Always-on for book renders. No opt-in flag required.
"""
from __future__ import annotations

import hashlib
import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_MAX_EXERCISES_PER_CHAPTER = 2

from phoenix_v4.exercises.models import AssemblyContext, EmotionalState

try:
    from phoenix_v4.rendering.locale_templates import get_template as _gt
except ImportError:
    def _gt(s, locale=None): return s


# ---------------------------------------------------------------------------
# Sentence utilities
# ---------------------------------------------------------------------------

def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


_PLACEHOLDER_RE = re.compile(r"^\[(?:Placeholder|Missing|Silence)\s*:")


def _is_placeholder_text(text: str) -> bool:
    return bool(_PLACEHOLDER_RE.match((text or "").strip()))


_CHAPTER_INDEX_TLS: int = 0  # Thread-local-ish chapter index for variant rotation

# Module-level locale for bridge functions (set by compose_chapter_prose)
_LOCALE_TLS: str | None = None

def _pick_variant(options: list[str], *seed_parts: str) -> str:
    if not options:
        return ""
    seed = "||".join((part or "").strip().lower() for part in seed_parts if part)
    if not seed:
        picked = options[_CHAPTER_INDEX_TLS % len(options)]
    else:
        # Mix in chapter index so same content in different chapters gets different picks
        seed = f"{seed}||ch{_CHAPTER_INDEX_TLS}"
        digest = hashlib.sha256(seed.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:8], "big") % len(options)
        picked = options[idx]
    # Locale-aware: translate the picked English string if locale is set
    return _gt(picked, locale=_LOCALE_TLS) if _LOCALE_TLS else picked


# ---------------------------------------------------------------------------
# Thesis derivation
# ---------------------------------------------------------------------------

def _derive_thesis(reflection: str, chapter_index: int = 0) -> str:
    """Extract a one-line thesis claim from REFLECTION prose."""
    sents = _sentences(reflection)
    # Priority keywords for thesis extraction
    thesis_markers = [
        ("perfect choice", "The point is that perfection is not available, but movement is."),
        ("regret", "The point is that anxiety predicts regret so loudly that it blocks useful decisions."),
        ("mechanism", "The point is that the mechanism treats every decision like a permanent threat."),
        ("alarm", "The point is that the alarm is information, not instruction."),
        ("comparison", "The point is that comparison uses someone else's exterior to judge your interior."),
        ("shame", "The point is that shame says you are the problem, but shame is a pattern, not a verdict."),
        ("watcher", "The point is that the part of you that watches is not the part that decides."),
        ("overwhelm", "The point is that overwhelm is a capacity signal, not a character flaw."),
        ("grief", "The point is that grief is not a problem to solve — it is a process to accompany."),
        ("spiral", "The point is that the spiral is a loop, not a descent — it returns to the same ground."),
        ("false alarm", "The point is that the alarm fires on prediction, not evidence."),
        # Adi Da / contemplative teacher vocabulary
        ("contraction", "The point is that the contraction is not who you are — it is what you do."),
        ("bright", "The point is that what you are seeking is already present before you start looking."),
        ("seeking", "The point is that seeking is the activity that obscures what is already here."),
        ("recognition", "The point is that recognition replaces seeking — you stop looking and start seeing."),
        ("separate self", "The point is that the separate self is an activity, not an entity."),
        ("avoidance", "The point is that avoidance maps the edges of what you are not yet willing to see."),
        ("relationship", "The point is that relationship is the mirror that reveals what you cannot see alone."),
        ("prior freedom", "The point is that freedom does not need to be achieved — it needs to be recognized."),
        ("vulnerability", "The point is that vulnerability is not the risk — the armor is."),
        # Emotional / somatic vocabulary
        ("nervous system", "The point is that your nervous system responds to predictions, not facts."),
        ("body", "The point is that the body knows before the mind does — trust the body."),
        ("holding", "The point is that what you are holding is costing more energy than you realize."),
        ("pattern", "The point is that seeing the pattern is the beginning of freedom from it."),
        ("rest", "The point is that rest is not earned — it is required."),
    ]
    reflection_lower = reflection.lower()
    # Collect ALL matching theses, then pick by chapter_index to rotate
    matched = [thesis for marker, thesis in thesis_markers if marker in reflection_lower]
    if matched:
        return matched[chapter_index % len(matched)]
    # Fallback: rotate across multiple generic theses using reflection hash + chapter_index
    _fallback_theses = [
        "The point is that you can act inside uncertainty without waiting for it to resolve.",
        "The point is that seeing the pattern clearly is the first step toward not being run by it.",
        "The point is that the feeling is real, but the story the feeling tells is often inaccurate.",
        "The point is that awareness does not fix anything — it makes fixing unnecessary.",
        "The point is that you have been working harder than you realize to stay contracted.",
        "The point is that what you are protecting yourself from is often less dangerous than the protection.",
        "The point is that ordinary moments carry the pattern more clearly than dramatic ones.",
    ]
    return _fallback_theses[(hash(reflection) + chapter_index) % len(_fallback_theses)]


# ---------------------------------------------------------------------------
# Bridge sentences (connect slots into argument flow)
# ---------------------------------------------------------------------------

def _bridge_after_opening(thesis: str, opening: str = "", scene: str = "") -> str:
    """Bridge from HOOK/SCENE → MECHANISM."""
    seed = f"{thesis} {opening} {scene}".lower()
    if "regret" in seed or "choice" in seed:
        options = [
            "This is why the freeze starts earlier than the choice: loss becomes imaginable before the decision does.",
            "What looks like indecision is usually grief arriving before the decision does. That matters because the body treats the prediction like fact.",
        ]
    elif "comparison" in seed:
        options = [
            "This is where comparison does its quiet damage: it makes another person's surface feel like evidence against you.",
            "The sting is not just what you saw. It is how fast your system turned it into a verdict, which means the pain starts before you can question the math.",
        ]
    elif "alarm" in seed or "false alarm" in seed:
        options = [
            "By the time you can explain the moment, the alarm has already chosen a meaning for it. That matters because the body is already obeying the prediction.",
            "The body is already behaving like the threat is real. This is where the chapter has to begin.",
        ]
    elif "shame" in seed:
        options = [
            "Shame always makes the same move first: it turns a moment into an identity sentence.",
            "The danger here is not the moment itself. It is the meaning shame races to stamp onto it, which means the injury often lands after the event.",
        ]
    elif "overwhelm" in seed:
        options = [
            "Shutdown rarely begins at the task. It begins where your system starts counting cost.",
            "What looks small on the screen can still feel expensive in the body. That matters because capacity gets spent before effort begins.",
        ]
    else:
        options = [
            "Stay with the moment a second longer. The pattern usually shows itself before the explanation does.",
            "That pause is doing more than slowing you down. It is showing you how the pattern enters, which means the chapter can name it before it hardens.",
            "Before the mind starts explaining, the body has already registered something. Trust that registration.",
            "The instinct to move past this moment quickly is itself data. Slow down and see what it protects.",
            "Something just shifted in your chest or your throat. That shift is where the chapter actually begins.",
            "Notice the impulse to understand before you have finished feeling. That impulse is the pattern defending itself.",
            "The body already knows something the mind has not caught up with yet. Let it lead for a moment.",
            "Right here is where the chapter earns its weight. Not in the concept, but in the felt registration.",
            "What you just felt is not a distraction from the point. It is the point arriving ahead of language.",
            "Hold this sensation without naming it. The name will come, but the sensation is more honest.",
            "There is a micro-flinch the body makes before the mind builds its story. That flinch is the trailhead.",
            "Do not skip ahead to the lesson. The body is still showing you where the lesson lives.",
        ]
    return _pick_variant(options, thesis, opening, scene)


def _bridge_before_story(thesis: str, reflection: str = "", story: str = "") -> str:
    """Bridge from REFLECTION → STORY."""
    seed = f"{thesis} {reflection} {story}".lower()
    if "comparison" in seed:
        options = [
            "For example, you can watch the pattern more clearly in somebody else's body before you can bear it in your own.",
            "Seen from the outside, the distortion gets harder to defend.",
        ]
    elif "shame" in seed:
        options = [
            "For example, watch where the sentence about identity gets written. It usually happens in a single beat.",
            "The pattern gets clearest when you can see the price land on a real person.",
        ]
    elif "choice" in seed or "regret" in seed:
        options = [
            "For example, the cost shows up fastest in a story. Watch how the prediction arrives before the fact does.",
            "You can see the mechanism better when it borrows someone else's future first.",
        ]
    else:
        options = [
            "Here is where the chapter stops talking about the pattern and lets you watch it happen.",
            "For example, the quickest way to feel the mechanism is to watch it take hold in an ordinary moment.",
            "What follows is not a metaphor. It is a report from someone who lived inside this pattern.",
            "The explanation can only go so far. A story goes the rest of the way.",
            "This is the turning point. Not a dramatic revelation. A quiet noticing.",
            "The pattern gets clearest when you watch it operate in someone else's day before returning to your own.",
            "Now watch what happens when the same pattern lands in a real body, in a real room.",
            "Theory describes the shape. A story lets you feel the weight of it.",
            "The next part is not instruction. It is evidence drawn from someone's lived experience.",
            "Concepts dissolve under pressure. What remains is the story of how the pressure actually felt.",
            "Here the chapter shifts from naming the pattern to witnessing it in motion.",
            "Words about the pattern only go so far. What follows is the pattern caught in the act.",
        ]
    return _pick_variant(options, thesis, reflection, story)


def _bridge_before_exercise(thesis: str, reflection: str = "", story: str = "") -> str:
    """Bridge from STORY → EXERCISE."""
    seed = f"{thesis} {reflection} {story}".lower()
    if "jaw" in seed or "sternum" in seed or "throat" in seed:
        options = [
            "So when the body tightens, do not solve the whole pattern here. Work with the place that braced first.",
            "In practice, start smaller than insight. Start where the body is still holding the chapter.",
        ]
    else:
        options = [
            "In practice, do not turn this into homework. Give the body one smaller, safer entry instead.",
            "So when the pattern surges, the next move is not to understand more. It is to make the first move cheaper.",
            "Understanding without practice is just information. The body needs something to do with what it just learned.",
            "The exercise that follows is not meant to fix anything. It is meant to make the pattern visible in your body.",
            "You do not need to master this. You need to try it once and notice what happens.",
            "Before moving on, give the body one concrete action. Insight without action evaporates by tomorrow.",
            "Now bring this from concept into sensation. The next step is deliberately small.",
            "The body learns through action, not agreement. Give it one move it can actually make right now.",
            "Knowing the pattern is not enough. The next step asks you to meet it with your body, not your mind.",
            "What follows is not a test. It is an invitation to feel the mechanism while it is still warm.",
            "Let the practice be undersized. A small move completed is worth more than a large one imagined.",
            "The shift from understanding to doing is where most chapters lose people. Stay with this one.",
        ]
    return _pick_variant(options, thesis, reflection, story)


def _bridge_before_integration(thesis: str, integration: str = "") -> str:
    """Bridge from EXERCISE → INTEGRATION."""
    options = [
        "Now notice what shifted before your mind starts summarizing it.",
        "Let the chapter land in the body before it turns back into explanation.",
        "Stay with what changed. Even if it only changed by one degree.",
        "Do not rush to the next thing. What just happened needs a few seconds to settle into the body.",
        "The shift may be small. Small is not insignificant. Small is where lasting change begins.",
        "Before the mind files this as 'done,' feel what is still open in the body. That openness is the real work.",
        "Pause here. The body is still processing what the mind already moved past.",
        "Give the landing a moment. The nervous system integrates slower than the reading eye.",
        "Whatever just moved in you does not need to be understood yet. It needs to be felt.",
        "Resist the urge to evaluate. Let the experience sit without a grade.",
        "The body registers change in its own time. Give it that time before the next chapter begins.",
        "Something loosened or something tightened. Either one is information worth keeping.",
    ]
    return _pick_variant(options, thesis, integration)


# ---------------------------------------------------------------------------
# Slot transforms
# ---------------------------------------------------------------------------

def _distill_mechanism(reflection: str, thesis: str) -> str:
    """Derive a mechanism-explanation paragraph from REFLECTION content."""
    reflection_lower = (reflection or "").lower()
    if "regret" in reflection_lower and "choice" in reflection_lower:
        return (
            "This is the mechanism underneath it: anxiety predicts regret so loudly that it drowns out your ability "
            "to make a useful decision. The mechanism is simple and brutal. The moment you choose one thing, your "
            "brain starts mourning everything you did not choose. It tries to find a perfect option with zero loss, "
            "but that option does not exist. Every path closes other paths. So the system freezes you, or lets you "
            "choose and then punishes you for choosing."
        )
    if "comparison" in reflection_lower:
        return (
            "The comparison engine runs on incomplete data. It takes someone "
            "else's visible output and measures it against your full interior experience. The comparison always "
            "loses because it is rigged — you see their best against your worst. The mechanism is automatic and "
            "relentless. Understanding it does not stop it. But it lets you see the score as inaccurate."
        )
    if "alarm" in reflection_lower or "false alarm" in reflection_lower:
        return (
            "The alarm fires on prediction, not evidence. Your nervous system "
            "treats anticipated social judgment with the same intensity it would treat physical danger. The alarm "
            "is not lying about the stakes as it perceives them. It is using an old threat model in a new context."
        )
    if "shame" in reflection_lower:
        return (
            "Shame selects the worst available interpretation and presents "
            "it as the only interpretation. It curates a database of your exposures and deletes evidence of "
            "competence. The assessment always finds you lacking because the database only contains evidence of lacking."
        )
    if "watcher" in reflection_lower or "watching" in reflection_lower:
        return (
            "The watcher is the shape anxiety takes when it turns inward. "
            "You watch yourself performing, then watch yourself watching, then evaluate how well you stopped watching. "
            "The recursion is infinite. Each layer creates a new layer to observe."
        )
    if "overwhelm" in reflection_lower:
        return (
            "Overwhelm is your capacity reaching its actual limit. Not your "
            "character failing, not your discipline collapsing — the demand has exceeded what the system can process "
            "right now. The mechanism treats this as emergency because, from the nervous system's perspective, it is."
        )
    if "grief" in reflection_lower or "loss" in reflection_lower:
        return (
            "Grief is your system processing an absence that it has not yet "
            "mapped. The neural pathways that expected the presence still fire. The mechanism is not broken — it is "
            "doing exactly what it should do when something significant has changed in the landscape."
        )
    if "spiral" in reflection_lower:
        return (
            "The spiral is a prediction engine running unchecked. Each link "
            "loads the next without waiting for evidence. The chain moves from signal to catastrophe in seconds. "
            "But each link is a prediction, not a fact. The chain has never once been right about the final link."
        )
    # Generic mechanism from thesis — rotate to avoid repetition
    core = thesis.replace("The point is that ", "")
    templates = [
        "Underneath the feeling is a simple mechanism: {core} When the alarm runs the response, your nervous system treats uncertainty like danger and asks for impossible certainty. That is why ordinary moments feel heavy.",
        "Here is the mechanism: {core} The nervous system does not distinguish between real threat and imagined threat. Both receive the same emergency response. This is why knowing better rarely helps.",
        "The pattern underneath: {core} Your body responds to the prediction of danger with the same chemistry it would use for actual danger. That chemistry does not care whether the prediction is accurate.",
        "What drives this: {core} The system was built for physical threats in open landscapes. It now runs in offices, apartments, and group chats. The mismatch between threat model and actual environment is the source of most suffering.",
        "The core mechanism is this: {core} Once the nervous system flags a moment as dangerous, it narrows perception to confirm the danger. Counter-evidence gets filtered out. The feeling becomes self-reinforcing.",
    ]
    picked = templates[hash(thesis) % len(templates)]
    if _LOCALE_TLS:
        picked = _gt(picked, locale=_LOCALE_TLS)
    try:
        return picked.format(core=core)
    except (KeyError, IndexError):
        return picked


def _trim_reflection(reflection: str, max_sentences: int = 7) -> str:
    """Trim REFLECTION to the most thesis-relevant sentences."""
    sents = _sentences(reflection)
    if not sents:
        return ""
    keep_keywords = (
        "choice", "cost", "regret", "perfect", "frozen", "adjust", "path",
        "mechanism", "alarm", "comparison", "shame", "watcher", "overwhelm",
        "grief", "spiral", "pattern", "system", "nervous",
    )
    chosen: list[str] = []
    for s in sents:
        low = s.lower()
        if any(k in low for k in keep_keywords):
            chosen.append(s)
        if len(chosen) >= max_sentences:
            break
    if len(chosen) < 4:
        chosen = sents[:max_sentences]
    joined = " ".join(chosen)
    # Strip academic hedging
    joined = re.sub(r"\bI have noticed that\s+", "", joined, flags=re.I)
    joined = re.sub(r"\bWhat I have come to understand is that\s+", "", joined, flags=re.I)
    joined = re.sub(r"\bWhat I have come to think about is\s+", "", joined, flags=re.I)
    joined = re.sub(r"\bWhat I have come to see is that\s+", "", joined, flags=re.I)
    joined = re.sub(r"\bWhat happens is that\s+", "", joined, flags=re.I)
    return joined.strip()


def _polish_scene(scene: str) -> str:
    """Fix common loc-var fallback collisions in SCENE prose."""
    s = (scene or "").strip()
    if not s:
        return s
    lower = s.lower()
    if "gray light through the window" in lower:
        replacement = "A washed-out stripe of light catches the glass"
        if any(token in lower for token in ("train", "platform", "car", "station")):
            replacement = "The train window throws your pale reflection back at you"
        elif any(token in lower for token in ("desk", "keyboard", "screen", "document", "inbox", "calendar")):
            replacement = "Late light smears across the edge of the desk"
        elif any(token in lower for token in ("hall", "office", "monitor", "keycard", "elevator")):
            replacement = "A pale rectangle from the hall window lies across the carpet"
        s = re.sub(r"gray light through the window(?:\s+(?:on|through|against)\s+(?:the\s+)?(?:glass|window))?", replacement, s, flags=re.I)
    s = s.replace("The gray light through the window afternoon", "The afternoon light is flat and gray")
    s = s.replace("through the window afternoon", "afternoon")
    s = re.sub(
        r"(?i)\b(fluorescent (?:station|tunnel) light) smears across the window through (?:your|the)\s+window\b",
        r"\1 smears across the window",
        s,
    )
    s = re.sub(
        r"(?i)\b(fluorescent (?:station|tunnel) light) smears across the window visible through the high windows\b",
        r"\1 is visible through the high windows",
        s,
    )
    s = re.sub(
        r"(?i)\b(fluorescent (?:station|tunnel) light) smears across the window against the building\b",
        r"\1 catches the building across from you",
        s,
    )
    s = re.sub(
        r"(?i)\b(fluorescent (?:station|tunnel) light) smears across the window is flat today\b",
        r"\1 lies flat across the window today",
        s,
    )
    s = s.replace("The the ", "The ")
    s = s.replace("the the ", "the ")
    s = s.replace("below below", "below")
    s = s.replace("through the window through the window", "against the window")
    s = re.sub(r"(?<=[.!?]\s)([a-z])", lambda m: m.group(1).upper(), s)
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s


def _fallback_takeaway(thesis: str) -> str:
    """Generate a takeaway when TAKEAWAY slot is missing/placeholder."""
    core = thesis.replace("The point is that ", "")
    template = "Remember this: {core} That is not a philosophy. That is what happened in this chapter."
    if _LOCALE_TLS:
        translated = _gt(template, locale=_LOCALE_TLS)
        try:
            return translated.format(core=core)
        except (KeyError, IndexError):
            return translated
    return template.format(core=core)


def _fallback_thread(thesis: str, chapter_index: int, total_chapters: int) -> str:
    """Generate a thread-forward when THREAD slot is missing/placeholder."""
    if chapter_index >= total_chapters - 1:
        return ""  # Last chapter: no thread-forward
    lower = thesis.lower()
    if "regret" in lower or "choice" in lower:
        return "What remains is the harder part: how to choose when loss still feels louder than relief."
    if "comparison" in lower:
        return "The next pressure point is harder to admit: what happens when someone else's life starts writing your standards for you."
    if "alarm" in lower or "false alarm" in lower:
        return "What remains is the moment after the alarm fires, when your body still wants to obey a prediction."
    if "shame" in lower:
        return "What remains is the sentence shame writes after the moment is over, when it tries to turn one event into identity."
    if "overwhelm" in lower:
        return "What remains is the quieter cost: what repeated overload teaches you to stop asking for."
    return "What remains is not more explanation. It is the next place this pattern asks for your life."


def _exercise_setup_sentence(reflection: str, story: str) -> str:
    seed = f"{reflection} {story}".lower()
    if "sternum" in seed or "chest" in seed:
        return "Start with the pressure under the sternum. That is the part still bracing."
    if "jaw" in seed:
        return "Start with the jaw that tightened while the story was unfolding."
    if "throat" in seed:
        return "Start with the throat that keeps rehearsing and swallowing the same sentence."
    if "shoulder" in seed or "shoulders" in seed:
        return "Start with the shoulders that lifted before you even noticed the cost."
    if "hand" in seed or "thumb" in seed or "trackpad" in seed:
        return "Start with the hand that hovered instead of moving. That freeze is the entry point."
    if "breath" in seed or "breathe" in seed:
        return "Start with the breath that shortened when the chapter turned."
    setup_fallbacks = [
        "Start with the place in your body that lifted while you were listening. That is where the practice begins.",
        "Start where you feel the most tension right now. Not where you think the tension should be — where it actually is.",
        "Begin with whatever your body is holding. You do not need to name it. Just locate it.",
        "Find the part of you that tightened during this chapter. That is your entry point.",
        "Notice where your body is bracing. Start there. Not with the thought — with the sensation.",
        "Scan from your scalp to your feet. The first place that speaks up is where you begin.",
        "Start with the part of you that wanted to look away during the last section.",
        "Place one hand where the tension is loudest. That contact is the first move.",
        "Begin where the weight settled. You will know the spot before you can explain it.",
        "Start with the simplest true thing your body is telling you right now.",
    ]
    return setup_fallbacks[hash(f"{reflection}{story}") % len(setup_fallbacks)]


def _shape_integration(integration: str) -> str:
    text = (integration or "").strip()
    if not text or _is_placeholder_text(text):
        return text
    sentences = _sentences(text)
    kept: list[str] = []
    for sentence in sentences:
        low = sentence.lower()
        if low.startswith("the point is") or low.startswith("what this means"):
            continue
        if len(re.findall(r"\b\w+\b", sentence)) <= 2 and low not in {"still here."}:
            continue
        kept.append(sentence)
    if not kept:
        kept = sentences[:3]
    total_words = 0
    limited: list[str] = []
    for sentence in kept:
        sentence_word_count = len(re.findall(r"\b\w+\b", sentence))
        if limited and total_words + sentence_word_count > 60:
            break
        limited.append(sentence)
        total_words += sentence_word_count
    return " ".join(limited or kept[:1])


def _emotional_state_from_arc_role(role: str) -> EmotionalState:
    r = (role or "").strip().lower()
    if r == "destabilization":
        return EmotionalState.HEAVY
    if r == "integration":
        return EmotionalState.CLOSE
    if r == "reframe":
        return EmotionalState.FLOW
    return EmotionalState.NEUTRAL


def _bump_exercise_stat(stats: dict | None, key: str) -> None:
    if stats is None:
        return
    stats[key] = int(stats.get(key, 0)) + 1
    stats["total"] = int(stats.get("total", 0)) + 1


def _build_assembly_context(
    chapter_index: int,
    total_chapters: int,
    emotional_role: str,
    exercise_atom_id: str,
    topic_id: str,
    persona_id: str,
    exercise_repeat_index: int,
) -> AssemblyContext:
    return AssemblyContext(
        first_encounter=chapter_index == 0,
        emotional_state=_emotional_state_from_arc_role(emotional_role),
        repeat_count=exercise_repeat_index,
        is_session_close=chapter_index >= max(total_chapters - 1, 0),
        persona=persona_id or "",
        exercise_id=exercise_atom_id or "",
        chapter_index=chapter_index,
        topic=topic_id or "",
    )


def _shape_thread(thread_raw: str, thesis: str, chapter_index: int, total_chapters: int) -> str:
    if thread_raw and not _is_placeholder_text(thread_raw):
        cleaned = re.sub(r"\bIn the next chapter,\s*", "", thread_raw, flags=re.I).strip()
        cleaned = re.sub(r"\bThere is more to explore\b[. ]*", "", cleaned, flags=re.I).strip()
        if cleaned:
            return cleaned
    return _fallback_thread(thesis, chapter_index, total_chapters)


# ---------------------------------------------------------------------------
# Main composition function
# ---------------------------------------------------------------------------

def compose_chapter_prose(
    slot_types: list[str],
    slot_proses: list[str],
    chapter_index: int = 0,
    total_chapters: int = 1,
    include_slot_labels_qa: bool = False,
    exercise_context: Optional[AssemblyContext] = None,
    locale: Optional[str] = None,
    *,
    topic_id: str = "",
    persona_id: str = "",
    emotional_role: str = "",
    exercise_atom_id: str = "",
    exercise_type_hint: str = "",
    exercise_repeat_index: int = 0,
    exercise_source_stats: Optional[dict] = None,
    book_seed: str = "",
) -> str:
    """
    Compose a single chapter's prose from its slot types and resolved prose strings.

    Reorders slots into bestseller argument flow:
      Opening (HOOK/SCENE) → Bridge → Mechanism → Bridge → Reflection → Bridge →
      Story → Bridge → Exercise → Integration → Takeaway → Thread

    Returns the composed chapter text (no heading — caller adds 'Chapter N').
    """
    # Set chapter index for variant rotation across all bridge/thesis functions
    global _CHAPTER_INDEX_TLS
    _CHAPTER_INDEX_TLS = chapter_index
    global _LOCALE_TLS
    _LOCALE_TLS = locale

    # Build slot_type → prose map (take first non-placeholder for each type)
    slot_map: dict[str, str] = {}
    for st, prose in zip(slot_types, slot_proses):
        st_upper = st.strip().upper()
        if st_upper not in slot_map or _is_placeholder_text(slot_map[st_upper]):
            slot_map[st_upper] = prose

    # Extract slot content
    hook = slot_map.get("HOOK", "")
    scene = _polish_scene(slot_map.get("SCENE", ""))
    story_raw = slot_map.get("STORY", "")
    pivot_raw = slot_map.get("PIVOT", "")
    reflection_raw = slot_map.get("REFLECTION", "")
    integration_raw = _shape_integration(slot_map.get("INTEGRATION", ""))
    exercise_raw = slot_map.get("EXERCISE", "")
    permission_raw = slot_map.get("PERMISSION", "")
    takeaway_raw = slot_map.get("TAKEAWAY", "")
    thread_raw = slot_map.get("THREAD", "")
    compression_raw = slot_map.get("COMPRESSION", "")

    # Derive thesis from reflection content
    thesis = _derive_thesis(reflection_raw, chapter_index) if not _is_placeholder_text(reflection_raw) else ""

    # Build composed chapter in argument order
    parts: list[str] = []

    # 1. Opening (prefer HOOK for body-first immediacy, use SCENE as fallback)
    opening = hook if (hook and not _is_placeholder_text(hook)) else scene
    if opening and not _is_placeholder_text(opening):
        parts.append(opening)

    # 2. SCENE (if both HOOK and SCENE exist, scene follows hook)
    if hook and scene and not _is_placeholder_text(hook) and not _is_placeholder_text(scene) and scene != opening:
        parts.append(scene)

    # 3. Bridge → Mechanism (derived from reflection)
    if thesis:
        parts.append(_bridge_after_opening(thesis, opening=opening, scene=scene))
        mechanism = _distill_mechanism(reflection_raw, thesis)
        parts.append(mechanism)
        parts.append(thesis)

    # 4. Trimmed reflection (the teaching layer — trimmed to thesis-relevant sentences)
    if reflection_raw and not _is_placeholder_text(reflection_raw):
        trimmed = _trim_reflection(reflection_raw)
        if trimmed:
            parts.append(trimmed)

    # 5. STORY with optional QA label
    if story_raw and not _is_placeholder_text(story_raw):
        parts.append(_bridge_before_story(thesis, reflection=reflection_raw, story=story_raw))
        if include_slot_labels_qa:
            # Find the original atom_id for STORY
            for st, prose in zip(slot_types, slot_proses):
                if st.strip().upper() == "STORY" and prose == story_raw:
                    break
        parts.append(story_raw)

    # 5a. PIVOT (land the story before teaching — Writer Spec §4.3a)
    # PIVOT names what the story revealed without explaining. Placed between STORY and REFLECTION.
    if pivot_raw and not _is_placeholder_text(pivot_raw):
        parts.append(pivot_raw)

    # 6. COMPRESSION (if present, adds density/summary)
    if compression_raw and not _is_placeholder_text(compression_raw):
        parts.append(compression_raw)

    # 7. Exercise with bridge
    # If exercise is placeholder or empty, try practice library (272 exercises with aha + integration)
    exercise_from_library_34 = False
    if _is_placeholder_text(exercise_raw) or not exercise_raw:
        try:
            from phoenix_v4.exercises.practice_library_loader import get_exercise_for_chapter
            seed = book_seed or f"ch{chapter_index}:{thesis[:20]}"
            composed = get_exercise_for_chapter(
                chapter_index=chapter_index,
                topic_id=topic_id,
                persona_id=persona_id,
                seed=seed,
            )
            if composed:
                exercise_raw = composed
                exercise_from_library_34 = True
        except Exception:
            pass

    if exercise_raw and not _is_placeholder_text(exercise_raw):
        eff_context = exercise_context or _build_assembly_context(
            chapter_index=chapter_index,
            total_chapters=total_chapters,
            emotional_role=emotional_role,
            exercise_atom_id=exercise_atom_id,
            topic_id=topic_id,
            persona_id=persona_id,
            exercise_repeat_index=exercise_repeat_index,
        )
        assembled_ok = False
        try:
            from phoenix_v4.exercises.component_assembler import assemble_exercise_for_chapter

            composed_exercise = assemble_exercise_for_chapter(
                exercise_id=eff_context.exercise_id or exercise_atom_id,
                exercise_type=exercise_type_hint,
                description_text=exercise_raw,
                ctx=eff_context,
                aha_text="",
                integration_text=integration_raw,
            )
            if composed_exercise.strip():
                setup = _exercise_setup_sentence(reflection_raw, story_raw)
                if setup:
                    parts.append(setup)
                parts.append(composed_exercise)
                assembled_ok = True
                if exercise_from_library_34:
                    _bump_exercise_stat(exercise_source_stats, "library_34_fallback")
                else:
                    _bump_exercise_stat(exercise_source_stats, "registry")
                integration_raw = ""
        except Exception:
            assembled_ok = False

        if not assembled_ok:
            # Legacy wrap: rotating bridges + Phoenix aha/integration via practice_library_loader
            try:
                from phoenix_v4.exercises.practice_library_loader import compose_exercise, load_component_templates

                composed = compose_exercise(
                    exercise={"name": "Exercise", "text": exercise_raw, "exercise_type": "body_awareness"},
                    chapter_index=chapter_index,
                    seed=book_seed or f"ch{chapter_index}:{thesis[:20]}",
                    templates=load_component_templates(),
                )
                if composed:
                    setup = _exercise_setup_sentence(reflection_raw, story_raw)
                    parts.append(setup)
                    parts.append(composed)
                    integration_raw = ""
                    if exercise_from_library_34:
                        _bump_exercise_stat(exercise_source_stats, "library_34_fallback")
                    else:
                        _bump_exercise_stat(exercise_source_stats, "registry")
                else:
                    raise ValueError("empty compose")
            except Exception:
                parts.append(_bridge_before_exercise(thesis, reflection=reflection_raw, story=story_raw))
                parts.append(_exercise_setup_sentence(reflection_raw, story_raw))
                parts.append(exercise_raw)
                if exercise_from_library_34:
                    _bump_exercise_stat(exercise_source_stats, "library_34_fallback")
                else:
                    _bump_exercise_stat(exercise_source_stats, "registry")

    # 7a. PERMISSION (receive the reader — Writer Spec §4.8)
    # Short emotional permission statement placed near INTEGRATION. High-cost chapters only.
    if permission_raw and not _is_placeholder_text(permission_raw):
        parts.append(permission_raw)

    # 8. Integration with bridge
    if integration_raw and not _is_placeholder_text(integration_raw):
        parts.append(_bridge_before_integration(thesis, integration=integration_raw))
        parts.append(integration_raw)
    elif thesis:
        # Fallback takeaway when integration is missing
        parts.append(_fallback_takeaway(thesis))

    # 9. Takeaway (explicit slot or fallback)
    if takeaway_raw and not _is_placeholder_text(takeaway_raw):
        parts.append(takeaway_raw)

    # 10. Thread-forward (explicit slot or fallback)
    thread = _shape_thread(thread_raw, thesis, chapter_index, total_chapters) if thesis else ""
    if thread:
        parts.append(thread)

    # Filter empty parts and join
    composed = "\n\n".join(p for p in parts if p and p.strip())

    # Locale post-processing: replace English template strings with locale versions
    if locale and locale != "en-US":
        try:
            from phoenix_v4.rendering.locale_templates import localize_rendered_text
            composed = localize_rendered_text(composed, locale)
        except ImportError:
            pass

    return composed


def compose_from_enriched_book(
    enriched: "EnrichedBook",
    quality_profile: str = "draft",
    *,
    governance_report: Optional[dict[str, Any]] = None,
) -> str:
    """
    Render an EnrichedBook to prose text.

    New pipeline path:
      Spine → Knobs → Beatmap → Enrichment → this → BookRender.

    The legacy path (assembly_compiler → compose_chapter_prose) is unchanged.
    Pilot behavior: concatenate slot bodies in beatmap order; skip visible gaps.

    Args:
        enriched: Output of phoenix_v4.planning.enrichment_select.select_enrichment
        quality_profile: Reserved for future quality-specific polishing (unused in pilot).
        governance_report: Optional mutable dict for telemetry
            (exercise_slots_dropped, chapter_contract_warnings, frame_governance_chapters,
            frame_softened_sentences, frame_stripped_sentences, frame_hard_fail_reasons).
    """
    del quality_profile  # pilot — reserved

    report = governance_report if governance_report is not None else {}
    report.setdefault("exercise_slots_dropped", [])
    report.setdefault("chapter_contract_warnings", [])
    report.setdefault("frame_governance_chapters", [])
    report.setdefault("frame_softened_sentences", [])
    report.setdefault("frame_stripped_sentences", [])
    report.setdefault("frame_hard_fail_reasons", [])

    try:
        from phoenix_v4.quality.ei_v2.config import load_ei_v2_config

        ei_cfg = load_ei_v2_config() or {}
    except Exception:
        ei_cfg = {}
    ex_gov = ei_cfg.get("exercise_governance") or {}
    format_default = int(ex_gov.get("max_per_chapter_default", DEFAULT_MAX_EXERCISES_PER_CHAPTER))
    overrides = ex_gov.get("override_per_format") or {}
    rid = (enriched.runtime_format or "").strip()
    format_cap = int(overrides[rid]) if rid in overrides else format_default

    from phoenix_v4.planning.chapter_planner import assign_chapter_purpose_contracts

    contracts = assign_chapter_purpose_contracts(
        len(enriched.chapters),
        enriched.runtime_format,
    )

    from phoenix_v4.quality.frame_governor import (
        FrameEnforcementContext,
        apply_frame_enforcement,
        load_frame_registry,
    )

    frame_registry = load_frame_registry()
    frame = str((enriched.spine_context or {}).get("frame") or "somatic_first").strip()

    chapters_prose: list[str] = []
    for ch_idx, ch in enumerate(enriched.chapters):
        contract = contracts[ch_idx] if ch_idx < len(contracts) else contracts[-1]
        max_allowed = min(int(contract.max_exercises), format_cap)

        ex_seen = 0
        slots_out = []
        for slot in ch.slots:
            st = str(slot.slot_type or "").strip().upper()
            if st == "EXERCISE":
                if ex_seen < max_allowed:
                    slots_out.append(slot)
                    ex_seen += 1
                else:
                    entry = {
                        "chapter": ch.number,
                        "chapter_index": ch_idx,
                        "slot_type": st,
                        "max_allowed": max_allowed,
                        "contract_max_exercises": contract.max_exercises,
                        "format_cap": format_cap,
                    }
                    if isinstance(report["exercise_slots_dropped"], list):
                        report["exercise_slots_dropped"].append(entry)
                    logger.warning(
                        "Exercise governance: dropped EXERCISE slot in chapter %s (cap=%s).",
                        ch.number,
                        max_allowed,
                    )
            else:
                slots_out.append(slot)

        if ch_idx > 0 and contracts[ch_idx].emotional_job == contracts[ch_idx - 1].emotional_job:
            msg = (
                f"chapter {ch.number}: emotional_job {contracts[ch_idx].emotional_job!r} "
                f"matches previous chapter — escalation contract may be weak"
            )
            if isinstance(report["chapter_contract_warnings"], list):
                report["chapter_contract_warnings"].append(msg)
            logger.warning("Chapter contract: %s", msg)

        if contracts[ch_idx].emotional_job in contracts[ch_idx].forbidden_repeats:
            msg = (
                f"chapter {ch.number}: emotional_job {contracts[ch_idx].emotional_job!r} "
                f"is listed in its own forbidden_repeats (YAML check)"
            )
            if isinstance(report["chapter_contract_warnings"], list):
                report["chapter_contract_warnings"].append(msg)

        chapter_body_parts: list[str] = []
        for slot in slots_out:
            if slot.content and not slot.content.startswith("[CONTENT GAP"):
                chapter_body_parts.append(slot.content)
        ch_body = "\n\n".join(chapter_body_parts)
        has_doctrine = any(
            str(s.slot_type or "").strip().upper() == "TEACHER_DOCTRINE" for s in slots_out
        )
        fe_ctx = FrameEnforcementContext(
            chapter_index=ch_idx,
            frame=frame,
            doctrine_chapter=has_doctrine,
            allow_early_spiritual=bool(contract.allow_early_spiritual),
            emotional_job=str(contract.emotional_job or ""),
        )
        ch_body, fg = apply_frame_enforcement(ch_body, fe_ctx, frame_registry)
        chapter_text = f"Chapter {ch.number}\n{ch.working_title}\n\n"
        if ch_body.strip():
            chapter_text += ch_body.strip() + "\n\n"
        chapters_prose.append(chapter_text.rstrip())

        if isinstance(report["frame_softened_sentences"], list):
            report["frame_softened_sentences"].extend(fg.softened_sentences)
        if isinstance(report["frame_stripped_sentences"], list):
            report["frame_stripped_sentences"].extend(fg.stripped_sentences)
        if isinstance(report["frame_hard_fail_reasons"], list):
            report["frame_hard_fail_reasons"].extend(fg.hard_fail_reasons)
        if (
            fg.violations
            or fg.softened_sentences
            or fg.stripped_sentences
            or fg.hard_fail_reasons
            or not fg.frame_compliant
        ):
            if isinstance(report["frame_governance_chapters"], list):
                report["frame_governance_chapters"].append(
                    {
                        "chapter": ch.number,
                        "chapter_index": ch_idx,
                        "violations": fg.violations,
                        "softened": fg.softened_sentences,
                        "stripped": fg.stripped_sentences,
                        "hard_fail": fg.hard_fail_reasons,
                        "frame_compliant": fg.frame_compliant,
                        "spiritual_density": fg.spiritual_density,
                    },
                )
            if fg.violations and not fg.softened_sentences and not fg.stripped_sentences:
                logger.warning(
                    "Frame governance (%s) chapter %s: %d open issue(s).",
                    frame,
                    ch.number,
                    len(fg.violations),
                )

    manuscript = "\n\n".join(chapters_prose)
    from phoenix_v4.quality.chapter_flow_gate import flow_profile_for_runtime_format
    from phoenix_v4.rendering.book_renderer import strengthen_rendered_spine_manuscript

    spine_seed = f"spine:{enriched.persona_id}:{enriched.topic}:{enriched.runtime_format}"
    profile = flow_profile_for_runtime_format(enriched.runtime_format)
    return strengthen_rendered_spine_manuscript(
        manuscript, book_seed=spine_seed, flow_profile=profile
    )
