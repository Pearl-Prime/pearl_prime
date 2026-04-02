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
import re
from typing import Optional

from phoenix_v4.exercises.models import AssemblyContext


# ---------------------------------------------------------------------------
# Sentence utilities
# ---------------------------------------------------------------------------

def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


_PLACEHOLDER_RE = re.compile(r"^\[(?:Placeholder|Missing|Silence)\s*:")


def _is_placeholder_text(text: str) -> bool:
    return bool(_PLACEHOLDER_RE.match((text or "").strip()))


def _pick_variant(options: list[str], *seed_parts: str) -> str:
    if not options:
        return ""
    seed = "||".join((part or "").strip().lower() for part in seed_parts if part)
    if not seed:
        return options[0]
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    idx = int.from_bytes(digest[:8], "big") % len(options)
    return options[idx]


# ---------------------------------------------------------------------------
# Thesis derivation
# ---------------------------------------------------------------------------

def _derive_thesis(reflection: str) -> str:
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
    ]
    reflection_lower = reflection.lower()
    for marker, thesis in thesis_markers:
        if marker in reflection_lower:
            return thesis
    # Fallback: generic but still thesis-shaped
    return "The point is that you can act inside uncertainty without waiting for it to resolve."


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
        ]
    return _pick_variant(options, thesis, reflection, story)


def _bridge_before_integration(thesis: str, integration: str = "") -> str:
    """Bridge from EXERCISE → INTEGRATION."""
    options = [
        "Now notice what shifted before your mind starts summarizing it.",
        "Let the chapter land in the body before it turns back into explanation.",
        "Stay with what changed. Even if it only changed by one degree.",
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
    # Generic mechanism from thesis
    core = thesis.replace("The point is that ", "")
    return (
        f"Underneath the feeling is a simple mechanism: {core} "
        "When the alarm runs the response, your nervous system treats uncertainty like danger and asks for "
        "impossible certainty. That is why ordinary moments feel heavy."
    )


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
    return f"Remember this: {core} That is not a philosophy. That is what happened in this chapter."


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
    return "Start with the place in your body that lifted while you were listening. That is where the practice begins."


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
) -> str:
    """
    Compose a single chapter's prose from its slot types and resolved prose strings.

    Reorders slots into bestseller argument flow:
      Opening (HOOK/SCENE) → Bridge → Mechanism → Bridge → Reflection → Bridge →
      Story → Bridge → Exercise → Integration → Takeaway → Thread

    Returns the composed chapter text (no heading — caller adds 'Chapter N').
    """
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
    thesis = _derive_thesis(reflection_raw) if not _is_placeholder_text(reflection_raw) else ""

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

    # 7. Exercise with bridge (component-aware when exercise_context is provided)
    if exercise_raw and not _is_placeholder_text(exercise_raw):
        if exercise_context is not None:
            # Use the component assembler for context-aware exercise rendering
            try:
                from phoenix_v4.exercises.component_assembler import (
                    assemble_exercise_for_chapter,
                )
                composed_exercise = assemble_exercise_for_chapter(
                    exercise_id=exercise_context.exercise_id,
                    exercise_type="",  # resolved from templates
                    description_text=exercise_raw,
                    ctx=exercise_context,
                    aha_text="",  # resolved from standards
                    integration_text=integration_raw,
                )
                if composed_exercise.strip():
                    parts.append(composed_exercise)
                    # Skip the separate integration block below since it was
                    # included in the component assembly
                    integration_raw = ""
            except Exception:
                # Fallback to legacy hardcoded bridges on any import/runtime error
                parts.append(_bridge_before_exercise(thesis, reflection=reflection_raw, story=story_raw))
                parts.append(_exercise_setup_sentence(reflection_raw, story_raw))
                parts.append(exercise_raw)
        else:
            # Legacy path: hardcoded bridges (backward compatible)
            parts.append(_bridge_before_exercise(thesis, reflection=reflection_raw, story=story_raw))
            parts.append(_exercise_setup_sentence(reflection_raw, story_raw))
            parts.append(exercise_raw)

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
    return composed
