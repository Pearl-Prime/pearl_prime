# Pearl_Prez Agent Prompt — ITE HTML Presentation for Humans

## Identity

You are Pearl_Prez working in the Phoenix Omega repo.

## Task

Create a single-file HTML presentation explaining the Implicit Therapeutic Engine (ITE) to non-technical humans. The audience is: potential partners, investors, brand licensees, and curious creators.

## Read first

- `specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md` (the full spec)
- `research/2026-03-30_implicit-therapeutic-visual-media.md` (research basis)

## Presentation structure (3 acts)

### Act 1: The Concepts (Simple)

Explain these ideas like you're talking to a smart friend over coffee:

1. **Your nervous system responds to what it sees** — even when you don't notice. Panel sizes, colors, spacing, music tempo — your body reads all of it before your brain does.

2. **Entertainment can regulate you** — not through wellness lectures, but through structure. A page layout that naturally slows your breathing. A color shift that signals safety. A musical phrase that matches your heartbeat. The viewer/reader never knows.

3. **"Stealth therapy"** — the best therapeutic mechanisms work when invisible. Research shows labeling content as "therapeutic" makes it less effective. So we don't. The experience is pure entertainment. The regulation is silent.

4. **Every format carries it** — manga panels, video editing rhythms, soundtrack composition, even the spacing between panels. The system is embedded at every layer.

### Act 2: The Benefits (What humans care about)

1. **Readers report feeling calmer** — without knowing why. They read longer. They come back more often. They recommend more.

2. **Creators get it for free** — the system is in the production pipeline. Authors write stories. The pipeline adds the regulation layer automatically through layout, color, music, and pacing rules.

3. **It's measurable, not mystical** — every mechanism maps to published research. Fractal backgrounds reduce stress up to 60%. Resonance breathing rate (~6/min) maximizes heart rate variability. Pentatonic melodies reduce sympathetic nervous activity. Strategic silence drops heart rate below baseline.

4. **Cold read test** — we test by giving content to readers who know nothing about the system. If they feel calmer without identifying why, it works. If they detect "wellness" framing, it fails.

### Act 3: The Tech & Science (Name it)

Name each system with a one-sentence plain-language explanation + the science:

| System | What it does | Science |
|--------|-------------|---------|
| **Panel Breath Engine** | Panel sizes progressively grow and shrink to match breathing rhythm | Visual rhythm entrainment → 6 breaths/min resonance → HRV improvement |
| **Color Temperature Arc** | Colors shift warm→cool across each chapter, mirroring regulation | Warm=arousal, cool=calming (Valdez & Mehrabian); saturation drives arousal |
| **Fractal Regulation Layer** | Nature-complexity backgrounds in calming scenes | FD 1.3-1.5 fractals → up to 60% stress reduction (Taylor, UOregon) |
| **Gutter Therapy System** | Space between panels widens after intense moments | Gutters scaffold emotional processing (graphic medicine research) |
| **Sabido Character Transmission** | Characters model regulation through behavior, never words | 50+ years of Sabido entertainment-education research |
| **Edit Rhythm Entrainment** | Video cuts slow to match breathing in calming scenes | Viewer respiration entrains to visual rhythm (Frontiers in Neuroscience) |
| **Soundtrack Therapeutic Engine** | Pentatonic melodies, strategic silence, tempo arcs | Bernardi: silence drops HR below baseline; 10-sec phrases match Mayer waves |
| **EI v2 Visual Therapeutic Scoring** | AI scores every chapter on 4 therapeutic dimensions | Composite ITE_score with pass/fail gates |

## Design requirements

- Single HTML file, self-contained (inline CSS, no external dependencies)
- Clean, modern design — think pitch deck, not PowerPoint
- Use a dark background with warm accent colors (matches the "Bright" theme from Adi Da doctrine + Phoenix branding)
- Large readable type (24px+ body, 48px+ headers)
- Slide-style layout (sections separated by full-height dividers)
- Mobile responsive
- Include the research table from Act 3 as a styled HTML table
- No emojis unless specifically requested
- File: `presentations/ite_human_overview.html`

## Rules

1. **Never say "therapy" in consumer-visible text.** Say "regulation," "calming architecture," "nervous system support."
2. **Lead every section with the human benefit, then the science.** Not the other way around.
3. **Keep it short.** Each slide should have ≤100 words. Total presentation ≤20 slides.
4. **No clinical claims.** "Supports regulation" not "treats anxiety."
5. **Cite research by paraphrase, not verbatim quote.**

## Write scope

- `presentations/ite_human_overview.html` (new)

## Out of scope

- Spec changes, code changes
- Detailed technical architecture diagrams
- Consumer-facing marketing (separate Pearl_Marketing task)
