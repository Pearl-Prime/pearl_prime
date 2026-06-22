export const meta = {
  name: 'author-brand-catalog-wf',
  description: 'Author tier-3 en_US catalog LISTINGS (series+books) for one brand via Pearl_Writer -> Pearl_Editor',
  phases: [
    { title: 'Author', detail: 'Pearl_Writer drafts each series (distinct titles + 400-520w descriptions)' },
    { title: 'Edit', detail: 'Pearl_Editor polishes, enforces distinctness + BISAC sanity' },
  ],
}

const d = (typeof args === 'string') ? JSON.parse(args) : args
const { brand, display_name, byline_note, brand_voice, series_ids } = d

const ENGINE_ANGLES = {
  false_alarm: "the body's alarm system firing when there is no real danger — bracing for something you can't name",
  overwhelm: "too much arriving at once — the flood, capacity exceeded, no room left to think",
  spiral: "one thought becoming a thousand — the downward pull of rumination that feeds itself",
  shame: "the buried belief that something is wrong with YOU — the defect you hide and overwork to cover",
  grief: "loss and letting go — what was taken, or what must finally be released to move on",
  comparison: "measuring yourself against everyone who looks calm and fine — and always coming up short",
  watcher: "the hypervigilant, scanning mind that never goes off duty — monitoring threats that never come",
}
const engineAnglesText = Object.entries(ENGINE_ANGLES).map(([k, v]) => `  - ${k}: ${v}`).join('\n')

const GOLD = `GOLD STANDARD (from a DIFFERENT brand "night_reset" — match its DEPTH and humanity, do NOT copy its nocturnal voice):
  title (comparison engine): "Everyone Else Seems to Sleep Fine"
  subtitle: "For the wide-awake who feel they're falling behind — measuring a restless night against everyone who looks calm"
  long_description excerpt: "At 3am, it feels like you're the only one still awake. Everyone else seems to have figured something out... This book is for the mind that measures itself against everyone else and always comes up short... You're not lazy and you're not failing. You've just pointed a high-performance instrument at the wrong target: yourself, in the dark... Nothing here will help you win the comparison. That's the point... Book 6 of the Still Hour Press series."
  voice_markers.register: "intimate, nocturnal, plainspoken; the voice of someone awake in the next room, not a clinician"`

const SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['series_id', 'series', 'books'],
  properties: {
    series_id: { type: 'string' },
    series: {
      type: 'object', additionalProperties: false,
      required: ['reader_promise_family', 'reader_avatar', 'series_voice_markers', 'comp_series'],
      properties: {
        reader_promise_family: { type: 'string' },
        reader_avatar: {
          type: 'object', additionalProperties: false,
          required: ['age', 'where_they_are', 'what_they_need', 'what_they_avoid'],
          properties: { age: { type: 'string' }, where_they_are: { type: 'string' }, what_they_need: { type: 'string' }, what_they_avoid: { type: 'string' } },
        },
        series_voice_markers: {
          type: 'object', additionalProperties: false,
          required: ['register', 'sentence_rhythm', 'metaphor_family'],
          properties: { register: { type: 'string' }, sentence_rhythm: { type: 'string' }, metaphor_family: { type: 'string' } },
        },
        comp_series: { type: 'array', items: { type: 'string' }, minItems: 3, maxItems: 3 },
      },
    },
    books: {
      type: 'array', minItems: 1,
      items: {
        type: 'object', additionalProperties: false,
        required: ['book_id', 'title', 'subtitle', 'cover_tagline', 'short_blurb', 'long_description', 'keywords', 'comp_titles', 'bisac_codes'],
        properties: {
          book_id: { type: 'string' },
          title: { type: 'string' },
          subtitle: { type: 'string' },
          cover_tagline: { type: 'string' },
          short_blurb: { type: 'string' },
          long_description: { type: 'string' },
          keywords: {
            type: 'object', additionalProperties: false, required: ['primary', 'secondary'],
            properties: { primary: { type: 'array', items: { type: 'string' }, minItems: 5, maxItems: 7 }, secondary: { type: 'array', items: { type: 'string' }, minItems: 2, maxItems: 3 } },
          },
          comp_titles: { type: 'array', items: { type: 'string' }, minItems: 3, maxItems: 3 },
          bisac_codes: { type: 'array', items: { type: 'string' }, minItems: 2 },
        },
      },
    },
  },
}

function writerPrompt(sid) {
  return `You are Pearl_Writer, a bestselling self-help catalog copywriter. Author the real marketplace LISTING (Amazon KDP / Audible) for EVERY book in ONE series of the imprint "${display_name}". This is production copy a buyer reads before purchasing — specific, emotionally precise, zero template/placeholder language.

STEP 1 — read the skeleton (locked structural facts: book_ids, engines, installment numbers, BISAC floor you MUST keep):
  cat config/source_of_truth/series_plans_en_us/${sid}.yaml
  for f in config/source_of_truth/book_plans_en_us/${sid}__*.yaml; do echo "== $f =="; cat "$f"; done

AUTHOR ONLY the book_plans that contain "_needs_authoring: true" — those are this run's arc-backed skeletons. SKIP any sibling file that lacks that flag or is already authored (legacy orphans): do NOT author them, do NOT include them in your output.

The series_id encodes brand__teacher__persona__topic. It has one book per ENGINE. Each engine is a distinct emotional doorway into the same topic — author each book to ITS angle:
${engineAnglesText}

${GOLD}

BRAND VOICE for ${display_name} (use THIS, never the gold's):
  register: ${brand_voice.register}
  metaphor family: ${brand_voice.metaphor_family}
  reader avoids: ${brand_voice.what_they_avoid}

FOR EACH BOOK:
- title: DISTINCT, evocative, specific — reflect this book's engine angle + topic + the persona's lived world. NEVER a generic "<Topic> Relief: ..." formula, NEVER the same title as a sibling book, NEVER an intent label like "scenario specific", NEVER truncated. (Gold: "Everyone Else Seems to Sleep Fine".)
- subtitle: persona-anchored, specific to this angle — NOT a thin "For X".
- cover_tagline: one haunting line.
- short_blurb: 2-3 sentences, the hook (no fragments).
- long_description: 380-520 words, SECOND PERSON, in the brand voice. Arc: open in the felt moment -> name exactly who this is for -> what they'll come to recognize, engine by engine of the topic -> what it will NOT promise (no fix, no optimization) -> a closing line of permission. End with the literal line: "Book <installment_number> of the ${display_name} <topic-as-words> series."
- keywords.primary: 5-7 real Amazon search phrases a sufferer would type; keywords.secondary: 2-3.
- comp_titles: exactly 3 real comparable bestsellers, each "Title (Author) — one-clause why".
- bisac_codes: KEEP the skeleton's floor exactly; you MAY append at most one more real SEL/PSY code. For ANY anxiety-family topic (anxiety/sleep_anxiety/social_anxiety/financial_anxiety/overthinking) the list MUST contain SEL036000 and MUST NOT contain SEL045000.

SERIES-LEVEL: reader_promise_family; reader_avatar{age, where_they_are = a vivid present-tense moment, what_they_need, what_they_avoid}; series_voice_markers{register, sentence_rhythm, metaphor_family}; comp_series (3 "Title (Author) — why").

${byline_note}

Return ONLY the structured object for series_id="${sid}", with every _needs_authoring:true book_id present exactly once (no legacy-orphan book_ids).`
}

function editorPrompt(authored, sid) {
  return `You are Pearl_Editor. Review and POLISH this authored series listing for the imprint "${display_name}" to ship-ready tier-3. Return the corrected full object (same schema, series_id="${sid}").

ENFORCE, fixing anything that fails:
1. Every book title is DISTINCT within the series, specific, evocative — no generic "<Topic> Relief" repeats, no intent-label leak ("scenario specific"), no truncation ("... Voices from"), no two books sharing a title.
2. Subtitles are persona-specific and concrete — reject thin "For <persona>" subtitles; rewrite them.
3. long_description: 380-520 words, real second-person brand voice, NO garbled template-merges (e.g. "workers who I want to connect but being around people is agony"), ends with the "Book N of the ${display_name} ... series." line.
4. short_blurb: complete sentences, no fragments.
5. bisac_codes: anxiety-family topic MUST include SEL036000 and MUST NOT include SEL045000; keep the skeleton floor.
6. keywords are real searchable phrases; comp_titles are 3 real books.
7. Brand voice = ${display_name}: ${brand_voice.register}. Metaphors: ${brand_voice.metaphor_family}.

Make every fix silently and return the full corrected object. Do not drop or add books.

AUTHORED DRAFT:
${JSON.stringify(authored)}`
}

phase('Author')
log(`${brand}: authoring ${series_ids.length} series via Pearl_Writer -> Pearl_Editor`)

const results = await pipeline(
  series_ids,
  (sid) => agent(writerPrompt(sid), { label: `write:${sid.split('__').slice(2).join('/')}`, phase: 'Author', schema: SCHEMA }),
  (authored, sid) => authored
    ? agent(editorPrompt(authored, sid), { label: `edit:${sid.split('__').slice(2).join('/')}`, phase: 'Edit', schema: SCHEMA })
    : null,
)

const ok = results.filter(Boolean)
log(`${brand}: ${ok.length}/${series_ids.length} series authored+edited`)
return ok
