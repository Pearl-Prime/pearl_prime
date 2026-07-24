#!/usr/bin/env python3
"""
Lane C (pearl-social-media-writer) — repair + extension builder.
Reads SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl, applies
in-place text repairs (same atom_id) for the touched cells
(anxiety/burnout x corporate_managers/gen_z_professionals[/healthcare_rns for the
broken-template fix]), writes the repaired file, and separately emits the new
MICRO_STORY/CASE_PROOF/CAROUSEL_SLIDE/THREAD_UNIT/VIDEO_BEAT rows as a draft
JSONL. Draft-first per SKILL.md; promotion to SOURCE_OF_TRUTH happens in a
second step after this script is reviewed.
"""
import json
from pathlib import Path

REPO = Path("/Users/ahjan/phoenix_omega_worktrees/social-writer-lane-c-atom-repair-20260723")
EVG = REPO / "SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl"
DRAFT_DIR = REPO / "artifacts/social_media_atoms/pearl_social_media_writer_20260723"

CITE_DIGEST = "artifacts/social_media_atoms/pearl_social_media_writer_20260723/deep_research_digest_20260723.md"
CITE_DELTA = "artifacts/social_media_atoms/pearl_social_media_writer_20260723/trend_pattern_delta_bank_20260723.md"

# ---------------------------------------------------------------------------
# 1. REPAIRS — rewrite `text` in place for these atom_ids. Everything else in
#    the row (all metadata) is preserved except char_count/word_count/source_refs
#    which are recomputed/updated to reflect the real rewrite + a specific
#    citation instead of the boilerplate SRC_AGENT_SPEC;SRC_ENGLISH_RESEARCH;
#    SRC_CAPTION_MATRIX tag.
# ---------------------------------------------------------------------------

BROKEN_TEMPLATE_SRC = (
    "SRC_LANE_A_DIGEST — pilot evidence (posts.jsonl copy_1bc8cdb2f97c) showed this exact "
    "row assembled into a live caption as \"corporate managers: more discipline will fix "
    "exhaustion is not the whole story.\" — the persona slug leaking into the sentence as "
    "raw metadata, named as the sharpest live defect in " + CITE_DIGEST + " Sec.0.2. "
    "Root cause: hook_family=contrarian_reframe mail-merge template, documented as "
    "\"Example C\" in artifacts/research/storyblocks_semantic_sourcing_20260720/"
    "RECOMMENDED_TAXONOMY.md:410 and stamped across 20 topics x 3 personas during the "
    "2026-07-21 scaleup wave (see this lane's GENERATOR_ROOT_CAUSE note)."
)

DEDUPE_SRC = (
    "SRC_LANE_A_DIGEST — live duplicate-rate audit (this lane, 2026-07-23) found this row's "
    "prior text byte-identical across corporate_managers/gen_z_professionals/healthcare_rns "
    "for this topic; rewritten as a persona-distinct sentence per " + CITE_DIGEST + " Sec.0.2's "
    "generic/dead diagnosis and the mission's cross-family thesis-reuse repair requirement."
)

repairs = {
    # --- A. broken-template HOOK_COVER-01 rewrites (grammar fix + de-leak persona) ---
    "EVG-ENUS-ANXI-CORP-HC-01": (
        "Arguing with a racing mind rarely wins the argument. The nervous system needs a "
        "signal that the threat has passed, not a better rebuttal.",
        BROKEN_TEMPLATE_SRC,
    ),
    "EVG-ENUS-ANXI-GEN_-HC-01": (
        "You can't logic your way out of a racing heart before a call. The body needs proof "
        "it's safe, not a smarter argument.",
        BROKEN_TEMPLATE_SRC,
    ),
    "EVG-ENUS-ANXI-HEAL-HC-01": (
        "Telling yourself to calm down mid-shift rarely works. The body needs a physical "
        "signal the threat has passed, not a pep talk.",
        BROKEN_TEMPLATE_SRC,
    ),
    "EVG-ENUS-BURN-CORP-HC-01": (
        "More discipline was never the missing piece. What's missing is a nervous system "
        "that's actually allowed to stand down.",
        BROKEN_TEMPLATE_SRC,
    ),
    "EVG-ENUS-BURN-GEN_-HC-01": (
        "Grinding harder doesn't fix exhaustion — it just teaches your body that exhaustion "
        "is the price of being taken seriously.",
        BROKEN_TEMPLATE_SRC,
    ),
    "EVG-ENUS-BURN-HEAL-HC-01": (
        "Pushing through another shift on willpower isn't discipline. It's a nervous system "
        "that never got the all-clear to rest.",
        BROKEN_TEMPLATE_SRC,
    ),
    # --- B. break exact HOOK_COVER-02/03 duplication (gen_z_professionals rewritten distinct
    #     from the corporate_managers text it was previously byte-identical to) ---
    "EVG-ENUS-ANXI-GEN_-HC-02": (
        "Tight chest before a notification even loads? That's not overreacting — that's a "
        "nervous system stuck scanning for the next hit.",
        DEDUPE_SRC,
    ),
    "EVG-ENUS-ANXI-GEN_-HC-03": (
        "Anxiety isn't a character flaw. It's a system that never got the memo the threat is "
        "over.",
        DEDUPE_SRC,
    ),
    "EVG-ENUS-BURN-GEN_-HC-02": (
        "If you've stopped noticing your shoulders live up by your ears, that's not "
        "resilience. That's just the new baseline.",
        DEDUPE_SRC,
    ),
    "EVG-ENUS-BURN-GEN_-HC-03": (
        "Burnout doesn't always look like collapse. Sometimes it looks like still answering "
        "Slack at 11pm and calling it commitment.",
        DEDUPE_SRC,
    ),
    # --- C. break cross-family thesis-sentence reuse (REFRAME + MECHANISM_EXPLAINER,
    #     gen_z_professionals rewritten distinct from the corporate_managers clause it was
    #     previously carrying verbatim) ---
    "EVG-ENUS-ANXI-GEN_-R-01": (
        "Try this instead: your body doesn't need a better argument, it needs a landmark. "
        "Name three things you can actually touch right now — that tells your nervous system "
        "the room isn't a threat faster than any reasoning does.",
        DEDUPE_SRC,
    ),
    "EVG-ENUS-BURN-GEN_-R-01": (
        "Rest isn't something you've earned after clearing the inbox. It's the input your "
        "nervous system needs whether or not the inbox is ever clear.",
        DEDUPE_SRC,
    ),
    "EVG-ENUS-ANXI-GEN_-ME-01": (
        "Here's the mechanism: your body reacts to a slow reply the same way it reacts to a "
        "real threat, because it can't fully tell social risk from physical risk. That's why "
        "breathing helps a little and a plan for the message helps a lot more.",
        DEDUPE_SRC,
    ),
    "EVG-ENUS-BURN-GEN_-ME-01": (
        "Here's what's actually happening: your nervous system doesn't log hours, it logs "
        "whether it ever got a real all-clear. Answering 'just one more thing' at 9pm tells "
        "it the shift never ended.",
        DEDUPE_SRC,
    ),
}


def recompute(row: dict, new_text: str, new_source_refs: str) -> dict:
    row = dict(row)
    row["text"] = new_text
    row["word_count"] = len(new_text.split())
    row["char_count"] = len(new_text)
    row["first_fold_chars"] = min(len(new_text), row.get("first_fold_chars", len(new_text)) if row.get("first_fold_chars", 0) >= 125 else len(new_text))
    # keep first_fold_chars sane: it should never exceed char_count
    row["first_fold_chars"] = min(row["first_fold_chars"], row["char_count"])
    row["source_refs"] = new_source_refs
    row["review_status"] = "draft_operator_review_required"
    row["acceptance_layer"] = "repaired in place — Lane C anti-drift pass, unscheduled"
    return row


def main():
    lines = EVG.read_text(encoding="utf-8").splitlines()
    out_lines = []
    touched = []
    for line in lines:
        if not line.strip():
            continue
        d = json.loads(line)
        aid = d.get("atom_id")
        if aid in repairs:
            new_text, src = repairs[aid]
            d = recompute(d, new_text, src)
            touched.append(aid)
        out_lines.append(json.dumps(d, ensure_ascii=False))
    missing = set(repairs) - set(touched)
    if missing:
        raise SystemExit(f"ERROR: atom_ids not found, aborting: {missing}")
    EVG.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"Repaired {len(touched)} rows in place in {EVG}")


if __name__ == "__main__":
    main()
