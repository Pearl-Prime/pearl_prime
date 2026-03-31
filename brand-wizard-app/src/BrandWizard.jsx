import { useState, useCallback } from "react";
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
  { id: "gentleDirect", left: "Gentle", right: "Direct", default: 40, color: "#6366f1", desc: "Controls sentence softness, permission language vs imperative commands" },
  { id: "simpleDeep", left: "Simple", right: "Deep", default: 50, color: "#059669", desc: "Controls vocabulary density, metaphor layers, conceptual complexity" },
  { id: "emotionalLogical", left: "Emotional", right: "Logical", default: 35, color: "#f43f5e", desc: "Controls story-to-data ratio, vulnerability level, analytical framing" },
  { id: "spiritualPractical", left: "Spiritual", right: "Practical", default: 45, color: "#7c3aed", desc: "Controls tradition references, sacred language, tool-first vs meaning-first" },
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
    id: "premium_soft", label: "Premium / Soft", desc: "Luxurious, muted, editorial",
    palette: ["#fdf4ff", "#d8b4fe", "#7e22ce", "#3b0764"], mood: "Elevated, refined, intimate",
    imagePrompt: "Premium editorial book cover with soft lavender and deep purple gradient, elegant thin serif typography, subtle gold foil accent line, silk fabric texture overlay, luxury beauty brand aesthetic, muted soft-focus floral",
    emotionPrompt: "Soft focus lavender field at golden hour, silk fabric flowing in slow motion breeze, delicate gold light particles, feeling of being held in luxury and care, premium spa atmosphere",
  },
  {
    id: "sacred_cosmic", label: "Sacred / Cosmic", desc: "Geometry, gradients, gold",
    palette: ["#0f172a", "#7c3aed", "#f59e0b", "#fef3c7"], mood: "Mystical, expansive, luminous",
    imagePrompt: "Sacred geometry book cover with deep navy background, intricate golden Flower of Life pattern, cosmic nebula purple and gold gradient, celestial star field, ancient wisdom meets modern design, gold foil mandala",
    emotionPrompt: "Vast cosmic nebula scene with sacred geometry overlaid in gold, spiraling galaxies forming mandala patterns, person meditating as silhouette against universe, feeling of infinite connection and awakening",
  },
];

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

function ProgressBar({ step, total, labels }) {
  const pct = ((step + 1) / total) * 100;
  return (
    <div className="mb-6">
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs font-bold text-gray-600 uppercase tracking-wider">Step {step + 1} of {total} — {labels[step]}</span>
        <span className="text-xs text-gray-400">{Math.round(pct)}%</span>
      </div>
      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div className="h-full bg-gradient-to-r from-gray-800 to-gray-600 rounded-full transition-all duration-500" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function ArchetypeCard({ arch, selected, onClick }) {
  const Icon = arch.icon;
  const isActive = selected === arch.id;
  return (
    <button onClick={() => onClick(arch.id)} className={`relative text-left p-5 rounded-2xl border-2 transition-all duration-300 ${isActive ? `${arch.activeBorder} ${arch.bg} shadow-lg scale-[1.02]` : `border-gray-200 bg-white hover:border-gray-300 hover:shadow-md hover:-translate-y-0.5`}`}>
      {isActive && <div className="absolute top-3 right-3"><div className="w-6 h-6 rounded-full bg-gray-900 flex items-center justify-center"><Check size={14} className="text-white" /></div></div>}
      <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${arch.gradient} flex items-center justify-center mb-3`}><Icon size={20} className="text-white" /></div>
      <h3 className="font-bold text-gray-900 text-sm">{arch.name}</h3>
      <p className="text-xs text-gray-500 mt-1 leading-relaxed">{arch.tagline}</p>
      <p className="text-[11px] text-gray-400 mt-2 leading-relaxed italic">{arch.visionVibe}</p>
      <div className="flex gap-1.5 mt-3 flex-wrap">
        {arch.tags.map((t) => <span key={t} className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${isActive ? 'bg-white/70 text-gray-700' : 'bg-gray-100 text-gray-500'}`}>{t}</span>)}
      </div>
    </button>
  );
}

function PersonaCard({ persona, selected, onClick }) {
  const isActive = selected === persona.id;
  return (
    <button onClick={() => onClick(persona.id)} className={`text-left p-4 rounded-xl border-2 transition-all duration-200 w-full ${isActive ? "border-gray-900 bg-gray-50 shadow-md" : "border-gray-200 bg-white hover:border-gray-300"}`}>
      <div className="flex items-start gap-3">
        <span className="text-2xl">{persona.emoji}</span>
        <div className="flex-1">
          <h4 className="font-bold text-sm text-gray-900">{persona.label}</h4>
          <p className="text-[11px] text-gray-500 mt-0.5">{persona.desc}</p>
          <p className="text-[11px] text-gray-600 font-medium mt-1.5">Needs: {persona.needs}</p>
          {isActive && <p className="text-[11px] text-indigo-600 mt-1.5 italic">{persona.impact}</p>}
        </div>
        {isActive && <div className="w-5 h-5 rounded-full bg-gray-900 flex items-center justify-center flex-shrink-0"><Check size={12} className="text-white" /></div>}
      </div>
    </button>
  );
}

function MomentCard({ moment, selected, onClick }) {
  const isActive = selected === moment.id;
  return (
    <button onClick={() => onClick(moment.id)} className={`text-left p-4 rounded-xl border-2 transition-all duration-200 w-full ${isActive ? "border-gray-900 bg-gray-50 shadow-md" : "border-gray-200 bg-white hover:border-gray-300"}`}>
      <div className="flex items-start gap-3">
        <span className="text-2xl">{moment.emoji}</span>
        <div className="flex-1">
          <h4 className="font-bold text-sm text-gray-900">{moment.label}</h4>
          <p className="text-[11px] text-gray-500 italic">{moment.scene}</p>
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
    premium_soft: { systemEffect: "Generates covers with lavender/purple gradients, thin serif type, gold accents, silk texture overlay", emotionalBenefit: "Readers feel elevated and cared for. Premium aesthetics trigger 'I deserve this' self-worth responses. Soft luxury attracts readers who associate healing with quality and refinement." },
    sacred_cosmic: { systemEffect: "Generates covers with sacred geometry, golden mandalas, cosmic nebula, celestial star fields", emotionalBenefit: "Readers feel connected to something larger. Sacred geometry triggers awe — the brain's pathway to perspective shift. Attracts seekers ready for depth and meaning beyond the everyday." },
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
            <div className="text-[9px] font-bold uppercase text-gray-400 mb-0.5">In the System</div>
            <p className="text-[11px] text-gray-600 leading-relaxed">{systemEffect}</p>
          </div>
        </div>
        <div className="flex items-start gap-2">
          <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: color + '15' }}>
            <Heart size={10} style={{ color }} />
          </div>
          <div>
            <div className="text-[9px] font-bold uppercase text-gray-400 mb-0.5">For Your Reader</div>
            <p className="text-[11px] text-gray-700 leading-relaxed font-medium">{emotionalBenefit}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function WhatThisChanges({ items }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-xl border border-gray-200 bg-gray-50 overflow-hidden">
      <button onClick={() => setOpen(!open)} className="w-full px-4 py-2.5 flex items-center gap-2 text-left">
        <Sparkles size={14} className="text-gray-500" />
        <span className="text-xs font-bold text-gray-600">What this changes</span>
        <ChevronRight size={14} className={`text-gray-400 ml-auto transition-transform ${open ? "rotate-90" : ""}`} />
      </button>
      {open && (
        <div className="px-4 pb-3 grid grid-cols-2 gap-1.5">
          {items.map((item, i) => <div key={i} className="flex items-center gap-1.5"><div className="w-1 h-1 rounded-full bg-gray-400" /><span className="text-[11px] text-gray-600">{item}</span></div>)}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// PERSONA IMPACT PANEL (Right side)
// ═══════════════════════════════════════════════════════════

function PersonaImpactPanel({ state }) {
  const arch = ARCHETYPES.find((a) => a.id === state.archetype);
  const persona = PERSONAS.find((p) => p.id === state.persona);
  const moment = MOMENTS.find((m) => m.id === state.moment);
  const proven = PROVEN[state.archetype] || PROVEN.nervous_system;
  const visual = VISUAL_STYLES.find((v) => v.id === state.visualStyle);
  const selectionCount = [state.archetype, state.persona, state.moment, state.visualStyle, state.tradition, (state.emotions || []).length > 0, Object.keys(state.voiceSettings || {}).length > 0, state.formatFocus].filter(Boolean).length;
  const completeness = Math.round((selectionCount / 8) * 100);

  return (
    <div className="space-y-4">
      <div className="text-center">
        <div className="relative w-20 h-20 mx-auto mb-2">
          <svg viewBox="0 0 80 80" className="w-full h-full -rotate-90">
            <circle cx="40" cy="40" r="34" fill="none" stroke="#f3f4f6" strokeWidth="6" />
            <circle cx="40" cy="40" r="34" fill="none" stroke="#1f2937" strokeWidth="6" strokeLinecap="round" strokeDasharray={`${completeness * 2.136} 213.6`} />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center"><span className="text-lg font-black text-gray-900">{completeness}%</span></div>
        </div>
        <p className="text-[10px] text-gray-500 font-semibold uppercase">Brand Defined</p>
      </div>
      {arch && (
        <div className={`rounded-xl p-3 ${arch.bg} border ${arch.border}`}>
          <div className="flex items-center gap-2">
            {(() => { const I = arch.icon; return <div className={`w-7 h-7 rounded-lg bg-gradient-to-br ${arch.gradient} flex items-center justify-center`}><I size={14} className="text-white" /></div>; })()}
            <div><div className="font-bold text-xs text-gray-900">{arch.name}</div><div className="text-[10px] text-gray-500">{arch.tagline}</div></div>
          </div>
        </div>
      )}
      {persona && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-gray-400 mb-1">Primary Reader</div>
          <div className="flex items-center gap-2"><span className="text-lg">{persona.emoji}</span><div><div className="text-xs font-bold text-gray-900">{persona.label}</div></div></div>
        </div>
      )}
      {moment && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-gray-400 mb-1">Trigger Moment</div>
          <div className="flex items-center gap-2"><span className="text-lg">{moment.emoji}</span><div><div className="text-xs font-bold text-gray-900">{moment.label}</div></div></div>
        </div>
      )}
      {arch && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-gray-400 mb-2">Revenue Personas</div>
          {proven.personas.map((p, i) => <div key={i} className="flex items-start gap-1.5 mb-1.5"><TrendingUp size={10} className="text-emerald-500 flex-shrink-0 mt-0.5" /><span className="text-[10px] text-gray-600 leading-tight">{p}</span></div>)}
        </div>
      )}
      {Object.keys(state.voiceSettings || {}).length > 0 && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-gray-400 mb-2">Voice Profile</div>
          {VOICE_SLIDERS.map((s) => { const val = state.voiceSettings?.[s.id] ?? s.default; return (
            <div key={s.id} className="flex items-center gap-2 mb-1"><span className="text-[9px] text-gray-400 w-14">{s.left}</span><div className="flex-1 h-1.5 bg-gray-100 rounded-full"><div className="h-full bg-gray-700 rounded-full transition-all" style={{ width: `${val}%` }} /></div><span className="text-[9px] text-gray-400 w-14 text-right">{s.right}</span></div>
          ); })}
        </div>
      )}
      {visual && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-gray-400 mb-2">Visual Style</div>
          <div className="flex gap-1.5 mb-1.5">{visual.palette.map((c, i) => <div key={i} className="w-8 h-8 rounded-lg shadow-sm" style={{ backgroundColor: c }} />)}</div>
          <div className="text-[10px] text-gray-600 font-medium">{visual.label}</div>
        </div>
      )}
      {state.formatFocus && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-gray-400 mb-1">Format</div>
          <div className="text-xs font-bold text-gray-900">{state.formatFocus === "manga" ? "Manga / Visual" : "Traditional Books"}</div>
        </div>
      )}
      <WhatThisChanges items={["Book prose tone & rhythm", "Cover art palette", "Video pacing & mood", "Exercise depth", "Audience keywords", "Title hook strategy", "Social content style", "Format distribution"]} />
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// WIZARD STEPS (11 steps)
// ═══════════════════════════════════════════════════════════

function Step1Archetype({ state, update }) {
  return (
    <div>
      <div className="bg-indigo-50 rounded-xl p-4 mb-6 border border-indigo-100">
        <p className="text-sm text-indigo-800 font-medium">Let's begin designing your brand!</p>
        <p className="text-xs text-indigo-600 mt-1">Your archetype is the emotional foundation of everything your brand creates. It defines the feeling readers associate with you across every title, cover, video, and social post. Each archetype carries a unique philosophy about how healing and growth work — choose the one that resonates with how you see the world.</p>
      </div>
      <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Choose Your Emotional World</h2>
      <p className="text-sm text-gray-500 mt-1 mb-2">This single choice sets the foundation for your entire brand. It determines your writing voice, visual aesthetic, exercise style, video treatment, audience targeting, and the emotional promise every piece of content makes. Take your time — this is the most important decision in the wizard.</p>
      <p className="text-xs text-gray-400 mb-6 italic">Each archetype below includes its vision — the world your brand invites readers into.</p>
      <div className="grid grid-cols-1 gap-3">
        {ARCHETYPES.map((arch) => <ArchetypeCard key={arch.id} arch={arch} selected={state.archetype} onClick={(id) => update({ archetype: id })} />)}
      </div>
      {state.archetype && SELECTION_FEEDBACK.archetypes[state.archetype] && (
        <SelectionFeedback
          systemEffect={SELECTION_FEEDBACK.archetypes[state.archetype].systemEffect}
          emotionalBenefit={SELECTION_FEEDBACK.archetypes[state.archetype].emotionalBenefit}
          color={ARCHETYPES.find(a => a.id === state.archetype)?.coverColors?.[0] || "#6366f1"}
        />
      )}
    </div>
  );
}

function Step2PrimaryReader({ state, update }) {
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
      <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Primary Reader</h2>
      <p className="text-sm text-gray-500 mt-1 mb-2">Every great brand has a protagonist — the person whose story it tells. This isn't about limiting your audience; it's about giving your brand a heartbeat.</p>
      <div className="rounded-xl bg-blue-50 border border-blue-100 p-4 mb-6">
        <p className="text-xs text-blue-800 leading-relaxed">
          <strong className="text-blue-900">Your catalog will automatically reach all audiences.</strong> The system builds books for every persona segment in your archetype. Choosing a primary reader here shapes your <em>brand narrative</em> — the voice of your titles, the tone of your covers, and the emotional hook that makes your brand instantly recognizable. Think of it as your lead character, not your only audience. Every cover, title, opening line, and exercise is tuned to this person first — then the system adapts the same content for every other persona.
        </p>
      </div>
      <div className="grid grid-cols-1 gap-2.5">
        {PERSONAS.map((p) => <PersonaCard key={p.id} persona={p} selected={state.persona} onClick={(id) => update({ persona: id })} />)}
      </div>
      {state.persona && SELECTION_FEEDBACK.personas[state.persona] && (
        <SelectionFeedback
          systemEffect={SELECTION_FEEDBACK.personas[state.persona].systemEffect}
          emotionalBenefit={SELECTION_FEEDBACK.personas[state.persona].emotionalBenefit}
          color="#3b82f6"
        />
      )}
      {state.persona && (
        <>
          <div className="mt-6">
            <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 mb-2">Choose lane</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
              {laneChoices.map((lane) => (
                <LaneChoiceCard
                  key={lane.key}
                  laneKey={lane.key}
                  label={lane.label}
                  hint={lane.hint}
                  selected={selectedLane === lane.key}
                  onSelect={(laneKey) => update({ onboardingLane: laneKey })}
                />
              ))}
            </div>
          </div>
          <div className="mt-6">
            <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 mb-2">Choose market</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
              {marketChoices.map((mkt) => (
                <MarketChoiceCard
                  key={mkt.key}
                  marketKey={mkt.key}
                  label={mkt.label}
                  hint={mkt.hint}
                  selected={selectedMarket === mkt.key}
                  onSelect={(marketKey) => update({ onboardingMarket: marketKey })}
                />
              ))}
            </div>
          </div>
          <OutputProofStrip
            wizardPersonaId={state.persona}
            formatFocus={selectedFormatFocus}
            market={selectedMarket}
            onboardingLane={selectedLane}
          />
        </>
      )}
    </div>
  );
}

function Step3TriggerMoment({ state, update }) {
  return (
    <div>
      <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">The Moment They Reach for Your Book</h2>
      <p className="text-sm text-gray-500 mt-1 mb-2">Books aren't bought in bookstores anymore. They're found in moments of desperation, curiosity, or quiet surrender — a 2AM search bar, a podcast clip that hits different, a TikTok that stops the scroll.</p>
      <div className="rounded-xl bg-amber-50 border border-amber-100 p-4 mb-6">
        <p className="text-xs text-amber-800 leading-relaxed">
          <strong className="text-amber-900">Your choice here determines everything about your hook strategy.</strong> It shapes how your titles are written, how your first paragraph lands, what emotional promise your cover makes, and how your TikTok captions stop the scroll. The most effective brands don't just speak to a person — they speak to a <em>moment</em>. Pick the moment your reader is most vulnerable, most open, most ready to receive what you have. That's where your book meets them.
        </p>
      </div>
      <div className="grid grid-cols-1 gap-2.5">
        {MOMENTS.map((m) => <MomentCard key={m.id} moment={m} selected={state.moment} onClick={(id) => update({ moment: id })} />)}
      </div>
      {state.moment && SELECTION_FEEDBACK.moments[state.moment] && (
        <SelectionFeedback
          systemEffect={SELECTION_FEEDBACK.moments[state.moment].systemEffect}
          emotionalBenefit={SELECTION_FEEDBACK.moments[state.moment].emotionalBenefit}
          color="#f59e0b"
        />
      )}
    </div>
  );
}

function Step4VoiceGraphs({ state, update }) {
  const handleSlider = (id, val) => update({ voiceSettings: { ...state.voiceSettings, [id]: val } });

  const graphComponents = [PulseWaveGraph, SpectrumBarGraph, EmotionRadarGraph, EnergyGaugeGraph];

  return (
    <div>
      <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Reveal Your Brand Tone</h2>
      <p className="text-sm text-gray-500 mt-1 mb-2">These four sliders control the personality of every sentence your brand produces. Slide them and watch the graphs respond — each visualization represents the frequency, texture, and energy of your brand's voice. There are no wrong answers. The system uses these settings to calibrate prose rhythm, vocabulary register, sentence structure, and the emotional temperature of every chapter.</p>
      <p className="text-xs text-gray-400 mb-6 italic">On the next page, you'll see exactly how each setting affects your reader's experience.</p>

      <div className="space-y-6">
        {VOICE_SLIDERS.map((s, idx) => {
          const val = state.voiceSettings?.[s.id] ?? s.default;
          const position = Math.max(1, Math.min(10, Math.round(val / 10) || 1));
          const toneData = VOICE_TONE_10[s.id][position - 1];
          const GraphComp = graphComponents[idx];
          return (
            <div key={s.id} className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-bold text-gray-800">{s.left}</span>
                <span className="text-[10px] text-gray-400 max-w-xs text-center">{s.desc}</span>
                <span className="text-sm font-bold text-gray-800">{s.right}</span>
              </div>

              <GraphComp position={position} color={s.color} />

              <input type="range" min="0" max="100" value={val}
                onChange={(e) => handleSlider(s.id, parseInt(e.target.value))}
                className="w-full h-2.5 bg-gray-100 rounded-lg appearance-none cursor-pointer mt-2"
                style={{ accentColor: s.color }}
              />

              <div className="flex justify-between items-center mt-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: s.color }} />
                  <span className="text-xs font-bold" style={{ color: s.color }}>{toneData.label}</span>
                </div>
                <span className="text-[10px] text-gray-400">Position {position} of 10</span>
              </div>

              <div className="mt-3 bg-gray-50 rounded-lg p-3 border border-gray-100">
                <p className="text-[11px] text-gray-700 leading-relaxed">{toneData.technique}</p>
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
  const handleSlider = (id, val) => update({ voiceSettings: { ...state.voiceSettings, [id]: val } });

  return (
    <div>
      <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Voice Tone — Reader Impact</h2>
      <p className="text-sm text-gray-500 mt-1 mb-2">Here's exactly what your voice settings mean for your reader. Slide the controls and watch both the graph and the impact change in real time. Each technique describes how we write your content at this setting, and the five benefits explain the psychological, emotional, and practical impact on your target persona.</p>
      <p className="text-xs text-gray-400 mb-6 italic">This scoring system ensures every voice choice maps to a real reader outcome — nothing is arbitrary.</p>

      <div className="space-y-6">
        {VOICE_SLIDERS.map((s, idx) => {
          const val = state.voiceSettings?.[s.id] ?? s.default;
          const position = Math.max(1, Math.min(10, Math.round(val / 10) || 1));
          const toneData = VOICE_TONE_10[s.id][position - 1];
          const GraphComp = graphComponents[idx];

          return (
            <div key={s.id} className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
              <div className="p-4 border-b border-gray-100" style={{ borderLeftWidth: 4, borderLeftColor: s.color }}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: s.color }} />
                    <span className="text-sm font-bold text-gray-900">{s.left} — {s.right}</span>
                  </div>
                  <span className="text-xs font-bold px-2.5 py-0.5 rounded-full" style={{ backgroundColor: s.color + '15', color: s.color }}>{toneData.label}</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{s.desc}</p>
              </div>

              <div className="p-4">
                {/* Graph + Slider */}
                <div className="bg-gray-50 rounded-xl p-3 mb-4 border border-gray-100">
                  <GraphComp position={position} color={s.color} />
                  <input type="range" min="0" max="100" value={val}
                    onChange={(e) => handleSlider(s.id, parseInt(e.target.value))}
                    className="w-full h-2.5 bg-gray-200 rounded-lg appearance-none cursor-pointer mt-2"
                    style={{ accentColor: s.color }}
                  />
                  <div className="flex justify-between items-center mt-1.5">
                    <span className="text-[10px] font-semibold" style={{ color: s.color }}>{s.left}</span>
                    <span className="text-[10px] text-gray-400">Position {position} of 10</span>
                    <span className="text-[10px] font-semibold" style={{ color: s.color }}>{s.right}</span>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-3 mb-4">
                  <div className="text-[10px] font-bold uppercase text-gray-400 mb-1">How We Write This</div>
                  <p className="text-sm text-gray-800 font-medium leading-relaxed">{toneData.technique}</p>
                </div>

                <div className="text-[10px] font-bold uppercase text-gray-400 mb-2">Reader Benefits at This Setting</div>
                <div className="space-y-2.5">
                  {toneData.benefits.map((benefit, i) => (
                    <div key={i} className="flex items-start gap-2.5">
                      <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 text-[10px] font-bold text-white" style={{ backgroundColor: s.color }}>{i + 1}</div>
                      <p className="text-[11px] text-gray-700 leading-relaxed">{benefit}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Step6VisualStyle({ state, update }) {
  const handleVisual = (id) => update({ visualStyle: id });
  const handleTradition = (val) => update({ tradition: val });
  const handleEmotion = (emotion) => {
    const current = state.emotions || [];
    if (current.includes(emotion)) update({ emotions: current.filter((e) => e !== emotion) });
    else if (current.length < 5) update({ emotions: [...current, emotion] });
  };
  const allEmotions = ["Finally calm", "Safe in my body", "Clear-headed", "In control", "Permission to rest", "Energized", "Connected to purpose", "Released", "Less alone", "Forgiven", "Grounded", "Hopeful", "Present", "Confident", "Resilient"];
  const selectedVisual = VISUAL_STYLES.find((v) => v.id === state.visualStyle);

  return (
    <div>
      <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Visual World & Emotional Outcomes</h2>
      <p className="text-sm text-gray-500 mt-1 mb-2">Your visual style controls every cover, social post, video thumbnail, and ad creative your brand produces. Your emotional outcomes define the transformation promise — the feeling readers have when they finish your content. Together, these two choices create the visual and emotional signature that makes your brand unmistakable.</p>

      <div className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3 mt-6">Visual Style</div>
      <p className="text-[11px] text-gray-500 mb-3">Each style includes a text-to-image prompt — this is what the system uses to generate your covers, thumbnails, and social content.</p>
      <div className="grid grid-cols-2 gap-3 mb-4">
        {VISUAL_STYLES.map((vs) => (
          <button key={vs.id} onClick={() => handleVisual(vs.id)}
            className={`p-4 rounded-xl border-2 text-left transition-all ${state.visualStyle === vs.id ? "border-gray-900 bg-gray-50 shadow-md" : "border-gray-200 bg-white hover:border-gray-300"}`}>
            <div className="flex gap-1.5 mb-2">{vs.palette.map((c, i) => <div key={i} className="w-6 h-6 rounded-md shadow-sm" style={{ backgroundColor: c }} />)}</div>
            <div className="text-xs font-bold text-gray-900">{vs.label}</div>
            <div className="text-[10px] text-gray-500 mt-0.5">{vs.desc}</div>
            <div className="text-[10px] text-gray-400 mt-1 italic">{vs.mood}</div>
          </button>
        ))}
      </div>

      {selectedVisual && (
        <>
          <div className="bg-gray-50 rounded-xl p-4 mb-4 border border-gray-200">
            <div className="text-[10px] font-bold uppercase text-gray-400 mb-2">Cover Image Prompt</div>
            <p className="text-[11px] text-gray-700 leading-relaxed mb-3 italic">"{selectedVisual.imagePrompt}"</p>
            <div className="text-[10px] font-bold uppercase text-gray-400 mb-2">Emotional Image Prompt</div>
            <p className="text-[11px] text-gray-700 leading-relaxed italic">"{selectedVisual.emotionPrompt}"</p>
          </div>
          {SELECTION_FEEDBACK.visualStyles[state.visualStyle] && (
            <SelectionFeedback
              systemEffect={SELECTION_FEEDBACK.visualStyles[state.visualStyle].systemEffect}
              emotionalBenefit={SELECTION_FEEDBACK.visualStyles[state.visualStyle].emotionalBenefit}
              color={selectedVisual.palette[2] || "#7c3aed"}
            />
          )}
          <div className="mb-4" />
        </>
      )}

      <div className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">
        Emotional Outcomes <span className="text-gray-300 normal-case font-normal">(pick up to 5)</span>
      </div>
      <p className="text-[11px] text-gray-500 mb-3">These are the feelings your reader has after finishing your content. They drive the transformation promise in every title, CTA, and marketing message.</p>
      <div className="flex flex-wrap gap-2 mb-3">
        {allEmotions.map((e) => {
          const active = (state.emotions || []).includes(e);
          return <button key={e} onClick={() => handleEmotion(e)} className={`text-xs px-3 py-1.5 rounded-full border transition-all ${active ? "bg-gray-900 text-white border-gray-900" : "bg-white text-gray-600 border-gray-200 hover:border-gray-400"}`}>{e}</button>;
        })}
      </div>

      {(state.emotions || []).length > 0 && (
        <div className="bg-gray-50 rounded-xl p-4 mb-8 border border-gray-200">
          <div className="text-[10px] font-bold uppercase text-gray-400 mb-2">Emotional Outcome Image Prompts</div>
          {state.emotions.map((e) => (
            <div key={e} className="mb-2">
              <span className="text-[10px] font-bold text-gray-700">{e}:</span>
              <span className="text-[11px] text-gray-600 italic ml-1">
                "Abstract visualization of '{e.toLowerCase()}' — soft light radiating from center, human silhouette in peaceful pose, {VISUAL_STYLES.find(v => v.id === state.visualStyle)?.mood?.toLowerCase() || 'serene'} color palette, therapeutic art style, feeling of deep transformation and release"
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">Spiritual Foundation</div>
      <p className="text-[11px] text-gray-500 mb-3">If your brand draws from a specific tradition, select it here. This influences vocabulary, references, and the philosophical grounding of your content. Optional — many powerful brands are tradition-agnostic.</p>
      <select className="w-full p-3 border border-gray-200 rounded-xl text-sm bg-white focus:border-gray-500 focus:ring-2 focus:ring-gray-100 outline-none"
        value={state.tradition || ""} onChange={(e) => handleTradition(e.target.value)}>
        <option value="">Select primary tradition (optional)...</option>
        {TRADITIONS.map((t) => <option key={t} value={t}>{t}</option>)}
      </select>
    </div>
  );
}

function Step7Topics({ state, update }) {
  const [selectedAngles, setSelectedAngles] = useState(state.angles || []);
  const [selectedTopicTags, setSelectedTopicTags] = useState(state.topicTags || []);

  const toggleAngle = (id) => { const next = selectedAngles.includes(id) ? selectedAngles.filter((a) => a !== id) : [...selectedAngles, id]; setSelectedAngles(next); update({ angles: next }); };
  const toggleTopicTag = (tag) => { const next = selectedTopicTags.includes(tag) ? selectedTopicTags.filter((t) => t !== tag) : [...selectedTopicTags, tag]; setSelectedTopicTags(next); update({ topicTags: next }); };

  const topicCategories = [
    { label: "Sleep & Anxiety", tags: ["anxiety-at-night", "overthinking", "panic-grounding", "sunday-dread"] },
    { label: "Burnout & Work", tags: ["burnout-recovery", "nervous-system-reset", "decision-fatigue", "phone-addiction"] },
    { label: "Grief & Healing", tags: ["grief-timeline", "toxic-relationship-healing", "intergenerational-trauma", "heartbreak-recovery", "emotional-numbness"] },
    { label: "Identity & Direction", tags: ["feeling-behind", "quarter-life-crisis", "identity-rebuild", "purpose-after-30"] },
    { label: "Focus & Performance", tags: ["habit-building", "ADHD-productivity", "dopamine-detox", "deep-work"] },
    { label: "Meaning & Spirituality", tags: ["meditation-beginners", "meaning-after-loss", "spiritual-no-religion", "inner-peace-chaos", "mindfulness-skeptics"] },
  ];

  return (
    <div>
      <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Claim Your Search Territory</h2>
      <p className="text-sm text-gray-500 mt-1 mb-2">This page defines what your brand is <em>about</em> — the topics people search for that lead them to your content, and the angles your books use to frame their message. Your topic selections feed directly into title generation, keyword targeting, series planning, and ad campaigns across all platforms.</p>
      <p className="text-xs text-gray-400 mb-6 italic">Select generously — the system uses these as seeds to generate hundreds of specific title and keyword variations.</p>

      <div className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">Content Angles</div>
      <p className="text-[11px] text-gray-500 mb-3">How your books open their argument. These framing modes determine whether your titles challenge, reveal, systematize, or reframe. Pick all that fit your brand voice.</p>
      <div className="grid grid-cols-1 gap-2 mb-4">
        {V4_ANGLES.map((angle) => {
          const active = selectedAngles.includes(angle.id);
          const Icon = angle.icon;
          const angleFeedback = {
            debunk: { systemEffect: "Titles open with contrarian hooks — 'What your therapist won't tell you.' Evidence-backed pivots that challenge mainstream advice.", emotionalBenefit: "Readers feel intellectually respected. The debunk angle validates their suspicion that conventional advice isn't working — giving them permission to try a different path without feeling naive." },
            framework: { systemEffect: "Titles lead with structure — '5-step protocol for...' Content organized into repeatable systems readers can follow.", emotionalBenefit: "Overwhelmed readers exhale when they see a clear system. Frameworks reduce cognitive load and decision fatigue — transforming vague anxiety into concrete, manageable steps." },
            reveal: { systemEffect: "Titles expose hidden truths — 'The real reason you can't sleep.' Content positions your brand as the insider source.", emotionalBenefit: "Readers experience the relief of finally understanding. The reveal angle creates 'aha moments' that rewrite their self-narrative — from 'something is wrong with me' to 'now I understand why.'" },
            leverage: { systemEffect: "Titles reframe existing traits — 'Your anxiety is a superpower.' Content turns perceived weaknesses into strategic advantages.", emotionalBenefit: "Readers stop fighting themselves and start working with what they have. The leverage angle is profoundly healing — it says 'you're not broken, you're just using your gifts wrong.'" },
            origin: { systemEffect: "Titles trace root causes — 'Where your pattern actually started.' Content builds narrative depth and causal understanding.", emotionalBenefit: "Readers experience the deep relief of understanding where their patterns began. Origin stories create compassion for their past selves — the first step to actual behavioral change." },
          };
          return (
            <button key={angle.id} onClick={() => toggleAngle(angle.id)}
              className={`flex items-start gap-3 p-4 rounded-xl border-2 text-left transition-all ${active ? "border-gray-900 bg-gray-50" : "border-gray-200 bg-white hover:border-gray-300"}`}>
              <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${active ? "bg-gray-900" : "bg-gray-100"}`}>
                <Icon size={16} className={active ? "text-white" : "text-gray-400"} />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-gray-900">{angle.label}</span>
                  {active && <Check size={16} className="text-gray-900" />}
                </div>
                <p className="text-[11px] text-gray-500 mt-0.5">{angle.desc}</p>
                {active && (
                  <>
                    <p className="text-[10px] text-indigo-600 mt-1 italic">Framing: {angle.framing}</p>
                    <div className="mt-2 pt-2 border-t border-gray-200">
                      <div className="flex items-start gap-1.5 mb-1">
                        <Zap size={9} className="text-indigo-500 flex-shrink-0 mt-0.5" />
                        <p className="text-[10px] text-gray-500">{angleFeedback[angle.id]?.systemEffect}</p>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <Heart size={9} className="text-rose-400 flex-shrink-0 mt-0.5" />
                        <p className="text-[10px] text-gray-700 font-medium">{angleFeedback[angle.id]?.emotionalBenefit}</p>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </button>
          );
        })}
      </div>

      <div className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">Topic Territory</div>
      <p className="text-[11px] text-gray-500 mb-4">Select the search topics your brand will own. Organized by category — pick across multiple categories to build a well-rounded brand presence.</p>
      <div className="space-y-5">
        {topicCategories.map((cat) => (
          <div key={cat.label}>
            <div className="text-[11px] font-bold text-gray-700 mb-2 flex items-center gap-1.5">
              <Hash size={12} className="text-gray-400" /> {cat.label}
            </div>
            <div className="flex flex-wrap gap-2">
              {cat.tags.map((tag) => {
                const active = selectedTopicTags.includes(tag);
                return (
                  <button key={tag} onClick={() => toggleTopicTag(tag)}
                    className={`text-[11px] px-3 py-1.5 rounded-full border transition-all ${active ? "bg-gray-900 text-white border-gray-900" : "bg-white text-gray-600 border-gray-200 hover:border-gray-400"}`}>
                    {tag.replace(/-/g, " ")}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {selectedTopicTags.length > 0 && (
        <div className="mt-4 bg-gray-50 rounded-xl p-3 border border-gray-200">
          <span className="text-[10px] font-bold text-gray-500">{selectedTopicTags.length} topics selected</span>
        </div>
      )}
    </div>
  );
}

function Step8MarketIntel({ state }) {
  const proven = PROVEN[state.archetype] || PROVEN.nervous_system;
  return (
    <div>
      <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Market Intelligence</h2>
      <p className="text-sm text-gray-500 mt-1 mb-2">Your creative vision is the soul of your brand. But soul alone doesn't pay rent. This page shows you how the system blends your unique direction with hard market data — real search volumes, proven buyer personas, and high-converting keyword territories — to ensure your catalog reaches the people who are already looking for what you're offering.</p>
      <p className="text-xs text-gray-400 mb-6 italic">Nothing changes about your brand's voice or identity. We just make sure it shows up where the demand is.</p>

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
              <div className="text-[10px] font-bold text-gray-900">{label}</div>
              <div className="text-[9px] text-gray-500">{desc}</div>
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
            <p className="text-[11px] text-gray-600">Archetype, voice, topics, angles, visual style — preserved as your brand's unique creative identity</p>
          </div>
          <div className="bg-white rounded-lg p-3">
            <div className="text-[10px] font-bold text-emerald-700 uppercase mb-1">Market Intelligence</div>
            <p className="text-[11px] text-gray-600">Proven revenue personas, trending search terms, high-conversion keywords, and demand data matched to your archetype</p>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5 mb-6">
        <div className="text-xs font-bold text-gray-700 mb-3">Proven Revenue Personas for Your Archetype</div>
        <p className="text-[11px] text-gray-500 mb-3">These are the audience segments with verified purchasing power in your emotional territory. The system ensures your catalog reaches all of them.</p>
        {proven.personas.map((p, i) => (
          <div key={i} className="flex items-start gap-2 mb-2.5">
            <Target size={12} className="text-indigo-500 flex-shrink-0 mt-0.5" />
            <span className="text-[11px] text-gray-600">{p}</span>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <div className="text-xs font-bold text-gray-700 mb-3">High-Performing Search Topics</div>
        <p className="text-[11px] text-gray-500 mb-3">These search terms have verified monthly volume and conversion rates. Your titles and keywords will be optimized around these terms alongside your custom selections.</p>
        <div className="flex flex-wrap gap-2">
          {proven.topics.map((t, i) => <span key={i} className="text-[11px] bg-gray-100 text-gray-700 px-3 py-1 rounded-full">{t}</span>)}
        </div>
      </div>
    </div>
  );
}

function Step9Formats({ state, update }) {
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
      <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Format & Channel Choices</h2>
      <p className="text-sm text-gray-500 mt-1 mb-2">Your format focus tells the catalog planner whether to optimize for visual-first short-form content or deep long-form books. Your channel selections determine where your brand publishes — each active channel adds content weight to the pipeline, meaning more formats, more variations, and more touchpoints with your audience.</p>

      <div className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3 mt-6">Primary Format Focus</div>
      <p className="text-[11px] text-gray-500 mb-3">This is the most important format decision. It changes how the catalog planner distributes content across your entire brand.</p>
      <div className="grid grid-cols-2 gap-3 mb-8">
        <button onClick={() => setFocus("manga")}
          className={`p-5 rounded-xl border-2 text-left transition-all ${formatFocus === "manga" ? "border-gray-900 bg-gray-50 shadow-md" : "border-gray-200 bg-white hover:border-gray-300"}`}>
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-rose-500 to-purple-600 flex items-center justify-center mb-3"><Image size={24} className="text-white" /></div>
          <div className="text-sm font-bold text-gray-900">Manga / Visual</div>
          <p className="text-[11px] text-gray-500 mt-1 leading-relaxed">Illustrated panels, visual storytelling, manga-style layouts. Audiobooks default to short formats (15-30 min). Optimized for Gen Z and Gen Alpha visual-first consumption.</p>
          {formatFocus === "manga" && <div className="mt-2 bg-rose-50 rounded-lg p-2"><p className="text-[10px] text-rose-700">Catalog planner will prioritize short-form audiobooks, visual content, and illustration-heavy formats across all channels.</p></div>}
        </button>
        <button onClick={() => setFocus("book")}
          className={`p-5 rounded-xl border-2 text-left transition-all ${formatFocus === "book" ? "border-gray-900 bg-gray-50 shadow-md" : "border-gray-200 bg-white hover:border-gray-300"}`}>
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center mb-3"><BookOpen size={24} className="text-white" /></div>
          <div className="text-sm font-bold text-gray-900">Traditional Books</div>
          <p className="text-[11px] text-gray-500 mt-1 leading-relaxed">Full-length narrative books, deep guided programs, comprehensive workbooks. Audiobooks in long formats (3-8 hrs). Optimized for depth-seeking readers.</p>
          {formatFocus === "book" && <div className="mt-2 bg-amber-50 rounded-lg p-2"><p className="text-[10px] text-amber-700">Catalog planner will prioritize long-form books, complete programs, and in-depth series across all channels.</p></div>}
        </button>
      </div>
      {formatFocus && SELECTION_FEEDBACK.formats[formatFocus] && (
        <SelectionFeedback
          systemEffect={SELECTION_FEEDBACK.formats[formatFocus].systemEffect}
          emotionalBenefit={SELECTION_FEEDBACK.formats[formatFocus].emotionalBenefit}
          color={formatFocus === "manga" ? "#e11d48" : "#d97706"}
        />
      )}
      <div className="mb-4" />

      <div className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">Publishing Channels</div>
      <p className="text-[11px] text-gray-500 mb-3">Select all channels you want your brand to publish through. Each channel generates dedicated content adapted for that platform's format, audience, and algorithm requirements.</p>
      <div className="grid grid-cols-1 gap-2">
        {CHANNELS.map((ch) => {
          const active = channels.includes(ch.id);
          const Icon = ch.icon;
          return (
            <button key={ch.id} onClick={() => toggleChannel(ch.id)}
              className={`flex items-start gap-3 p-3.5 rounded-xl border-2 text-left transition-all ${active ? "border-gray-900 bg-gray-50" : "border-gray-200 bg-white hover:border-gray-300"}`}>
              <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${active ? "bg-gray-900" : "bg-gray-100"}`}>
                <Icon size={16} className={active ? "text-white" : "text-gray-400"} />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-gray-900">{ch.label}</span>
                  {active && <Check size={14} className="text-gray-900" />}
                </div>
                <p className="text-[10px] text-gray-500 mt-0.5">{ch.desc}</p>
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

function Step10Blueprint({ state }) {
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

  return (
    <div>
      <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Your Brand Blueprint</h2>
      <p className="text-sm text-gray-500 mt-1 mb-6">A complete report of your brand identity, projected impact scores, and all the choices that built this universe. Review everything below before launching.</p>

      <div className="grid grid-cols-2 gap-3 mb-8">
        {scores.map((s) => (
          <div key={s.label} className="bg-white rounded-xl p-4 border border-gray-200 text-center">
            <div className="relative w-16 h-16 mx-auto mb-2">
              <svg viewBox="0 0 64 64" className="w-full h-full -rotate-90">
                <circle cx="32" cy="32" r="28" fill="none" stroke="#f3f4f6" strokeWidth="5" />
                <circle cx="32" cy="32" r="28" fill="none" strokeWidth="5" strokeLinecap="round" style={{ color: s.value > 85 ? '#10b981' : s.value > 70 ? '#6366f1' : '#f59e0b' }} className="stroke-current" strokeDasharray={`${s.value * 1.759} 175.9`} />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center"><span className="text-lg font-black text-gray-900">{s.value}</span></div>
            </div>
            <div className="text-xs font-bold text-gray-900">{s.label}</div>
            <div className="text-[10px] text-gray-500 mt-0.5">{s.desc}</div>
          </div>
        ))}
      </div>

      <div className="rounded-xl bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 p-5 mb-6">
        <div className="flex items-center gap-2 mb-2"><Rocket size={16} className="text-emerald-600" /><span className="text-sm font-bold text-emerald-800">Brand Assessment</span></div>
        <p className="text-xs text-emerald-700 leading-relaxed">
          {marketability >= 85 ? "Exceptional brand positioning. Your archetype, audience, and topic choices align powerfully with high-revenue market segments. This brand has strong commercial potential with deep reader impact." : marketability >= 75 ? "Strong brand foundation. Your selections create a compelling identity with solid market alignment. A few more refinements could push this into exceptional territory." : "Good starting point. Your brand identity is taking shape — consider adding more topic selections and channel coverage to strengthen your market position."}
        </p>
      </div>

      <div className="space-y-3">
        {arch && <div className={`rounded-xl p-4 ${arch.bg} border ${arch.border}`}><div className="text-[10px] font-bold uppercase text-gray-500 mb-1">Emotional World</div><div className="font-bold text-gray-900">{arch.name}</div><div className="text-xs text-gray-600">{arch.tagline}</div></div>}
        <div className="grid grid-cols-2 gap-3">
          {persona && <div className="bg-white rounded-xl p-3 border border-gray-200"><div className="text-[10px] font-bold uppercase text-gray-400 mb-1">Primary Reader</div><div className="text-xs font-bold">{persona.emoji} {persona.label}</div></div>}
          {moment && <div className="bg-white rounded-xl p-3 border border-gray-200"><div className="text-[10px] font-bold uppercase text-gray-400 mb-1">Trigger Moment</div><div className="text-xs font-bold">{moment.emoji} {moment.label}</div></div>}
          {visual && <div className="bg-white rounded-xl p-3 border border-gray-200"><div className="text-[10px] font-bold uppercase text-gray-400 mb-1">Visual Style</div><div className="text-xs font-bold">{visual.label}</div></div>}
          {state.tradition && <div className="bg-white rounded-xl p-3 border border-gray-200"><div className="text-[10px] font-bold uppercase text-gray-400 mb-1">Tradition</div><div className="text-xs font-bold">{state.tradition}</div></div>}
          {state.onboardingLane && <div className="bg-white rounded-xl p-3 border border-gray-200"><div className="text-[10px] font-bold uppercase text-gray-400 mb-1">Onboarding Lane</div><div className="text-xs font-bold">{state.onboardingLane.replace(/_/g, " ")}</div></div>}
          {state.onboardingMarket && <div className="bg-white rounded-xl p-3 border border-gray-200"><div className="text-[10px] font-bold uppercase text-gray-400 mb-1">Onboarding Market</div><div className="text-xs font-bold">{state.onboardingMarket}</div></div>}
          {state.formatFocus && <div className="bg-white rounded-xl p-3 border border-gray-200"><div className="text-[10px] font-bold uppercase text-gray-400 mb-1">Format Focus</div><div className="text-xs font-bold">{state.formatFocus === "manga" ? "Manga / Visual" : "Traditional Books"}</div></div>}
          {(state.channels || []).length > 0 && <div className="bg-white rounded-xl p-3 border border-gray-200"><div className="text-[10px] font-bold uppercase text-gray-400 mb-1">Channels</div><div className="text-xs font-bold">{state.channels.length} active</div></div>}
        </div>
        {(state.emotions || []).length > 0 && <div className="bg-white rounded-xl p-3 border border-gray-200"><div className="text-[10px] font-bold uppercase text-gray-400 mb-1.5">Emotional Outcomes</div><div className="flex flex-wrap gap-1.5">{state.emotions.map((e) => <span key={e} className="text-[10px] bg-gray-100 text-gray-700 px-2.5 py-0.5 rounded-full">{e}</span>)}</div></div>}
        {(state.topicTags || []).length > 0 && <div className="bg-white rounded-xl p-3 border border-gray-200"><div className="text-[10px] font-bold uppercase text-gray-400 mb-1.5">Topics ({state.topicTags.length})</div><div className="flex flex-wrap gap-1.5">{state.topicTags.map((t) => <span key={t} className="text-[10px] bg-gray-100 text-gray-700 px-2.5 py-0.5 rounded-full">{t.replace(/-/g, " ")}</span>)}</div></div>}
        {(state.angles || []).length > 0 && <div className="bg-white rounded-xl p-3 border border-gray-200"><div className="text-[10px] font-bold uppercase text-gray-400 mb-1.5">Content Angles</div><div className="flex flex-wrap gap-1.5">{state.angles.map((a) => { const angle = V4_ANGLES.find((v) => v.id === a); return <span key={a} className="text-[10px] bg-gray-100 text-gray-700 px-2.5 py-0.5 rounded-full">{angle?.label || a}</span>; })}</div></div>}
      </div>
    </div>
  );
}

function Step11Launch({ state, update }) {
  const handleField = (field, val) => update({ contact: { ...state.contact, [field]: val } });
  const c = state.contact || {};
  const isReady = c.firstName?.trim() && c.lastName?.trim() && c.email?.trim() && c.email?.includes("@");
  const [submitted, setSubmitted] = useState(false);
  const [yamlOutput, setYamlOutput] = useState("");
  const [showYaml, setShowYaml] = useState(false);

  const handleLaunch = () => { setYamlOutput(generateYAML(state)); setSubmitted(true); };

  if (submitted) {
    const arch = ARCHETYPES.find((a) => a.id === state.archetype);
    const persona = PERSONAS.find((p) => p.id === state.persona);
    const moment = MOMENTS.find((m) => m.id === state.moment);
    const visual = VISUAL_STYLES.find((v) => v.id === state.visualStyle);

    const choiceAudit = [
      arch && { label: "Emotional World", value: arch.name, icon: arch.icon, gradient: arch.gradient, systemEffect: SELECTION_FEEDBACK.archetypes[state.archetype]?.systemEffect, emotionalBenefit: SELECTION_FEEDBACK.archetypes[state.archetype]?.emotionalBenefit },
      persona && { label: "Primary Reader", value: `${persona.emoji} ${persona.label}`, icon: Users, gradient: "from-blue-500 to-cyan-500", systemEffect: SELECTION_FEEDBACK.personas[state.persona]?.systemEffect, emotionalBenefit: SELECTION_FEEDBACK.personas[state.persona]?.emotionalBenefit },
      moment && { label: "Trigger Moment", value: `${moment.emoji} ${moment.label}`, icon: Target, gradient: "from-amber-500 to-orange-500", systemEffect: SELECTION_FEEDBACK.moments[state.moment]?.systemEffect, emotionalBenefit: SELECTION_FEEDBACK.moments[state.moment]?.emotionalBenefit },
      Object.keys(state.voiceSettings || {}).length > 0 && { label: "Voice Tone", value: `${Object.keys(state.voiceSettings).length} dimensions tuned`, icon: SlidersHorizontal, gradient: "from-indigo-500 to-violet-500", systemEffect: "All 4 voice dimensions calibrate prose rhythm, vocabulary register, sentence structure, and emotional temperature across every chapter, audiobook, and social post", emotionalBenefit: "Your reader experiences a voice that feels personally written for them — the exact blend of challenge and comfort they need. Every sentence lands because the tone matches their emotional readiness." },
      visual && { label: "Visual Style", value: visual.label, icon: Palette, gradient: "from-rose-500 to-pink-500", systemEffect: SELECTION_FEEDBACK.visualStyles[state.visualStyle]?.systemEffect, emotionalBenefit: SELECTION_FEEDBACK.visualStyles[state.visualStyle]?.emotionalBenefit },
      (state.emotions || []).length > 0 && { label: "Emotional Outcomes", value: state.emotions.join(", "), icon: Heart, gradient: "from-rose-400 to-red-500", systemEffect: `${state.emotions.length} transformation promises woven into every title, CTA, and marketing message`, emotionalBenefit: "These feelings become the north star of every piece of content — your reader knows exactly what transformation awaits them, creating hope before they read a single word." },
      state.tradition && { label: "Spiritual Foundation", value: state.tradition, icon: Sun, gradient: "from-amber-400 to-yellow-500", systemEffect: "Influences vocabulary, philosophical grounding, and tradition-specific references throughout all content", emotionalBenefit: "Readers with this tradition feel recognized and respected. The language carries the weight of authentic lineage rather than surface-level appropriation." },
      (state.angles || []).length > 0 && { label: "Content Angles", value: state.angles.map(a => V4_ANGLES.find(v => v.id === a)?.label).filter(Boolean).join(", "), icon: Layers, gradient: "from-purple-500 to-indigo-500", systemEffect: `${state.angles.length} framing modes active — every title opens with one of these argumentative strategies`, emotionalBenefit: "Each angle gives your reader a different doorway into healing. Multiple angles means your brand reaches people wherever they are in their readiness for change." },
      (state.topicTags || []).length > 0 && { label: "Search Territory", value: `${state.topicTags.length} topics claimed`, icon: Search, gradient: "from-emerald-500 to-teal-500", systemEffect: `${state.topicTags.length} search topics feed into title generation, keyword targeting, series planning, and ad campaigns`, emotionalBenefit: "Your content appears in the exact moment someone types their pain into a search bar. You're not marketing — you're answering a cry for help with exactly the right words." },
      state.onboardingLane && { label: "Onboarding Lane", value: state.onboardingLane.replace(/_/g, " "), icon: Layers, gradient: "from-fuchsia-500 to-purple-500", systemEffect: "Proof strip and registry matching now constrain to your selected lane so stakeholders preview the right output family early.", emotionalBenefit: "You can immediately see if the lane you want to lead with has convincing proof, reducing launch-time surprises." },
      state.onboardingMarket && { label: "Onboarding Market", value: state.onboardingMarket, icon: Globe, gradient: "from-sky-500 to-cyan-500", systemEffect: "Registry matches now use explicit market filtering during onboarding to avoid cross-market false confidence.", emotionalBenefit: "Your team reviews examples that actually match the market you plan to launch in." },
      state.formatFocus && { label: "Format Focus", value: state.formatFocus === "manga" ? "Manga / Visual" : "Traditional Books", icon: BookOpen, gradient: "from-cyan-500 to-blue-500", systemEffect: SELECTION_FEEDBACK.formats[state.formatFocus]?.systemEffect, emotionalBenefit: SELECTION_FEEDBACK.formats[state.formatFocus]?.emotionalBenefit },
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
                <span className="text-2xl font-black text-gray-900">{overallScore}</span>
                <span className="text-[8px] font-bold uppercase text-gray-400">Overall</span>
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
            <p className="text-lg font-bold text-gray-700 mb-1">Your brand universe is born.</p>
            <p className="text-sm text-gray-500 max-w-md mx-auto leading-relaxed">
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
                <div className="absolute inset-0 flex items-center justify-center"><span className="text-sm font-black text-gray-900">{s.value}</span></div>
              </div>
              <div className="text-[9px] font-bold uppercase text-gray-400">{s.label}</div>
            </div>
          ))}
        </div>

        {/* Choice Audit — every choice with what it does */}
        <div className="mb-8">
          <h2 className="text-lg font-extrabold text-gray-900 mb-1">Your Brand Choices</h2>
          <p className="text-xs text-gray-500 mb-4">Every choice you made, what it activates in the system, and how it helps your readers mentally and emotionally.</p>

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
                      <div className="text-[9px] font-bold uppercase text-gray-400">{choice.label}</div>
                      <div className="text-sm font-bold text-gray-900 truncate">{choice.value}</div>
                    </div>
                    <div className="text-[9px] font-bold text-emerald-500 bg-emerald-50 px-2 py-0.5 rounded-full flex-shrink-0">Active</div>
                  </div>
                  <div className="px-4 py-3 space-y-2.5">
                    <div className="flex items-start gap-2">
                      <div className="w-4 h-4 rounded-full bg-indigo-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Zap size={8} className="text-indigo-500" />
                      </div>
                      <div>
                        <span className="text-[9px] font-bold uppercase text-gray-400">System Effect </span>
                        <p className="text-[11px] text-gray-600 leading-relaxed">{choice.systemEffect}</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-4 h-4 rounded-full bg-rose-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Heart size={8} className="text-rose-400" />
                      </div>
                      <div>
                        <span className="text-[9px] font-bold uppercase text-gray-400">Reader Benefit </span>
                        <p className="text-[11px] text-gray-700 leading-relaxed font-medium">{choice.emotionalBenefit}</p>
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
            <p className="text-sm text-gray-800 leading-relaxed font-medium">
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
              <Download size={14} className="text-gray-500" />
              <span className="text-xs font-bold text-gray-700">Brand Configuration (YAML)</span>
            </div>
            <ChevronRight size={14} className={`text-gray-400 transition-transform ${showYaml ? "rotate-90" : ""}`} />
          </button>
          {showYaml && (
            <div className="bg-gray-900 p-4 overflow-auto max-h-96">
              <pre className="text-[11px] text-green-400 font-mono whitespace-pre-wrap">{yamlOutput}</pre>
            </div>
          )}
        </div>

        {/* Final Message */}
        <div className="text-center py-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-50 text-emerald-700 text-xs font-bold mb-3">
            <Check size={12} /> Brand configuration saved
          </div>
          <p className="text-sm text-gray-500 max-w-md mx-auto">
            Your brand universe is ready. The Pearl Prime system will use every choice you've made to generate your catalog — books, audiobooks, manga, videos, and social content that changes lives.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Launch Your Brand</h2>
      <p className="text-sm text-gray-500 mt-1 mb-6">Add your contact information to complete your brand setup. All required fields must be filled before the Launch Brand button activates.</p>
      <div className="space-y-4 mb-6">
        <div className="grid grid-cols-2 gap-3">
          <div><label className="text-xs font-semibold text-gray-600 mb-1 block">First Name *</label><input type="text" placeholder="First Name" className="w-full p-3 border border-gray-200 rounded-xl text-sm focus:border-gray-500 outline-none" value={c.firstName || ""} onChange={(e) => handleField("firstName", e.target.value)} /></div>
          <div><label className="text-xs font-semibold text-gray-600 mb-1 block">Last Name *</label><input type="text" placeholder="Last Name" className="w-full p-3 border border-gray-200 rounded-xl text-sm focus:border-gray-500 outline-none" value={c.lastName || ""} onChange={(e) => handleField("lastName", e.target.value)} /></div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div><label className="text-xs font-semibold text-gray-600 mb-1 block">Email *</label><input type="email" placeholder="you@example.com" className="w-full p-3 border border-gray-200 rounded-xl text-sm focus:border-gray-500 outline-none" value={c.email || ""} onChange={(e) => handleField("email", e.target.value)} /></div>
          <div><label className="text-xs font-semibold text-gray-600 mb-1 block">Phone</label><input type="tel" placeholder="+1 555 000 0000" className="w-full p-3 border border-gray-200 rounded-xl text-sm focus:border-gray-500 outline-none" value={c.phone || ""} onChange={(e) => handleField("phone", e.target.value)} /></div>
        </div>
        <div className="text-xs font-bold uppercase tracking-wider text-gray-400 mt-6 mb-3">Messaging Channels</div>
        <div className="grid grid-cols-2 gap-3">
          <div><label className="text-[10px] text-gray-400 font-semibold mb-1 block">LINE ID</label><input type="text" placeholder="U..." className="w-full p-2.5 border border-gray-200 rounded-lg text-sm focus:border-gray-500 outline-none" value={c.line || ""} onChange={(e) => handleField("line", e.target.value)} /></div>
          <div><label className="text-[10px] text-gray-400 font-semibold mb-1 block">WhatsApp</label><input type="tel" placeholder="+1..." className="w-full p-2.5 border border-gray-200 rounded-lg text-sm focus:border-gray-500 outline-none" value={c.whatsapp || ""} onChange={(e) => handleField("whatsapp", e.target.value)} /></div>
          <div><label className="text-[10px] text-gray-400 font-semibold mb-1 block">WeChat ID</label><input type="text" className="w-full p-2.5 border border-gray-200 rounded-lg text-sm focus:border-gray-500 outline-none" value={c.wechat || ""} onChange={(e) => handleField("wechat", e.target.value)} /></div>
          <div><label className="text-[10px] text-gray-400 font-semibold mb-1 block">FB Messenger</label><input type="text" className="w-full p-2.5 border border-gray-200 rounded-lg text-sm focus:border-gray-500 outline-none" value={c.messenger || ""} onChange={(e) => handleField("messenger", e.target.value)} /></div>
        </div>
        <div><label className="text-[10px] text-gray-400 font-semibold mb-1 block">Preferred Channel</label><select className="w-full p-2.5 border border-gray-200 rounded-lg text-sm bg-white focus:border-gray-500 outline-none" value={c.preferred || "email"} onChange={(e) => handleField("preferred", e.target.value)}><option value="email">Email Only</option><option value="line">LINE</option><option value="whatsapp">WhatsApp</option><option value="wechat">WeChat</option><option value="fb_messenger">FB Messenger</option></select></div>
        <div className="bg-gray-50 rounded-xl p-3 flex items-start gap-2"><Shield size={14} className="text-gray-400 flex-shrink-0 mt-0.5" /><p className="text-[11px] text-gray-500">Tax ID (SSN/EIN) collected through a separate secure process after approval. We never collect sensitive financial information through this form.</p></div>
      </div>
      <button onClick={handleLaunch} disabled={!isReady}
        className={`w-full py-5 rounded-2xl text-lg font-extrabold tracking-tight transition-all ${isReady ? "bg-gray-900 text-white hover:bg-gray-800 shadow-lg hover:shadow-xl cursor-pointer" : "bg-gray-200 text-gray-400 cursor-not-allowed"}`}>
        {isReady ? "Launch Brand" : "Complete required fields to launch"}
      </button>
      {!isReady && <p className="text-center text-[11px] text-gray-400 mt-2">Fill in First Name, Last Name, and Email to activate the launch button.</p>}
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
  let y = `# Brand Admin Application — ${ts}\n# Pearl Prime Brand Configuration\n\n`;
  y += `brand_admin:\n  first_name: "${san(c.firstName)}"\n  last_name: "${san(c.lastName)}"\n  email: "${san(c.email)}"\n  phone: "${san(c.phone)}"\n\n`;
  y += `  messaging_channels:\n    line_id: "${san(c.line)}"\n    whatsapp: "${san(c.whatsapp)}"\n    wechat_id: "${san(c.wechat)}"\n    fb_messenger: "${san(c.messenger)}"\n    preferred_channel: "${c.preferred || "email"}"\n\n`;
  y += `  brand_positioning:\n    brand_angle: "${state.archetype}"\n    trigger_moment: "${state.moment}"\n    persona: "${state.persona}"\n\n`;
  y += `  voice_settings:\n`;
  Object.entries(state.voiceSettings || {}).forEach(([k, v]) => { y += `    ${k}: ${v}\n`; });
  y += `\n  visual_style: "${state.visualStyle}"\n  tradition: "${state.tradition}"\n  emotional_outcomes: [${(state.emotions || []).map((e) => `"${e}"`).join(", ")}]\n\n`;
  y += `  content_angles: [${(state.angles || []).map((a) => `"${a}"`).join(", ")}]\n  topic_tags: [${(state.topicTags || []).map((t) => `"${t}"`).join(", ")}]\n\n`;
  y += `  onboarding_lane: "${state.onboardingLane || "self_help"}"\n  onboarding_market: "${state.onboardingMarket || "us"}"\n`;
  y += `  format_focus: "${state.formatFocus || "book"}"\n  channels: [${(state.channels || []).map((c) => `"${c}"`).join(", ")}]\n\n`;
  y += `  revenue_blend:\n    user_topics_weight: 0.30\n    proven_topics_weight: 0.70\n    note: "System blends brand identity with persona-based demand and proven search terms"\n\n`;
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
        <button onClick={() => setActive("a")} className={`flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-all ${active === "a" ? `${colorA} bg-gray-50` : "text-gray-400"}`}>{labelA}</button>
        <button onClick={() => setActive("b")} className={`flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-all ${active === "b" ? `${colorB} bg-gray-50` : "text-gray-400"}`}>{labelB}</button>
      </div>
      <div className="p-5 min-h-[140px] transition-all duration-300">{active === "a" ? contentA : contentB}</div>
    </div>
  );
}

function IntroWelcome({ onNext }) {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <div className="max-w-3xl mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-gray-100 text-gray-600 text-xs font-semibold mb-6"><Sparkles size={12} /> Pearl Prime Brand Studio</div>
          <h1 className="text-5xl font-black tracking-tight leading-tight mb-2 bg-gradient-to-r from-purple-600 via-violet-600 to-purple-600 bg-clip-text text-transparent">Define Your Brand</h1>
          <h2 className="text-3xl font-black tracking-tight bg-gradient-to-r from-purple-600 via-violet-600 to-purple-600 bg-clip-text text-transparent mb-6">Create A Universe</h2>
          <p className="text-gray-500 text-lg max-w-xl mx-auto leading-relaxed">A brand in Pearl Prime is a complete publishing identity — with its own voice, visual world, emotional territory, and audience. Every book, audiobook, video, and piece of content flows from the choices you make here.</p>
        </div>
        <div className="rounded-2xl bg-gray-50 border border-gray-200 p-8 mb-10">
          <h2 className="text-xl font-bold mb-4 text-gray-900">What is a Pearl Prime brand?</h2>
          <div className="grid grid-cols-1 gap-4">
            {[
              { icon: PenTool, label: "A writing voice", desc: "Gentle or direct. Poetic or practical. Your brand's prose has a personality that readers recognize across every title." },
              { icon: Image, label: "A visual world", desc: "Cover art, color palettes, typography — from soft watercolors to bold geometric. Your books look like they belong together." },
              { icon: Film, label: "A video presence", desc: "Daily TikTok, YouTube Shorts, and Reels. Cinematic or minimal. Symbolic or raw. Your social content has a signature look." },
              { icon: Users, label: "An audience", desc: "Burned-out professionals, Gen Z navigators, grief carriers, Gen Alpha explorers — your brand speaks to one core reader and reaches all." },
              { icon: Layers, label: "A content system", desc: "Books, audiobooks, workbooks, manga, exercises, freebies — all generated from your brand's DNA. Hundreds of titles, one coherent identity." },
            ].map(({ icon: I, label, desc }) => (
              <div key={label} className="flex gap-4 items-start">
                <div className="w-10 h-10 rounded-xl bg-gray-200 flex items-center justify-center flex-shrink-0"><I size={18} className="text-gray-600" /></div>
                <div><h3 className="font-bold text-sm text-gray-900">{label}</h3><p className="text-xs text-gray-500 leading-relaxed mt-0.5">{desc}</p></div>
              </div>
            ))}
          </div>
        </div>
        <div className="text-center">
          <button onClick={onNext} className="inline-flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-gray-900 text-white font-bold text-sm shadow-lg hover:bg-gray-800 transition-all hover:-translate-y-0.5">See Your Journey <ChevronRight size={18} /></button>
        </div>
      </div>
    </div>
  );
}

function IntroJourney({ onNext, onBack }) {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <button onClick={onBack} className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 mb-6"><ChevronLeft size={14} /> Back</button>
        <div className="text-center mb-10">
          <h1 className="text-3xl font-black tracking-tight mb-2">Your Journey</h1>
          <p className="text-lg font-bold text-gray-500">11 choices that build everything</p>
          <p className="text-sm text-gray-400 mt-2 max-w-lg mx-auto">Each step below shapes a different dimension of your brand. Together, they create a complete publishing identity that produces hundreds of titles across 40+ platforms in 75+ countries.</p>
        </div>
        <div className="space-y-2 mb-12">
          {[
            { step: "1", name: "Emotional World", desc: "Choose your brand's archetype — the feeling that defines everything", color: "from-indigo-500 to-blue-500" },
            { step: "2", name: "Primary Reader", desc: "Pick the protagonist of your brand narrative", color: "from-emerald-500 to-teal-500" },
            { step: "3", name: "Trigger Moment", desc: "The exact moment they reach for your book", color: "from-rose-500 to-pink-500" },
            { step: "4", name: "Voice Tone Graphs", desc: "Slide and see how your voice shapes the reading experience", color: "from-indigo-500 to-violet-500" },
            { step: "5", name: "Voice Impact", desc: "See the psychological and emotional benefits of each setting", color: "from-purple-500 to-indigo-500" },
            { step: "6", name: "Visual & Emotions", desc: "Define your color world, style, and transformation promise", color: "from-rose-500 to-amber-500" },
            { step: "7", name: "Topics & Angles", desc: "Claim the search territory your brand will own", color: "from-amber-500 to-orange-500" },
            { step: "8", name: "Market Intelligence", desc: "See how we blend your vision with proven demand data", color: "from-emerald-500 to-green-500" },
            { step: "9", name: "Formats & Channels", desc: "Manga or books, audiobooks or TikTok — choose your pipeline", color: "from-blue-500 to-cyan-500" },
            { step: "10", name: "Blueprint", desc: "Full report with scores: marketability, youth reach, life impact", color: "from-violet-500 to-purple-500" },
            { step: "11", name: "Launch", desc: "Add your info and launch your brand into the universe", color: "from-gray-700 to-gray-900" },
          ].map(({ step, name, desc, color }) => (
            <div key={step} className="flex gap-3 items-center bg-gray-50 rounded-xl p-3.5 border border-gray-100 hover:border-gray-200 transition-all">
              <div className={`w-9 h-9 rounded-full bg-gradient-to-br ${color} flex items-center justify-center text-white font-bold text-xs flex-shrink-0`}>{step}</div>
              <div className="flex-1">
                <span className="font-bold text-sm text-gray-900">{name}</span>
                <span className="text-xs text-gray-500 ml-2">{desc}</span>
              </div>
            </div>
          ))}
        </div>
        <div className="text-center">
          <p className="text-gray-400 text-sm mb-6">First, let's show you what your choices create.</p>
          <button onClick={onNext} className="inline-flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-gray-900 text-white font-bold text-sm shadow-lg hover:bg-gray-800 transition-all hover:-translate-y-0.5">See Examples <ChevronRight size={18} /></button>
        </div>
      </div>
    </div>
  );
}

function ShowcaseProse({ onNext, onBack }) {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <button onClick={onBack} className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 mb-4"><ChevronLeft size={14} /> Back</button>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 text-indigo-600 text-xs font-semibold mb-4"><PenTool size={12} /> Step 1 Preview — Writing Voice</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">Same topic. Completely different voice.</h1>
        <p className="text-gray-500 mb-8">Your archetype choice transforms how every sentence sounds. Two brands, same topic — watch how the prose, exercises, and energy change completely.</p>
        <CompareBlock labelA="Stillness Lab" labelB="Clear Mind Lab" colorA="text-indigo-600" colorB="text-amber-600"
          contentA={<div><div className="flex gap-2 mb-3"><div className="w-14 h-20 rounded-lg shadow-md flex-shrink-0" style={{ background: "linear-gradient(135deg, #6366f1, #818cf8, #e0e7ff)" }} /><div><div className="text-[10px] text-gray-400 font-semibold uppercase">Stillness Lab</div><div className="text-sm font-bold text-gray-900">The Body Keeps the Score at 2AM</div></div></div><p className="text-sm text-gray-700 leading-relaxed italic border-l-2 border-indigo-300 pl-3">"Your body remembers what your mind tries to forget. Right now, your shoulders are holding yesterday's argument."</p><div className="mt-3 bg-indigo-50 rounded-lg p-3"><div className="text-[10px] font-bold text-indigo-600 uppercase mb-1">Exercise</div><p className="text-xs text-indigo-800">"Inhale for 4 counts. Hold for 7. Exhale slowly for 8."</p></div></div>}
          contentB={<div><div className="flex gap-2 mb-3"><div className="w-14 h-20 rounded-lg shadow-md flex-shrink-0" style={{ background: "linear-gradient(135deg, #d97706, #f59e0b, #fef3c7)" }} /><div><div className="text-[10px] text-gray-400 font-semibold uppercase">Clear Mind Lab</div><div className="text-sm font-bold text-gray-900">Your Phone Is Stealing Your Sleep</div></div></div><p className="text-sm text-gray-700 leading-relaxed italic border-l-2 border-amber-400 pl-3">"You're staring at the ceiling because your brain is running yesterday's argument on a loop."</p><div className="mt-3 bg-amber-50 rounded-lg p-3"><div className="text-[10px] font-bold text-amber-600 uppercase mb-1">Exercise</div><p className="text-xs text-amber-800">"Phone in another room. Lie flat. Breathe out longer than in. 90 seconds. Go."</p></div></div>}
        />
        <div className="text-center mt-8"><button onClick={onNext} className="inline-flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-gray-900 text-white font-bold text-sm hover:bg-gray-800 transition-all">See Cover Differences <ChevronRight size={18} /></button></div>
      </div>
    </div>
  );
}

function ShowcaseCovers({ onNext, onBack }) {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <button onClick={onBack} className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 mb-4"><ChevronLeft size={14} /> Back</button>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-50 text-rose-600 text-xs font-semibold mb-4"><Image size={12} /> Visual Style Preview</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">Your visual style shapes everything.</h1>
        <p className="text-gray-500 mb-8">Covers, social content, video aesthetics — all driven by one choice.</p>
        <div className="grid grid-cols-3 gap-4 mb-8">
          {ARCHETYPES.slice(0, 3).map((arch) => (
            <div key={arch.id} className="text-center">
              <div className="w-full h-40 rounded-xl shadow-lg mb-2" style={{ background: `linear-gradient(135deg, ${arch.coverColors[0]}, ${arch.coverColors[1]}, ${arch.coverColors[2]})` }}>
                <div className="flex flex-col items-center justify-end h-full p-3"><div className="text-[9px] font-bold text-white/90 text-center leading-tight">{arch.sampleTitle}</div><div className="text-[7px] text-white/60 mt-0.5">{arch.name}</div></div>
              </div>
              <div className="text-xs font-bold text-gray-900">{arch.name}</div><div className="text-[10px] text-gray-500">{arch.coverStyle}</div>
            </div>
          ))}
        </div>
        <div className="text-center mt-8"><button onClick={onNext} className="inline-flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-gray-900 text-white font-bold text-sm hover:bg-gray-800 transition-all">See Video Styles <ChevronRight size={18} /></button></div>
      </div>
    </div>
  );
}

function ShowcaseVideo({ onNext, onBack }) {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <button onClick={onBack} className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 mb-4"><ChevronLeft size={14} /> Back</button>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 text-amber-600 text-xs font-semibold mb-4"><Film size={12} /> Video & Social Preview</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">Daily content. Your signature look.</h1>
        <p className="text-gray-500 mb-8">TikTok, YouTube Shorts, Reels — all auto-generated from your brand DNA across 48 Social channels.</p>
        <div className="grid grid-cols-2 gap-4 mb-8">
          {ARCHETYPES.slice(0, 4).map((arch) => (
            <div key={arch.id} className="rounded-xl overflow-hidden border border-gray-200">
              <div className="h-32 flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${arch.coverColors[0]}88, ${arch.coverColors[1]}66)` }}><div className="text-center"><Play size={24} className="text-white/60 mx-auto mb-1" /><div className="text-[10px] text-white/80 font-bold">{arch.name}</div></div></div>
              <div className="p-3 bg-white"><div className="text-xs font-bold text-gray-900">{arch.videoStyle}</div><div className="text-[10px] text-gray-500 mt-0.5">Daily across YouTube, TikTok, Instagram, Facebook, X</div></div>
            </div>
          ))}
        </div>
        <div className="text-center mt-8"><button onClick={onNext} className="inline-flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-gray-900 text-white font-bold text-sm hover:bg-gray-800 transition-all">See Format Diversity <ChevronRight size={18} /></button></div>
      </div>
    </div>
  );
}

function ShowcaseFormats({ onNext, onBack }) {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <button onClick={onBack} className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 mb-4"><ChevronLeft size={14} /> Back</button>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 text-emerald-600 text-xs font-semibold mb-4"><Layers size={12} /> Format Diversity</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">One brand. Infinite formats.</h1>
        <p className="text-gray-500 mb-8">Books, manga, audiobooks, courses, journals — all from the same brand DNA.</p>
        <div className="grid grid-cols-3 gap-3 mb-8">
          {V4_FORMATS_STRUCTURAL.map((f) => (
            <div key={f.id} className="p-4 rounded-xl border border-gray-200 bg-white">
              <div className="text-[10px] text-gray-400 font-mono mb-1">{f.id}</div><div className="text-xs font-bold text-gray-900">{f.label}</div><div className="text-[10px] text-gray-500 mt-0.5">{f.desc}</div>
              <div className="mt-2 flex items-center gap-2"><span className="text-[9px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{f.chapters} ch</span><span className="text-[9px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{f.tier}</span></div>
            </div>
          ))}
        </div>
        <div className="rounded-xl bg-gray-50 border border-gray-200 p-5 mb-8"><p className="text-xs text-gray-600 leading-relaxed">Plus manga editions, audiobooks in multiple lengths, daily video content, pocket guides, 7-day transformation programs, mastercourse series, and interactive workbooks. The system adapts your brand to every format and platform automatically.</p></div>
        <div className="text-center mt-8"><button onClick={onNext} className="inline-flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-gray-900 text-white font-bold text-sm hover:bg-gray-800 transition-all">Start Building Your Brand <ArrowRight size={18} /></button></div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// MAIN WIZARD
// ═══════════════════════════════════════════════════════════

const STEP_LABELS = ["Emotional World", "Primary Reader", "Trigger Moment", "Voice Graphs", "Voice Impact", "Visual & Emotions", "Topics", "Market Intel", "Formats", "Blueprint", "Launch"];

export default function BrandWizard() {
  const [phase, setPhase] = useState("intro");
  const [introPage, setIntroPage] = useState(0);
  const [step, setStep] = useState(0);
  const [state, setState] = useState({
    archetype: null, persona: null, moment: null,
    voiceSettings: {}, visualStyle: null, emotions: [],
    tradition: "", angles: [], topicTags: [],
    formatFocus: null, channels: [],
    onboardingLane: "self_help", onboardingMarket: "us",
    contact: { firstName: "", lastName: "", email: "", phone: "", line: "", whatsapp: "", wechat: "", messenger: "", preferred: "email" },
  });

  const update = useCallback((patch) => setState((prev) => ({ ...prev, ...patch })), []);
  const scrollTop = () => window.scrollTo({ top: 0, behavior: "smooth" });
  const nextIntro = () => { setIntroPage((p) => p + 1); scrollTop(); };
  const prevIntro = () => { if (introPage > 0) { setIntroPage((p) => p - 1); scrollTop(); } };
  const startWizard = () => { setPhase("wizard"); setStep(0); scrollTop(); };
  const nextStep = () => { if (step < 10) { setStep((s) => s + 1); scrollTop(); } };
  const prevStep = () => { if (step > 0) { setStep((s) => s - 1); scrollTop(); } else { setPhase("intro"); setIntroPage(5); scrollTop(); } };

  // INTRO: 0=welcome, 1=journey, 2=prose, 3=covers, 4=video, 5=formats
  if (phase === "intro") {
    if (introPage === 0) return <IntroWelcome onNext={nextIntro} />;
    if (introPage === 1) return <IntroJourney onNext={nextIntro} onBack={prevIntro} />;
    if (introPage === 2) return <ShowcaseProse onNext={nextIntro} onBack={prevIntro} />;
    if (introPage === 3) return <ShowcaseCovers onNext={nextIntro} onBack={prevIntro} />;
    if (introPage === 4) return <ShowcaseVideo onNext={nextIntro} onBack={prevIntro} />;
    if (introPage === 5) return <ShowcaseFormats onNext={startWizard} onBack={prevIntro} />;
  }

  const canNext = step === 0
    ? !!state.archetype
    : step === 1
      ? !!state.persona && !!state.onboardingLane && !!state.onboardingMarket
      : step === 2
        ? !!state.moment
        : true;

  const steps = [
    <Step1Archetype key={0} state={state} update={update} />,
    <Step2PrimaryReader key={1} state={state} update={update} />,
    <Step3TriggerMoment key={2} state={state} update={update} />,
    <Step4VoiceGraphs key={3} state={state} update={update} />,
    <Step5VoiceEffects key={4} state={state} update={update} />,
    <Step6VisualStyle key={5} state={state} update={update} />,
    <Step7Topics key={6} state={state} update={update} />,
    <Step8MarketIntel key={7} state={state} />,
    <Step9Formats key={8} state={state} update={update} />,
    <Step10Blueprint key={9} state={state} />,
    <Step11Launch key={10} state={state} update={update} />,
  ];

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-4 py-6">
        <ProgressBar step={step} total={11} labels={STEP_LABELS} />
        <div className="flex gap-6">
          <div className="flex-1 min-w-0">
            {steps[step]}
            <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-100">
              <button onClick={prevStep} className="flex items-center gap-1.5 px-4 py-2.5 text-sm font-semibold text-gray-500 hover:text-gray-800 transition-colors"><ChevronLeft size={16} /> Back</button>
              {step < 10 && <button onClick={nextStep} disabled={!canNext} className={`flex items-center gap-1.5 px-6 py-2.5 rounded-xl text-sm font-bold transition-all ${canNext ? "bg-gray-900 text-white hover:bg-gray-800 shadow-md" : "bg-gray-200 text-gray-400 cursor-not-allowed"}`}>Continue <ChevronRight size={16} /></button>}
            </div>
          </div>
          <div className="w-72 flex-shrink-0 hidden lg:block">
            <div className="sticky top-6">
              <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-3">Brand Impact</div>
              <PersonaImpactPanel state={state} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}