# Stock and Generated Image Bank Cover/Social Plan - 2026-07-15

Audience: Pearl_Research + Pearl_Architect for Phoenix Omega.

Scope: analyze existing Waystream self-help image banks for KDP/book covers, audiobook/storefront thumbnails, and social/content assets. This is a plan only. No R2 upload, renderer edit, image generation, asset move, or production approval is claimed.

## Executive recommendation

Use the banks as a curated source layer, not as a renderer dependency.

The best path is to create a small `curated_image_winners` registry that sits between raw banks and downstream pipelines. Cover and social renderers should consume only registry rows that have passed human visual curation, source-page license verification, crop checks, safety checks, and an operator look gate. The raw folders stay where they are.

Recommended primary roles:

| Use case | Best primary source | Why |
| --- | --- | --- |
| KDP/book covers | Curated stock photos from `mental_health_editorial_100x`, plus generated/abstract reruns for weak topics | Stock is strongest for symbolic cover metaphors when legally clean. Generated/hybrid fills trauma, self_worth, burnout, and other face/legal-risk gaps. |
| Audiobook/podcast/store thumbnails | Cover-derived square adaptations after cover approval | Square storefront art should inherit the approved cover identity, then adapt via `platform_cover_profiles.yaml`; it should not select independent raw images. |
| Organic social posts | Hybrid: generated/derived topic-persona bank for planning, curated stock or seed-generated art for final posts | Social needs persona specificity, many crops, and text-safe backgrounds. The 1000 bank is excellent for planning coverage, not automatic publishing. |
| Quote cards/carousels | Hybrid: curated background image plus deterministic PIL/Canva text overlay | Text must remain deterministic and mobile-legible. No text should be baked into image prompts. |
| Ads/launch assets | Legally clean stock or generated images with no recognizable people/logos, then platform-specific derivatives | Ads have the strictest endorsement, face, trademark, and sensitive-topic risk. Prefer Pexels/Pixabay/Unsplash or clean generated art over Openverse CC-BY unless attribution is explicitly handled. |
| Moodboards/prompting | `topic_persona_image_bank_1000_20260715` | It gives complete topic/persona coverage and future-generation prompts, but many assets inherit Openverse or manga/reference provenance. |

Readiness summary:

- `mental_health_editorial`: best qualitative QA and strongest/reject notes; ideation and shortlist seed, not production-approved.
- `mental_health_editorial_100x`: closest production-source pool because it is broad, PIL-validated, and contains many Pexels records; still not production-approved until source-page license, face/logo, and safety review.
- `topic_persona_image_bank_20260714`: sparse but high-signal generated seed set; useful for social/ad creative direction and possible final use after AI/source policy review.
- `topic_persona_image_bank_1000_20260715`: best complete topic/persona coverage; primary use is internal creative source, persona planning, moodboards, prompt generation, and social placeholder testing.

Production-ready count today: `0`. No image in any bank should be called production-approved until source-page license verification and human curation are completed.

## Current bank inventory and counts

| Bank | Counts | Coverage | Strength | Current approval class |
| --- | ---: | --- | --- | --- |
| `artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial/` | 83 downloaded asset records; 113 files; 12 warnings | 12 core topics, 6-8 assets/topic; Openverse 43 + Openverse More 40 | Best human QA notes, strongest/reject lists, weak-topic queries | `IDEATION_ONLY`, with some shortlist candidates |
| `artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x/` | 1,822 asset records; 1,753 downloaded records; 1,752 unique local downloads; 1,781 files; 69 warnings | 12 topics, all >=100 records; Pexels 1,179 + Openverse 643 | Best broad stock pool; contact sheets have enough choices to curate | `SOCIAL_READY` source pool after curation; `COVER_READY` candidate pool after license gate |
| `artifacts/generated/topic_persona_image_bank_20260714/` | 16 PNG images; 20 files | Sparse, prompt-authored seed set across personas and topics | Best original persona-aware scenes; no text/logos requested | `SOCIAL_READY` candidate set after AI/source review; not broad enough for system coverage |
| `artifacts/generated/topic_persona_image_bank_1000_20260715/` | 1,000 JPEG assets; 1,012 files; 6 coverage CSVs; 6 quality flags | 57 topics x 13 personas = 741/741 cells, plus 259 variants | Best matrix coverage and prompt source | `IDEATION_ONLY` by default; selected rows can graduate after provenance review |

`mental_health_editorial_100x` topic records:

| Topic | Records | Local download records | Notes |
| --- | ---: | ---: | --- |
| anxiety | 142 | 132 | Strong wire, cliff/edge, storm, and motion assets. Needs face/cliff safety review. |
| depression | 140 | 139 | Many empty chair/room/window assets. Cover curation should prefer room/light metaphors over people. |
| grief | 200 | 196 | Strong candles, beds, empty rooms, leaves. Good cover pool. |
| overthinking | 103 | 103 | Thinest pool after trauma, but visually strong: maze, clocks, staircases, papers. |
| burnout | 123 | 122 | Better than small bank, but still needs real editorial rerun for non-clipart premium covers. |
| self_worth | 156 | 131 | Mixed quality; some body/face/cultural specificity risk. Needs careful rerun. |
| anger | 200 | 198 | Strong cracked glass/earth, storm, ember metaphors. Avoid rage-face imagery. |
| loneliness | 162 | 161 | Strong window, bench, swing, silhouette assets. |
| healing | 185 | 175 | Good forest/path/sprout/dawn assets; weak kintsugi/repaired-object lane. |
| boundaries | 140 | 137 | Strong doors, gates, fences, lines. Watch body/swimsuit false positives. |
| trauma | 103 | 100 | Exactly at target after downloads and visually riskiest. Needs rerun/abstract generation. |
| hope | 168 | 159 | Good seedling/sunrise/path assets. Grade muted for heavy-topic adjacency. |

`topic_persona_image_bank_1000_20260715` source mix:

| Source kind | Count | Use |
| --- | ---: | --- |
| `openverse_stock_download` | 625 | Moodboard and possible final source only after original source-page verification. |
| `generated_seed_20260714` | 270 | Strong social/ad direction; can become final candidates if generation provenance and style QA pass. |
| `manga_warrior_calm_bank` | 80 | Internal prompt/style reference only unless this specific manga style is approved for a campaign. |
| `manga_reference_sheet` | 25 | Ideation only for this self-help cover/social lane due style and provenance mismatch. |

`topic_persona_image_bank_1000_20260715` aspect mix:

| Aspect | Count | Best use |
| --- | ---: | --- |
| 16:9 | 356 | YouTube thumbnails, blog headers, wide social/video backgrounds |
| 1:1 | 283 | Square social, profile/store tiles, ad variants |
| 4:5 | 188 | Instagram/LinkedIn feed cards and carousels |
| 9:16 | 173 | Reels, TikTok, YouTube Shorts, vertical storyboards |

## Stock-photo bank role

`mental_health_editorial` is the qualitative teacher bank. Its QA report is valuable because it names strongest assets, rejects, watchlist risks, and rerun queries. Use it to train the curation rubric and to seed first shortlists. It is not the final production bank because it is Openverse-only fallback material and each asset still needs original source-page verification.

`mental_health_editorial_100x` is the production-source candidate bank. It has enough breadth to support real curation, especially because many records are from Pexels and many images are high-resolution portrait stock. It still needs:

- human visual shortlisting;
- source-page license verification for every chosen asset;
- face/person, logo, readable-text, trademark, and property scan;
- sensitive-topic safety review;
- platform crop tests;
- operator look approval.

Provider preference for final use:

1. Pexels candidates first, when visually strong and no identifiable person/trademark risk.
2. Pixabay candidates if a future rerun adds them and a local copy is downloaded for intended use.
3. Unsplash candidates as metadata/hotlink/source-download entries until the proper API use/download registration path is wired.
4. Openverse candidates only after the original source page and specific Creative Commons/public-domain status are verified.

## Generated 1000-image bank role

Treat `topic_persona_image_bank_1000_20260715` as a broad internal creative/source bank, not a final asset library.

Best uses:

- complete topic/persona visual coverage for social planning;
- visual direction examples for the social prompt pack;
- placeholder images for dry-run manifests, clearly labelled non-final;
- prompt generation and future render requests;
- persona-specific campaign storyboards;
- A/B planning for topic/persona metaphors;
- identifying where stock metaphors fail and generated/hybrid art should take over.

Do not use it automatically for final covers or ads because:

- 625 assets derive from Openverse stock and inherit source-page verification requirements;
- 105 assets derive from manga/reference surfaces that are not aligned with Waystream self-help cover identity by default;
- many expanded topics are mapped to a core visual family rather than native art;
- resolution is social-friendly but not always KDP master-friendly;
- some rows have quality flags;
- the bank includes variants from a smaller source set, so it can create repeated visual language if used at scale without curation.

The 16-image seed bank from 2026-07-14 is more suitable as a high-touch style source than the 1000-bank derivatives. Use the seed bank to define generated/hybrid art direction for social and weak-topic reruns.

## Cover pipeline integration plan

The cover pipeline should not scan raw bank folders. It should read a curated registry.

Existing cover truths to preserve:

- `waystream_cover_system.yaml` already owns the 1600x2560 KDP canvas, author families, palettes, topic symbols, and image-family prompts.
- `scripts/publish/waystream_covers/assign.py` resolves a catalog row into a deterministic `Spec`.
- `scripts/publish/waystream_covers/render.py` already creates contact sheets, plan-vs-drawn checks, thumbnails, and look-approval surfaces.
- `platform_cover_profiles.yaml` is an adaptation layer, not a design layer. KDP, square audiobook, Kobo, and other outputs should adapt an approved master rather than creating separate designs.

Best integration:

1. Add a curated image registry later, for example `config/publishing/curated_waystream_image_sources.yaml` or `artifacts/curation/waystream_image_winners_20260715.json`.
2. Registry rows reference raw local paths, source URLs, license status, score, crop notes, and usage classes.
3. Cover resolver consumes only approved registry rows and only for image-family backgrounds or one-off pilot covers.
4. Existing typography, palette, title/subtitle fit, symbol contrast, and zero-overlap gates stay in the renderer.
5. Cover QA adds a source-provenance panel to the existing contact sheet, but does not duplicate the cover system.

KDP/book-cover guidance:

- Prefer non-human, symbolic, object, landscape, texture, and architectural metaphors.
- Avoid recognizable faces, distress poses, medical/procedure imagery, screens, brand marks, and celebrity/public-figure likenesses.
- Only use a cover candidate when it has enough negative space for title/subtitle/byline and can crop to 1600x2560 without losing the metaphor.
- Use the stock image as the image layer; keep all text in PIL.
- For Openverse/CC-BY assets, confirm that required attribution can be carried in the book copyright page, metadata, or other acceptable surface before final cover use.
- For CC0/PDM/Pexels/Pixabay/Unsplash assets, still retain creator/source provenance even when attribution is not required.

Audiobook/podcast/storefront thumbnail guidance:

- Start from the approved book cover or approved master image, then adapt to square profiles in `platform_cover_profiles.yaml`.
- For ACX/Findaway-like square assets, use title + author only and avoid marketing-copy badges unless the destination permits them.
- Use stronger single-symbol/focal candidates than KDP, because square thumbnails compress harder.
- If the cover metaphor is too subtle in square crop, create a square-specific crop from the same approved source, not a new unrelated image.

## Social media integration plan

The social prompt pack is authored but the social code/config/schema directories are not present in this worktree yet. Therefore, image-bank integration should target the planned L0/L3/L4 seams, not pretend a live social renderer exists.

Recommended social integration:

1. L0 schema should include `visual_source_ref`, `usage_class`, `license_status`, and `attribution_required` on every `media_ref`.
2. L3 `image_render_config.yaml` should point to curated registry rows, not raw bank folders.
3. L3 image renderer should support three source modes:
   - `approved_cover_source`: crop/derive from an approved book cover or cover image;
   - `approved_curated_image`: crop from a curated winner row;
   - `generated_prompt_reference`: use a prompt/style reference and queue new final art, not the reference image itself.
4. L4 Canva lane should use curated images as image slots and preserve attribution/source IDs in the exported manifest.
5. L5 video/Pearl Animator should use the bank for background stills, first-frame covers, and mood references, but final video stills need the same registry/provenance gate.
6. L7 QA gates should reject any media ref with `license_status != verified`, `usage_class == ideation_only`, or missing attribution when required.

Current platform sizing references checked on 2026-07-15:

- Meta feed placements support 1:1 and 4:5, with 4:5 recommended for vertical single-image feed ads in Meta Business Help: https://www.facebook.com/business/help/103816146375741
- Pinterest recommends standard image ads at 2:3 / 1000x1500, PNG/JPEG, with larger ratios at risk of feed cutoff: https://business.pinterest.com/creative-best-practices/
- TikTok Auction In-Feed Ads list vertical 9:16 as recommended, with >=540x960 minimum, common video file formats, and <=500 MB for non-Spark ads: https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads?redirected=2
- YouTube says square or vertical videos up to three minutes can be classified as Shorts after the relevant rollout dates, and its aspect-ratio help warns not to bake padding/black bars into videos: https://support.google.com/youtube/answer/15424877?hl=en and https://support.google.com/youtube/answer/6375112
- LinkedIn single image ads support landscape, square, and vertical; LinkedIn recommends 4:5 to avoid borders for vertical mobile delivery: https://business.linkedin.com/advertise/ads/sponsored-content/single-image-ads-specs
- LinkedIn document ads accept PDF/PPT/DOC formats with a 100 MB and 300-page limit; videos/animations in documents are static: https://www.linkedin.com/help/lms/answer/a493903

Practical defaults for this program:

| Asset type | Default dimensions | Best source class |
| --- | --- | --- |
| Instagram carousel/quote card | 1080x1350, 4:5 | curated stock/generator background plus PIL/Canva text |
| LinkedIn image/document slide | 1080x1350, 4:5, or 1200x1200 for broad delivery | cleaner professional metaphor, low clutter |
| Pinterest Pin | 1000x1500, 2:3 | direct, searchable metaphor with clear text overlay |
| TikTok/Reels/Shorts still or background | 1080x1920, 9:16 | generated/curated vertical background with UI safe zones |
| YouTube standard thumbnail | 1920x1080, 16:9 | 1000-bank wide rows for ideation; final from curated/approved source |

## Topic-by-topic metaphor strategy

Status meanings:

- `COVER_READY`: enough pre-legal candidates exist to enter cover curation. Not production-approved.
- `SOCIAL_READY`: enough candidates exist for social/quote/carousel backgrounds after normal curation, but cover needs stronger rerun or tighter selection.
- `IDEATION_ONLY`: use for moodboards or prompt references only.
- `RERUN_NEEDED`: current bank has meaningful gaps or legal/safety risk before first cover/social pilot.

| Topic | Recommended cover metaphors | Best bank(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| anxiety | tangled wires/string, storm cloud over small horizon, motion-blur traffic, single figure at distance, fog/edge landscape | 100x stock; small QA shortlist; 1000 for persona planning | COVER_READY | Avoid chest-clutch, panic-face, unsafe cliff/edge crops, and recognizable people. |
| depression | empty chair by grey window, rain on glass, foggy empty road, bare tree, low-lit empty room | 100x stock; small QA expansion | SOCIAL_READY | Good social pool, but cover should rerun for premium empty-room/grey-window assets. |
| grief | empty bed, empty chair/table, candle/lantern, fallen leaves, faded photo without recognizable people | 100x stock; small QA shortlist | COVER_READY | Avoid memorial/news context and identifiable old photos. |
| overthinking | maze/labyrinth, clock faces/gears, spiral staircase, mirror loop, scattered notes/papers | 100x stock; small QA | COVER_READY | One of the strongest topic sets; protect negative space for type. |
| burnout | burned match, candle burned out, wilted desk plant, empty office at night, empty coffee cup/no logo | 100x stock plus rerun | RERUN_NEEDED | Current pool has useful assets but too much clipart/generic desk risk. |
| self_worth | seedling through soil, hands holding seedling, silhouette on hill, sunlight through clouds, mirror silhouette/no face | 100x stock plus generated seed/rerun | RERUN_NEEDED | Avoid beauty/body-centric images, cultural/statue false positives, direct faces. |
| anger | cracked glass/earth, embers, storm lightning, broken chain, pressure-fracture texture | 100x stock; small QA | COVER_READY | Keep it symbolic. Avoid violent scenes, fists as aggression, weapons, or rage faces. |
| loneliness | one lit window, empty bench in fog, empty swing, distant silhouette, empty road/beach | 100x stock; small QA | COVER_READY | Strong emotional read without requiring faces. |
| healing | forest path morning, dawn, new leaves, sprout, repaired pottery/kintsugi | 100x stock; rerun for repaired-object | SOCIAL_READY | Forest/dawn works; kintsugi lane is weak and needs targeted rerun. |
| boundaries | line in sand, locked/unlocked door, open gate, threshold doorway, minimal fence | 100x stock; small QA | COVER_READY | Avoid body/swimsuit false positives and busy architectural distractions. |
| trauma | storm over calm water, shadow on wall, cracked mirror abstract, fragmented reflection, repaired object | generated/hybrid rerun; limited 100x stock | RERUN_NEEDED | Highest sensitive-topic risk. Avoid accident, blood, abuse, substance, broken wine glass, and identifiable distressed people. |
| hope | seedling, sunrise/horizon, small light in darkness, open doorway with light, path toward light | 100x stock; small QA | COVER_READY | Grade muted so it does not feel falsely cheerful beside heavier topics. |

Weak topics and exact rerun queries:

| Topic | Rerun queries |
| --- | --- |
| trauma | `cracked mirror dark abstract no person`; `storm over calm water moody`; `shadow silhouette wall minimal no face`; `fragmented mirror abstract no blood no accident`; `repaired ceramic gold repair macro no person` |
| burnout | `burned match macro dark editorial`; `candle burned out dark photo`; `wilted desk plant night office no logo`; `empty office night desk no readable screen`; `laptop night exhausted desk no logo no face` |
| self_worth | `sapling through soil`; `hands holding seedling close up`; `mirror reflection silhouette no face`; `standing silhouette hill minimal`; `sunlight through clouds moody` |
| depression | `empty chair grey window`; `rain on glass moody`; `foggy empty road`; `bare tree fog`; `empty room low light` |
| healing | `kintsugi pottery close up`; `repaired pottery gold repair macro`; `new growth burned tree`; `forest path morning`; `green sprout soil` |

## Topic and persona usage strategy

For book covers, topic matters more than persona. Waystream covers already differentiate by author line, palette, template family, title/subtitle, topic symbol, and installment count. Adding persona-heavy photography to covers risks making the system feel like niche stock ads and can collide with legal/sensitive-topic concerns.

For social and ads, persona matters a lot. Use the 1000-bank to choose persona-specific visual treatments, then graduate only clean winners.

Persona strategy:

| Persona group | Best visual treatment | Avoid |
| --- | --- | --- |
| corporate_managers, tech_finance_burnout, entrepreneurs | offices at night, closed laptops, empty desks, blurred motion, decision/pressure objects | readable screens, logos, financial charts that imply advice, recognizable workplace brands |
| healthcare_rns, first_responders | post-shift quiet rooms, folded jacket, hands/cup, dawn station, non-clinical recovery | patients, procedures, emergency scenes, uniforms with badges, crisis imagery |
| working_parents, gen_x_sandwich | kitchen table, closed laptop, calendar blocks with no readable text, car/rain, caregiving objects | child faces, school names, medical/care facility identifiers |
| gen_z_professionals, gen_z_student, gen_alpha_students | apartment windows, headphones, phone face down, school/study rooms, digital boundaries | readable UI, social app logos, overly polished influencer imagery |
| educators | classroom after hours, empty desk, chalkboard without readable text, paper stacks | school logos, child faces, identifiable classrooms |
| millennial_women_professionals, midlife_women | symbolic interiors, hands, silhouettes, mirror/no-face, natural light | beauty/glamour framing, body-centric self-worth imagery, direct identifiable portraits |

Usage class decisions:

| Class | Graduation rule |
| --- | --- |
| Production book cover candidate | `license_status=verified`, cover_score >=85, no face/logo/trademark risk, KDP crop pass, source attribution plan, operator look approval. |
| Social media candidate | `license_status=verified` or generated provenance approved, social_score >=75, platform crop pass, safety copy check, attribution plan if needed. |
| Ad creative candidate | all social gates plus no recognizable people unless release/warranty is explicit; no implied endorsement; no medical/clinical claim tone. |
| Moodboard/ideation-only reference | useful style/metaphor, but license pending, source mapped, derivative, low-res, manga/reference, or quality-flagged. Not publishable. |
| Reject/legal-risk/low-quality | visible logos/text, recognizable person in sensitive context, off-topic, news/protest/accident context, low detail, non-commercial/no-derivatives license, unclear source, or generic stock cliche. |

## Legal/compliance gates

Current external provider/license checks:

- Pexels license: Pexels says photos/videos can be downloaded and used for free, including commercial uses, attribution is not required, and modification is allowed. It also forbids putting identifiable people in a bad/offensive light, implying endorsement, trademark use, and redistributing as a competing stock service. Source: https://www.pexels.com/license/
- Pixabay Content License: Pixabay allows broad use but restricts standalone distribution, commercial use with recognizable trademarks/logos, immoral/illegal or misleading uses, trademark/service-mark use, and reminds users that other IP/privacy/property rights may apply. Source: https://pixabay.com/service/license-summary/
- Unsplash license: Unsplash permits free commercial and non-commercial use without permission, with attribution appreciated, but forbids selling images without significant modification and compiling images to replicate a competing service. Source: https://unsplash.com/license
- Openverse Terms: Openverse aggregates third-party openly licensed metadata, does not verify licensing status, requires compliance with CC/source-platform terms, and makes users independently responsible for verifying rights. Source: https://docs.openverse.org/terms_of_service.html
- CC BY 4.0: attribution, license notice, and modification indication are required when supplied/applicable, and privacy/publicity/moral rights can still limit use. Source: https://creativecommons.org/licenses/by/4.0/deed.en
- CC0: commercial copying/modification is allowed without asking permission, but publicity/privacy, trademark, and no-warranty limitations still matter. Source: https://creativecommons.org/publicdomain/zero/1.0/deed.en

Required gates for every selected winner:

1. Source-page verification: open the original source URL, verify license/status on the source page, record `license_verified_at`, `verified_by`, and a snapshot path.
2. License compatibility: reject non-commercial (`NC`), no-derivatives (`ND`) when cropping/editing is required, unclear custom licenses, and any source whose terms cannot support cover/social/ad use.
3. Attribution plan: store required attribution text and where it will appear. For CC-BY covers, decide whether book copyright page/metadata is sufficient before use.
4. Face/person review: default to no recognizable faces for covers, ads, trauma, depression, grief, anger, and clinical-adjacent content. Reject people shown in a bad light.
5. Logo/readable-text scan: OCR and visual review for brand marks, UI, watermarks, posters, book spines, software names, screens, license plates, school/hospital signs, and visible trademarks.
6. Medical/clinical tone check: reject hospital/patient/procedure imagery unless a specific healthcare lane approves it; no cure/treatment promise visuals.
7. Sensitive-topic safety: for trauma, depression, grief, anger, and anxiety, avoid accident scenes, self-harm cues, abuse implications, panic imagery, weapons, substance-specific imagery, or exploitation of distress.
8. Property/release risk: reject private interiors, artworks, museum objects, architecture, or product designs when rights are unclear and the asset is meant for commercial cover/ad use.
9. Generated-source provenance: for generated/derived assets, record prompt, source image, derivative chain, model/tool if known, and whether any stock source license is inherited.
10. Platform policy fit: social/ad variants must obey platform crop, safe-zone, and claim rules before scheduling payloads are emitted.

## Curation scoring rubric

Score each candidate 0-100 for cover and social separately. Any legal/safety hard fail sets the relevant score to 0 and moves the asset to reject or ideation-only.

Cover score:

| Criterion | Points |
| --- | ---: |
| Metaphor fit to topic without cliche/literal pathology | 20 |
| Single focal read at thumbnail | 20 |
| KDP crop and negative-space fit | 20 |
| Waystream brand tone and palette compatibility | 15 |
| Legal simplicity and attribution feasibility | 15 |
| Technical quality, resolution, no artifacts | 10 |

Social score:

| Criterion | Points |
| --- | ---: |
| Scroll-stopping visual salience | 20 |
| Text overlay readability and safe zones | 20 |
| Platform crop flexibility across 4:5, 2:3, 9:16, 1:1, 16:9 | 15 |
| Persona/topic emotional specificity | 15 |
| Save/share utility for quote, carousel, checklist, or ad hook | 10 |
| Legal/safety/ad suitability | 10 |
| Freshness versus generic stock look | 10 |

Recommended thresholds:

- `cover_score >=85`: cover pilot candidate after license verification.
- `cover_score 70-84`: social or cover moodboard candidate.
- `social_score >=75`: social pilot candidate after license verification.
- `ad_score >=85` plus no face/logo/legal ambiguity: ad candidate.
- Any score below 60: ideation or reject, depending on reason.

## Metadata schema for selected winners

Minimum fields requested by the operator are included, with added provenance and QA fields needed for production use.

```yaml
asset_id: "wss_anxiety_tangled_wire_pexels_8101094"
bank_id: "mental_health_editorial_100x"
source_kind: "stock_photo"
usage_classes:
  - "production_book_cover_candidate"
  - "social_media_candidate"
topic: "anxiety"
persona: null
metaphor: "tangled wire"
provider: "pexels"
local_path: "artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x/downloads/pexels/anxiety/pexels__anxiety__8101094.jpeg"
source_url: "https://www.pexels.com/photo/white-electrical-wire-on-gray-concrete-floor-8101094/"
creator_name: null
title: "A coiled white cable lies on a cracked and textured concrete floor..."
license_name: "Pexels License"
license_url: "https://www.pexels.com/license/"
license_status: "pending_source_page_verification"
license_verified_at: null
verified_by: null
source_snapshot_path: null
attribution_required: false
attribution_text: "Photo by <creator> on Pexels"
cover_score: null
social_score: null
ad_score: null
crop_notes:
  kdp_1600x2560: "pending"
  square_3000x3000: "pending"
  ig_1080x1350: "pending"
  pinterest_1000x1500: "pending"
  vertical_1080x1920: "pending"
face_logo_verdict: "pending"
medical_safety_verdict: "pending"
sensitive_topic_verdict: "pending"
reject_reason: null
r2_key: null
qa_report_path: null
operator_approval_ref: null
```

For generated/derived images, add:

```yaml
generated_prompt: "..."
generation_model_or_tool: "unknown|imagegen|flux|derived_variant"
derivative_of:
  - source_asset_id: "..."
    source_license_status: "..."
source_native_topic: "..."
source_native_persona: "..."
topic_family_status: "native_core|mapped"
```

## R2/storage plan

Do not upload now.

When curation is complete, upload only curated winners, derivatives, manifests, and license snapshots. Do not push the entire 100x bank by default.

Proposed local manifest:

```text
artifacts/curation/waystream_image_winners_20260715/
  curated_winners.json
  license_snapshots/
  contact_sheet_shortlist.jpg
  crop_previews/
  QA_REPORT.md
```

Proposed R2 keys after approval:

```text
brand/way_stream_sanctuary/image_bank/curated/curated_winners.json
brand/way_stream_sanctuary/image_bank/curated/source/{asset_id}.{ext}
brand/way_stream_sanctuary/image_bank/curated/license_snapshots/{asset_id}.html
brand/way_stream_sanctuary/image_bank/curated/crop_previews/{asset_id}/{profile}.png
brand/way_stream_sanctuary/image_bank/curated/derivatives/cover/{book_id}.png
brand/way_stream_sanctuary/image_bank/curated/derivatives/social/{platform}/{asset_id}_{format}.png
```

Storage rules:

- Raw bank paths remain immutable local provenance.
- Curated rows store checksums and source paths.
- R2 manifest stores selected winners, not every raw result.
- Every derivative points back to exactly one approved source row or one approved generated prompt/source chain.
- R2 upload happens only after source-page license verification and curation QA.

## Implementation wave plan

Smallest safe lanes:

1. Curation manifest lane, docs/data only.
   - Write a shortlist manifest and crop/contact-sheet review packet.
   - Pick 3-5 candidates per core topic from `mental_health_editorial_100x`, with small-bank QA notes as guidance.
   - No renderer edits. No uploads.

2. License verification lane, selected assets only.
   - Verify source pages for the first 24-36 shortlisted assets.
   - Record snapshots, terms, attribution, and face/logo risk.
   - Output `license_status=verified|rejected|needs_owner_call`.

3. Cover pilot planning lane, no renderer edit until assets are verified.
   - Select one safe topic, recommended `overthinking` or `boundaries`.
   - Produce a non-invasive pilot spec for how the existing cover renderer would read one curated registry row.
   - Only after operator approval, add optional registry consumption behind a flag.

4. Social L3 integration lane after the social L0 schema exists.
   - Add `visual_source_ref` and `usage_class` fields to media refs.
   - Render one quote card and one carousel cover using verified curated images.
   - Keep output look-gated; no full-book scale.

5. Weak-topic rerun lane.
   - Rerun `trauma`, `burnout`, `self_worth`, `depression`, and `healing` with exact queries above.
   - Prefer Pexels/Pixabay/Unsplash for simpler production use; use Openverse only with source verification.
   - No R2 upload until the verification lane passes.

6. R2 selected-winners lane.
   - Push only verified selected winners and manifests using the existing R2 helper.
   - Do not upload raw banks unless the operator explicitly requests archival storage.

Recommended first implementation lane: curation manifest lane for 24-36 candidates across `overthinking`, `boundaries`, `grief`, `loneliness`, `anxiety`, and `hope`. This avoids weak-topic rerun complexity and proves the registry shape before any cover/social renderer changes.

## Open questions

1. Should CC-BY assets ever be allowed on final paid book covers if attribution is available in the book copyright page but not visible on the cover?
2. Should generated images be allowed for paid ads, or only for organic social, until an AI-image disclosure/compliance policy is written?
3. Should the first cover pilot use a stock source, a generated seed source, or a hybrid source? Recommendation: stock source for `overthinking` or `boundaries`.
4. Should Pinterest and LinkedIn documents share the same 4:5 slide template, or should Pinterest keep a dedicated 2:3 template? Recommendation: dedicated 2:3 Pinterest template.
5. Should the 1000-bank manga/reference-derived rows be excluded from all self-help social final-use candidates by default? Recommendation: yes, ideation-only unless a manga-style campaign is explicitly approved.

## Exact next prompts to dispatch

### Prompt 1 - Pearl_Curator shortlist, no legal approval

```text
EXECUTE. You are Pearl_Curator for Phoenix Omega.

Task: create a docs/data-only shortlist from the existing Waystream image banks. Do not move, delete, generate, upload, or edit renderers.

Read:
- docs/STOCK_AND_GENERATED_IMAGE_BANK_COVER_SOCIAL_PLAN_2026-07-15.md
- artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial/QA_REPORT.md
- artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x/QA_REPORT.md
- artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x/index.json
- contact sheets under artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x/contact_sheets/

Mission:
Pick 3-5 shortlist candidates each for anxiety, grief, overthinking, anger, loneliness, boundaries, and hope. For each candidate, write topic, metaphor, provider, local_path, source_url, cover_score draft, social_score draft, crop_notes, and reject_reason if rejected. Mark every row license_status=pending_source_page_verification.

Deliver:
artifacts/curation/waystream_image_winners_20260715/curated_winners_draft.json
artifacts/curation/waystream_image_winners_20260715/QA_REPORT.md

Do not claim production approval.
```

### Prompt 2 - Pearl_Legal source-page verification

```text
EXECUTE. You are Pearl_Legal_Research for Phoenix Omega.

Task: verify source-page license/compliance for only the shortlist rows created by Pearl_Curator. Do not upload, edit renderers, or approve images visually.

Read:
- docs/STOCK_AND_GENERATED_IMAGE_BANK_COVER_SOCIAL_PLAN_2026-07-15.md
- artifacts/curation/waystream_image_winners_20260715/curated_winners_draft.json

Mission:
Open each source_url, verify the source-page license, creator/attribution, commercial-use compatibility, and any visible face/logo/property risk. Save a compact verification ledger with license_status=verified|rejected|needs_owner_call and exact evidence notes. Reject NC/ND/unclear sources for final cover use.

Deliver:
artifacts/curation/waystream_image_winners_20260715/license_verification_ledger.json
artifacts/curation/waystream_image_winners_20260715/LICENSE_QA_REPORT.md

Do not call any image production-ready unless source page and visual/legal checks pass.
```

### Prompt 3 - Pearl_Architect registry seam

```text
EXECUTE. You are Pearl_Architect for Phoenix Omega.

Task: design the smallest registry seam for curated image winners. Do not edit cover renderers yet.

Read:
- docs/STOCK_AND_GENERATED_IMAGE_BANK_COVER_SOCIAL_PLAN_2026-07-15.md
- config/publishing/waystream_cover_system.yaml
- config/publishing/platform_cover_profiles.yaml
- docs/agent_prompt_packs/20260714_social_media_pipeline/INDEX.md

Mission:
Draft the machine contract for curated image winners that both cover and future social L3 can consume. Include fields for topic, persona, usage_classes, provider, local_path, source_url, license_status, scores, crop_notes, attribution, and r2_key. Recommend where the config/manifest should live and how cover/social code should reference it without scanning raw banks.

Deliver:
docs/specs/CURATED_IMAGE_WINNERS_REGISTRY_SPEC.md

Do not implement renderer changes.
```

### Prompt 4 - Pearl_Int weak-topic rerun plan

```text
EXECUTE. You are Pearl_Int_ImageBank for Phoenix Omega.

Task: plan, but do not run, the weak-topic rerun for trauma, burnout, self_worth, depression, and healing.

Read:
- docs/STOCK_AND_GENERATED_IMAGE_BANK_COVER_SOCIAL_PLAN_2026-07-15.md
- config/brand_management/stock_image_bank_topics.yaml
- scripts/brand/build_stock_image_bank.py

Mission:
Prepare a rerun query plan using the exact weak-topic queries in the plan doc. Provider priority: Pexels/Pixabay/Unsplash first for production simplicity, Openverse only with source verification. Include expected output path, credentials needed, no-upload default, and curation gates.

Deliver:
artifacts/curation/waystream_image_winners_20260715/weak_topic_rerun_plan.md

Do not call provider APIs, download, upload, generate, or move assets.
```

