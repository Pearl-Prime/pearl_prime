# Social Visual Publishable Quality Spec

Date: 2026-07-18

Status: design-quality specification for deterministic social media post visuals. This is not live publishing authorization.

## Problem

Phoenix already proved a bounded deterministic social system: platform sizing, dry-run payloads, static renders, carousels, storyboards, and draft publishing safety.

That does not prove the posts look good.

The current gap is aesthetic and editorial: preview cards can be technically valid while still looking ugly, generic, repeated, or low-value. A social post must stop the scroll, feel native to the platform, make the viewer understand the message quickly, and look worthy of the brand.

## What The Research Says

The local research points to these visual principles:

- hook early and deliver value fast;
- visual salience and first-frame readability matter within the first half-second;
- visual quality, subtitles, and local-language overlays improve engagement;
- carousels need clear narrative rhythm, not random slide decks;
- captions and on-screen text must be short, readable, high-contrast, and mobile-safe;
- short-form videos need a 0-3 second pattern interrupt, 3-8 second problem recognition, 8-20 second value, 20-25 second proof, and final CTA;
- visual/text content must localize by market, not merely resize or translate;
- quality beats frequency;
- overly generic stock, vague carousel covers, and dense text walls fail.

## Publishable Quality Standard

A social creative is publishable-quality only if it passes all of these:

1. Scroll stop: first frame or first slide is instantly legible and specific.
2. Platform-native fit: the post looks built for the surface, not resized from another platform.
3. Visual hierarchy: one primary idea, one focal point, clean reading path.
4. Image awareness: text avoids faces, key objects, clutter, and metaphor focal points.
5. Negative space: title/caption placement uses available quiet zones, not arbitrary top/bottom slots.
6. Typography: premium font pairing, strong size contrast, line breaks that look designed.
7. Contrast: text remains readable on phone-size preview with plates/shadows when needed.
8. Topic metaphor: image and design support the topic, not decorative filler.
9. Variety: no repeated-background spam or one-card template monotony.
10. Cohesion: visual, copy, topic, CTA, and platform objective feel like one idea.
11. Localization: local-market visuals and text overlays respect local norms.
12. Proof safety: no unverified claims, unsafe faces/logos, or unlicensed production media.

## Design Families

Use a rotating grammar family, not one template:

- `photo_full_bleed_emotional`: strong image, title in true negative space, subtle plate only when needed.
- `premium_type_poster`: type-led design with rich hierarchy, not a plain note card.
- `tool_checklist_card`: clean utility layout for saveable tools.
- `diagram_framework`: simple visual model, flow, or contrast diagram.
- `story_carousel`: visual narrative with pacing from tension to insight.
- `book_page_quote`: book/page visual or excerpt card with quote bridge.
- `faceless_video_broll`: vertical storyboard or MP4 with captions and gentle motion.
- `object_metaphor`: one object carries the whole idea with progressive crops. The on-image
  "Visual metaphor:" label MUST co-lock with the selected bank asset family (e.g. maze/exit
  for overthinking, marked path for hope, tangled cord for anxiety). Mismatched labels are a
  hard look-gate fail.
- `localized_lifestyle_note`: market-native design style for JP/TW/KR/CN/HK/SG.

## Anti-Patterns

Reject:

- bland centered note cards;
- tiny subtitles;
- text over the most important part of the image;
- repeated same background across many posts;
- one color palette everywhere;
- generic wellness stock that says nothing;
- slides with no narrative rhythm;
- carousels that are just resized book pages;
- videos with slow logo intros;
- AI-looking sameness or default template energy;
- inaccessible contrast or unreadable mobile text;
- social posts that need external context to make sense.

## Required Proofs

Every visual rebuild must produce:

- contact sheet;
- individual renders;
- platform-size receipts;
- source image/provenance rows;
- crop and negative-space notes;
- typography and contrast report;
- operator-look scorecard;
- trace from source atom/copy to visual design decision;
- explicit `production_ready=false` unless operator/license gates are complete.

