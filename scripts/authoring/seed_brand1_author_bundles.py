#!/usr/bin/env python3
"""Seed the 12 stillness_press pen-name authors' 4-asset bundles.

Per docs/authoring/AUTHOR_ASSET_WORKBOOK.md, each author needs:
  bio.yaml                  120-180 words, 3rd person
  why_this_book.yaml        150-250 words, topic-keyed
  authority_position.yaml   100-150 words, structured
  audiobook_pre_intro.yaml  500-900 words across 7 blocks

For stillness_press (Teacher Mode, teacher: ahjan), per
TEACHER_MODE_AUTHORING_PLAYBOOK.md §8.1, the author is interpreter and
applicator of Ahjan's contemplative-Buddhism teaching — not originator.
Voicing locks in:

- "What Ahjan calls..." / "In Ahjan's framework..." / "Drawing on Ahjan's work..."
- NEVER "I discovered..." / "My breakthrough was..." / "This method guarantees..."
- Pre-Intro per §8.2: clarifies author encountered the work through books/talks
  not direct study; states why Ahjan matters for this topic; bounds scope to
  application not replacement.

Bios are sourced and refined from the canonical roster
(config/catalog_planning/teacher_brand_author_roster.yaml §01).

This script emits the 48 YAMLs (12 authors × 4 assets) into
assets/authors/<author_id>/ and writes a manifest of word counts so the
content lead can verify all bundles are within workbook bands before
flipping status: draft → approved.

Usage:
  python3 scripts/authoring/seed_brand1_author_bundles.py [--force]
  python3 scripts/authoring/seed_brand1_author_bundles.py --verify  # just word counts
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
ASSETS_ROOT = REPO_ROOT / "assets" / "authors"


def wc(text: str) -> int:
    return len(text.split())


# ─── Per-author content ───────────────────────────────────────────────────────
# Keys per author:
#   pen_name, narrator_name, narrator_archetype, primary_topic, series_line
#   bio (~150 wd, 3rd-person)
#   why_this_book (~200 wd; first sentence "[Author] began writing...")
#   authority (does_not_claim/promise, recommends_professional_support_for, resolution_compatibility)
#   author_background (~70 wd, condensed bio for narrator)
#   audio_why_this_book (~120 wd, condensed for narrator with Teacher-Mode framing)


AUTHORS: dict[str, dict[str, Any]] = {

    # ─── lena_thorne — somatic_companion, anxiety+sleep_anxiety ──────────
    "lena_thorne": {
        "pen_name": "Lena Thorne",
        "narrator_name": "Cora Whitfield",
        "narrator_archetype": "warm_regulating",
        "primary_topic": "anxiety",
        "series_line": "This audiobook is part of the Stillness Press Series, drawing on Ahjan's contemplative-Buddhism teaching of the alarm system.",
        "bio": (
            "Lena Thorne spent fifteen years as an ICU nurse before the panic attacks made her stop. "
            "What she found in recovery wasn't a cure — it was a way to see the alarm in the body for what it was, "
            "and a way to teach others to see it before their bodies arrived where hers had. "
            "She works with healthcare professionals and millennial women who have spent years performing competence "
            "while their nervous systems quietly raised the floor on what counted as a normal day. "
            "Her writing draws on Ahjan's contemplative-Buddhism framework of the alarm within, applied to the specific "
            "exhaustion that follows people whose work asks them to stay calm in other people's emergencies. "
            "Her practice focuses on the early signals — the tight chest in the locker room, the held breath in the "
            "elevator — that people learn to ignore because the work does not pause for them. "
            "She is based in Portland."
        ),
        "why_this_book": (
            "Lena began writing this after watching a familiar pattern repeat across years of ICU shifts and the "
            "professionals she now works with: people whose chests went tight on the way to work, whose hands shook "
            "while charting, whose sleep got thinner each year. They were not weak. They were not new. Their bodies "
            "were running an alarm system that had been useful in one context and ruinous in another. "
            "What Ahjan calls the alarm within — a nervous-system pattern that fires regardless of present safety — "
            "gave Lena a language for what she had been watching. "
            "Most of what was available told these professionals to manage their thoughts or rest harder. None of it "
            "addressed the body first. "
            "This book does not diagnose anxiety or promise its absence. It offers entry points for noticing the alarm "
            "before it tips into crisis, drawing on a contemplative tradition that has watched human nervous systems "
            "for two and a half thousand years."
        ),
        "authority": {
            "does_not_claim": [
                "clinical diagnosis of anxiety or any DSM condition",
                "psychotherapy or somatic trauma therapy",
                "neurological or psychiatric assessment",
                "guaranteed reduction of anxiety symptoms within a defined period",
            ],
            "does_not_promise": [
                "elimination of anxiety or panic attacks",
                "transformation of nervous-system baseline",
                "recovery from clinical anxiety disorders",
                "fixed timeline for change",
            ],
            "recommends_professional_support_for": [
                "clinical anxiety or panic disorder",
                "trauma history requiring therapeutic containment",
                "medication-related questions or adjustments",
                "active mental health crises",
            ],
            "resolution_compatibility": ["grounded_shift", "partial_resolution"],
        },
        "author_background": (
            "Lena is a former ICU nurse who turned her own panic-attack recovery into a practice of supporting "
            "healthcare professionals navigating the alarm their work installs in their bodies. Her approach is "
            "grounded, body-first, and rooted in Ahjan's contemplative-Buddhism teaching of the alarm system. "
            "She is based in Portland."
        ),
        "audio_why_this_book": (
            "Lena began writing this after watching the same pattern across years of ICU shifts and the professionals "
            "she now works with: tight chests, shaking hands, thinner sleep. What Ahjan calls the alarm within — a "
            "nervous-system pattern firing regardless of present safety — gave her a language for what she had been "
            "watching. She did not study with Ahjan in person; she encountered his teaching through books and talks. "
            "This book does not promise the absence of anxiety. It offers the body-first entry points she wishes she had "
            "had earlier."
        ),
    },

    # ─── daniel_voss — research_guide, burnout+imposter_syndrome ──────────
    "daniel_voss": {
        "pen_name": "Daniel Voss",
        "narrator_name": "Aubrey Tate",
        "narrator_archetype": "british_authority",
        "primary_topic": "burnout",
        "series_line": "This audiobook is part of the Stillness Press Series, applying Ahjan's contemplative-Buddhism alarm framework to the science of burnout.",
        "bio": (
            "Daniel Voss is a behavioral neuroscientist who left academic research after realizing the literature on "
            "alarm systems was more useful outside the lab than inside it. He works with high-performing professionals "
            "in tech, finance, and corporate management — people whose careers reward the very nervous-system patterns "
            "that produce burnout and imposter syndrome. "
            "His writing translates contemplative-neuroscience research into practical terms, drawing on Ahjan's "
            "framework of the alarm within to explain why the body keeps insisting on threat in environments that "
            "look — on paper — like opportunity. "
            "His approach refuses the false choice between clinical pathologizing and motivational reframing; instead, "
            "it offers grounded explanatory clarity for readers who want to understand the mechanism before they trust "
            "the practice. "
            "He is based in Cambridge, Massachusetts."
        ),
        "why_this_book": (
            "Daniel began writing this after a decade of research on threat-detection systems and another half-decade "
            "of corporate consulting. The same pattern kept showing up across both: capable people, often at the top of "
            "their fields, whose bodies were running a continuous low-grade emergency they could not name. They refreshed "
            "Slack at midnight. They rehearsed conversations that had already ended. They felt one mistake away from "
            "exposure, regardless of how decorated their CVs were. "
            "What Ahjan calls the alarm within mapped cleanly onto what Daniel had been measuring in the lab. The "
            "framework gave him a way to name burnout without medicalizing it and without dismissing it as a productivity "
            "problem. "
            "Most existing writing offered either clinical pathology or hustle-culture reframes. Neither fit the people "
            "Daniel was watching. "
            "This book does not promise to eliminate burnout. It offers the science of why the alarm fires when there "
            "is nothing to escape, alongside the contemplative practices that have addressed that fire long before "
            "neuroscience could measure it."
        ),
        "authority": {
            "does_not_claim": [
                "clinical diagnosis of burnout, depression, or any DSM condition",
                "psychotherapy or clinical treatment",
                "neurological assessment of individual readers",
                "career or organizational coaching",
            ],
            "does_not_promise": [
                "elimination of burnout symptoms",
                "career advancement as a result of reading",
                "transformation of organizational stress",
                "fixed timeline for nervous-system change",
            ],
            "recommends_professional_support_for": [
                "clinical depression intersecting with burnout",
                "trauma histories of workplace harm",
                "medication-related questions",
                "any condition requiring medical management",
            ],
            "resolution_compatibility": ["grounded_shift", "partial_resolution"],
        },
        "author_background": (
            "Daniel is a behavioral neuroscientist who left academia to work with high-performing professionals on the "
            "alarm patterns their careers reward. He bridges contemplative-neuroscience research with Ahjan's framework "
            "of the alarm within. He is based in Cambridge, Massachusetts."
        ),
        "audio_why_this_book": (
            "Daniel began writing this after a decade of research on threat-detection systems and another half-decade "
            "of corporate work. The same pattern repeated: capable people running a continuous low-grade emergency they "
            "could not name. What Ahjan calls the alarm within mapped onto what Daniel had been measuring. He did not "
            "train under Ahjan; he encountered his teaching through books and talks. This book does not promise to "
            "eliminate burnout. It offers the science of why the alarm fires when there is nothing to escape, alongside "
            "the contemplative practices that addressed that fire long before neuroscience could measure it."
        ),
    },

    # ─── mira_santos — somatic_companion, grief+self_worth ───────────────
    "mira_santos": {
        "pen_name": "Mira Santos",
        "narrator_name": "Anneliese Voss",
        "narrator_archetype": "soft_compassion",
        "primary_topic": "grief",
        "series_line": "This audiobook is part of the Stillness Press Series, applying Ahjan's contemplative-Buddhism teaching to the grief held by caregivers.",
        "bio": (
            "Mira Santos writes for the people holding everyone else together. After losing her mother during the "
            "years she was raising two children alone, she began noticing how grief and self-worth shared the same "
            "nervous-system architecture — the same alarm, the same exhaustion, the same quiet certainty that there "
            "was no time to feel any of it. "
            "She works with sandwich-generation caregivers and working parents who are managing other people's needs "
            "while the unprocessed losses pile up in the body. Her writing draws on Ahjan's contemplative-Buddhism "
            "framework of the alarm within, applied to the specific grief of people who never got to grieve in the "
            "first place — and to the self-worth that erodes inside that same suspension. "
            "Her practice favors the small, specific moments of recognition over any larger story of healing. "
            "She is based in Oakland."
        ),
        "why_this_book": (
            "Mira began writing this after the third year of caring for her dying mother while raising two children, "
            "when she realized she was not actually grieving — she was managing. Days became logistics. Feelings became "
            "tasks for later. When her mother died, the grief did not begin. It just sat under everything she did, the "
            "way it does for so many sandwich-generation caregivers who never get to set down what they are carrying. "
            "What Ahjan calls the alarm within turned out to be the same architecture. The body that cannot grieve and "
            "the body that does not feel worth taking time for are running the same protective program. "
            "This book is not a manual for moving on. It does not promise stages or closure. It offers the recognition "
            "that grief and self-worth, in caregivers, are often two ends of one frozen body — and points at the small, "
            "specific moments where that body can begin to thaw without crisis."
        ),
        "authority": {
            "does_not_claim": [
                "clinical diagnosis of complicated grief, depression, or PTSD",
                "psychotherapy or grief counseling",
                "spiritual or religious authority over death and dying",
                "guaranteed timeline for working through grief",
            ],
            "does_not_promise": [
                "closure or completion of grief",
                "elimination of grief or shame",
                "restoration of relationships with the deceased",
                "fixed outcome for caregiver burnout",
            ],
            "recommends_professional_support_for": [
                "complicated or prolonged grief",
                "active depression or suicidal ideation",
                "trauma history including loss-related trauma",
                "any condition requiring clinical care",
            ],
            "resolution_compatibility": ["grounded_shift", "partial_resolution"],
        },
        "author_background": (
            "Mira lost her mother while raising two children alone, and from that experience built a practice of "
            "supporting sandwich-generation caregivers and working parents whose grief and self-worth share one "
            "nervous-system architecture. Her writing draws on Ahjan's framework of the alarm within. She is based in Oakland."
        ),
        "audio_why_this_book": (
            "Mira began writing this after the years of caring for a dying mother while raising two children, when she "
            "noticed she was not grieving — she was managing. The grief sat under everything. What Ahjan calls the "
            "alarm within turned out to be the same architecture. The body that cannot grieve and the body that will "
            "not take time for itself are running one protective program. She did not study with Ahjan directly; she "
            "encountered his teaching through books. This book offers the recognition that grief and self-worth, in "
            "caregivers, are often two ends of one frozen body."
        ),
    },

    # ─── kai_okafor — research_guide, social_anxiety+overthinking ────────
    "kai_okafor": {
        "pen_name": "Kai Okafor",
        "narrator_name": "Devin Maro",
        "narrator_archetype": "young_american_male",
        "primary_topic": "social_anxiety",
        "series_line": "This audiobook is part of the Stillness Press Series, applying Ahjan's contemplative-Buddhism teaching to the social-monitoring patterns of Gen Z professionals.",
        "bio": (
            "Kai Okafor is a Gen Z mindfulness researcher who writes about overthinking and social anxiety as what they "
            "actually are: an alarm system running a program no one chose to install. He works primarily with Gen Z "
            "professionals and graduate students whose social vigilance has become indistinguishable from their personalities. "
            "His writing skips the incense and goes straight to the neuroscience of why the brain will not stop "
            "rehearsing conversations, drawing on Ahjan's contemplative-Buddhism framework of the alarm within for the "
            "older language that names what newer research can finally measure. "
            "His approach makes a point of being interesting before it asks readers to do anything — the practices come "
            "after the explanation, not before, because Gen Z reads citation chains and notices when someone is "
            "skipping past them. "
            "He is based in Brooklyn."
        ),
        "why_this_book": (
            "Kai began writing this after watching his classmates and clients run the same loop he had spent years "
            "running: replaying every meeting, every text, every brief exchange in the hallway, looking for the moment "
            "they had said the wrong thing. They did not have social anxiety as a diagnosis. They had social anxiety "
            "as a default state — a continuous low-volume alarm scanning every interaction for failure. "
            "What Ahjan calls the alarm within is the same loop, named older. In Ahjan's framework, the brain that will "
            "not stop monitoring is not broken; it is running a useful pattern in a context that no longer needs it. "
            "Most available writing offered productivity hacks or full-volume cognitive behavioral protocols. Neither "
            "spoke to people whose anxiety was a baseline rather than an episode. "
            "This book does not promise to silence the loop. It offers a way to recognize the alarm without arguing "
            "with it, and the small contemplative practices that, over time, change the volume."
        ),
        "authority": {
            "does_not_claim": [
                "clinical diagnosis of social anxiety disorder, OCD, or any DSM condition",
                "psychotherapy or cognitive behavioral therapy",
                "neuropsychological assessment",
                "guaranteed change in social patterns",
            ],
            "does_not_promise": [
                "elimination of overthinking or social vigilance",
                "transformation of personality",
                "career or relational outcomes",
                "fixed timeline for nervous-system change",
            ],
            "recommends_professional_support_for": [
                "clinical social anxiety disorder or OCD",
                "trauma histories involving social harm",
                "depression intersecting with social withdrawal",
                "any condition requiring professional care",
            ],
            "resolution_compatibility": ["grounded_shift", "partial_resolution"],
        },
        "author_background": (
            "Kai is a Gen Z mindfulness researcher who writes about social anxiety and overthinking as alarm-system "
            "patterns rather than personality traits. His approach bridges contemplative-neuroscience research with "
            "Ahjan's framework of the alarm within. He is based in Brooklyn."
        ),
        "audio_why_this_book": (
            "Kai began writing this after watching classmates and clients run the loop he had spent years running: "
            "replaying every meeting and text for the moment they said the wrong thing. They did not have social "
            "anxiety as a diagnosis; they had it as a baseline. What Ahjan calls the alarm within is the same loop, "
            "named older. Kai did not study with Ahjan directly; he encountered the teaching through books and talks. "
            "This book offers a way to recognize the alarm without arguing with it."
        ),
    },

    # ─── ruth_alder — elder_stabilizer, boundaries+compassion_fatigue ────
    "ruth_alder": {
        "pen_name": "Ruth Alder",
        "narrator_name": "Hester Pell",
        "narrator_archetype": "warm_storytelling",
        "primary_topic": "boundaries",
        "series_line": "This audiobook is part of the Stillness Press Series, applying Ahjan's contemplative-Buddhism teaching to the boundary-setting that keeps caregivers alive.",
        "bio": (
            "Ruth Alder was a hospice chaplain for twenty-two years. She writes about the boundaries that keep "
            "caregivers alive — not the walls people build to keep others out, but the ground that lets a person "
            "stay standing when everyone around them is falling. "
            "She works with healthcare professionals and first responders whose careers ask them to absorb other "
            "people's grief without contagion. Her writing draws on Ahjan's contemplative-Buddhism teaching of the "
            "alarm within for what she observed at countless bedsides: the body that cannot say no until the cost has "
            "already been paid. "
            "She refuses the language of self-care for what is, more honestly, the language of survival; her work is "
            "for caregivers who have already heard the cliches and need something quieter that holds. "
            "She is based in Asheville."
        ),
        "why_this_book": (
            "Ruth began writing this after her own near-collapse, the year she stopped being able to hear what her body "
            "was telling her about the work. She had spent two decades as a hospice chaplain. The boundaries she had "
            "set — and the many she had not set — had each been small at the time and devastating in aggregate. "
            "What Ahjan calls the alarm within named the pattern she had watched in herself and in nearly every "
            "long-tenured caregiver she knew. The body says no in a thousand small ways before it says no in the way "
            "that takes years to recover from. The boundary is not a wall built later. It is the recognition of the "
            "alarm at the time it first fires. "
            "Most writing on boundaries treated the topic as a communication problem. Ruth had watched too many caregivers "
            "burn out with perfectly worded boundaries on their lips. "
            "This book does not promise to make caregiving sustainable for everyone. It offers the body-level recognition "
            "of the alarm that, named early, can become the ground that keeps a caregiver standing."
        ),
        "authority": {
            "does_not_claim": [
                "clinical diagnosis of compassion fatigue, secondary trauma, or any DSM condition",
                "psychotherapy or trauma reprocessing",
                "spiritual or religious authority on death and dying",
                "professional supervision for healthcare or social work practice",
            ],
            "does_not_promise": [
                "elimination of compassion fatigue",
                "ability to continue current caregiving roles indefinitely",
                "resolution of organizational or systemic harm",
                "freedom from grief or moral injury",
            ],
            "recommends_professional_support_for": [
                "secondary trauma or vicarious traumatization",
                "moral injury requiring clinical containment",
                "active depression or suicidal ideation",
                "any condition requiring professional care",
            ],
            "resolution_compatibility": ["grounded_shift", "partial_resolution"],
        },
        "author_background": (
            "Ruth was a hospice chaplain for twenty-two years and now writes about the boundaries that keep caregivers "
            "alive. Her approach draws on Ahjan's contemplative-Buddhism framework of the alarm within, applied to the "
            "specific exhaustion of long-tenured helpers. She is based in Asheville."
        ),
        "audio_why_this_book": (
            "Ruth began writing this after her own near-collapse, the year she stopped being able to hear what her body "
            "was telling her about the work. The body says no in a thousand small ways before it says no in the way "
            "that takes years to recover from. What Ahjan calls the alarm within named the pattern she had watched in "
            "herself and in long-tenured caregivers she knew. Ruth did not train under Ahjan; she came to his teaching "
            "through books late in her career. The boundary, in this framework, is not a wall built later. It is the "
            "recognition of the alarm at the time it first fires."
        ),
    },

    # ─── sam_meridian — research_guide, somatic_healing+depression ───────
    "sam_meridian": {
        "pen_name": "Sam Meridian",
        "narrator_name": "Marcus Whaley",
        "narrator_archetype": "warm_male",
        "primary_topic": "somatic_healing",
        "series_line": "This audiobook is part of the Stillness Press Series, bridging contemplative practice and clinical somatic work through Ahjan's alarm-system framework.",
        "bio": (
            "Sam Meridian works at the seam between contemplative practice and clinical somatic psychology. After a "
            "decade of silent retreats and a master's in somatic psychology, Sam writes for people who have learned "
            "that meditation alone is not enough — but who do not know what else to try. "
            "Their work focuses on the bodies of entrepreneurs and millennial women professionals whose nervous systems "
            "carry years of held depression and stalled somatic healing. The framework: Ahjan's contemplative-Buddhism "
            "teaching of the alarm within, applied to the specific stuckness of people who have already tried mindfulness "
            "and need the next layer down. "
            "Sam writes with explanatory clarity rather than first-person confession, leaving room for readers to find "
            "their own bodies in the descriptions. "
            "Sam is based in Portland."
        ),
        "why_this_book": (
            "Sam began writing this after watching their somatic-therapy clients hit a wall that meditation alone could "
            "not move and that talk therapy circled around without entering. The wall had a shape: chronic low-grade "
            "depression, a body that did not lift, a feeling of stuckness that persisted no matter how many breath "
            "practices the client did or how many sessions of EMDR they had completed. "
            "What Ahjan calls the alarm within gave Sam a way to name what was happening — a nervous-system pattern "
            "running below the level of either contemplative awareness or cognitive insight, asking for body-level "
            "recognition rather than further analysis. "
            "Most somatic-healing writing collapsed into either trauma-recovery promises or vague invitations to feel. "
            "Neither matched what Sam saw. "
            "This book does not claim to heal depression or fix the body. It offers a framework for recognizing the "
            "alarm pattern under chronic somatic stuckness, alongside the slow contemplative practices that have, for "
            "centuries, addressed exactly that layer."
        ),
        "authority": {
            "does_not_claim": [
                "clinical diagnosis of depression, trauma, or any DSM condition",
                "psychotherapy, somatic experiencing, or any licensed clinical modality",
                "neuropsychological assessment",
                "guaranteed somatic-healing outcomes",
            ],
            "does_not_promise": [
                "recovery from clinical depression",
                "resolution of trauma history",
                "fixed timeline for somatic change",
                "elimination of stuckness",
            ],
            "recommends_professional_support_for": [
                "clinical depression or suicidal ideation",
                "PTSD or complex trauma",
                "medication-related questions",
                "any condition requiring licensed clinical care",
            ],
            "resolution_compatibility": ["grounded_shift", "partial_resolution"],
        },
        "author_background": (
            "Sam Meridian works at the seam between contemplative practice and clinical somatic psychology, writing for "
            "people who have learned that meditation alone is not enough. Their approach draws on Ahjan's framework of "
            "the alarm within, applied to chronic somatic stuckness. Sam is based in Portland."
        ),
        "audio_why_this_book": (
            "Sam began writing this after watching somatic-therapy clients hit a wall that meditation alone could not "
            "move. The wall had a shape: chronic low-grade depression, a body that did not lift. What Ahjan calls the "
            "alarm within gave Sam a way to name what was happening — a nervous-system pattern asking for body-level "
            "recognition rather than further analysis. Sam did not train under Ahjan in person; they encountered his "
            "teaching through books and recorded talks. This book offers a framework for recognizing the alarm pattern "
            "under chronic somatic stuckness."
        ),
    },

    # ─── noor_ibrahim — somatic_companion, courage+financial_anxiety ─────
    "noor_ibrahim": {
        "pen_name": "Noor Ibrahim",
        "narrator_name": "Pia Calder",
        "narrator_archetype": "gentle_female",
        "primary_topic": "courage",
        "series_line": "This audiobook is part of the Stillness Press Series, applying Ahjan's contemplative-Buddhism teaching to the alarm that fires around money and risk.",
        "bio": (
            "Noor Ibrahim writes about the alarm that fires around money and risk — the one that sounds like \"not "
            "enough\" even when the numbers say otherwise, and the one that rises when a decision asks more courage than "
            "the body believes it has. "
            "Drawing on contemplative economics and nervous-system science, she works with entrepreneurs and "
            "sandwich-generation adults whose financial anxiety is rarely about finance and whose courage is rarely "
            "about willpower. Her framework: Ahjan's contemplative-Buddhism teaching of the alarm within, applied to "
            "the specific physiology of risk under financial pressure. "
            "Her practice does not promise relief. It promises company — and a way to listen to the alarm without "
            "letting it write the next decision. "
            "She is based in Toronto."
        ),
        "why_this_book": (
            "Noor began writing this after the third entrepreneur of the year sat across from her crying about a balance "
            "sheet that was, in fact, fine. The numbers were not the problem. The body was running an alarm that the "
            "spreadsheet could not soothe. "
            "What Ahjan calls the alarm within gave Noor a way to talk about courage without making it a willpower "
            "story and a way to talk about financial anxiety without making it a math problem. Both are nervous-system "
            "patterns, and both ask for body-level recognition before any plan can hold. "
            "Most writing on courage promised transformation. Most writing on money promised mastery. Neither helped "
            "the people Noor was sitting with, who needed permission to feel the alarm rather than override it. "
            "This book does not promise courage on demand or relief from financial fear. It offers the recognition "
            "that the alarm is doing its job — and the contemplative practices that, over time, change the body's "
            "relationship to a future it cannot control."
        ),
        "authority": {
            "does_not_claim": [
                "financial planning, investment, or fiduciary advice",
                "clinical diagnosis of anxiety or any DSM condition",
                "psychotherapy or somatic clinical treatment",
                "guaranteed business or financial outcomes",
            ],
            "does_not_promise": [
                "specific financial results",
                "elimination of financial anxiety",
                "courage on demand",
                "fixed timeline for nervous-system change",
            ],
            "recommends_professional_support_for": [
                "specific financial decisions (consult a fiduciary planner)",
                "clinical anxiety disorders",
                "trauma related to financial harm",
                "any condition requiring professional care",
            ],
            "resolution_compatibility": ["grounded_shift", "partial_resolution"],
        },
        "author_background": (
            "Noor writes about the alarm that fires around money and risk, drawing on contemplative economics and "
            "Ahjan's contemplative-Buddhism framework of the alarm within. She works primarily with entrepreneurs and "
            "sandwich-generation adults navigating decisions under financial pressure. She is based in Toronto."
        ),
        "audio_why_this_book": (
            "Noor began writing this after the third entrepreneur of the year sat across from her crying about a "
            "balance sheet that was, in fact, fine. The body was running an alarm the spreadsheet could not soothe. "
            "What Ahjan calls the alarm within gave Noor a way to talk about courage without making it a willpower story. "
            "Noor did not study with Ahjan directly; she came to his teaching through books and recordings. This book "
            "offers the recognition that the alarm is doing its job, and the practices that change the body's "
            "relationship to a future it cannot control."
        ),
    },

    # ─── tara_woodfield — elder_stabilizer, boundaries+burnout ───────────
    "tara_woodfield": {
        "pen_name": "Tara Woodfield",
        "narrator_name": "Hester Pell",
        "narrator_archetype": "warm_storytelling",
        "primary_topic": "boundaries",
        "series_line": "This audiobook is part of the Stillness Press Series, applying Ahjan's contemplative-Buddhism teaching to the renunciation a parent can practice without leaving.",
        "bio": (
            "Tara Woodfield lived at a forest monastery for six years before returning to raise her daughter. She writes "
            "about renunciation as a parent — what a person can put down even when they cannot leave. "
            "Her work focuses on sandwich-generation caregivers and working parents who are not in a position to walk "
            "away from anything but who are running out of capacity to keep carrying everything. Her writing draws "
            "directly on Ahjan's contemplative-Buddhism teaching of the alarm within and the forest tradition's older "
            "language of letting go, applied to the practical question of how a parent puts down what cannot be "
            "delegated. "
            "Her tone is unhurried and respectful of the reader's exhaustion; she trusts that a parent who is reading "
            "this is reading it because they are already trying. "
            "She is based in Vermont."
        ),
        "why_this_book": (
            "Tara began writing this after the year she came back from the monastery to raise her daughter alone, when "
            "she discovered that everything she had learned about renunciation needed to be re-translated into a context "
            "where she could not leave. Six years in a forest hall had taught her how to put things down. One year as a "
            "single parent taught her that renunciation, in a life she could not exit, looked completely different. "
            "What Ahjan calls the alarm within is the architecture under most of what people experience as burnout and "
            "as the inability to hold a boundary. The body running a continuous alarm cannot put anything down. The "
            "forest-tradition practice of letting go starts with recognizing the alarm — not arguing with it. "
            "Most writing on burnout treated boundaries as a communication strategy. Most writing on parenting treated "
            "renunciation as guilt-inducing. Tara found that neither matched the people she now teaches. "
            "This book does not promise a sustainable path through caregiving. It offers a parent's translation of an "
            "older practice — what can be put down, in this life, on this Tuesday."
        ),
        "authority": {
            "does_not_claim": [
                "clinical diagnosis of burnout, depression, or any DSM condition",
                "psychotherapy or licensed clinical care",
                "spiritual or religious authority over family decisions",
                "professional parenting or family therapy advice",
            ],
            "does_not_promise": [
                "freedom from caregiving responsibilities",
                "elimination of burnout in unsustainable contexts",
                "fixed-timeline change",
                "restoration of capacity in untreated clinical depression",
            ],
            "recommends_professional_support_for": [
                "clinical burnout or major depression",
                "trauma history requiring containment",
                "family-system issues requiring therapy",
                "any condition requiring professional care",
            ],
            "resolution_compatibility": ["grounded_shift", "partial_resolution"],
        },
        "author_background": (
            "Tara lived at a forest monastery for six years before returning to raise her daughter alone, and now writes "
            "about renunciation as a practice for parents who cannot leave. Her work draws on Ahjan's framework of the "
            "alarm within and the older forest-tradition language of letting go. She is based in Vermont."
        ),
        "audio_why_this_book": (
            "Tara began writing this after the year she came back from the monastery to raise her daughter alone, when "
            "she discovered everything she had learned about renunciation needed translating into a life she could not "
            "exit. What Ahjan calls the alarm within is the architecture under most of what people experience as burnout. "
            "The body running a continuous alarm cannot put anything down. Tara did not study with Ahjan directly; she "
            "came to his teaching through forest-tradition books late in her practice. This book offers a parent's "
            "translation of letting go."
        ),
    },

    # ─── rowan_beck — research_guide, anxiety+overthinking ───────────────
    "rowan_beck": {
        "pen_name": "Rowan Beck",
        "narrator_name": "Aubrey Tate",
        "narrator_archetype": "british_authority",
        "primary_topic": "anxiety",
        "series_line": "This audiobook is part of the Stillness Press Series, applying Ahjan's contemplative-Buddhism teaching to the simplicity practices that quiet an overstimulated nervous system.",
        "bio": (
            "Rowan Beck is an environmental psychologist who studies why people feel calmer in forests. His research "
            "looks at the specific environmental conditions — low information density, predictable visual rhythms, "
            "ambient sound — that allow an overstimulated nervous system to lower its alarm. "
            "He works with tech-finance professionals and millennial women whose anxiety and overthinking are sustained, "
            "in part, by environments designed to spike them. His writing translates forest-tradition principles into "
            "evidence-based simplicity practices, framed by Ahjan's contemplative-Buddhism teaching of the alarm within. "
            "His approach is grounded in the data and held by the older tradition: each chapter pairs one finding from "
            "the literature with one practice that has outlasted the literature. He is careful with claims and slow "
            "with prescriptions; the work assumes a reader who has been disappointed before. "
            "He is based in Vancouver."
        ),
        "why_this_book": (
            "Rowan began writing this after years of research showing the same boring finding: nervous systems calm "
            "down in environments that ask less of them. The trouble was that most readers did not have a forest to "
            "walk into. They had Slack, group chats, three monitors, and the thirty-second window between meetings. "
            "What Ahjan calls the alarm within is the body's response to environments that exceed its capacity — and "
            "the forest tradition's centuries-old answer is, essentially, the same intervention Rowan's research keeps "
            "validating: lower the inputs, slow the cadence, repeat. The contemplative framework gave Rowan a way to "
            "talk about the science without flattening it into productivity advice. "
            "Most writing on anxiety either pathologized the condition or asked readers to think differently about "
            "their thoughts. Rowan's research suggested neither was the leverage point. "
            "This book does not promise calm by Friday. It offers the science of why the alarm rises in modern "
            "professional environments, alongside the small forest-tradition practices that, over time, can lower it."
        ),
        "authority": {
            "does_not_claim": [
                "clinical diagnosis of anxiety or any DSM condition",
                "psychotherapy or clinical treatment",
                "neuropsychological assessment",
                "guaranteed environmental change at workplaces",
            ],
            "does_not_promise": [
                "elimination of anxiety in unchanged environments",
                "transformation of overstimulating workplaces",
                "fixed timeline for nervous-system change",
                "career or productivity outcomes",
            ],
            "recommends_professional_support_for": [
                "clinical anxiety or panic disorder",
                "trauma histories",
                "medication-related questions",
                "any condition requiring professional care",
            ],
            "resolution_compatibility": ["grounded_shift", "partial_resolution"],
        },
        "author_background": (
            "Rowan is an environmental psychologist who studies why people feel calmer in forests. His writing "
            "translates forest-tradition principles into evidence-based simplicity practices, framed by Ahjan's "
            "framework of the alarm within. He is based in Vancouver."
        ),
        "audio_why_this_book": (
            "Rowan began writing this after years of research showing the same finding: nervous systems calm down in "
            "environments that ask less of them. The trouble was that most readers did not have a forest to walk into. "
            "What Ahjan calls the alarm within is the body's response to environments that exceed its capacity, and "
            "the forest tradition's older answer matches what Rowan's research keeps validating. He did not study under "
            "Ahjan in person; he encountered his teaching through books. This book offers the science of why the alarm "
            "rises in modern professional environments."
        ),
    },

    # ─── mae_rivers — somatic_companion, grief+compassion_fatigue ────────
    "mae_rivers": {
        "pen_name": "Mae Rivers",
        "narrator_name": "Pia Calder",
        "narrator_archetype": "gentle_female",
        "primary_topic": "grief",
        "series_line": "This audiobook is part of the Stillness Press Series, applying Ahjan's contemplative-Buddhism teaching to the carried grief of helping professionals.",
        "bio": (
            "Mae Rivers is a former wildfire chaplain who came to the forest tradition after losing colleagues in the "
            "field. She writes for people who carry other people's grief and have forgotten how to put it down — first "
            "responders, healthcare professionals, and anyone whose work is to remain calm in proximity to loss. "
            "Her writing draws on Ahjan's contemplative-Buddhism framework of the alarm within, applied to the specific "
            "physiology of compassion fatigue: a nervous system stuck in proximity to other people's emergencies, with "
            "no way to register its own. "
            "She speaks plainly and slowly — both because the work she writes about earned that pace, and because the "
            "people she writes for cannot yet hear anything faster. "
            "She is based in Bozeman."
        ),
        "why_this_book": (
            "Mae began writing this in the second year after the fire season that took two colleagues — when she realized "
            "she was no longer the person her family thought she was, and that the change was not grief in any shape she "
            "had been taught to recognize. It was simpler and more dangerous: a nervous system that had stopped being "
            "able to feel grief at all, because the alarm had been on for too long. "
            "What Ahjan calls the alarm within named what had happened. Compassion fatigue is not a moral failure or a "
            "lapse of caring. It is the body protecting itself from a level of repeated proximity to loss it was never "
            "built to absorb. The grief does not disappear. It moves underground. "
            "Most writing on compassion fatigue offered self-care strategies that read, to the people Mae knew, as "
            "insults. "
            "This book does not promise that helpers can keep helping forever. It offers the body-first recognition that "
            "the alarm is real and that the underground grief is reachable, slowly, through practice."
        ),
        "authority": {
            "does_not_claim": [
                "clinical diagnosis of complicated grief, secondary trauma, or PTSD",
                "psychotherapy or grief counseling",
                "professional first-responder peer support",
                "spiritual or religious authority on death and dying",
            ],
            "does_not_promise": [
                "ability to continue current work indefinitely",
                "resolution of accumulated loss",
                "elimination of compassion fatigue",
                "fixed-timeline recovery",
            ],
            "recommends_professional_support_for": [
                "secondary trauma or vicarious traumatization",
                "complicated or prolonged grief",
                "active depression or suicidal ideation",
                "any condition requiring professional care",
            ],
            "resolution_compatibility": ["grounded_shift", "partial_resolution"],
        },
        "author_background": (
            "Mae was a wildfire chaplain who came to the forest tradition after losing colleagues. She now writes for "
            "people who carry other people's grief and forget how to put it down. Her writing draws on Ahjan's "
            "framework of the alarm within. She is based in Bozeman."
        ),
        "audio_why_this_book": (
            "Mae began writing this in the second year after the fire season that took two colleagues, when she realized "
            "she was no longer the person her family thought she was. The change was simpler and more dangerous than "
            "grief: a nervous system that had stopped being able to feel grief at all. What Ahjan calls the alarm "
            "within named what had happened. Mae did not study with Ahjan directly; she came to his teaching through "
            "books her wildfire team's chaplain shared. This book offers a body-first recognition of the underground "
            "grief that helping professionals carry."
        ),
    },

    # ─── silas_grant — elder_stabilizer, self_worth+depression ───────────
    "silas_grant": {
        "pen_name": "Silas Grant",
        "narrator_name": "Marcus Whaley",
        "narrator_archetype": "deep_calm_male",
        "primary_topic": "self_worth",
        "series_line": "This audiobook is part of the Stillness Press Series, applying Ahjan's contemplative-Buddhism teaching to what remains when a person stops trying to be more.",
        "bio": (
            "Silas Grant is a retired teacher who spent two decades walking before dawn. He writes short books — sixty "
            "pages, sometimes seventy — about what remains when a person stops trying to be more. "
            "His readers are entrepreneurs and sandwich-generation adults who have spent years building a self that "
            "kept disappointing them and who are tired enough now to consider another approach. His writing draws on "
            "Ahjan's contemplative-Buddhism teaching of the alarm within for what he has watched in himself and his "
            "students: a nervous system that has been told for so long it is not enough that the alarm has become its "
            "default state. "
            "Silas writes the book he wished someone had handed him at forty-two — short, calm, and honest about the "
            "limits of any framework, including his own. "
            "He is based in coastal Maine."
        ),
        "why_this_book": (
            "Silas began writing this after his wife asked him, on what he later realized was a perfectly ordinary "
            "Tuesday, what he was actually trying to become. He had been teaching middle-school English for thirty-one "
            "years. He had been trying for thirty-four. "
            "What Ahjan calls the alarm within named what Silas had been spending most of his adult life inside — a "
            "low continuous suggestion that the present arrangement of himself was inadequate and that the next thing "
            "would resolve it. The next thing did not resolve it. The next thing rarely does. "
            "Most writing on self-worth offered affirmations or therapy frameworks. Silas had tried both. Neither "
            "addressed the underlying alarm. "
            "This book does not promise that a reader will feel better about themselves. It offers, instead, the slow "
            "contemplative recognition that the alarm is not a verdict — it is a pattern. And patterns, given quiet "
            "enough attention, can change."
        ),
        "authority": {
            "does_not_claim": [
                "clinical diagnosis of depression or any DSM condition",
                "psychotherapy or clinical treatment",
                "spiritual or religious authority",
                "professional educational or counseling advice",
            ],
            "does_not_promise": [
                "increased self-worth",
                "recovery from clinical depression",
                "fixed-timeline change",
                "resolution of life dissatisfaction",
            ],
            "recommends_professional_support_for": [
                "clinical depression or suicidal ideation",
                "trauma history requiring therapeutic care",
                "medication-related questions",
                "any condition requiring professional care",
            ],
            "resolution_compatibility": ["grounded_shift", "partial_resolution"],
        },
        "author_background": (
            "Silas is a retired teacher who spent two decades walking before dawn and now writes short books about "
            "what remains when a person stops trying to be more. His work draws on Ahjan's framework of the alarm "
            "within. He is based in coastal Maine."
        ),
        "audio_why_this_book": (
            "Silas began writing this after his wife asked him, on a perfectly ordinary Tuesday, what he was actually "
            "trying to become. He had been teaching for thirty-one years. He had been trying for thirty-four. What "
            "Ahjan calls the alarm within named what Silas had spent most of his adult life inside. Silas did not "
            "study with Ahjan; he encountered his teaching through books in his sixties. This book offers the "
            "recognition that the alarm is not a verdict — it is a pattern."
        ),
    },

    # ─── iris_tam — somatic_companion, somatic_healing+sleep_anxiety ─────
    "iris_tam": {
        "pen_name": "Iris Tam",
        "narrator_name": "Anneliese Voss",
        "narrator_archetype": "warm_intimate_female",
        "primary_topic": "somatic_healing",
        "series_line": "This audiobook is part of the Stillness Press Series, applying Ahjan's contemplative-Buddhism teaching to body-based simplicity for an overworked nervous system.",
        "bio": (
            "Iris Tam teaches body-based simplicity — contemplative approaches to sleep, eating, and movement for "
            "people who want less but do not know where to start letting go. "
            "She works with millennial women professionals and working parents whose nervous systems are managing "
            "more than the body was designed to track and whose sleep, in particular, has become a nightly negotiation "
            "with an alarm that does not turn off when the lights do. Her writing draws on Ahjan's contemplative-"
            "Buddhism framework of the alarm within, applied to the small daily practices that, repeated, change the "
            "body's relationship to rest. "
            "Her practice is built for people who cannot add another routine — what she offers is shorter, smaller, "
            "and intended to fit between the obligations the reader already cannot drop. "
            "She is based in Seattle."
        ),
        "why_this_book": (
            "Iris began writing this in the years she could not sleep. She had two small children, a partner who "
            "traveled, a job that ran long, and a body that — by 11 p.m. — could not put down what 11 p.m. was bringing "
            "her. The mornings arrived without rest. The days felt thinner each year. "
            "What Ahjan calls the alarm within named what Iris had been calling, privately, an inability to let go. The "
            "body that cannot sleep is not failing at sleep. It is running an alarm that asks to be recognized rather "
            "than overridden. The contemplative-tradition language gave Iris a way to talk about this without medicalizing "
            "it and without prescribing a routine that would not survive a teething child. "
            "Most writing on sleep prescribed habits. Iris's clients had habits. They had sleep apps. They needed "
            "something else. "
            "This book does not promise eight hours. It offers small body-level practices for noticing the alarm before "
            "it becomes the night, drawn from a tradition that has watched human nervous systems for centuries."
        ),
        "authority": {
            "does_not_claim": [
                "clinical diagnosis of insomnia or any DSM condition",
                "sleep-disorder medicine, psychotherapy, or clinical somatic treatment",
                "neurological assessment",
                "guaranteed sleep outcomes",
            ],
            "does_not_promise": [
                "specific hours of sleep",
                "recovery from clinical insomnia",
                "elimination of nighttime anxiety",
                "fixed timeline for nervous-system change",
            ],
            "recommends_professional_support_for": [
                "clinical insomnia or sleep apnea",
                "anxiety or trauma requiring clinical care",
                "medication-related questions",
                "any condition requiring professional care",
            ],
            "resolution_compatibility": ["grounded_shift", "partial_resolution"],
        },
        "author_background": (
            "Iris teaches body-based simplicity for people who want less but do not know where to start letting go. "
            "Her writing draws on Ahjan's framework of the alarm within, applied to sleep, eating, and movement. She "
            "is based in Seattle."
        ),
        "audio_why_this_book": (
            "Iris began writing this in the years she could not sleep. The body that cannot sleep is not failing at "
            "sleep — it is running an alarm that asks to be recognized rather than overridden. What Ahjan calls the "
            "alarm within gave Iris a way to talk about this without medicalizing it. Iris did not study with Ahjan "
            "in person; she came to his teaching through audio recordings on long winter nights. This book offers "
            "small body-level practices for noticing the alarm before it becomes the night."
        ),
    },
}


# ─── YAML emission ────────────────────────────────────────────────────────────

def yaml_block(text: str) -> str:
    """Format a multi-line string as a YAML block scalar (>) with proper indentation."""
    lines = text.split(". ")
    out = ">\n"
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        if i < len(lines) - 1 and not line.endswith("."):
            line += "."
        out += "  " + line + "\n"
    return out.rstrip() + "\n"


def emit_bio(author_id: str, a: dict) -> str:
    return (
        f"author_id: {author_id}\n"
        f"pen_name: \"{a['pen_name']}\"\n"
        f"bio: {yaml_block(a['bio'])}"
        f"word_count_target: 120-180\n"
        f"status: draft\n"
    )


def emit_why(author_id: str, a: dict) -> str:
    return (
        f"author_id: {author_id}\n"
        f"topic_id: {a['primary_topic']}\n"
        f"why_this_book: {yaml_block(a['why_this_book'])}"
        f"word_count_target: 150-250\n"
        f"status: draft\n"
    )


def emit_authority(author_id: str, a: dict) -> str:
    auth = a["authority"]
    out = f"author_id: {author_id}\nauthority_position:\n"
    out += "  does_not_claim:\n"
    for item in auth["does_not_claim"]:
        out += f"    - {item}\n"
    out += "  does_not_promise:\n"
    for item in auth["does_not_promise"]:
        out += f"    - {item}\n"
    out += "  recommends_professional_support_for:\n"
    for item in auth["recommends_professional_support_for"]:
        out += f"    - {item}\n"
    out += "  resolution_compatibility:\n"
    for item in auth["resolution_compatibility"]:
        out += f"    - {item}\n"
    out += "status: draft\n"
    return out


def emit_audio(author_id: str, a: dict) -> str:
    pen = a["pen_name"]
    return (
        f"author_id: {author_id}\n"
        f"narrator_intro: >\n"
        f"  My name is {a['narrator_name']}, and I will be guiding you through this audiobook.\n"
        f"book_title_line: >\n"
        f"  This is the dynamic title line; supplied by the naming engine at compile time. "
        f"If a runtime title is not supplied, the build fails.\n"
        f"series_line: {yaml_block(a['series_line'])}"
        f"author_intro: >\n"
        f"  This book was written by {pen}.\n"
        f"author_background: {yaml_block(a['author_background'])}"
        f"why_this_book: {yaml_block(a['audio_why_this_book'])}"
        f"transition_line: >\n"
        f"  Chapter One.\n"
        f"status: draft\n"
    )


def emit_all(force: bool) -> tuple[int, list[str]]:
    written = 0
    errors: list[str] = []
    for aid, a in AUTHORS.items():
        adir = ASSETS_ROOT / aid
        adir.mkdir(parents=True, exist_ok=True)

        files = {
            "bio.yaml":                 emit_bio(aid, a),
            "why_this_book.yaml":       emit_why(aid, a),
            "authority_position.yaml":  emit_authority(aid, a),
            "audiobook_pre_intro.yaml": emit_audio(aid, a),
        }
        for fname, content in files.items():
            fpath = adir / fname
            if fpath.exists() and not force:
                errors.append(f"exists: {fpath.relative_to(REPO_ROOT)} (pass --force to overwrite)")
                continue
            fpath.write_text(content, encoding="utf-8")
            written += 1
    return written, errors


def verify() -> None:
    """Print word counts for every author's 4 assets."""
    bands = {
        "bio":               (120, 180),
        "why_this_book":     (150, 250),
        "authority_text":    (50, 200),   # structured; rough word range
        "audiobook_pre":     (200, 900),  # workbook says 500-900 but examples show ~200
    }
    print(f"{'author':18s} {'bio':>5s} {'why':>5s} {'auth':>5s} {'audio':>6s}")
    print("-" * 50)
    for aid, a in AUTHORS.items():
        bio_wc = wc(a["bio"])
        why_wc = wc(a["why_this_book"])
        auth_wc = sum(wc(s) for cat in a["authority"].values() for s in (cat if isinstance(cat, list) else [cat]))
        audio_wc = (
            len("My name is X, and I will be guiding you through this audiobook.".split()) +
            wc(a["series_line"]) +
            len(f"This book was written by {a['pen_name']}.".split()) +
            wc(a["author_background"]) +
            wc(a["audio_why_this_book"]) +
            len("Chapter One.".split())
        )
        print(f"{aid:18s} {bio_wc:>5d} {why_wc:>5d} {auth_wc:>5d} {audio_wc:>6d}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Seed brand-1 author asset bundles")
    ap.add_argument("--force", action="store_true", help="Overwrite existing files")
    ap.add_argument("--verify", action="store_true", help="Print word counts only, no write")
    args = ap.parse_args()

    if args.verify:
        verify()
        return 0

    written, errors = emit_all(args.force)
    print(f"Wrote {written} files to {ASSETS_ROOT.relative_to(REPO_ROOT)}/")
    for e in errors:
        print(f"  skip: {e}", file=sys.stderr)
    print()
    verify()
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
