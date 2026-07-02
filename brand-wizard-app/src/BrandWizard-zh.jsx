import { useState, useCallback, useRef, useMemo, useEffect } from "react";
import { useTranslation } from "./useTranslation.jsx";
import { matchBrand } from "./brandMatch.js";
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
    id: "nervous_system", name: "静息实验室",
    tagline: "当身体不停呐喊时",
    icon: Shield, gradient: "from-indigo-500 to-blue-600",
    bg: "bg-gradient-to-br from-indigo-50 to-blue-50",
    accent: "text-indigo-600", border: "border-indigo-200", activeBorder: "border-indigo-500",
    tags: ["平静", "躯体", "调节"],
    coverStyle: "柔和渐变、低饱和色调、有机线条",
    proseStyle: "温柔、从容、随呼吸而行",
    videoStyle: "慢镜头自然景象、柔焦画面、环境氛围",
    sampleTitle: "凌晨两点，身体记得一切",
    sampleSubtitle: "为停不下来的心灵重置神经系统",
    sampleProse: "您的身体记得那些您的大脑试图遗忘的一切。此刻，您的肩膀还扛着昨天的争吵，您的牙关还咬着那些没说出口的话。这不是缺陷——这是您的神经系统在做它本该做的事。",
    sampleExercise: "4-7-8 呼吸重置：吸气数 4 拍，屏息数 7 拍，缓慢呼气数 8 拍。重复三次。57 秒，即可改变整个神经系统的状态。",
    coverColors: ["#6366f1", "#818cf8", "#e0e7ff"],
    emotions: ["终于平静", "在身体里感到安全", "释放", "脚踏实地", "允许自己休息"],
    visionVibe: "在这个世界里，寂静不是空洞的——它是饱满的。身体是指南针，不是囚笼。读者找到安全感，不是通过逃避感受，而是终于学会倾听它。",
  },
  {
    id: "identity_direction", name: "指南针工作室",
    tagline: "献给那些感到迷茫但未破碎的人",
    icon: Compass, gradient: "from-emerald-500 to-teal-600",
    bg: "bg-gradient-to-br from-emerald-50 to-teal-50",
    accent: "text-emerald-600", border: "border-emerald-200", activeBorder: "border-emerald-500",
    tags: ["方向", "身份", "目标"],
    coverStyle: "简洁线条、罗盘图案、开阔地平线",
    proseStyle: "直接、温暖、向前",
    videoStyle: "延时旅途、黎明场景、道路意象",
    sampleTitle: "你没有落后——你在建造",
    sampleSubtitle: "在所有人看似都已找到方向时，寻找属于自己的路",
    sampleProse: "刷一刷动态，每个人都在赢。他们有事业、有感情、有那间养得活植物的公寓。而你坐在这里，不知道自己究竟在做什么。",
    sampleExercise: "诚实盘点：写下这周你主动选择的三件事——哪怕是小事。一顿饭、一次对话、一次拒绝。再写下一件你回避的事。这个模式，就是你的指南针。",
    coverColors: ["#059669", "#34d399", "#d1fae5"],
    emotions: ["头脑清晰", "与目标相连", "充满希望", "自信", "充满活力"],
    visionVibe: "在这个世界里，不知道不是失败——那是开始。方向来自诚实的自我观察，而非与外界的比较。读者在一个个小小的、勇敢的选择中，建立起自己的身份认同。",
  },
  {
    id: "emotional_healing", name: "柔光灯笼",
    tagline: "悲伤不遵循时间表",
    icon: Heart, gradient: "from-rose-500 to-pink-600",
    bg: "bg-gradient-to-br from-rose-50 to-pink-50",
    accent: "text-rose-600", border: "border-rose-200", activeBorder: "border-rose-500",
    tags: ["疗愈", "悲伤", "温柔"],
    coverStyle: "温暖水彩、柔和光线、亲密特写",
    proseStyle: "温柔、见证、给予许可",
    videoStyle: "温馨灯光、窗上雨滴、温暖室内",
    sampleTitle: "现在不好受，没关系",
    sampleSubtitle: "陪你度过那些无人预警的悲伤",
    sampleProse: "没有人告诉你，悲伤可以是这种感觉——不是哭泣，而是麻木。是你忘记为什么走进这个房间，是食物失去了味道，是电话响了你只是盯着看。",
    sampleExercise: "见证练习：把一只手放在胸口。大声说出来：「这很难。我有权利感受这一切。我现在不需要解决它。」感受内心发生了什么变化。",
    coverColors: ["#f43f5e", "#fb7185", "#ffe4e6"],
    emotions: ["不再孤单", "被宽恕", "释放", "在身体里感到安全", "充满希望"],
    visionVibe: "在这个世界里，痛苦不需要转化为生产力。悲伤被陪伴见证，而非被解决建议。读者找到疗愈，不是因为被修复，而是终于被看见。",
  },
  {
    id: "performance_focus", name: "澄心实验室",
    tagline: "切断噪音，执行要事",
    icon: Zap, gradient: "from-amber-500 to-orange-600",
    bg: "bg-gradient-to-br from-amber-50 to-orange-50",
    accent: "text-amber-600", border: "border-amber-200", activeBorder: "border-amber-500",
    tags: ["专注", "自律", "执行"],
    coverStyle: "粗体排版、高对比度、几何设计",
    proseStyle: "直接、有力、行动导向",
    videoStyle: "快速剪辑、深色背景、动态文字",
    sampleTitle: "你的手机正在偷走你的人生",
    sampleSubtitle: "21 天方案，夺回深度专注力",
    sampleProse: "你在午前查看手机 47 次。不是因为你自律性差——而是屏幕上的每一个应用，都是由博士团队精心设计，专门劫持你的多巴胺系统。",
    sampleExercise: "90 分钟专注块：设一个计时器，选定一项任务，手机放到另一个房间。计时结束时，你就完成了——哪怕还不完美。发出去吧。",
    coverColors: ["#d97706", "#f59e0b", "#fef3c7"],
    emotions: ["掌控感", "头脑清晰", "充满活力", "自信", "有韧性"],
    visionVibe: "在这个世界里，清晰是武器，行动胜过思考。读者穿越信息过载，建立不依赖意志力运转的系统。",
  },
  {
    id: "spiritual_awakening", name: "凤凰涅槃",
    tagline: "旧我必须死去，真我才能重生",
    icon: Flame, gradient: "from-purple-500 to-violet-600",
    bg: "bg-gradient-to-br from-purple-50 to-violet-50",
    accent: "text-purple-600", border: "border-purple-200", activeBorder: "border-purple-500",
    tags: ["觉醒", "意义", "目标"],
    coverStyle: "神圣几何、宇宙渐变、金色点缀",
    proseStyle: "沉思、多层次、诗意",
    videoStyle: "电影感自然景观、宇宙意象、仪式性动作",
    sampleTitle: "思绪之间的寂静，即是神性",
    sampleSubtitle: "为那些试遍一切、最终放弃的人写的冥想指引",
    sampleProse: "你读过那些书，下载过那些应用，坐在蒲团上等待什么发生。什么都没有——只有你的购物清单不请自来。",
    sampleExercise: "间隙练习：闭上眼睛，深吸一口气。在吸气顶点、呼气之前——感受那个间隙，停在那里。那就是门。",
    coverColors: ["#7c3aed", "#a78bfa", "#ede9fe"],
    emotions: ["活在当下", "与目标相连", "脚踏实地", "释放", "充满希望"],
    visionVibe: "在这个世界里，神圣就藏在平凡之中，寂静不是空洞而是光芒四射。读者发现，他们一直在寻找的，也一直在寻找他们。",
  },
];

const PERSONAS = [
  { id: "burned_out_pro", label: "倦怠职场人", emoji: "💼", desc: "精疲力竭、麻木、靠残存动力硬撑", needs: "重启、缓解、允许自己停下", impact: "内容切入「周日焦虑」和职场疲惫叙事" },
  { id: "gen_z_seeker", label: "Gen Z 探索者", emoji: "🧭", desc: "压力过载、不断比较、不停刷屏", needs: "方向、认可、真实可用的工具", impact: "短内容优先，TikTok 原生钩子，反内卷基调" },
  { id: "gen_alpha", label: "Gen Alpha 探索者", emoji: "🌱", desc: "在过度刺激中成长，早期具备情感觉察力", needs: "适龄工具、情感词汇、安全引导", impact: "以漫画视觉为主，游戏化练习，适合监护人审阅" },
  { id: "grief_carrier", label: "悲伤承载者", emoji: "🕯️", desc: "失去、麻木、无法言说", needs: "被见证、温柔以待、无需「修复」", impact: "给予许可的语言，不强行正能量，温和行动引导" },
  { id: "anxious_achiever", label: "焦虑成就者", emoji: "⚡", desc: "外在成功，内在崩塌", needs: "神经系统支持、诚实面对", impact: "高绩效框架与脆弱感的隐秘入口" },
  { id: "spiritual_returner", label: "灵性回归者", emoji: "🌅", desc: "试过一切，仍在寻找", needs: "深度、真实、拒绝空话", impact: "深度沉思散文，尊重传统，去大师化" },
  { id: "new_parent", label: "疲惫新手父母", emoji: "👶", desc: "身份迷失、时间匮乏、充满愧疚", needs: "快速工具、自我慈悲", impact: "微内容优先，零内疚框架，实用练习" },
];

const MOMENTS = [
  { id: "2am_overthinking", label: "凌晨 2 点 — 思绪停不下来", scene: "黑暗的房间，手机的微光，飞速运转的思绪", emoji: "🌙", hookStyle: "以辗转难眠的感受开篇，认可那种螺旋式焦虑，提供一个即时的接地工具" },
  { id: "after_breakup", label: "分手或失去之后", scene: "空荡荡的公寓，沉默，麻木", emoji: "💔", hookStyle: "精准命名那种特定的悲伤——不是悲哀，而是麻木，是食物失去味道的那种" },
  { id: "burnout_cant_quit", label: "倦怠却无法停下", scene: "办公室洗手间，深呼吸，面具重新戴上", emoji: "🔥", hookStyle: "捕捉他们戴上面具的那一刻，道出公开表演与私下崩溃之间的落差" },
  { id: "feeling_behind", label: "感觉落后于人生", scene: "刷着动态，每个人都在赢，只有你原地踏步", emoji: "📱", hookStyle: "精准触达比较性刷屏行为，将「落后」重新定义为一种建构，让手机成为触发物" },
  { id: "panic_spike", label: "恐慌发作 / 焦虑骤升", scene: "胸口紧绷，无法呼吸，世界在收缩", emoji: "😰", hookStyle: "身体优先的语言，先命名身体感受再命名情绪，立即进行躯体干预" },
  { id: "sunday_dread", label: "周日夜晚的周一焦虑", scene: "沙发上，钟声滴答，胃在下沉", emoji: "⏰", hookStyle: "触及每周一次的预期性焦虑循环，认可那种沉重感，将周日重构为一种夺回" },
];

const TRADITIONS = [
  "禅宗佛教", "苏菲神秘主义", "吠檀多", "金刚乘佛教", "道教",
  "斯多葛主义", "佛教心理学", "躯体治疗", "多迷走神经理论",
  "默观基督教", "原住民智慧", "世俗正念",
  "呼吸科学", "深度心理学"
];

const VOICE_SLIDERS = [
  { id: "gentleDirect", left: "温柔", right: "直接", default: 50, color: "#6366f1", desc: "控制句子的柔和度，赋予许可的语言与命令式语气之间的平衡" },
  { id: "simpleDeep", left: "简洁", right: "深邃", default: 50, color: "#059669", desc: "控制词汇密度、隐喻层次和概念复杂度" },
  { id: "emotionalLogical", left: "情感化", right: "逻辑化", default: 25, color: "#f43f5e", desc: "控制故事与数据的比例、脆弱感的程度和分析框架" },
  { id: "spiritualPractical", left: "灵性", right: "实用", default: 50, color: "#7c3aed", desc: "控制传统引用、神圣语言、工具优先与意义优先之间的平衡" },
];

const VISUAL_STYLES = [
  {
    id: "calm_minimal", label: "平静 / 极简", desc: "干净、通透、大量留白",
    palette: ["#f8fafc", "#e2e8f0", "#94a3b8", "#475569"], mood: "宁静、开阔、可呼吸",
    imagePrompt: "Minimalist book cover with vast white space, single delicate ink wash element floating in center, soft grey gradient background, thin sans-serif typography, Japanese zen aesthetic, editorial photography style, muted tones, clean geometric border",
    emotionPrompt: "Abstract soft watercolor wash in pale blue and white, single drop of color expanding outward in calm ripples, zen garden raked sand pattern, misty morning light, feeling of deep exhale and release",
  },
  {
    id: "dark_intense", label: "深沉 / 强烈", desc: "情绪感、高对比、戏剧化",
    palette: ["#1e1b4b", "#312e81", "#6366f1", "#c7d2fe"], mood: "有力、沉浸、电影感",
    imagePrompt: "Dramatic book cover with deep indigo and black, single shaft of violet light cutting through darkness, bold condensed typography, cinematic film grain, high contrast, moody atmospheric fog, Blade Runner color palette",
    emotionPrompt: "Person standing at edge of cliff at night, lightning illuminating the scene, dramatic cloud formations, deep indigo sky with electric violet lightning bolts, feeling of breakthrough power and transformation",
  },
  {
    id: "earthy_organic", label: "大地 / 有机", desc: "自然纹理、温暖色调",
    palette: ["#fef3c7", "#d97706", "#92400e", "#451a03"], mood: "踏实、温暖、有质感",
    imagePrompt: "Book cover with handmade paper texture, warm amber and brown tones, dried botanical pressed flowers, hand-lettered serif typography, golden hour light, natural linen texture background, artisan craft aesthetic",
    emotionPrompt: "Hands cupping warm soil with a seedling sprouting, golden sunlight filtering through oak leaves, warm terracotta and amber palette, feeling of rootedness and connection to earth, morning garden dew",
  },
  {
    id: "bold_modern", label: "大胆 / 现代", desc: "锐利排版、几何构成",
    palette: ["#fafafa", "#18181b", "#ef4444", "#fbbf24"], mood: "活力、果断、醒目",
    imagePrompt: "Bold book cover with stark black and white contrast, oversized helvetica bold typography, single red geometric accent shape, Swiss design grid layout, Bauhaus influence, high energy, magazine editorial style",
    emotionPrompt: "Abstract geometric explosion of red and yellow shapes on white background, sharp angular forms radiating outward, feeling of decisive action and clarity, kinetic energy frozen in motion",
  },
  {
    id: "premium_soft",
    label: "高级 / 几何",
    desc: "精致、精准、高端定位",
    palette: ["#fdf4ff", "#d8b4fe", "#7e22ce", "#3b0764"],
    mood: "升华、几何、永恒",
    imagePrompt:
      "Premium luxury nonfiction book cover with precise geometric layout, thin elegant serif or restrained sans typography, subtle gold line or foil accent, controlled lavender and deep purple planes, editorial grid discipline, aspirational transformation",
    emotionPrompt:
      "Architectural light on refined surfaces, crisp geometric shadows, sense of order and quiet authority, timeless high-end publishing mood",
  },
  {
    id: "sacred_cosmic",
    label: "神秘 / 深邃",
    desc: "氛围感、沉思性、微光流转",
    palette: ["#0f172a", "#7c3aed", "#f59e0b", "#fef3c7"], mood: "引人、开阔、仍具商业感",
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
  "终于平静": "/onboarding/proof/wizard/emotion_finally_calm.png",
  "在身体里感到安全": "/onboarding/proof/wizard/emotion_safe_in_body.png",
  "允许自己休息": "/onboarding/proof/wizard/emotion_permission_rest.png",
  "头脑清晰": "/onboarding/proof/wizard/emotion_clear_headed.png",
  "掌控感": "/onboarding/proof/wizard/emotion_in_control.png",
  "与目标相连": "/onboarding/proof/wizard/emotion_connected_purpose.png",
  "充满活力": "/onboarding/proof/wizard/emotion_energized.png",
  "自信": "/onboarding/proof/wizard/emotion_confident.png",
  "有韧性": "/onboarding/proof/wizard/emotion_resilient.png",
  "释放": "/onboarding/proof/wizard/emotion_released.png",
  "被宽恕": "/onboarding/proof/wizard/emotion_forgiven.png",
  "不再孤单": "/onboarding/proof/wizard/emotion_less_alone.png",
  "脚踏实地": "/onboarding/proof/wizard/emotion_grounded.png",
  "充满希望": "/onboarding/proof/wizard/emotion_hopeful.png",
  "活在当下": "/onboarding/proof/wizard/emotion_present.png",
};

const TOPIC_TAG_PROOF_URL = Object.fromEntries(
  [
    "anxiety-at-night",
    "过度思虑",
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
    keywords: ["nervous system regulation audiobook", "职业倦怠康复", "stop overthinking at night", "anxiety before sleep", "polyvagal calm"],
  },
  identity_direction: {
    personas: ["Gen Z navigating adulting 18-24 (fastest-growing segment)", "Millennial women career transition 30-44", "Identity rebuilders post-divorce 28-50"],
    topics: ["feeling behind compared to peers", "lost sense of purpose after 30", "quarter-life crisis", "rebuilding identity after breakup", "what to do with your life"],
    keywords: ["feeling lost in life audiobook", "四分之一人生危机", "finding purpose", "identity crisis self help", "what am I doing with my life"],
  },
  emotional_healing: {
    personas: ["Grief/loss navigators all ages ($70-100M/yr)", "Trauma-aware millennials body-based recovery", "Parents processing intergenerational patterns"],
    topics: ["grief that doesn't follow a timeline", "healing after toxic relationship", "代际创伤", "从心碎中复原", "情感麻木"],
    keywords: ["grief audiobook", "healing after breakup", "trauma recovery self help", "emotional healing", "letting go of past"],
  },
  performance_focus: {
    personas: ["Corporate middle managers 32-50 ($50-80M/yr)", "Entrepreneurs/solopreneurs 28-50 ($60-100M/yr)", "Tech workers seeking focus 25-40"],
    topics: ["phone addiction destroying focus", "can't stick to habits", "decision fatigue as a manager", "ADHD-friendly productivity", "多巴胺排毒"],
    keywords: ["focus audiobook", "productivity self help", "习惯养成", "ADHD focus techniques", "deep work practice"],
  },
  spiritual_awakening: {
    personas: ["Gen X wisdom seekers 45-58 ($165M/yr highest-spending)", "Contemplative professionals seeking meaning", "Post-crisis seekers finding new framework"],
    topics: ["meditation that actually works for beginners", "finding meaning after loss", "spiritual practice without religion", "inner peace in chaos", "mindfulness for skeptics"],
    keywords: ["meditation audiobook", "finding inner peace", "spiritual growth", "mindfulness for beginners", "meaning of life self help"],
  },
};

// V4 Angles
const V4_ANGLES = [
  { id: "debunk", label: "破除迷思", desc: "挑战主流观点——「你的咨询师不会告诉你的事」", framing: "反常识钩子，以证据支撑的转折", icon: AlertTriangle },
  { id: "framework", label: "框架体系", desc: "给他们一套方法——「5 步方案……」", framing: "结构化、可重复、工具优先", icon: Layers },
  { id: "reveal", label: "揭晓", desc: "揭示隐藏真相——「你睡不着的真正原因」", framing: "内部知识，「没人谈论这个」", icon: Eye },
  { id: "leverage", label: "杠杆借力", desc: "利用他们已有的——「你的焦虑是一种超能力」", framing: "将现有特质重构为优势", icon: Zap },
  { id: "origin", label: "溯源起点", desc: "追溯根源——「你的模式究竟从哪里开始」", framing: "叙事深度、因果链条、「顿悟时刻」", icon: Search },
];

// V4 Formats
const V4_FORMATS_STRUCTURAL = [
  { id: "F001", label: "标准自我成长", chapters: "12-16", tier: "full", desc: "经典叙事弧，练习穿插其中" },
  { id: "F002", label: "引导式课程", chapters: "8-12", tier: "full", desc: "循序渐进的转变方案" },
  { id: "F003", label: "每日日记", chapters: "30-90", tier: "micro", desc: "每天一页，以反思为主" },
  { id: "F004", label: "躯体化练习册", chapters: "10-14", tier: "full", desc: "以身体练习为主，叙述最少化" },
  { id: "F005", label: "叙事旅程", chapters: "14-20", tier: "full", desc: "故事驱动，深刻情感弧线" },
  { id: "F006", label: "精华智慧", chapters: "6-8", tier: "mini", desc: "内容密集，影响深远，篇幅简短" },
];

// ═══════════════════════════════════════════════════════════
// VOICE TONE DATA — 10 positions per slider with benefits
// ═══════════════════════════════════════════════════════════

const VOICE_TONE_10 = {
  gentleDirect: [
    {
      position: 1, label: "极度温柔",
      technique: "以「你可能会注意到……「开头——从不发号施令，只是陪伴读者一同观察",
      benefits: [
        "Creates immediate psychological safety — reader's nervous system downregulates on first page",
        "Disarms shame and self-criticism that blocks receptivity to new ideas",
        "Readers who've been told 'just try harder' finally feel seen instead of lectured",
        "Builds trust with trauma-aware audiences who distrust authority-tone content",
        "Reduces book abandonment — gentle entry keeps anxious readers turning pages",
      ],
    },
    {
      position: 2, label: "非常温柔",
      technique: "使用赋权语言：「这样做没问题「和「你有权利……「",
      benefits: [
        "Gives explicit permission to feel — many readers have never received this",
        "Counteracts internalized 'suck it up' messaging from family or culture",
        "Emotionally overwhelmed readers feel validated rather than pathologized",
        "Creates a sense of being parented well — meeting an unmet developmental need",
        "Reduces the shame spiral that prevents readers from doing the exercises",
      ],
    },
    {
      position: 3, label: "温柔",
      technique: "练习以邀请的方式呈现，而非指令——「如果你愿意，可以试试……「",
      benefits: [
        "Respects reader autonomy — they choose to engage rather than being told to",
        "People with control-related trauma can participate without triggering resistance",
        "练习完成率更高——邀请比命令让人感到更安全",
        "Builds intrinsic motivation rather than compliance-based engagement",
        "Reader feels like a collaborator, not a patient — preserves dignity",
      ],
    },
    {
      position: 4, label: "柔和",
      technique: "句子节奏舒缓，有意设置停顿，注重呼吸感",
      benefits: [
        "Reading pace mirrors meditation — the book itself becomes a calming practice",
        "Anxious readers' heart rate actually slows when prose rhythm is paced",
        "Creates space for emotional processing between concepts",
        "有声书版本可作为恐慌时刻的情绪降级工具",
        "Readers report feeling 'held' by the writing — attachment need met through text",
      ],
    },
    {
      position: 5, label: "平衡偏温柔",
      technique: "先给予认可，再提供方向——先承认感受，再提供出路",
      benefits: [
        "Mirrors ideal therapeutic rapport — feel understood, then open to change",
        "Both emotional and logical readers find their entry point",
        "Prevents the 'this book doesn't get me' abandonment that pure advice triggers",
        "Creates a rhythm readers can predict and trust across chapters",
        "Balanced enough for skeptics while warm enough for emotionally-driven readers",
      ],
    },
    {
      position: 6, label: "平衡偏直接",
      technique: "以温暖的语气陈述真相——「这才是真正发生的事「",
      benefits: [
        "Readers get the 'real talk' they crave without feeling attacked",
        "Builds authority — readers trust a voice that tells them the truth kindly",
        "Works for both self-help newcomers and experienced personal-development readers",
        "Strong TikTok clip potential — direct truth cuts through scroll noise",
        "Creates quotable moments readers screenshot and share",
      ],
    },
    {
      position: 7, label: "坚定",
      technique: "行动优先的句式——先说要做什么，再解释为什么",
      benefits: [
        "Overwhelmed readers need fewer decisions — clear direction reduces cognitive load",
        "Performance-oriented readers respond to efficiency and structure",
        "更高的行动转化率——读者真正去做练习，而不只是阅读",
        "Creates a sense of being coached by someone who knows what they're doing",
        "Stronger titles and hooks for ad copy — direct language converts better",
      ],
    },
    {
      position: 8, label: "直接",
      technique: "短句精炼有力，没有废话，每个字都有其意义",
      benefits: [
        "ADHD-friendly — attention captured and held through rhythm and brevity",
        "Male-skewing audience feels respected — no unnecessary emotional padding",
        "Social media clips hit harder — short sentences = viral text-on-screen content",
        "Builds momentum — readers feel they're making progress fast",
        "Cuts through the 'every self-help book sounds the same' fatigue",
      ],
    },
    {
      position: 9, label: "非常直接",
      technique: "直面式诚实——「你其实已经知道了。只是在回避而已。「",
      benefits: [
        "Breaks through denial — some readers need to be challenged, not comforted",
        "High-achiever audience respects the courage to say what others won't",
        "Creates 'I feel called out' moments that drive word-of-mouth sharing",
        "Differentiates from the soft-tone self-help market — stands out on shelves",
        "Builds fierce loyalty — readers who connect with this voice become evangelists",
      ],
    },
    {
      position: 10, label: "极度直接",
      technique: "使用祈使句和命令式——「停止阅读。现在去做。然后再回来。「",
      benefits: [
        "Maximum behavior change — no ambiguity about what the reader should do",
        "Creates drill-sergeant loyalty in readers who respond to structure",
        "有声书版本可作为实时教练辅导使用",
        "Content repurposes perfectly into course modules and challenge formats",
        "Readers complete entire programs — the commanding voice maintains momentum",
      ],
    },
  ],
  simpleDeep: [
    {
      position: 1, label: "极度简洁",
      technique: "小学程度的阅读难度——每句话清晰明了，零术语",
      benefits: [
        "Accessible to ESL readers — opens international markets dramatically",
        "Gen Alpha and young Gen Z can engage without barrier",
        "Readers in emotional crisis can absorb content when cognition is impaired",
        "Widest possible market reach — no educational prerequisite",
        "有声书理解度最高——听众无需倒带重听",
      ],
    },
    {
      position: 2, label: "非常简洁",
      technique: "一段只讲一个概念——以小而清晰的模块构建理解",
      benefits: [
        "ADHD readers can follow without losing the thread",
        "Each paragraph is a complete, usable unit — easy to highlight and save",
        "Works perfectly as TikTok carousel content — one slide per concept",
        "Readers feel smart and capable rather than intimidated",
        "练习完成率更高——操作说明不可能被误解",
      ],
    },
    {
      position: 3, label: "简洁",
      technique: "日常比喻——「就像清理浏览器标签页一样「",
      benefits: [
        "Abstract concepts land instantly through familiar reference points",
        "Readers explain ideas to friends using your metaphors — organic word-of-mouth",
        "Creates 'aha moments' without requiring background knowledge",
        "Content is meme-able and shareable on social platforms",
        "Bridge between clinical concepts and lived experience",
      ],
    },
    {
      position: 4, label: "易于理解",
      technique: "清晰讲解，偶尔深入——每章引入一个新术语",
      benefits: [
        "Readers feel they're learning without being overwhelmed",
        "Builds vocabulary gradually — reader grows with the book",
        "Strikes the sweet spot for mainstream self-help audience",
        "Good for podcast interviews — author can explain simply but show depth",
        "Creates authority without alienation — reader trusts the writer's knowledge",
      ],
    },
    {
      position: 5, label: "平衡",
      technique: "日常语言与丰富概念相结合——用「简单来说「作为过渡桥梁",
      benefits: [
        "Serves the widest range of educational backgrounds",
        "Book clubs can discuss at multiple levels — everyone finds something",
        "过渡段落在有声书中效果出色——播讲者可以传递深度转变的信号",
        "Strong review potential — readers feel both comforted and challenged",
        "Longest shelf life — doesn't feel too basic or too academic after rereading",
      ],
    },
    {
      position: 6, label: "深思熟虑",
      technique: "多句展开一个观点——在得出洞见之前先构建论证",
      benefits: [
        "Intellectually curious readers feel respected and engaged",
        "Creates page-turner quality — readers want to see where the idea goes",
        "Strong for series — later volumes can deepen without losing the audience",
        "Generates rich discussion material for therapy and group contexts",
        "Differentiates from shallow pop-psychology — earns premium pricing",
      ],
    },
    {
      position: 7, label: "丰富",
      technique: "多层含义——表面阅读即可理解，但再读会发现更多",
      benefits: [
        "Books become reference texts readers return to — longer customer lifetime value",
        "Creates intellectual community — fans discuss hidden layers online",
        "音频版本值得反复收听——推动重复参与",
        "Attracts therapist and counselor audiences who recommend books to clients",
        "Content supports mastercourse format — enough depth for multi-week study",
      ],
    },
    {
      position: 8, label: "深邃",
      technique: "哲学与科学交织——引用研究成果，不说教",
      benefits: [
        "Positions author as genuine authority, not just a motivational speaker",
        "Attracts Gen X wisdom-seeker market — highest-spending demographic",
        "Strong for keynote and TEDx content — ideas are substantive enough for stage",
        "Creates books that therapists assign — institutional recommendation pipeline",
        "Long-tail SEO potential — niche depth owns specific search territories",
      ],
    },
    {
      position: 9, label: "非常深邃",
      technique: "跨学科综合——连接神经科学、哲学与实践",
      benefits: [
        "Creates 'the book that changed my life' reactions — viral review potential",
        "Thought-leader positioning — author becomes known for original frameworks",
        "Academic and clinical citation potential — extends reach beyond consumer market",
        "有声书高端定价具有说服力——内容足够厚实，支撑长篇音频",
        "International translation appeal — depth translates better than colloquialisms",
      ],
    },
    {
      position: 10, label: "极度深邃",
      technique: "研究生级别的概念与原创框架——挑战读者成长",
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
      position: 1, label: "极度情感化",
      technique: "以故事开篇——每个概念都通过亲历叙事引入",
      benefits: [
        "Mirror neurons activate — reader physically feels what characters feel",
        "Emotional memory encoding — readers remember content 6x longer than facts alone",
        "Creates the 'I cried reading this' reviews that drive viral sharing",
        "Deeply cathartic for readers carrying unprocessed emotion",
        "有声书版本成为陪伴——听众与播讲者建立起类社交的情感联结",
      ],
    },
    {
      position: 2, label: "非常情感化",
      technique: "文字中高度袒露脆弱——作者自身的创伤清晰可见",
      benefits: [
        "Readers feel less alone — 'someone else has been through this' is profoundly healing",
        "Dismantles the 'expert on a pedestal' barrier that blocks real connection",
        "Creates intense word-of-mouth — readers personally recommend to friends in crisis",
        "Strong podcast interview content — vulnerable stories captivate audiences",
        "Builds fierce community — readers bond with each other through shared emotional resonance",
      ],
    },
    {
      position: 3, label: "情感化",
      technique: "练习包含日记和身体感知工作——「留意内心升起的感受「",
      benefits: [
        "Develops reader's emotional intelligence — a lifelong skill beyond the book",
        "Somatic awareness exercises create real physiological change, not just insight",
        "Especially transformative for men and high-performers who've been cut off from feeling",
        "Creates a practice the reader continues after the book — ongoing engagement",
        "Strong workbook companion potential — emotional exercises adapt to journal format",
      ],
    },
    {
      position: 4, label: "温暖",
      technique: "以亲密语气直称读者「你「——如同亲密朋友写来的信",
      benefits: [
        "Attachment theory activation — reader feels securely 'held' by the text",
        "Reduces defensiveness — intimate tone bypasses intellectual resistance",
        "Highest read-through rates — readers don't want the 'conversation' to end",
        "有声书感觉像一次私人治疗——建立深度的个人联结",
        "Strong for grief and healing topics where clinical distance would feel cold",
      ],
    },
    {
      position: 5, label: "平衡",
      technique: "情感开篇，逻辑展开，整合收尾——每章都是一段旅程",
      benefits: [
        "Both heart and head readers feel served in every chapter",
        "Creates the most balanced reviews — 'moving AND practical' is the gold standard",
        "Works across all platforms — emotional hooks for social, logical depth for books",
        "Couples and friends with different styles can both love the same book",
        "跨人群吸引力最强——没有任何一类读者被排除在外",
      ],
    },
    {
      position: 6, label: "有理有据",
      technique: "以故事佐证数据，而非以数据说明故事",
      benefits: [
        "Skeptical readers stay engaged — their 'prove it' need is met consistently",
        "Creates authority through substance — reviews mention 'well-researched'",
        "Strong for B2B and corporate wellness markets where emotions need framing",
        "Content repurposes into presentations and white papers — business applications",
        "Attracts healthcare and therapy professionals as audience and referrers",
      ],
    },
    {
      position: 7, label: "分析性",
      technique: "结构化论述——论点、证据、启示、行动",
      benefits: [
        "Engineering and tech-industry readers finally find self-help they respect",
        "Creates clear, quotable frameworks that get shared in professional contexts",
        "Strong LinkedIn and professional social media clip potential",
        "Supports course and certification format — logical progression is built in",
        "感知价值更高——读者觉得自己获得的是工具，而不仅仅是安慰",
      ],
    },
    {
      position: 8, label: "逻辑化",
      technique: "以数据为主的章节——数字、研究和指标支撑每一个论断",
      benefits: [
        "Positions brand in the 'evidence-based' category — premium market positioning",
        "Readers use the data to convince friends and family — built-in evangelism tool",
        "Strong for corporate book-club adoption — 'this isn't woo-woo' positioning",
        "Creates excerpt content for health and science publications",
        "Male-skewing audience finally engages with emotional topics through logic door",
      ],
    },
    {
      position: 9, label: "非常逻辑化",
      technique: "将读者视为有能力做决策的人——以对待智识成年人的方式对待",
      benefits: [
        "Respects reader's intelligence — builds loyalty through trust in their capacity",
        "Creates 'I recommend this to my smartest friends' word-of-mouth",
        "Strong for executive and leadership markets where emotional language feels weak",
        "内容适合转化为主题演讲——逻辑结构在台上表现出色",
        "Academic review potential — substantive enough to be cited in research",
      ],
    },
    {
      position: 10, label: "极度逻辑化",
      technique: "将转变框架为系统性技能习得，成果可量化",
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
      position: 1, label: "极度灵性",
      technique: "全文贯穿传统脉络、传承谱系与神圣教师的引用",
      benefits: [
        "Readers seeking meaning find it — existential anxiety addressed at the root",
        "Creates a sense of belonging to something ancient and larger than oneself",
        "Attracts the highest-spending demographic — Gen X wisdom seekers ($165M/yr)",
        "Book becomes a spiritual companion — readers keep it on nightstands for years",
        "Strong retreat and workshop tie-in — spiritual content creates immersive events",
      ],
    },
    {
      position: 2, label: "非常灵性",
      technique: "神圣语言：「临在「、「觉知「、「见证「、「伟大转化「",
      benefits: [
        "Creates transcendent reading experiences — readers report feeling 'transported'",
        "Poetry of language itself becomes healing — beauty as medicine",
        "有声书版本可作为引导冥想使用——一内容，两用途",
        "Strong international appeal — spiritual language translates across cultures",
        "Builds devoted following — spiritual readers are the most loyal audience segment",
      ],
    },
    {
      position: 3, label: "灵性",
      technique: "练习涵盖冥想、沉思与以静默为基础的修炼",
      benefits: [
        "Develops reader's capacity for stillness — counterbalances digital overstimulation",
        "Meditation-based exercises create measurable neurological benefits",
        "Creates daily practice that extends engagement far beyond reading the book",
        "Strong for Gen Alpha — meditation skills are increasingly taught in schools",
        "Retreat-center and yoga-studio recommendation pipeline — institutional distribution",
      ],
    },
    {
      position: 4, label: "意义优先",
      technique: "意义建构是首要目标——「我为何在此「被直接回应",
      benefits: [
        "Addresses the deepest human need — purpose and significance",
        "Readers in midlife transition find the existential grounding they're seeking",
        "Creates content that feels timeless rather than trend-dependent",
        "Strong for grief and loss topics — meaning-making is the ultimate healing",
        "Builds author platform as wisdom figure, not just expert — longer career arc",
      ],
    },
    {
      position: 5, label: "平衡",
      technique: "内在转化与外在行动相连——沉思落于执行",
      benefits: [
        "Serves both spiritual seekers and practical doers in one book",
        "Creates the 'woo-meets-science' positioning that dominates bestseller lists",
        "Both meditation-loving and productivity-loving readers find their entry point",
        "口碑传播潜力最强——跨越不同社交圈层被推荐",
        "Platform flexibility — works for podcasts, courses, retreats, AND workshops",
      ],
    },
    {
      position: 6, label: "脚踏实地",
      technique: "灵性洞见转化为日常习惯与日常规律",
      benefits: [
        "Wisdom becomes usable — reader can start today, not 'when they're ready'",
        "Appeals to 'spiritual but practical' — the fastest-growing reader segment",
        "Creates content that works as 7-day challenges and 30-day programs",
        "Strong for social media — habit content performs exceptionally on all platforms",
        "Bridges the gap between self-help and spirituality sections in bookstores",
      ],
    },
    {
      position: 7, label: "应用导向",
      technique: "以工具开篇——介绍技法，说明使用时机，解释为何有效",
      benefits: [
        "Readers take immediate action — exercises feel doable, not abstract",
        "Strong for pocket-guide format — tools are reference-able and compact",
        "Creates the 'I actually did the exercises' reviews that drive sales",
        "Corporate wellness programs adopt tool-based content more readily",
        "练习完成率更高——实用框架降低抗拒感",
      ],
    },
    {
      position: 8, label: "实用",
      technique: "功能性语言：「系统「、「协议「、「技法「——完全不涉及传统",
      benefits: [
        "Opens the secular wellness market — readers who avoid 'spiritual' labels",
        "Strong for healthcare referrals — clinical professionals recommend secular content",
        "Creates content that works in corporate and educational institutional settings",
        "Appeals to science-minded readers who want results without metaphysics",
        "TikTok and YouTube performance highest — practical content has broadest appeal",
      ],
    },
    {
      position: 9, label: "非常实用",
      technique: "行为改变是首要目标——追踪可量化的成果",
      benefits: [
        "Readers can prove the book worked — drives reviews with specific results",
        "Creates before/after narratives perfect for marketing and testimonials",
        "Strong for employer-sponsored wellness — ROI can be demonstrated",
        "App and digital product integration natural — tracking is built into the approach",
        "Health insurance and benefits platform partnerships become possible",
      ],
    },
    {
      position: 10, label: "极度实用",
      technique: "纯协议式结构——每章都是可落地的系统，成果可量化",
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
  const isComplete = step === total - 2; // step 7 ("蓝图") only
  const pct = isComplete ? 100 : ((step + 1) / total) * 100;
  return (
    <div className="brand-studio-panel mb-6 px-5 py-4 sm:mb-8">
      {isComplete && (
        <p className="text-center text-3xl font-extrabold mb-3" style={{ color: '#d97706', fontFamily: 'Cormorant Garamond, serif' }}>
          {t("ui", "恭喜——您的品牌已 100% 配置完成！")}
        </p>
      )}
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-wider text-violet-600">
            {isComplete ? t("ui", "完成") : t("ui", "第 {n} 步 / 共 {total} 步").replace("{n}", step + 1).replace("{total}", total)}
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
  const labels = ["感受", "思考", "Do", "分享", "信任", "回归"];
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
      systemEffect: "为所有书目设置注重呼吸感的节奏、躯体练习，以及以调节为优先的结构",
      emotionalBenefit: "读者的神经系统从第一段就开始平静下来。内容发挥着共同调节的作用——降低皮质醇，减缓心率，允许休息。读者反映，文字本身让他们感到『被托住了』。",
    },
    identity_direction: {
      systemEffect: "启用推进式散文、诚实自审练习，以及反比较钩子策略",
      emotionalBenefit: "读者停止刷屏，开始做选择。这将『我不知道自己在做什么』的瘫痪状态转化为动力。每一章都通过一个个小而勇敢的决定重建身份认同——对抗那种感觉自己落后于人的羞耻感。",
    },
    emotional_healing: {
      systemEffect: "启用以温柔为先的语言、以见证为基础的练习，以及具有悲伤素养的内容节奏",
      emotionalBenefit: "读者感到被看见，而非被修复。这以陪伴回应悲痛与痛苦——没有毒性积极，没有时间表，没有『你应该已经走出来了』。它扮演了许多读者从未曾拥有过的慈悲见证者的角色。",
    },
    performance_focus: {
      systemEffect: "启用行动优先的散文、基于协议的练习，以及削减噪音的钩子策略",
      emotionalBenefit: "读者穿透信息过载，数周来第一次采取真实行动。这减轻了决策疲劳，建立依靠结构而非意志力运行的系统，并恢复了掌控感。",
    },
    spiritual_awakening: {
      systemEffect: "启用沉思性散文层次、觉察落差的练习，以及寻找意义的钩子策略",
      emotionalBenefit: "读者发现，他们一直在追寻的，其实从未离开过自己。这在一个流于表面的世界里创造了深度的空间——在那些智识化的自我提升无法抵达的地方，与灵性探求者相遇。",
    },
  },
  personas: {
    burned_out_pro: { systemEffect: "围绕疲竭钩子、『周日恐惧』叙事，以及不放弃的康复框架来调整标题", emotionalBenefit: "内容触达正处于生存模式的人——没有愧疚感，没有『再努力一点』。你的品牌成为第一个真诚说出『你不是懒，你是耗尽了』的声音。" },
    gen_z_seeker: { systemEffect: "优化短内容钩子、TikTok 原生语言、反内卷语气，以及让人停止滑动的开场", emotionalBenefit: "你的品牌以 Z 世代的母语与他们相遇——真实性优先。在一片表演式健康内容的海洋中，你成为值得信赖的声音，提供真正有用的工具，没有尴尬。" },
    gen_alpha: { systemEffect: "启用漫画优先格式、视觉叙事、游戏化练习，以及对监护人友好的内容过滤", emotionalBenefit: "你正在为从童年起就拥有情感词汇的第一代人创作内容。视觉格式给了他们父母那一代从未有过的工具——适龄且真正有用。" },
    grief_carrier: { systemEffect: "设置赋权语言、柔和的行动引导、拒绝毒性积极，以及以见证为基础的练习结构", emotionalBenefit: "你的品牌成为陪伴读者走过那些无以名状之悲的同行者——那种没有人教过他们如何面对的悲痛。不修复，不设时间表，只是陪伴，以及那份深刻的允许：你可以不好。" },
    anxious_achiever: { systemEffect: "在高绩效框架与脆弱的后门之间架桥，加入神经系统支持与冒名顶替综合症钩子", emotionalBenefit: "你触达那些外表看起来还好、内心却正在崩塌的人。你的品牌在成就语言与脆弱之间架桥——这是高成就者真正愿意走进去的那扇疗愈后门。" },
    spiritual_returner: { systemEffect: "启用厚重的沉思性散文、传统敏感的引用、反导师定位，以及深度优先的钩子", emotionalBenefit: "你的品牌与那些什么都试过、被肤浅答案耗尽的人对话。厚重而真实的内容，尊重他们的智识，匹配他们的深度。" },
    new_parent: { systemEffect: "优先采用微格式呈现、无负担框架、快速工具练习，以及适合孩子午睡时长的内容", emotionalBenefit: "你的品牌在父母偷来的片刻触达他们——凌晨三点喂奶时，孩子午睡时刷手机时。无负担的微格式工具帮助他们找回自我，而不是增加他们的压力。" },
  },
  moments: {
    "2am_overthinking": { systemEffect: "以感受性语言开场，认可那种螺旋下坠的感觉，并在前30秒内提供即时的落地工具", emotionalBenefit: "内容在他们最脆弱的那一刻捕捉到了他们——躺着睡不着，手机屏幕亮着，思绪飞转。这个钩子之所以有效，是因为它描述的正是他们此刻身体里的感受。" },
    "after_breakup": { systemEffect: "精确命名那种麻木的特定质感，避免给出建议，以身体对失去的觉察作为引导", emotionalBenefit: "你在没有人谈论的那种麻木里与他们相遇——不是那种哭泣的麻木，而是食物失去味道的那种。你的品牌说出了他们无法表达的，而仅仅是被说出，就已经开始了疗愈。" },
    "burnout_cant_quit": { systemEffect: "捕捉戴回面具的那一刻，触及公开与私下之间的落差，将康复定义为一种技能而非奢侈", emotionalBenefit: "你触及的是他们对着洗手间镜子、又要把面具戴回去之间的那一刻。内容认可了『表演中的他们』与『真实的他们』之间的落差——允许他们停止伪装。" },
    "feeling_behind": { systemEffect: "针对比较式刷屏行为，将『落后』重新定义为『建构中』，将手机转化为触发物", emotionalBenefit: "你用真相打断比较式刷屏：他们并非落后，他们正在建构。手机本身成为一个触发物，将无意识的刷屏转化为诚实的自我反思。" },
    "panic_spike": { systemEffect: "身体优先的语言，先命名身体感受再命名情绪，立即进行躯体干预 within 10 seconds", emotionalBenefit: "当思维已经离场，内容使用以身体为先的语言。在恐慌中，身体需要先听到『我看见你』，大脑才能开始处理任何事情。这在真实的时刻帮助真实的人。" },
    "sunday_dread": { systemEffect: "触及每周焦虑的循环，认可那种沉重的感受，将周日重新定义为自我找回，而非倒计时", emotionalBenefit: "你说出了数百万人感受却从未言说的每周恐惧。你的品牌从焦虑手中夺回周日——将那种沉重的感觉转化为准备与自我关爱的仪式。" },
  },
  visualStyles: {
    calm_minimal: { systemEffect: "生成封面风格：大量留白、柔和水墨、禅意美学、低饱和色调", emotionalBenefit: "读者在视觉上感到释然——留白传递出『你可以在这里喘口气』的信号。封面在书还没打开之前就像一次冥想。为感官过载的读者减轻视觉焦虑。" },
    dark_intense: { systemEffect: "生成封面风格：深靛蓝/黑色、戏剧性光效、电影颗粒感、高对比度", emotionalBenefit: "读者感受到自身转变的份量。黑暗美学传递出深度的信号——这不是温和的健康内容，这是真正的工作。吸引那些不信任『软化包装』自我提升的读者。" },
    earthy_organic: { systemEffect: "生成封面风格：手工质感、植物元素、温暖琥珀色调、工匠美学", emotionalBenefit: "读者在读到任何一个字之前就感到踏实。自然质感触发亲生物性平静——大脑将有机视觉解读为『安全』。对于躯体疗愈和自然疗愈尤为有力。" },
    bold_modern: { systemEffect: "生成封面风格：强烈对比、超大字体、红色几何装饰、瑞士设计网格", emotionalBenefit: "读者感到充满活力、果断有力。大胆的视觉穿透书架噪音与滑动疲劳，传递出『这个不一样』的信号——吸引那些厌倦了粉彩系健康内容、渴望行动的读者。" },
    premium_soft: { systemEffect: "生成封面风格：几何结构、精确的排版层次、金色装饰线、克制的奢华色调", emotionalBenefit: "读者感到手中握着的是某种权威而用心之物。几何高端风格传递出精工与清晰的信号——吸引那些希望兼具编辑公信力的转变体验的读者。" },
    sacred_cosmic: { systemEffect: "生成神秘氛围感封面——深蓝与紫色，微妙光线，沉思深度，无恐怖感", emotionalBenefit: "读者感到好奇与内在的扩展。神秘的视觉邀请深度探索者进入，不会造成奇幻过载——在书架和缩略图上都具有磁力。" },
  },
  formats: {
    manga: { systemEffect: "书单规划器优先排列图文分镜、短篇有声书（15至30分钟）、跨所有渠道的视觉叙事", emotionalBenefit: "视觉型读者通过图像处理情绪比文字更快。漫画能降低阅读焦虑，以 Z 世代和 Alpha 世代的母语形式触达他们，并通过故事让复杂的心理概念变得易于理解。" },
    book: { systemEffect: "书单规划器优先排列全长叙事、深度课程、综合练习册、长篇有声书（3至8小时）", emotionalBenefit: "深度读者渴望沉浸——长篇内容允许他们放慢脚步、深入其中。全长书籍成为陪伴，培养持续的专注力，推动持久的转变。" },
  },
};

function SelectionFeedback({ systemEffect, emotionalBenefit, color = "#6366f1" }) {
  if (!systemEffect && !emotionalBenefit) return null;
  return (
    <div className="mt-4 rounded-xl border overflow-hidden" style={{ borderColor: color + '30' }}>
      <div className="px-4 py-2.5 flex items-center gap-2" style={{ backgroundColor: color + '08' }}>
        <Sparkles size={13} style={{ color }} />
        <span className="text-[11px] font-bold" style={{ color }}>这将激活的内容</span>
      </div>
      <div className="px-4 py-3 bg-white">
        <div className="flex items-start gap-2 mb-2.5">
          <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: color + '15' }}>
            <Zap size={10} style={{ color }} />
          </div>
          <div>
            <div className="text-[9px] font-bold uppercase text-white mb-0.5">在系统中</div>
            <p className="text-[11px] text-white leading-relaxed">{systemEffect}</p>
          </div>
        </div>
        <div className="flex items-start gap-2">
          <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: color + '15' }}>
            <Heart size={10} style={{ color }} />
          </div>
          <div>
            <div className="text-[9px] font-bold uppercase text-white mb-0.5">对你的读者</div>
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
        <span className="text-xs font-bold text-white">{label || "这会改变什么"}</span>
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
        <p className="text-[10px] text-white font-semibold uppercase">{_t("ui", "品牌已定义")}</p>
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
            <span className="text-xs font-bold text-white">这将激活的内容</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>系统效果：</strong> {_SF.archetypes[arch.id].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>读者感受：</strong> {_SF.archetypes[arch.id].emotionalBenefit}</div>
        </div>
      )}
      {step === 1 && persona && _SF.personas[persona.id] && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-violet-500" />
            <span className="text-xs font-bold text-white">这将激活的内容</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>系统效果：</strong> {_SF.personas[persona.id].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>读者感受：</strong> {_SF.personas[persona.id].emotionalBenefit}</div>
        </div>
      )}
      {step === 1 && persona && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-1">读者</div>
          <div className="flex items-center gap-2"><span className="text-lg">{persona.emoji}</span><div><div className="text-xs font-bold text-white">{persona.label}</div></div></div>
        </div>
      )}
      {step === 1 && persona && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-2">读者画像</div>
          <div className="text-[10px] text-white leading-tight mb-1.5">{persona.desc}</div>
          <div className="text-[10px] text-white leading-tight mb-1.5"><strong>需求：</strong> {persona.needs}</div>
          <div className="text-[10px] text-white leading-tight"><strong>影响：</strong> {persona.impact}</div>
        </div>
      )}
      {step === 2 && moment && _SF.moments[moment.id] && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-violet-500" />
            <span className="text-xs font-bold text-white">这将激活的内容</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>系统效果：</strong> {_SF.moments[moment.id].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>读者感受：</strong> {_SF.moments[moment.id].emotionalBenefit}</div>
        </div>
      )}
      {step >= 3 && Object.keys(state.voiceSettings || {}).length > 0 && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-2">声音画像</div>
          {VOICE_SLIDERS.map((s) => { const val = state.voiceSettings?.[s.id] ?? s.default; return (
            <div key={s.id} className="flex items-center gap-2 mb-1"><span className="text-[9px] text-white w-14">{s.left}</span><div className="flex-1 h-1.5 bg-gray-100 rounded-full"><div className="h-full bg-gray-700 rounded-full transition-all" style={{ width: `${val}%` }} /></div><span className="text-[9px] text-white w-14 text-right">{s.right}</span></div>
          ); })}
        </div>
      )}
      {step === 4 && visual && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-2">影响</div>
          <div className="flex gap-1.5 mb-1.5">{visual.palette.map((c, i) => <div key={i} className="w-8 h-8 rounded-lg shadow-sm" style={{ backgroundColor: c }} />)}</div>
          <div className="text-[10px] text-white font-medium">{visual.label}</div>
        </div>
      )}
      {step === 4 && state.visualStyle && _SF.visualStyles[state.visualStyle] && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-violet-500" />
            <span className="text-xs font-bold text-white">这将激活的内容</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>系统效果：</strong> {_SF.visualStyles[state.visualStyle].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>读者感受：</strong> {_SF.visualStyles[state.visualStyle].emotionalBenefit}</div>
        </div>
      )}
      {step === 6 && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-3">
            <Compass size={14} className="text-indigo-500" />
            <span className="text-xs font-bold text-white">内容角度</span>
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
                        <span className="text-[9px] font-bold" style={{ color: cat.color }}>{angleInfo?.label}: {(cat.tags.find(t => t.id === selectedTagId)?.label) || selectedTagId.replace(/-/g, " ")}</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <div className="w-1 h-1 rounded-full mt-1.5 flex-shrink-0" style={{ backgroundColor: cat.color }} />
                        <p className="text-[9px] text-white leading-relaxed">{selectedTag.bullet}</p>
                      </div>
                    </>
                  ) : (
                    <p className="text-[9px] text-white/70 italic">选择话题…</p>
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
            <span className="text-xs font-bold text-white">跳转到章节</span>
          </div>
          <div className="space-y-0.5">
            {[
              { id: "rev-category", label: "真实类别", icon: "🎯" },
              { id: "rev-voice", label: "声音特征", icon: "🎙️" },
              { id: "rev-positioning", label: "定位图", icon: "📍" },
              { id: "rev-visual", label: "视觉身份", icon: "🎨" },
              { id: "rev-emotion", label: "情感阶梯", icon: "📈" },
              { id: "rev-topics", label: "话题策略", icon: "🗂️" },
              { id: "rev-engine", label: "内容引擎", icon: "⚙️" },
              { id: "rev-loop", label: "优势循环", icon: "🔄" },
              { id: "rev-journey", label: "读者旅程", icon: "🚶" },
              { id: "rev-synergy", label: "声音 × 话题", icon: "🔗" },
              { id: "rev-radar", label: "品牌实力", icon: "📊" },
              { id: "rev-synthesis", label: "综合", icon: "✨" },
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
            <span className="text-xs font-bold text-white">情感画像</span>
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
        eyebrow="基础"
        title="选择您的情感世界"
        subtitle="您的原型是读者将您与某种感受联系起来的方式——贯穿文章、封面、视频和社交内容。选择最符合您希望呈现方式的世界观。"
        helper="每张卡片都包含一段简短的愿景，描述您的品牌邀请读者进入的世界。"
      />
      <div className="mb-6 rounded-xl border border-indigo-100/80 bg-indigo-50/60 px-4 py-3 backdrop-blur-sm">
        <p className="text-xs font-medium text-indigo-900">{useTranslation().t("steps", "这是品牌工作室中影响力最大的选择——其他一切都建立在您在此选择的情感领域之上。")}</p>
      </div>
      <div className="grid grid-cols-1 gap-3">
        {_A.map((arch) => <ArchetypeCard key={arch.id} arch={arch} selected={state.archetype} onClick={(id) => update({ archetype: id })} />)}
      </div>
    </div>
  );
}

function Step2PrimaryReader({ state, update, i18n = {} }) {
  const { tPersonas: _P = PERSONAS } = i18n;
  // Market/lane step removed 2026-06-03 — locale routing happens server-side.

  return (
    <div>
      <StepHero
        eyebrow="受众"
        title="主要读者"
        subtitle="每个强大的品牌都有一位主角——您首要服务的读者。您的目录仍然能触达每个群体；这个选择首先塑造语调、封面和钩子。"
      />
      <div className="mb-6 rounded-xl border border-blue-100/80 bg-blue-50/50 p-4 backdrop-blur-sm">
        <p className="text-xs leading-relaxed text-blue-900">
          {useTranslation().t("steps", "仍然触达所有人。 我们首先根据这位读者调整标题、包装和练习，然后再适配您原型的其他细分群体。")}
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
        eyebrow="钩子"
        title="他们向您伸出手的那一刻"
        subtitle="选择您的读者最敞开心扉的场景——标题、封面和社交钩子都由此而来。"
      />
      <details open className="mb-5 rounded-xl border border-amber-100/90 bg-amber-50/40 px-4 py-2 text-xs text-amber-900 backdrop-blur-sm open:pb-3">
        <summary className="cursor-pointer font-semibold text-amber-900/90 outline-none">为什么这很重要</summary>
        <p className="mt-2 leading-relaxed text-amber-900/85">
          {useTranslation().t("steps", "强大的品牌讲述一个时刻，而不仅仅是一个人群。这个选择引导第一句话、封面承诺，以及让人停止刷屏的钩子。")}
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
  const audioSrc = VOICE_AUDIO_SRC_ZH;
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
        eyebrow="声音"
        title="塑造您的品牌基调"
        subtitle="四个滑块——滑动并观察图表变化。每个维度都会改变每一句话的感受。"
      />
      <p className="mb-5 text-[11px] text-white">下一步将展示每个维度对读者的具体影响。</p>

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
                <span className="text-[10px] text-white">位置 {position} / 10</span>
              </div>

              {audioSrc[s.id] && (
                <div className="mt-2 flex items-center gap-2">
                  <button onClick={() => playAudio(s.id, position)} className="text-[10px] text-violet-600 hover:text-violet-800 flex items-center gap-1">
                    <Play size={10} /> 收听位置 {position}
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
        eyebrow="影响力"
        title="您的基调为读者带来什么"
        subtitle="滑动后，若想完整了解，请展开下方的影响说明。"
      />

      <div className="mb-6 rounded-2xl border border-violet-100 bg-violet-50/50 px-4 py-3">
        <p className="text-[10px] font-bold uppercase tracking-wider text-violet-800">旁白预览</p>
        <p className="mt-1 text-[11px] leading-relaxed text-white">
          同一段抚慰文字，三种 Edge TTS 流水线演示音色。聆听后，配合上方滑块调整至最适合的声音。
        </p>
        <div className="mt-3 space-y-2">
          <div>
            <span className="text-[10px] font-semibold text-white">调节／平静</span>
            <audio className="mt-1 block h-9 w-full" controls preload="metadata" src="/onboarding/audio/voice_cmp_comfort_voice_regulating_female.mp3" />
          </div>
          <div>
            <span className="text-[10px] font-semibold text-white">温暖共情</span>
            <audio className="mt-1 block h-9 w-full" controls preload="metadata" src="/onboarding/audio/voice_cmp_comfort_voice_warm_male.mp3" />
          </div>
          <div>
            <span className="text-[10px] font-semibold text-white">直接／权威</span>
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
                  <summary className="cursor-pointer text-xs font-bold text-white outline-none">这对读者的影响</summary>
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
        eyebrow="视觉与感受"
        title="视觉世界"
        subtitle="选择读者将与您的品牌联系在一起的视觉身份——封面、社交和视频都由此而来。"
      />

      <div className="text-xs font-bold uppercase tracking-wider text-violet-600/90 mb-3">视觉风格</div>
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
  { name: "安全感与平静", icon: "🛡️", color: "#6366f1", items: ["终于平静", "在身体里感到安全", "允许自己休息"], impacts: { "终于平静": "读者的神经系统进入下调状态——他们停止戒备，开始接纳", "在身体里感到安全": "从第一页起建立躯体信任，减少阅读过程中的应激反应", "允许自己休息": "瓦解让精疲力竭的读者无法接触自我成长内容的罪恶感循环" } },
  { name: "清晰与方向", icon: "🧭", color: "#059669", items: ["头脑清晰", "掌控感", "与目标相连"], impacts: { "头脑清晰": "突破决策疲劳——读者感到迷雾散去，开始做出选择", "掌控感": "为那些感到人生在对自己「发生」而非「流经」自己的读者，重建掌控感", "与目标相连": "架起「我该怎么做」与「这为何重要」之间的桥梁——读者找到前进的动力" } },
  { name: "活力与自信", icon: "⚡", color: "#f59e0b", items: ["充满活力", "自信", "有韧性"], impacts: { "充满活力": "将被动读者转变为行动者——他们合上书，然后出发", "自信": "重建被冒充者综合征和比较文化侵蚀的自我信任", "有韧性": "读者培养出反弹能力——挫折成为数据，而非身份" } },
  { name: "释放与疗愈", icon: "🕊️", color: "#f43f5e", items: ["释放", "被宽恕", "不再孤单"], impacts: { "释放": "悲伤、怨恨和积压的紧绷终于有了出口——读者真正地呼出一口气", "被宽恕": "自我关怀取代内在批评者——读者不再因为做了一个普通人而惩罚自己", "不再孤单": "为无名之痛命名——读者发现他们「奇怪」的痛苦其实是普遍的，孤立感由此瓦解" } },
  { name: "当下感与希望", icon: "✨", color: "#7c3aed", items: ["脚踏实地", "充满希望", "活在当下"], impacts: { "脚踏实地": "将读者锚定在身体和当下——反刍与对未来的焦虑失去了抓手", "充满希望": "重新点燃「改变是可能的」这一信念——这是自我成长领域最强大的转化驱动力", "活在当下": "读者停止活在悔恨或焦虑中，真实感受到「此刻在场」是什么滋味" } },
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
        eyebrow="承诺"
        title="视觉"
        subtitle="这些是读者离开时所携带的感受——他们能够说出口的转变。每一个标题、每一个行动引导、每一条营销信息，都指向这些承诺。"
      />
      <div className="mb-6 rounded-xl border border-rose-100/80 bg-rose-50/50 p-4 backdrop-blur-sm">
        <p className="text-xs leading-relaxed text-rose-900">
          <strong>每个类别选一个。</strong> 您的选择成为整个品牌情感上的北极星。封面以视觉方式承诺这些感受，标题将其命名，练习将其兑现。系统将您的选择编织进它生成的每一件内容之中。
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
  { label: "睡眠与焦虑", icon: "😰", color: "#6366f1", tags: [
    { id: "anxiety-at-night", label: "夜间焦虑", angle: "framework", bullet: "提供睡前焦虑方案——3 个身体扫描练习，在皮质醇循环失控前将其打断" },
    { id: "过度思虑", label: "过度思虑", angle: "origin", bullet: "将过度思虑的模式追溯到童年的生存策略——你的大脑学会了扫描危险，然后再也没有停下来" },
    { id: "panic-grounding", label: "恐慌接地", angle: "debunk", bullet: "破除「深呼吸就好了」的迷思——恐慌需要先进行躯体干预，认知工具在后" },
    { id: "sunday-dread", label: "周日恐惧", angle: "leverage", bullet: "将周日焦虑重构为神经系统的每周预报——这种焦虑本身包含着需要改变之事的信息" },
  ]},
  { label: "职业倦怠与工作", icon: "🔥", color: "#f59e0b", tags: [
    { id: "burnout-recovery", label: "职业倦怠恢复", angle: "debunk", bullet: "破除「去度个假就好了」的迷思——职业倦怠是神经系统的状态，不是日程安排的问题" },
    { id: "nervous-system-reset", label: "神经系统重置", angle: "framework", bullet: "提供有多迷走神经理论支撑的 5 天迷走神经重置方案——读者可以立即跟随执行的结构" },
    { id: "decision-fatigue", label: "决策疲劳", angle: "reveal", bullet: "揭示决策疲劳与意志力无关——那是前额叶皮质过载，在运行过时的威胁软件" },
    { id: "phone-addiction", label: "手机成瘾", angle: "leverage", bullet: "将手机重构为生物反馈工具——你的刷屏模式精确揭示了你的神经系统在渴望什么" },
  ]},
  { label: "悲伤与疗愈", icon: "🕊️", color: "#f43f5e", tags: [
    { id: "grief-timeline", label: "悲伤时间线", angle: "debunk", bullet: "破除「悲伤五阶段」模型——悲伤是非线性的，知道这一点能阻止读者将自己的疗愈过程病理化" },
    { id: "toxic-relationship-healing", label: "有毒关系疗愈", angle: "origin", bullet: "将吸引力模式追溯到早期依恋创伤——理解起源能打破重复循环" },
    { id: "intergenerational-trauma", label: "代际创伤", angle: "reveal", bullet: "揭示创伤如何通过表观遗传学和家族沉默传递——读者明白，他们的痛苦不只是「想太多」" },
    { id: "heartbreak-recovery", label: "心碎恢复", angle: "framework", bullet: "将康复分为三个阶段：生存、稳定、重建——在心碎者感到迷失时给予他们一张地图" },
    { id: "emotional-numbness", label: "情感麻木", angle: "leverage", bullet: "将麻木重构为神经系统最精密的保护机制——不是感受的缺失，而是感受的过载" },
  ]},
  { label: "身份认同与人生方向", icon: "🧭", color: "#059669", tags: [
    { id: "feeling-behind", label: "感觉落后", angle: "debunk", bullet: "破除比较时间线——根本不存在「落后」，因为每个人都在完全不同的基础上建造" },
    { id: "quarter-life-crisis", label: "四分之一人生危机", angle: "leverage", bullet: "将危机重构为身份系统的升级——那种不适是你正在超越旧版自我的证明" },
    { id: "identity-rebuild", label: "身份重建", angle: "framework", bullet: "提供 4 阶段身份重建框架——从解构到整合，再到真实表达" },
    { id: "purpose-after-30", label: "30岁后的人生意义", angle: "origin", bullet: "将意义的空洞追溯到继承的职业剧本——一旦你看清自己活的是谁的梦想，你自己的梦想便会显现" },
  ]},
  { label: "专注力与表现", icon: "⚡", color: "#0ea5e9", tags: [
    { id: "habit-building", label: "习惯养成", angle: "framework", bullet: "将习惯养成系统化为环境设计＋身份转变——即使动力失效，这个结构依然有效" },
    { id: "ADHD-productivity", label: "ADHD效率", angle: "leverage", bullet: "将 ADHD 的超专注重构为战略优势——你的大脑没有坏掉，那些效率建议只是为别人设计的" },
    { id: "dopamine-detox", label: "多巴胺排毒", angle: "debunk", bullet: "破除流行的多巴胺排毒趋势——真正的问题是奖励敏感性，解决之道是重新校准，而非剥夺" },
    { id: "deep-work", label: "深度工作", angle: "reveal", bullet: "揭示焦虑型思维的深度工作需要在专注块之间进行神经系统重置——而不仅仅是意志力和计时器" },
  ]},
  { label: "意义与灵性", icon: "✨", color: "#7c3aed", tags: [
    { id: "meditation-beginners", label: "冥想入门", angle: "debunk", bullet: "破除「清空思绪」的误解——冥想是关于觉察思绪，而非消除它们。这一重构让初学者不再轻易放弃" },
    { id: "meaning-after-loss", label: "失去后的意义", angle: "origin", bullet: "将意义建构追溯到人类对叙事连贯性的需求——当失去打碎了故事，重建意义就是疗愈" },
    { id: "spiritual-no-religion", label: "无宗教灵性", angle: "leverage", bullet: "将灵性渴望重构为一种特质，而非缺口——你不需要借助他人的传统来触及深度与超越" },
    { id: "inner-peace-chaos", label: "混乱中的内心平静", angle: "reveal", bullet: "揭示内心平静不是混乱的消失，而是与混乱建立不同的关系——噪音不会停止，但你不再溺其中" },
    { id: "mindfulness-skeptics", label: "对正念持怀疑态度者", angle: "framework", bullet: "提供有神经科学数据支撑、怀疑者也能接受的 5 分钟练习——无需香薰，无需咒语，只有可量化的结果" },
  ]},
];

const ANGLE_FEEDBACK = {
  debunk: { label: "破除迷思", icon: "🔍", systemEffect: "标题以反常识钩子开头——「你的咨询师不会告诉你的事。」", emotionalBenefit: "读者感到智识上被尊重，他们对传统建议无效的怀疑得到验证。" },
  framework: { label: "框架体系", icon: "🔧", systemEffect: "标题以结构引领——「5 步方案……」可重复的系统。", emotionalBenefit: "不知所措的读者看到清晰系统时终于松一口气，将模糊的焦虑转化为具体步骤。" },
  reveal: { label: "揭晓", icon: "💡", systemEffect: "标题揭示隐藏真相——「你睡不着的真正原因。」", emotionalBenefit: "读者经历「顿悟时刻」，将自我叙事从「我坏掉了」改写为「我被理解了」。" },
  leverage: { label: "杠杆借力", icon: "🔄", systemEffect: "标题重构弱点——「你的焦虑是一种超能力。」", emotionalBenefit: "读者停止与自己对抗。传递「你没有坏掉，只是用错了你的天赋」的信念。" },
  origin: { label: "根源", icon: "🌱", systemEffect: "标题追溯根本原因——「你的模式究竟从哪里开始。」", emotionalBenefit: "从理解模式的起源中获得深层释怀，为过去的自己生出慈悲。" },
};

// ═══════════════════════════════════════════════════════════
// MARKET DATA — Visual Identity & Topic/Angle research scores
// ═══════════════════════════════════════════════════════════
const VISUAL_MARKET = {
  calm_minimal:      { shelf: 62, trust: 88, social: 70, premium: 78, rank: 5, demo: "30–55, F-lean", superpower: "被治疗师和专业人士推荐——「公信力」之选" },
  dark_intense:      { shelf: 84, trust: 68, social: 85, premium: 80, rank: 3, demo: "22–38, neutral", superpower: "产生最多自然用户内容——读者将其作为身份信号分享" },
  earthy_organic:    { shelf: 65, trust: 82, social: 74, premium: 68, rank: 6, demo: "28–50, F-strong", superpower: "建立最深厚的准社会信任——读者感到作者是他们中的一员" },
  bold_modern:       { shelf: 88, trust: 72, social: 82, premium: 75, rank: 1, demo: "25–40, neutral", superpower: "在任何书架或动态中穿透视觉噪音——停止刷屏的冠军" },
  premium_soft:      { shelf: 78, trust: 85, social: 76, premium: 92, rank: 2, demo: "30–50, 女性略多", superpower: "让读者感到是在投资自己，而非仅仅购买一本书" },
  sacred_cosmic:     { shelf: 75, trust: 77, social: 79, premium: 83, rank: 4, demo: "28–45, 女性略多", superpower: "建立狂热追随者——购买的读者成为布道者" },
};

const ANGLE_MARKET = {
  debunk:    { viral: 88, trust: 45, conversion: 55, seo: 60, tip: "最适合漏斗顶端——争议性内容在冷受众中驱动分享" },
  framework: { viral: 55, trust: 82, conversion: 90, seo: 85, tip: "最适合漏斗中端——准备行动的受众需要结构" },
  reveal:    { viral: 80, trust: 65, conversion: 65, seo: 70, tip: "最适合邮件钩子——将好奇心引导至更深层内容" },
  leverage:  { viral: 75, trust: 70, conversion: 72, seo: 50, tip: "最适合重构异议——将抗拒转化为认同" },
  origin:    { viral: 50, trust: 92, conversion: 60, seo: 55, tip: "最适合长篇忠诚度——与现有受众加深信任" },
};

const TOPIC_MARKET = {
  "睡眠与焦虑":       { search: 95, competition: 88, monetization: 82, growth: 75, platform: "YouTube" },
  "职业倦怠与工作":        { search: 80, competition: 75, monetization: 78, growth: 85, platform: "LinkedIn" },
  "悲伤与疗愈":       { search: 55, competition: 40, monetization: 60, growth: 65, platform: "Podcasts" },
  "身份认同与人生方向":  { search: 60, competition: 55, monetization: 70, growth: 80, platform: "TikTok" },
  "专注力与表现":   { search: 85, competition: 82, monetization: 88, growth: 70, platform: "YouTube" },
  "意义与灵性":{ search: 50, competition: 45, monetization: 65, growth: 75, platform: "书籍" },
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
        eyebrow="领域"
        title="占领您的搜索领地"
        subtitle="每个类别选一个话题——每个选择都设定了您的品牌用来框定该领域的内容角度。随着您的选择，侧边栏会实时更新。"
      />
      <div className="mb-6 rounded-xl border border-indigo-100/80 bg-indigo-50/50 p-4 backdrop-blur-sm">
        <p className="text-xs leading-relaxed text-indigo-900">
          <strong>每个类别选一个。</strong> 每个话题都配有一个内容角度——破除、框架、揭示、善用或根源。切换话题时，侧边栏的角度和策略也会随之更新。
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
                    <span>{tag.label || tag.id.replace(/-/g, " ")}</span>
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
      <h2 className="text-2xl font-extrabold text-white tracking-tight">市场洞察</h2>
      <p className="text-sm text-white mt-1 mb-2">您的创意愿景是品牌的灵魂。但灵魂本身无法支付账单。这一页展示系统如何将您的独特方向与实际市场数据相融合——真实的搜索量、经验证的买家画像和高转化关键词领域——以确保您的目录触达那些已在寻找您所提供内容的人。</p>
      <p className="text-xs text-white mb-6 italic">您品牌的声音和身份不会改变。我们只是确保它出现在需求所在之处。</p>

      {/* Gen Z / Gen Alpha FIRST */}
      <div className="rounded-xl border border-violet-200 bg-violet-50 p-5 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Globe size={16} className="text-violet-600" />
          <span className="text-sm font-bold text-violet-800">年轻受众触达：Z 世代 + Alpha 世代</span>
        </div>
        <p className="text-xs text-violet-700 leading-relaxed mb-3">
          Pearl Prime 上的每个品牌都会自动服务 Z 世代和 Alpha 世代读者——无需额外配置。系统为您的内容创建适龄适配版本：针对移动优先消费调整的短篇格式、针对刷屏发现优化的视觉优先排版、TikTok 和 YouTube Shorts 的平台原生钩子，以及为以图像而非段落思考的读者打造的全插画漫画风格版本。Alpha 世代（2010-2025 年出生）是第一个从出生起就拥有情感词汇的世代——他们比任何一个前代都更早地搜索心理健康内容。您的品牌在他们所在之处与他们相遇。
        </p>
        <div className="grid grid-cols-3 gap-2">
          {[
            { icon: Smartphone, label: "短内容优先", desc: "TikTok、Reels、Shorts 优化" },
            { icon: BookMarked, label: "漫画版本", desc: "全插画视觉格式" },
            { icon: Headphones, label: "微有声书", desc: "15-30 分钟移动端收听" },
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
          <span className="text-sm font-bold text-emerald-800">融合如何运作</span>
        </div>
        <p className="text-xs text-emerald-700 leading-relaxed mb-4">
          我们将您的创意方向——原型、声音、话题和角度——与经验证的高效搜索词、受众细分和实时市场信号相结合。您的品牌身份保持完整，而系统确保您的目录瞄准人们正在积极搜索的话题。这意味着您的书籍出现在需求已然存在之处，您的标题匹配人们实际输入搜索栏的内容，您的内容触达拥有经验证消费能力的买家画像。结果：您独特的声音触达尽可能广泛的受众。
        </p>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white rounded-lg p-3">
            <div className="text-[10px] font-bold text-emerald-700 uppercase mb-1">您的方向</div>
            <p className="text-[11px] text-white">原型、声音、话题、角度、视觉风格——保留为您品牌独特的创意身份</p>
          </div>
          <div className="bg-white rounded-lg p-3">
            <div className="text-[10px] font-bold text-emerald-700 uppercase mb-1">市场洞察</div>
            <p className="text-[11px] text-white">经验证的收益画像、热门搜索词、高转化关键词，以及与您原型匹配的需求数据</p>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5 mb-6">
        <div className="text-xs font-bold text-white mb-3">适合您原型的经验证收益画像</div>
        <p className="text-[11px] text-white mb-3">这些是在您的情感领域中拥有经验证购买力的受众细分群体。系统确保您的目录触达所有这些人。</p>
        {proven.personas.map((p, i) => (
          <div key={i} className="flex items-start gap-2 mb-2.5">
            <Target size={12} className="text-indigo-500 flex-shrink-0 mt-0.5" />
            <span className="text-[11px] text-white">{p}</span>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <div className="text-xs font-bold text-white mb-3">高效能搜索话题</div>
        <p className="text-[11px] text-white mb-3">这些搜索词拥有经验证的月搜索量和转化率。您的标题和关键词将围绕这些词与您的自定义选择一起优化。</p>
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
    { id: "audiobook", label: "有声书", icon: Headphones, desc: "在 Audible、Spotify、Apple Books 和全球 40 余个平台上发布完整旁白有声书", benefit: "听众在通勤、散步和难眠之夜中疗愈——您的声音成为他们最脆弱的私密时刻的陪伴" },
    { id: "yt_channel", label: "YouTube 频道", icon: Tv, desc: "每日视频内容——短视频、长篇讲座、引导式练习和可视化章节", benefit: "视觉型学习者通过动态图像处理情感——您的品牌成为他们动态中每日的存在，通过持续出现建立信任" },
    { id: "tiktok", label: "TikTok", icon: Smartphone, desc: "平台原生短视频，搭配热门音频、文字叠加和钩子优先的剪辑方式", benefit: "您在刷屏途中捕捉到脆弱时刻的人——30 秒的视频可以成为改变人生的第一步" },
    { id: "pocket_guide", label: "口袋指南", icon: BookOpen, desc: "浓缩为 30-50 页的快速参考版——周末即可读完，收获核心精华", benefit: "无法承诺读完整本书的不知所措读者，得到即时的释怀——一本周末就能读完、传递核心转变的书" },
    { id: "7_day_guide", label: "7 天实操方案", icon: Clock, desc: "压缩版转变方案——每天一章，明确的每日行动，快速见效", benefit: "结构减少不知所措——那些「想读时再读」失败的读者，在每日作业的积累动力中茁壮成长" },
    { id: "mastercourse", label: "大师课系列", icon: GraduationCap, desc: "多卷深度系列，复杂度递进——4-8 本书层层递进", benefit: "投入的读者在数月内深入其中——每一卷都建立在上一卷基础上，创造推动真实、持久改变的持续修行" },
    { id: "workbook", label: "互动练习册", icon: PenTool, desc: "以练习为主的配套书，含填写区域、追踪表格和引导式反思空间", benefit: "书写激活与阅读不同的大脑通路——练习册将被动消费转化为主动的自我发现与整合" },
    { id: "daily_journal", label: "每日日记", icon: BookMarked, desc: "30-90 day guided journal — one prompt per day with space for writing and reflection", benefit: "每日提示锻炼自我意识肌肉——读者一页一页地与自己的内心世界建立持续的关系" },
  ];

  return (
    <div>
      <h2 className="text-2xl font-extrabold text-white tracking-tight">格式与渠道选择</h2>
      <p className="text-sm text-white mt-1 mb-2">您的格式重心告诉目录规划器是优化视觉优先的短内容，还是深度长篇书籍。您的渠道选择决定您的品牌在哪里发布——每个激活的渠道都为流水线增加内容权重，意味着更多格式、更多变体，以及与受众更多的接触点。</p>

      <div className="text-xs font-bold uppercase tracking-wider text-white mb-3 mt-6">主要格式重心</div>
      <p className="text-[11px] text-white mb-3">这是最重要的格式决策，它改变了目录规划器在整个品牌中分配内容的方式。</p>
      <div className="grid grid-cols-2 gap-3 mb-8">
        <button onClick={() => setFocus("manga")}
          className={`p-5 rounded-xl border-2 text-left transition-all ${formatFocus === "manga" ? "border-gray-900 bg-gray-50 shadow-md" : "border-gray-200 bg-white hover:border-gray-300"}`}>
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-rose-500 to-purple-600 flex items-center justify-center mb-3"><Image size={24} className="text-white" /></div>
          <div className="text-sm font-bold text-white">漫画 / 视觉</div>
          <p className="text-[11px] text-white mt-1 leading-relaxed">插画面板、视觉叙事、漫画式排版。有声书默认为短篇格式（15-30 分钟）。针对 Z 世代和 Alpha 世代的视觉优先消费方式优化。</p>
          {formatFocus === "manga" && <div className="mt-2 bg-rose-50 rounded-lg p-2"><p className="text-[10px] text-rose-700">目录规划器将在所有渠道优先考虑短篇有声书、视觉内容和插画密集型格式。</p></div>}
        </button>
        <button onClick={() => setFocus("book")}
          className={`p-5 rounded-xl border-2 text-left transition-all ${formatFocus === "book" ? "border-gray-900 bg-gray-50 shadow-md" : "border-gray-200 bg-white hover:border-gray-300"}`}>
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center mb-3"><BookOpen size={24} className="text-white" /></div>
          <div className="text-sm font-bold text-white">传统书籍</div>
          <p className="text-[11px] text-white mt-1 leading-relaxed">全长叙事书籍、深度引导课程、综合练习册。有声书为长篇格式（3-8 小时）。针对追求深度的读者优化。</p>
          {formatFocus === "book" && <div className="mt-2 bg-amber-50 rounded-lg p-2"><p className="text-[10px] text-amber-700">目录规划器将在所有渠道优先考虑长篇书籍、完整课程和深度系列。</p></div>}
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

      <div className="text-xs font-bold uppercase tracking-wider text-white mb-3">发布渠道</div>
      <p className="text-[11px] text-white mb-3">选择您希望品牌发布内容的所有渠道。每个渠道都会生成专属内容，适配该平台的格式、受众和算法要求。</p>
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
      if (found) return { tagId, tagLabel: found.label || found.id.replace(/-/g, " "), angle: found.angle, bullet: found.bullet, category: cat.label, catIcon: cat.icon, catColor: cat.color };
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
    if (v.id === "gentleDirect") return p <= 3 ? "赋予许可" : p >= 8 ? "权威有力" : "平衡";
    if (v.id === "simpleDeep") return p <= 3 ? "易于接近" : p >= 8 ? "多层次" : "中等深度";
    if (v.id === "emotionalLogical") return p <= 3 ? "故事引领" : p >= 8 ? "数据驱动" : "平衡";
    if (v.id === "spiritualPractical") return p <= 3 ? "沉思" : p >= 8 ? "策略性" : "融合";
    return "";
  });

  // Generate true category statement
  const trueCategory = arch && persona
    ? `${arch.name} for ${persona.label}${moment ? ` — 捕捉他们在「${moment.label}」的时刻` : ""}`
    : arch ? arch.name : "蓝图";

  // Content engine steps derived from voice + angle mix
  const engineSteps = [
    { step: "命名问题", desc: moment ? `以「${moment.scene}」开场——读者当下的精确状态` : "以读者的确切痛点开场", icon: "🎯" },
    { step: "重构身份认同", desc: `运用${uniqueAngles.includes("debunk") ? "破除迷思" : uniqueAngles.includes("reveal") ? "揭晓" : "溯源起点"}的切角改变他们的自我叙事`, icon: "🪞" },
    { step: "提供微工具", desc: `提供${uniqueAngles.includes("framework") ? "今晚就能使用的框架" : "可立即实践的可行洞见"}`, icon: "🔧" },
    { step: "落在情感上", desc: emotions.length > 0 ? `每件内容都以此作结：「${emotions[0]}」` : "每件内容都落在承诺的感受上", icon: "💫" },
  ];

  // Unfair advantage loop
  const loopSteps = [
    { label: "重构", desc: "打破他们的旧故事", color: "#6366f1" },
    { label: "调节", desc: "平静神经系统", color: "#059669" },
    { label: "修复", desc: "从身体开始重建", color: "#f59e0b" },
    { label: "重新定向", desc: "指向新的身份认同", color: "#f43f5e" },
  ];

  // Positioning map coords — Gentle↔Direct on X, Simple↔Deep on Y
  const posX = voicePositions.find(v => v.id === "gentleDirect")?.position || 5;
  const posY = voicePositions.find(v => v.id === "simpleDeep")?.position || 5;

  // Emotional staircase — build ascending steps from trigger to each emotion
  const staircaseSteps = [
    { label: moment ? moment.label : "痛点", color: "#f43f5e", sub: "他们的起点" },
    ...emotions.slice(0, 5).map((e, i) => {
      const cat = _EC.find(c => c.items.includes(e));
      return { label: e, color: cat?.color || "#6366f1", sub: cat?.name || "" };
    }),
  ];

  return (
    <div>
      <StepHero
        eyebrow="揭晓"
        title="这就是您的品牌"
        subtitle=""
      />

      {/* ═══ 1. TRUE CATEGORY — gradient banner ═══ */}
      {arch && (
        <div id="rev-category" className={`mb-6 rounded-2xl border-2 p-6 bg-gradient-to-br ${arch.gradient} shadow-lg`}>
          <div className="text-center">
            <div className="text-white/70 text-[10px] font-bold uppercase tracking-[0.3em] mb-2">您的真实类别</div>
            <div className="text-white text-xl font-extrabold mb-2">{trueCategory}</div>
            <div className="text-white/80 text-sm leading-relaxed">{arch.tagline}</div>
            {arch.visionVibe && <p className="mt-3 text-white/70 text-[11px] leading-relaxed max-w-md mx-auto italic">{arch.visionVibe}</p>}
          </div>
        </div>
      )}

      {/* ═══ 2. VOICE SIGNATURE — circular gauges ═══ */}
      {Object.keys(state.voiceSettings || {}).length > 0 && (
        <div id="rev-voice" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">声音特征</div>
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
            你的声音是 <span className="text-white font-semibold">{voiceDesc.join(" · ")}</span>
          </div>
        </div>
      )}

      {/* ═══ 2b. POSITIONING MAP — 2D quadrant ═══ */}
      <div id="rev-positioning" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">定位图</div>
        <div className="text-[10px] text-white/70 mb-3 text-center">您的声音在市场版图中的位置</div>
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
          <text x="30" y="285" fontSize="9" fill="#9ca3af" fontWeight="bold">温柔</text>
          <text x="265" y="285" fontSize="9" fill="#9ca3af" fontWeight="bold">直接</text>
          <text x="5" y="15" fontSize="9" fill="#9ca3af" fontWeight="bold" transform="rotate(-90 10 15)">深邃</text>
          <text x="5" y="275" fontSize="9" fill="#9ca3af" fontWeight="bold" transform="rotate(-90 10 275)">简洁</text>
          {/* Quadrant labels */}
          <text x="95" y="75" textAnchor="middle" fontSize="8" fill="#6366f1" fontWeight="600">智慧引路人</text>
          <text x="225" y="75" textAnchor="middle" fontSize="8" fill="#059669" fontWeight="600">专业教练</text>
          <text x="95" y="210" textAnchor="middle" fontSize="8" fill="#f59e0b" fontWeight="600">温暖的朋友</text>
          <text x="225" y="210" textAnchor="middle" fontSize="8" fill="#f43f5e" fontWeight="600">大胆的导师</text>
          {/* Brand dot */}
          {(() => {
            const dotX = 30 + (posX / 10) * 260;
            const dotY = 270 - (posY / 10) * 260;
            return (<>
              <circle cx={dotX} cy={dotY} r="14" fill="#6366f1" fillOpacity="0.15" stroke="#6366f1" strokeWidth="2" />
              <circle cx={dotX} cy={dotY} r="6" fill="#6366f1" />
              <text x={dotX} y={dotY - 20} textAnchor="middle" fontSize="9" fill="#6366f1" fontWeight="bold">您</text>
            </>);
          })()}
        </svg>
      </div>

      {/* ═══ 3. VISUAL IDENTITY + MARKET DATA ═══ */}
      {visual && (() => {
        const vm = VISUAL_MARKET[visual.id] || {};
        const bars = [
          { label: "书架吸引力", val: vm.shelf || 0, color: "#f59e0b" },
          { label: "信任信号", val: vm.trust || 0, color: "#059669" },
          { label: "社交传播力", val: vm.social || 0, color: "#6366f1" },
          { label: "高端质感", val: vm.premium || 0, color: "#7c3aed" },
        ];
        return (
          <div id="rev-visual" className="mb-6 rounded-2xl border border-gray-200 bg-white overflow-hidden shadow-sm">
            <div className="flex items-center gap-0 border-b border-gray-100">
              {visual.palette.map((col, i) => (
                <div key={i} className="flex-1 h-12" style={{ backgroundColor: col }} />
              ))}
            </div>
            <div className="p-4">
              <div className="text-[10px] font-bold uppercase text-white">视觉身份</div>
              <div className="mt-1 text-base font-bold text-white">{visual.label}</div>
              <p className="mt-1 text-[11px] text-white italic">{visual.mood}</p>
            </div>
            <div className="px-4 pb-4">
              <div className="text-[9px] font-bold uppercase tracking-wider text-white mb-2">市场评分</div>
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
                <span className="text-[9px] px-2 py-0.5 rounded-full bg-violet-100 text-white font-bold">排名 #{vm.rank || '—'}</span>
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
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">情感阶梯</div>
          <div className="text-[10px] text-white/70 mb-4">您的读者从痛苦走向承诺——每一步都建立在上一步之上</div>
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
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">话题 × 角度策略</div>
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
                    <span className="text-[11px] font-bold text-white flex-1">{p.tagLabel}</span>
                    <span className="text-[9px] px-2 py-0.5 rounded-full font-bold" style={{ backgroundColor: p.catColor + '15', color: p.catColor }}>{af?.icon} {af?.label}</span>
                  </div>
                  <p className="text-[10px] text-white/70 leading-relaxed mb-2">{p.bullet}</p>
                  {/* Market mini-bars */}
                  <div className="grid grid-cols-2 gap-x-3 gap-y-1">
                    {[
                      { label: "传播力", val: am.viral, color: "#f43f5e" },
                      { label: "搜索", val: tm.search, color: "#0ea5e9" },
                      { label: "转化", val: am.conversion, color: "#059669" },
                      { label: "增长", val: tm.growth, color: "#f59e0b" },
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
                      综合评分: {comboScore}
                    </span>
                    <span className="text-[8px] text-white/70">{tm.platform && `最佳平台：${tm.platform}`}</span>
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
        <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-1">内容引擎公式</div>
        <div className="text-[10px] text-white/70 mb-5">每一件内容都遵循这一序列——您独特的飞轮</div>
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
          <span className="text-[9px] font-bold text-white/50 uppercase tracking-wider">↻ 每件内容都重复此循环</span>
          <div className="h-px flex-1" style={{ background: 'linear-gradient(90deg, transparent, #b4530940, transparent)' }} />
        </div>
      </div>

      {/* ═══ 7. UNFAIR ADVANTAGE LOOP — circular diagram ═══ */}
      <div id="rev-loop" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">不公平优势循环</div>
        <div className="text-[10px] text-white/70 mb-4 text-center">每一件内容都为下一件提供养分——每一个出口都是通往更深转变的入口</div>
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
          <text x="160" y="170" textAnchor="middle" fontSize="7" fill="#6b7280">持续重复</text>
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
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">受众体验</div>
          <div className="text-[10px] text-white/70 mb-3">{persona.emoji} {persona.label} 体验你的品牌的过程：</div>
          <div className="flex flex-col items-center gap-1.5">
            {[
              { phase: "触发", desc: `${moment.emoji} ${moment.scene}`, color: "#f43f5e", bg: "bg-rose-50" },
              { phase: "发现", desc: `他们找到您的内容——钩子精准命名了他们的痛苦`, color: "#f59e0b", bg: "bg-amber-50" },
              { phase: "信任", desc: `您${voiceDesc[0]}的声音让他们感到${voiceDesc[2]} — 不是被说教，而是被理解`, color: "#3b82f6", bg: "bg-blue-50" },
              { phase: "转变", desc: emotions[0] ? `他们开始感受到：「${emotions[0]}」` : "承诺的情感触达", color: "#059669", bg: "bg-emerald-50" },
              { phase: "回归", desc: `他们回来，因为每一件内容都在更深层次提供同样的转变`, color: "#7c3aed", bg: "bg-violet-50" },
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
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">声音 × 话题协同</div>
          <div className="text-[10px] text-white/70 mb-3">您的声音基调如何放大每个内容角度</div>
          <div className="space-y-3">
            {topicAnglePairs.map((p, i) => {
              const af = _AF[p.angle];
              const score = calcSynergyScore(voicePositions, p.angle);
              const multiplier = (0.5 + (score / 100) * 1.5).toFixed(1);
              const barColor = p.catColor;
              const gentlePos = voicePositions.find(v => v.id === "gentleDirect")?.position || 5;
              const toneWord = gentlePos <= 3 ? "温柔地" : gentlePos >= 8 ? "直接地" : "清晰地";
              return (
                <div key={i} className="rounded-xl bg-white p-3 border border-violet-100">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm">{p.catIcon}</span>
                    <span className="text-[10px] text-white flex-1">
                      您以<strong>{toneWord}</strong>的语调进行{af?.label} <strong>{p.tagLabel}</strong>
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
                <span className="text-[10px] font-bold text-white">整体声音契合度</span>
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
          { label: "视觉", val: visualAvg, color: "#7c3aed" },
          { label: "传播力", val: avg("viral"), color: "#f43f5e" },
          { label: "信任", val: avg("trust"), color: "#059669" },
          { label: "转化", val: avg("conversion"), color: "#f59e0b" },
          { label: "SEO", val: avg("seo"), color: "#0ea5e9" },
          { label: "增长", val: avg("growth"), color: "#6366f1" },
        ];
        const overallScore = Math.round(dims.reduce((s, d) => s + d.val, 0) / dims.length);
        const sides = 6, cx = 150, cy = 110, r = 75;

        return (
          <div id="rev-radar" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <div className="text-[10px] font-bold uppercase tracking-wider text-white">品牌实力</div>
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
          <div className="text-violet-300/70 text-[10px] font-bold uppercase tracking-[0.3em] mb-3 text-center">品牌综合</div>
          <p className="text-center text-white text-sm leading-relaxed font-medium">
            你是 <strong>{arch.name}</strong> — 以{voiceDesc[0]}、{voiceDesc[1]}的语调，捕捉{" "}
            <strong>{persona.label}</strong>
            {moment && <>在他们<em>「{moment.label}」</em>时刻</>}，{" "}
            {uniqueAngles.length > 0 && <>运用 {uniqueAngles.map(a => _AF[a]?.label).join(" + ")} 的切角</>}{" "}
            {emotions.length > 0
              ? <>传递一个承诺：<strong>「{emotions[0]}」</strong></>
              : <>带来蜕变</>
            }。
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
    { label: "市场可行性", value: marketability, desc: "Alignment with proven market demand" },
    { label: "年轻受众触达", value: youthReach, desc: "Gen Z and Gen Alpha compatibility" },
    { label: "生命影响力", value: lifeImpact, desc: "Transformation depth for your reader" },
    { label: "平台覆盖范围", value: reachScore, desc: "Multi-channel distribution coverage" },
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
      ? "卓越的品牌定位。您的原型、受众和话题选择与高收益市场细分强力契合。这个品牌具有强大的商业潜力和深远的读者影响力。"
      : marketability >= 75
        ? "强大的品牌基础。您的选择创造了令人信服的品牌身份，与市场高度契合。再进行一些优化，便可迈入卓越领域。"
        : "良好的起点。您的品牌身份正在成形——考虑增加更多话题选择和渠道覆盖，以强化您的市场地位。";

  return (
    <div>
      <StepHero
        eyebrow="揭晓"
        title="这就是您的品牌"
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
                  <div className="text-[10px] font-bold uppercase text-violet-600/90">主要读者</div>
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
                  <div className="text-[10px] font-bold uppercase text-violet-600">视觉风格</div>
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
                  <div className="text-[8px] font-bold uppercase text-white">通道</div>
                  <div className="mt-0.5 text-[11px] font-semibold text-white">{state.onboardingLane.replace(/_/g, " ")}</div>
                </div>
              ) : null}
              {state.onboardingMarket ? (
                <div className="rounded-xl border border-violet-100/90 bg-white/80 p-2.5 text-center opacity-90">
                  <div className="text-[8px] font-bold uppercase text-white">市场</div>
                  <div className="mt-0.5 text-[11px] font-semibold text-white">{state.onboardingMarket}</div>
                </div>
              ) : null}
              {state.formatFocus ? (
                <div className="rounded-xl border border-violet-100/90 bg-white/80 p-2.5 text-center opacity-90">
                  <div className="text-[8px] font-bold uppercase text-white">格式</div>
                  <div className="mt-0.5 text-[11px] font-semibold text-white">{state.formatFocus === "manga" ? "漫画／视觉" : "书籍"}</div>
                </div>
              ) : null}
              {(state.channels || []).length > 0 ? (
                <div className="rounded-xl border border-violet-100/90 bg-white/80 p-2.5 text-center opacity-90">
                  <div className="text-[8px] font-bold uppercase text-white">渠道</div>
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
              <span className="text-xs font-bold text-emerald-900">沿您的方向阅读</span>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-emerald-900/90">{assessmentText}</p>
          </div>
        </section>
      </div>

      {/* Demoted score strip — same numeric logic, after narrative sections */}
      <div className="mt-10 rounded-2xl border border-gray-100 bg-gray-50/60 px-3 py-3 opacity-90">
        <div className="mb-2 text-center text-[9px] font-bold uppercase tracking-wider text-white">信号分数</div>
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

  const [matched, setMatched] = useState(null);

  const readTeacherMode = () => {
    try { const raw = localStorage.getItem("phoenix_book_mode"); if (raw) return JSON.parse(raw); } catch (_) {}
    const p = new URLSearchParams(window.location.search);
    const ut = p.get("teacher"), um = p.get("mode");
    if (ut) return { mode: "teacher", teacher: ut };
    if (um === "composite") return { mode: "composite", teacher: null };
    return { mode: "composite", teacher: null };
  };

  const handleLaunch = async () => {
    setYamlOutput(generateYAML(state));
    setSubmitted(true);
    try {
      const r = await fetch("brand_admin_brands.json", { cache: "no-store" });
      const brands = r.ok ? await r.json() : {};
      const m = matchBrand(state, brands, readTeacherMode());
      if (m) { setMatched(m); try { localStorage.setItem("phoenix_pending_brand", JSON.stringify(m)); } catch (_) {} }
    } catch (_) {}
  };

  if (submitted) {
    const arch = _A.find((a) => a.id === state.archetype);
    const persona = _P.find((p) => p.id === state.persona);
    const moment = _M.find((m) => m.id === state.moment);
    const visual = _V.find((v) => v.id === state.visualStyle);

    const choiceAudit = [
      arch && { label: "原型", value: arch.name, icon: arch.icon, gradient: arch.gradient, systemEffect: _SF.archetypes[state.archetype]?.systemEffect, emotionalBenefit: _SF.archetypes[state.archetype]?.emotionalBenefit },
      persona && { label: "读者", value: `${persona.emoji} ${persona.label}`, icon: Users, gradient: "from-blue-500 to-cyan-500", systemEffect: _SF.personas[state.persona]?.systemEffect, emotionalBenefit: _SF.personas[state.persona]?.emotionalBenefit },
      moment && { label: "时刻", value: `${moment.emoji} ${moment.label}`, icon: Target, gradient: "from-amber-500 to-orange-500", systemEffect: _SF.moments[state.moment]?.systemEffect, emotionalBenefit: _SF.moments[state.moment]?.emotionalBenefit },
      Object.keys(state.voiceSettings || {}).length > 0 && { label: "语气", value: `${Object.keys(state.voiceSettings).length} dimensions tuned`, icon: SlidersHorizontal, gradient: "from-indigo-500 to-violet-500", systemEffect: "全部 4 个声音维度校准每一章节、有声书和社交帖子的文章节奏、词汇层次、句式结构和情感温度", emotionalBenefit: "您的读者感受到一种仿佛专为他们写就的声音——那是他们所需的挑战与慰藉的精确融合。每一句话都能落地，因为语调契合了他们的情感准备状态。" },
      visual && { label: "影响", value: visual.label, icon: Palette, gradient: "from-rose-500 to-pink-500", systemEffect: _SF.visualStyles[state.visualStyle]?.systemEffect, emotionalBenefit: _SF.visualStyles[state.visualStyle]?.emotionalBenefit },
      (state.emotions || []).length > 0 && { label: "视觉", value: state.emotions.join(", "), icon: Heart, gradient: "from-rose-400 to-red-500", systemEffect: `${state.emotions.length} transformation promises woven into every title, CTA, and marketing message`, emotionalBenefit: "这些感受成为每一件内容的北极星——您的读者清楚知道等待他们的是怎样的转变，在读到第一个字之前，希望已经生根。" },
      state.tradition && { label: "灵性基础", value: state.tradition, icon: Sun, gradient: "from-amber-400 to-yellow-500", systemEffect: "影响所有内容中的词汇选择、哲学根基和传统特定引用", emotionalBenefit: "拥有这一传统的读者感到被认可和尊重。语言承载着真实传承的分量，而非流于表面的挪用。" },
      (state.angles || []).length > 0 && { label: "内容角度", value: state.angles.map(a => V4_ANGLES.find(v => v.id === a)?.label).filter(Boolean).join(", "), icon: Layers, gradient: "from-purple-500 to-indigo-500", systemEffect: `${state.angles.length} framing modes active — every title opens with one of these argumentative strategies`, emotionalBenefit: "每个角度为您的读者提供不同的疗愈入口。多种角度意味着您的品牌能触达处于不同改变准备程度的人。" },
      (state.topicTags || []).length > 0 && { label: "搜索领地", value: `${state.topicTags.length} 个主题已确认`, icon: Search, gradient: "from-emerald-500 to-teal-500", systemEffect: `${state.topicTags.length} search topics feed into title generation, keyword targeting, series planning, and ad campaigns`, emotionalBenefit: "您的内容在某人将痛苦打入搜索栏的那一刻出现。您不是在营销——您是用恰好正确的话回应一声求助的呼喊。" },
      state.onboardingLane && { label: "引导通道", value: state.onboardingLane.replace(/_/g, " "), icon: Layers, gradient: "from-fuchsia-500 to-purple-500", systemEffect: "验证条和注册匹配现在限定在您选择的通道内，让利益相关者提前预览正确的输出系列。", emotionalBenefit: "您可以立即看到您希望主推的通道是否有充分的验证支撑，减少上线时的意外。" },
      state.onboardingMarket && { label: "引导市场", value: state.onboardingMarket, icon: Globe, gradient: "from-sky-500 to-cyan-500", systemEffect: "注册匹配现在在引导流程中使用明确的市场过滤，避免跨市场产生虚假的信心。", emotionalBenefit: "您的团队审查真正与您计划进入的市场相匹配的示例。" },
      state.formatFocus && { label: "内容格式重心", value: state.formatFocus === "manga" ? "漫画 / 视觉" : "传统书籍", icon: BookOpen, gradient: "from-cyan-500 to-blue-500", systemEffect: _SF.formats[state.formatFocus]?.systemEffect, emotionalBenefit: _SF.formats[state.formatFocus]?.emotionalBenefit },
      (state.channels || []).length > 0 && { label: "发布渠道", value: `${state.channels.length} channels active`, icon: Globe, gradient: "from-violet-500 to-purple-500", systemEffect: `Content adapts to ${state.channels.length} platforms — each generates format-specific, algorithm-optimized variations`, emotionalBenefit: "您的读者在他们已经花时间的地方发现您。无论是凌晨 3 点刷 TikTok，还是周日听着有声书散步——您的品牌就在那里，准备好了，以正确的格式。" },
    ].filter(Boolean);

    const baseScore = 72;
    const marketability = Math.min(Math.round(baseScore + (state.archetype ? 8 : 0) + (state.persona ? 6 : 0) + ((state.topicTags || []).length > 3 ? 5 : (state.topicTags || []).length > 0 ? 3 : 0)), 97);
    const youthReach = Math.min(Math.round(65 + (state.formatFocus === "manga" ? 20 : 8) + ((state.channels || []).includes("tiktok") ? 8 : 0) + (state.persona === "gen_alpha" || state.persona === "gen_z_seeker" ? 7 : 3)), 98);
    const lifeImpact = Math.min(Math.round(baseScore + (state.moment ? 5 : 0) + (Object.keys(state.voiceSettings || {}).length > 0 ? 4 : 0) + (state.visualStyle ? 3 : 0) + 5), 96);
    const reachScore = Math.min(Math.round(70 + Math.min((state.channels || []).length * 1.5, 6) + (state.formatFocus ? 4 : 0) + (state.archetype ? 8 : 0)), 95);
    const overallScore = Math.round((marketability + youthReach + lifeImpact + reachScore) / 4);

    return (
      <div className="py-4">
        {/* Assigned brand — the wizard matched these selections to one existing brand */}
        {matched && (
          <div className="mb-6 rounded-2xl border border-emerald-300 bg-emerald-50 p-6 text-center">
            <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-700">{t("ui", "Your assigned brand")}</div>
            <div className="mt-1 text-2xl font-black text-gray-900">{matched.publication_corp}</div>
            <div className="mt-1 font-mono text-[11px] text-gray-500">
              {matched.is_teacher ? `${t("ui", "Teacher brand")} · ${matched.teacher}` : t("ui", "Composite brand")} · {matched.brand_id}
            </div>
            <button
              onClick={() => { window.location.href = "brand_handoff_dashboard.html?brand=" + encodeURIComponent(matched.brand_id); }}
              className="mt-4 inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-7 py-3 text-sm font-bold text-white shadow-lg transition-all hover:-translate-y-0.5 hover:bg-emerald-700"
            >
              {t("ui", "Open Brand Director")} <ArrowRight size={16} />
            </button>
          </div>
        )}
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
                <span className="text-[8px] font-bold uppercase text-white">总体</span>
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
            <p className="text-lg font-bold text-white mb-1">你的品牌宇宙诞生了。</p>
            <p className="text-sm text-white max-w-md mx-auto leading-relaxed">
              You've made {choiceAudit.length} defining choices that shape everything your brand creates — every book, audiobook, video, cover, and piece of social content. Here's what you've built and how it helps the people who need it most.
            </p>
          </div>
        </div>

        {/* Score Cards */}
        <div className="grid grid-cols-4 gap-2 mb-8">
          {[
            { label: "市场可行性", value: marketability, color: "#10b981" },
            { label: "年轻受众触达", value: youthReach, color: "#8b5cf6" },
            { label: "生命影响力", value: lifeImpact, color: "#ec4899" },
            { label: "平台覆盖范围", value: reachScore, color: "#3b82f6" },
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
          <h2 className="text-lg font-extrabold text-white mb-1">你的品牌选择</h2>
          <p className="text-xs text-white mb-4">您做出的每一个选择，它在系统中激活的功能，以及它如何从心理和情感层面帮助您的读者。</p>

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
                    <div className="text-[9px] font-bold text-emerald-500 bg-emerald-50 px-2 py-0.5 rounded-full flex-shrink-0">已激活</div>
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
              <span className="text-sm font-bold text-purple-800">用一句话描述你的品牌</span>
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
              <span className="text-xs font-bold text-white">品牌配置（YAML）</span>
            </div>
            <ChevronRight size={14} className={`text-white transition-transform ${showYaml ? "rotate-90" : ""}`} />
          </button>
          {showYaml && (
            <div className="bg-gray-900 p-4 overflow-auto max-h-96">
              <div className="flex gap-2 mb-3">
                <button onClick={() => { navigator.clipboard.writeText(yamlOutput); setYamlCopied(true); setTimeout(() => setYamlCopied(false), 2000); }}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-bold transition-colors">
                  <Check size={11} />{yamlCopied ? "已复制！" : "复制"}
                </button>
                <button onClick={() => { const blob = new Blob([yamlOutput], {type: "text/yaml"}); const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "brand-config.yaml"; a.click(); }}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-bold transition-colors">
                  <Download size={11} />下载 .yaml
                </button>
              </div>
              <pre className="text-[11px] text-green-400 font-mono whitespace-pre-wrap">{yamlOutput}</pre>
            </div>
          )}
        </div>

        {/* Final Message */}
        <div className="text-center py-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-50 text-emerald-700 text-xs font-bold mb-3">
            <Check size={12} /> 品牌配置已保存
          </div>
          <p className="text-sm text-white max-w-md mx-auto">
            您的品牌宇宙已就绪。Pearl Prime 系统将运用您的每一个选择，生成您的内容目录——改变人生的书籍、有声书、漫画、视频和社交内容。
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 rounded-2xl border border-violet-200/80 bg-gradient-to-br from-violet-50/90 via-white to-fuchsia-50/30 px-5 py-6 text-center shadow-sm">
        <h2 className="text-2xl font-extrabold tracking-tight sm:text-3xl" style={{ color: '#d97706', fontFamily: 'Cormorant Garamond, serif' }}>填写联系方式并点击「激活」</h2>
        <p className="mx-auto mt-3 max-w-md text-sm text-white/70">
          您将立即获得品牌内容目录的发布权限
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
          <Check size={14} className="shrink-0 text-emerald-600" strokeWidth={2.5} /> 读者和市场已选择
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
              <label className="mb-1 block text-xs font-semibold text-white">名字 *</label>
              <input
                type="text"
                placeholder="名字"
                className="w-full rounded-xl border border-gray-200 p-3 text-sm outline-none focus:border-gray-500"
                value={c.firstName || ""}
                onChange={(e) => handleField("firstName", e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold text-white">姓氏 *</label>
              <input
                type="text"
                placeholder="姓氏"
                className="w-full rounded-xl border border-gray-200 p-3 text-sm outline-none focus:border-gray-500"
                value={c.lastName || ""}
                onChange={(e) => handleField("lastName", e.target.value)}
              />
            </div>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-semibold text-white">邮箱 *</label>
              <input
                type="email"
                placeholder="you@example.com"
                className="w-full rounded-xl border border-gray-200 p-3 text-sm outline-none focus:border-gray-500"
                value={c.email || ""}
                onChange={(e) => handleField("email", e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold text-white">电话</label>
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
          <h3 className="mb-4 text-[10px] font-bold uppercase tracking-[0.15em] text-white">2 · 通讯渠道</h3>
          <p className="mb-3 text-[11px] text-white">可选——让我们通过邮件之外的方式联系您。</p>
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
                placeholder="+86..."
                className="w-full rounded-lg border border-gray-200 p-2.5 text-sm outline-none focus:border-gray-500"
                value={c.whatsapp || ""}
                onChange={(e) => handleField("whatsapp", e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-[10px] font-semibold text-white">微信号</label>
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
            <label className="mb-1 block text-[10px] font-semibold text-white">首选渠道</label>
            <select
              className="w-full rounded-lg border border-gray-200 bg-white p-2.5 text-sm outline-none focus:border-gray-500"
              value={c.preferred || "email"}
              onChange={(e) => handleField("preferred", e.target.value)}
            >
              <option value="email">仅限邮件</option>
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
            <div className="text-xs font-bold text-slate-800">安全流程</div>
            <p className="mt-1 text-[11px] leading-relaxed text-slate-600">
              税务识别号（SSN/EIN）将在审核通过后通过独立安全流程收集。本表单不收集敏感财务信息。
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
        {isReady ? "激活" : "添加姓名和邮箱以激活"}
      </button>
      {!isReady ? <p className="mt-2 text-center text-[11px] text-white">填写名字、姓氏和有效邮箱，即可解锁激活。</p> : null}
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
  // Accept ?teacher= URL param (back-compat) and ?mode=composite (explicit composite entry).
  if (!teacherMode) {
    const params = new URLSearchParams(window.location.search);
    const urlTeacher = params.get("teacher");
    const urlMode = params.get("mode");
    if (urlTeacher) teacherMode = { mode: "teacher", teacher: urlTeacher };
    else if (urlMode === "composite") teacherMode = { mode: "composite", teacher: null };
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
    { icon: PenTool, label: t("ui", "声音"), tint: "from-violet-500 to-indigo-600" },
    { icon: Image, label: t("ui", "视觉"), tint: "from-fuchsia-500 to-pink-600" },
    { icon: Users, label: t("ui", "读者"), tint: "from-sky-500 to-blue-600" },
    { icon: Layers, label: t("ui", "格式"), tint: "from-emerald-500 to-teal-600" },
  ];
  return (
    <div className="brand-studio-bg min-h-screen text-white">
      <div className="mx-auto max-w-3xl px-6 py-16">
        <div className="brand-studio-panel p-10 text-center sm:p-12">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-violet-200/80 bg-violet-50/80 px-4 py-1.5 text-xs font-semibold text-violet-800 backdrop-blur-sm">
            <Sparkles size={12} /> {t("ui", "Pearl Prime 品牌工作室")}
          </div>
          <h1 className="text-4xl font-black leading-tight tracking-tight text-white sm:text-5xl">{t("ui", "启动并塑造您的出版品牌")}</h1>
          <p className="mx-auto mt-4 max-w-lg text-base leading-relaxed text-white">
            {t("ui", "一次引导式会话——声音、外观与验证三者对齐。")}
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
              {t("ui", "开始构建")} <ChevronRight size={18} />
            </button>
          </div>
          <p className="mt-8 text-center text-xs">
            <a
              href="https://brand-admin-onboarding-bu2.pages.dev/pearl_prime_v6-3.html"
              className="font-semibold text-orange-400 underline decoration-orange-300 underline-offset-2 hover:text-orange-300"
            >
              {t("ui", "返回起点")}
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
    { step: "1", title: t("intro", "基础"), sub: t("intro", "原型与读者"), color: "from-indigo-500 to-violet-600" },
    { step: "2", title: t("intro", "声音"), sub: t("intro", "基调与影响"), color: "from-violet-500 to-fuchsia-600" },
    { step: "3", title: t("intro", "视觉与话题"), sub: t("intro", "视觉 + 领域"), color: "from-rose-500 to-orange-500" },
    { step: "4", title: t("intro", "格式"), sub: t("intro", "渠道与流水线"), color: "from-sky-500 to-cyan-600" },
    { step: "5", title: t("intro", "揭晓"), sub: t("intro", "蓝图与启动"), color: "from-slate-600 to-gray-900" },
  ];
  return (
    <div className="brand-studio-bg min-h-screen text-white">
      <div className="mx-auto max-w-3xl px-6 py-12">
        <button type="button" onClick={onBack} className="mb-6 flex items-center gap-1 text-xs text-white transition-colors hover:text-white">
          <ChevronLeft size={14} /> {t("ui", "返回")}
        </button>
        <div className="brand-studio-panel p-8 sm:p-10">
          <div className="text-center">
            <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-violet-600">{t("intro", "工作原理")}</p>
            <h1 className="mt-2 text-3xl font-black tracking-tight">{t("intro", "五个节拍，十一个选择")}</h1>
            <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-white">
              {t("intro", "基础 → 格式 → 蓝图 → 启动。")}
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
          {/* Mode picker — Teacher Books + Music Books (canonical 2026-06-03). */}
          <div className="mt-6 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
            <button
              type="button"
              onClick={onChooseTeacher}
              className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white shadow-lg transition-all hover:-translate-y-0.5 hover:bg-gray-800"
            >
              {t("ui", "老师之书")} <ArrowRight size={18} />
            </button>
            <button
              type="button"
              onClick={() => {
                try { localStorage.setItem("phoenix_book_mode", JSON.stringify({ mode: "music", teacher: null })); } catch (_) {}
                window.location.href = "/musician_reflections_survey";
              }}
              className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white shadow-lg transition-all hover:-translate-y-0.5 hover:bg-gray-800"
            >
              {t("ui", "音乐之书")} <ArrowRight size={18} />
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
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 text-indigo-600 text-xs font-semibold mb-4"><PenTool size={12} /> 第 1 步预览——写作声音</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">同一主题，截然不同的声音。</h1>
        <p className="text-white mb-8">两个品牌，同一话题——感受文字与能量的转变。</p>
        <CompareBlock labelA="静息实验室" labelB="澄心实验室" colorA="text-indigo-600" colorB="text-amber-600"
          contentA={<div><div className="flex gap-2 mb-3"><div className="w-14 h-20 rounded-lg shadow-md flex-shrink-0" style={{ background: "linear-gradient(135deg, #6366f1, #818cf8, #e0e7ff)" }} /><div><div className="text-[10px] text-white font-semibold uppercase">静息实验室</div><div className="text-sm font-bold text-white">凌晨两点，身体记得一切</div></div></div><p className="text-sm text-white leading-relaxed italic border-l-2 border-indigo-300 pl-3">"Your body remembers what your mind tries to forget. Right now, your shoulders are holding yesterday's argument."</p><div className="mt-3 bg-indigo-50 rounded-lg p-3"><div className="text-[10px] font-bold text-indigo-600 uppercase mb-1">练习</div><p className="text-xs text-indigo-800">"Inhale for 4 counts. Hold for 7. Exhale slowly for 8."</p></div></div>}
          contentB={<div><div className="flex gap-2 mb-3"><div className="w-14 h-20 rounded-lg shadow-md flex-shrink-0" style={{ background: "linear-gradient(135deg, #d97706, #f59e0b, #fef3c7)" }} /><div><div className="text-[10px] text-white font-semibold uppercase">澄心实验室</div><div className="text-sm font-bold text-white">您的手机正在偷走您的睡眠</div></div></div><p className="text-sm text-white leading-relaxed italic border-l-2 border-amber-400 pl-3">"您盯着天花板，因为大脑正在循环播放昨天的争论。"</p><div className="mt-3 bg-amber-50 rounded-lg p-3"><div className="text-[10px] font-bold text-amber-600 uppercase mb-1">练习</div><p className="text-xs text-amber-800">"手机放到另一个房间，平躺，呼气比吸气慢一些，90 秒，开始。"</p></div></div>}
        />
        <div className="mt-8 text-center">
          <button type="button" onClick={onNext} className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white transition-all hover:bg-gray-800">
            查看封面差异 <ChevronRight size={18} />
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
        <h1 className="text-3xl font-black tracking-tight mb-2">您的视觉风格塑造一切。</h1>
        <p className="text-white mb-8">一个选择，在封面和缩略图中层层扩散。</p>
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
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 text-amber-600 text-xs font-semibold mb-4"><Film size={12} /> 视频与社交预览</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">每日内容，您的标志性风格。</h1>
        <p className="text-white mb-8">短视频继承您的色调与氛围。</p>
        <div className="grid grid-cols-2 gap-4 mb-8">
          {ARCHETYPES.slice(0, 4).map((arch) => (
            <div key={arch.id} className="rounded-xl overflow-hidden border border-gray-200">
              <div className="h-32 flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${arch.coverColors[0]}88, ${arch.coverColors[1]}66)` }}><div className="text-center"><Play size={24} className="text-white/80 mx-auto mb-1" /><div className="text-[10px] text-white/80 font-bold">{arch.name}</div></div></div>
              <div className="p-3 bg-white"><div className="text-xs font-bold text-white">{arch.videoStyle}</div><div className="text-[10px] text-white mt-0.5">每日发布于 YouTube、TikTok、Instagram、Facebook、X</div></div>
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
        <h1 className="text-3xl font-black tracking-tight mb-2">一个品牌，无限格式。</h1>
        <p className="text-white mb-8">同一基因——不同容器。</p>
        <div className="grid grid-cols-3 gap-3 mb-8">
          {V4_FORMATS_STRUCTURAL.map((f) => (
            <div key={f.id} className="p-4 rounded-xl border border-gray-200 bg-white">
              <div className="text-[10px] text-white font-mono mb-1">{f.id}</div><div className="text-xs font-bold text-white">{f.label}</div><div className="text-[10px] text-white mt-0.5">{f.desc}</div>
              <div className="mt-2 flex items-center gap-2"><span className="text-[9px] bg-gray-100 text-white px-2 py-0.5 rounded-full">{f.chapters} ch</span><span className="text-[9px] bg-gray-100 text-white px-2 py-0.5 rounded-full">{f.tier}</span></div>
            </div>
          ))}
        </div>
        <div className="rounded-xl bg-gray-50 border border-gray-200 p-5 mb-8"><p className="text-xs text-white leading-relaxed">漫画、音频、课程、日记、视频——从同一内核自动适配。</p></div>
        <div className="mt-8 text-center">
          <button type="button" onClick={onNext} className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white transition-all hover:bg-gray-800">
            开始构建你的品牌 <ArrowRight size={18} />
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

const STEP_LABELS = ["原型", "读者", "时刻", "语气", "影响", "视觉", "主题", "蓝图", "启动"];

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
  const goToTeacherShowcase = () => { window.location.href = "teacher_showcase-zh.html"; };

  // If ?teacher= / ?mode=composite / ?mode=music in URL, skip intro and jump to wizard step 1.
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlTeacher = params.get("teacher");
    const urlMode = params.get("mode");
    if (urlTeacher || urlMode === "composite" || urlMode === "music") { setPhase("wizard"); setStep(0); scrollTop(); }
  }, []);

  // INTRO: 0=welcome, 1=journey → straight to wizard (preview pages removed)
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
          <ChevronLeft size={14} /> {t("ui", "返回")}
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
                  <ChevronLeft size={16} /> {t("ui", "返回")}
                </button>
                {step < 8 ? (
                  <button
                    type="button"
                    onClick={nextStep}
                    disabled={!canNext}
                    className={`flex items-center gap-1.5 rounded-xl px-6 py-2.5 text-sm font-bold transition-all ${canNext ? "bg-gray-900 text-white shadow-md shadow-slate-300/40 hover:bg-gray-800" : "cursor-not-allowed bg-gray-200 text-white"}`}
                  >
                    {t("ui", "下一步")} <ChevronRight size={16} />
                  </button>
                ) : null}
              </div>
            </div>
            <div className="hidden w-72 flex-shrink-0 lg:block">
              <div className="sticky top-8">
                <div className="mb-3 text-[10px] font-bold uppercase tracking-wider text-violet-600/90">{t("ui", "工作室洞察")}</div>
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