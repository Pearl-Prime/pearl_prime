import { useState, useCallback, useRef, useMemo, useEffect } from "react";
import { useTranslation } from "./useTranslation.jsx";
import { ChevronRight, ChevronLeft, Eye, Sparkles, BookOpen, Mic, Film, Palette, Heart, Target, Zap, Shield, Sun, Moon, Flame, Feather, Brain, Compass, Star, Check, AlertTriangle, Download, Play, PenTool, Image, Layers, ArrowRight, Users, BarChart3, TrendingUp, Radio, Headphones, Tv, Smartphone, BookMarked, GraduationCap, Clock, Rocket, Award, Crown, Globe, Volume2, Brush, Activity, Search, Hash, Tag, Grip, CircleDot, SlidersHorizontal } from "lucide-react";
import { OutputProofStrip } from "./onboarding/OutputProofStrip.jsx";
import { LaneChoiceCard } from "./onboarding/LaneChoiceCard.jsx";
import { MarketChoiceCard } from "./onboarding/MarketChoiceCard.jsx";

// ─────────────────────────────────────────────────────────────
// PEARL PRIME — BRAND CREATION WIZARD v2.1
// White theme, 11-step wizard, persona impact panel
// Voice Tone split: Graphs page + Effects page
// Text-to-image prompts for visual styles
// V4 knobs integration
// ─────────────────────────────────────────────────────────────

// ═══════════════════════════════════════════════════════════
// DATA
// ═══════════════════════════════════════════════════════════

const ARCHETYPES = [
  {
    id: "nervous_system", name: "Stillness Lab",
    tagline: "When the body won't stop screaming",
    icon: Shield, gradient: "from-indigo-500 to-blue-600",
    bg: "bg-gradient-to-br from-indigo-50 to-blue-50",
    accent: "text-indigo-600", border: "border-indigo-200", activeBorder: "border-indigo-500",
    tags: ["Calm", "Somatic", "Regulation"],
    coverStyle: "Soft gradients, muted tones, organic shapes",
    proseStyle: "Gentle, paced, breath-aware",
    videoStyle: "Slow motion nature, soft focus, ambient",
    sampleTitle: "The Body Keeps the Score at 2AM",
    sampleSubtitle: "A nervous system reset for minds that won't shut off",
    sampleProse: "Your body remembers what your mind tries to forget. Right now, your shoulders are holding yesterday's argument. Your jaw is clenching around words you didn't say. This isn't a flaw — it's your nervous system doing exactly what it was designed to do.",
    sampleExercise: "4-7-8 Breath Reset: Inhale for 4 counts. Hold for 7. Exhale slowly for 8. Three cycles. That's 57 seconds to shift your entire nervous system state.",
    coverColors: ["#6366f1", "#818cf8", "#e0e7ff"],
    emotions: ["Finally calm", "Safe in my body", "Released", "Grounded", "Permission to rest"],
    visionVibe: "A world where silence isn't empty — it's full. Where the body is a compass, not a cage. Readers find safety not by escaping sensation but by finally listening to it.",
  },
  {
    id: "identity_direction", name: "Compass Studio",
    tagline: "For those who feel lost but aren't broken",
    icon: Compass, gradient: "from-emerald-500 to-teal-600",
    bg: "bg-gradient-to-br from-emerald-50 to-teal-50",
    accent: "text-emerald-600", border: "border-emerald-200", activeBorder: "border-emerald-500",
    tags: ["Direction", "Identity", "Purpose"],
    coverStyle: "Clean lines, compass motifs, open horizons",
    proseStyle: "Direct, warm, forward-moving",
    videoStyle: "Time-lapse journeys, dawn scenes, path imagery",
    sampleTitle: "You're Not Behind — You're Building",
    sampleSubtitle: "Finding direction when everyone else seems to have it figured out",
    sampleProse: "Scroll through your feed and everyone's winning. They've got the career, the relationship, the apartment with the plants that don't die. And you're sitting here wondering what you're even doing.",
    sampleExercise: "The Honest Audit: Write three things you chose this week — even small ones. A meal, a conversation, a boundary. Now write one thing you avoided. The pattern is your compass needle.",
    coverColors: ["#059669", "#34d399", "#d1fae5"],
    emotions: ["Clear-headed", "Connected to purpose", "Hopeful", "Confident", "Energized"],
    visionVibe: "A world where not knowing isn't failure — it's the beginning. Where direction comes from honest self-observation, not external comparison. Readers build identity through small, brave choices.",
  },
  {
    id: "emotional_healing", name: "Soft Lantern",
    tagline: "Grief doesn't follow a schedule",
    icon: Heart, gradient: "from-rose-500 to-pink-600",
    bg: "bg-gradient-to-br from-rose-50 to-pink-50",
    accent: "text-rose-600", border: "border-rose-200", activeBorder: "border-rose-500",
    tags: ["Healing", "Grief", "Tenderness"],
    coverStyle: "Warm watercolors, soft light, intimate close-ups",
    proseStyle: "Tender, witnessing, permission-giving",
    videoStyle: "Intimate lighting, rain on windows, warm interiors",
    sampleTitle: "It's Okay to Not Be Okay Right Now",
    sampleSubtitle: "A companion for the grief nobody prepared you for",
    sampleProse: "Nobody told you grief could feel like this — not the crying kind, but the numb kind. The kind where you forget why you walked into a room, where food has no taste, where your phone rings and you just watch it.",
    sampleExercise: "The Witness Practice: Place one hand on your chest. Say out loud: 'This is hard. I'm allowed to feel this. I don't have to fix it right now.' Notice what shifts.",
    coverColors: ["#f43f5e", "#fb7185", "#ffe4e6"],
    emotions: ["Less alone", "Forgiven", "Released", "Safe in my body", "Hopeful"],
    visionVibe: "A world where pain doesn't have to be productive. Where grief is met with witness, not advice. Readers find healing not by being fixed but by finally being seen.",
  },
  {
    id: "performance_focus", name: "Clear Mind Lab",
    tagline: "Cut the noise. Execute what matters.",
    icon: Zap, gradient: "from-amber-500 to-orange-600",
    bg: "bg-gradient-to-br from-amber-50 to-orange-50",
    accent: "text-amber-600", border: "border-amber-200", activeBorder: "border-amber-500",
    tags: ["Focus", "Discipline", "Execution"],
    coverStyle: "Bold typography, sharp contrast, geometric",
    proseStyle: "Direct, punchy, action-oriented",
    videoStyle: "Fast cuts, dark backgrounds, kinetic text",
    sampleTitle: "Your Phone Is Stealing Your Life",
    sampleSubtitle: "A 21-day protocol for reclaiming deep focus",
    sampleProse: "You checked your phone 47 times before noon. Not because you're undisciplined — because every app on that screen was engineered by teams of PhDs to hijack your dopamine system.",
    sampleExercise: "The 90-Minute Block: Set one timer. Pick one task. Phone in another room. When the timer rings, you're done — even if it's not perfect. Ship it.",
    coverColors: ["#d97706", "#f59e0b", "#fef3c7"],
    emotions: ["In control", "Clear-headed", "Energized", "Confident", "Resilient"],
    visionVibe: "A world where clarity is a weapon. Where action beats reflection. Readers cut through information overload and build systems that run without willpower.",
  },
  {
    id: "spiritual_awakening", name: "Phoenix Rising",
    tagline: "The old you has to die for the real you to live",
    icon: Flame, gradient: "from-purple-500 to-violet-600",
    bg: "bg-gradient-to-br from-purple-50 to-violet-50",
    accent: "text-purple-600", border: "border-purple-200", activeBorder: "border-purple-500",
    tags: ["Awakening", "Meaning", "Depth"],
    coverStyle: "Sacred geometry, cosmic gradients, gold accents",
    proseStyle: "Contemplative, layered, poetic",
    videoStyle: "Cinematic nature, cosmic imagery, ritual movement",
    sampleTitle: "The Silence Between Your Thoughts Is God",
    sampleSubtitle: "Meditation for people who've tried everything and given up",
    sampleProse: "You've read the books. Downloaded the apps. Sat on the cushion and waited for something to happen. Nothing did — except your grocery list showing up uninvited.",
    sampleExercise: "The Gap Practice: Close your eyes. Take one breath. At the top of the inhale, before you exhale — notice the gap. Stay there. That's the door.",
    coverColors: ["#7c3aed", "#a78bfa", "#ede9fe"],
    emotions: ["Present", "Connected to purpose", "Grounded", "Released", "Hopeful"],
    visionVibe: "A world where the sacred lives in the ordinary. Where silence isn't empty but radiant. Readers discover that what they've been seeking has been seeking them.",
  },
];

const PERSONAS = [
  { id: "burned_out_pro", label: "Burned-Out Professional", emoji: "💼", desc: "Drained, numb, running on fumes", needs: "Reset, relief, permission to stop", impact: "Content hooks into 'Sunday dread' and workplace exhaustion narratives" },
  { id: "gen_z_seeker", label: "Gen Z Navigator", emoji: "🧭", desc: "Overwhelmed, comparing, scrolling", needs: "Direction, validation, real tools", impact: "Short-form first, TikTok-native hooks, anti-hustle tone" },
  { id: "gen_alpha", label: "Gen Alpha Explorer", emoji: "🌱", desc: "Growing up overstimulated, emotionally aware early", needs: "Age-appropriate tools, emotional vocabulary, safe guidance", impact: "Visual-heavy manga format, gamified exercises, guardian-safe" },
  { id: "grief_carrier", label: "Grief Carrier", emoji: "🕯️", desc: "Loss, numbness, can't explain it", needs: "Witness, tenderness, not fixing", impact: "Permission-giving language, no toxic positivity, soft CTAs" },
  { id: "anxious_achiever", label: "Anxious Achiever", emoji: "⚡", desc: "Succeeding outside, crumbling inside", needs: "Nervous system support, honesty", impact: "High-performance framing with vulnerability backdoor" },
  { id: "spiritual_returner", label: "Spiritual Returner", emoji: "🌅", desc: "Tried everything, still searching", needs: "Depth, authenticity, no fluff", impact: "Dense contemplative prose, tradition-aware, anti-guru" },
  { id: "new_parent", label: "Overwhelmed Parent", emoji: "👶", desc: "Lost identity, no time, guilt", needs: "Quick tools, self-compassion", impact: "Micro-format priority, guilt-free framing, practical exercises" },
];

const MOMENTS = [
  { id: "2am_overthinking", label: "2AM — Can't stop thinking", scene: "Dark room, phone glow, racing mind", emoji: "🌙", hookStyle: "Opens with the sensation of lying awake, validates the spiral, offers one immediate grounding tool" },
  { id: "after_breakup", label: "After a breakup or loss", scene: "Empty apartment, silence, numbness", emoji: "💔", hookStyle: "Names the specific flavor of grief — not sadness but numbness, the food-has-no-taste kind" },
  { id: "burnout_cant_quit", label: "Burned out but can't quit", scene: "Office bathroom, deep breath, mask back on", emoji: "🔥", hookStyle: "Catches them in the mask-on moment, speaks to the gap between public performance and private collapse" },
  { id: "feeling_behind", label: "Feeling behind in life", scene: "Scrolling feed, everyone winning, you stuck", emoji: "📱", hookStyle: "Targets comparison scrolling, reframes 'behind' as a construction, turns the phone into the trigger object" },
  { id: "panic_spike", label: "Panic attack / anxiety spike", scene: "Chest tight, can't breathe, world shrinking", emoji: "😰", hookStyle: "Physical-first language, names body sensations before emotions, immediate somatic intervention" },
  { id: "sunday_dread", label: "Sunday dread before Monday", scene: "Couch, clock ticking, stomach sinking", emoji: "⏰", hookStyle: "Taps the weekly cycle of anticipatory anxiety, validates the sinking feeling, reframes the Sunday as reclamation" },
];

const TRADITIONS = [
  "Zen Buddhism", "Sufi mysticism", "Vedanta", "Vajrayana", "Taoism",
  "Stoicism", "Buddhist psychology", "Somatic therapy", "Polyvagal theory",
  "Contemplative Christianity", "Indigenous wisdom", "Secular mindfulness",
  "Breathwork science", "Depth psychology"
];

const VOICE_SLIDERS = [
  { id: "gentleDirect", left: "Gentle", right: "Direct", default: 50, color: "#6366f1", desc: "Controls sentence softness, permission language vs imperative commands" },
  { id: "simpleDeep", left: "Simple", right: "Deep", default: 50, color: "#059669", desc: "Controls vocabulary density, metaphor layers, conceptual complexity" },
  { id: "emotionalLogical", left: "Emotional", right: "Logical", default: 25, color: "#f43f5e", desc: "Controls story-to-data ratio, vulnerability level, analytical framing" },
  { id: "spiritualPractical", left: "Spiritual", right: "Practical", default: 50, color: "#7c3aed", desc: "Controls tradition references, sacred language, tool-first vs meaning-first" },
];

const VISUAL_STYLES = [
  {
    id: "calm_minimal", label: "Calm / Minimal", desc: "Clean, airy, lots of white space",
    palette: ["#f8fafc", "#e2e8f0", "#94a3b8", "#475569"], mood: "Serene, spacious, breathable",
    imagePrompt: "Minimalist book cover with vast white space, single delicate ink wash element floating in center, soft grey gradient background, thin sans-serif typography, Japanese zen aesthetic, editorial photography style, muted tones, clean geometric border",
    emotionPrompt: "Abstract soft watercolor wash in pale blue and white, single drop of color expanding outward in calm ripples, zen garden raked sand pattern, misty morning light, feeling of deep exhale and release",
  },
  {
    id: "dark_intense", label: "Dark / Intense", desc: "Moody, contrast-heavy, dramatic",
    palette: ["#1e1b4b", "#312e81", "#6366f1", "#c7d2fe"], mood: "Powerful, immersive, cinematic",
    imagePrompt: "Dramatic book cover with deep indigo and black, single shaft of violet light cutting through darkness, bold condensed typography, cinematic film grain, high contrast, moody atmospheric fog, Blade Runner color palette",
    emotionPrompt: "Person standing at edge of cliff at night, lightning illuminating the scene, dramatic cloud formations, deep indigo sky with electric violet lightning bolts, feeling of breakthrough power and transformation",
  },
  {
    id: "earthy_organic", label: "Earthy / Organic", desc: "Natural textures, warm tones",
    palette: ["#fef3c7", "#d97706", "#92400e", "#451a03"], mood: "Grounded, warm, textured",
    imagePrompt: "Book cover with handmade paper texture, warm amber and brown tones, dried botanical pressed flowers, hand-lettered serif typography, golden hour light, natural linen texture background, artisan craft aesthetic",
    emotionPrompt: "Hands cupping warm soil with a seedling sprouting, golden sunlight filtering through oak leaves, warm terracotta and amber palette, feeling of rootedness and connection to earth, morning garden dew",
  },
  {
    id: "bold_modern", label: "Bold / Modern", desc: "Sharp typography, geometric",
    palette: ["#fafafa", "#18181b", "#ef4444", "#fbbf24"], mood: "Energetic, decisive, striking",
    imagePrompt: "Bold book cover with stark black and white contrast, oversized helvetica bold typography, single red geometric accent shape, Swiss design grid layout, Bauhaus influence, high energy, magazine editorial style",
    emotionPrompt: "Abstract geometric explosion of red and yellow shapes on white background, sharp angular forms radiating outward, feeling of decisive action and clarity, kinetic energy frozen in motion",
  },
  {
    id: "premium_soft",
    label: "Premium / Geometric",
    desc: "Refined, precise, luxury-positioned",
    palette: ["#fdf4ff", "#d8b4fe", "#7e22ce", "#3b0764"],
    mood: "Elevated, geometric, timeless",
    imagePrompt:
      "Premium luxury nonfiction book cover with precise geometric layout, thin elegant serif or restrained sans typography, subtle gold line or foil accent, controlled lavender and deep purple planes, editorial grid discipline, aspirational transformation",
    emotionPrompt:
      "Architectural light on refined surfaces, crisp geometric shadows, sense of order and quiet authority, timeless high-end publishing mood",
  },
  {
    id: "sacred_cosmic",
    label: "Mysterious / Deep",
    desc: "Atmospheric, contemplative, subtly luminous",
    palette: ["#0f172a", "#7c3aed", "#f59e0b", "#fef3c7"], mood: "Intriguing, expansive, still commercial",
    imagePrompt:
      "Premium mysterious nonfiction book cover, atmospheric deep navy and violet, subtle sacred geometry or soft nebula hint, contemplative spiritual-transformation adjacent, magnetic curiosity without horror, crisp typography zone, editorial finish",
    emotionPrompt:
      "Contemplative night sky or soft abstract depth, subtle light bloom, sense of mystery and inward expansion without fantasy excess, emotionally open-ended, thumbnail-strong focal read",
  },
];

/** Visual-identity proof — curated bank (styles) + FLUX wizard pack; assets in public/onboarding/proof/wizard/ */
const VISUAL_IDENTITY_PROOF_URL = {
  calm_minimal: "/onboarding/proof/wizard/style_calm_minimal.png",
  dark_intense: "/onboarding/proof/wizard/style_dark_intense.png",
  earthy_organic: "/onboarding/proof/wizard/style_earthy_organic.png",
  bold_modern: "/onboarding/proof/wizard/style_bold_modern.png",
  premium_soft: "/onboarding/proof/wizard/style_premium_soft.png",
  sacred_cosmic: "/onboarding/proof/wizard/style_sacred_cosmic.png",
};

const ARCHETYPE_PROOF_URL = {
  nervous_system: "/onboarding/proof/wizard/archetype_nervous_system.png",
  identity_direction: "/onboarding/proof/wizard/archetype_identity_direction.png",
  emotional_healing: "/onboarding/proof/wizard/archetype_emotional_healing.png",
  performance_focus: "/onboarding/proof/wizard/archetype_performance_focus.png",
  spiritual_awakening: "/onboarding/proof/wizard/archetype_spiritual_awakening.png",
};

const PERSONA_PROOF_URL = {
  burned_out_pro: "/onboarding/proof/wizard/persona_burned_out_pro.png",
  gen_z_seeker: "/onboarding/proof/wizard/persona_gen_z_seeker.png",
  gen_alpha: "/onboarding/proof/wizard/persona_gen_alpha.png",
  grief_carrier: "/onboarding/proof/wizard/persona_grief_carrier.png",
  anxious_achiever: "/onboarding/proof/wizard/persona_anxious_achiever.png",
  spiritual_returner: "/onboarding/proof/wizard/persona_spiritual_returner.png",
  new_parent: "/onboarding/proof/wizard/persona_overwhelmed_parent.png",
};

const MOMENT_PROOF_URL = {
  "2am_overthinking": "/onboarding/proof/wizard/moment_2am_overthinking.png",
  after_breakup: "/onboarding/proof/wizard/moment_after_breakup.png",
  burnout_cant_quit: "/onboarding/proof/wizard/moment_burnout_office.png",
  feeling_behind: "/onboarding/proof/wizard/moment_comparison_scroll.png",
  panic_spike: "/onboarding/proof/wizard/moment_panic_tight_space.png",
  sunday_dread: "/onboarding/proof/wizard/moment_sunday_dread.png",
};

const EMOTION_PROOF_URL = {
  "Finally calm": "/onboarding/proof/wizard/emotion_finally_calm.png",
  "Safe in my body": "/onboarding/proof/wizard/emotion_safe_in_body.png",
  "Clear-headed": "/onboarding/proof/wizard/emotion_clear_headed.png",
  "In control": "/onboarding/proof/wizard/emotion_in_control.png",
  "Permission to rest": "/onboarding/proof/wizard/emotion_permission_rest.png",
  Energized: "/onboarding/proof/wizard/emotion_energized.png",
  "Connected to purpose": "/onboarding/proof/wizard/emotion_connected_purpose.png",
  Released: "/onboarding/proof/wizard/emotion_released.png",
  "Less alone": "/onboarding/proof/wizard/emotion_less_alone.png",
  Forgiven: "/onboarding/proof/wizard/emotion_forgiven.png",
  Grounded: "/onboarding/proof/wizard/emotion_grounded.png",
  Hopeful: "/onboarding/proof/wizard/emotion_hopeful.png",
  Present: "/onboarding/proof/wizard/emotion_present.png",
  Confident: "/onboarding/proof/wizard/emotion_confident.png",
  Resilient: "/onboarding/proof/wizard/emotion_resilient.png",
};

const TOPIC_TAG_PROOF_URL = Object.fromEntries(
  [
    "anxiety-at-night",
    "overthinking",
    "panic-grounding",
    "sunday-dread",
    "burnout-recovery",
    "nervous-system-reset",
    "decision-fatigue",
    "phone-addiction",
    "grief-timeline",
    "toxic-relationship-healing",
    "intergenerational-trauma",
    "heartbreak-recovery",
    "emotional-numbness",
    "feeling-behind",
    "quarter-life-crisis",
    "identity-rebuild",
    "purpose-after-30",
    "habit-building",
    "ADHD-productivity",
    "dopamine-detox",
    "deep-work",
    "meditation-beginners",
    "meaning-after-loss",
    "spiritual-no-religion",
    "inner-peace-chaos",
    "mindfulness-skeptics",
  ].map((t) => [t, `/onboarding/proof/wizard/topic_${t.replace(/-/g, "_")}.png`]),
);

const PROVEN = {
  nervous_system: {
    personas: ["Millennial women professionals 30-44 ($130-165M/yr)", "Tech/finance burnout pros 25-45 ($80-120M/yr)", "Working parents under-12 ($70-100M/yr)"],
    topics: ["anxiety that won't shut off at night", "burnout recovery without quitting", "nervous system regulation after work", "overthinking in bed", "panic attack grounding techniques"],
    keywords: ["nervous system regulation audiobook", "burnout recovery", "stop overthinking at night", "anxiety before sleep", "polyvagal calm"],
  },
  identity_direction: {
    personas: ["Gen Z navigating adulting 18-24 (fastest-growing segment)", "Millennial women career transition 30-44", "Identity rebuilders post-divorce 28-50"],
    topics: ["feeling behind compared to peers", "lost sense of purpose after 30", "quarter-life crisis", "rebuilding identity after breakup", "what to do with your life"],
    keywords: ["feeling lost in life audiobook", "quarter life crisis", "finding purpose", "identity crisis self help", "what am I doing with my life"],
  },
  emotional_healing: {
    personas: ["Grief/loss navigators all ages ($70-100M/yr)", "Trauma-aware millennials body-based recovery", "Parents processing intergenerational patterns"],
    topics: ["grief that doesn't follow a timeline", "healing after toxic relationship", "intergenerational trauma", "heartbreak recovery", "emotional numbness"],
    keywords: ["grief audiobook", "healing after breakup", "trauma recovery self help", "emotional healing", "letting go of past"],
  },
  performance_focus: {
    personas: ["Corporate middle managers 32-50 ($50-80M/yr)", "Entrepreneurs/solopreneurs 28-50 ($60-100M/yr)", "Tech workers seeking focus 25-40"],
    topics: ["phone addiction destroying focus", "can't stick to habits", "decision fatigue as a manager", "ADHD-friendly productivity", "dopamine detox"],
    keywords: ["focus audiobook", "productivity self help", "habit building", "ADHD focus techniques", "deep work practice"],
  },
  spiritual_awakening: {
    personas: ["Gen X wisdom seekers 45-58 ($165M/yr highest-spending)", "Contemplative professionals seeking meaning", "Post-crisis seekers finding new framework"],
    topics: ["meditation that actually works for beginners", "finding meaning after loss", "spiritual practice without religion", "inner peace in chaos", "mindfulness for skeptics"],
    keywords: ["meditation audiobook", "finding inner peace", "spiritual growth", "mindfulness for beginners", "meaning of life self help"],
  },
};

// V4 Angles
const V4_ANGLES = [
  { id: "debunk", label: "Debunk", desc: "Challenge mainstream advice — 'What your therapist won't tell you'", framing: "Contrarian hook, evidence-backed pivot", icon: AlertTriangle },
  { id: "framework", label: "Framework", desc: "Give them a system — '5-step protocol for...'", framing: "Structured, repeatable, tool-first", icon: Layers },
  { id: "reveal", label: "Reveal", desc: "Expose hidden truth — 'The real reason you can't sleep'", framing: "Insider knowledge, 'nobody talks about this'", icon: Eye },
  { id: "leverage", label: "Leverage", desc: "Use what they already have — 'Your anxiety is a superpower'", framing: "Reframe existing trait as advantage", icon: Zap },
  { id: "origin", label: "Origin Story", desc: "Trace the root — 'Where your pattern actually started'", framing: "Narrative depth, causal chain, 'aha moment'", icon: Search },
];

// V4 Formats
const V4_FORMATS_STRUCTURAL = [
  { id: "F001", label: "Standard Self-Help", chapters: "12-16", tier: "full", desc: "Classic narrative arc with exercises woven in" },
  { id: "F002", label: "Guided Program", chapters: "8-12", tier: "full", desc: "Step-by-step transformation protocol" },
  { id: "F003", label: "Daily Journal", chapters: "30-90", tier: "micro", desc: "One page per day, reflection-heavy" },
  { id: "F004", label: "Somatic Workbook", chapters: "10-14", tier: "full", desc: "Body-first exercises, minimal narrative" },
  { id: "F005", label: "Narrative Journey", chapters: "14-20", tier: "full", desc: "Story-driven, deep emotional arc" },
  { id: "F006", label: "Compressed Wisdom", chapters: "6-8", tier: "mini", desc: "Dense, high-impact, short read" },
];

// ═══════════════════════════════════════════════════════════
// VOICE TONE DATA — 10 positions per slider with benefits
// ═══════════════════════════════════════════════════════════

const VOICE_TONE_10 = {
  gentleDirect: [
    {
      position: 1, label: "Ultra-Gentle",
      technique: "Opens with 'You might notice...' — never commands, only observes alongside the reader",
      benefits: [
        "Creates immediate psychological safety — reader's nervous system downregulates on first page",
        "Disarms shame and self-criticism that blocks receptivity to new ideas",
        "Readers who've been told 'just try harder' finally feel seen instead of lectured",
        "Builds trust with trauma-aware audiences who distrust authority-tone content",
        "Reduces book abandonment — gentle entry keeps anxious readers turning pages",
      ],
    },
    {
      position: 2, label: "Very Gentle",
      technique: "Uses permission language: 'It's okay to...' and 'You're allowed to...'",
      benefits: [
        "Gives explicit permission to feel — many readers have never received this",
        "Counteracts internalized 'suck it up' messaging from family or culture",
        "Emotionally overwhelmed readers feel validated rather than pathologized",
        "Creates a sense of being parented well — meeting an unmet developmental need",
        "Reduces the shame spiral that prevents readers from doing the exercises",
      ],
    },
    {
      position: 3, label: "Gentle",
      technique: "Exercises framed as invitations, not instructions — 'If you'd like, try...'",
      benefits: [
        "Respects reader autonomy — they choose to engage rather than being told to",
        "People with control-related trauma can participate without triggering resistance",
        "Higher exercise completion rate — invitations feel safer than commands",
        "Builds intrinsic motivation rather than compliance-based engagement",
        "Reader feels like a collaborator, not a patient — preserves dignity",
      ],
    },
    {
      position: 4, label: "Soft",
      technique: "Slower sentence rhythm with intentional pauses and breath-aware pacing",
      benefits: [
        "Reading pace mirrors meditation — the book itself becomes a calming practice",
        "Anxious readers' heart rate actually slows when prose rhythm is paced",
        "Creates space for emotional processing between concepts",
        "Audiobook version works as a de-escalation tool during panic moments",
        "Readers report feeling 'held' by the writing — attachment need met through text",
      ],
    },
    {
      position: 5, label: "Balanced-Gentle",
      technique: "Validation before direction — acknowledges feelings first, then offers a path",
      benefits: [
        "Mirrors ideal therapeutic rapport — feel understood, then open to change",
        "Both emotional and logical readers find their entry point",
        "Prevents the 'this book doesn't get me' abandonment that pure advice triggers",
        "Creates a rhythm readers can predict and trust across chapters",
        "Balanced enough for skeptics while warm enough for emotionally-driven readers",
      ],
    },
    {
      position: 6, label: "Balanced-Direct",
      technique: "Clear statements of truth with warmth — 'Here's what's actually happening'",
      benefits: [
        "Readers get the 'real talk' they crave without feeling attacked",
        "Builds authority — readers trust a voice that tells them the truth kindly",
        "Works for both self-help newcomers and experienced personal-development readers",
        "Strong TikTok clip potential — direct truth cuts through scroll noise",
        "Creates quotable moments readers screenshot and share",
      ],
    },
    {
      position: 7, label: "Firm",
      technique: "Action-first sentences — leads with what to do, explains why after",
      benefits: [
        "Overwhelmed readers need fewer decisions — clear direction reduces cognitive load",
        "Performance-oriented readers respond to efficiency and structure",
        "Higher conversion to action — readers do the exercises, not just read about them",
        "Creates a sense of being coached by someone who knows what they're doing",
        "Stronger titles and hooks for ad copy — direct language converts better",
      ],
    },
    {
      position: 8, label: "Direct",
      technique: "Short punchy sentences. No fluff. Every word earns its place.",
      benefits: [
        "ADHD-friendly — attention captured and held through rhythm and brevity",
        "Male-skewing audience feels respected — no unnecessary emotional padding",
        "Social media clips hit harder — short sentences = viral text-on-screen content",
        "Builds momentum — readers feel they're making progress fast",
        "Cuts through the 'every self-help book sounds the same' fatigue",
      ],
    },
    {
      position: 9, label: "Very Direct",
      technique: "Confrontational honesty — 'You already know this. You're avoiding it.'",
      benefits: [
        "Breaks through denial — some readers need to be challenged, not comforted",
        "High-achiever audience respects the courage to say what others won't",
        "Creates 'I feel called out' moments that drive word-of-mouth sharing",
        "Differentiates from the soft-tone self-help market — stands out on shelves",
        "Builds fierce loyalty — readers who connect with this voice become evangelists",
      ],
    },
    {
      position: 10, label: "Ultra-Direct",
      technique: "Commands and imperatives — 'Stop reading. Do this now. Then come back.'",
      benefits: [
        "Maximum behavior change — no ambiguity about what the reader should do",
        "Creates drill-sergeant loyalty in readers who respond to structure",
        "Audiobook version works as a real-time coaching session",
        "Content repurposes perfectly into course modules and challenge formats",
        "Readers complete entire programs — the commanding voice maintains momentum",
      ],
    },
  ],
  simpleDeep: [
    {
      position: 1, label: "Ultra-Simple",
      technique: "5th-grade reading level — every sentence crystal clear, zero jargon",
      benefits: [
        "Accessible to ESL readers — opens international markets dramatically",
        "Gen Alpha and young Gen Z can engage without barrier",
        "Readers in emotional crisis can absorb content when cognition is impaired",
        "Widest possible market reach — no educational prerequisite",
        "Audiobook comprehension highest — listener doesn't need to rewind",
      ],
    },
    {
      position: 2, label: "Very Simple",
      technique: "One concept per paragraph — builds understanding in small clear blocks",
      benefits: [
        "ADHD readers can follow without losing the thread",
        "Each paragraph is a complete, usable unit — easy to highlight and save",
        "Works perfectly as TikTok carousel content — one slide per concept",
        "Readers feel smart and capable rather than intimidated",
        "Higher exercise completion — instructions are impossible to misunderstand",
      ],
    },
    {
      position: 3, label: "Simple",
      technique: "Everyday metaphors — 'It's like clearing your browser tabs'",
      benefits: [
        "Abstract concepts land instantly through familiar reference points",
        "Readers explain ideas to friends using your metaphors — organic word-of-mouth",
        "Creates 'aha moments' without requiring background knowledge",
        "Content is meme-able and shareable on social platforms",
        "Bridge between clinical concepts and lived experience",
      ],
    },
    {
      position: 4, label: "Accessible",
      technique: "Clear explanations with occasional depth — introduces one new term per chapter",
      benefits: [
        "Readers feel they're learning without being overwhelmed",
        "Builds vocabulary gradually — reader grows with the book",
        "Strikes the sweet spot for mainstream self-help audience",
        "Good for podcast interviews — author can explain simply but show depth",
        "Creates authority without alienation — reader trusts the writer's knowledge",
      ],
    },
    {
      position: 5, label: "Balanced",
      technique: "Mix of plain language and richer concepts — 'simply put' bridges used",
      benefits: [
        "Serves the widest range of educational backgrounds",
        "Book clubs can discuss at multiple levels — everyone finds something",
        "Transitions work well in audiobook — narrator can signal shifts in depth",
        "Strong review potential — readers feel both comforted and challenged",
        "Longest shelf life — doesn't feel too basic or too academic after rereading",
      ],
    },
    {
      position: 6, label: "Thoughtful",
      technique: "Multi-sentence idea development — builds arguments before arriving at insights",
      benefits: [
        "Intellectually curious readers feel respected and engaged",
        "Creates page-turner quality — readers want to see where the idea goes",
        "Strong for series — later volumes can deepen without losing the audience",
        "Generates rich discussion material for therapy and group contexts",
        "Differentiates from shallow pop-psychology — earns premium pricing",
      ],
    },
    {
      position: 7, label: "Rich",
      technique: "Layered meaning — surface reading works, but rereading reveals more",
      benefits: [
        "Books become reference texts readers return to — longer customer lifetime value",
        "Creates intellectual community — fans discuss hidden layers online",
        "Audio version rewards re-listening — drives repeat engagement",
        "Attracts therapist and counselor audiences who recommend books to clients",
        "Content supports mastercourse format — enough depth for multi-week study",
      ],
    },
    {
      position: 8, label: "Deep",
      technique: "Philosophy and science woven together — references research without lecturing",
      benefits: [
        "Positions author as genuine authority, not just a motivational speaker",
        "Attracts Gen X wisdom-seeker market — highest-spending demographic",
        "Strong for keynote and TEDx content — ideas are substantive enough for stage",
        "Creates books that therapists assign — institutional recommendation pipeline",
        "Long-tail SEO potential — niche depth owns specific search territories",
      ],
    },
    {
      position: 9, label: "Very Deep",
      technique: "Cross-disciplinary synthesis — connects neuroscience, philosophy, and practice",
      benefits: [
        "Creates 'the book that changed my life' reactions — viral review potential",
        "Thought-leader positioning — author becomes known for original frameworks",
        "Academic and clinical citation potential — extends reach beyond consumer market",
        "Premium audiobook pricing justified — substantive enough for long-form audio",
        "International translation appeal — depth translates better than colloquialisms",
      ],
    },
    {
      position: 10, label: "Ultra-Deep",
      technique: "Graduate-level concepts, original frameworks, challenges reader to grow",
      benefits: [
        "Creates intellectual legacy — books referenced for decades",
        "Attracts high-income, high-education readers with strongest purchasing power",
        "Supports masterclass and certification program development",
        "Strong institutional and university adoption potential",
        "Author platform becomes a school of thought, not just a personal brand",
      ],
    },
  ],
  emotionalLogical: [
    {
      position: 1, label: "Ultra-Emotional",
      technique: "Story-first chapters — every concept arrives through a lived experience narrative",
      benefits: [
        "Mirror neurons activate — reader physically feels what characters feel",
        "Emotional memory encoding — readers remember content 6x longer than facts alone",
        "Creates the 'I cried reading this' reviews that drive viral sharing",
        "Deeply cathartic for readers carrying unprocessed emotion",
        "Audiobook version becomes a companion — listeners form parasocial bond with narrator",
      ],
    },
    {
      position: 2, label: "Very Emotional",
      technique: "High vulnerability in prose — the author's own wounds are visible in the writing",
      benefits: [
        "Readers feel less alone — 'someone else has been through this' is profoundly healing",
        "Dismantles the 'expert on a pedestal' barrier that blocks real connection",
        "Creates intense word-of-mouth — readers personally recommend to friends in crisis",
        "Strong podcast interview content — vulnerable stories captivate audiences",
        "Builds fierce community — readers bond with each other through shared emotional resonance",
      ],
    },
    {
      position: 3, label: "Emotional",
      technique: "Exercises include journaling and felt-sense work — 'Notice what arises'",
      benefits: [
        "Develops reader's emotional intelligence — a lifelong skill beyond the book",
        "Somatic awareness exercises create real physiological change, not just insight",
        "Especially transformative for men and high-performers who've been cut off from feeling",
        "Creates a practice the reader continues after the book — ongoing engagement",
        "Strong workbook companion potential — emotional exercises adapt to journal format",
      ],
    },
    {
      position: 4, label: "Warm",
      technique: "Reader addressed as 'you' in intimate tone — like a letter from a close friend",
      benefits: [
        "Attachment theory activation — reader feels securely 'held' by the text",
        "Reduces defensiveness — intimate tone bypasses intellectual resistance",
        "Highest read-through rates — readers don't want the 'conversation' to end",
        "Audiobook feels like a private therapy session — deep personal connection",
        "Strong for grief and healing topics where clinical distance would feel cold",
      ],
    },
    {
      position: 5, label: "Balanced",
      technique: "Emotional opening, logical middle, integrative close — each chapter a journey",
      benefits: [
        "Both heart and head readers feel served in every chapter",
        "Creates the most balanced reviews — 'moving AND practical' is the gold standard",
        "Works across all platforms — emotional hooks for social, logical depth for books",
        "Couples and friends with different styles can both love the same book",
        "Strongest cross-demographic appeal — no reader type is excluded",
      ],
    },
    {
      position: 6, label: "Reasoned",
      technique: "Evidence-supported storytelling — stories illustrate data, not the reverse",
      benefits: [
        "Skeptical readers stay engaged — their 'prove it' need is met consistently",
        "Creates authority through substance — reviews mention 'well-researched'",
        "Strong for B2B and corporate wellness markets where emotions need framing",
        "Content repurposes into presentations and white papers — business applications",
        "Attracts healthcare and therapy professionals as audience and referrers",
      ],
    },
    {
      position: 7, label: "Analytical",
      technique: "Structured arguments — claim, evidence, implication, action",
      benefits: [
        "Engineering and tech-industry readers finally find self-help they respect",
        "Creates clear, quotable frameworks that get shared in professional contexts",
        "Strong LinkedIn and professional social media clip potential",
        "Supports course and certification format — logical progression is built in",
        "Higher perceived value — readers feel they're getting tools, not just comfort",
      ],
    },
    {
      position: 8, label: "Logical",
      technique: "Data-forward chapters — numbers, studies, and metrics anchor every claim",
      benefits: [
        "Positions brand in the 'evidence-based' category — premium market positioning",
        "Readers use the data to convince friends and family — built-in evangelism tool",
        "Strong for corporate book-club adoption — 'this isn't woo-woo' positioning",
        "Creates excerpt content for health and science publications",
        "Male-skewing audience finally engages with emotional topics through logic door",
      ],
    },
    {
      position: 9, label: "Very Logical",
      technique: "Reader addressed as capable decision-maker — treated as intelligent adult",
      benefits: [
        "Respects reader's intelligence — builds loyalty through trust in their capacity",
        "Creates 'I recommend this to my smartest friends' word-of-mouth",
        "Strong for executive and leadership markets where emotional language feels weak",
        "Content translates to keynote speaking — logical structure plays well on stage",
        "Academic review potential — substantive enough to be cited in research",
      ],
    },
    {
      position: 10, label: "Ultra-Logical",
      technique: "Transformation framed as systematic skill acquisition with measurable outcomes",
      benefits: [
        "Appeals to quantified-self audience — the largest growth segment in wellness",
        "Creates trackable outcomes readers can measure — drives 5-star reviews",
        "Strong for app integration — logical frameworks translate to digital tools",
        "Corporate training and workshop adaptation is seamless",
        "Readers become practitioners — they teach the system to others, expanding reach",
      ],
    },
  ],
  spiritualPractical: [
    {
      position: 1, label: "Ultra-Spiritual",
      technique: "References to traditions, lineages, and sacred teachers woven throughout",
      benefits: [
        "Readers seeking meaning find it — existential anxiety addressed at the root",
        "Creates a sense of belonging to something ancient and larger than oneself",
        "Attracts the highest-spending demographic — Gen X wisdom seekers ($165M/yr)",
        "Book becomes a spiritual companion — readers keep it on nightstands for years",
        "Strong retreat and workshop tie-in — spiritual content creates immersive events",
      ],
    },
    {
      position: 2, label: "Very Spiritual",
      technique: "Sacred language: 'presence', 'awareness', 'witness', 'the great turning'",
      benefits: [
        "Creates transcendent reading experiences — readers report feeling 'transported'",
        "Poetry of language itself becomes healing — beauty as medicine",
        "Audiobook version works as guided meditation — dual-use content",
        "Strong international appeal — spiritual language translates across cultures",
        "Builds devoted following — spiritual readers are the most loyal audience segment",
      ],
    },
    {
      position: 3, label: "Spiritual",
      technique: "Exercises include meditation, contemplation, and silence-based practices",
      benefits: [
        "Develops reader's capacity for stillness — counterbalances digital overstimulation",
        "Meditation-based exercises create measurable neurological benefits",
        "Creates daily practice that extends engagement far beyond reading the book",
        "Strong for Gen Alpha — meditation skills are increasingly taught in schools",
        "Retreat-center and yoga-studio recommendation pipeline — institutional distribution",
      ],
    },
    {
      position: 4, label: "Meaning-First",
      technique: "Meaning-making is the primary goal — 'Why am I here?' addressed directly",
      benefits: [
        "Addresses the deepest human need — purpose and significance",
        "Readers in midlife transition find the existential grounding they're seeking",
        "Creates content that feels timeless rather than trend-dependent",
        "Strong for grief and loss topics — meaning-making is the ultimate healing",
        "Builds author platform as wisdom figure, not just expert — longer career arc",
      ],
    },
    {
      position: 5, label: "Balanced",
      technique: "Inner transformation connected to outer action — contemplation meets execution",
      benefits: [
        "Serves both spiritual seekers and practical doers in one book",
        "Creates the 'woo-meets-science' positioning that dominates bestseller lists",
        "Both meditation-loving and productivity-loving readers find their entry point",
        "Strongest word-of-mouth potential — recommended across different friend groups",
        "Platform flexibility — works for podcasts, courses, retreats, AND workshops",
      ],
    },
    {
      position: 6, label: "Grounded",
      technique: "Spiritual insights translated into daily habits and routines",
      benefits: [
        "Wisdom becomes usable — reader can start today, not 'when they're ready'",
        "Appeals to 'spiritual but practical' — the fastest-growing reader segment",
        "Creates content that works as 7-day challenges and 30-day programs",
        "Strong for social media — habit content performs exceptionally on all platforms",
        "Bridges the gap between self-help and spirituality sections in bookstores",
      ],
    },
    {
      position: 7, label: "Applied",
      technique: "Tool-first chapters — here's the technique, here's when to use it, here's why it works",
      benefits: [
        "Readers take immediate action — exercises feel doable, not abstract",
        "Strong for pocket-guide format — tools are reference-able and compact",
        "Creates the 'I actually did the exercises' reviews that drive sales",
        "Corporate wellness programs adopt tool-based content more readily",
        "Higher exercise completion — practical framing reduces resistance",
      ],
    },
    {
      position: 8, label: "Practical",
      technique: "Functional language: 'system', 'protocol', 'technique' — zero tradition references",
      benefits: [
        "Opens the secular wellness market — readers who avoid 'spiritual' labels",
        "Strong for healthcare referrals — clinical professionals recommend secular content",
        "Creates content that works in corporate and educational institutional settings",
        "Appeals to science-minded readers who want results without metaphysics",
        "TikTok and YouTube performance highest — practical content has broadest appeal",
      ],
    },
    {
      position: 9, label: "Very Practical",
      technique: "Behavior change is the primary goal — measurable outcomes tracked",
      benefits: [
        "Readers can prove the book worked — drives reviews with specific results",
        "Creates before/after narratives perfect for marketing and testimonials",
        "Strong for employer-sponsored wellness — ROI can be demonstrated",
        "App and digital product integration natural — tracking is built into the approach",
        "Health insurance and benefits platform partnerships become possible",
      ],
    },
    {
      position: 10, label: "Ultra-Practical",
      technique: "Pure protocol — actionable with measurable outcomes, every chapter a system to install",
      benefits: [
        "Maximum behavior change — no ambiguity about what success looks like",
        "Creates the strongest 'before and after' transformation testimonials",
        "Enterprise training and certification program ready out of the box",
        "Quantified results create press and media coverage opportunities",
        "Reader becomes a practitioner who teaches others — exponential reach",
      ],
    },
  ],
};

// ═══════════════════════════════════════════════════════════
// SHARED COMPONENTS
// ═══════════════════════════════════════════════════════════

function StepHero({ eyebrow, title, subtitle, helper }) {
  const { t } = useTranslation();
  return (
    <div className="mb-8">
      {eyebrow ? <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.2em] text-violet-600">{t("steps", eyebrow)}</p> : null}
      <h2 className="text-2xl font-extrabold tracking-tight text-white sm:text-3xl">{t("steps", title)}</h2>
      {subtitle ? <p className="mt-2 max-w-2xl text-sm leading-relaxed text-white">{t("steps", subtitle)}</p> : null}
      {helper ? <p className="mt-2 text-xs text-white">{t("steps", helper)}</p> : null}
    </div>
  );
}

function ProgressBar({ step, total, labels, t }) {
  const isComplete = step === total - 2; // step 7 ("Your Brand") only
  const pct = isComplete ? 100 : ((step + 1) / total) * 100;
  return (
    <div className="brand-studio-panel mb-6 px-5 py-4 sm:mb-8">
      {isComplete && (
        <p className="text-center text-3xl font-extrabold mb-3" style={{ color: '#d97706', fontFamily: 'Cormorant Garamond, serif' }}>
          {t("ui", "Congratulations — Your Brand Is 100% Configured!")}
        </p>
      )}
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-wider text-violet-600">
            {isComplete ? t("ui", "Complete") : t("ui", "Step {n} of {total}").replace("{n}", step + 1).replace("{total}", total)}
          </p>
          <p className="text-sm font-bold text-white">{labels[step]}</p>
        </div>
        <span className="text-xs font-semibold tabular-nums text-white">{Math.round(pct)}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-gray-100/90">
        <div
          className="h-full rounded-full bg-gradient-to-r from-violet-600 via-indigo-600 to-violet-700 transition-all duration-500 ease-out"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function ArchetypeCard({ arch, selected, onClick }) {
  const Icon = arch.icon;
  const isActive = selected === arch.id;
  const proofSrc = ARCHETYPE_PROOF_URL[arch.id];
  return (
    <button onClick={() => onClick(arch.id)} className={`relative text-left p-5 rounded-2xl border-2 transition-all duration-300 ${isActive ? `${arch.activeBorder} ${arch.bg} shadow-lg scale-[1.02]` : `border-gray-200 bg-white hover:border-gray-300 hover:shadow-md hover:-translate-y-0.5`}`}>
      {isActive && <div className="absolute top-3 right-3 z-10"><div className="w-6 h-6 rounded-full bg-gray-900 flex items-center justify-center"><Check size={14} className="text-white" /></div></div>}
      <div className={`mb-3 overflow-hidden rounded-xl border bg-gray-100 aspect-video ${isActive ? "ring-2 ring-offset-2 ring-gray-900 border-gray-900/20" : "border-gray-100"}`}>
        <img
          src={proofSrc}
          alt=""
          className={`w-full h-full object-cover transition-transform duration-300 ${isActive ? "scale-[1.04]" : ""}`}
          loading="lazy"
        />
      </div>
      <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${arch.gradient} flex items-center justify-center mb-3`}><Icon size={20} className="text-white" /></div>
      <h3 className="font-bold text-white text-sm">{arch.name}</h3>
      <p className="text-xs text-white mt-1 leading-relaxed">{arch.tagline}</p>
      <p className="text-[11px] text-white mt-2 leading-relaxed italic">{arch.visionVibe}</p>
      <div className="flex gap-1.5 mt-3 flex-wrap">
        {arch.tags.map((t) => <span key={t} className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${isActive ? 'bg-white/70 text-white' : 'bg-gray-100 text-white'}`}>{t}</span>)}
      </div>
    </button>
  );
}

function PersonaCard({ persona, selected, onClick }) {
  const isActive = selected === persona.id;
  const proofSrc = PERSONA_PROOF_URL[persona.id];
  return (
    <button onClick={() => onClick(persona.id)} className={`text-left p-4 rounded-xl border-2 transition-all duration-200 w-full ${isActive ? "border-gray-900 bg-gray-50 shadow-md scale-[1.01]" : "border-gray-200 bg-white hover:border-gray-300"}`}>
      <div className={`mb-2 overflow-hidden rounded-lg border bg-gray-100 ${isActive ? "ring-2 ring-offset-1 ring-gray-900 border-gray-900/20" : "border-gray-100"}`}>
        <img
          src={proofSrc}
          alt=""
          className={`w-3/4 mx-auto object-contain transition-transform duration-200 ${isActive ? "scale-105" : ""}`}
          loading="lazy"
        />
      </div>
      <div className="flex items-center gap-2">
        <span className="text-lg">{persona.emoji}</span>
        <h4 className="font-bold text-sm text-white flex-1">{persona.label}</h4>
        {isActive && <div className="w-5 h-5 rounded-full bg-gray-900 flex items-center justify-center flex-shrink-0"><Check size={12} className="text-white" /></div>}
      </div>
    </button>
  );
}

function MomentCard({ moment, selected, onClick }) {
  const isActive = selected === moment.id;
  const proofSrc = MOMENT_PROOF_URL[moment.id];
  return (
    <button onClick={() => onClick(moment.id)} className={`text-left p-4 rounded-xl border-2 transition-all duration-200 w-full ${isActive ? "border-gray-900 bg-gray-50 shadow-md scale-[1.01]" : "border-gray-200 bg-white hover:border-gray-300"}`}>
      <div className={`mb-2 overflow-hidden rounded-lg border bg-gray-100 aspect-video ${isActive ? "ring-2 ring-offset-1 ring-gray-900 border-gray-900/20" : "border-gray-100"}`}>
        <img
          src={proofSrc}
          alt=""
          className={`w-full h-full object-cover transition-transform duration-200 ${isActive ? "scale-105" : ""}`}
          loading="lazy"
        />
      </div>
      <div className="flex items-start gap-3">
        <span className="text-2xl">{moment.emoji}</span>
        <div className="flex-1">
          <h4 className="font-bold text-sm text-white">{moment.label}</h4>
          <p className="text-[11px] text-white italic">{moment.scene}</p>
          {isActive && <p className="text-[11px] text-indigo-600 mt-1.5">{moment.hookStyle}</p>}
        </div>
        {isActive && <div className="w-5 h-5 rounded-full bg-gray-900 flex items-center justify-center flex-shrink-0"><Check size={12} className="text-white" /></div>}
      </div>
    </button>
  );
}

// Voice Tone Interactive Graphs — respond to slider position (1-10)
function PulseWaveGraph({ position, color }) {
  const w = 240, h = 70;
  const freq = 0.5 + (position / 10) * 4;
  const amp = 25 - (position / 10) * 12;
  const smoothness = 1 - (position / 10) * 0.6;
  const lines = [];
  for (let row = 0; row < 3; row++) {
    const pts = [];
    for (let x = 0; x <= w; x += 2) {
      const phase = row * 1.2;
      const y = h / 2 + Math.sin((x / w) * Math.PI * freq + phase) * (amp - row * 4) * smoothness + (row - 1) * 5;
      pts.push(`${x},${y.toFixed(1)}`);
    }
    lines.push(pts.join(" "));
  }
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-20">
      <defs><linearGradient id={`pw-${color.replace('#','')}`} x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stopColor={color} stopOpacity="0.1"/><stop offset="50%" stopColor={color} stopOpacity="0.8"/><stop offset="100%" stopColor={color} stopOpacity="0.1"/></linearGradient></defs>
      {lines.map((pts, i) => <polyline key={i} fill="none" stroke={`url(#pw-${color.replace('#','')})`} strokeWidth={3 - i * 0.8} points={pts} opacity={1 - i * 0.25} />)}
      <circle cx={120} cy={h / 2} r={4 + position * 0.5} fill={color} opacity="0.5"><animate attributeName="r" values={`${4 + position * 0.5};${6 + position * 0.5};${4 + position * 0.5}`} dur="2s" repeatCount="indefinite" /></circle>
    </svg>
  );
}

function SpectrumBarGraph({ position, color }) {
  const barCount = 12;
  return (
    <svg viewBox="0 0 240 70" className="w-full h-20">
      {Array.from({ length: barCount }).map((_, i) => {
        const center = ((position - 1) / 9) * barCount;
        const dist = Math.abs(i - center);
        const h = Math.max(8, 55 * Math.exp(-dist * dist / (2 + position * 0.5)));
        return (
          <g key={i}>
            <rect x={i * 20 + 2} y={70 - h} width="16" height={h} rx="4" fill={color} opacity={Math.max(0.15, 1 - dist / (barCount / 2))} />
            <rect x={i * 20 + 5} y={70 - h + 2} width="10" height={Math.max(0, h - 8)} rx="2" fill="white" opacity="0.15" />
          </g>
        );
      })}
    </svg>
  );
}

function EmotionRadarGraph({ position, color }) {
  const sides = 6;
  const cx = 120, cy = 35, r = 30;
  const labels = ["Feel", "Think", "Do", "Share", "Trust", "Return"];
  const outerPts = [], innerPts = [];
  for (let i = 0; i < sides; i++) {
    const angle = (Math.PI * 2 * i) / sides - Math.PI / 2;
    outerPts.push(`${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`);
    const val = 0.3 + Math.sin(i * 1.8 + position * 0.3) * 0.3 + (position / 10) * 0.4;
    innerPts.push(`${cx + r * val * Math.cos(angle)},${cy + r * val * Math.sin(angle)}`);
  }
  return (
    <svg viewBox="0 0 240 70" className="w-full h-20">
      <polygon fill="none" stroke="#e5e7eb" strokeWidth="1" points={outerPts.join(" ")} />
      <polygon fill="none" stroke="#e5e7eb" strokeWidth="0.5" strokeDasharray="2" points={outerPts.map((p, i) => {
        const angle = (Math.PI * 2 * i) / sides - Math.PI / 2;
        return `${cx + r * 0.5 * Math.cos(angle)},${cy + r * 0.5 * Math.sin(angle)}`;
      }).join(" ")} />
      <polygon fill={color} fillOpacity="0.15" stroke={color} strokeWidth="2" points={innerPts.join(" ")} />
      {labels.map((l, i) => {
        const angle = (Math.PI * 2 * i) / sides - Math.PI / 2;
        return <text key={l} x={cx + (r + 10) * Math.cos(angle)} y={cy + (r + 10) * Math.sin(angle)} textAnchor="middle" dominantBaseline="middle" fontSize="7" fill="#9ca3af">{l}</text>;
      })}
    </svg>
  );
}

function EnergyGaugeGraph({ position, color }) {
  const cx = 120, cy = 50, r = 40;
  const startAngle = -160, endAngle = -20;
  const sweepAngle = (position / 10) * (endAngle - startAngle);
  const tickCount = 10;
  return (
    <svg viewBox="0 0 240 70" className="w-full h-20">
      {Array.from({ length: tickCount + 1 }).map((_, i) => {
        const angle = ((startAngle + (endAngle - startAngle) * (i / tickCount)) * Math.PI) / 180;
        const x1 = cx + (r - 3) * Math.cos(angle), y1 = cy + (r - 3) * Math.sin(angle);
        const x2 = cx + r * Math.cos(angle), y2 = cy + r * Math.sin(angle);
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke={i <= position ? color : "#e5e7eb"} strokeWidth="2" strokeLinecap="round" />;
      })}
      <path d={`M ${cx + (r - 8) * Math.cos((startAngle * Math.PI) / 180)} ${cy + (r - 8) * Math.sin((startAngle * Math.PI) / 180)} A ${r - 8} ${r - 8} 0 0 1 ${cx + (r - 8) * Math.cos(((startAngle + sweepAngle) * Math.PI) / 180)} ${cy + (r - 8) * Math.sin(((startAngle + sweepAngle) * Math.PI) / 180)}`} fill="none" stroke={color} strokeWidth="5" strokeLinecap="round" />
      <circle cx={cx} cy={cy} r="3" fill={color} />
      {(() => { const a = ((startAngle + sweepAngle) * Math.PI) / 180; return <line x1={cx} y1={cy} x2={cx + 22 * Math.cos(a)} y2={cy + 22 * Math.sin(a)} stroke={color} strokeWidth="2" strokeLinecap="round" />; })()}
    </svg>
  );
}

// ═══════════════════════════════════════════════════════════
// SELECTION FEEDBACK DATA — what each choice does + emotional benefit
// ═══════════════════════════════════════════════════════════

const SELECTION_FEEDBACK = {
  archetypes: {
    nervous_system: {
      systemEffect: "Sets prose to breath-aware pacing, somatic exercises, and regulation-first structure across all titles",
      emotionalBenefit: "Your readers' nervous systems downregulate from the first paragraph. Content functions as a co-regulation tool — reducing cortisol, slowing heart rate, and giving permission to rest. Readers report feeling 'held' by the writing itself.",
    },
    identity_direction: {
      systemEffect: "Activates forward-moving prose, honest-audit exercises, and anti-comparison hook strategy",
      emotionalBenefit: "Readers stop scrolling and start choosing. This transforms the paralysis of 'I don't know what I'm doing' into momentum. Each chapter rebuilds identity through small, brave decisions — counteracting the shame of feeling behind.",
    },
    emotional_healing: {
      systemEffect: "Enables tenderness-first language, witness-based exercises, and grief-literate content pacing",
      emotionalBenefit: "Readers feel seen, not fixed. This meets grief and pain with presence — no toxic positivity, no timelines, no 'you should be over this.' It fills the role of the compassionate witness many readers never had.",
    },
    performance_focus: {
      systemEffect: "Engages action-first prose, protocol-based exercises, and noise-cutting hook strategy",
      emotionalBenefit: "Readers cut through information overload and take their first real action in weeks. This reduces decision fatigue, builds systems that run on structure instead of willpower, and restores the feeling of being in control.",
    },
    spiritual_awakening: {
      systemEffect: "Activates contemplative prose layers, gap-awareness exercises, and meaning-seeking hook strategy",
      emotionalBenefit: "Readers discover that what they've been chasing has been inside them all along. This creates space for depth in a world of surfaces — meeting spiritual seekers where intellectualized self-help couldn't reach.",
    },
  },
  personas: {
    burned_out_pro: { systemEffect: "Tunes titles around exhaustion hooks, 'Sunday dread' narratives, and recovery-without-quitting framing", emotionalBenefit: "Content reaches people in survival mode — no guilt, no 'just try harder.' Your brand becomes the first voice that says 'you're not lazy, you're depleted' and actually means it." },
    gen_z_seeker: { systemEffect: "Optimizes for short-form hooks, TikTok-native language, anti-hustle tone, and scroll-stopping openings", emotionalBenefit: "Your brand meets Gen Z in their native language — authenticity-first. You become the trusted voice in a sea of performative wellness, offering real tools without the cringe." },
    gen_alpha: { systemEffect: "Activates manga-first format, visual storytelling, gamified exercises, and guardian-safe content filters", emotionalBenefit: "You're building content for the first generation with emotional vocabulary from childhood. Visual formats give them tools their parents never had — age-appropriate and genuinely helpful." },
    grief_carrier: { systemEffect: "Sets permission-giving language, soft CTAs, no toxic positivity, and witness-based exercise structure", emotionalBenefit: "Your brand becomes a companion through the unnamed grief — the kind nobody prepared them for. No fixing, no timelines. Just presence and the radical permission to not be okay." },
    anxious_achiever: { systemEffect: "Bridges high-performance framing with vulnerability backdoors, nervous system support, and imposter syndrome hooks", emotionalBenefit: "You reach people who look fine outside and are crumbling inside. Your brand bridges achievement language with vulnerability — the backdoor to healing that achievers will actually walk through." },
    spiritual_returner: { systemEffect: "Activates dense contemplative prose, tradition-aware references, anti-guru positioning, and depth-first hooks", emotionalBenefit: "Your brand speaks to people who've tried everything and are exhausted by shallow answers. Dense, authentic content that respects their intelligence and meets their depth." },
    new_parent: { systemEffect: "Prioritizes micro-format delivery, guilt-free framing, quick-tool exercises, and naptime-length content", emotionalBenefit: "Your brand reaches parents in the stolen moments — 3AM feeds, naptime scrolls. Micro-format tools with zero guilt help them reclaim identity without adding to their overwhelm." },
  },
  moments: {
    "2am_overthinking": { systemEffect: "Opens with sensation-based language, validates the spiral, offers immediate grounding tool within first 30 seconds", emotionalBenefit: "Content catches them in the exact moment of vulnerability — lying awake, phone glowing, mind racing. The hook lands because it describes what they're physically feeling right now." },
    "after_breakup": { systemEffect: "Names the specific numbness flavor, avoids advice-giving, leads with somatic awareness of loss", emotionalBenefit: "You meet them in the numbness nobody talks about — not the crying kind, but the food-has-no-taste kind. Your brand names what they can't articulate, and that alone begins healing." },
    "burnout_cant_quit": { systemEffect: "Catches the mask-on moment, speaks to public/private gap, frames recovery as a skill not a luxury", emotionalBenefit: "You speak to the moment between the bathroom mirror and the mask going back on. Content validates the gap between who they perform and who they are — permission to stop pretending." },
    "feeling_behind": { systemEffect: "Targets comparison-scrolling behavior, reframes 'behind' as construction, turns phone into trigger object", emotionalBenefit: "You interrupt the comparison scroll with truth: they're not behind, they're building. The phone itself becomes the trigger object, transforming mindless scrolling into honest self-reflection." },
    "panic_spike": { systemEffect: "Physical-first language, names body sensations before emotions, immediate somatic intervention within 10 seconds", emotionalBenefit: "Content uses body-first language when the mind has left the building. During panic, the body needs to hear 'I see you' before the mind can process anything. This saves real people in real moments." },
    "sunday_dread": { systemEffect: "Taps weekly anxiety cycle, validates sinking feeling, reframes Sunday as reclamation rather than countdown", emotionalBenefit: "You name the weekly dread that millions feel but never articulate. Your brand reclaims Sunday from anxiety — transforming the sinking feeling into a ritual of preparation and self-compassion." },
  },
  visualStyles: {
    calm_minimal: { systemEffect: "Generates covers with vast white space, soft ink wash, zen aesthetic, muted palettes", emotionalBenefit: "Readers experience visual relief — white space signals 'you can breathe here.' Covers feel like a meditation before the book is even opened. Reduces visual anxiety for overstimulated audiences." },
    dark_intense: { systemEffect: "Generates covers with deep indigo/black, dramatic lighting, cinematic grain, high contrast", emotionalBenefit: "Readers feel the gravity of their own transformation. Dark aesthetics signal depth — this isn't gentle wellness, it's real work. Attracts readers who distrust soft-looking self-help." },
    earthy_organic: { systemEffect: "Generates covers with handmade textures, botanical elements, warm amber tones, artisan aesthetic", emotionalBenefit: "Readers feel grounded before they read a word. Natural textures trigger biophilic calm — the brain interprets organic visuals as 'safe.' Powerful for somatic and nature-based healing." },
    bold_modern: { systemEffect: "Generates covers with stark contrast, oversized typography, red geometric accents, Swiss design grid", emotionalBenefit: "Readers feel energized and decisive. Bold visuals cut through shelf noise and scroll fatigue. Signals 'this is different' — attracting action-oriented readers tired of pastel wellness." },
    premium_soft: { systemEffect: "Generates covers with geometric structure, precise typography hierarchy, gold accent lines, disciplined luxury palettes", emotionalBenefit: "Readers feel they are holding something authoritative and intentional. Geometric premium signals craft and clarity — attracting buyers who want transformation with editorial credibility." },
    sacred_cosmic: { systemEffect: "Generates mysterious atmospheric covers — deep blues and violets, subtle light, contemplative depth without horror", emotionalBenefit: "Readers feel curiosity and inward expansion. Mysterious visuals invite depth seekers without fantasy overload — magnetic on shelf and thumbnail." },
  },
  formats: {
    manga: { systemEffect: "Catalog planner prioritizes illustrated panels, short-form audiobooks (15-30 min), visual storytelling across all channels", emotionalBenefit: "Visual-first readers process emotions through images faster than text. Manga reduces reading anxiety, engages Gen Z/Alpha natively, and makes complex psychological concepts accessible through story." },
    book: { systemEffect: "Catalog planner prioritizes full-length narratives, deep programs, comprehensive workbooks, long-form audiobooks (3-8 hrs)", emotionalBenefit: "Deep readers crave immersion — long-form gives them permission to slow down and go deep. Full-length books become companions, building sustained attention that drives lasting transformation." },
  },
};

function SelectionFeedback({ systemEffect, emotionalBenefit, color = "#6366f1" }) {
  if (!systemEffect && !emotionalBenefit) return null;
  return (
    <div className="mt-4 rounded-xl border overflow-hidden" style={{ borderColor: color + '30' }}>
      <div className="px-4 py-2.5 flex items-center gap-2" style={{ backgroundColor: color + '08' }}>
        <Sparkles size={13} style={{ color }} />
        <span className="text-[11px] font-bold" style={{ color }}>What This Activates</span>
      </div>
      <div className="px-4 py-3 bg-white">
        <div className="flex items-start gap-2 mb-2.5">
          <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: color + '15' }}>
            <Zap size={10} style={{ color }} />
          </div>
          <div>
            <div className="text-[9px] font-bold uppercase text-white mb-0.5">In the System</div>
            <p className="text-[11px] text-white leading-relaxed">{systemEffect}</p>
          </div>
        </div>
        <div className="flex items-start gap-2">
          <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: color + '15' }}>
            <Heart size={10} style={{ color }} />
          </div>
          <div>
            <div className="text-[9px] font-bold uppercase text-white mb-0.5">For Your Reader</div>
            <p className="text-[11px] text-white leading-relaxed font-medium">{emotionalBenefit}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function WhatThisChanges({ items, label }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-xl border border-gray-200 bg-gray-50 overflow-hidden">
      <button onClick={() => setOpen(!open)} className="w-full px-4 py-2.5 flex items-center gap-2 text-left">
        <Sparkles size={14} className="text-white" />
        <span className="text-xs font-bold text-white">{label || "What this changes"}</span>
        <ChevronRight size={14} className={`text-white ml-auto transition-transform ${open ? "rotate-90" : ""}`} />
      </button>
      {open && (
        <div className="px-4 pb-3 grid grid-cols-2 gap-1.5">
          {items.map((item, i) => <div key={i} className="flex items-center gap-1.5"><div className="w-1 h-1 rounded-full bg-gray-400" /><span className="text-[11px] text-white">{item}</span></div>)}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// PERSONA IMPACT PANEL (Right side)
// ═══════════════════════════════════════════════════════════

function PersonaImpactPanel({ state, step = 0, i18n = {} }) {
  const { tArchetypes: _A = ARCHETYPES, tPersonas: _P = PERSONAS, tMoments: _M = MOMENTS, tVisualStyles: _V = VISUAL_STYLES, tProven: _PR = PROVEN, tSelectionFeedback: _SF = SELECTION_FEEDBACK, tEmotionCategories: _EC = EMOTION_CATEGORIES, tAngleFeedback: _AF = ANGLE_FEEDBACK, t: _t = (c, k) => k } = i18n;
  const arch = _A.find((a) => a.id === state.archetype);
  const persona = _P.find((p) => p.id === state.persona);
  const moment = _M.find((m) => m.id === state.moment);
  const proven = _PR[state.archetype] || _PR.nervous_system;
  const visual = _V.find((v) => v.id === state.visualStyle);
  const completeness = step >= 7 ? 100 : Math.round(((step + 1) / 9) * 100);

  return (
    <div className="space-y-4">
      <div className="text-center">
        <div className="relative w-20 h-20 mx-auto mb-2">
          <svg viewBox="0 0 80 80" className="w-full h-full -rotate-90">
            <circle cx="40" cy="40" r="34" fill="none" stroke="#f3f4f6" strokeWidth="6" />
            <circle cx="40" cy="40" r="34" fill="none" stroke="#e67e22" strokeWidth="6" strokeLinecap="round" strokeDasharray={`${completeness * 2.136} 213.6`} />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center"><span className="text-lg font-black text-white">{completeness}%</span></div>
        </div>
        <p className="text-[10px] text-white font-semibold uppercase">{_t("ui", "Brand Defined")}</p>
      </div>
      {step === 0 && arch && (
        <div className={`rounded-xl p-3 ${arch.bg} border ${arch.border}`}>
          <div className="flex items-center gap-2">
            {(() => { const I = arch.icon; return <div className={`w-7 h-7 rounded-lg bg-gradient-to-br ${arch.gradient} flex items-center justify-center`}><I size={14} className="text-white" /></div>; })()}
            <div><div className="font-bold text-xs text-white">{arch.name}</div><div className="text-[10px] text-white">{arch.tagline}</div></div>
          </div>
        </div>
      )}
      {step === 0 && arch && _SF.archetypes[arch.id] && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-violet-500" />
            <span className="text-xs font-bold text-white">What This Activates</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>In the System:</strong> {_SF.archetypes[arch.id].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>For Your Reader:</strong> {_SF.archetypes[arch.id].emotionalBenefit}</div>
        </div>
      )}
      {step === 1 && persona && _SF.personas[persona.id] && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-violet-500" />
            <span className="text-xs font-bold text-white">What This Activates</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>In the System:</strong> {_SF.personas[persona.id].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>For Your Reader:</strong> {_SF.personas[persona.id].emotionalBenefit}</div>
        </div>
      )}
      {step === 1 && persona && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-1">Primary Reader</div>
          <div className="flex items-center gap-2"><span className="text-lg">{persona.emoji}</span><div><div className="text-xs font-bold text-white">{persona.label}</div></div></div>
        </div>
      )}
      {step === 1 && persona && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-2">Reader Profile</div>
          <div className="text-[10px] text-white leading-tight mb-1.5">{persona.desc}</div>
          <div className="text-[10px] text-white leading-tight mb-1.5"><strong>Needs:</strong> {persona.needs}</div>
          <div className="text-[10px] text-white leading-tight"><strong>Impact:</strong> {persona.impact}</div>
        </div>
      )}
      {step === 2 && moment && _SF.moments[moment.id] && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-violet-500" />
            <span className="text-xs font-bold text-white">What This Activates</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>In the System:</strong> {_SF.moments[moment.id].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>For Your Reader:</strong> {_SF.moments[moment.id].emotionalBenefit}</div>
        </div>
      )}
      {step >= 3 && Object.keys(state.voiceSettings || {}).length > 0 && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-2">Voice Profile</div>
          {VOICE_SLIDERS.map((s) => { const val = state.voiceSettings?.[s.id] ?? s.default; return (
            <div key={s.id} className="flex items-center gap-2 mb-1"><span className="text-[9px] text-white w-14">{s.left}</span><div className="flex-1 h-1.5 bg-gray-100 rounded-full"><div className="h-full bg-gray-700 rounded-full transition-all" style={{ width: `${val}%` }} /></div><span className="text-[9px] text-white w-14 text-right">{s.right}</span></div>
          ); })}
        </div>
      )}
      {step === 4 && visual && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-2">Visual Style</div>
          <div className="flex gap-1.5 mb-1.5">{visual.palette.map((c, i) => <div key={i} className="w-8 h-8 rounded-lg shadow-sm" style={{ backgroundColor: c }} />)}</div>
          <div className="text-[10px] text-white font-medium">{visual.label}</div>
        </div>
      )}
      {step === 4 && state.visualStyle && _SF.visualStyles[state.visualStyle] && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-violet-500" />
            <span className="text-xs font-bold text-white">What This Activates</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>In the System:</strong> {_SF.visualStyles[state.visualStyle].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>For Your Reader:</strong> {_SF.visualStyles[state.visualStyle].emotionalBenefit}</div>
        </div>
      )}
      {step === 6 && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-3">
            <Compass size={14} className="text-indigo-500" />
            <span className="text-xs font-bold text-white">Content Angles</span>
          </div>
          <div className="space-y-2">
            {TOPIC_CATEGORIES.map((cat) => {
              const selectedTagId = (state.topicTags || []).find(t => cat.tags.some(ct => ct.id === t));
              const selectedTag = selectedTagId ? cat.tags.find(ct => ct.id === selectedTagId) : null;
              const angleInfo = selectedTag ? _AF[selectedTag.angle] : null;
              return (
                <div key={cat.label} className="rounded-lg p-2.5 border transition-all duration-200" style={{ borderColor: selectedTag ? cat.color + '40' : '#e5e7eb', backgroundColor: selectedTag ? cat.color + '08' : '#fff' }}>
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className="text-xs">{cat.icon}</span>
                    <span className="text-[10px] font-bold text-white">{cat.label}</span>
                  </div>
                  {selectedTag ? (
                    <>
                      <div className="flex items-center gap-1 mb-1">
                        <span className="text-[9px]">{angleInfo?.icon}</span>
                        <span className="text-[9px] font-bold" style={{ color: cat.color }}>{angleInfo?.label}: {selectedTagId.replace(/-/g, " ")}</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <div className="w-1 h-1 rounded-full mt-1.5 flex-shrink-0" style={{ backgroundColor: cat.color }} />
                        <p className="text-[9px] text-white leading-relaxed">{selectedTag.bullet}</p>
                      </div>
                    </>
                  ) : (
                    <p className="text-[9px] text-white/70 italic">Pick a topic...</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
      {step === 7 && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-3">
            <Compass size={14} className="text-violet-500" />
            <span className="text-xs font-bold text-white">Jump to Section</span>
          </div>
          <div className="space-y-0.5">
            {[
              { id: "rev-category", label: "True Category", icon: "🎯" },
              { id: "rev-voice", label: "Voice Signature", icon: "🎙️" },
              { id: "rev-positioning", label: "Positioning Map", icon: "📍" },
              { id: "rev-visual", label: "Visual Identity", icon: "🎨" },
              { id: "rev-emotion", label: "Emotional Staircase", icon: "📈" },
              { id: "rev-topics", label: "Topic Strategy", icon: "🗂️" },
              { id: "rev-engine", label: "Content Engine", icon: "⚙️" },
              { id: "rev-loop", label: "Advantage Loop", icon: "🔄" },
              { id: "rev-journey", label: "Reader Journey", icon: "🚶" },
              { id: "rev-synergy", label: "Voice × Topic", icon: "🔗" },
              { id: "rev-radar", label: "Brand Strength", icon: "📊" },
              { id: "rev-synthesis", label: "Synthesis", icon: "✨" },
            ].map(s => (
              <button
                key={s.id}
                onClick={() => document.getElementById(s.id)?.scrollIntoView({ behavior: "smooth", block: "start" })}
                className="flex items-center gap-2 w-full text-left rounded-lg px-2 py-1.5 text-[10px] text-white hover:bg-white hover:shadow-sm transition-all"
              >
                <span className="text-xs">{s.icon}</span>
                <span>{s.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}
      {step === 5 && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Heart size={14} className="text-rose-500" />
            <span className="text-xs font-bold text-white">Emotional Profile</span>
          </div>
          <div className="bg-white rounded-lg border border-gray-100 p-3 mb-3">
            <svg viewBox="0 0 240 140" className="w-full h-40">
              {(() => {
                const sides = 5;
                const cx = 120, cy = 70, r = 55;
                const catLabels = _EC.map(c => c.icon + " " + c.name.split(" ")[0]);
                const emos = state.emotions || [];
                const outerPts = [], innerPts = [];
                for (let i = 0; i < sides; i++) {
                  const angle = (Math.PI * 2 * i) / sides - Math.PI / 2;
                  outerPts.push(`${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`);
                  const cat = _EC[i];
                  const selected = emos.find(e => cat.items.includes(e));
                  const itemIdx = selected ? cat.items.indexOf(selected) : -1;
                  const val = selected ? 0.4 + (itemIdx + 1) * 0.2 : 0.15;
                  innerPts.push(`${cx + r * val * Math.cos(angle)},${cy + r * val * Math.sin(angle)}`);
                }
                return (<>
                  <polygon fill="none" stroke="#e5e7eb" strokeWidth="1" points={outerPts.join(" ")} />
                  <polygon fill="none" stroke="#e5e7eb" strokeWidth="0.5" strokeDasharray="3" points={outerPts.map((_, i) => { const a = (Math.PI * 2 * i) / sides - Math.PI / 2; return `${cx + r * 0.5 * Math.cos(a)},${cy + r * 0.5 * Math.sin(a)}`; }).join(" ")} />
                  <polygon fill="#f43f5e" fillOpacity="0.15" stroke="#f43f5e" strokeWidth="2" points={innerPts.join(" ")} />
                  {catLabels.map((l, i) => { const a = (Math.PI * 2 * i) / sides - Math.PI / 2; return <text key={l} x={cx + (r + 14) * Math.cos(a)} y={cy + (r + 14) * Math.sin(a)} textAnchor="middle" dominantBaseline="middle" fontSize="8" fill="#9ca3af">{l}</text>; })}
                </>);
              })()}
            </svg>
          </div>
          <div className="space-y-2 mt-2">
            {(state.emotions || []).map((e) => {
              const cat = _EC.find(c => c.items.includes(e));
              return (
                <div key={e} className="bg-white rounded-lg p-2 border border-gray-100">
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className="text-xs">{cat?.icon}</span>
                    <span className="text-[10px] font-bold text-white">{e}</span>
                  </div>
                  {cat?.impacts?.[e] && (
                    <div className="flex items-start gap-1.5">
                      <div className="w-1 h-1 rounded-full mt-1.5 flex-shrink-0" style={{ backgroundColor: cat.color }} />
                      <p className="text-[9px] text-white leading-relaxed">{cat.impacts[e]}</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// WIZARD STEPS (11 steps)
// ═══════════════════════════════════════════════════════════

function Step1Archetype({ state, update, i18n = {} }) {
  const { tArchetypes: _A = ARCHETYPES } = i18n;
  return (
    <div>
      <StepHero
        eyebrow="Foundation"
        title="Choose your emotional world"
        subtitle="Your archetype is the feeling readers associate with you — across prose, covers, video, and social. Pick the worldview that matches how you want to show up."
        helper="Each card includes a short vision of the world your brand invites readers into."
      />
      <div className="mb-6 rounded-xl border border-indigo-100/80 bg-indigo-50/60 px-4 py-3 backdrop-blur-sm">
        <p className="text-xs font-medium text-indigo-900">{useTranslation().t("steps", "This is the highest-leverage choice in the studio — everything else builds on the emotional territory you choose here.")}</p>
      </div>
      <div className="grid grid-cols-1 gap-3">
        {_A.map((arch) => <ArchetypeCard key={arch.id} arch={arch} selected={state.archetype} onClick={(id) => update({ archetype: id })} />)}
      </div>
    </div>
  );
}

function Step2PrimaryReader({ state, update, i18n = {} }) {
  const { tPersonas: _P = PERSONAS } = i18n;
  const laneChoices = [
    { key: "self_help", label: "Self-help books", hint: "Long-form titles and programs for deep transformation." },
    { key: "manga", label: "Manga / visual stories", hint: "Panel-first storytelling for youth and visual-native readers." },
    { key: "pearl_news", label: "Pearl News editorial", hint: "Article-led civic and narrative explainers." },
    { key: "tools", label: "Breathwork / tools", hint: "Utility-first experiences and practical support flows." },
    { key: "hybrid", label: "Hybrid lane", hint: "Blend book, manga, and editorial proof in one path." },
  ];
  const marketChoices = [
    { key: "us", label: "United States (en-US)", hint: "Primary launch market." },
    { key: "japan", label: "Japan (ja-JP)", hint: "Localized visual and wording expectations." },
    { key: "taiwan", label: "Taiwan (zh-TW)", hint: "Traditional Chinese market alignment." },
  ];

  const selectedLane = state.onboardingLane || "self_help";
  const selectedMarket = state.onboardingMarket || "us";

  const selectedFormatFocus = selectedLane === "manga" ? "manga" : state.formatFocus;

  return (
    <div>
      <StepHero
        eyebrow="Audience"
        title="Primary reader"
        subtitle="Every strong brand has a protagonist — the reader you lead with. Your catalog still reaches every segment; this choice shapes voice, covers, and hooks first."
      />
      <div className="mb-6 rounded-xl border border-blue-100/80 bg-blue-50/50 p-4 backdrop-blur-sm">
        <p className="text-xs leading-relaxed text-blue-900">
          {useTranslation().t("steps", "Still reaching everyone. We tune titles, packaging, and exercises to this reader first, then adapt across your archetype's other segments.")}
        </p>
      </div>
      <div className="grid grid-cols-1 gap-2.5">
        {_P.map((p) => <PersonaCard key={p.id} persona={p} selected={state.persona} onClick={(id) => update({ persona: id })} />)}
      </div>
    </div>
  );
}

function Step3TriggerMoment({ state, update, i18n = {} }) {
  const { tMoments: _M = MOMENTS } = i18n;
  return (
    <div>
      <StepHero
        eyebrow="Hook"
        title="The moment they reach for you"
        subtitle="Pick the scene where your reader is most open — titles, covers, and social hooks follow from here."
      />
      <details open className="mb-5 rounded-xl border border-amber-100/90 bg-amber-50/40 px-4 py-2 text-xs text-amber-900 backdrop-blur-sm open:pb-3">
        <summary className="cursor-pointer font-semibold text-amber-900/90 outline-none">Why this matters</summary>
        <p className="mt-2 leading-relaxed text-amber-900/85">
          {useTranslation().t("steps", "Strong brands speak to a moment, not only a demographic. This choice steers first lines, cover promise, and scroll-stopping hooks.")}
        </p>
      </details>
      <div className="grid grid-cols-1 gap-2.5">
        {_M.map((m) => <MomentCard key={m.id} moment={m} selected={state.moment} onClick={(id) => update({ moment: id })} />)}
      </div>
    </div>
  );
}

const VOICE_5_STOPS = [1, 3, 6, 8, 10];
const VOICE_5_VALUES = [0, 25, 50, 75, 100];
const VOICE_AUDIO_SRC = {
  gentleDirect: { 1: "/onboarding/proof/wizard/p1.mp3", 3: "/onboarding/proof/wizard/p3.mp3", 6: "/onboarding/proof/wizard/p6.mp3", 8: "/onboarding/proof/wizard/p8.mp3", 10: "/onboarding/proof/wizard/p10.mp3" },
  simpleDeep: { 1: "/onboarding/proof/wizard/sd_p1.mp3", 3: "/onboarding/proof/wizard/sd_p3.mp3", 6: "/onboarding/proof/wizard/sd_p6.mp3", 8: "/onboarding/proof/wizard/sd_p8.mp3", 10: "/onboarding/proof/wizard/sd_p10.mp3" },
  emotionalLogical: { 1: "/onboarding/proof/wizard/el_p1.mp3", 3: "/onboarding/proof/wizard/el_p3.mp3", 6: "/onboarding/proof/wizard/el_p6.mp3", 8: "/onboarding/proof/wizard/el_p8.mp3", 10: "/onboarding/proof/wizard/el_p10.mp3" },
  spiritualPractical: { 1: "/onboarding/proof/wizard/sp_p1.mp3", 3: "/onboarding/proof/wizard/sp_p3.mp3", 6: "/onboarding/proof/wizard/sp_p6.mp3", 8: "/onboarding/proof/wizard/sp_p8.mp3", 10: "/onboarding/proof/wizard/sp_p10.mp3" },
};
const VOICE_AUDIO_SRC_JA = {
  gentleDirect: { 1: "/onboarding/proof/wizard/ja_p1.mp3", 3: "/onboarding/proof/wizard/ja_p3.mp3", 6: "/onboarding/proof/wizard/ja_p6.mp3", 8: "/onboarding/proof/wizard/ja_p8.mp3", 10: "/onboarding/proof/wizard/ja_p10.mp3" },
  simpleDeep: { 1: "/onboarding/proof/wizard/ja_sd_p1.mp3", 3: "/onboarding/proof/wizard/ja_sd_p3.mp3", 6: "/onboarding/proof/wizard/ja_sd_p6.mp3", 8: "/onboarding/proof/wizard/ja_sd_p8.mp3", 10: "/onboarding/proof/wizard/ja_sd_p10.mp3" },
  emotionalLogical: { 1: "/onboarding/proof/wizard/ja_el_p1.mp3", 3: "/onboarding/proof/wizard/ja_el_p3.mp3", 6: "/onboarding/proof/wizard/ja_el_p6.mp3", 8: "/onboarding/proof/wizard/ja_el_p8.mp3", 10: "/onboarding/proof/wizard/ja_el_p10.mp3" },
  spiritualPractical: { 1: "/onboarding/proof/wizard/ja_sp_p1.mp3", 3: "/onboarding/proof/wizard/ja_sp_p3.mp3", 6: "/onboarding/proof/wizard/ja_sp_p6.mp3", 8: "/onboarding/proof/wizard/ja_sp_p8.mp3", 10: "/onboarding/proof/wizard/ja_sp_p10.mp3" },
};
const VOICE_AUDIO_SRC_ZH = {
  gentleDirect: { 1: "/onboarding/proof/wizard/zh_p1.mp3", 3: "/onboarding/proof/wizard/zh_p3.mp3", 6: "/onboarding/proof/wizard/zh_p6.mp3", 8: "/onboarding/proof/wizard/zh_p8.mp3", 10: "/onboarding/proof/wizard/zh_p10.mp3" },
  simpleDeep: { 1: "/onboarding/proof/wizard/zh_sd_p1.mp3", 3: "/onboarding/proof/wizard/zh_sd_p3.mp3", 6: "/onboarding/proof/wizard/zh_sd_p6.mp3", 8: "/onboarding/proof/wizard/zh_sd_p8.mp3", 10: "/onboarding/proof/wizard/zh_sd_p10.mp3" },
  emotionalLogical: { 1: "/onboarding/proof/wizard/zh_el_p1.mp3", 3: "/onboarding/proof/wizard/zh_el_p3.mp3", 6: "/onboarding/proof/wizard/zh_el_p6.mp3", 8: "/onboarding/proof/wizard/zh_el_p8.mp3", 10: "/onboarding/proof/wizard/zh_el_p10.mp3" },
  spiritualPractical: { 1: "/onboarding/proof/wizard/zh_sp_p1.mp3", 3: "/onboarding/proof/wizard/zh_sp_p3.mp3", 6: "/onboarding/proof/wizard/zh_sp_p6.mp3", 8: "/onboarding/proof/wizard/zh_sp_p8.mp3", 10: "/onboarding/proof/wizard/zh_sp_p10.mp3" },
};
const VOICE_AUDIO_SRC_TW = {
  gentleDirect: { 1: "/onboarding/proof/wizard/tw_p1.mp3", 3: "/onboarding/proof/wizard/tw_p3.mp3", 6: "/onboarding/proof/wizard/tw_p6.mp3", 8: "/onboarding/proof/wizard/tw_p8.mp3", 10: "/onboarding/proof/wizard/tw_p10.mp3" },
  simpleDeep: { 1: "/onboarding/proof/wizard/tw_sd_p1.mp3", 3: "/onboarding/proof/wizard/tw_sd_p3.mp3", 6: "/onboarding/proof/wizard/tw_sd_p6.mp3", 8: "/onboarding/proof/wizard/tw_sd_p8.mp3", 10: "/onboarding/proof/wizard/tw_sd_p10.mp3" },
  emotionalLogical: { 1: "/onboarding/proof/wizard/tw_el_p1.mp3", 3: "/onboarding/proof/wizard/tw_el_p3.mp3", 6: "/onboarding/proof/wizard/tw_el_p6.mp3", 8: "/onboarding/proof/wizard/tw_el_p8.mp3", 10: "/onboarding/proof/wizard/tw_el_p10.mp3" },
  spiritualPractical: { 1: "/onboarding/proof/wizard/tw_sp_p1.mp3", 3: "/onboarding/proof/wizard/tw_sp_p3.mp3", 6: "/onboarding/proof/wizard/tw_sp_p6.mp3", 8: "/onboarding/proof/wizard/tw_sp_p8.mp3", 10: "/onboarding/proof/wizard/tw_sp_p10.mp3" },
};

function snap5(val) {
  let best = 0;
  let bestDist = Infinity;
  VOICE_5_VALUES.forEach((v, i) => { const d = Math.abs(val - v); if (d < bestDist) { bestDist = d; best = i; } });
  return best;
}

function Step4VoiceGraphs({ state, update, i18n = {} }) {
  const audioRef = useRef(null);
  const audioSrc = i18n.locale === "ja" ? VOICE_AUDIO_SRC_JA : i18n.locale === "zh" ? VOICE_AUDIO_SRC_ZH : i18n.locale === "tw" ? VOICE_AUDIO_SRC_TW : VOICE_AUDIO_SRC;
  const playAudio = useCallback((sliderId, position) => {
    if (audioRef.current) { audioRef.current.pause(); audioRef.current.currentTime = 0; }
    const src = audioSrc[sliderId]?.[position];
    if (!src) return;
    const a = new Audio(src);
    audioRef.current = a;
    a.play().catch(() => {});
  }, [audioSrc]);

  const handleSlider = (id, rawVal) => {
    const idx = snap5(parseInt(rawVal));
    const snappedVal = VOICE_5_VALUES[idx];
    const pos = VOICE_5_STOPS[idx];
    update({ voiceSettings: { ...state.voiceSettings, [id]: snappedVal } });
    if (audioSrc[id]) playAudio(id, pos);
  };

  const graphComponents = [PulseWaveGraph, SpectrumBarGraph, EmotionRadarGraph, EnergyGaugeGraph];

  return (
    <div>
      <StepHero
        eyebrow="Voice"
        title="Shape your brand tone"
        subtitle="Four sliders — slide and watch the graphs move. Each axis changes how every sentence feels."
      />
      <p className="mb-5 text-[11px] text-white">Next step shows what each position does for your reader.</p>

      <div className="space-y-6">
        {VOICE_SLIDERS.map((s, idx) => {
          const val = state.voiceSettings?.[s.id] ?? s.default;
          const snapIdx = snap5(val);
          const position = VOICE_5_STOPS[snapIdx];
          const toneData = VOICE_TONE_10[s.id][position - 1];
          const GraphComp = graphComponents[idx];
          return (
            <div key={s.id} className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-bold text-white">{s.left}</span>
                <span className="text-[10px] text-white max-w-xs text-center">{s.desc}</span>
                <span className="text-sm font-bold text-white">{s.right}</span>
              </div>

              <GraphComp position={position} color={s.color} />

              <input type="range" min="0" max="100" step="25" value={VOICE_5_VALUES[snapIdx]}
                onChange={(e) => handleSlider(s.id, e.target.value)}
                className="w-full h-2.5 bg-gray-100 rounded-lg appearance-none cursor-pointer mt-2"
                style={{ accentColor: s.color }}
              />

              <div className="flex justify-between items-center mt-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: s.color }} />
                  <span className="text-xs font-bold" style={{ color: s.color }}>{toneData.label}</span>
                </div>
                <span className="text-[10px] text-white">Position {position} of 10</span>
              </div>

              {audioSrc[s.id] && (
                <div className="mt-2 flex items-center gap-2">
                  <button onClick={() => playAudio(s.id, position)} className="text-[10px] text-violet-600 hover:text-violet-800 flex items-center gap-1">
                    <Play size={10} /> Listen to position {position}
                  </button>
                </div>
              )}

              <div className="mt-3 bg-gray-50 rounded-lg p-3 border border-gray-100">
                <p className="text-[11px] text-white leading-relaxed">{toneData.technique}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Step5VoiceEffects({ state, update }) {
  const graphComponents = [PulseWaveGraph, SpectrumBarGraph, EmotionRadarGraph, EnergyGaugeGraph];
  const handleSlider = (id, rawVal) => {
    const idx = snap5(parseInt(rawVal));
    update({ voiceSettings: { ...state.voiceSettings, [id]: VOICE_5_VALUES[idx] } });
  };

  return (
    <div>
      <StepHero
        eyebrow="Impact"
        title="What your tone does for readers"
        subtitle="Slide, then open impact below if you want the full read."
      />

      <div className="mb-6 rounded-2xl border border-violet-100 bg-violet-50/50 px-4 py-3">
        <p className="text-[10px] font-bold uppercase tracking-wider text-violet-800">Narrator preview</p>
        <p className="mt-1 text-[11px] leading-relaxed text-white">
          Same comfort passage, three Edge TTS pipeline-demo voices. Pair what you hear with the sliders above.
        </p>
        <div className="mt-3 space-y-2">
          <div>
            <span className="text-[10px] font-semibold text-white">Regulating / calm</span>
            <audio className="mt-1 block h-9 w-full" controls preload="metadata" src="/onboarding/audio/voice_cmp_comfort_voice_regulating_female.mp3" />
          </div>
          <div>
            <span className="text-[10px] font-semibold text-white">Warm empathetic</span>
            <audio className="mt-1 block h-9 w-full" controls preload="metadata" src="/onboarding/audio/voice_cmp_comfort_voice_warm_male.mp3" />
          </div>
          <div>
            <span className="text-[10px] font-semibold text-white">Direct / authority</span>
            <audio className="mt-1 block h-9 w-full" controls preload="metadata" src="/onboarding/audio/voice_cmp_comfort_voice_direct_authority.mp3" />
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {VOICE_SLIDERS.map((s, idx) => {
          const val = state.voiceSettings?.[s.id] ?? s.default;
          const snapIdx = snap5(val);
          const position = VOICE_5_STOPS[snapIdx];
          const toneData = VOICE_TONE_10[s.id][position - 1];
          const GraphComp = graphComponents[idx];

          return (
            <div key={s.id} className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
              <div className="p-4 border-b border-gray-100" style={{ borderLeftWidth: 4, borderLeftColor: s.color }}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: s.color }} />
                    <span className="text-sm font-bold text-white">{s.left} — {s.right}</span>
                  </div>
                  <span className="text-xs font-bold px-2.5 py-0.5 rounded-full" style={{ backgroundColor: s.color + '15', color: s.color }}>{toneData.label}</span>
                </div>
              </div>

              <div className="p-4">
                <div className="bg-gray-50 rounded-xl p-3 mb-3 border border-gray-100">
                  <GraphComp position={position} color={s.color} />
                  <input type="range" min="0" max="100" step="25" value={VOICE_5_VALUES[snapIdx]}
                    onChange={(e) => handleSlider(s.id, e.target.value)}
                    className="w-full h-2.5 bg-gray-200 rounded-lg appearance-none cursor-pointer mt-2"
                    style={{ accentColor: s.color }}
                  />
                  <div className="flex justify-between items-center mt-1.5">
                    <span className="text-[10px] font-semibold" style={{ color: s.color }}>{s.left}</span>
                    <span className="text-[10px] text-white">{position}/10</span>
                    <span className="text-[10px] font-semibold" style={{ color: s.color }}>{s.right}</span>
                  </div>
                </div>

                <details className="rounded-lg border border-gray-100 bg-gray-50/90 px-3 py-2 text-[11px] text-white open:pb-3">
                  <summary className="cursor-pointer text-xs font-bold text-white outline-none">How this lands for readers</summary>
                  <p className="mt-2 text-[11px] leading-relaxed text-white">{s.desc}</p>
                  <p className="mt-2 text-sm font-medium leading-relaxed text-white">{toneData.technique}</p>
                  <div className="mt-3 space-y-2">
                    {toneData.benefits.map((benefit, i) => (
                      <div key={i} className="flex items-start gap-2">
                        <div className="w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0 text-[9px] font-bold text-white" style={{ backgroundColor: s.color }}>{i + 1}</div>
                        <p className="text-[11px] text-white leading-relaxed">{benefit}</p>
                      </div>
                    ))}
                  </div>
                </details>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Step5VisualStyle({ state, update, i18n = {} }) {
  const { tVisualStyles: _V = VISUAL_STYLES } = i18n;
  const handleVisual = (id) => update({ visualStyle: id });
  const handleTradition = (val) => update({ tradition: val });
  const selectedVisual = _V.find((v) => v.id === state.visualStyle);

  return (
    <div>
      <StepHero
        eyebrow="Look & feel"
        title="Visual world"
        subtitle="Pick the visual identity your readers will associate with your brand — covers, social, and video all follow from here."
      />

      <div className="text-xs font-bold uppercase tracking-wider text-violet-600/90 mb-3">Visual style</div>
      <div className="grid grid-cols-2 gap-3 mb-4">
        {_V.map((vs) => (
          <button key={vs.id} onClick={() => handleVisual(vs.id)}
            className={`p-4 rounded-xl border-2 text-left transition-all duration-200 ${state.visualStyle === vs.id ? "border-gray-900 bg-gray-50 shadow-md scale-[1.01]" : "border-gray-200 bg-white hover:border-gray-300"}`}>
            <div className={`w-full aspect-video mb-2 rounded-lg overflow-hidden border bg-gray-100 ${state.visualStyle === vs.id ? "ring-2 ring-offset-2 ring-gray-900 border-gray-900/20" : "border-gray-100"}`}>
              <img
                src={VISUAL_IDENTITY_PROOF_URL[vs.id]}
                alt=""
                className={`w-full h-full object-cover transition-transform duration-300 ${state.visualStyle === vs.id ? "scale-105" : ""}`}
                loading="lazy"
              />
            </div>
            <div className="flex gap-1.5 mb-2">{vs.palette.map((c, i) => <div key={i} className="w-6 h-6 rounded-md shadow-sm" style={{ backgroundColor: c }} />)}</div>
            <div className="text-xs font-bold text-white">{vs.label}</div>
            <div className="text-[10px] text-white mt-0.5">{vs.desc}</div>
            <div className="text-[10px] text-white mt-1 italic">{vs.mood}</div>
          </button>
        ))}
      </div>

    </div>
  );
}

const EMOTION_CATEGORIES = [
  { name: "Safety & Calm", icon: "🛡️", color: "#6366f1", items: ["Finally calm", "Safe in my body", "Permission to rest"], impacts: { "Finally calm": "Readers' nervous systems downregulate — they stop bracing and start absorbing", "Safe in my body": "Somatic trust builds from the first page, reducing fight-or-flight during reading", "Permission to rest": "Dissolves the guilt loop that keeps burned-out readers from engaging with self-help" } },
  { name: "Clarity & Direction", icon: "🧭", color: "#059669", items: ["Clear-headed", "In control", "Connected to purpose"], impacts: { "Clear-headed": "Cuts through decision fatigue — readers feel the fog lift and start choosing", "In control": "Restores agency in readers who feel life is happening to them, not through them", "Connected to purpose": "Bridges the gap between 'what do I do' and 'why does it matter' — readers find momentum" } },
  { name: "Energy & Confidence", icon: "⚡", color: "#f59e0b", items: ["Energized", "Confident", "Resilient"], impacts: { "Energized": "Transforms passive readers into action-takers — they close the book and move", "Confident": "Rebuilds self-trust that imposter syndrome and comparison culture eroded", "Resilient": "Readers develop bounce-back capacity — setbacks become data, not identity" } },
  { name: "Release & Healing", icon: "🕊️", color: "#f43f5e", items: ["Released", "Forgiven", "Less alone"], impacts: { "Released": "Grief, resentment, and held tension finally have somewhere to go — readers exhale for real", "Forgiven": "Self-compassion replaces the inner critic — readers stop punishing themselves for being human", "Less alone": "Names the unnamed — readers discover their 'weird' pain is universal, breaking isolation" } },
  { name: "Presence & Hope", icon: "✨", color: "#7c3aed", items: ["Grounded", "Hopeful", "Present"], impacts: { "Grounded": "Anchors readers in the body and the now — rumination and future-anxiety lose their grip", "Hopeful": "Reignites the belief that change is possible — the most powerful conversion driver in self-help", "Present": "Readers stop living in regret or anxiety and taste what being here actually feels like" } },
];

function Step6EmotionalOutcomes({ state, update, i18n = {} }) {
  const { tEmotionCategories: _EC = EMOTION_CATEGORIES } = i18n;
  const handleEmotion = (emotion, category) => {
    const current = state.emotions || [];
    const categoryEmotions = _EC.find(c => c.name === category)?.items || [];
    const filtered = current.filter(e => !categoryEmotions.includes(e));
    if (current.includes(emotion)) update({ emotions: filtered });
    else update({ emotions: [...filtered, emotion] });
  };

  return (
    <div>
      <StepHero
        eyebrow="Promise"
        title="Emotional Outcomes"
        subtitle="These are the feelings your reader walks away with — the transformation they can name. Every title, CTA, and marketing message points back to these promises."
      />
      <div className="mb-6 rounded-xl border border-rose-100/80 bg-rose-50/50 p-4 backdrop-blur-sm">
        <p className="text-xs leading-relaxed text-rose-900">
          <strong>Pick one for each category.</strong> Your choices become the emotional north star of your entire brand. Covers promise these feelings visually. Titles name them. Exercises deliver them. The system weaves your selections into every piece of content it generates.
        </p>
      </div>
      <div className="space-y-4 mb-4">
        {_EC.map((cat) => (
          <div key={cat.name} className="rounded-xl border-2 p-4" style={{ borderColor: cat.color + '40', backgroundColor: cat.color + '08' }}>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-base">{cat.icon}</span>
              <span className="text-xs font-bold text-white">{cat.name}</span>
              <div className="flex-1 h-px" style={{ backgroundColor: cat.color + '30' }} />
            </div>
            <div className="flex flex-wrap gap-2">
              {cat.items.map((e) => {
                const active = (state.emotions || []).includes(e);
                const eSrc = EMOTION_PROOF_URL[e];
                return (
                  <button
                    key={e}
                    onClick={() => handleEmotion(e, cat.name)}
                    className={`inline-flex items-center gap-2 text-xs px-3 py-2 rounded-lg border transition-all duration-200 ${active ? "bg-gray-900 text-white border-gray-900 shadow-md scale-[1.02]" : "bg-gray-50 text-white border-gray-200 hover:border-gray-400"}`}
                  >
                    <img
                      src={eSrc}
                      alt=""
                      className={`w-8 h-8 rounded-full object-cover border flex-shrink-0 transition-transform duration-200 ${active ? "border-white/40 scale-110" : "border-gray-200"}`}
                      loading="lazy"
                    />
                    <span>{e}</span>
                    {active && <Check size={12} className="text-white" />}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}

const TOPIC_CATEGORIES = [
  { label: "Sleep & Anxiety", icon: "😰", color: "#6366f1", tags: [
    { id: "anxiety-at-night", angle: "framework", bullet: "Delivers a pre-sleep anxiety protocol — 3 body scans that interrupt the cortisol loop before it spirals" },
    { id: "overthinking", angle: "origin", bullet: "Traces the overthinking pattern to a childhood survival strategy — your brain learned to scan for danger and never stopped" },
    { id: "panic-grounding", angle: "debunk", bullet: "Debunks 'just breathe through it' — panic needs somatic intervention first, cognitive tools second" },
    { id: "sunday-dread", angle: "leverage", bullet: "Reframes Sunday dread as your nervous system's weekly forecast — the dread itself contains data about what needs to change" },
  ]},
  { label: "Burnout & Work", icon: "🔥", color: "#f59e0b", tags: [
    { id: "burnout-recovery", angle: "debunk", bullet: "Debunks 'just take a vacation' — burnout is a nervous system state, not a scheduling problem" },
    { id: "nervous-system-reset", angle: "framework", bullet: "Provides a 5-day vagal tone reset protocol backed by polyvagal research — structure readers can follow immediately" },
    { id: "decision-fatigue", angle: "reveal", bullet: "Reveals that decision fatigue isn't about willpower — it's an overloaded prefrontal cortex running outdated threat software" },
    { id: "phone-addiction", angle: "leverage", bullet: "Reframes the phone as a biofeedback tool — your scroll pattern reveals exactly what your nervous system is craving" },
  ]},
  { label: "Grief & Healing", icon: "🕊️", color: "#f43f5e", tags: [
    { id: "grief-timeline", angle: "debunk", bullet: "Debunks the '5 stages' model — grief is nonlinear, and knowing this stops readers from pathologizing their own healing" },
    { id: "toxic-relationship-healing", angle: "origin", bullet: "Traces the attraction pattern to early attachment wounds — understanding the origin breaks the repetition cycle" },
    { id: "intergenerational-trauma", angle: "reveal", bullet: "Reveals how trauma transmits through epigenetics and family silence — readers understand their pain isn't 'just in their head'" },
    { id: "heartbreak-recovery", angle: "framework", bullet: "Structures recovery into three phases: survive, stabilize, rebuild — giving the broken-hearted a map when they feel lost" },
    { id: "emotional-numbness", angle: "leverage", bullet: "Reframes numbness as the nervous system's most sophisticated protection — not absence of feeling, but an excess of it" },
  ]},
  { label: "Identity & Direction", icon: "🧭", color: "#059669", tags: [
    { id: "feeling-behind", angle: "debunk", bullet: "Debunks the comparison timeline — there is no 'behind' because everyone is building on completely different foundations" },
    { id: "quarter-life-crisis", angle: "leverage", bullet: "Reframes the crisis as the identity system upgrading — the discomfort is proof you're outgrowing the old version" },
    { id: "identity-rebuild", angle: "framework", bullet: "Provides a 4-phase identity reconstruction framework — from deconstruction through integration to authentic expression" },
    { id: "purpose-after-30", angle: "origin", bullet: "Traces the purpose void to inherited career scripts — once you see whose dream you were living, yours becomes visible" },
  ]},
  { label: "Focus & Performance", icon: "⚡", color: "#0ea5e9", tags: [
    { id: "habit-building", angle: "framework", bullet: "Systematizes habit formation into environment design + identity shift — structure that works even when motivation fails" },
    { id: "ADHD-productivity", angle: "leverage", bullet: "Reframes ADHD hyperfocus as a strategic advantage — your brain isn't broken, the productivity advice was designed for someone else" },
    { id: "dopamine-detox", angle: "debunk", bullet: "Debunks the viral dopamine detox trend — the real issue is reward sensitivity, and the fix is recalibration, not deprivation" },
    { id: "deep-work", angle: "reveal", bullet: "Reveals that deep work for anxious minds requires nervous system resets between blocks — not just willpower and timers" },
  ]},
  { label: "Meaning & Spirituality", icon: "✨", color: "#7c3aed", tags: [
    { id: "meditation-beginners", angle: "debunk", bullet: "Debunks 'clear your mind' — meditation is about noticing thoughts, not eliminating them. This reframe keeps beginners from quitting" },
    { id: "meaning-after-loss", angle: "origin", bullet: "Traces meaning-making to the human need for narrative coherence — when loss shatters the story, rebuilding meaning is the healing" },
    { id: "spiritual-no-religion", angle: "leverage", bullet: "Reframes spiritual hunger as a feature, not a gap — you don't need someone else's tradition to access depth and transcendence" },
    { id: "inner-peace-chaos", angle: "reveal", bullet: "Reveals that inner peace isn't the absence of chaos but a different relationship to it — the noise doesn't stop, but you stop drowning" },
    { id: "mindfulness-skeptics", angle: "framework", bullet: "Delivers a skeptic-friendly 5-minute practice backed by neuroscience data — no incense, no mantras, just measurable results" },
  ]},
];

const ANGLE_FEEDBACK = {
  debunk: { label: "Debunk", icon: "🔍", systemEffect: "Titles open with contrarian hooks — 'What your therapist won't tell you.'", emotionalBenefit: "Readers feel intellectually respected. Validates their suspicion that conventional advice isn't working." },
  framework: { label: "Framework", icon: "🔧", systemEffect: "Titles lead with structure — '5-step protocol for...' Repeatable systems.", emotionalBenefit: "Overwhelmed readers exhale when they see a clear system. Transforms vague anxiety into concrete steps." },
  reveal: { label: "Reveal", icon: "💡", systemEffect: "Titles expose hidden truths — 'The real reason you can't sleep.'", emotionalBenefit: "Readers experience 'aha moments' that rewrite their self-narrative from broken to understood." },
  leverage: { label: "Leverage", icon: "🔄", systemEffect: "Titles reframe weaknesses — 'Your anxiety is a superpower.'", emotionalBenefit: "Readers stop fighting themselves. Says 'you're not broken, you're just using your gifts wrong.'" },
  origin: { label: "Origin", icon: "🌱", systemEffect: "Titles trace root causes — 'Where your pattern actually started.'", emotionalBenefit: "Deep relief from understanding where patterns began. Creates compassion for their past selves." },
};

// ═══════════════════════════════════════════════════════════
// MARKET DATA — Visual Identity & Topic/Angle research scores
// ═══════════════════════════════════════════════════════════
const VISUAL_MARKET = {
  calm_minimal:      { shelf: 62, trust: 88, social: 70, premium: 78, rank: 5, demo: "30–55, F-lean", superpower: "Gets recommended by therapists and professionals — the 'credibility' choice" },
  dark_intense:      { shelf: 84, trust: 68, social: 85, premium: 80, rank: 3, demo: "22–38, neutral", superpower: "Generates the most organic UGC — readers share it as an identity signal" },
  earthy_organic:    { shelf: 65, trust: 82, social: 74, premium: 68, rank: 6, demo: "28–50, F-strong", superpower: "Builds deepest parasocial trust — readers feel the author is one of them" },
  bold_modern:       { shelf: 88, trust: 72, social: 82, premium: 75, rank: 1, demo: "25–40, neutral", superpower: "Cuts through visual noise on any shelf or feed — the stop-scroll champion" },
  premium_soft:      { shelf: 78, trust: 85, social: 76, premium: 92, rank: 2, demo: "30–50, F-slight", superpower: "Makes readers feel they're investing in themselves, not just buying a book" },
  sacred_cosmic:     { shelf: 75, trust: 77, social: 79, premium: 83, rank: 4, demo: "28–45, F-slight", superpower: "Builds cult followings — readers who buy in become evangelists" },
};

const ANGLE_MARKET = {
  debunk:    { viral: 88, trust: 45, conversion: 55, seo: 60, tip: "Best for top-of-funnel — controversy drives shares on cold audiences" },
  framework: { viral: 55, trust: 82, conversion: 90, seo: 85, tip: "Best for mid-funnel — audiences ready to act need structure" },
  reveal:    { viral: 80, trust: 65, conversion: 65, seo: 70, tip: "Best for email hooks — bridges curiosity into deeper content" },
  leverage:  { viral: 75, trust: 70, conversion: 72, seo: 50, tip: "Best for reframing objections — turns resistance into buy-in" },
  origin:    { viral: 50, trust: 92, conversion: 60, seo: 55, tip: "Best for long-form loyalty — deepens trust with existing audience" },
};

const TOPIC_MARKET = {
  "Sleep & Anxiety":       { search: 95, competition: 88, monetization: 82, growth: 75, platform: "YouTube" },
  "Burnout & Work":        { search: 80, competition: 75, monetization: 78, growth: 85, platform: "LinkedIn" },
  "Grief & Healing":       { search: 55, competition: 40, monetization: 60, growth: 65, platform: "Podcasts" },
  "Identity & Direction":  { search: 60, competition: 55, monetization: 70, growth: 80, platform: "TikTok" },
  "Focus & Performance":   { search: 85, competition: 82, monetization: 88, growth: 70, platform: "YouTube" },
  "Meaning & Spirituality":{ search: 50, competition: 45, monetization: 65, growth: 75, platform: "Books" },
};

// Ideal voice profiles per angle — from synergy research
const ANGLE_IDEAL_VOICE = {
  debunk:    { gentleDirect: 3, simpleDeep: 4, emotionalLogical: 4, spiritualPractical: 7 },
  framework: { gentleDirect: 6, simpleDeep: 3, emotionalLogical: 7, spiritualPractical: 9 },
  reveal:    { gentleDirect: 4, simpleDeep: 5, emotionalLogical: 2, spiritualPractical: 5 },
  leverage:  { gentleDirect: 5, simpleDeep: 5, emotionalLogical: 4, spiritualPractical: 7 },
  origin:    { gentleDirect: 2, simpleDeep: 5, emotionalLogical: 2, spiritualPractical: 4 },
};
const ANGLE_DIM_WEIGHTS = {
  debunk:    { gentleDirect: 3.0, simpleDeep: 1.0, emotionalLogical: 1.5, spiritualPractical: 1.5 },
  framework: { gentleDirect: 1.0, simpleDeep: 3.0, emotionalLogical: 1.5, spiritualPractical: 2.0 },
  reveal:    { gentleDirect: 1.5, simpleDeep: 1.5, emotionalLogical: 3.0, spiritualPractical: 1.0 },
  leverage:  { gentleDirect: 1.5, simpleDeep: 1.0, emotionalLogical: 2.0, spiritualPractical: 2.5 },
  origin:    { gentleDirect: 3.0, simpleDeep: 1.5, emotionalLogical: 2.5, spiritualPractical: 1.0 },
};

function calcSynergyScore(voicePositions, angle) {
  const ideal = ANGLE_IDEAL_VOICE[angle];
  const weights = ANGLE_DIM_WEIGHTS[angle];
  if (!ideal || !weights) return 50;
  let actualDist = 0, maxDist = 0;
  for (const dim of Object.keys(ideal)) {
    const vp = voicePositions.find(v => v.id === dim);
    const pos = vp ? vp.position : 5;
    const w = weights[dim];
    actualDist += w * Math.abs(pos - ideal[dim]);
    maxDist += w * 9;
  }
  return Math.round(100 * (1 - actualDist / maxDist));
}

function Step7Topics({ state, update, i18n = {} }) {
  const { tAngleFeedback: _AF = ANGLE_FEEDBACK } = i18n;
  const handleTopicTag = (tagId, categoryLabel) => {
    const current = state.topicTags || [];
    const categoryTagIds = TOPIC_CATEGORIES.find(c => c.label === categoryLabel)?.tags.map(t => t.id) || [];
    const filtered = current.filter(t => !categoryTagIds.includes(t));
    if (current.includes(tagId)) update({ topicTags: filtered });
    else update({ topicTags: [...filtered, tagId] });
  };

  return (
    <div>
      <StepHero
        eyebrow="Territory"
        title="Claim Your Search Territory"
        subtitle="Pick one topic per category — each choice sets the content angle your brand uses to frame that territory. Watch the sidebar update as you choose."
      />
      <div className="mb-6 rounded-xl border border-indigo-100/80 bg-indigo-50/50 p-4 backdrop-blur-sm">
        <p className="text-xs leading-relaxed text-indigo-900">
          <strong>One per category.</strong> Each topic is paired with a content angle — debunk, framework, reveal, leverage, or origin. As you switch topics, the angle and strategy in the sidebar changes.
        </p>
      </div>
      <div className="space-y-4">
        {TOPIC_CATEGORIES.map((cat) => (
          <div key={cat.label} className="rounded-xl border-2 p-4" style={{ borderColor: cat.color + '40', backgroundColor: cat.color + '08' }}>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-base">{cat.icon}</span>
              <span className="text-xs font-bold text-white">{cat.label}</span>
              <div className="flex-1 h-px" style={{ backgroundColor: cat.color + '30' }} />
            </div>
            <div className="flex flex-wrap gap-2">
              {cat.tags.map((tag) => {
                const active = (state.topicTags || []).includes(tag.id);
                const tSrc = TOPIC_TAG_PROOF_URL[tag.id];
                const angleInfo = _AF[tag.angle];
                return (
                  <button key={tag.id} onClick={() => handleTopicTag(tag.id, cat.label)}
                    className={`inline-flex items-center gap-2 text-[11px] px-3 py-2 rounded-lg border transition-all duration-200 ${active ? "bg-gray-900 text-white border-gray-900 shadow-md scale-[1.02]" : "bg-white/80 text-white border-gray-200 hover:border-gray-400"}`}>
                    <img
                      src={tSrc}
                      alt=""
                      className={`w-7 h-7 rounded-md object-cover border flex-shrink-0 ${active ? "border-white/30 ring-1 ring-white/40" : "border-gray-200"}`}
                      loading="lazy"
                    />
                    <span>{tag.id.replace(/-/g, " ")}</span>
                    {angleInfo && <span className="text-[9px] opacity-60">{angleInfo.icon}</span>}
                    {active && <Check size={12} className="text-white" />}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Step8MarketIntel({ state }) {
  const proven = PROVEN[state.archetype] || PROVEN.nervous_system;
  return (
    <div>
      <h2 className="text-2xl font-extrabold text-white tracking-tight">Market Intelligence</h2>
      <p className="text-sm text-white mt-1 mb-2">Your creative vision is the soul of your brand. But soul alone doesn't pay rent. This page shows you how the system blends your unique direction with hard market data — real search volumes, proven buyer personas, and high-converting keyword territories — to ensure your catalog reaches the people who are already looking for what you're offering.</p>
      <p className="text-xs text-white mb-6 italic">Nothing changes about your brand's voice or identity. We just make sure it shows up where the demand is.</p>

      {/* Gen Z / Gen Alpha FIRST */}
      <div className="rounded-xl border border-violet-200 bg-violet-50 p-5 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Globe size={16} className="text-violet-600" />
          <span className="text-sm font-bold text-violet-800">Youth Reach: Gen Z + Gen Alpha</span>
        </div>
        <p className="text-xs text-violet-700 leading-relaxed mb-3">
          Every brand on Pearl Prime automatically serves Gen Z and Gen Alpha readers — no extra configuration needed. The system creates age-appropriate adaptations of your content: shorter formats tuned for mobile-first consumption, visual-first layouts optimized for scroll-based discovery, platform-native hooks for TikTok and YouTube Shorts, and fully illustrated manga-style editions for readers who think in images rather than paragraphs. Gen Alpha (born 2010-2025) is the first generation growing up with emotional vocabulary from day one — they're searching for mental health content at younger ages than any previous generation. Your brand meets them where they are.
        </p>
        <div className="grid grid-cols-3 gap-2">
          {[
            { icon: Smartphone, label: "Short-form first", desc: "TikTok, Reels, Shorts optimized" },
            { icon: BookMarked, label: "Manga editions", desc: "Full illustrated visual format" },
            { icon: Headphones, label: "Micro audiobooks", desc: "15-30 min listens for mobile" },
          ].map(({ icon: I, label, desc }) => (
            <div key={label} className="bg-white rounded-lg p-2.5 text-center">
              <I size={16} className="text-violet-500 mx-auto mb-1" />
              <div className="text-[10px] font-bold text-white">{label}</div>
              <div className="text-[9px] text-white">{desc}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <TrendingUp size={16} className="text-emerald-600" />
          <span className="text-sm font-bold text-emerald-800">How the Blend Works</span>
        </div>
        <p className="text-xs text-emerald-700 leading-relaxed mb-4">
          We combine your creative direction — archetype, voice, topics, and angles — with proven high-performing search terms, audience segments, and real-time market signals. Your brand identity stays completely intact while the system ensures your catalog targets the topics people are actively searching for. This means your books appear where demand already exists, your titles match what people actually type into search bars, and your content reaches buyer personas with verified spending power. The result: your unique voice reaches the largest possible audience.
        </p>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white rounded-lg p-3">
            <div className="text-[10px] font-bold text-emerald-700 uppercase mb-1">Your Direction</div>
            <p className="text-[11px] text-white">Archetype, voice, topics, angles, visual style — preserved as your brand's unique creative identity</p>
          </div>
          <div className="bg-white rounded-lg p-3">
            <div className="text-[10px] font-bold text-emerald-700 uppercase mb-1">Market Intelligence</div>
            <p className="text-[11px] text-white">Proven revenue personas, trending search terms, high-conversion keywords, and demand data matched to your archetype</p>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5 mb-6">
        <div className="text-xs font-bold text-white mb-3">Proven Revenue Personas for Your Archetype</div>
        <p className="text-[11px] text-white mb-3">These are the audience segments with verified purchasing power in your emotional territory. The system ensures your catalog reaches all of them.</p>
        {proven.personas.map((p, i) => (
          <div key={i} className="flex items-start gap-2 mb-2.5">
            <Target size={12} className="text-indigo-500 flex-shrink-0 mt-0.5" />
            <span className="text-[11px] text-white">{p}</span>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <div className="text-xs font-bold text-white mb-3">High-Performing Search Topics</div>
        <p className="text-[11px] text-white mb-3">These search terms have verified monthly volume and conversion rates. Your titles and keywords will be optimized around these terms alongside your custom selections.</p>
        <div className="flex flex-wrap gap-2">
          {proven.topics.map((t, i) => <span key={i} className="text-[11px] bg-gray-100 text-white px-3 py-1 rounded-full">{t}</span>)}
        </div>
      </div>
    </div>
  );
}

function Step9Formats({ state, update, i18n = {} }) {
  const { tSelectionFeedback: _SF = SELECTION_FEEDBACK } = i18n;
  const formatFocus = state.formatFocus || null;
  const channels = state.channels || [];
  const setFocus = (focus) => update({ formatFocus: focus });
  const toggleChannel = (ch) => { const next = channels.includes(ch) ? channels.filter((c) => c !== ch) : [...channels, ch]; update({ channels: next }); };

  const CHANNELS = [
    { id: "audiobook", label: "Audiobook", icon: Headphones, desc: "Full narrated audiobooks on Audible, Spotify, Apple Books, and 40+ platforms worldwide", benefit: "Listeners heal during commutes, walks, and sleepless nights — your voice becomes a companion in their most vulnerable private moments" },
    { id: "yt_channel", label: "YouTube Channel", icon: Tv, desc: "Daily video content — shorts, long-form talks, guided sessions, and visualized chapters", benefit: "Visual learners process emotion through moving images — your brand becomes a daily presence in their feed, building trust through consistent showing up" },
    { id: "tiktok", label: "TikTok", icon: Smartphone, desc: "Platform-native short-form video with trending audio, text overlays, and hook-first editing", benefit: "You catch people mid-scroll in moments of vulnerability — a 30-second clip can be the first step toward a life change" },
    { id: "pocket_guide", label: "Pocket Guide", icon: BookOpen, desc: "Condensed 30-50 page quick-reference editions — the essential takeaways in a weekend read", benefit: "Overwhelmed readers who can't commit to a full book get immediate relief — a weekend read that delivers the essential transformation" },
    { id: "7_day_guide", label: "How to Do It in 7 Days", icon: Clock, desc: "Compressed transformation protocol — one chapter per day, clear daily actions, quick wins", benefit: "Structure reduces overwhelm — readers who've failed at 'read when you feel like it' thrive with daily assignments that build momentum" },
    { id: "mastercourse", label: "Mastercourse Series", icon: GraduationCap, desc: "Multi-volume deep-dive series with progressive complexity — 4-8 books building on each other", benefit: "Committed readers go deep over months — each volume builds on the last, creating the sustained practice that drives real, lasting change" },
    { id: "workbook", label: "Interactive Workbook", icon: PenTool, desc: "Exercise-heavy companion with fill-in sections, tracking sheets, and guided reflection spaces", benefit: "Writing activates different brain pathways than reading — workbooks turn passive consumption into active self-discovery and integration" },
    { id: "daily_journal", label: "Daily Journal", icon: BookMarked, desc: "30-90 day guided journal — one prompt per day with space for writing and reflection", benefit: "Daily prompts build the self-awareness muscle — readers develop an ongoing relationship with their own inner world, one page at a time" },
  ];

  return (
    <div>
      <h2 className="text-2xl font-extrabold text-white tracking-tight">Format & Channel Choices</h2>
      <p className="text-sm text-white mt-1 mb-2">Your format focus tells the catalog planner whether to optimize for visual-first short-form content or deep long-form books. Your channel selections determine where your brand publishes — each active channel adds content weight to the pipeline, meaning more formats, more variations, and more touchpoints with your audience.</p>

      <div className="text-xs font-bold uppercase tracking-wider text-white mb-3 mt-6">Primary Format Focus</div>
      <p className="text-[11px] text-white mb-3">This is the most important format decision. It changes how the catalog planner distributes content across your entire brand.</p>
      <div className="grid grid-cols-2 gap-3 mb-8">
        <button onClick={() => setFocus("manga")}
          className={`p-5 rounded-xl border-2 text-left transition-all ${formatFocus === "manga" ? "border-gray-900 bg-gray-50 shadow-md" : "border-gray-200 bg-white hover:border-gray-300"}`}>
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-rose-500 to-purple-600 flex items-center justify-center mb-3"><Image size={24} className="text-white" /></div>
          <div className="text-sm font-bold text-white">Manga / Visual</div>
          <p className="text-[11px] text-white mt-1 leading-relaxed">Illustrated panels, visual storytelling, manga-style layouts. Audiobooks default to short formats (15-30 min). Optimized for Gen Z and Gen Alpha visual-first consumption.</p>
          {formatFocus === "manga" && <div className="mt-2 bg-rose-50 rounded-lg p-2"><p className="text-[10px] text-rose-700">Catalog planner will prioritize short-form audiobooks, visual content, and illustration-heavy formats across all channels.</p></div>}
        </button>
        <button onClick={() => setFocus("book")}
          className={`p-5 rounded-xl border-2 text-left transition-all ${formatFocus === "book" ? "border-gray-900 bg-gray-50 shadow-md" : "border-gray-200 bg-white hover:border-gray-300"}`}>
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center mb-3"><BookOpen size={24} className="text-white" /></div>
          <div className="text-sm font-bold text-white">Traditional Books</div>
          <p className="text-[11px] text-white mt-1 leading-relaxed">Full-length narrative books, deep guided programs, comprehensive workbooks. Audiobooks in long formats (3-8 hrs). Optimized for depth-seeking readers.</p>
          {formatFocus === "book" && <div className="mt-2 bg-amber-50 rounded-lg p-2"><p className="text-[10px] text-amber-700">Catalog planner will prioritize long-form books, complete programs, and in-depth series across all channels.</p></div>}
        </button>
      </div>
      {formatFocus && _SF.formats[formatFocus] && (
        <SelectionFeedback
          systemEffect={_SF.formats[formatFocus].systemEffect}
          emotionalBenefit={_SF.formats[formatFocus].emotionalBenefit}
          color={formatFocus === "manga" ? "#e11d48" : "#d97706"}
        />
      )}
      <div className="mb-4" />

      <div className="text-xs font-bold uppercase tracking-wider text-white mb-3">Publishing Channels</div>
      <p className="text-[11px] text-white mb-3">Select all channels you want your brand to publish through. Each channel generates dedicated content adapted for that platform's format, audience, and algorithm requirements.</p>
      <div className="grid grid-cols-1 gap-2">
        {CHANNELS.map((ch) => {
          const active = channels.includes(ch.id);
          const Icon = ch.icon;
          return (
            <button key={ch.id} onClick={() => toggleChannel(ch.id)}
              className={`flex items-start gap-3 p-3.5 rounded-xl border-2 text-left transition-all ${active ? "border-gray-900 bg-gray-50" : "border-gray-200 bg-white hover:border-gray-300"}`}>
              <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${active ? "bg-gray-900" : "bg-gray-100"}`}>
                <Icon size={16} className={active ? "text-white" : "text-white"} />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">{ch.label}</span>
                  {active && <Check size={14} className="text-white" />}
                </div>
                <p className="text-[10px] text-white mt-0.5">{ch.desc}</p>
                {active && ch.benefit && (
                  <div className="mt-1.5 flex items-start gap-1.5">
                    <Heart size={9} className="text-rose-400 flex-shrink-0 mt-0.5" />
                    <p className="text-[10px] text-rose-600 font-medium leading-relaxed">{ch.benefit}</p>
                  </div>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function StepBrandReveal({ state, i18n = {} }) {
  const { tArchetypes: _A = ARCHETYPES, tPersonas: _P = PERSONAS, tMoments: _M = MOMENTS, tVisualStyles: _V = VISUAL_STYLES, tEmotionCategories: _EC = EMOTION_CATEGORIES, tAngleFeedback: _AF = ANGLE_FEEDBACK, tSelectionFeedback: _SF = SELECTION_FEEDBACK, tProven: _PR = PROVEN } = i18n;
  const arch = _A.find((a) => a.id === state.archetype);
  const persona = _P.find((p) => p.id === state.persona);
  const moment = _M.find((m) => m.id === state.moment);
  const visual = _V.find((v) => v.id === state.visualStyle);
  const emotions = state.emotions || [];
  const topics = state.topicTags || [];

  // Derive topic+angle pairs
  const topicAnglePairs = topics.map(tagId => {
    for (const cat of TOPIC_CATEGORIES) {
      const found = cat.tags.find(t => t.id === tagId);
      if (found) return { tagId, angle: found.angle, bullet: found.bullet, category: cat.label, catIcon: cat.icon, catColor: cat.color };
    }
    return null;
  }).filter(Boolean);
  const uniqueAngles = [...new Set(topicAnglePairs.map(p => p.angle))];

  // Voice positions
  const voicePositions = VOICE_SLIDERS.map(s => {
    const val = state.voiceSettings?.[s.id] ?? s.default;
    const snapIdx = snap5(val);
    return { ...s, position: VOICE_5_STOPS[snapIdx] };
  });

  // Derive voice descriptors
  const voiceDesc = voicePositions.map(v => {
    const p = v.position;
    if (v.id === "gentleDirect") return p <= 3 ? "permission-giving" : p >= 8 ? "commanding" : "balanced";
    if (v.id === "simpleDeep") return p <= 3 ? "accessible" : p >= 8 ? "layered" : "mid-depth";
    if (v.id === "emotionalLogical") return p <= 3 ? "story-led" : p >= 8 ? "data-driven" : "balanced";
    if (v.id === "spiritualPractical") return p <= 3 ? "contemplative" : p >= 8 ? "tactical" : "blended";
    return "";
  });

  // Generate true category statement
  const trueCategory = arch && persona
    ? `${arch.name} for ${persona.label}${moment ? ` — catching them at "${moment.label}"` : ""}`
    : arch ? arch.name : "Your Brand";

  // Content engine steps derived from voice + angle mix
  const engineSteps = [
    { step: "Name the Problem", desc: moment ? `Open with "${moment.scene}" — your reader's exact moment` : "Open with the reader's exact pain point", icon: "🎯" },
    { step: "Reframe Identity", desc: `Use ${uniqueAngles.includes("debunk") ? "debunk" : uniqueAngles.includes("reveal") ? "reveal" : "origin"} angles to shift their self-story`, icon: "🪞" },
    { step: "Give a Micro-Tool", desc: `Deliver ${uniqueAngles.includes("framework") ? "a framework they can use tonight" : "an actionable insight they can apply immediately"}`, icon: "🔧" },
    { step: "Land in Emotion", desc: emotions.length > 0 ? `Every piece ends at: "${emotions[0]}"` : "Every piece ends in the promised feeling", icon: "💫" },
  ];

  // Unfair advantage loop
  const loopSteps = [
    { label: "Reframe", desc: "Break their old story", color: "#6366f1" },
    { label: "Regulate", desc: "Calm the nervous system", color: "#059669" },
    { label: "Restore", desc: "Rebuild from the body up", color: "#f59e0b" },
    { label: "Reorient", desc: "Point toward new identity", color: "#f43f5e" },
  ];

  // Positioning map coords — Gentle↔Direct on X, Simple↔Deep on Y
  const posX = voicePositions.find(v => v.id === "gentleDirect")?.position || 5;
  const posY = voicePositions.find(v => v.id === "simpleDeep")?.position || 5;

  // Emotional staircase — build ascending steps from trigger to each emotion
  const staircaseSteps = [
    { label: moment ? moment.label : "Pain Point", color: "#f43f5e", sub: "Where they start" },
    ...emotions.slice(0, 5).map((e, i) => {
      const cat = _EC.find(c => c.items.includes(e));
      return { label: e, color: cat?.color || "#6366f1", sub: cat?.name || "" };
    }),
  ];

  return (
    <div>
      <StepHero
        eyebrow="Reveal"
        title="Here is your brand"
        subtitle=""
      />

      {/* ═══ 1. TRUE CATEGORY — gradient banner ═══ */}
      {arch && (
        <div id="rev-category" className={`mb-6 rounded-2xl border-2 p-6 bg-gradient-to-br ${arch.gradient} shadow-lg`}>
          <div className="text-center">
            <div className="text-white/70 text-[10px] font-bold uppercase tracking-[0.3em] mb-2">Your True Category</div>
            <div className="text-white text-xl font-extrabold mb-2">{trueCategory}</div>
            <div className="text-white/80 text-sm leading-relaxed">{arch.tagline}</div>
            {arch.visionVibe && <p className="mt-3 text-white/70 text-[11px] leading-relaxed max-w-md mx-auto italic">{arch.visionVibe}</p>}
          </div>
        </div>
      )}

      {/* ═══ 2. VOICE SIGNATURE — circular gauges ═══ */}
      {Object.keys(state.voiceSettings || {}).length > 0 && (
        <div id="rev-voice" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">Voice Signature</div>
          <div className="grid grid-cols-4 gap-3">
            {voicePositions.map((s) => {
              const pct = (s.position / 10) * 100;
              return (
                <div key={s.id} className="text-center">
                  <div className="relative mx-auto mb-2 w-14 h-14">
                    <svg viewBox="0 0 64 64" className="w-full h-full -rotate-90">
                      <circle cx="32" cy="32" r="26" fill="none" stroke="#f3f4f6" strokeWidth="5" />
                      <circle cx="32" cy="32" r="26" fill="none" stroke={s.color} strokeWidth="5" strokeLinecap="round" strokeDasharray={`${pct * 1.63} 163`} />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-xs font-black text-white">{s.position}</span>
                    </div>
                  </div>
                  <div className="text-[9px] font-bold text-white">{s.left}</div>
                  <div className="text-[8px] text-white/80">{s.right}</div>
                </div>
              );
            })}
          </div>
          <div className="mt-3 text-center text-[10px] text-white/80">
            Your voice is <span className="text-white font-semibold">{voiceDesc.join(" · ")}</span>
          </div>
        </div>
      )}

      {/* ═══ 2b. POSITIONING MAP — 2D quadrant ═══ */}
      <div id="rev-positioning" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">Positioning Map</div>
        <div className="text-[10px] text-white/70 mb-3 text-center">Where your voice sits in the market landscape</div>
        <svg viewBox="0 0 300 300" className="w-full max-w-[280px] mx-auto">
          {/* Quadrant background */}
          <rect x="30" y="10" width="130" height="130" fill="#6366f115" rx="4" />
          <rect x="160" y="10" width="130" height="130" fill="#05966915" rx="4" />
          <rect x="30" y="140" width="130" height="130" fill="#f59e0b15" rx="4" />
          <rect x="160" y="140" width="130" height="130" fill="#f43f5e15" rx="4" />
          {/* Axes */}
          <line x1="30" y1="140" x2="290" y2="140" stroke="#e5e7eb" strokeWidth="1" />
          <line x1="160" y1="10" x2="160" y2="270" stroke="#e5e7eb" strokeWidth="1" />
          {/* Axis labels */}
          <text x="30" y="285" fontSize="9" fill="#9ca3af" fontWeight="bold">Gentle</text>
          <text x="265" y="285" fontSize="9" fill="#9ca3af" fontWeight="bold">Direct</text>
          <text x="5" y="15" fontSize="9" fill="#9ca3af" fontWeight="bold" transform="rotate(-90 10 15)">Deep</text>
          <text x="5" y="275" fontSize="9" fill="#9ca3af" fontWeight="bold" transform="rotate(-90 10 275)">Simple</text>
          {/* Quadrant labels */}
          <text x="95" y="75" textAnchor="middle" fontSize="8" fill="#6366f1" fontWeight="600">Wise Guide</text>
          <text x="225" y="75" textAnchor="middle" fontSize="8" fill="#059669" fontWeight="600">Expert Coach</text>
          <text x="95" y="210" textAnchor="middle" fontSize="8" fill="#f59e0b" fontWeight="600">Warm Friend</text>
          <text x="225" y="210" textAnchor="middle" fontSize="8" fill="#f43f5e" fontWeight="600">Bold Mentor</text>
          {/* Brand dot */}
          {(() => {
            const dotX = 30 + (posX / 10) * 260;
            const dotY = 270 - (posY / 10) * 260;
            return (<>
              <circle cx={dotX} cy={dotY} r="14" fill="#6366f1" fillOpacity="0.15" stroke="#6366f1" strokeWidth="2" />
              <circle cx={dotX} cy={dotY} r="6" fill="#6366f1" />
              <text x={dotX} y={dotY - 20} textAnchor="middle" fontSize="9" fill="#6366f1" fontWeight="bold">You</text>
            </>);
          })()}
        </svg>
      </div>

      {/* ═══ 3. VISUAL IDENTITY + MARKET DATA ═══ */}
      {visual && (() => {
        const vm = VISUAL_MARKET[visual.id] || {};
        const bars = [
          { label: "Shelf Appeal", val: vm.shelf || 0, color: "#f59e0b" },
          { label: "Trust Signal", val: vm.trust || 0, color: "#059669" },
          { label: "Social Share", val: vm.social || 0, color: "#6366f1" },
          { label: "Premium Feel", val: vm.premium || 0, color: "#7c3aed" },
        ];
        return (
          <div id="rev-visual" className="mb-6 rounded-2xl border border-gray-200 bg-white overflow-hidden shadow-sm">
            <div className="flex items-center gap-0 border-b border-gray-100">
              {visual.palette.map((col, i) => (
                <div key={i} className="flex-1 h-12" style={{ backgroundColor: col }} />
              ))}
            </div>
            <div className="p-4">
              <div className="text-[10px] font-bold uppercase text-white">Visual Identity</div>
              <div className="mt-1 text-base font-bold text-white">{visual.label}</div>
              <p className="mt-1 text-[11px] text-white italic">{visual.mood}</p>
            </div>
            <div className="px-4 pb-4">
              <div className="text-[9px] font-bold uppercase tracking-wider text-white mb-2">Market Scores</div>
              <div className="space-y-2">
                {bars.map(b => (
                  <div key={b.label} className="flex items-center gap-2">
                    <span className="text-[9px] text-white w-20 flex-shrink-0">{b.label}</span>
                    <div className="flex-1 h-3 bg-gray-800/30 rounded-lg overflow-hidden">
                      <div data-bar className="h-full rounded-lg transition-all duration-700" style={{ width: `${b.val}%`, backgroundColor: b.color }} />
                    </div>
                    <span className="text-[10px] font-bold w-7 text-right" style={{ color: b.color }}>{b.val}</span>
                  </div>
                ))}
              </div>
              <div className="mt-3 flex items-center gap-2">
                <span className="text-[9px] px-2 py-0.5 rounded-full bg-violet-100 text-white font-bold">Rank #{vm.rank || '—'}</span>
                <span className="text-[9px] text-white/70">{vm.demo}</span>
              </div>
              <p className="mt-2 text-[10px] text-white/80 leading-relaxed italic">{vm.superpower}</p>
            </div>
          </div>
        );
      })()}

      {/* ═══ 4. EMOTIONAL STAIRCASE ═══ */}
      {staircaseSteps.length > 1 && (
        <div id="rev-emotion" className="mb-6 rounded-2xl border border-rose-200/80 bg-gradient-to-br from-rose-50/60 to-white p-5 shadow-sm">
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">Emotional Staircase</div>
          <div className="text-[10px] text-white/70 mb-4">Your reader ascends from pain to promise — each step builds on the last</div>
          <div className="flex items-end gap-2" style={{ height: "180px" }}>
            {staircaseSteps.map((s, i) => {
              const heightPx = 40 + (i / Math.max(staircaseSteps.length - 1, 1)) * 140;
              return (
                <div key={i} className="flex-1 flex flex-col items-center" style={{ height: "100%", justifyContent: "flex-end" }}>
                  <div className="text-[9px] font-bold text-white text-center mb-1 leading-tight">{s.label}</div>
                  <div className="w-full rounded-t-lg relative" style={{ height: `${heightPx}px`, backgroundColor: s.color + '30', borderLeft: `3px solid ${s.color}`, borderTop: `3px solid ${s.color}`, borderRight: `1px solid ${s.color}40` }}>
                    <div className="absolute top-1.5 left-1/2 -translate-x-1/2 w-5 h-5 rounded-full flex items-center justify-center text-[8px] font-black text-white" style={{ backgroundColor: s.color }}>{i + 1}</div>
                    <div className="absolute bottom-1.5 left-1/2 -translate-x-1/2 text-[7px] text-white/70 whitespace-nowrap">{s.sub}</div>
                  </div>
                </div>
              );
            })}
          </div>
          <div className="mt-4 flex justify-center gap-3">
            {_EC.map((cat) => {
              const selected = emotions.find(e => cat.items.includes(e));
              return (
                <div key={cat.name} className={`text-center ${selected ? '' : 'opacity-20'}`}>
                  <div className="text-base">{cat.icon}</div>
                  <div className="text-[7px] text-white/70">{selected || '—'}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ═══ 5. TOPIC ANGLE STRATEGY ═══ */}
      {topicAnglePairs.length > 0 && (
        <div id="rev-topics" className="mb-6 rounded-2xl border border-indigo-200/80 bg-gradient-to-br from-indigo-50/60 to-white p-5 shadow-sm">
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">Topic × Angle Strategy</div>
          <div className="space-y-4">
            {topicAnglePairs.map(p => {
              const af = _AF[p.angle];
              const am = ANGLE_MARKET[p.angle] || {};
              const tm = TOPIC_MARKET[p.category] || {};
              const comboScore = Math.round(((am.viral || 0) + (am.conversion || 0) + (tm.search || 0) + (tm.monetization || 0)) / 4);
              return (
                <div key={p.tagId} className="rounded-xl p-3 border" style={{ borderColor: p.catColor + '30', backgroundColor: p.catColor + '06' }}>
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className="text-sm">{p.catIcon}</span>
                    <span className="text-[11px] font-bold text-white flex-1">{p.tagId.replace(/-/g, " ")}</span>
                    <span className="text-[9px] px-2 py-0.5 rounded-full font-bold" style={{ backgroundColor: p.catColor + '15', color: p.catColor }}>{af?.icon} {af?.label}</span>
                  </div>
                  <p className="text-[10px] text-white/70 leading-relaxed mb-2">{p.bullet}</p>
                  {/* Market mini-bars */}
                  <div className="grid grid-cols-2 gap-x-3 gap-y-1">
                    {[
                      { label: "Viral", val: am.viral, color: "#f43f5e" },
                      { label: "Search", val: tm.search, color: "#0ea5e9" },
                      { label: "Convert", val: am.conversion, color: "#059669" },
                      { label: "Growth", val: tm.growth, color: "#f59e0b" },
                    ].map(b => (
                      <div key={b.label} className="flex items-center gap-1.5">
                        <span className="text-[8px] text-white/70 w-10 flex-shrink-0">{b.label}</span>
                        <div className="flex-1 h-2 bg-gray-800/30 rounded-lg overflow-hidden">
                          <div data-bar className="h-full rounded-lg" style={{ width: `${b.val || 0}%`, backgroundColor: b.color }} />
                        </div>
                        <span className="text-[8px] font-bold w-5 text-right" style={{ color: b.color }}>{b.val || 0}</span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-[9px] font-bold px-2 py-0.5 rounded-full" style={{ backgroundColor: comboScore >= 75 ? '#05966920' : comboScore >= 60 ? '#f59e0b20' : '#f43f5e20', color: comboScore >= 75 ? '#059669' : comboScore >= 60 ? '#f59e0b' : '#f43f5e' }}>
                      Combo Score: {comboScore}
                    </span>
                    <span className="text-[8px] text-white/70">{tm.platform && `Best on ${tm.platform}`}</span>
                  </div>
                </div>
              );
            })}
          </div>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {uniqueAngles.map(a => {
              const info = _AF[a];
              return <span key={a} className="text-[9px] bg-indigo-100 text-white px-2 py-1 rounded-full font-semibold">{info?.icon} {info?.label}</span>;
            })}
          </div>
        </div>
      )}

      {/* ═══ 6. CONTENT ENGINE FORMULA — dashboard flow ═══ */}
      <div id="rev-engine" className="mb-6 rounded-2xl border border-amber-200/80 bg-gradient-to-br from-amber-50/40 to-white p-5 shadow-sm">
        <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-1">Content Engine Formula</div>
        <div className="text-[10px] text-white/70 mb-5">Every piece of content follows this sequence — your unique flywheel</div>
        {/* Horizontal flow */}
        <div className="grid grid-cols-4 gap-0 relative">
          {engineSteps.map((s, i) => (
            <div key={i} className="relative flex flex-col items-center text-center">
              {/* Connector line */}
              {i < engineSteps.length - 1 && (
                <div className="absolute top-5 left-[55%] w-[90%] h-0.5 z-0" style={{ background: 'linear-gradient(90deg, #b45309, #d9770640)' }} />
              )}
              {/* Number circle */}
              <div className="relative z-10 w-10 h-10 rounded-full flex items-center justify-center text-lg mb-2" style={{ backgroundColor: '#b4530920', border: '2px solid #b45309' }}>
                {s.icon}
              </div>
              {/* Step number */}
              <div className="text-[8px] font-bold uppercase tracking-widest text-white/50 mb-1">Step {i + 1}</div>
              {/* Title */}
              <div className="text-[11px] font-bold text-white leading-tight mb-1">{s.step}</div>
              {/* Description */}
              <div className="text-[9px] text-white/70 leading-relaxed px-1">{s.desc}</div>
            </div>
          ))}
        </div>
        {/* Repeat arrow */}
        <div className="mt-4 flex items-center justify-center gap-2">
          <div className="h-px flex-1" style={{ background: 'linear-gradient(90deg, transparent, #b4530940, transparent)' }} />
          <span className="text-[9px] font-bold text-white/50 uppercase tracking-wider">↻ Repeat with every piece</span>
          <div className="h-px flex-1" style={{ background: 'linear-gradient(90deg, transparent, #b4530940, transparent)' }} />
        </div>
      </div>

      {/* ═══ 7. UNFAIR ADVANTAGE LOOP — circular diagram ═══ */}
      <div id="rev-loop" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">Unfair Advantage Loop</div>
        <div className="text-[10px] text-white/70 mb-4 text-center">Every piece of content feeds the next — each exit is an entrance to deeper transformation</div>
        <svg viewBox="0 0 320 320" className="w-full max-w-[300px] mx-auto">
          {/* Connecting arc arrows */}
          <defs>
            <marker id="loopArrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
              <polygon points="0 0, 8 3, 0 6" fill="#6b7280" />
            </marker>
          </defs>
          {/* Curved paths between nodes */}
          <path d="M 205 68 Q 250 100 245 155" fill="none" stroke="#6b728040" strokeWidth="2" markerEnd="url(#loopArrow)" />
          <path d="M 245 195 Q 250 250 205 270" fill="none" stroke="#6b728040" strokeWidth="2" markerEnd="url(#loopArrow)" />
          <path d="M 115 270 Q 70 250 65 195" fill="none" stroke="#6b728040" strokeWidth="2" markerEnd="url(#loopArrow)" />
          <path d="M 65 155 Q 70 100 115 68" fill="none" stroke="#6b728040" strokeWidth="2" markerEnd="url(#loopArrow)" />
          {/* Center label */}
          <text x="160" y="156" textAnchor="middle" fontSize="9" fill="#9ca3af" fontWeight="bold">↻ LOOP</text>
          <text x="160" y="170" textAnchor="middle" fontSize="7" fill="#6b7280">repeats</text>
          {/* Nodes */}
          {loopSteps.map((s, i) => {
            const positions = [
              { x: 160, y: 52 },   // top
              { x: 262, y: 168 },  // right
              { x: 160, y: 280 },  // bottom
              { x: 58, y: 168 },   // left
            ];
            const { x, y } = positions[i];
            return (
              <g key={i}>
                <circle cx={x} cy={y} r="44" fill={s.color + '12'} stroke={s.color} strokeWidth="2.5" />
                <circle cx={x} cy={y - 10} r="12" fill={s.color} />
                <text x={x} y={y - 6} textAnchor="middle" fontSize="11" fontWeight="900" fill="white">{i + 1}</text>
                <text x={x} y={y + 10} textAnchor="middle" fontSize="12" fontWeight="bold" fill={s.color}>{s.label}</text>
                <text x={x} y={y + 24} textAnchor="middle" fontSize="8" fill="#9ca3af">{s.desc}</text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* ═══ 8. AUDIENCE EXPERIENCE WALKTHROUGH ═══ */}
      {persona && moment && (
        <div id="rev-journey" className="mb-6 rounded-2xl border border-emerald-200/80 bg-gradient-to-br from-emerald-50/40 to-white p-5 shadow-sm">
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">Audience Experience</div>
          <div className="text-[10px] text-white/70 mb-3">How {persona.emoji} {persona.label} experiences your brand:</div>
          <div className="flex flex-col items-center gap-1.5">
            {[
              { phase: "Trigger", desc: `${moment.emoji} ${moment.scene}`, color: "#f43f5e", bg: "bg-rose-50" },
              { phase: "Discovery", desc: `They find your content — the hook names their exact pain`, color: "#f59e0b", bg: "bg-amber-50" },
              { phase: "Trust", desc: `Your ${voiceDesc[0]} voice makes them feel ${voiceDesc[2]} — not lectured, understood`, color: "#3b82f6", bg: "bg-blue-50" },
              { phase: "Shift", desc: emotions[0] ? `They start to feel: "${emotions[0]}"` : "The promised emotion lands", color: "#059669", bg: "bg-emerald-50" },
              { phase: "Return", desc: `They come back because every piece delivers the same transformation at deeper levels`, color: "#7c3aed", bg: "bg-violet-50" },
            ].reverse().map((p, i, arr) => {
              const widthPct = 40 + ((arr.length - 1 - i) / (arr.length - 1)) * 60;
              const stepNum = arr.length - i;
              return (
                <div key={i} className={`rounded-xl p-3 ${p.bg} border transition-all`} style={{ width: `${widthPct}%`, borderColor: p.color + '40' }}>
                  <div className="flex items-center gap-2">
                    <div className="flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-black text-white" style={{ backgroundColor: p.color }}>{stepNum}</div>
                    <span className="text-[10px] font-bold" style={{ color: p.color }}>{p.phase}</span>
                  </div>
                  <p className="text-[9px] text-white/70 mt-1 leading-relaxed">{p.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ═══ 9. VOICE × TOPIC SYNERGY — research-scored ═══ */}
      {topicAnglePairs.length > 0 && (
        <div id="rev-synergy" className="mb-6 rounded-2xl border border-violet-200/80 bg-gradient-to-br from-violet-50/40 to-white p-5 shadow-sm">
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">Voice × Topic Synergy</div>
          <div className="text-[10px] text-white/70 mb-3">How well your voice tone amplifies each content angle</div>
          <div className="space-y-3">
            {topicAnglePairs.map((p, i) => {
              const af = _AF[p.angle];
              const score = calcSynergyScore(voicePositions, p.angle);
              const multiplier = (0.5 + (score / 100) * 1.5).toFixed(1);
              const barColor = p.catColor;
              const gentlePos = voicePositions.find(v => v.id === "gentleDirect")?.position || 5;
              const toneWord = gentlePos <= 3 ? "gently" : gentlePos >= 8 ? "directly" : "clearly";
              return (
                <div key={i} className="rounded-xl bg-white p-3 border border-violet-100">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm">{p.catIcon}</span>
                    <span className="text-[10px] text-white flex-1">
                      You <strong>{toneWord}</strong> {af?.label?.toLowerCase()} <strong>{p.tagId.replace(/-/g, " ")}</strong>
                    </span>
                    <span className="text-[9px]">{af?.icon}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-3 bg-gray-800/30 rounded-lg overflow-hidden">
                      <div data-bar className="h-full rounded-lg transition-all duration-700" style={{ width: `${score}%`, backgroundColor: barColor }} />
                    </div>
                    <span className="text-[11px] font-black w-8 text-right" style={{ color: barColor }}>{score}</span>
                    <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full" style={{ backgroundColor: barColor + '15', color: barColor }}>{multiplier}x</span>
                  </div>
                </div>
              );
            })}
          </div>
          {/* Average synergy */}
          {(() => {
            const avgSynergy = Math.round(topicAnglePairs.reduce((s, p) => s + calcSynergyScore(voicePositions, p.angle), 0) / topicAnglePairs.length);
            const avgColor = avgSynergy >= 75 ? '#059669' : avgSynergy >= 50 ? '#f59e0b' : '#f43f5e';
            return (
              <div className="mt-3 flex items-center justify-between rounded-lg bg-violet-50 border border-violet-100 p-2.5">
                <span className="text-[10px] font-bold text-white">Overall Voice Fit</span>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-black" style={{ color: avgColor }}>{avgSynergy}</span>
                  <span className="text-[9px] text-white/70">/100</span>
                </div>
              </div>
            );
          })()}
        </div>
      )}




      {/* ═══ 13. BRAND STRENGTH — research-scored ═══ */}
      {(() => {
        // Visual market scores
        const vm = VISUAL_MARKET[visual?.id] || {};
        const visualAvg = vm.shelf ? Math.round((vm.shelf + vm.trust + vm.social + vm.premium) / 4) : 0;

        // Angle+topic combo scores — average across all selected pairs
        const pairScores = topicAnglePairs.map(p => {
          const am = ANGLE_MARKET[p.angle] || {};
          const tm = TOPIC_MARKET[p.category] || {};
          return {
            viral: am.viral || 0, trust: am.trust || 0, conversion: am.conversion || 0, seo: am.seo || 0,
            search: tm.search || 0, growth: tm.growth || 0, monetization: tm.monetization || 0,
          };
        });
        const avg = (key) => pairScores.length ? Math.round(pairScores.reduce((s, p) => s + p[key], 0) / pairScores.length) : 0;

        // 6-axis radar: Visual, Viral, Trust, Conversion, SEO, Growth
        const dims = [
          { label: "Visual", val: visualAvg, color: "#7c3aed" },
          { label: "Viral", val: avg("viral"), color: "#f43f5e" },
          { label: "Trust", val: avg("trust"), color: "#059669" },
          { label: "Convert", val: avg("conversion"), color: "#f59e0b" },
          { label: "SEO", val: avg("seo"), color: "#0ea5e9" },
          { label: "Growth", val: avg("growth"), color: "#6366f1" },
        ];
        const overallScore = Math.round(dims.reduce((s, d) => s + d.val, 0) / dims.length);
        const sides = 6, cx = 150, cy = 110, r = 75;

        return (
          <div id="rev-radar" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <div className="text-[10px] font-bold uppercase tracking-wider text-white">Brand Strength</div>
              <div className="flex items-center gap-2">
                <span className={`text-lg font-black ${overallScore >= 75 ? 'text-emerald-500' : overallScore >= 55 ? 'text-amber-500' : 'text-rose-400'}`}>{overallScore}</span>
                <span className="text-[9px] text-white/70">/100</span>
              </div>
            </div>
            <svg viewBox="0 0 300 230" className="w-full" style={{ height: "220px" }}>
              {(() => {
                const outerPts = [], innerPts = [];
                for (let i = 0; i < sides; i++) {
                  const angle = (Math.PI * 2 * i) / sides - Math.PI / 2;
                  outerPts.push(`${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`);
                  const val = dims[i].val / 100;
                  innerPts.push(`${cx + r * val * Math.cos(angle)},${cy + r * val * Math.sin(angle)}`);
                }
                return (<>
                  <polygon fill="none" stroke="#e5e7eb" strokeWidth="1" points={outerPts.join(" ")} />
                  <polygon fill="none" stroke="#e5e7eb" strokeWidth="0.5" strokeDasharray="3" points={outerPts.map((_, i) => { const a = (Math.PI * 2 * i) / sides - Math.PI / 2; return `${cx + r * 0.5 * Math.cos(a)},${cy + r * 0.5 * Math.sin(a)}`; }).join(" ")} />
                  <polygon fill="#6366f1" fillOpacity="0.12" stroke="#6366f1" strokeWidth="2.5" points={innerPts.join(" ")} />
                  {dims.map((d, i) => {
                    const a = (Math.PI * 2 * i) / sides - Math.PI / 2;
                    const lx = cx + (r + 22) * Math.cos(a);
                    const ly = cy + (r + 22) * Math.sin(a);
                    return (<g key={d.label}>
                      <text x={lx} y={ly - 5} textAnchor="middle" dominantBaseline="middle" fontSize="10" fontWeight="bold" fill={d.color}>{d.val}</text>
                      <text x={lx} y={ly + 7} textAnchor="middle" dominantBaseline="middle" fontSize="8" fontWeight="600" fill="#9ca3af">{d.label}</text>
                    </g>);
                  })}
                  {dims.map((d, i) => { const a = (Math.PI * 2 * i) / sides - Math.PI / 2; const val = d.val / 100; return (<circle key={i} cx={cx + r * val * Math.cos(a)} cy={cy + r * val * Math.sin(a)} r="4" fill={d.color} stroke="white" strokeWidth="2" />); })}
                </>);
              })()}
            </svg>
            {/* Score breakdown bars */}
            <div className="space-y-1.5 mt-2">
              {dims.map(d => (
                <div key={d.label} className="flex items-center gap-2">
                  <span className="text-[8px] text-white/70 w-12 flex-shrink-0">{d.label}</span>
                  <div className="flex-1 h-2 bg-gray-800/30 rounded-lg overflow-hidden">
                    <div data-bar className="h-full rounded-lg transition-all duration-700" style={{ width: `${d.val}%`, backgroundColor: d.color }} />
                  </div>
                  <span className="text-[9px] font-bold w-6 text-right" style={{ color: d.color }}>{d.val}</span>
                </div>
              ))}
            </div>
          </div>
        );
      })()}

      {/* ═══ 14. ONE-SENTENCE SYNTHESIS ═══ */}
      {arch && persona && (
        <div id="rev-synthesis" className="rounded-2xl border-2 border-violet-300 bg-gradient-to-br from-violet-900 to-indigo-900 p-6 shadow-lg">
          <div className="text-violet-300/70 text-[10px] font-bold uppercase tracking-[0.3em] mb-3 text-center">Brand Synthesis</div>
          <p className="text-center text-white text-sm leading-relaxed font-medium">
            You are <strong>{arch.name}</strong> — a {voiceDesc[0]}, {voiceDesc[1]} voice that catches{" "}
            <strong>{persona.label}</strong>
            {moment && <> at their <em>{moment.label.toLowerCase()}</em> moment</>},{" "}
            {uniqueAngles.length > 0 && <>uses {uniqueAngles.map(a => _AF[a]?.label?.toLowerCase()).join(" + ")} angles to</>}{" "}
            {emotions.length > 0
              ? <>deliver one promise: <strong>"{emotions[0]}"</strong></>
              : <>deliver transformation</>
            }.
          </p>
        </div>
      )}
    </div>
  );
}

function Step10Blueprint_UNUSED({ state }) {
  const arch = ARCHETYPES.find((a) => a.id === state.archetype);
  const persona = PERSONAS.find((p) => p.id === state.persona);
  const moment = MOMENTS.find((m) => m.id === state.moment);
  const visual = VISUAL_STYLES.find((v) => v.id === state.visualStyle);

  const baseScore = 72;
  const marketability = Math.min(Math.round(baseScore + (state.archetype ? 8 : 0) + (state.persona ? 6 : 0) + ((state.topicTags || []).length > 3 ? 5 : (state.topicTags || []).length > 0 ? 3 : 0)), 97);
  const youthReach = Math.min(Math.round(65 + (state.formatFocus === "manga" ? 20 : 8) + ((state.channels || []).includes("tiktok") ? 8 : 0) + (state.persona === "gen_alpha" || state.persona === "gen_z_seeker" ? 7 : 3)), 98);
  const lifeImpact = Math.min(Math.round(baseScore + (state.moment ? 5 : 0) + (Object.keys(state.voiceSettings || {}).length > 0 ? 4 : 0) + (state.visualStyle ? 3 : 0) + 5), 96);
  const reachScore = Math.min(Math.round(70 + Math.min((state.channels || []).length * 1.5, 6) + (state.formatFocus ? 4 : 0) + (state.archetype ? 8 : 0)), 95);

  const scores = [
    { label: "Marketability", value: marketability, desc: "Alignment with proven market demand" },
    { label: "Youth Reach", value: youthReach, desc: "Gen Z and Gen Alpha compatibility" },
    { label: "Life Impact", value: lifeImpact, desc: "Transformation depth for your reader" },
    { label: "Platform Reach", value: reachScore, desc: "Multi-channel distribution coverage" },
  ];

  const brandOneSentence = [
    arch?.name,
    persona && `${persona.emoji} ${persona.label}`,
    moment && `${moment.emoji} ${moment.label}`,
  ]
    .filter(Boolean)
    .join(" · ");

  const assessmentText =
    marketability >= 85
      ? "Exceptional brand positioning. Your archetype, audience, and topic choices align powerfully with high-revenue market segments. This brand has strong commercial potential with deep reader impact."
      : marketability >= 75
        ? "Strong brand foundation. Your selections create a compelling identity with solid market alignment. A few more refinements could push this into exceptional territory."
        : "Good starting point. Your brand identity is taking shape — consider adding more topic selections and channel coverage to strengthen your market position.";

  return (
    <div>
      <StepHero
        eyebrow="Reveal"
        title="Here is your brand"
        subtitle="Your choices — distilled first, then grouped so you can read the arc at a glance."
      />

      {brandOneSentence ? (
        <p className="mb-8 rounded-2xl border border-violet-300/80 bg-gradient-to-br from-violet-50 via-white to-fuchsia-50/60 px-5 py-6 text-center text-lg font-extrabold leading-snug tracking-tight text-violet-950 shadow-md [text-shadow:0_1px_0_rgba(255,255,255,0.9)] sm:text-xl sm:leading-snug">
          {brandOneSentence}
        </p>
      ) : null}

      <div className="mb-6 rounded-2xl border border-indigo-100 bg-indigo-50/40 px-4 py-3">
        <p className="text-[10px] font-bold uppercase tracking-wider text-indigo-800">Audiobook voice — preview</p>
        <p className="mt-1 text-[11px] text-white">Regulating narrator on the comfort benchmark (registry: <span className="font-mono text-[10px]">cmp_voice_narrator_contrast_v1</span>).</p>
        <audio className="mt-2 block h-9 w-full max-w-md" controls preload="metadata" src="/onboarding/audio/voice_cmp_comfort_voice_regulating_female.mp3" />
      </div>

      <div className="space-y-8">
        <section className="rounded-2xl border border-slate-200/90 bg-slate-50/50 p-4 shadow-sm ring-1 ring-slate-200/70 sm:p-5">
          <h3 className="mb-4 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">1 · Brand identity</h3>
          <div className="space-y-3">
            {arch ? (
              <div className={`rounded-2xl border-2 p-5 ${arch.bg} ${arch.border}`}>
                <div className="text-[10px] font-bold uppercase text-white">Emotional world</div>
                <div className="mt-1 text-xl font-bold text-white">{arch.name}</div>
                <p className="mt-1 text-sm text-white">{arch.tagline}</p>
              </div>
            ) : null}
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {persona ? (
                <div className="rounded-2xl border border-violet-200/90 bg-white p-4 shadow-md ring-1 ring-violet-100/80">
                  <div className="text-[10px] font-bold uppercase text-violet-600/90">Primary reader</div>
                  <div className="mt-1.5 text-base font-extrabold leading-snug text-white sm:text-lg">
                    {persona.emoji} {persona.label}
                  </div>
                </div>
              ) : null}
              {moment ? (
                <div className="rounded-2xl border border-amber-200/90 bg-white p-4 shadow-md ring-1 ring-amber-100/80">
                  <div className="text-[10px] font-bold uppercase text-amber-700/90">Trigger moment</div>
                  <div className="mt-1.5 text-base font-extrabold leading-snug text-white sm:text-lg">
                    {moment.emoji} {moment.label}
                  </div>
                </div>
              ) : null}
              {state.tradition ? (
                <div className="rounded-2xl border border-gray-200/90 bg-white/90 p-4 shadow-sm sm:col-span-2">
                  <div className="text-[10px] font-bold uppercase text-white">Tradition</div>
                  <div className="mt-1 text-sm font-semibold text-white">{state.tradition}</div>
                </div>
              ) : null}
            </div>
          </div>
        </section>

        <section className="rounded-2xl border border-violet-200/80 bg-violet-50/35 p-4 shadow-sm ring-1 ring-violet-200/60 sm:p-5">
          <h3 className="mb-4 text-[10px] font-bold uppercase tracking-[0.2em] text-violet-700/90">2 · How it shows up</h3>
          <div className="space-y-3">
            {visual ? (
              <div className="overflow-hidden rounded-2xl border-2 border-white bg-white shadow-md ring-1 ring-violet-200/80">
                <div className="flex gap-2 border-b border-gray-100 bg-gradient-to-r from-slate-50 to-violet-50/40 px-4 py-3">
                  {visual.palette.map((col, i) => (
                    <div key={i} className="h-10 w-10 rounded-xl shadow-md ring-2 ring-white" style={{ backgroundColor: col }} />
                  ))}
                </div>
                <div className="p-4">
                  <div className="text-[10px] font-bold uppercase text-violet-600">Visual style</div>
                  <div className="mt-1 text-base font-bold text-white">{visual.label}</div>
                  <p className="mt-1 text-xs text-white">{visual.desc}</p>
                  <p className="mt-2 text-[11px] italic text-white">{visual.mood}</p>
                </div>
              </div>
            ) : null}
            <div className="text-[9px] font-bold uppercase tracking-wider text-violet-600/70">Publishing context</div>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
              {state.onboardingLane ? (
                <div className="rounded-xl border border-violet-100/90 bg-white/80 p-2.5 text-center opacity-90">
                  <div className="text-[8px] font-bold uppercase text-white">Lane</div>
                  <div className="mt-0.5 text-[11px] font-semibold text-white">{state.onboardingLane.replace(/_/g, " ")}</div>
                </div>
              ) : null}
              {state.onboardingMarket ? (
                <div className="rounded-xl border border-violet-100/90 bg-white/80 p-2.5 text-center opacity-90">
                  <div className="text-[8px] font-bold uppercase text-white">Market</div>
                  <div className="mt-0.5 text-[11px] font-semibold text-white">{state.onboardingMarket}</div>
                </div>
              ) : null}
              {state.formatFocus ? (
                <div className="rounded-xl border border-violet-100/90 bg-white/80 p-2.5 text-center opacity-90">
                  <div className="text-[8px] font-bold uppercase text-white">Format</div>
                  <div className="mt-0.5 text-[11px] font-semibold text-white">{state.formatFocus === "manga" ? "Manga / visual" : "Books"}</div>
                </div>
              ) : null}
              {(state.channels || []).length > 0 ? (
                <div className="rounded-xl border border-violet-100/90 bg-white/80 p-2.5 text-center opacity-90">
                  <div className="text-[8px] font-bold uppercase text-white">Channels</div>
                  <div className="mt-0.5 text-[11px] font-semibold text-white">{state.channels.length} active</div>
                </div>
              ) : null}
            </div>
          </div>
        </section>

        <section className="rounded-2xl border border-rose-200/80 bg-gradient-to-br from-rose-50/50 to-amber-50/20 p-4 shadow-sm ring-1 ring-rose-200/50 sm:p-5">
          <h3 className="mb-3 text-[10px] font-bold uppercase tracking-[0.2em] text-rose-800/80">3 · What it promises</h3>
          {(state.emotions || []).length > 0 ? (
            <div className="mb-4 rounded-2xl border border-rose-100 bg-gradient-to-br from-rose-50/80 to-amber-50/40 p-4 shadow-sm">
              <div className="text-[10px] font-bold uppercase text-rose-800/90">Emotional outcomes</div>
              <div className="mt-3 flex flex-wrap gap-2">
                {state.emotions.map((e) => (
                  <span
                    key={e}
                    className="rounded-full border border-white/80 bg-white/90 px-3 py-1.5 text-xs font-semibold text-rose-950 shadow-sm"
                  >
                    {e}
                  </span>
                ))}
              </div>
            </div>
          ) : null}
          {(state.topicTags || []).length > 0 ? (
            <div className="mb-4 rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
              <div className="text-[10px] font-bold uppercase text-white">Topics ({state.topicTags.length})</div>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {state.topicTags.map((t) => (
                  <span key={t} className="rounded-full bg-gray-100 px-2.5 py-1 text-[10px] font-medium text-white">
                    {t.replace(/-/g, " ")}
                  </span>
                ))}
              </div>
            </div>
          ) : null}
          {(state.angles || []).length > 0 ? (
            <div className="mb-4 rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
              <div className="text-[10px] font-bold uppercase text-white">Content angles</div>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {state.angles.map((a) => {
                  const angle = V4_ANGLES.find((v) => v.id === a);
                  return (
                    <span key={a} className="rounded-full bg-indigo-50 px-2.5 py-1 text-[10px] font-semibold text-indigo-900">
                      {angle?.label || a}
                    </span>
                  );
                })}
              </div>
            </div>
          ) : null}
          <div className="rounded-2xl border border-emerald-200 bg-gradient-to-r from-emerald-50/90 to-teal-50/50 p-4">
            <div className="flex items-center gap-2">
              <Rocket size={16} className="text-emerald-600" />
              <span className="text-xs font-bold text-emerald-900">Read on your direction</span>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-emerald-900/90">{assessmentText}</p>
          </div>
        </section>
      </div>

      {/* Demoted score strip — same numeric logic, after narrative sections */}
      <div className="mt-10 rounded-2xl border border-gray-100 bg-gray-50/60 px-3 py-3 opacity-90">
        <div className="mb-2 text-center text-[9px] font-bold uppercase tracking-wider text-white">Signal scores</div>
        <div className="grid grid-cols-4 gap-2">
          {scores.map((s) => (
            <div key={s.label} className="rounded-lg bg-white/90 px-1 py-2 text-center shadow-sm">
              <div className="relative mx-auto mb-1 h-10 w-10">
                <svg viewBox="0 0 64 64" className="h-full w-full -rotate-90">
                  <circle cx="32" cy="32" r="26" fill="none" stroke="#f3f4f6" strokeWidth="4" />
                  <circle
                    cx="32"
                    cy="32"
                    r="26"
                    fill="none"
                    strokeWidth="4"
                    strokeLinecap="round"
                    style={{ color: s.value > 85 ? "#10b981" : s.value > 70 ? "#6366f1" : "#f59e0b" }}
                    className="stroke-current"
                    strokeDasharray={`${s.value * 1.63} 163`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-xs font-black text-white">{s.value}</span>
                </div>
              </div>
              <div className="text-[8px] font-bold uppercase leading-tight text-white">{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Step11Launch({ state, update, i18n = {} }) {
  const { tArchetypes: _A = ARCHETYPES, tPersonas: _P = PERSONAS, tMoments: _M = MOMENTS, tVisualStyles: _V = VISUAL_STYLES, tSelectionFeedback: _SF = SELECTION_FEEDBACK } = i18n;
  const handleField = (field, val) => update({ contact: { ...state.contact, [field]: val } });
  const c = state.contact || {};
  const isReady = c.firstName?.trim() && c.lastName?.trim() && c.email?.trim() && c.email?.includes("@");
  const [submitted, setSubmitted] = useState(false);
  const [yamlOutput, setYamlOutput] = useState("");
  const [showYaml, setShowYaml] = useState(false);
  const [yamlCopied, setYamlCopied] = useState(false);

  const handleLaunch = () => { setYamlOutput(generateYAML(state)); setSubmitted(true); };

  if (submitted) {
    const arch = _A.find((a) => a.id === state.archetype);
    const persona = _P.find((p) => p.id === state.persona);
    const moment = _M.find((m) => m.id === state.moment);
    const visual = _V.find((v) => v.id === state.visualStyle);

    const choiceAudit = [
      arch && { label: "Emotional World", value: arch.name, icon: arch.icon, gradient: arch.gradient, systemEffect: _SF.archetypes[state.archetype]?.systemEffect, emotionalBenefit: _SF.archetypes[state.archetype]?.emotionalBenefit },
      persona && { label: "Primary Reader", value: `${persona.emoji} ${persona.label}`, icon: Users, gradient: "from-blue-500 to-cyan-500", systemEffect: _SF.personas[state.persona]?.systemEffect, emotionalBenefit: _SF.personas[state.persona]?.emotionalBenefit },
      moment && { label: "Trigger Moment", value: `${moment.emoji} ${moment.label}`, icon: Target, gradient: "from-amber-500 to-orange-500", systemEffect: _SF.moments[state.moment]?.systemEffect, emotionalBenefit: _SF.moments[state.moment]?.emotionalBenefit },
      Object.keys(state.voiceSettings || {}).length > 0 && { label: "Voice Tone", value: `${Object.keys(state.voiceSettings).length} dimensions tuned`, icon: SlidersHorizontal, gradient: "from-indigo-500 to-violet-500", systemEffect: "All 4 voice dimensions calibrate prose rhythm, vocabulary register, sentence structure, and emotional temperature across every chapter, audiobook, and social post", emotionalBenefit: "Your reader experiences a voice that feels personally written for them — the exact blend of challenge and comfort they need. Every sentence lands because the tone matches their emotional readiness." },
      visual && { label: "Visual Style", value: visual.label, icon: Palette, gradient: "from-rose-500 to-pink-500", systemEffect: _SF.visualStyles[state.visualStyle]?.systemEffect, emotionalBenefit: _SF.visualStyles[state.visualStyle]?.emotionalBenefit },
      (state.emotions || []).length > 0 && { label: "Emotional Outcomes", value: state.emotions.join(", "), icon: Heart, gradient: "from-rose-400 to-red-500", systemEffect: `${state.emotions.length} transformation promises woven into every title, CTA, and marketing message`, emotionalBenefit: "These feelings become the north star of every piece of content — your reader knows exactly what transformation awaits them, creating hope before they read a single word." },
      state.tradition && { label: "Spiritual Foundation", value: state.tradition, icon: Sun, gradient: "from-amber-400 to-yellow-500", systemEffect: "Influences vocabulary, philosophical grounding, and tradition-specific references throughout all content", emotionalBenefit: "Readers with this tradition feel recognized and respected. The language carries the weight of authentic lineage rather than surface-level appropriation." },
      (state.angles || []).length > 0 && { label: "Content Angles", value: state.angles.map(a => V4_ANGLES.find(v => v.id === a)?.label).filter(Boolean).join(", "), icon: Layers, gradient: "from-purple-500 to-indigo-500", systemEffect: `${state.angles.length} framing modes active — every title opens with one of these argumentative strategies`, emotionalBenefit: "Each angle gives your reader a different doorway into healing. Multiple angles means your brand reaches people wherever they are in their readiness for change." },
      (state.topicTags || []).length > 0 && { label: "Search Territory", value: `${state.topicTags.length} topics claimed`, icon: Search, gradient: "from-emerald-500 to-teal-500", systemEffect: `${state.topicTags.length} search topics feed into title generation, keyword targeting, series planning, and ad campaigns`, emotionalBenefit: "Your content appears in the exact moment someone types their pain into a search bar. You're not marketing — you're answering a cry for help with exactly the right words." },
      state.onboardingLane && { label: "Onboarding Lane", value: state.onboardingLane.replace(/_/g, " "), icon: Layers, gradient: "from-fuchsia-500 to-purple-500", systemEffect: "Proof strip and registry matching now constrain to your selected lane so stakeholders preview the right output family early.", emotionalBenefit: "You can immediately see if the lane you want to lead with has convincing proof, reducing launch-time surprises." },
      state.onboardingMarket && { label: "Onboarding Market", value: state.onboardingMarket, icon: Globe, gradient: "from-sky-500 to-cyan-500", systemEffect: "Registry matches now use explicit market filtering during onboarding to avoid cross-market false confidence.", emotionalBenefit: "Your team reviews examples that actually match the market you plan to launch in." },
      state.formatFocus && { label: "Format Focus", value: state.formatFocus === "manga" ? "Manga / Visual" : "Traditional Books", icon: BookOpen, gradient: "from-cyan-500 to-blue-500", systemEffect: _SF.formats[state.formatFocus]?.systemEffect, emotionalBenefit: _SF.formats[state.formatFocus]?.emotionalBenefit },
      (state.channels || []).length > 0 && { label: "Publishing Channels", value: `${state.channels.length} channels active`, icon: Globe, gradient: "from-violet-500 to-purple-500", systemEffect: `Content adapts to ${state.channels.length} platforms — each generates format-specific, algorithm-optimized variations`, emotionalBenefit: "Your reader discovers you wherever they already spend time. Whether it's a 3AM TikTok scroll or a Sunday audiobook walk — your brand is there, ready, in the right format." },
    ].filter(Boolean);

    const baseScore = 72;
    const marketability = Math.min(Math.round(baseScore + (state.archetype ? 8 : 0) + (state.persona ? 6 : 0) + ((state.topicTags || []).length > 3 ? 5 : (state.topicTags || []).length > 0 ? 3 : 0)), 97);
    const youthReach = Math.min(Math.round(65 + (state.formatFocus === "manga" ? 20 : 8) + ((state.channels || []).includes("tiktok") ? 8 : 0) + (state.persona === "gen_alpha" || state.persona === "gen_z_seeker" ? 7 : 3)), 98);
    const lifeImpact = Math.min(Math.round(baseScore + (state.moment ? 5 : 0) + (Object.keys(state.voiceSettings || {}).length > 0 ? 4 : 0) + (state.visualStyle ? 3 : 0) + 5), 96);
    const reachScore = Math.min(Math.round(70 + Math.min((state.channels || []).length * 1.5, 6) + (state.formatFocus ? 4 : 0) + (state.archetype ? 8 : 0)), 95);
    const overallScore = Math.round((marketability + youthReach + lifeImpact + reachScore) / 4);

    return (
      <div className="py-4">
        {/* Celebration Header */}
        <div className="relative text-center mb-8 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-purple-50 via-white to-white rounded-3xl" />
          <div className="relative z-10 py-10 px-6">
            {/* Animated celebration ring */}
            <div className="relative w-28 h-28 mx-auto mb-5">
              <svg viewBox="0 0 112 112" className="w-full h-full">
                <defs>
                  <linearGradient id="congrats-ring" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#7c3aed" />
                    <stop offset="50%" stopColor="#ec4899" />
                    <stop offset="100%" stopColor="#f59e0b" />
                  </linearGradient>
                </defs>
                <circle cx="56" cy="56" r="50" fill="none" stroke="#f3f4f6" strokeWidth="6" />
                <circle cx="56" cy="56" r="50" fill="none" stroke="url(#congrats-ring)" strokeWidth="6" strokeLinecap="round" strokeDasharray={`${overallScore * 3.14} 314`} className="-rotate-90 origin-center" style={{ transition: "stroke-dasharray 1.5s ease-out" }} />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-2xl font-black text-white">{overallScore}</span>
                <span className="text-[8px] font-bold uppercase text-white">Overall</span>
              </div>
            </div>

            {/* Floating celebration dots */}
            <div className="absolute top-4 left-1/4 w-2 h-2 rounded-full bg-purple-300 opacity-60" style={{ animation: "pulse 2s ease-in-out infinite" }} />
            <div className="absolute top-8 right-1/3 w-1.5 h-1.5 rounded-full bg-pink-300 opacity-60" style={{ animation: "pulse 2.5s ease-in-out infinite 0.5s" }} />
            <div className="absolute top-12 left-1/3 w-1 h-1 rounded-full bg-amber-300 opacity-60" style={{ animation: "pulse 3s ease-in-out infinite 1s" }} />
            <div className="absolute top-6 right-1/4 w-2.5 h-2.5 rounded-full bg-emerald-300 opacity-40" style={{ animation: "pulse 2.2s ease-in-out infinite 0.3s" }} />

            <style>{`@keyframes pulse { 0%, 100% { transform: scale(1) translateY(0); opacity: 0.4; } 50% { transform: scale(1.5) translateY(-8px); opacity: 0.8; } }`}</style>

            <h1 className="text-4xl font-black tracking-tight mb-2 bg-gradient-to-r from-purple-600 via-pink-500 to-amber-500 bg-clip-text text-transparent">
              Congratulations
            </h1>
            <p className="text-lg font-bold text-white mb-1">Your brand universe is born.</p>
            <p className="text-sm text-white max-w-md mx-auto leading-relaxed">
              You've made {choiceAudit.length} defining choices that shape everything your brand creates — every book, audiobook, video, cover, and piece of social content. Here's what you've built and how it helps the people who need it most.
            </p>
          </div>
        </div>

        {/* Score Cards */}
        <div className="grid grid-cols-4 gap-2 mb-8">
          {[
            { label: "Marketability", value: marketability, color: "#10b981" },
            { label: "Youth Reach", value: youthReach, color: "#8b5cf6" },
            { label: "Life Impact", value: lifeImpact, color: "#ec4899" },
            { label: "Platform Reach", value: reachScore, color: "#3b82f6" },
          ].map((s) => (
            <div key={s.label} className="text-center bg-white rounded-xl p-3 border border-gray-200 shadow-sm">
              <div className="relative w-12 h-12 mx-auto mb-1.5">
                <svg viewBox="0 0 48 48" className="w-full h-full -rotate-90">
                  <circle cx="24" cy="24" r="20" fill="none" stroke="#f3f4f6" strokeWidth="4" />
                  <circle cx="24" cy="24" r="20" fill="none" stroke={s.color} strokeWidth="4" strokeLinecap="round" strokeDasharray={`${s.value * 1.257} 125.7`} />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center"><span className="text-sm font-black text-white">{s.value}</span></div>
              </div>
              <div className="text-[9px] font-bold uppercase text-white">{s.label}</div>
            </div>
          ))}
        </div>

        {/* Choice Audit — every choice with what it does */}
        <div className="mb-8">
          <h2 className="text-lg font-extrabold text-white mb-1">Your Brand Choices</h2>
          <p className="text-xs text-white mb-4">Every choice you made, what it activates in the system, and how it helps your readers mentally and emotionally.</p>

          <div className="space-y-3">
            {choiceAudit.map((choice, idx) => {
              const Icon = choice.icon;
              return (
                <div key={idx} className="rounded-xl border border-gray-200 bg-white overflow-hidden shadow-sm">
                  <div className="flex items-center gap-3 p-4 border-b border-gray-100">
                    <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${choice.gradient} flex items-center justify-center flex-shrink-0`}>
                      <Icon size={16} className="text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-[9px] font-bold uppercase text-white">{choice.label}</div>
                      <div className="text-sm font-bold text-white truncate">{choice.value}</div>
                    </div>
                    <div className="text-[9px] font-bold text-emerald-500 bg-emerald-50 px-2 py-0.5 rounded-full flex-shrink-0">Active</div>
                  </div>
                  <div className="px-4 py-3 space-y-2.5">
                    <div className="flex items-start gap-2">
                      <div className="w-4 h-4 rounded-full bg-indigo-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Zap size={8} className="text-indigo-500" />
                      </div>
                      <div>
                        <span className="text-[9px] font-bold uppercase text-white">System Effect </span>
                        <p className="text-[11px] text-white leading-relaxed">{choice.systemEffect}</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-4 h-4 rounded-full bg-rose-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Heart size={8} className="text-rose-400" />
                      </div>
                      <div>
                        <span className="text-[9px] font-bold uppercase text-white">Reader Benefit </span>
                        <p className="text-[11px] text-white leading-relaxed font-medium">{choice.emotionalBenefit}</p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Brand Summary Statement */}
        {arch && persona && (
          <div className="rounded-2xl bg-gradient-to-br from-purple-50 via-pink-50 to-amber-50 border border-purple-100 p-6 mb-8">
            <div className="flex items-center gap-2 mb-3">
              <Crown size={16} className="text-purple-600" />
              <span className="text-sm font-bold text-purple-800">Your Brand in One Sentence</span>
            </div>
            <p className="text-sm text-white leading-relaxed font-medium">
              A <span className="text-purple-700 font-bold">{arch.name}</span> brand that speaks to the <span className="text-blue-700 font-bold">{persona.label}</span>
              {moment ? <> in their <span className="text-amber-700 font-bold">{moment.label.toLowerCase()}</span> moment</> : ""},
              with a <span className="text-indigo-700 font-bold">{visual?.label || "distinctive"}</span> visual world
              {state.formatFocus ? <> delivered through <span className="text-cyan-700 font-bold">{state.formatFocus === "manga" ? "manga & visual" : "deep long-form"}</span> formats</> : ""}
              {(state.channels || []).length > 0 ? <> across <span className="text-violet-700 font-bold">{state.channels.length} publishing channels</span></> : ""}.
            </p>
          </div>
        )}

        {/* YAML Output Toggle */}
        <div className="rounded-xl border border-gray-200 overflow-hidden mb-6">
          <button onClick={() => setShowYaml(!showYaml)} className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors">
            <div className="flex items-center gap-2">
              <Download size={14} className="text-white" />
              <span className="text-xs font-bold text-white">Brand Configuration (YAML)</span>
            </div>
            <ChevronRight size={14} className={`text-white transition-transform ${showYaml ? "rotate-90" : ""}`} />
          </button>
          {showYaml && (
            <div className="bg-gray-900 p-4 overflow-auto max-h-96">
              <div className="flex gap-2 mb-3">
                <button onClick={() => { navigator.clipboard.writeText(yamlOutput); setYamlCopied(true); setTimeout(() => setYamlCopied(false), 2000); }}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-bold transition-colors">
                  <Check size={11} />{yamlCopied ? "Copied!" : "Copy"}
                </button>
                <button onClick={() => { const blob = new Blob([yamlOutput], {type: "text/yaml"}); const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "brand-config.yaml"; a.click(); }}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-bold transition-colors">
                  <Download size={11} />Download .yaml
                </button>
              </div>
              <pre className="text-[11px] text-green-400 font-mono whitespace-pre-wrap">{yamlOutput}</pre>
            </div>
          )}
        </div>

        {/* Final Message */}
        <div className="text-center py-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-50 text-emerald-700 text-xs font-bold mb-3">
            <Check size={12} /> Brand configuration saved
          </div>
          <p className="text-sm text-white max-w-md mx-auto">
            Your brand universe is ready. The Pearl Prime system will use every choice you've made to generate your catalog — books, audiobooks, manga, videos, and social content that changes lives.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 rounded-2xl border border-violet-200/80 bg-gradient-to-br from-violet-50/90 via-white to-fuchsia-50/30 px-5 py-6 text-center shadow-sm">
        <h2 className="text-2xl font-extrabold tracking-tight sm:text-3xl" style={{ color: '#d97706', fontFamily: 'Cormorant Garamond, serif' }}>Enter Contact Details And Click 'Activate'</h2>
        <p className="mx-auto mt-3 max-w-md text-sm text-white/70">
          You will immediately gain access to your brand catalog for posting
        </p>
      </div>

      <div
        className="mb-6 flex flex-col items-center gap-2 rounded-xl border border-emerald-100/90 bg-emerald-50/40 px-4 py-3 text-[11px] text-emerald-950/80 sm:flex-row sm:flex-wrap sm:justify-center sm:gap-x-8 sm:gap-y-1"
        role="note"
        aria-label="Before you activate"
      >
        <span className="inline-flex items-center gap-1.5 font-medium">
          <Check size={14} className="shrink-0 text-emerald-600" strokeWidth={2.5} /> Brand direction set
        </span>
        <span className="inline-flex items-center gap-1.5 font-medium">
          <Check size={14} className="shrink-0 text-emerald-600" strokeWidth={2.5} /> Reader and market chosen
        </span>
        <span className="inline-flex items-center gap-1.5 font-medium">
          <Check size={14} className="shrink-0 text-emerald-600" strokeWidth={2.5} /> Launch details ready
        </span>
      </div>

      <div className="mb-6 space-y-6">
        <section className="rounded-2xl border border-gray-200/90 bg-white/90 p-5 shadow-sm backdrop-blur-sm">
          <h3 className="mb-4 text-[10px] font-bold uppercase tracking-[0.15em] text-white">1 · Identity &amp; contact</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-semibold text-white">First name *</label>
              <input
                type="text"
                placeholder="First name"
                className="w-full rounded-xl border border-gray-200 p-3 text-sm outline-none focus:border-gray-500"
                value={c.firstName || ""}
                onChange={(e) => handleField("firstName", e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold text-white">Last name *</label>
              <input
                type="text"
                placeholder="Last name"
                className="w-full rounded-xl border border-gray-200 p-3 text-sm outline-none focus:border-gray-500"
                value={c.lastName || ""}
                onChange={(e) => handleField("lastName", e.target.value)}
              />
            </div>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-semibold text-white">Email *</label>
              <input
                type="email"
                placeholder="you@example.com"
                className="w-full rounded-xl border border-gray-200 p-3 text-sm outline-none focus:border-gray-500"
                value={c.email || ""}
                onChange={(e) => handleField("email", e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold text-white">Phone</label>
              <div className="flex rounded-xl border border-gray-200 overflow-hidden">
                <select
                  className="bg-transparent border-r border-gray-200 px-2 py-3 text-sm outline-none appearance-none cursor-pointer"
                  value={c.phoneCode || "+1"}
                  onChange={(e) => handleField("phoneCode", e.target.value)}
                  style={{ background: 'rgba(0,0,0,.3)', color: 'rgba(250,246,240,.9)', borderColor: 'rgba(180,83,9,.18)' }}
                >
                  <option value="+1">🇺🇸 +1</option>
                  <option value="+44">🇬🇧 +44</option>
                  <option value="+66">🇹🇭 +66</option>
                  <option value="+81">🇯🇵 +81</option>
                  <option value="+82">🇰🇷 +82</option>
                  <option value="+86">🇨🇳 +86</option>
                  <option value="+91">🇮🇳 +91</option>
                  <option value="+61">🇦🇺 +61</option>
                  <option value="+49">🇩🇪 +49</option>
                  <option value="+33">🇫🇷 +33</option>
                  <option value="+971">🇦🇪 +971</option>
                  <option value="+65">🇸🇬 +65</option>
                  <option value="+55">🇧🇷 +55</option>
                  <option value="+234">🇳🇬 +234</option>
                  <option value="+27">🇿🇦 +27</option>
                </select>
                <input
                  type="tel"
                  placeholder="555 000 0000"
                  className="flex-1 p-3 text-sm outline-none border-none"
                  value={c.phone || ""}
                  onChange={(e) => handleField("phone", e.target.value)}
                />
              </div>
            </div>
          </div>
        </section>

        <section className="rounded-2xl border border-gray-200/90 bg-white/90 p-5 shadow-sm backdrop-blur-sm">
          <h3 className="mb-4 text-[10px] font-bold uppercase tracking-[0.15em] text-white">2 · Messaging channels</h3>
          <p className="mb-3 text-[11px] text-white">Optional — how we reach you beyond email.</p>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-[10px] font-semibold text-white">LINE ID</label>
              <input
                type="text"
                placeholder="U..."
                className="w-full rounded-lg border border-gray-200 p-2.5 text-sm outline-none focus:border-gray-500"
                value={c.line || ""}
                onChange={(e) => handleField("line", e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-[10px] font-semibold text-white">WhatsApp</label>
              <input
                type="tel"
                placeholder="+1..."
                className="w-full rounded-lg border border-gray-200 p-2.5 text-sm outline-none focus:border-gray-500"
                value={c.whatsapp || ""}
                onChange={(e) => handleField("whatsapp", e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-[10px] font-semibold text-white">WeChat ID</label>
              <input
                type="text"
                className="w-full rounded-lg border border-gray-200 p-2.5 text-sm outline-none focus:border-gray-500"
                value={c.wechat || ""}
                onChange={(e) => handleField("wechat", e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-[10px] font-semibold text-white">FB Messenger</label>
              <input
                type="text"
                className="w-full rounded-lg border border-gray-200 p-2.5 text-sm outline-none focus:border-gray-500"
                value={c.messenger || ""}
                onChange={(e) => handleField("messenger", e.target.value)}
              />
            </div>
          </div>
          <div className="mt-3">
            <label className="mb-1 block text-[10px] font-semibold text-white">Preferred channel</label>
            <select
              className="w-full rounded-lg border border-gray-200 bg-white p-2.5 text-sm outline-none focus:border-gray-500"
              value={c.preferred || "email"}
              onChange={(e) => handleField("preferred", e.target.value)}
            >
              <option value="email">Email only</option>
              <option value="line">LINE</option>
              <option value="whatsapp">WhatsApp</option>
              <option value="wechat">WeChat</option>
              <option value="fb_messenger">FB Messenger</option>
            </select>
          </div>
        </section>

        <section className="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50/80 p-4">
          <Shield size={18} className="mt-0.5 flex-shrink-0 text-slate-500" />
          <div>
            <div className="text-xs font-bold text-slate-800">Secure process</div>
            <p className="mt-1 text-[11px] leading-relaxed text-slate-600">
              Tax ID (SSN/EIN) is collected through a separate secure step after approval. We do not collect sensitive financial data in this form.
            </p>
          </div>
        </section>
      </div>

      <button
        type="button"
        onClick={handleLaunch}
        disabled={!isReady}
        className={`w-full rounded-2xl py-6 text-3xl font-black uppercase tracking-widest transition-all ${isReady ? "cursor-pointer bg-gradient-to-r from-violet-700 to-indigo-800 text-white shadow-lg shadow-violet-300/40 hover:from-violet-800 hover:to-indigo-900" : "cursor-not-allowed bg-gray-200 text-white"}`}
      >
        {isReady ? "ACTIVATE" : "Add name & email to activate"}
      </button>
      {!isReady ? <p className="mt-2 text-center text-[11px] text-white">First name, last name, and a valid email unlock activation.</p> : null}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// YAML GENERATOR
// ═══════════════════════════════════════════════════════════

function generateYAML(state) {
  const san = (s) => (s || "").replace(/<[^>]*>/g, "").replace(/https?:\/\/\S+/g, "").replace(/[<>"'`]/g, "").substring(0, 500).trim();
  const proven = PROVEN[state.archetype] || PROVEN.nervous_system;
  const c = state.contact || {};
  const ts = new Date().toISOString().split("T")[0];

  // Read teacher selection set by teacher_select.html before wizard launch
  let teacherMode = null;
  try {
    const raw = localStorage.getItem("phoenix_book_mode");
    if (raw) teacherMode = JSON.parse(raw);
  } catch (_) {}
  // Also accept ?teacher= URL param as fallback
  if (!teacherMode) {
    const urlTeacher = new URLSearchParams(window.location.search).get("teacher");
    if (urlTeacher) teacherMode = { mode: "teacher", teacher: urlTeacher };
  }

  let y = `# Brand Admin Application — ${ts}\n# Pearl Prime Brand Configuration\n\n`;
  y += `brand_admin:\n  first_name: "${san(c.firstName)}"\n  last_name: "${san(c.lastName)}"\n  email: "${san(c.email)}"\n  phone: "${san((c.phoneCode || '+1') + ' ' + c.phone)}"\n\n`;
  y += `  messaging_channels:\n    line_id: "${san(c.line)}"\n    whatsapp: "${san(c.whatsapp)}"\n    wechat_id: "${san(c.wechat)}"\n    fb_messenger: "${san(c.messenger)}"\n    preferred_channel: "${c.preferred || "email"}"\n\n`;
  y += `  brand_positioning:\n    brand_angle: "${state.archetype}"\n    trigger_moment: "${state.moment}"\n    persona: "${state.persona}"\n\n`;
  y += `  voice_settings:\n`;
  Object.entries(state.voiceSettings || {}).forEach(([k, v]) => { y += `    ${k}: ${v}\n`; });
  y += `\n  visual_style: "${state.visualStyle}"\n  tradition: "${state.tradition}"\n  emotional_outcomes: [${(state.emotions || []).map((e) => `"${e}"`).join(", ")}]\n\n`;
  y += `  content_angles: [${(state.angles || []).map((a) => `"${a}"`).join(", ")}]\n  topic_tags: [${(state.topicTags || []).map((t) => `"${t}"`).join(", ")}]\n\n`;
  y += `  onboarding_lane: "${state.onboardingLane || "self_help"}"\n  onboarding_market: "${state.onboardingMarket || "us"}"\n`;
  y += `  format_focus: "${state.formatFocus || "book"}"\n  channels: [${(state.channels || []).map((c) => `"${c}"`).join(", ")}]\n\n`;
  y += `  revenue_blend:\n    user_topics_weight: 0.30\n    proven_topics_weight: 0.70\n    note: "System blends brand identity with persona-based demand and proven search terms"\n\n`;

  // Teacher mode block — written when admin selected a teacher in Step 1
  // Mode is always "generalized": teachings are used but teacher name is NOT in content.
  // The +5% boost increases how much catalog content draws from this teacher's tradition.
  // See: config/catalog_planning/teacher_mode_config.yaml → user_selection_boost
  if (teacherMode && teacherMode.teacher) {
    y += `  teacher_mode:\n`;
    y += `    selected_teacher: "${san(teacherMode.teacher)}"\n`;
    y += `    mode: generalized\n`;
    y += `    teacher_boost_pct: 5\n`;
    y += `    rebalance_from: composite\n`;
    y += `    note: "Teacher teachings woven into content at tradition level — no teacher name in books. +5% of catalog draws from this teacher's doctrine_profile instead of composite/no-teacher pool."\n\n`;
  } else {
    y += `  teacher_mode:\n    mode: composite\n    selected_teacher: null\n    teacher_boost_pct: 0\n\n`;
  }

  y += `  proven_personas:\n`;
  proven.personas.forEach((p) => { y += `    - "${p}"\n`; });
  y += `\n  proven_search_topics:\n`;
  proven.topics.forEach((t) => { y += `    - "${t}"\n`; });
  y += `\n  proven_keywords:\n`;
  proven.keywords.forEach((k) => { y += `    - "${k}"\n`; });
  return y;
}

// ═══════════════════════════════════════════════════════════
// INTRO + SHOWCASE PAGES
// ═══════════════════════════════════════════════════════════

function CompareBlock({ labelA, labelB, contentA, contentB, colorA, colorB }) {
  const [active, setActive] = useState("a");
  return (
    <div className="rounded-2xl border border-gray-200 bg-white overflow-hidden">
      <div className="flex border-b border-gray-200">
        <button onClick={() => setActive("a")} className={`flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-all ${active === "a" ? `${colorA} bg-gray-50` : "text-white"}`}>{labelA}</button>
        <button onClick={() => setActive("b")} className={`flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-all ${active === "b" ? `${colorB} bg-gray-50` : "text-white"}`}>{labelB}</button>
      </div>
      <div className="p-5 min-h-[140px] transition-all duration-300">{active === "a" ? contentA : contentB}</div>
    </div>
  );
}

function IntroWelcome({ onNext }) {
  const { t } = useTranslation();
  const pillars = [
    { icon: PenTool, label: t("ui", "Voice"), tint: "from-violet-500 to-indigo-600" },
    { icon: Image, label: t("ui", "Visual"), tint: "from-fuchsia-500 to-pink-600" },
    { icon: Users, label: t("ui", "Reader"), tint: "from-sky-500 to-blue-600" },
    { icon: Layers, label: t("ui", "Formats"), tint: "from-emerald-500 to-teal-600" },
  ];
  return (
    <div className="brand-studio-bg min-h-screen text-white">
      <div className="mx-auto max-w-3xl px-6 py-16">
        <div className="brand-studio-panel p-10 text-center sm:p-12">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-violet-200/80 bg-violet-50/80 px-4 py-1.5 text-xs font-semibold text-violet-800 backdrop-blur-sm">
            <Sparkles size={12} /> {t("ui", "Pearl Prime Brand Studio")}
          </div>
          <h1 className="text-4xl font-black leading-tight tracking-tight text-white sm:text-5xl">{t("ui", "Launch and shape your publishing brand")}</h1>
          <p className="mx-auto mt-4 max-w-lg text-base leading-relaxed text-white">
            {t("ui", "One guided session — voice, look, and proof aligned.")}
          </p>
          <div className="mx-auto mt-10 grid max-w-md grid-cols-4 gap-3">
            {pillars.map(({ icon: I, label, tint }) => (
              <div key={label} className="flex flex-col items-center gap-2">
                <div className={`flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br ${tint} shadow-lg shadow-slate-300/30`}>
                  <I size={22} className="text-white" />
                </div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-white">{label}</span>
              </div>
            ))}
          </div>
          <div className="mt-12">
            <button
              type="button"
              onClick={onNext}
              className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white shadow-lg shadow-slate-400/30 transition-all hover:-translate-y-0.5 hover:bg-gray-800"
            >
              {t("ui", "Start building")} <ChevronRight size={18} />
            </button>
          </div>
          <p className="mt-8 text-center text-xs">
            <a
              href="https://brand-admin-onboarding.pages.dev/pearl_prime_v6-3.html"
              className="font-semibold text-orange-400 underline decoration-orange-300 underline-offset-2 hover:text-orange-300"
            >
              {t("ui", "Back To Start")}
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

function IntroJourney({ onNext, onBack, onChooseTeacher }) {
  const { t } = useTranslation();
  const phases = [
    { step: "1", title: t("intro", "Foundation"), sub: t("intro", "Archetype & reader"), color: "from-indigo-500 to-violet-600" },
    { step: "2", title: t("intro", "Voice"), sub: t("intro", "Tone & impact"), color: "from-violet-500 to-fuchsia-600" },
    { step: "3", title: t("intro", "Look & topics"), sub: t("intro", "Visuals + territory"), color: "from-rose-500 to-orange-500" },
    { step: "4", title: t("intro", "Formats"), sub: t("intro", "Channels & pipeline"), color: "from-sky-500 to-cyan-600" },
    { step: "5", title: t("intro", "Reveal"), sub: t("intro", "Blueprint & launch"), color: "from-slate-600 to-gray-900" },
  ];
  return (
    <div className="brand-studio-bg min-h-screen text-white">
      <div className="mx-auto max-w-3xl px-6 py-12">
        <button type="button" onClick={onBack} className="mb-6 flex items-center gap-1 text-xs text-white transition-colors hover:text-white">
          <ChevronLeft size={14} /> {t("ui", "Back")}
        </button>
        <div className="brand-studio-panel p-8 sm:p-10">
          <div className="text-center">
            <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-violet-600">{t("intro", "How this works")}</p>
            <h1 className="mt-2 text-3xl font-black tracking-tight">{t("intro", "Five beats, eleven choices")}</h1>
            <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-white">
              {t("intro", "Foundation → formats → blueprint → launch.")}
            </p>
          </div>
          <div className="relative mt-10">
            <div className="absolute left-[18px] top-1 bottom-1 w-px bg-gradient-to-b from-violet-200 via-indigo-200 to-gray-200 sm:left-1/2 sm:top-[16px] sm:bottom-auto sm:h-1 sm:w-full sm:max-w-xl sm:-translate-x-1/2 sm:bg-gradient-to-r" aria-hidden />
            <div className="space-y-4 sm:grid sm:grid-cols-5 sm:gap-3 sm:space-y-0">
              {phases.map(({ step, title, sub, color }) => (
                <div key={step} className="relative flex gap-3 sm:flex-col sm:items-center sm:text-center">
                  <div className={`relative z-[1] flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br ${color} text-xs font-bold text-white shadow-md`}>
                    {step}
                  </div>
                  <div className="pt-0.5 sm:pt-2">
                    <div className="text-sm font-bold text-white">{title}</div>
                    <div className="text-[11px] text-white">{sub}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="mt-8" />
          <div className="mt-6 text-center">
            <button
              type="button"
              onClick={onChooseTeacher}
              className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white shadow-lg transition-all hover:-translate-y-0.5 hover:bg-gray-800"
            >
              {t("ui", "Choose Your Teacher")} <ArrowRight size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ShowcaseProse({ onNext, onBack }) {
  return (
    <div className="brand-studio-bg min-h-screen text-white">
      <div className="mx-auto max-w-3xl px-6 py-12">
        <button type="button" onClick={onBack} className="mb-4 flex items-center gap-1 text-xs text-white transition-colors hover:text-white">
          <ChevronLeft size={14} /> Back
        </button>
        <div className="brand-studio-panel p-6 sm:p-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 text-indigo-600 text-xs font-semibold mb-4"><PenTool size={12} /> Step 1 Preview — Writing Voice</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">Same topic. Completely different voice.</h1>
        <p className="text-white mb-8">Two brands, one topic — feel the shift in prose and energy.</p>
        <CompareBlock labelA="Stillness Lab" labelB="Clear Mind Lab" colorA="text-indigo-600" colorB="text-amber-600"
          contentA={<div><div className="flex gap-2 mb-3"><div className="w-14 h-20 rounded-lg shadow-md flex-shrink-0" style={{ background: "linear-gradient(135deg, #6366f1, #818cf8, #e0e7ff)" }} /><div><div className="text-[10px] text-white font-semibold uppercase">Stillness Lab</div><div className="text-sm font-bold text-white">The Body Keeps the Score at 2AM</div></div></div><p className="text-sm text-white leading-relaxed italic border-l-2 border-indigo-300 pl-3">"Your body remembers what your mind tries to forget. Right now, your shoulders are holding yesterday's argument."</p><div className="mt-3 bg-indigo-50 rounded-lg p-3"><div className="text-[10px] font-bold text-indigo-600 uppercase mb-1">Exercise</div><p className="text-xs text-indigo-800">"Inhale for 4 counts. Hold for 7. Exhale slowly for 8."</p></div></div>}
          contentB={<div><div className="flex gap-2 mb-3"><div className="w-14 h-20 rounded-lg shadow-md flex-shrink-0" style={{ background: "linear-gradient(135deg, #d97706, #f59e0b, #fef3c7)" }} /><div><div className="text-[10px] text-white font-semibold uppercase">Clear Mind Lab</div><div className="text-sm font-bold text-white">Your Phone Is Stealing Your Sleep</div></div></div><p className="text-sm text-white leading-relaxed italic border-l-2 border-amber-400 pl-3">"You're staring at the ceiling because your brain is running yesterday's argument on a loop."</p><div className="mt-3 bg-amber-50 rounded-lg p-3"><div className="text-[10px] font-bold text-amber-600 uppercase mb-1">Exercise</div><p className="text-xs text-amber-800">"Phone in another room. Lie flat. Breathe out longer than in. 90 seconds. Go."</p></div></div>}
        />
        <div className="mt-8 text-center">
          <button type="button" onClick={onNext} className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white transition-all hover:bg-gray-800">
            See cover differences <ChevronRight size={18} />
          </button>
        </div>
        </div>
      </div>
    </div>
  );
}

function ShowcaseCovers({ onNext, onBack }) {
  return (
    <div className="brand-studio-bg min-h-screen text-white">
      <div className="mx-auto max-w-3xl px-6 py-12">
        <button type="button" onClick={onBack} className="mb-4 flex items-center gap-1 text-xs text-white transition-colors hover:text-white">
          <ChevronLeft size={14} /> Back
        </button>
        <div className="brand-studio-panel p-6 sm:p-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-50 text-rose-600 text-xs font-semibold mb-4"><Image size={12} /> Visual Style Preview</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">Your visual style shapes everything.</h1>
        <p className="text-white mb-8">One choice ripples across covers and thumbnails.</p>
        <div className="grid grid-cols-3 gap-4 mb-8">
          {ARCHETYPES.slice(0, 3).map((arch) => (
            <div key={arch.id} className="text-center">
              <div className="w-full h-40 rounded-xl shadow-lg mb-2" style={{ background: `linear-gradient(135deg, ${arch.coverColors[0]}, ${arch.coverColors[1]}, ${arch.coverColors[2]})` }}>
                <div className="flex flex-col items-center justify-end h-full p-3"><div className="text-[9px] font-bold text-white/90 text-center leading-tight">{arch.sampleTitle}</div><div className="text-[7px] text-white/80 mt-0.5">{arch.name}</div></div>
              </div>
              <div className="text-xs font-bold text-white">{arch.name}</div><div className="text-[10px] text-white">{arch.coverStyle}</div>
            </div>
          ))}
        </div>
        <div className="mt-8 text-center">
          <button type="button" onClick={onNext} className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white transition-all hover:bg-gray-800">
            See video styles <ChevronRight size={18} />
          </button>
        </div>
        </div>
      </div>
    </div>
  );
}

function ShowcaseVideo({ onNext, onBack }) {
  return (
    <div className="brand-studio-bg min-h-screen text-white">
      <div className="mx-auto max-w-3xl px-6 py-12">
        <button type="button" onClick={onBack} className="mb-4 flex items-center gap-1 text-xs text-white transition-colors hover:text-white">
          <ChevronLeft size={14} /> Back
        </button>
        <div className="brand-studio-panel p-6 sm:p-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 text-amber-600 text-xs font-semibold mb-4"><Film size={12} /> Video & Social Preview</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">Daily content. Your signature look.</h1>
        <p className="text-white mb-8">Short-form video inherits your palette and mood.</p>
        <div className="grid grid-cols-2 gap-4 mb-8">
          {ARCHETYPES.slice(0, 4).map((arch) => (
            <div key={arch.id} className="rounded-xl overflow-hidden border border-gray-200">
              <div className="h-32 flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${arch.coverColors[0]}88, ${arch.coverColors[1]}66)` }}><div className="text-center"><Play size={24} className="text-white/80 mx-auto mb-1" /><div className="text-[10px] text-white/80 font-bold">{arch.name}</div></div></div>
              <div className="p-3 bg-white"><div className="text-xs font-bold text-white">{arch.videoStyle}</div><div className="text-[10px] text-white mt-0.5">Daily across YouTube, TikTok, Instagram, Facebook, X</div></div>
            </div>
          ))}
        </div>
        <div className="mt-8 text-center">
          <button type="button" onClick={onNext} className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white transition-all hover:bg-gray-800">
            See format diversity <ChevronRight size={18} />
          </button>
        </div>
        </div>
      </div>
    </div>
  );
}

function ShowcaseFormats({ onNext, onBack }) {
  return (
    <div className="brand-studio-bg min-h-screen text-white">
      <div className="mx-auto max-w-3xl px-6 py-12">
        <button type="button" onClick={onBack} className="mb-4 flex items-center gap-1 text-xs text-white transition-colors hover:text-white">
          <ChevronLeft size={14} /> Back
        </button>
        <div className="brand-studio-panel p-6 sm:p-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 text-emerald-600 text-xs font-semibold mb-4"><Layers size={12} /> Format Diversity</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">One brand. Infinite formats.</h1>
        <p className="text-white mb-8">Same DNA — different containers.</p>
        <div className="grid grid-cols-3 gap-3 mb-8">
          {V4_FORMATS_STRUCTURAL.map((f) => (
            <div key={f.id} className="p-4 rounded-xl border border-gray-200 bg-white">
              <div className="text-[10px] text-white font-mono mb-1">{f.id}</div><div className="text-xs font-bold text-white">{f.label}</div><div className="text-[10px] text-white mt-0.5">{f.desc}</div>
              <div className="mt-2 flex items-center gap-2"><span className="text-[9px] bg-gray-100 text-white px-2 py-0.5 rounded-full">{f.chapters} ch</span><span className="text-[9px] bg-gray-100 text-white px-2 py-0.5 rounded-full">{f.tier}</span></div>
            </div>
          ))}
        </div>
        <div className="rounded-xl bg-gray-50 border border-gray-200 p-5 mb-8"><p className="text-xs text-white leading-relaxed">Manga, audio, courses, journals, video — adapted automatically from the same core.</p></div>
        <div className="mt-8 text-center">
          <button type="button" onClick={onNext} className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white transition-all hover:bg-gray-800">
            Start building your brand <ArrowRight size={18} />
          </button>
        </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// MAIN WIZARD
// ═══════════════════════════════════════════════════════════

const STEP_LABELS = ["Emotional World", "Primary Reader", "Trigger Moment", "Voice Tone", "Visual Style", "Emotional Outcomes", "Topics", "Your Brand", "Launch"];

export default function BrandWizard() {
  const { t, td, to, tv, locale, isEn } = useTranslation();

  // ── Translated data constants ──
  const tArchetypes = useMemo(() => td("archetypes", ARCHETYPES, ["name", "tagline", "sampleTitle", "sampleSubtitle", "sampleProse", "sampleExercise", "visionVibe", "tags", "coverStyle", "proseStyle", "videoStyle", "emotions"]), [locale]);
  const tPersonas = useMemo(() => td("personas", PERSONAS, ["label", "desc", "needs", "impact"]), [locale]);
  const tMoments = useMemo(() => td("moments", MOMENTS, ["label", "scene", "hookStyle"]), [locale]);
  const tVisualStyles = useMemo(() => td("visualStyles", VISUAL_STYLES, ["label", "desc", "mood"]), [locale]);
  const tEmotionCategories = useMemo(() => td("emotionCategories", EMOTION_CATEGORIES, ["name", "items"]), [locale]);
  const tAngleFeedback = useMemo(() => {
    const out = {};
    for (const [k, v] of Object.entries(ANGLE_FEEDBACK)) {
      out[k] = to("angleFeedback", v, ["label", "systemEffect", "emotionalBenefit"]);
    }
    return out;
  }, [locale]);
  const tSelectionFeedback = useMemo(() => {
    const out = {};
    for (const [section, entries] of Object.entries(SELECTION_FEEDBACK)) {
      out[section] = {};
      for (const [k, v] of Object.entries(entries)) {
        out[section][k] = to("selectionFeedback", v, ["systemEffect", "emotionalBenefit"]);
      }
    }
    return out;
  }, [locale]);
  const tProven = useMemo(() => {
    const out = {};
    for (const [k, v] of Object.entries(PROVEN)) {
      out[k] = to("proven", v, ["personas", "topics", "keywords"]);
    }
    return out;
  }, [locale]);
  const tStepLabels = useMemo(() => STEP_LABELS.map(l => t("steps", l)), [locale]);
  const tV4FormatsStructural = useMemo(() => td("formats", V4_FORMATS_STRUCTURAL, ["label", "desc"]), [locale]);

  const [phase, setPhase] = useState("intro");
  const [introPage, setIntroPage] = useState(0);
  const [step, setStep] = useState(0);
  const [state, setState] = useState({
    archetype: null, persona: null, moment: null,
    voiceSettings: {}, visualStyle: null, emotions: [],
    tradition: "", angles: [], topicTags: [],
    formatFocus: null, channels: [],
    onboardingLane: "self_help", onboardingMarket: "us",
    contact: { firstName: "", lastName: "", email: "", phoneCode: "+1", phone: "", line: "", whatsapp: "", wechat: "", messenger: "", preferred: "email" },
  });

  const update = useCallback((patch) => setState((prev) => ({ ...prev, ...patch })), []);
  const scrollTop = () => window.scrollTo({ top: 0, behavior: "instant" });
  const nextIntro = () => { setIntroPage((p) => p + 1); scrollTop(); };
  const prevIntro = () => { if (introPage > 0) { setIntroPage((p) => p - 1); scrollTop(); } };
  const startWizard = () => { setPhase("wizard"); setStep(0); scrollTop(); };
  const nextStep = () => { if (step < 8) { setStep((s) => s + 1); scrollTop(); } };
  const prevStep = () => { if (step > 0) { setStep((s) => s - 1); scrollTop(); } else { setPhase("intro"); setIntroPage(1); scrollTop(); } };
  const goToHowItWorks = () => { setPhase("intro"); setIntroPage(1); scrollTop(); };
  const goToTeacherShowcase = () => { window.location.href = "teacher_showcase.html"; };

  // If ?teacher= in URL, skip intro and jump straight to wizard step 1
  useEffect(() => {
    const urlTeacher = new URLSearchParams(window.location.search).get("teacher");
    if (urlTeacher) { setPhase("wizard"); setStep(0); scrollTop(); }
  }, []);

  // INTRO: 0=welcome, 1=journey → choose teacher → wizard
  if (phase === "intro") {
    if (introPage === 0) return <IntroWelcome onNext={nextIntro} />;
    if (introPage >= 1) return <IntroJourney onNext={startWizard} onBack={prevIntro} onChooseTeacher={goToTeacherShowcase} />;
  }

  const canNext = step === 0
    ? !!state.archetype
    : step === 1
      ? !!state.persona && !!state.onboardingLane && !!state.onboardingMarket
      : step === 2
        ? !!state.moment
        : true;

  const i18nData = { tArchetypes, tPersonas, tMoments, tVisualStyles, tEmotionCategories, tAngleFeedback, tSelectionFeedback, tProven, tV4FormatsStructural, t };

  const steps = [
    <Step1Archetype key={0} state={state} update={update} i18n={i18nData} />,
    <Step2PrimaryReader key={1} state={state} update={update} i18n={i18nData} />,
    <Step3TriggerMoment key={2} state={state} update={update} i18n={i18nData} />,
    <Step4VoiceGraphs key={3} state={state} update={update} i18n={i18nData} />,
    <Step5VisualStyle key={4} state={state} update={update} i18n={i18nData} />,
    <Step6EmotionalOutcomes key={5} state={state} update={update} i18n={i18nData} />,
    <Step7Topics key={6} state={state} update={update} i18n={i18nData} />,
    <StepBrandReveal key={7} state={state} i18n={i18nData} />,
    <Step11Launch key={8} state={state} update={update} i18n={i18nData} />,
  ];

  return (
    <div className="brand-studio-bg min-h-screen">
      <div className="mx-auto max-w-6xl px-4 py-8">
        <button
          type="button"
          onClick={goToHowItWorks}
          className="mb-6 flex items-center gap-1 text-xs text-white transition-colors hover:text-gray-200"
        >
          <ChevronLeft size={14} /> {t("ui", "Back")}
        </button>
        <ProgressBar step={step} total={9} labels={tStepLabels} t={t} />
        <div className="brand-studio-panel p-6 sm:p-8 lg:p-10">
          <div className="flex gap-6 lg:gap-8">
            <div className="min-w-0 flex-1">
              <div style={step === 8 ? { maxHeight: "calc(100dvh - 220px)", overflowY: "auto", paddingRight: "4px" } : {}}>
                {steps[step]}
              </div>
              <div className="mt-8 flex items-center justify-between border-t border-gray-100/80 pt-6">
                <button type="button" onClick={prevStep} className="flex items-center gap-1.5 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:text-white">
                  <ChevronLeft size={16} /> {t("ui", "Back")}
                </button>
                {step < 8 ? (
                  <button
                    type="button"
                    onClick={nextStep}
                    disabled={!canNext}
                    className={`flex items-center gap-1.5 rounded-xl px-6 py-2.5 text-sm font-bold transition-all ${canNext ? "bg-gray-900 text-white shadow-md shadow-slate-300/40 hover:bg-gray-800" : "cursor-not-allowed bg-gray-200 text-white"}`}
                  >
                    {t("ui", "Continue")} <ChevronRight size={16} />
                  </button>
                ) : null}
              </div>
            </div>
            <div className="hidden w-72 flex-shrink-0 lg:block">
              <div className="sticky top-8">
                <div className="mb-3 text-[10px] font-bold uppercase tracking-wider text-violet-600/90">{t("ui", "Studio insight")}</div>
                <div className="rounded-2xl border border-gray-100/90 bg-white/60 p-1 shadow-inner backdrop-blur-sm">
                  <PersonaImpactPanel state={state} step={step} i18n={i18nData} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}