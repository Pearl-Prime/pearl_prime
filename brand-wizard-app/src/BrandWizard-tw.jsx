import { useState, useCallback, useRef, useMemo, useEffect } from "react";
import { useTranslation } from "./useTranslation.jsx";
import { matchBrand } from "./brandMatch.js";
import { ChevronRight, ChevronLeft, Eye, Sparkles, BookOpen, Mic, Film, Palette, Heart, Target, Zap, Shield, Sun, Moon, Flame, Feather, Brain, Compass, Star, Check, AlertTriangle, Download, Play, PenTool, Image, Layers, ArrowRight, Users, BarChart3, TrendingUp, Radio, Headphones, Tv, Smartphone, BookMarked, GraduationCap, Clock, Rocket, Award, Crown, Globe, Volume2, Brush, Activity, Search, Hash, Tag, Grip, CircleDot, SlidersHorizontal } from "lucide-react";
import { OutputProofStrip } from "./onboarding/OutputProofStrip.jsx";
import { LaneChoiceCard } from "./onboarding/LaneChoiceCard.jsx";
import { MarketChoiceCard } from "./onboarding/MarketChoiceCard.jsx";

/** zh-TW wizard default market; ?market= / phoenix_onboarding_market override onboarding.html handoff. */
function resolveOnboardingMarket() {
  const norm = (s) => String(s || "").toLowerCase().replace(/[\s-]+/g, "_");
  try {
    const url = new URLSearchParams(window.location.search).get("market");
    if (url) {
      const k = norm(url);
      if (k === "tw" || k === "taiwan" || k === "zh_tw") return "taiwan";
      return k;
    }
  } catch (_) {}
  try {
    const stored = localStorage.getItem("phoenix_onboarding_market");
    if (stored) {
      const k = norm(stored);
      if (k === "tw" || k === "taiwan" || k === "zh_tw") return "taiwan";
      return k;
    }
  } catch (_) {}
  return "taiwan";
}

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
    id: "nervous_system", name: "靜息實驗室",
    tagline: "當身體不停吶喊時",
    icon: Shield, gradient: "from-indigo-500 to-blue-600",
    bg: "bg-gradient-to-br from-indigo-50 to-blue-50",
    accent: "text-indigo-600", border: "border-indigo-200", activeBorder: "border-indigo-500",
    tags: ["平靜", "軀體", "調節"],
    coverStyle: "柔和漸層、低飽和色調、有機形狀",
    proseStyle: "輕柔、節奏舒緩、以呼吸為依歸",
    videoStyle: "慢動作自然場景、柔焦、環境氛圍",
    sampleTitle: "凌晨兩點，身體記得一切",
    sampleSubtitle: "為停不下來的思緒，重啟神經系統",
    sampleProse: "身體記得那些心智試圖遺忘的事。此刻，您的肩膀還承載著昨天的爭吵；下巴緊咬著那些沒說出口的話。這不是缺陷——這是您的神經系統正在做它本來就該做的事。",
    sampleExercise: "4-7-8 呼吸重整法：吸氣數到 4，憋氣數到 7，緩慢吐氣數到 8。重複三次。只需 57 秒，就能轉換整個神經系統的狀態。",
    coverColors: ["#6366f1", "#818cf8", "#e0e7ff"],
    emotions: ["終於平靜", "在身體裡感到安全", "釋放", "腳踏實地", "允許自己休息"],
    visionVibe: "在這個世界裡，寂靜不是空洞——而是飽滿的。身體是羅盤，不是囚籠。讀者不是逃離感受來找到安全感，而是終於學會傾聽它。",
  },
  {
    id: "identity_direction", name: "指南針工作室",
    tagline: "獻給那些感到迷茫但未破碎的人",
    icon: Compass, gradient: "from-emerald-500 to-teal-600",
    bg: "bg-gradient-to-br from-emerald-50 to-teal-50",
    accent: "text-emerald-600", border: "border-emerald-200", activeBorder: "border-emerald-500",
    tags: ["方向", "身分", "目標"],
    coverStyle: "俐落線條、羅盤圖紋、開闊地平線",
    proseStyle: "直接、溫暖、向前推進",
    videoStyle: "縮時旅程、黎明場景、道路意象",
    sampleTitle: "你不是落後——你是在建構",
    sampleSubtitle: "當所有人似乎都已找到方向，你還在尋覓",
    sampleProse: "滑過動態消息，所有人都過得很好。他們有理想的工作、穩定的感情、連植物都不會枯死的公寓。而你坐在這裡，不知道自己究竟在做什麼。",
    sampleExercise: "誠實盤點：寫下這週你做的三個選擇——哪怕很微小也好，一頓飯、一段對話、一條界線。再寫下一件你逃避的事。這個模式，就是你的羅盤指針。",
    coverColors: ["#059669", "#34d399", "#d1fae5"],
    emotions: ["頭腦清晰", "與目標相連", "充滿希望", "自信", "充滿活力"],
    visionVibe: "在這個世界裡，不知道不是失敗——而是起點。方向來自誠實的自我觀察，而非外在比較。讀者透過一個個細小而勇敢的選擇，建構自己的身份認同。",
  },
  {
    id: "emotional_healing", name: "柔光燈籠",
    tagline: "悲傷不遵循時間表",
    icon: Heart, gradient: "from-rose-500 to-pink-600",
    bg: "bg-gradient-to-br from-rose-50 to-pink-50",
    accent: "text-rose-600", border: "border-rose-200", activeBorder: "border-rose-500",
    tags: ["療癒", "悲傷", "溫柔"],
    coverStyle: "溫暖水彩、柔和光線、親密特寫",
    proseStyle: "溫柔、見證陪伴、給予許可",
    videoStyle: "溫馨燈光、雨打窗欞、溫暖室內",
    sampleTitle: "現在不好也沒關係",
    sampleSubtitle: "陪伴你度過那段沒有人提醒過你的悲傷",
    sampleProse: "沒有人告訴過你，悲傷可以是這種感覺——不是那種哭泣的悲傷，而是麻木的那種。你忘記為什麼走進一個房間，食物失去了味道，電話響了你只是看著它。",
    sampleExercise: "見證練習：將一隻手放在胸口，大聲說：「這很難受。我可以感受這一切。我不必現在就解決它。」留意身體有什麼變化。",
    coverColors: ["#f43f5e", "#fb7185", "#ffe4e6"],
    emotions: ["不再孤單", "被寬恕", "釋放", "在身體裡感到安全", "充滿希望"],
    visionVibe: "在這個世界裡，痛苦不需要變得有生產力。悲傷被陪伴見證，而非被建議解決。讀者不是被修復而療癒，而是終於被看見。",
  },
  {
    id: "performance_focus", name: "澄心實驗室",
    tagline: "切斷噪音，執行要事",
    icon: Zap, gradient: "from-amber-500 to-orange-600",
    bg: "bg-gradient-to-br from-amber-50 to-orange-50",
    accent: "text-amber-600", border: "border-amber-200", activeBorder: "border-amber-500",
    tags: ["專注", "自律", "執行"],
    coverStyle: "粗獷字體、強烈對比、幾何風格",
    proseStyle: "直接、有力、行動導向",
    videoStyle: "快速剪輯、深色背景、動態文字",
    sampleTitle: "你的手機正在偷走你的人生",
    sampleSubtitle: "奪回深度專注力的 21 天計畫",
    sampleProse: "你在中午前已查看手機 47 次。不是因為你缺乏自律——而是因為螢幕上的每個 App，都是由一群博士組成的團隊精心設計，專門劫持你的多巴胺系統。",
    sampleExercise: "90 分鐘專注模式：設定一個計時器，選定一項任務，手機放到另一個房間。計時器響起時就完成——即使不完美也好，直接交出去。",
    coverColors: ["#d97706", "#f59e0b", "#fef3c7"],
    emotions: ["掌控感", "頭腦清晰", "充滿活力", "自信", "有韌性"],
    visionVibe: "在這個世界裡，清晰是一種武器。行動勝過反思。讀者穿透資訊超載，建立不依賴意志力也能運作的系統。",
  },
  {
    id: "spiritual_awakening", name: "鳳凰涅槃",
    tagline: "舊我必須死去，真我才能重生",
    icon: Flame, gradient: "from-purple-500 to-violet-600",
    bg: "bg-gradient-to-br from-purple-50 to-violet-50",
    accent: "text-purple-600", border: "border-purple-200", activeBorder: "border-purple-500",
    tags: ["覺醒", "意義", "目標"],
    coverStyle: "神聖幾何、宇宙漸層、金色點綴",
    proseStyle: "沉思、層次豐富、詩意",
    videoStyle: "電影感自然場景、宇宙意象、儀式性動作",
    sampleTitle: "思緒之間的靜默，就是神聖",
    sampleSubtitle: "獻給試過一切、卻已放棄的人的冥想",
    sampleProse: "你讀過那些書，下載了那些 App，坐在蒲團上等待某種感應。什麼都沒有發生——除了採購清單不請自來地出現在腦海裡。",
    sampleExercise: "間隙練習：閉上眼睛，深吸一口氣。在吸氣的頂端、還未吐氣之前——感受那個間隙。停留在那裡。那就是入口。",
    coverColors: ["#7c3aed", "#a78bfa", "#ede9fe"],
    emotions: ["活在當下", "與目標相連", "腳踏實地", "釋放", "充滿希望"],
    visionVibe: "在這個世界裡，神聖棲居於日常之中。寂靜不是空洞，而是光亮的。讀者發現，他們一直在追尋的，其實也一直在追尋著他們。",
  },
];

const PERSONAS = [
  { id: "burned_out_pro", label: "倦怠職場人", emoji: "💼", desc: "精疲力竭、麻木、靠殘存動力硬撐", needs: "重啟、緩解、允許自己停下", impact: "內容切入「週日恐懼症」與職場身心俱疲的共鳴敘事" },
  { id: "gen_z_seeker", label: "Gen Z 探索者", emoji: "🧭", desc: "壓力過載、不斷比較、不停刷屏", needs: "方向、認可、真實可用的工具", impact: "以短影音為優先、TikTok 原生鉤子、反過度努力語調" },
  { id: "gen_alpha", label: "Gen Alpha 探索者", emoji: "🌱", desc: "在過度刺激中成長，早期具備情感覺察力", needs: "適齡工具、情感詞彙、安全引導", impact: "以視覺為主的漫畫格式、遊戲化練習、適合監護人審閱" },
  { id: "grief_carrier", label: "悲傷承載者", emoji: "🕯️", desc: "失去、麻木、無法言說", needs: "被見證、溫柔以待、無需「修復」", impact: "給予許可的語言、拒絕有毒正能量、溫和的行動呼籲" },
  { id: "anxious_achiever", label: "焦慮成就者", emoji: "⚡", desc: "外在成功，內在崩塌", needs: "神經系統支持、誠實面對", impact: "高效能框架搭配脆弱的後門入口" },
  { id: "spiritual_returner", label: "靈性回歸者", emoji: "🌅", desc: "試過一切，仍在尋找", needs: "深度、真實、拒絕空話", impact: "濃厚沉思散文、尊重傳統脈絡、反大師姿態" },
  { id: "new_parent", label: "疲憊新手父母", emoji: "👶", desc: "身分迷失、時間匱乏、充滿愧疚", needs: "快速工具、自我慈悲", impact: "以微格式為優先、無罪惡感框架、實用練習" },
];

const MOMENTS = [
  { id: "2am_overthinking", label: "凌晨 2 點 — 思緒停不下來", scene: "黑暗的房間、手機的光、飛速運轉的思緒", emoji: "🌙", hookStyle: "以輾轉難眠的身體感受開場，認可那種思緒旋渦，並提供一個立即可用的安定工具" },
  { id: "after_breakup", label: "分手或失去之後", scene: "空蕩蕩的公寓、寂靜、麻木", emoji: "💔", hookStyle: "為那種特定的悲傷命名——不是哀傷，而是麻木，那種食物失去味道的感受" },
  { id: "burnout_cant_quit", label: "倦怠卻無法停下", scene: "辦公室廁所、深呼吸、再次戴上面具", emoji: "🔥", hookStyle: "捕捉到他們重新戴上面具的那一刻，觸及公開表現與私下崩潰之間的鴻溝" },
  { id: "feeling_behind", label: "感覺落後於人生", scene: "滑著動態，所有人都在贏，只有你卡在原地", emoji: "📱", hookStyle: "鎖定比較式滑手機的行為，將「落後」重新定義為一種建構，把手機轉化為觸發物" },
  { id: "panic_spike", label: "恐慌發作 / 焦慮驟升", scene: "胸口緊繃、呼吸困難、世界在縮小", emoji: "😰", hookStyle: "身體感受優先的語言，在情緒之前先命名身體感覺，立即提供身體介入工具" },
  { id: "sunday_dread", label: "週日夜晚的週一焦慮", scene: "坐在沙發上、時鐘滴答、胃往下沉", emoji: "⏰", hookStyle: "觸及每週循環的預期焦慮，認可那種往下沉的感受，將週日重新定義為奪回自我的時刻" },
];

const TRADITIONS = [
  "禪宗佛教", "蘇菲神秘主義", "吠檀多", "金剛乘佛教", "道教",
  "斯多葛主義", "佛教心理學", "軀體治療", "多迷走神經理論",
  "默觀基督教", "原住民智慧", "世俗正念",
  "呼吸科學", "深度心理學"
];

const VOICE_SLIDERS = [
  { id: "gentleDirect", left: "溫柔", right: "直接", default: 50, color: "#6366f1", desc: "控制句子的柔和度——給予許可的語言 vs. 命令式指令" },
  { id: "simpleDeep", left: "簡單明瞭", right: "深刻", default: 50, color: "#059669", desc: "控制詞彙密度、隱喻層次與概念複雜度" },
  { id: "emotionalLogical", left: "情感豐富", right: "邏輯清晰", default: 25, color: "#f43f5e", desc: "控制故事與數據的比例、脆弱程度與分析框架" },
  { id: "spiritualPractical", left: "靈性", right: "實用", default: 50, color: "#7c3aed", desc: "控制傳統引用、神聖語言，以及工具優先 vs. 意義優先" },
];

const VISUAL_STYLES = [
  {
    id: "calm_minimal", label: "平靜 / 極簡", desc: "乾淨、通透、大量留白",
    palette: ["#f8fafc", "#e2e8f0", "#94a3b8", "#475569"], mood: "寧靜、開闊、可呼吸",
    imagePrompt: "Minimalist book cover with vast white space, single delicate ink wash element floating in center, soft grey gradient background, thin sans-serif typography, Japanese zen aesthetic, editorial photography style, muted tones, clean geometric border",
    emotionPrompt: "Abstract soft watercolor wash in pale blue and white, single drop of color expanding outward in calm ripples, zen garden raked sand pattern, misty morning light, feeling of deep exhale and release",
  },
  {
    id: "dark_intense", label: "深沉 / 強烈", desc: "情緒感、高對比、戲劇化",
    palette: ["#1e1b4b", "#312e81", "#6366f1", "#c7d2fe"], mood: "有力、沉浸、電影感",
    imagePrompt: "Dramatic book cover with deep indigo and black, single shaft of violet light cutting through darkness, bold condensed typography, cinematic film grain, high contrast, moody atmospheric fog, Blade Runner color palette",
    emotionPrompt: "Person standing at edge of cliff at night, lightning illuminating the scene, dramatic cloud formations, deep indigo sky with electric violet lightning bolts, feeling of breakthrough power and transformation",
  },
  {
    id: "earthy_organic", label: "大地 / 有機", desc: "自然紋理、溫暖色調",
    palette: ["#fef3c7", "#d97706", "#92400e", "#451a03"], mood: "踏實、溫暖、有質感",
    imagePrompt: "Book cover with handmade paper texture, warm amber and brown tones, dried botanical pressed flowers, hand-lettered serif typography, golden hour light, natural linen texture background, artisan craft aesthetic",
    emotionPrompt: "Hands cupping warm soil with a seedling sprouting, golden sunlight filtering through oak leaves, warm terracotta and amber palette, feeling of rootedness and connection to earth, morning garden dew",
  },
  {
    id: "bold_modern", label: "大膽 / 現代", desc: "銳利排版、幾何構成",
    palette: ["#fafafa", "#18181b", "#ef4444", "#fbbf24"], mood: "活力、果斷、醒目",
    imagePrompt: "Bold book cover with stark black and white contrast, oversized helvetica bold typography, single red geometric accent shape, Swiss design grid layout, Bauhaus influence, high energy, magazine editorial style",
    emotionPrompt: "Abstract geometric explosion of red and yellow shapes on white background, sharp angular forms radiating outward, feeling of decisive action and clarity, kinetic energy frozen in motion",
  },
  {
    id: "premium_soft",
    label: "高級 / 幾何",
    desc: "精緻、精準、高端定位",
    palette: ["#fdf4ff", "#d8b4fe", "#7e22ce", "#3b0764"],
    mood: "昇華、幾何、永恆",
    imagePrompt:
      "Premium luxury nonfiction book cover with precise geometric layout, thin elegant serif or restrained sans typography, subtle gold line or foil accent, controlled lavender and deep purple planes, editorial grid discipline, aspirational transformation",
    emotionPrompt:
      "Architectural light on refined surfaces, crisp geometric shadows, sense of order and quiet authority, timeless high-end publishing mood",
  },
  {
    id: "sacred_cosmic",
    label: "神秘 / 深邃",
    desc: "氛圍感、沉思性、微光流轉",
    palette: ["#0f172a", "#7c3aed", "#f59e0b", "#fef3c7"], mood: "引人、開闊、仍具商業感",
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
  "終於平靜": "/onboarding/proof/wizard/emotion_finally_calm.png",
  "在身體裡感到安全": "/onboarding/proof/wizard/emotion_safe_in_body.png",
  "允許自己休息": "/onboarding/proof/wizard/emotion_permission_rest.png",
  "頭腦清晰": "/onboarding/proof/wizard/emotion_clear_headed.png",
  "掌控感": "/onboarding/proof/wizard/emotion_in_control.png",
  "與目標相連": "/onboarding/proof/wizard/emotion_connected_purpose.png",
  "充滿活力": "/onboarding/proof/wizard/emotion_energized.png",
  "自信": "/onboarding/proof/wizard/emotion_confident.png",
  "有韌性": "/onboarding/proof/wizard/emotion_resilient.png",
  "釋放": "/onboarding/proof/wizard/emotion_released.png",
  "被寬恕": "/onboarding/proof/wizard/emotion_forgiven.png",
  "不再孤單": "/onboarding/proof/wizard/emotion_less_alone.png",
  "腳踏實地": "/onboarding/proof/wizard/emotion_grounded.png",
  "充滿希望": "/onboarding/proof/wizard/emotion_hopeful.png",
  "活在當下": "/onboarding/proof/wizard/emotion_present.png",
};

const TOPIC_TAG_PROOF_URL = Object.fromEntries(
  [
    "anxiety-at-night",
    "過度思考",
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
    keywords: ["nervous system regulation audiobook", "燃盡後的復原", "stop overthinking at night", "anxiety before sleep", "polyvagal calm"],
  },
  identity_direction: {
    personas: ["Gen Z navigating adulting 18-24 (fastest-growing segment)", "Millennial women career transition 30-44", "Identity rebuilders post-divorce 28-50"],
    topics: ["feeling behind compared to peers", "lost sense of purpose after 30", "quarter-life crisis", "rebuilding identity after breakup", "what to do with your life"],
    keywords: ["feeling lost in life audiobook", "四分之一人生危機", "finding purpose", "identity crisis self help", "what am I doing with my life"],
  },
  emotional_healing: {
    personas: ["Grief/loss navigators all ages ($70-100M/yr)", "Trauma-aware millennials body-based recovery", "Parents processing intergenerational patterns"],
    topics: ["grief that doesn't follow a timeline", "healing after toxic relationship", "跨世代創傷", "心碎後的復原", "情感麻木"],
    keywords: ["grief audiobook", "healing after breakup", "trauma recovery self help", "emotional healing", "letting go of past"],
  },
  performance_focus: {
    personas: ["Corporate middle managers 32-50 ($50-80M/yr)", "Entrepreneurs/solopreneurs 28-50 ($60-100M/yr)", "Tech workers seeking focus 25-40"],
    topics: ["phone addiction destroying focus", "can't stick to habits", "decision fatigue as a manager", "ADHD-friendly productivity", "多巴胺排毒"],
    keywords: ["focus audiobook", "productivity self help", "習慣養成", "ADHD focus techniques", "deep work practice"],
  },
  spiritual_awakening: {
    personas: ["Gen X wisdom seekers 45-58 ($165M/yr highest-spending)", "Contemplative professionals seeking meaning", "Post-crisis seekers finding new framework"],
    topics: ["meditation that actually works for beginners", "finding meaning after loss", "spiritual practice without religion", "inner peace in chaos", "mindfulness for skeptics"],
    keywords: ["meditation audiobook", "finding inner peace", "spiritual growth", "mindfulness for beginners", "meaning of life self help"],
  },
};

// V4 Angles
const V4_ANGLES = [
  { id: "debunk", label: "破除迷思", desc: "挑戰主流建議——「你的治療師不會告訴你的事」", framing: "反直覺鉤子，以佐證為支撐的轉折", icon: AlertTriangle },
  { id: "framework", label: "框架體系", desc: "給他們一套系統——「……的五步驟實踐方法」", framing: "有結構、可重複、工具優先", icon: Layers },
  { id: "reveal", label: "揭曉", desc: "揭露隱藏真相——「你睡不著的真正原因」", framing: "內行知識，「這件事沒有人說」", icon: Eye },
  { id: "leverage", label: "槓桿借力", desc: "善用他們已有的——「你的焦慮是超能力」", framing: "將既有特質重新定義為優勢", icon: Zap },
  { id: "origin", label: "溯源起點", desc: "追溯根源——「你的模式究竟從哪裡開始」", framing: "敘事深度、因果鏈、「啊哈時刻」", icon: Search },
];

// V4 Formats
const V4_FORMATS_STRUCTURAL = [
  { id: "F001", label: "標準自我成長", chapters: "12-16", tier: "full", desc: "經典敘事弧線，穿插練習" },
  { id: "F002", label: "引導式課程", chapters: "8-12", tier: "full", desc: "逐步蛻變方案" },
  { id: "F003", label: "每日日誌", chapters: "30-90", tier: "micro", desc: "每天一頁，以反思為主" },
  { id: "F004", label: "身體感知練習本", chapters: "10-14", tier: "full", desc: "身體優先的練習，敘事極簡" },
  { id: "F005", label: "敘事旅程", chapters: "14-20", tier: "full", desc: "以故事驅動、深度情感弧線" },
  { id: "F006", label: "精萃智慧", chapters: "6-8", tier: "mini", desc: "濃縮、高衝擊力、短篇閱讀" },
];

// ═══════════════════════════════════════════════════════════
// VOICE TONE DATA — 10 positions per slider with benefits
// ═══════════════════════════════════════════════════════════

const VOICE_TONE_10 = {
  gentleDirect: [
    {
      position: 1, label: "極度溫柔",
      technique: "以「您可能會注意到⋯⋯」開場——從不下命令，只是陪伴讀者一同觀察",
      benefits: [
        "Creates immediate psychological safety — reader's nervous system downregulates on first page",
        "Disarms shame and self-criticism that blocks receptivity to new ideas",
        "Readers who've been told 'just try harder' finally feel seen instead of lectured",
        "Builds trust with trauma-aware audiences who distrust authority-tone content",
        "Reduces book abandonment — gentle entry keeps anxious readers turning pages",
      ],
    },
    {
      position: 2, label: "非常溫柔",
      technique: "使用許可性語言：「這樣是可以的⋯⋯」與「您有權利⋯⋯」",
      benefits: [
        "Gives explicit permission to feel — many readers have never received this",
        "Counteracts internalized 'suck it up' messaging from family or culture",
        "Emotionally overwhelmed readers feel validated rather than pathologized",
        "Creates a sense of being parented well — meeting an unmet developmental need",
        "Reduces the shame spiral that prevents readers from doing the exercises",
      ],
    },
    {
      position: 3, label: "溫柔",
      technique: "練習以邀請方式呈現，而非指令——「如果您願意，可以試試⋯⋯」",
      benefits: [
        "Respects reader autonomy — they choose to engage rather than being told to",
        "People with control-related trauma can participate without triggering resistance",
        "更高的練習完成率——邀請的方式比命令更讓人感到安全",
        "Builds intrinsic motivation rather than compliance-based engagement",
        "Reader feels like a collaborator, not a patient — preserves dignity",
      ],
    },
    {
      position: 4, label: "柔和",
      technique: "較慢的句子節奏，刻意留有停頓，配合呼吸的緩慢步調",
      benefits: [
        "Reading pace mirrors meditation — the book itself becomes a calming practice",
        "Anxious readers' heart rate actually slows when prose rhythm is paced",
        "Creates space for emotional processing between concepts",
        "有聲書版本在恐慌時刻可作為情緒降溫的工具",
        "Readers report feeling 'held' by the writing — attachment need met through text",
      ],
    },
    {
      position: 5, label: "平衡偏溫柔",
      technique: "先給予肯定，再給予方向——先承認感受，再提供前進之路",
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
      technique: "溫暖而直接地陳述真相——「這就是實際上正在發生的事」",
      benefits: [
        "Readers get the 'real talk' they crave without feeling attacked",
        "Builds authority — readers trust a voice that tells them the truth kindly",
        "Works for both self-help newcomers and experienced personal-development readers",
        "Strong TikTok clip potential — direct truth cuts through scroll noise",
        "Creates quotable moments readers screenshot and share",
      ],
    },
    {
      position: 7, label: "堅定",
      technique: "行動優先的句子——先說要做什麼，之後再解釋原因",
      benefits: [
        "Overwhelmed readers need fewer decisions — clear direction reduces cognitive load",
        "Performance-oriented readers respond to efficiency and structure",
        "更高的行動轉化率——讀者真正去做練習，而不只是閱讀關於練習的內容",
        "Creates a sense of being coached by someone who knows what they're doing",
        "Stronger titles and hooks for ad copy — direct language converts better",
      ],
    },
    {
      position: 8, label: "直接",
      technique: "簡短有力的句子。沒有贅詞。每個字都必須有其價值。",
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
      technique: "對峙式的誠實——「您早已知道這件事。您只是在逃避。」",
      benefits: [
        "Breaks through denial — some readers need to be challenged, not comforted",
        "High-achiever audience respects the courage to say what others won't",
        "Creates 'I feel called out' moments that drive word-of-mouth sharing",
        "Differentiates from the soft-tone self-help market — stands out on shelves",
        "Builds fierce loyalty — readers who connect with this voice become evangelists",
      ],
    },
    {
      position: 10, label: "極度直接",
      technique: "命令式語氣——「停止閱讀。現在就去做。做完再回來。」",
      benefits: [
        "Maximum behavior change — no ambiguity about what the reader should do",
        "Creates drill-sergeant loyalty in readers who respond to structure",
        "有聲書版本可作為即時教練課程使用",
        "Content repurposes perfectly into course modules and challenge formats",
        "Readers complete entire programs — the commanding voice maintains momentum",
      ],
    },
  ],
  simpleDeep: [
    {
      position: 1, label: "極度簡單明瞭",
      technique: "小學五年級的閱讀程度——每個句子都清晰透徹，零專業術語",
      benefits: [
        "Accessible to ESL readers — opens international markets dramatically",
        "Gen Alpha and young Gen Z can engage without barrier",
        "Readers in emotional crisis can absorb content when cognition is impaired",
        "Widest possible market reach — no educational prerequisite",
        "有聲書的理解程度最高——聽眾無需倒帶重聽",
      ],
    },
    {
      position: 2, label: "非常簡單明瞭",
      technique: "每段一個概念——以小而清晰的段落逐步建立理解",
      benefits: [
        "ADHD readers can follow without losing the thread",
        "Each paragraph is a complete, usable unit — easy to highlight and save",
        "Works perfectly as TikTok carousel content — one slide per concept",
        "Readers feel smart and capable rather than intimidated",
        "更高的練習完成率——指示說明清晰到不可能產生誤解",
      ],
    },
    {
      position: 3, label: "簡單明瞭",
      technique: "日常生活的比喻——「就像清除瀏覽器的所有分頁」",
      benefits: [
        "Abstract concepts land instantly through familiar reference points",
        "Readers explain ideas to friends using your metaphors — organic word-of-mouth",
        "Creates 'aha moments' without requiring background knowledge",
        "Content is meme-able and shareable on social platforms",
        "Bridge between clinical concepts and lived experience",
      ],
    },
    {
      position: 4, label: "易於親近",
      technique: "清晰的說明與適度的深度——每章引入一個新概念",
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
      technique: "平易近人的語言與較豐富的概念並用——以「簡單來說」作為橋梁",
      benefits: [
        "Serves the widest range of educational backgrounds",
        "Book clubs can discuss at multiple levels — everyone finds something",
        "轉場在有聲書中效果良好——朗讀者能夠傳遞深度轉換的訊號",
        "Strong review potential — readers feel both comforted and challenged",
        "Longest shelf life — doesn't feel too basic or too academic after rereading",
      ],
    },
    {
      position: 6, label: "深思熟慮",
      technique: "多句話的概念發展——先建立論點，再帶出洞見",
      benefits: [
        "Intellectually curious readers feel respected and engaged",
        "Creates page-turner quality — readers want to see where the idea goes",
        "Strong for series — later volumes can deepen without losing the audience",
        "Generates rich discussion material for therapy and group contexts",
        "Differentiates from shallow pop-psychology — earns premium pricing",
      ],
    },
    {
      position: 7, label: "豐富",
      technique: "多層次的意義——表面閱讀有效，重讀則能發現更多",
      benefits: [
        "Books become reference texts readers return to — longer customer lifetime value",
        "Creates intellectual community — fans discuss hidden layers online",
        "有聲版本值得反覆聆聽——促進重複參與",
        "Attracts therapist and counselor audiences who recommend books to clients",
        "Content supports mastercourse format — enough depth for multi-week study",
      ],
    },
    {
      position: 8, label: "深刻",
      technique: "哲學與科學交織——引用研究但不說教",
      benefits: [
        "Positions author as genuine authority, not just a motivational speaker",
        "Attracts Gen X wisdom-seeker market — highest-spending demographic",
        "Strong for keynote and TEDx content — ideas are substantive enough for stage",
        "Creates books that therapists assign — institutional recommendation pipeline",
        "Long-tail SEO potential — niche depth owns specific search territories",
      ],
    },
    {
      position: 9, label: "非常深刻",
      technique: "跨領域的整合——連結神經科學、哲學與實踐",
      benefits: [
        "Creates 'the book that changed my life' reactions — viral review potential",
        "Thought-leader positioning — author becomes known for original frameworks",
        "Academic and clinical citation potential — extends reach beyond consumer market",
        "高端有聲書定價具備正當性——內容足夠扎實，適合長篇有聲格式",
        "International translation appeal — depth translates better than colloquialisms",
      ],
    },
    {
      position: 10, label: "極度深刻",
      technique: "研究所程度的概念、原創框架，挑戰讀者持續成長",
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
      position: 1, label: "極度情感豐富",
      technique: "以故事開篇——每個概念都透過親身經歷的敘事呈現",
      benefits: [
        "Mirror neurons activate — reader physically feels what characters feel",
        "Emotional memory encoding — readers remember content 6x longer than facts alone",
        "Creates the 'I cried reading this' reviews that drive viral sharing",
        "Deeply cathartic for readers carrying unprocessed emotion",
        "有聲書版本成為一位陪伴者——聽眾與朗讀者形成了一種擬社交的連結",
      ],
    },
    {
      position: 2, label: "非常情感豐富",
      technique: "高度的脆弱性——作者自身的傷痛清晰可見於文字之中",
      benefits: [
        "Readers feel less alone — 'someone else has been through this' is profoundly healing",
        "Dismantles the 'expert on a pedestal' barrier that blocks real connection",
        "Creates intense word-of-mouth — readers personally recommend to friends in crisis",
        "Strong podcast interview content — vulnerable stories captivate audiences",
        "Builds fierce community — readers bond with each other through shared emotional resonance",
      ],
    },
    {
      position: 3, label: "情感豐富",
      technique: "練習包含日記書寫與身體感知的工作——「注意內在升起了什麼」",
      benefits: [
        "Develops reader's emotional intelligence — a lifelong skill beyond the book",
        "Somatic awareness exercises create real physiological change, not just insight",
        "Especially transformative for men and high-performers who've been cut off from feeling",
        "Creates a practice the reader continues after the book — ongoing engagement",
        "Strong workbook companion potential — emotional exercises adapt to journal format",
      ],
    },
    {
      position: 4, label: "溫暖",
      technique: "以「您」稱呼讀者，語氣親密——如同親密好友寫來的信",
      benefits: [
        "Attachment theory activation — reader feels securely 'held' by the text",
        "Reduces defensiveness — intimate tone bypasses intellectual resistance",
        "Highest read-through rates — readers don't want the 'conversation' to end",
        "有聲書感覺像一場私人心理諮詢——建立深層的個人連結",
        "Strong for grief and healing topics where clinical distance would feel cold",
      ],
    },
    {
      position: 5, label: "平衡",
      technique: "情感開場、邏輯主體、整合收尾——每章都是一段旅程",
      benefits: [
        "Both heart and head readers feel served in every chapter",
        "Creates the most balanced reviews — 'moving AND practical' is the gold standard",
        "Works across all platforms — emotional hooks for social, logical depth for books",
        "Couples and friends with different styles can both love the same book",
        "跨族群吸引力最強——沒有任何一種讀者類型被排除在外",
      ],
    },
    {
      position: 6, label: "理性分析",
      technique: "有實證支持的故事敘述——故事用來詮釋數據，而非相反",
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
      technique: "結構性論證——主張、證據、意涵、行動",
      benefits: [
        "Engineering and tech-industry readers finally find self-help they respect",
        "Creates clear, quotable frameworks that get shared in professional contexts",
        "Strong LinkedIn and professional social media clip potential",
        "Supports course and certification format — logical progression is built in",
        "更高的感知價值——讀者感覺獲得的是工具，而不只是安慰",
      ],
    },
    {
      position: 8, label: "邏輯清晰",
      technique: "數據優先的章節——數字、研究與指標為每個主張提供依據",
      benefits: [
        "Positions brand in the 'evidence-based' category — premium market positioning",
        "Readers use the data to convince friends and family — built-in evangelism tool",
        "Strong for corporate book-club adoption — 'this isn't woo-woo' positioning",
        "Creates excerpt content for health and science publications",
        "Male-skewing audience finally engages with emotional topics through logic door",
      ],
    },
    {
      position: 9, label: "非常邏輯清晰",
      technique: "將讀者視為有能力的決策者——以有智慧的成年人的方式對待",
      benefits: [
        "Respects reader's intelligence — builds loyalty through trust in their capacity",
        "Creates 'I recommend this to my smartest friends' word-of-mouth",
        "Strong for executive and leadership markets where emotional language feels weak",
        "內容可轉化為主題演講——邏輯性的結構在舞台上表現出色",
        "Academic review potential — substantive enough to be cited in research",
      ],
    },
    {
      position: 10, label: "極度邏輯清晰",
      technique: "轉化被框架為系統性技能的習得，並有可衡量的成果",
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
      position: 1, label: "極度靈性",
      technique: "貫穿全文引用各種傳統、傳承與神聖導師",
      benefits: [
        "Readers seeking meaning find it — existential anxiety addressed at the root",
        "Creates a sense of belonging to something ancient and larger than oneself",
        "Attracts the highest-spending demographic — Gen X wisdom seekers ($165M/yr)",
        "Book becomes a spiritual companion — readers keep it on nightstands for years",
        "Strong retreat and workshop tie-in — spiritual content creates immersive events",
      ],
    },
    {
      position: 2, label: "非常靈性",
      technique: "神聖性語言：「臨在」、「覺察」、「見證者」、「偉大的轉化」",
      benefits: [
        "Creates transcendent reading experiences — readers report feeling 'transported'",
        "Poetry of language itself becomes healing — beauty as medicine",
        "有聲書版本可作為引導式冥想使用——一份內容，兩種用途",
        "Strong international appeal — spiritual language translates across cultures",
        "Builds devoted following — spiritual readers are the most loyal audience segment",
      ],
    },
    {
      position: 3, label: "靈性",
      technique: "練習包含冥想、靜觀與以靜默為基礎的修行",
      benefits: [
        "Develops reader's capacity for stillness — counterbalances digital overstimulation",
        "Meditation-based exercises create measurable neurological benefits",
        "Creates daily practice that extends engagement far beyond reading the book",
        "Strong for Gen Alpha — meditation skills are increasingly taught in schools",
        "Retreat-center and yoga-studio recommendation pipeline — institutional distribution",
      ],
    },
    {
      position: 4, label: "意義優先",
      technique: "意義的建立是主要目標——直接探討「我為何在此？」",
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
      technique: "內在轉化與外在行動相連——靜觀與執行相遇",
      benefits: [
        "Serves both spiritual seekers and practical doers in one book",
        "Creates the 'woo-meets-science' positioning that dominates bestseller lists",
        "Both meditation-loving and productivity-loving readers find their entry point",
        "口碑傳播潛力最強——跨越不同朋友圈互相推薦",
        "Platform flexibility — works for podcasts, courses, retreats, AND workshops",
      ],
    },
    {
      position: 6, label: "腳踏實地",
      technique: "靈性洞見轉化為日常習慣與生活常規",
      benefits: [
        "Wisdom becomes usable — reader can start today, not 'when they're ready'",
        "Appeals to 'spiritual but practical' — the fastest-growing reader segment",
        "Creates content that works as 7-day challenges and 30-day programs",
        "Strong for social media — habit content performs exceptionally on all platforms",
        "Bridges the gap between self-help and spirituality sections in bookstores",
      ],
    },
    {
      position: 7, label: "應用導向",
      technique: "以工具開篇——這是技巧，這是使用時機，這是它的運作原理",
      benefits: [
        "Readers take immediate action — exercises feel doable, not abstract",
        "Strong for pocket-guide format — tools are reference-able and compact",
        "Creates the 'I actually did the exercises' reviews that drive sales",
        "Corporate wellness programs adopt tool-based content more readily",
        "更高的練習完成率——實用性的框架降低了阻力",
      ],
    },
    {
      position: 8, label: "實用",
      technique: "功能性語言：「系統」、「規程」、「技巧」——零傳統參照",
      benefits: [
        "Opens the secular wellness market — readers who avoid 'spiritual' labels",
        "Strong for healthcare referrals — clinical professionals recommend secular content",
        "Creates content that works in corporate and educational institutional settings",
        "Appeals to science-minded readers who want results without metaphysics",
        "TikTok and YouTube performance highest — practical content has broadest appeal",
      ],
    },
    {
      position: 9, label: "非常實用",
      technique: "行為改變是主要目標——追蹤可衡量的成果",
      benefits: [
        "Readers can prove the book worked — drives reviews with specific results",
        "Creates before/after narratives perfect for marketing and testimonials",
        "Strong for employer-sponsored wellness — ROI can be demonstrated",
        "App and digital product integration natural — tracking is built into the approach",
        "Health insurance and benefits platform partnerships become possible",
      ],
    },
    {
      position: 10, label: "極度實用",
      technique: "純粹的規程——可付諸行動並有可衡量的成果，每章都是一套待安裝的系統",
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
  const isComplete = step === total - 2; // step 7 ("藍圖") only
  const pct = isComplete ? 100 : ((step + 1) / total) * 100;
  return (
    <div className="brand-studio-panel mb-6 px-5 py-4 sm:mb-8">
      {isComplete && (
        <p className="text-center text-3xl font-extrabold mb-3" style={{ color: '#d97706', fontFamily: 'Cormorant Garamond, serif' }}>
          {t("ui", "恭喜——您的品牌已 100% 設定完成！")}
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
  const labels = ["感受", "思考", "Do", "分享", "信任", "回歸"];
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
      systemEffect: "在所有書目中，將文字設定為具有呼吸意識的節奏、身體性練習，以及調節優先的結構",
      emotionalBenefit: "您的讀者從第一段開始，神經系統就開始向下調節。內容作為一種共同調節工具——降低皮質醇、減緩心率，並給予休息的許可。讀者表示，感覺自己被文字本身「接住了」。",
    },
    identity_direction: {
      systemEffect: "啟用向前推進的文字風格、誠實自我審視的練習，以及反比較的吸引策略",
      emotionalBenefit: "讀者停止漫無目的地滑動，開始主動做選擇。這將「我不知道自己在做什麼」的癱瘓感轉化為動能。每一章都透過微小而勇敢的決定重建身份認同——抵抗那種落後於人的羞恥感。",
    },
    emotional_healing: {
      systemEffect: "啟用溫柔優先的語言、以見證為基礎的練習，以及具有悲傷識讀能力的內容節奏",
      emotionalBenefit: "讀者感到被看見，而非被修復。這以臨在來回應悲傷與痛苦——沒有有毒的正面思考，沒有時間表，沒有「您應該已經走出來了」。它填補了許多讀者從未擁有過的慈悲見證者的角色。",
    },
    performance_focus: {
      systemEffect: "運用行動優先的文字、以規程為基礎的練習，以及切除噪音的吸引策略",
      emotionalBenefit: "讀者穿透資訊過載，在數週以來第一次採取真實的行動。這降低了決策疲勞，建立以結構而非意志力運作的系統，並恢復掌控感。",
    },
    spiritual_awakening: {
      systemEffect: "啟用多層次的靜觀文字、落差覺察練習，以及尋求意義的吸引策略",
      emotionalBenefit: "讀者發現，他們一直在追尋的，其實早已存在於自身之內。這在一個充斥表面的世界中，為深度創造了空間——在知識化的自助書籍無法觸及之處，遇見靈性的追尋者。",
    },
  },
  personas: {
    burned_out_pro: { systemEffect: "圍繞疲憊耗盡的吸引點、「週日恐懼」的敘事，以及「不放棄也能復原」的框架來調整書名", emotionalBenefit: "內容觸及處於生存模式的人——沒有罪惡感，沒有「再努力一點就好」。您的品牌成為第一個說出「您不是懶惰，您是耗盡了」並且真心如此的聲音。" },
    gen_z_seeker: { systemEffect: "針對短篇吸引開頭、TikTok 原生語言、反過度努力的語調，以及讓人停止滑動的開場方式進行優化", emotionalBenefit: "您的品牌以 Z 世代的母語與他們相遇——真實性優先。在一片表演式身心健康的海洋中，您成為值得信賴的聲音，提供真實的工具，沒有令人尷尬的說教感。" },
    gen_alpha: { systemEffect: "啟用漫畫優先格式、視覺敘事、遊戲化練習，以及適合家長監護的內容過濾", emotionalBenefit: "您正在為有史以來第一個從童年就擁有情緒詞彙的世代建構內容。視覺格式給予他們父母那一代從未擁有的工具——符合年齡發展，且真正有幫助。" },
    grief_carrier: { systemEffect: "設定許可性語言、柔和的行動呼籲、零有毒正面思考，以及以見證為基礎的練習結構", emotionalBenefit: "您的品牌成為陪伴讀者度過那些無以名狀之悲傷的夥伴——那種沒有人事先告訴他們會遭遇的悲傷。沒有修復，沒有時間表。只有臨在，以及那份徹底許可自己「不必沒事」的空間。" },
    anxious_achiever: { systemEffect: "在高績效框架與脆弱性的後門之間搭橋，融入神經系統支持與冒牌者症候群的切入點", emotionalBenefit: "您觸及那些外表看似正常、內心卻正在崩潰的人。您的品牌在成就語言與脆弱性之間搭起橋樑——這是高成就者真正願意走進去的療癒後門。" },
    spiritual_returner: { systemEffect: "啟用深沉的靜觀文字風格、具備傳統意識的參照、反導師定位，以及深度優先的吸引策略", emotionalBenefit: "您的品牌與那些嘗試過一切、已被膚淺答案耗盡的人對話。厚實而真誠的內容，尊重他們的智識，也回應他們的深度。" },
    new_parent: { systemEffect: "優先安排微型格式的傳遞方式、零罪惡感的框架、快速工具練習，以及適合孩子午睡時長的內容", emotionalBenefit: "您的品牌在父母偷來的片刻中觸及他們——凌晨三點哺乳，孩子午睡時滑手機。零罪惡感的微型格式工具，幫助他們在不增加負擔的前提下，找回自我認同。" },
  },
  moments: {
    "2am_overthinking": { systemEffect: "以感官性語言開場，認可那種螺旋式下墜的感受，並在前三十秒內提供立即可用的接地工具", emotionalBenefit: "內容在讀者最脆弱的時刻捕捉住他們——躺在床上睡不著，手機螢幕發著光，腦袋停不下來。那個吸引人的開頭之所以奏效，是因為它描述的正是他們此刻身體上的真實感受。" },
    "after_breakup": { systemEffect: "點名那種特定的麻木感，避免給予建議，以對失去的身體性覺察作為引導", emotionalBenefit: "您在那種無人提起的麻木感中與他們相遇——不是那種會哭泣的，而是那種「食之無味」的麻木。您的品牌說出他們無法言說的，光是這樣，療癒便已開始。" },
    "burnout_cant_quit": { systemEffect: "捕捉重新戴上面具的那個時刻，與公眾自我和私下自我之間的落差對話，將復原框架為一種技能，而非奢侈品", emotionalBenefit: "您與那個在浴室鏡子前、重新戴上面具之前的時刻對話。內容認可了他們所表演的自我與真實自我之間的落差——允許他們停止假裝。" },
    "feeling_behind": { systemEffect: "針對比較式滑動行為，將「落後」重新框架為「建構中」，並將手機轉化為觸發意識的物件", emotionalBenefit: "您用真相打斷比較式的滑動習慣：他們並非落後，他們正在建構自己的人生。手機本身成為觸發物，將無意識的滑動轉化為誠實的自我省思。" },
    "panic_spike": { systemEffect: "身體感受優先的語言，在情緒之前先命名身體感覺，立即提供身體介入工具 within 10 seconds", emotionalBenefit: "在心智已無法運作的時刻，內容使用身體優先的語言。在恐慌發作時，身體需要先聽到「我看見你」，心智才能開始處理任何事情。這在真實的時刻，救助了真實的人。" },
    "sunday_dread": { systemEffect: "切入每週的焦慮循環，認可那種沉重的心情，將週日重新框架為自我找回的時刻，而非倒數計時。", emotionalBenefit: "您說出了數百萬人感受卻從未能言說的每週恐懼。您的品牌從焦慮中奪回週日——將那種沉重的心情轉化為準備與自我慈悲的儀式。" },
  },
  visualStyles: {
    calm_minimal: { systemEffect: "生成具有大面積留白、柔和水墨渲染、禪意美學與低彩度色調的封面", emotionalBenefit: "讀者感受到視覺上的紓解——留白傳遞「您可以在這裡呼吸」的訊號。封面在書還未翻開之前，就已像一次冥想。為過度刺激的讀者降低視覺焦慮。" },
    dark_intense: { systemEffect: "生成具有深靛藍／黑色調、戲劇性光影、電影質感顆粒感與高對比的封面", emotionalBenefit: "讀者感受到自身轉化的份量與重量。深色美學傳遞深度的訊號——這不是溫柔的身心健康，而是真實的功課。吸引那些不信任外表柔和的自助書籍的讀者。" },
    earthy_organic: { systemEffect: "生成具有手作質感、植物元素、溫暖琥珀色調與工藝美學的封面", emotionalBenefit: "讀者在讀到第一個字之前，已先感到穩定扎根。自然質感觸發親生命的平靜——大腦將有機視覺詮釋為「安全」。對身體性與自然療癒特別有力。" },
    bold_modern: { systemEffect: "生成具有強烈對比、超大字體、紅色幾何點綴與瑞士設計格線的封面", emotionalBenefit: "讀者感到充滿能量、果斷有力。大膽的視覺設計穿透書架上的噪音與滑動疲勞。傳遞「這個不一樣」的訊號——吸引那些已厭倦粉彩色系身心健康書籍的行動導向讀者。" },
    premium_soft: { systemEffect: "生成具有幾何結構、精確字體層次、金色點綴線條與節制奢華色調的封面", emotionalBenefit: "讀者感覺手中握著的是具有權威性與用心之作。幾何感的高端設計傳遞工藝與清晰的訊號——吸引那些希望轉化同時具備編輯公信力的讀者。" },
    sacred_cosmic: { systemEffect: "生成神秘氛圍感的封面——深藍與紫羅蘭色調、細膩的光線、靜觀的深度，但不帶恐怖感", emotionalBenefit: "讀者感受到好奇心與內在的擴展。神秘的視覺設計邀請深度追尋者，不帶過度奇幻的色彩——在書架與縮圖上都極具磁吸力。" },
  },
  formats: {
    manga: { systemEffect: "目錄規劃師優先安排插圖分格、短篇有聲書（十五至三十分鐘），以及跨所有平台的視覺敘事", emotionalBenefit: "視覺優先的讀者透過影像處理情感的速度比文字更快。漫畫降低了閱讀焦慮，能以 Z 世代和 Alpha 世代的母語方式與他們互動，並透過故事讓複雜的心理概念變得易於理解。" },
    book: { systemEffect: "目錄規劃師優先安排完整長度的敘事、深度課程、完整的練習冊，以及長篇有聲書（三至八小時）", emotionalBenefit: "深度閱讀者渴望沉浸——長篇形式給予他們放慢腳步、深入探索的許可。完整長度的書籍成為陪伴者，建立持續的專注力，推動持久的轉化。" },
  },
};

function SelectionFeedback({ systemEffect, emotionalBenefit, color = "#6366f1" }) {
  if (!systemEffect && !emotionalBenefit) return null;
  return (
    <div className="mt-4 rounded-xl border overflow-hidden" style={{ borderColor: color + '30' }}>
      <div className="px-4 py-2.5 flex items-center gap-2" style={{ backgroundColor: color + '08' }}>
        <Sparkles size={13} style={{ color }} />
        <span className="text-[11px] font-bold" style={{ color }}>這將啟動的內容</span>
      </div>
      <div className="px-4 py-3 bg-white">
        <div className="flex items-start gap-2 mb-2.5">
          <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: color + '15' }}>
            <Zap size={10} style={{ color }} />
          </div>
          <div>
            <div className="text-[9px] font-bold uppercase text-white mb-0.5">在系統中</div>
            <p className="text-[11px] text-white leading-relaxed">{systemEffect}</p>
          </div>
        </div>
        <div className="flex items-start gap-2">
          <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: color + '15' }}>
            <Heart size={10} style={{ color }} />
          </div>
          <div>
            <div className="text-[9px] font-bold uppercase text-white mb-0.5">對你的讀者</div>
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
        <span className="text-xs font-bold text-white">{label || "這會改變什麼"}</span>
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
        <p className="text-[10px] text-white font-semibold uppercase">{_t("ui", "品牌已定義")}</p>
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
            <span className="text-xs font-bold text-white">這將啟動的內容</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>系統效果：</strong> {_SF.archetypes[arch.id].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>讀者感受：</strong> {_SF.archetypes[arch.id].emotionalBenefit}</div>
        </div>
      )}
      {step === 1 && persona && _SF.personas[persona.id] && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-violet-500" />
            <span className="text-xs font-bold text-white">這將啟動的內容</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>系統效果：</strong> {_SF.personas[persona.id].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>讀者感受：</strong> {_SF.personas[persona.id].emotionalBenefit}</div>
        </div>
      )}
      {step === 1 && persona && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-1">讀者</div>
          <div className="flex items-center gap-2"><span className="text-lg">{persona.emoji}</span><div><div className="text-xs font-bold text-white">{persona.label}</div></div></div>
        </div>
      )}
      {step === 1 && persona && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-2">讀者輪廓</div>
          <div className="text-[10px] text-white leading-tight mb-1.5">{persona.desc}</div>
          <div className="text-[10px] text-white leading-tight mb-1.5"><strong>需求：</strong> {persona.needs}</div>
          <div className="text-[10px] text-white leading-tight"><strong>影響力：</strong> {persona.impact}</div>
        </div>
      )}
      {step === 2 && moment && _SF.moments[moment.id] && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-violet-500" />
            <span className="text-xs font-bold text-white">這將啟動的內容</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>系統效果：</strong> {_SF.moments[moment.id].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>讀者感受：</strong> {_SF.moments[moment.id].emotionalBenefit}</div>
        </div>
      )}
      {step >= 3 && Object.keys(state.voiceSettings || {}).length > 0 && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-2">語音輪廓</div>
          {VOICE_SLIDERS.map((s) => { const val = state.voiceSettings?.[s.id] ?? s.default; return (
            <div key={s.id} className="flex items-center gap-2 mb-1"><span className="text-[9px] text-white w-14">{s.left}</span><div className="flex-1 h-1.5 bg-gray-100 rounded-full"><div className="h-full bg-gray-700 rounded-full transition-all" style={{ width: `${val}%` }} /></div><span className="text-[9px] text-white w-14 text-right">{s.right}</span></div>
          ); })}
        </div>
      )}
      {step === 4 && visual && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-2">影響</div>
          <div className="flex gap-1.5 mb-1.5">{visual.palette.map((c, i) => <div key={i} className="w-8 h-8 rounded-lg shadow-sm" style={{ backgroundColor: c }} />)}</div>
          <div className="text-[10px] text-white font-medium">{visual.label}</div>
        </div>
      )}
      {step === 4 && state.visualStyle && _SF.visualStyles[state.visualStyle] && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-violet-500" />
            <span className="text-xs font-bold text-white">這將啟動的內容</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>系統效果：</strong> {_SF.visualStyles[state.visualStyle].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>讀者感受：</strong> {_SF.visualStyles[state.visualStyle].emotionalBenefit}</div>
        </div>
      )}
      {step === 6 && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-3">
            <Compass size={14} className="text-indigo-500" />
            <span className="text-xs font-bold text-white">內容切角</span>
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
                    <p className="text-[9px] text-white/70 italic">選擇主題…</p>
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
            <span className="text-xs font-bold text-white">跳至章節</span>
          </div>
          <div className="space-y-0.5">
            {[
              { id: "rev-category", label: "真正類別", icon: "🎯" },
              { id: "rev-voice", label: "語音特質", icon: "🎙️" },
              { id: "rev-positioning", label: "定位圖", icon: "📍" },
              { id: "rev-visual", label: "視覺識別", icon: "🎨" },
              { id: "rev-emotion", label: "情感階梯", icon: "📈" },
              { id: "rev-topics", label: "主題策略", icon: "🗂️" },
              { id: "rev-engine", label: "內容引擎", icon: "⚙️" },
              { id: "rev-loop", label: "優勢迴圈", icon: "🔄" },
              { id: "rev-journey", label: "讀者旅程", icon: "🚶" },
              { id: "rev-synergy", label: "語音 × 主題", icon: "🔗" },
              { id: "rev-radar", label: "品牌力", icon: "📊" },
              { id: "rev-synthesis", label: "綜合", icon: "✨" },
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
            <span className="text-xs font-bold text-white">情感輪廓</span>
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
        eyebrow="基礎"
        title="選擇您的情感世界"
        subtitle="您的原型是讀者與您連結的感受——貫穿文字、封面、影片與社群。選擇最符合您希望展現樣貌的世界觀。"
        helper="每張卡片都包含一段簡短的願景，描述您的品牌邀請讀者進入的那個世界。"
      />
      <div className="mb-6 rounded-xl border border-indigo-100/80 bg-indigo-50/60 px-4 py-3 backdrop-blur-sm">
        <p className="text-xs font-medium text-indigo-900">{useTranslation().t("steps", "這是整個創作坊中最關鍵的選擇——其餘一切都建立在您在此選定的情感領域之上。")}</p>
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
        eyebrow="受眾"
        title="主要讀者"
        subtitle="每個強大的品牌都有一位主角——您首要服務的讀者。您的作品目錄仍然觸及每個族群；這個選擇優先塑造語音、封面與鉤子。"
      />
      <div className="mb-6 rounded-xl border border-blue-100/80 bg-blue-50/50 p-4 backdrop-blur-sm">
        <p className="text-xs leading-relaxed text-blue-900">
          {useTranslation().t("steps", "仍然觸及每一個人。 我們優先為這位讀者調整標題、包裝與練習，再跨您原型的其他族群進行調適。")}
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
        eyebrow="鉤子"
        title="他們伸手觸及您的那一刻"
        subtitle="選擇讀者最開放的那個場景——標題、封面與社群鉤子都由此延伸。"
      />
      <details open className="mb-5 rounded-xl border border-amber-100/90 bg-amber-50/40 px-4 py-2 text-xs text-amber-900 backdrop-blur-sm open:pb-3">
        <summary className="cursor-pointer font-semibold text-amber-900/90 outline-none">為什麼這很重要</summary>
        <p className="mt-2 leading-relaxed text-amber-900/85">
          {useTranslation().t("steps", "強大的品牌觸及某個時刻，而不僅僅是某個族群。這個選擇引導第一句話、封面承諾，以及讓人停下滑動的鉤子。")}
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
  const audioSrc = VOICE_AUDIO_SRC_TW;
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
        eyebrow="語音風格"
        title="塑造您的品牌語調"
        subtitle="四個滑桿——滑動並觀察圖表移動。每個軸向都改變每一句話的感受。"
      />
      <p className="mb-5 text-[11px] text-white">下一步將說明每個設定如何影響您的讀者體驗。</p>

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
                    <Play size={10} /> 收聽位置 {position}
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
        eyebrow="影響力"
        title="您的語調為讀者帶來什麼"
        subtitle="滑動後，若想深入了解，請展開下方的影響力說明。"
      />

      <div className="mb-6 rounded-2xl border border-violet-100 bg-violet-50/50 px-4 py-3">
        <p className="text-[10px] font-bold uppercase tracking-wider text-violet-800">旁白預覽</p>
        <p className="mt-1 text-[11px] leading-relaxed text-white">
          相同的舒緩段落，三種 Edge TTS 示範語音。對照上方滑桿聆聽配對效果。
        </p>
        <div className="mt-3 space-y-2">
          <div>
            <span className="text-[10px] font-semibold text-white">調節／平靜</span>
            <audio className="mt-1 block h-9 w-full" controls preload="metadata" src="/onboarding/audio/voice_cmp_comfort_voice_regulating_female.mp3" />
          </div>
          <div>
            <span className="text-[10px] font-semibold text-white">溫暖共情</span>
            <audio className="mt-1 block h-9 w-full" controls preload="metadata" src="/onboarding/audio/voice_cmp_comfort_voice_warm_male.mp3" />
          </div>
          <div>
            <span className="text-[10px] font-semibold text-white">直接／權威</span>
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
                  <summary className="cursor-pointer text-xs font-bold text-white outline-none">這對讀者的影響</summary>
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
        eyebrow="視覺與風格"
        title="視覺世界"
        subtitle="選擇讀者將與您品牌連結的視覺識別——封面、社群與影片均由此延伸。"
      />

      <div className="text-xs font-bold uppercase tracking-wider text-violet-600/90 mb-3">視覺風格</div>
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
  { name: "安全感與平靜", icon: "🛡️", color: "#6366f1", items: ["終於平靜", "在身體裡感到安全", "允許自己休息"], impacts: { "終於平靜": "讀者的神經系統進入平靜模式——停止戒備，開始真正吸收內容", "在身體裡感到安全": "從第一頁起建立身體層面的信任感，降低閱讀時的戰鬥或逃跑反應", "允許自己休息": "化解讓燃盡讀者無法接觸自我成長內容的罪惡感迴圈" } },
  { name: "清晰感與方向感", icon: "🧭", color: "#059669", items: ["頭腦清晰", "掌控感", "與目標相連"], impacts: { "頭腦清晰": "突破決策疲勞——讀者感受到迷霧散去，開始重新做選擇", "掌控感": "為那些感覺生活只是發生在自己身上、而非由自己主導的讀者，重建主體意識", "與目標相連": "填補「我該怎麼做」與「這為什麼重要」之間的鴻溝——讀者找到前進的動能" } },
  { name: "活力與自信", icon: "⚡", color: "#f59e0b", items: ["充滿活力", "自信", "有韌性"], impacts: { "充滿活力": "將被動的讀者轉化為行動者——合上書本，就開始行動", "自信": "重建被冒牌者症候群與比較文化侵蝕的自我信任", "有韌性": "讀者培養出復原力——挫折成為資料，而非身份標籤" } },
  { name: "釋放與療癒", icon: "🕊️", color: "#f43f5e", items: ["釋放", "被寬恕", "不再孤單"], impacts: { "釋放": "悲傷、怨恨與積壓的緊繃終於有了去處——讀者真正地呼出那口氣", "被寬恕": "自我慈悲取代內在批評者——讀者不再因為身為人類而懲罰自己", "不再孤單": "為說不出口的感受命名——讀者發現自己「奇怪」的痛苦其實是普遍的，打破孤立感" } },
  { name: "活在當下與希望", icon: "✨", color: "#7c3aed", items: ["腳踏實地", "充滿希望", "活在當下"], impacts: { "腳踏實地": "將讀者錨定在身體與當下——反芻思緒與對未來的焦慮失去了掌控力", "充滿希望": "重新點燃「改變是可能的」這份信念——這是自我成長領域最強大的轉化驅動力", "活在當下": "讀者不再活在悔恨或焦慮中，真正品味「活在當下」是什麼感覺" } },
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
        eyebrow="承諾"
        title="視覺"
        subtitle="這些是您的讀者帶走的感受——他們能說出口的蛻變。每個標題、CTA 與行銷訊息都指向這些承諾。"
      />
      <div className="mb-6 rounded-xl border border-rose-100/80 bg-rose-50/50 p-4 backdrop-blur-sm">
        <p className="text-xs leading-relaxed text-rose-900">
          <strong>每個類別選一個。</strong> 您的選擇成為整個品牌的情感北極星。封面以視覺呈現這些感受的承諾，標題為它們命名，練習讓它們實現。系統將您的選擇編織進每一件生成的內容中。
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
  { label: "睡眠與焦慮", icon: "😰", color: "#6366f1", tags: [
    { id: "anxiety-at-night", label: "夜間焦慮", angle: "framework", bullet: "提供入睡前的焦慮應對方案——3 個身體掃描練習，在皮質醇迴圈失控前加以中斷" },
    { id: "過度思考", label: "過度思考", angle: "origin", bullet: "將過度思考的模式追溯至童年的生存策略——你的大腦學會了掃描危險，而且從未停止" },
    { id: "panic-grounding", label: "恐慌接地", angle: "debunk", bullet: "破解「深呼吸就好」的迷思——恐慌需要先進行身體介入，認知工具是第二步" },
    { id: "sunday-dread", label: "週日恐懼", angle: "leverage", bullet: "將週日恐懼症重新定義為神經系統的每週預報——那份恐懼本身就包含了需要改變的線索" },
  ]},
  { label: "燃盡與工作", icon: "🔥", color: "#f59e0b", tags: [
    { id: "burnout-recovery", label: "職業倦怠恢復", angle: "debunk", bullet: "破解「去度個假就好」的迷思——燃盡是神經系統的狀態，不是行程安排的問題" },
    { id: "nervous-system-reset", label: "神經系統重置", angle: "framework", bullet: "提供以多重迷走神經理論為基礎的五天迷走神經調節方案——讀者可以立即跟著執行的結構" },
    { id: "decision-fatigue", label: "決策疲勞", angle: "reveal", bullet: "揭示決策疲勞與意志力無關——那是過載的前額葉皮質在運行過時的威脅偵測程式" },
    { id: "phone-addiction", label: "手機成癮", angle: "leverage", bullet: "將手機重新定義為生物回饋工具——你的滑動模式精確揭示了神經系統正在渴求什麼" },
  ]},
  { label: "悲傷與療癒", icon: "🕊️", color: "#f43f5e", tags: [
    { id: "grief-timeline", label: "悲傷時間線", angle: "debunk", bullet: "破解「悲傷五階段」模型——悲傷是非線性的，了解這一點能防止讀者將自己的療癒過程病理化" },
    { id: "toxic-relationship-healing", label: "有毒關係療癒", angle: "origin", bullet: "將吸引力模式追溯至早期依附創傷——理解源頭能打破重複的循環" },
    { id: "intergenerational-trauma", label: "代際創傷", angle: "reveal", bullet: "揭示創傷如何透過表觀遺傳學與家族沉默傳遞——讓讀者明白他們的痛苦不是「自己想太多」" },
    { id: "heartbreak-recovery", label: "心碎恢復", angle: "framework", bullet: "將復原分為三個階段：撐過去、穩定下來、重新建立——在心碎者感到迷失時給予一張地圖" },
    { id: "emotional-numbness", label: "情感麻木", angle: "leverage", bullet: "將麻木重新定義為神經系統最精密的保護機制——不是感受的缺席，而是感受的過載" },
  ]},
  { label: "身份認同與方向", icon: "🧭", color: "#059669", tags: [
    { id: "feeling-behind", label: "感覺落後", angle: "debunk", bullet: "破解比較時間軸——不存在「落後」，因為每個人都是在截然不同的基礎上建構自己的人生" },
    { id: "quarter-life-crisis", label: "四分之一人生危機", angle: "leverage", bullet: "將危機重新定義為身份系統的升級——那份不適正是你已超越舊版自我的證明" },
    { id: "identity-rebuild", label: "身份重建", angle: "framework", bullet: "提供四階段身份重建框架——從解構、整合到真實表達" },
    { id: "purpose-after-30", label: "30歲後的人生意義", angle: "origin", bullet: "將目標感的空洞追溯至繼承的職涯劇本——一旦看清你活在誰的夢想裡，你自己的夢想就會浮現" },
  ]},
  { label: "專注力與表現", icon: "⚡", color: "#0ea5e9", tags: [
    { id: "habit-building", label: "習慣養成", angle: "framework", bullet: "將習慣養成系統化為環境設計加身份轉換——即使動力消失，這套結構依然有效" },
    { id: "ADHD-productivity", label: "ADHD效率", angle: "leverage", bullet: "將 ADHD 的超專注力重新定義為策略優勢——你的大腦沒有問題，只是那些生產力建議根本不是為你設計的" },
    { id: "dopamine-detox", label: "多巴胺排毒", angle: "debunk", bullet: "破解爆紅的多巴胺排毒趨勢——真正的問題是獎勵敏感度，解方是重新校準，而非剝奪" },
    { id: "deep-work", label: "深度工作", angle: "reveal", bullet: "揭示焦慮型心智的深度工作，需要在每個工作區塊之間重整神經系統——不只是意志力和計時器" },
  ]},
  { label: "意義與靈性", icon: "✨", color: "#7c3aed", tags: [
    { id: "meditation-beginners", label: "冥想入門", angle: "debunk", bullet: "破解「清空你的思緒」——冥想是關於覺察念頭，而非消除它們。這個重新框架能防止初學者放棄" },
    { id: "meaning-after-loss", label: "失去後的意義", angle: "origin", bullet: "將意義建構追溯至人類對敘事連貫性的需求——當失落打碎了故事，重建意義就是療癒" },
    { id: "spiritual-no-religion", label: "無宗教靈性", angle: "leverage", bullet: "將靈性渴望重新定義為特質，而非缺口——你不需要借助他人的傳統，也能觸及深度與超越" },
    { id: "inner-peace-chaos", label: "混亂中的內心平靜", angle: "reveal", bullet: "揭示內心平靜不是混亂的消失，而是與混亂建立不同的關係——噪音不會停止，但你不再溺水" },
    { id: "mindfulness-skeptics", label: "對正念持懷疑態度者", angle: "framework", bullet: "提供對懷疑者友善的五分鐘練習，以神經科學數據為基礎——不需要香、不需要咒語，只有可量化的成果" },
  ]},
];

const ANGLE_FEEDBACK = {
  debunk: { label: "破除迷思", icon: "🔍", systemEffect: "標題以反直覺鉤子開場——「你的治療師不會告訴你的事。」", emotionalBenefit: "讀者感受到智識上的尊重，讓他們懷疑傳統建議行不通的直覺得到了驗證。" },
  framework: { label: "框架體系", icon: "🔧", systemEffect: "標題以結構引導——「……的五步驟方法」。可重複執行的系統。", emotionalBenefit: "不知所措的讀者看到清晰的系統時，終於能喘一口氣。將模糊的焦慮轉化為具體步驟。" },
  reveal: { label: "揭曉", icon: "💡", systemEffect: "標題揭露隱藏真相——「你睡不著的真正原因。」", emotionalBenefit: "讀者經歷「啊哈時刻」，將自我敘事從「我有問題」改寫為「我被理解了」。" },
  leverage: { label: "槓桿借力", icon: "🔄", systemEffect: "標題重新定義弱點——「你的焦慮是超能力。」", emotionalBenefit: "讀者停止與自己對抗。傳遞的訊息是：「你沒有問題，只是還沒學會善用自己的天賦。」" },
  origin: { label: "根源", icon: "🌱", systemEffect: "標題追溯根本原因——「你的模式究竟從哪裡開始。」", emotionalBenefit: "從理解模式的起源中獲得深層的釋懷感，對過去的自己升起慈悲心。" },
};

// ═══════════════════════════════════════════════════════════
// MARKET DATA — Visual Identity & Topic/Angle research scores
// ═══════════════════════════════════════════════════════════
const VISUAL_MARKET = {
  calm_minimal:      { shelf: 62, trust: 88, social: 70, premium: 78, rank: 5, demo: "30–55, F-lean", superpower: "獲得治療師與專業人士推薦——「公信力」的選擇" },
  dark_intense:      { shelf: 84, trust: 68, social: 85, premium: 80, rank: 3, demo: "22–38, neutral", superpower: "產生最多有機用戶生成內容——讀者將其作為身份訊號分享" },
  earthy_organic:    { shelf: 65, trust: 82, social: 74, premium: 68, rank: 6, demo: "28–50, F-strong", superpower: "建立最深層的準社交信任——讀者感覺作者是自己人" },
  bold_modern:       { shelf: 88, trust: 72, social: 82, premium: 75, rank: 1, demo: "25–40, neutral", superpower: "在任何書架或動態中突破視覺噪音——讓人停下滑動的冠軍" },
  premium_soft:      { shelf: 78, trust: 85, social: 76, premium: 92, rank: 2, demo: "30–50, 女性略多", superpower: "讓讀者感覺是在投資自己，而不只是買一本書" },
  sacred_cosmic:     { shelf: 75, trust: 77, social: 79, premium: 83, rank: 4, demo: "28–45, 女性略多", superpower: "建立忠誠追隨者——投入其中的讀者成為品牌傳教士" },
};

const ANGLE_MARKET = {
  debunk:    { viral: 88, trust: 45, conversion: 55, seo: 60, tip: "最適合漏斗頂端——爭議性驅動陌生受眾的分享" },
  framework: { viral: 55, trust: 82, conversion: 90, seo: 85, tip: "最適合漏斗中段——準備採取行動的受眾需要結構" },
  reveal:    { viral: 80, trust: 65, conversion: 65, seo: 70, tip: "最適合電子郵件鉤子——將好奇心引橋至更深層的內容" },
  leverage:  { viral: 75, trust: 70, conversion: 72, seo: 50, tip: "最適合重新框架異議——將抗拒轉化為認同" },
  origin:    { viral: 50, trust: 92, conversion: 60, seo: 55, tip: "最適合長篇忠誠度——與既有受眾深化信任" },
};

const TOPIC_MARKET = {
  "睡眠與焦慮":       { search: 95, competition: 88, monetization: 82, growth: 75, platform: "YouTube" },
  "燃盡與工作":        { search: 80, competition: 75, monetization: 78, growth: 85, platform: "LinkedIn" },
  "悲傷與療癒":       { search: 55, competition: 40, monetization: 60, growth: 65, platform: "Podcasts" },
  "身份認同與方向":  { search: 60, competition: 55, monetization: 70, growth: 80, platform: "TikTok" },
  "專注力與表現":   { search: 85, competition: 82, monetization: 88, growth: 70, platform: "YouTube" },
  "意義與靈性":{ search: 50, competition: 45, monetization: 65, growth: 75, platform: "書籍" },
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
        eyebrow="領域"
        title="宣示您的搜尋領域"
        subtitle="每個類別選一個主題——每個選擇設定您品牌用來框架該領域的內容切角。選擇時觀察側邊欄的更新。"
      />
      <div className="mb-6 rounded-xl border border-indigo-100/80 bg-indigo-50/50 p-4 backdrop-blur-sm">
        <p className="text-xs leading-relaxed text-indigo-900">
          <strong>每個類別選一個。</strong> 每個主題都搭配一個內容切角——破解迷思、框架、揭露、善用優勢或追溯根源。切換主題時，側邊欄的切角與策略也會隨之更新。
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
      <h2 className="text-2xl font-extrabold text-white tracking-tight">市場情報</h2>
      <p className="text-sm text-white mt-1 mb-2">您的創意願景是品牌的靈魂。但光有靈魂還不夠。這個頁面向您展示系統如何將您獨特的方向與紮實的市場數據相融合——真實的搜尋量、經驗證的買家輪廓，以及高轉換率的關鍵字領域——以確保您的作品目錄觸及那些已經在尋找您所提供的事物的人。</p>
      <p className="text-xs text-white mb-6 italic">您品牌的語音與身份認同毫無改變。我們只是確保它出現在需求所在之處。</p>

      {/* Gen Z / Gen Alpha FIRST */}
      <div className="rounded-xl border border-violet-200 bg-violet-50 p-5 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Globe size={16} className="text-violet-600" />
          <span className="text-sm font-bold text-violet-800">年輕族群觸及：Z 世代 + Alpha 世代</span>
        </div>
        <p className="text-xs text-violet-700 leading-relaxed mb-3">
          Pearl Prime 上的每個品牌，自動服務 Z 世代與 Alpha 世代讀者——無需額外設定。系統為您的內容建立適齡的調適版本：針對行動優先消費習慣縮短格式、針對滑動式發現優化的視覺優先版面、TikTok 與 YouTube Shorts 的平台原生鉤子，以及為用圖像而非段落思考的讀者打造的全圖漫畫風格版本。Alpha 世代（2010-2025 年出生）是第一個從出生就擁有情感詞彙的世代——他們搜尋心理健康內容的年齡，比以往任何世代都更早。您的品牌在他們所在之處與他們相遇。
        </p>
        <div className="grid grid-cols-3 gap-2">
          {[
            { icon: Smartphone, label: "短格式優先", desc: "TikTok、Reels、Shorts 優化" },
            { icon: BookMarked, label: "漫畫版本", desc: "全圖視覺格式" },
            { icon: Headphones, label: "微型有聲書", desc: "15-30 分鐘行動裝置聆聽" },
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
          <span className="text-sm font-bold text-emerald-800">融合如何運作</span>
        </div>
        <p className="text-xs text-emerald-700 leading-relaxed mb-4">
          我們將您的創意方向——原型、語音、主題與切角——與經過驗證的高效搜尋詞、受眾族群及即時市場訊號相結合。您的品牌身份認同完整保留，同時系統確保您的作品目錄鎖定人們正在積極搜尋的主題。這意味著您的書籍出現在需求已然存在之處，您的標題與人們實際輸入搜尋欄的詞彙相符，您的內容觸及具備驗證消費能力的買家輪廓。結果是：您獨特的聲音觸及最廣大的受眾。
        </p>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white rounded-lg p-3">
            <div className="text-[10px] font-bold text-emerald-700 uppercase mb-1">您的方向</div>
            <p className="text-[11px] text-white">原型、語音、主題、切角、視覺風格——作為您品牌獨特的創意身份認同完整保留</p>
          </div>
          <div className="bg-white rounded-lg p-3">
            <div className="text-[10px] font-bold text-emerald-700 uppercase mb-1">市場情報</div>
            <p className="text-[11px] text-white">與您原型匹配的經驗證收益輪廓、熱門搜尋詞、高轉換率關鍵字，以及需求數據</p>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5 mb-6">
        <div className="text-xs font-bold text-white mb-3">您原型的經驗證收益輪廓</div>
        <p className="text-[11px] text-white mb-3">這些是在您的情感領域中具備驗證購買力的受眾族群。系統確保您的作品目錄觸及所有這些族群。</p>
        {proven.personas.map((p, i) => (
          <div key={i} className="flex items-start gap-2 mb-2.5">
            <Target size={12} className="text-indigo-500 flex-shrink-0 mt-0.5" />
            <span className="text-[11px] text-white">{p}</span>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <div className="text-xs font-bold text-white mb-3">高效能搜尋主題</div>
        <p className="text-[11px] text-white mb-3">這些搜尋詞具備驗證的每月搜尋量與轉換率。您的標題與關鍵字將圍繞這些詞彙，連同您的自訂選擇一起進行優化。</p>
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
    { id: "audiobook", label: "有聲書", icon: Headphones, desc: "在 Audible、Spotify、Apple Books 及全球 40 餘個平台發布的完整朗讀有聲書", benefit: "聽眾在通勤、散步與輾轉難眠的夜晚療癒——您的聲音成為他們最脆弱的私密時刻的陪伴" },
    { id: "yt_channel", label: "YouTube 頻道", icon: Tv, desc: "每日影片內容——短影片、長篇談話、引導式練習，以及視覺化章節", benefit: "視覺型學習者透過動態影像處理情感——您的品牌成為他們動態中每日出現的存在，透過持續現身建立信任" },
    { id: "tiktok", label: "TikTok", icon: Smartphone, desc: "平台原生短影音，搭配熱門音樂、文字疊層與鉤子優先的剪輯", benefit: "您在脆弱時刻捕捉到正在滑手機的人——一支 30 秒短片，可能是生命改變的第一步" },
    { id: "pocket_guide", label: "口袋指南", icon: BookOpen, desc: "濃縮的 30-50 頁快速參考版——週末閱讀即可掌握的核心精華", benefit: "無法承諾閱讀完整書籍的不知所措讀者，獲得立即的解脫——一個週末就能完成核心蛻變的閱讀" },
    { id: "7_day_guide", label: "七天實踐法", icon: Clock, desc: "精縮的蛻變方案——每天一章，清晰的每日行動，快速的小勝利", benefit: "結構感降低不知所措——那些「想到才看」計劃失敗的讀者，在建立動能的每日任務中重拾節奏" },
    { id: "mastercourse", label: "大師課程系列", icon: GraduationCap, desc: "多冊深度探索系列，複雜度逐步遞進——4-8 本相互建構的書籍", benefit: "投入的讀者在數月間深入探索——每一冊在上一冊的基礎上建構，創造真正、持久改變所需的持續修練" },
    { id: "workbook", label: "互動練習本", icon: PenTool, desc: "以練習為主的配套讀本，包含填寫區段、追蹤表格與引導式反思空間", benefit: "書寫啟動與閱讀不同的大腦路徑——練習本將被動消費轉化為主動的自我發現與整合" },
    { id: "daily_journal", label: "每日日誌", icon: BookMarked, desc: "30-90 day guided journal — one prompt per day with space for writing and reflection", benefit: "每日提示鍛鍊自我覺察的肌肉——讀者一頁一頁地與自己的內在世界建立持續的關係" },
  ];

  return (
    <div>
      <h2 className="text-2xl font-extrabold text-white tracking-tight">格式與頻道選擇</h2>
      <p className="text-sm text-white mt-1 mb-2">您的格式重心告訴作品目錄規劃，是要優化視覺優先的短篇內容，還是深度長篇書籍。您的頻道選擇決定品牌在哪裡發布——每個啟用的頻道都為流程增加內容份量，意味著更多格式、更多變體，以及與受眾更多的接觸點。</p>

      <div className="text-xs font-bold uppercase tracking-wider text-white mb-3 mt-6">主要格式重心</div>
      <p className="text-[11px] text-white mb-3">這是最重要的格式決策，它將改變作品目錄規劃分配內容至整個品牌的方式。</p>
      <div className="grid grid-cols-2 gap-3 mb-8">
        <button onClick={() => setFocus("manga")}
          className={`p-5 rounded-xl border-2 text-left transition-all ${formatFocus === "manga" ? "border-gray-900 bg-gray-50 shadow-md" : "border-gray-200 bg-white hover:border-gray-300"}`}>
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-rose-500 to-purple-600 flex items-center justify-center mb-3"><Image size={24} className="text-white" /></div>
          <div className="text-sm font-bold text-white">漫畫 / 視覺</div>
          <p className="text-[11px] text-white mt-1 leading-relaxed">圖文面板、視覺敘事、漫畫式排版。有聲書預設為短篇格式（15-30 分鐘）。針對 Z 世代與 Alpha 世代的視覺優先消費習慣優化。</p>
          {formatFocus === "manga" && <div className="mt-2 bg-rose-50 rounded-lg p-2"><p className="text-[10px] text-rose-700">作品目錄規劃將在所有頻道優先排程短篇有聲書、視覺內容，以及插圖豐富的格式。</p></div>}
        </button>
        <button onClick={() => setFocus("book")}
          className={`p-5 rounded-xl border-2 text-left transition-all ${formatFocus === "book" ? "border-gray-900 bg-gray-50 shadow-md" : "border-gray-200 bg-white hover:border-gray-300"}`}>
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center mb-3"><BookOpen size={24} className="text-white" /></div>
          <div className="text-sm font-bold text-white">傳統書籍</div>
          <p className="text-[11px] text-white mt-1 leading-relaxed">完整篇幅的敘事書籍、深度引導課程、綜合練習本。有聲書採長篇格式（3-8 小時）。針對追求深度的讀者優化。</p>
          {formatFocus === "book" && <div className="mt-2 bg-amber-50 rounded-lg p-2"><p className="text-[10px] text-amber-700">作品目錄規劃將在所有頻道優先排程長篇書籍、完整課程，以及深度系列。</p></div>}
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

      <div className="text-xs font-bold uppercase tracking-wider text-white mb-3">發布頻道</div>
      <p className="text-[11px] text-white mb-3">選擇您希望品牌發布的所有頻道。每個頻道生成專屬內容，針對該平台的格式、受眾與演算法需求進行調適。</p>
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
    if (v.id === "gentleDirect") return p <= 3 ? "給予許可" : p >= 8 ? "指引有力" : "平衡";
    if (v.id === "simpleDeep") return p <= 3 ? "易於親近" : p >= 8 ? "層次豐富" : "中等深度";
    if (v.id === "emotionalLogical") return p <= 3 ? "以故事引導" : p >= 8 ? "以數據驅動" : "平衡";
    if (v.id === "spiritualPractical") return p <= 3 ? "沉思冥想" : p >= 8 ? "策略實用" : "融合調和";
    return "";
  });

  // Generate true category statement
  const trueCategory = arch && persona
    ? `${arch.name} for ${persona.label}${moment ? ` — 捕捉他們在「${moment.label}」的時刻` : ""}`
    : arch ? arch.name : "藍圖";

  // Content engine steps derived from voice + angle mix
  const engineSteps = [
    { step: "命名問題", desc: moment ? `以「${moment.scene}」開場——讀者當下的精確狀態` : "以讀者的確切痛點開場", icon: "🎯" },
    { step: "重塑身份認同", desc: `運用${uniqueAngles.includes("debunk") ? "破除迷思" : uniqueAngles.includes("reveal") ? "揭曉" : "溯源起點"}的切角改變他們的自我敘事`, icon: "🪞" },
    { step: "給予微型工具", desc: `提供${uniqueAngles.includes("framework") ? "今晚就能使用的框架" : "可立即實踐的可行洞見"}`, icon: "🔧" },
    { step: "落地於情感", desc: emotions.length > 0 ? `每件內容都以此作結：「${emotions[0]}」` : "每件內容都落在承諾的感受上", icon: "💫" },
  ];

  // Unfair advantage loop
  const loopSteps = [
    { label: "重新框架", desc: "打破他們舊有的故事", color: "#6366f1" },
    { label: "調節", desc: "平靜神經系統", color: "#059669" },
    { label: "重建", desc: "從身體開始重建", color: "#f59e0b" },
    { label: "重新定向", desc: "指向新的身份認同", color: "#f43f5e" },
  ];

  // Positioning map coords — Gentle↔Direct on X, Simple↔Deep on Y
  const posX = voicePositions.find(v => v.id === "gentleDirect")?.position || 5;
  const posY = voicePositions.find(v => v.id === "simpleDeep")?.position || 5;

  // Emotional staircase — build ascending steps from trigger to each emotion
  const staircaseSteps = [
    { label: moment ? moment.label : "痛點", color: "#f43f5e", sub: "他們的起點" },
    ...emotions.slice(0, 5).map((e, i) => {
      const cat = _EC.find(c => c.items.includes(e));
      return { label: e, color: cat?.color || "#6366f1", sub: cat?.name || "" };
    }),
  ];

  return (
    <div>
      <StepHero
        eyebrow="揭曉"
        title="這就是您的品牌"
        subtitle=""
      />

      {/* ═══ 1. TRUE CATEGORY — gradient banner ═══ */}
      {arch && (
        <div id="rev-category" className={`mb-6 rounded-2xl border-2 p-6 bg-gradient-to-br ${arch.gradient} shadow-lg`}>
          <div className="text-center">
            <div className="text-white/70 text-[10px] font-bold uppercase tracking-[0.3em] mb-2">您的真正類別</div>
            <div className="text-white text-xl font-extrabold mb-2">{trueCategory}</div>
            <div className="text-white/80 text-sm leading-relaxed">{arch.tagline}</div>
            {arch.visionVibe && <p className="mt-3 text-white/70 text-[11px] leading-relaxed max-w-md mx-auto italic">{arch.visionVibe}</p>}
          </div>
        </div>
      )}

      {/* ═══ 2. VOICE SIGNATURE — circular gauges ═══ */}
      {Object.keys(state.voiceSettings || {}).length > 0 && (
        <div id="rev-voice" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">語音特質</div>
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
            你的聲音是 <span className="text-white font-semibold">{voiceDesc.join(" · ")}</span>
          </div>
        </div>
      )}

      {/* ═══ 2b. POSITIONING MAP — 2D quadrant ═══ */}
      <div id="rev-positioning" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">定位圖</div>
        <div className="text-[10px] text-white/70 mb-3 text-center">您的語音在市場版圖中的位置</div>
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
          <text x="30" y="285" fontSize="9" fill="#9ca3af" fontWeight="bold">溫柔</text>
          <text x="265" y="285" fontSize="9" fill="#9ca3af" fontWeight="bold">直接</text>
          <text x="5" y="15" fontSize="9" fill="#9ca3af" fontWeight="bold" transform="rotate(-90 10 15)">深刻</text>
          <text x="5" y="275" fontSize="9" fill="#9ca3af" fontWeight="bold" transform="rotate(-90 10 275)">簡單明瞭</text>
          {/* Quadrant labels */}
          <text x="95" y="75" textAnchor="middle" fontSize="8" fill="#6366f1" fontWeight="600">智慧引導者</text>
          <text x="225" y="75" textAnchor="middle" fontSize="8" fill="#059669" fontWeight="600">專業教練</text>
          <text x="95" y="210" textAnchor="middle" fontSize="8" fill="#f59e0b" fontWeight="600">溫暖摯友</text>
          <text x="225" y="210" textAnchor="middle" fontSize="8" fill="#f43f5e" fontWeight="600">有力的導師</text>
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
          { label: "書架吸引力", val: vm.shelf || 0, color: "#f59e0b" },
          { label: "信任訊號", val: vm.trust || 0, color: "#059669" },
          { label: "社群分享力", val: vm.social || 0, color: "#6366f1" },
          { label: "高端質感", val: vm.premium || 0, color: "#7c3aed" },
        ];
        return (
          <div id="rev-visual" className="mb-6 rounded-2xl border border-gray-200 bg-white overflow-hidden shadow-sm">
            <div className="flex items-center gap-0 border-b border-gray-100">
              {visual.palette.map((col, i) => (
                <div key={i} className="flex-1 h-12" style={{ backgroundColor: col }} />
              ))}
            </div>
            <div className="p-4">
              <div className="text-[10px] font-bold uppercase text-white">視覺識別</div>
              <div className="mt-1 text-base font-bold text-white">{visual.label}</div>
              <p className="mt-1 text-[11px] text-white italic">{visual.mood}</p>
            </div>
            <div className="px-4 pb-4">
              <div className="text-[9px] font-bold uppercase tracking-wider text-white mb-2">市場評分</div>
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
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">情感階梯</div>
          <div className="text-[10px] text-white/70 mb-4">您的讀者從痛苦走向承諾——每一步都在上一步的基礎上建構</div>
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
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">主題 × 切角策略</div>
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
                      { label: "病毒傳播力", val: am.viral, color: "#f43f5e" },
                      { label: "搜尋", val: tm.search, color: "#0ea5e9" },
                      { label: "轉換力", val: am.conversion, color: "#059669" },
                      { label: "成長潛力", val: tm.growth, color: "#f59e0b" },
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
                      綜合評分: {comboScore}
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
        <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-1">內容引擎公式</div>
        <div className="text-[10px] text-white/70 mb-5">每一件內容都遵循這個序列——您獨特的飛輪</div>
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
          <span className="text-[9px] font-bold text-white/50 uppercase tracking-wider">↻ 每件內容都重複此流程</span>
          <div className="h-px flex-1" style={{ background: 'linear-gradient(90deg, transparent, #b4530940, transparent)' }} />
        </div>
      </div>

      {/* ═══ 7. UNFAIR ADVANTAGE LOOP — circular diagram ═══ */}
      <div id="rev-loop" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">不對稱優勢迴圈</div>
        <div className="text-[10px] text-white/70 mb-4 text-center">每一件內容都滋養下一件——每個出口都是更深層蛻變的入口</div>
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
          <text x="160" y="170" textAnchor="middle" fontSize="7" fill="#6b7280">持續重複</text>
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
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">受眾體驗</div>
          <div className="text-[10px] text-white/70 mb-3">{persona.emoji} {persona.label} 體驗你的品牌的過程：</div>
          <div className="flex flex-col items-center gap-1.5">
            {[
              { phase: "觸發", desc: `${moment.emoji} ${moment.scene}`, color: "#f43f5e", bg: "bg-rose-50" },
              { phase: "發現", desc: `他們找到您的內容——鉤子精確命名了他們的痛`, color: "#f59e0b", bg: "bg-amber-50" },
              { phase: "信任", desc: `您${voiceDesc[0]}的聲音讓他們感到${voiceDesc[2]} — 不是被說教，而是被理解`, color: "#3b82f6", bg: "bg-blue-50" },
              { phase: "轉化", desc: emotions[0] ? `他們開始感受到：「${emotions[0]}」` : "承諾的情感觸達", color: "#059669", bg: "bg-emerald-50" },
              { phase: "回歸", desc: `他們再次回來，因為每一件內容都在更深的層次傳遞同樣的蛻變`, color: "#7c3aed", bg: "bg-violet-50" },
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
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">語音 × 主題協同效應</div>
          <div className="text-[10px] text-white/70 mb-3">您的語音語調如何放大每個內容切角</div>
          <div className="space-y-3">
            {topicAnglePairs.map((p, i) => {
              const af = _AF[p.angle];
              const score = calcSynergyScore(voicePositions, p.angle);
              const multiplier = (0.5 + (score / 100) * 1.5).toFixed(1);
              const barColor = p.catColor;
              const gentlePos = voicePositions.find(v => v.id === "gentleDirect")?.position || 5;
              const toneWord = gentlePos <= 3 ? "溫柔地" : gentlePos >= 8 ? "直接地" : "清晰地";
              return (
                <div key={i} className="rounded-xl bg-white p-3 border border-violet-100">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm">{p.catIcon}</span>
                    <span className="text-[10px] text-white flex-1">
                      您以<strong>{toneWord}</strong>的語調進行{af?.label} <strong>{p.tagLabel}</strong>
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
                <span className="text-[10px] font-bold text-white">整體語音契合度</span>
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
          { label: "視覺", val: visualAvg, color: "#7c3aed" },
          { label: "病毒傳播力", val: avg("viral"), color: "#f43f5e" },
          { label: "信任", val: avg("trust"), color: "#059669" },
          { label: "轉換力", val: avg("conversion"), color: "#f59e0b" },
          { label: "SEO", val: avg("seo"), color: "#0ea5e9" },
          { label: "成長潛力", val: avg("growth"), color: "#6366f1" },
        ];
        const overallScore = Math.round(dims.reduce((s, d) => s + d.val, 0) / dims.length);
        const sides = 6, cx = 150, cy = 110, r = 75;

        return (
          <div id="rev-radar" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <div className="text-[10px] font-bold uppercase tracking-wider text-white">品牌力</div>
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
          <div className="text-violet-300/70 text-[10px] font-bold uppercase tracking-[0.3em] mb-3 text-center">品牌綜合</div>
          <p className="text-center text-white text-sm leading-relaxed font-medium">
            你是 <strong>{arch.name}</strong> — 以{voiceDesc[0]}、{voiceDesc[1]}的語調，捕捉{" "}
            <strong>{persona.label}</strong>
            {moment && <>在他們<em>「{moment.label}」</em>時刻</>}，{" "}
            {uniqueAngles.length > 0 && <>運用 {uniqueAngles.map(a => _AF[a]?.label).join(" + ")} 的切角</>}{" "}
            {emotions.length > 0
              ? <>傳遞一個承諾：<strong>「{emotions[0]}」</strong></>
              : <>帶來蛻變</>
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
    { label: "市場潛力", value: marketability, desc: "Alignment with proven market demand" },
    { label: "年輕族群觸及力", value: youthReach, desc: "Gen Z and Gen Alpha compatibility" },
    { label: "生命影響力", value: lifeImpact, desc: "Transformation depth for your reader" },
    { label: "平台觸及力", value: reachScore, desc: "Multi-channel distribution coverage" },
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
      ? "卓越的品牌定位。您的原型、受眾與主題選擇，與高收益市場區隔形成強力對齊。這個品牌具備強大的商業潛力，以及對讀者的深遠影響力。"
      : marketability >= 75
        ? "堅實的品牌基礎。您的選擇創造出具說服力的身份認同，與市場形成穩固的對齊。再進行幾項精煉，就能推進至卓越的境界。"
        : "良好的起點。您的品牌身份認同正在成形——考慮增加更多主題選擇與頻道覆蓋率，以強化您的市場定位。";

  return (
    <div>
      <StepHero
        eyebrow="揭曉"
        title="這就是您的品牌"
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
                  <div className="text-[10px] font-bold uppercase text-violet-600/90">主要讀者</div>
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
                  <div className="text-[10px] font-bold uppercase text-violet-600">視覺風格</div>
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
                  <div className="text-[8px] font-bold uppercase text-white">路線</div>
                  <div className="mt-0.5 text-[11px] font-semibold text-white">{state.onboardingLane.replace(/_/g, " ")}</div>
                </div>
              ) : null}
              {state.onboardingMarket ? (
                <div className="rounded-xl border border-violet-100/90 bg-white/80 p-2.5 text-center opacity-90">
                  <div className="text-[8px] font-bold uppercase text-white">市場</div>
                  <div className="mt-0.5 text-[11px] font-semibold text-white">{state.onboardingMarket}</div>
                </div>
              ) : null}
              {state.formatFocus ? (
                <div className="rounded-xl border border-violet-100/90 bg-white/80 p-2.5 text-center opacity-90">
                  <div className="text-[8px] font-bold uppercase text-white">格式</div>
                  <div className="mt-0.5 text-[11px] font-semibold text-white">{state.formatFocus === "manga" ? "漫畫／視覺" : "書籍"}</div>
                </div>
              ) : null}
              {(state.channels || []).length > 0 ? (
                <div className="rounded-xl border border-violet-100/90 bg-white/80 p-2.5 text-center opacity-90">
                  <div className="text-[8px] font-bold uppercase text-white">頻道</div>
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
              <span className="text-xs font-bold text-emerald-900">閱讀您的方向說明</span>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-emerald-900/90">{assessmentText}</p>
          </div>
        </section>
      </div>

      {/* Demoted score strip — same numeric logic, after narrative sections */}
      <div className="mt-10 rounded-2xl border border-gray-100 bg-gray-50/60 px-3 py-3 opacity-90">
        <div className="mb-2 text-center text-[9px] font-bold uppercase tracking-wider text-white">信號分數</div>
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
  const { t } = useTranslation();
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
      persona && { label: "讀者", value: `${persona.emoji} ${persona.label}`, icon: Users, gradient: "from-blue-500 to-cyan-500", systemEffect: _SF.personas[state.persona]?.systemEffect, emotionalBenefit: _SF.personas[state.persona]?.emotionalBenefit },
      moment && { label: "時刻", value: `${moment.emoji} ${moment.label}`, icon: Target, gradient: "from-amber-500 to-orange-500", systemEffect: _SF.moments[state.moment]?.systemEffect, emotionalBenefit: _SF.moments[state.moment]?.emotionalBenefit },
      Object.keys(state.voiceSettings || {}).length > 0 && { label: "語氣", value: `${Object.keys(state.voiceSettings).length} dimensions tuned`, icon: SlidersHorizontal, gradient: "from-indigo-500 to-violet-500", systemEffect: "全部 4 個語音維度校準每一個章節、有聲書與社群貼文的行文節奏、詞彙層次、句子結構與情感溫度", emotionalBenefit: "您的讀者體驗到一種感覺像是為他們量身書寫的聲音——正是他們所需要的挑戰與溫柔的精準調和。每一句話都能落地，因為語調與他們的情感準備狀態相符。" },
      visual && { label: "影響", value: visual.label, icon: Palette, gradient: "from-rose-500 to-pink-500", systemEffect: _SF.visualStyles[state.visualStyle]?.systemEffect, emotionalBenefit: _SF.visualStyles[state.visualStyle]?.emotionalBenefit },
      (state.emotions || []).length > 0 && { label: "視覺", value: state.emotions.join(", "), icon: Heart, gradient: "from-rose-400 to-red-500", systemEffect: `${state.emotions.length} transformation promises woven into every title, CTA, and marketing message`, emotionalBenefit: "這些感受成為每一件內容的北極星——您的讀者清楚知道什麼樣的蛻變在等待著他們，在閱讀第一個字之前就已燃起希望。" },
      state.tradition && { label: "靈性基礎", value: state.tradition, icon: Sun, gradient: "from-amber-400 to-yellow-500", systemEffect: "影響所有內容中的詞彙選擇、哲學基礎，以及特定傳統的引用", emotionalBenefit: "具有這個傳統背景的讀者感到被認可與尊重。語言承載著真實傳承的份量，而非表面的挪用。" },
      (state.angles || []).length > 0 && { label: "內容切角", value: state.angles.map(a => V4_ANGLES.find(v => v.id === a)?.label).filter(Boolean).join(", "), icon: Layers, gradient: "from-purple-500 to-indigo-500", systemEffect: `${state.angles.length} framing modes active — every title opens with one of these argumentative strategies`, emotionalBenefit: "每個切角為您的讀者提供不同的療癒入口。多種切角意味著您的品牌能在讀者改變準備度的任何階段觸及他們。" },
      (state.topicTags || []).length > 0 && { label: "搜尋領域", value: `${state.topicTags.length} 個主題已確認`, icon: Search, gradient: "from-emerald-500 to-teal-500", systemEffect: `${state.topicTags.length} search topics feed into title generation, keyword targeting, series planning, and ad campaigns`, emotionalBenefit: "您的內容在某人將痛苦輸入搜尋欄的那一刻精確出現。您不是在行銷——您是以恰到好處的話語，回應一聲求助的呼喚。" },
      state.onboardingLane && { label: "引導路線", value: state.onboardingLane.replace(/_/g, " "), icon: Layers, gradient: "from-fuchsia-500 to-purple-500", systemEffect: "成效展示列與資料庫配對，現在已限縮於您選定的路線，讓利益關係人能夠提早預覽正確的產出系列。", emotionalBenefit: "您可以立即查看您想優先採用的路線是否有令人信服的成效佐證，減少上線時的意外。" },
      state.onboardingMarket && { label: "引導市場", value: state.onboardingMarket, icon: Globe, gradient: "from-sky-500 to-cyan-500", systemEffect: "資料庫配對在引導過程中，現在使用明確的市場篩選，以避免跨市場的錯誤信心。", emotionalBenefit: "您的團隊審閱的範例，確實與您計劃進入的市場相符。" },
      state.formatFocus && { label: "格式重心", value: state.formatFocus === "manga" ? "漫畫 / 視覺" : "傳統書籍", icon: BookOpen, gradient: "from-cyan-500 to-blue-500", systemEffect: _SF.formats[state.formatFocus]?.systemEffect, emotionalBenefit: _SF.formats[state.formatFocus]?.emotionalBenefit },
      (state.channels || []).length > 0 && { label: "發布頻道", value: `${state.channels.length} channels active`, icon: Globe, gradient: "from-violet-500 to-purple-500", systemEffect: `Content adapts to ${state.channels.length} platforms — each generates format-specific, algorithm-optimized variations`, emotionalBenefit: "您的讀者在他們本來就花時間的地方發現您。無論是凌晨三點滑 TikTok，還是週日的有聲書散步——您的品牌都在那裡，準備好了，以正確的格式等待著他們。" },
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
              onClick={() => { window.location.href = "/brand_admin_weekly_os?brand=" + encodeURIComponent(matched.brand_id); }}
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
                <span className="text-[8px] font-bold uppercase text-white">總體</span>
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
            <p className="text-lg font-bold text-white mb-1">你的品牌宇宙誕生了。</p>
            <p className="text-sm text-white max-w-md mx-auto leading-relaxed">
              You've made {choiceAudit.length} defining choices that shape everything your brand creates — every book, audiobook, video, cover, and piece of social content. Here's what you've built and how it helps the people who need it most.
            </p>
          </div>
        </div>

        {/* Score Cards */}
        <div className="grid grid-cols-4 gap-2 mb-8">
          {[
            { label: "市場潛力", value: marketability, color: "#10b981" },
            { label: "年輕族群觸及力", value: youthReach, color: "#8b5cf6" },
            { label: "生命影響力", value: lifeImpact, color: "#ec4899" },
            { label: "平台觸及力", value: reachScore, color: "#3b82f6" },
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
          <h2 className="text-lg font-extrabold text-white mb-1">你的品牌選擇</h2>
          <p className="text-xs text-white mb-4">您的每一個選擇，在系統中所啟動的功能，以及如何在心理與情感層面幫助您的讀者。</p>

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
                    <div className="text-[9px] font-bold text-emerald-500 bg-emerald-50 px-2 py-0.5 rounded-full flex-shrink-0">已啟動</div>
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
              <span className="text-sm font-bold text-purple-800">用一句話描述你的品牌</span>
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
                  <Check size={11} />{yamlCopied ? "已複製！" : "複製"}
                </button>
                <button onClick={() => { const blob = new Blob([yamlOutput], {type: "text/yaml"}); const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "brand-config.yaml"; a.click(); }}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-bold transition-colors">
                  <Download size={11} />下載 .yaml
                </button>
              </div>
              <pre className="text-[11px] text-green-400 font-mono whitespace-pre-wrap">{yamlOutput}</pre>
            </div>
          )}
        </div>

        {/* Final Message */}
        <div className="text-center py-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-50 text-emerald-700 text-xs font-bold mb-3">
            <Check size={12} /> 品牌設定已儲存
          </div>
          <p className="text-sm text-white max-w-md mx-auto">
            您的品牌宇宙已準備就緒。Pearl Prime 系統將運用您的每一個選擇，為您生成完整的作品目錄——書籍、有聲書、漫畫、影片，以及能夠改變生命的社群內容。
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 rounded-2xl border border-violet-200/80 bg-gradient-to-br from-violet-50/90 via-white to-fuchsia-50/30 px-5 py-6 text-center shadow-sm">
        <h2 className="text-2xl font-extrabold tracking-tight sm:text-3xl" style={{ color: '#d97706', fontFamily: 'Cormorant Garamond, serif' }}>填入聯絡資料並點擊「啟用」</h2>
        <p className="mx-auto mt-3 max-w-md text-sm text-white/70">
          您將立即獲得品牌作品目錄的發布權限
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
          <Check size={14} className="shrink-0 text-emerald-600" strokeWidth={2.5} /> 讀者和市場已選擇
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
              <label className="mb-1 block text-xs font-semibold text-white">電子郵件 *</label>
              <input
                type="email"
                placeholder="you@example.com"
                className="w-full rounded-xl border border-gray-200 p-3 text-sm outline-none focus:border-gray-500"
                value={c.email || ""}
                onChange={(e) => handleField("email", e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold text-white">電話</label>
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
          <h3 className="mb-4 text-[10px] font-bold uppercase tracking-[0.15em] text-white">2 · 訊息聯絡管道</h3>
          <p className="mb-3 text-[11px] text-white">選填 — 讓我們除電子郵件外也能聯絡到您。</p>
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
            <label className="mb-1 block text-[10px] font-semibold text-white">首選管道</label>
            <select
              className="w-full rounded-lg border border-gray-200 bg-white p-2.5 text-sm outline-none focus:border-gray-500"
              value={c.preferred || "email"}
              onChange={(e) => handleField("preferred", e.target.value)}
            >
              <option value="email">僅限電郵</option>
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
              稅務識別碼（SSN/EIN）將於審核通過後透過獨立的安全步驟收集，本表單不收取任何敏感財務資料。
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
        {isReady ? "啟動" : "填入姓名與電郵以啟動"}
      </button>
      {!isReady ? <p className="mt-2 text-center text-[11px] text-white">填入姓名與有效的電子郵件信箱，即可解鎖啟用。</p> : null}
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
  y += `  onboarding_lane: "${state.onboardingLane || "self_help"}"\n  onboarding_market: "${state.onboardingMarket || "taiwan"}"\n`;
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
    { icon: PenTool, label: t("ui", "語音風格"), tint: "from-violet-500 to-indigo-600" },
    { icon: Image, label: t("ui", "視覺"), tint: "from-fuchsia-500 to-pink-600" },
    { icon: Users, label: t("ui", "讀者"), tint: "from-sky-500 to-blue-600" },
    { icon: Layers, label: t("ui", "格式"), tint: "from-emerald-500 to-teal-600" },
  ];
  return (
    <div className="brand-studio-bg min-h-screen text-white">
      <div className="mx-auto max-w-3xl px-6 py-16">
        <div className="brand-studio-panel p-10 text-center sm:p-12">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-violet-200/80 bg-violet-50/80 px-4 py-1.5 text-xs font-semibold text-violet-800 backdrop-blur-sm">
            <Sparkles size={12} /> {t("ui", "Pearl Prime 品牌工作室")}
          </div>
          <h1 className="text-4xl font-black leading-tight tracking-tight text-white sm:text-5xl">{t("ui", "啟動並塑造您的出版品牌")}</h1>
          <p className="mx-auto mt-4 max-w-lg text-base leading-relaxed text-white">
            {t("ui", "一次引導式設定——語音、外觀與成效，完整對齊。")}
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
              {t("ui", "開始建立")} <ChevronRight size={18} />
            </button>
          </div>
          <p className="mt-8 text-center text-xs">
            <a
              href="https://brand-admin-onboarding-bu2.pages.dev/pearl_prime_v6-3.html"
              className="font-semibold text-orange-400 underline decoration-orange-300 underline-offset-2 hover:text-orange-300"
            >
              {t("ui", "返回起點")}
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
    { step: "1", title: t("intro", "基礎"), sub: t("intro", "原型與讀者"), color: "from-indigo-500 to-violet-600" },
    { step: "2", title: t("intro", "語音風格"), sub: t("intro", "語調與影響力"), color: "from-violet-500 to-fuchsia-600" },
    { step: "3", title: t("intro", "外觀與主題"), sub: t("intro", "視覺 + 領域"), color: "from-rose-500 to-orange-500" },
    { step: "4", title: t("intro", "格式"), sub: t("intro", "頻道與流程"), color: "from-sky-500 to-cyan-600" },
    { step: "5", title: t("intro", "揭曉"), sub: t("intro", "藍圖與啟動"), color: "from-slate-600 to-gray-900" },
  ];
  return (
    <div className="brand-studio-bg min-h-screen text-white">
      <div className="mx-auto max-w-3xl px-6 py-12">
        <button type="button" onClick={onBack} className="mb-6 flex items-center gap-1 text-xs text-white transition-colors hover:text-white">
          <ChevronLeft size={14} /> {t("ui", "返回")}
        </button>
        <div className="brand-studio-panel p-8 sm:p-10">
          <div className="text-center">
            <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-violet-600">{t("intro", "運作方式")}</p>
            <h1 className="mt-2 text-3xl font-black tracking-tight">{t("intro", "五個節拍，十一個選擇")}</h1>
            <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-white">
              {t("intro", "基礎 → 格式 → 藍圖 → 啟動。")}
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
              {t("ui", "老師之書")} <ArrowRight size={18} />
            </button>
            <button
              type="button"
              onClick={() => {
                try { localStorage.setItem("phoenix_book_mode", JSON.stringify({ mode: "music", teacher: null })); } catch (_) {}
                window.location.href = "/musician_reflections_survey";
              }}
              className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white shadow-lg transition-all hover:-translate-y-0.5 hover:bg-gray-800"
            >
              {t("ui", "音樂之書")} <ArrowRight size={18} />
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
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 text-indigo-600 text-xs font-semibold mb-4"><PenTool size={12} /> 第一步預覽——書寫語音</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">相同主題。截然不同的語音風格。</h1>
        <p className="text-white mb-8">兩個品牌，一個主題——感受文字與能量的轉換。</p>
        <CompareBlock labelA="靜息實驗室" labelB="澄心實驗室" colorA="text-indigo-600" colorB="text-amber-600"
          contentA={<div><div className="flex gap-2 mb-3"><div className="w-14 h-20 rounded-lg shadow-md flex-shrink-0" style={{ background: "linear-gradient(135deg, #6366f1, #818cf8, #e0e7ff)" }} /><div><div className="text-[10px] text-white font-semibold uppercase">靜息實驗室</div><div className="text-sm font-bold text-white">凌晨兩點，身體記得一切</div></div></div><p className="text-sm text-white leading-relaxed italic border-l-2 border-indigo-300 pl-3">"Your body remembers what your mind tries to forget. Right now, your shoulders are holding yesterday's argument."</p><div className="mt-3 bg-indigo-50 rounded-lg p-3"><div className="text-[10px] font-bold text-indigo-600 uppercase mb-1">練習</div><p className="text-xs text-indigo-800">"Inhale for 4 counts. Hold for 7. Exhale slowly for 8."</p></div></div>}
          contentB={<div><div className="flex gap-2 mb-3"><div className="w-14 h-20 rounded-lg shadow-md flex-shrink-0" style={{ background: "linear-gradient(135deg, #d97706, #f59e0b, #fef3c7)" }} /><div><div className="text-[10px] text-white font-semibold uppercase">澄心實驗室</div><div className="text-sm font-bold text-white">您的手機正在偷走您的睡眠</div></div></div><p className="text-sm text-white leading-relaxed italic border-l-2 border-amber-400 pl-3">"您盯著天花板，因為大腦正在循環播放昨天的爭論。"</p><div className="mt-3 bg-amber-50 rounded-lg p-3"><div className="text-[10px] font-bold text-amber-600 uppercase mb-1">練習</div><p className="text-xs text-amber-800">"手機放到另一個房間。平躺。吐氣比吸氣更長。90 秒。開始。"</p></div></div>}
        />
        <div className="mt-8 text-center">
          <button type="button" onClick={onNext} className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white transition-all hover:bg-gray-800">
            查看封面差異 <ChevronRight size={18} />
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
        <h1 className="text-3xl font-black tracking-tight mb-2">您的視覺風格塑造一切。</h1>
        <p className="text-white mb-8">一個選擇，波及所有封面與縮圖。</p>
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
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 text-amber-600 text-xs font-semibold mb-4"><Film size={12} /> 影片與社群預覽</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">每日內容。您的專屬風格。</h1>
        <p className="text-white mb-8">短影音繼承您的色彩與氛圍。</p>
        <div className="grid grid-cols-2 gap-4 mb-8">
          {ARCHETYPES.slice(0, 4).map((arch) => (
            <div key={arch.id} className="rounded-xl overflow-hidden border border-gray-200">
              <div className="h-32 flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${arch.coverColors[0]}88, ${arch.coverColors[1]}66)` }}><div className="text-center"><Play size={24} className="text-white/80 mx-auto mb-1" /><div className="text-[10px] text-white/80 font-bold">{arch.name}</div></div></div>
              <div className="p-3 bg-white"><div className="text-xs font-bold text-white">{arch.videoStyle}</div><div className="text-[10px] text-white mt-0.5">每日發布於 YouTube、TikTok、Instagram、Facebook、X</div></div>
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
        <h1 className="text-3xl font-black tracking-tight mb-2">一個品牌。無限格式。</h1>
        <p className="text-white mb-8">相同的 DNA——不同的容器。</p>
        <div className="grid grid-cols-3 gap-3 mb-8">
          {V4_FORMATS_STRUCTURAL.map((f) => (
            <div key={f.id} className="p-4 rounded-xl border border-gray-200 bg-white">
              <div className="text-[10px] text-white font-mono mb-1">{f.id}</div><div className="text-xs font-bold text-white">{f.label}</div><div className="text-[10px] text-white mt-0.5">{f.desc}</div>
              <div className="mt-2 flex items-center gap-2"><span className="text-[9px] bg-gray-100 text-white px-2 py-0.5 rounded-full">{f.chapters} ch</span><span className="text-[9px] bg-gray-100 text-white px-2 py-0.5 rounded-full">{f.tier}</span></div>
            </div>
          ))}
        </div>
        <div className="rounded-xl bg-gray-50 border border-gray-200 p-5 mb-8"><p className="text-xs text-white leading-relaxed">漫畫、有聲、課程、日誌、影片——全部從同一個核心自動調適而來。</p></div>
        <div className="mt-8 text-center">
          <button type="button" onClick={onNext} className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white transition-all hover:bg-gray-800">
            開始建立你的品牌 <ArrowRight size={18} />
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

const STEP_LABELS = ["原型", "讀者", "時刻", "語氣", "影響", "視覺", "主題", "藍圖", "啟動"];

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
    onboardingLane: "self_help", onboardingMarket: "taiwan",
    contact: { firstName: "", lastName: "", email: "", phoneCode: "+886", phone: "", line: "", whatsapp: "", wechat: "", messenger: "", preferred: "email" },
  });

  const update = useCallback((patch) => setState((prev) => ({ ...prev, ...patch })), []);
  const scrollTop = () => window.scrollTo({ top: 0, behavior: "instant" });
  const nextIntro = () => { setIntroPage((p) => p + 1); scrollTop(); };
  const prevIntro = () => { if (introPage > 0) { setIntroPage((p) => p - 1); scrollTop(); } };
  const startWizard = () => { setPhase("wizard"); setStep(0); scrollTop(); };
  const nextStep = () => { if (step < 8) { setStep((s) => s + 1); scrollTop(); } };
  const prevStep = () => { if (step > 0) { setStep((s) => s - 1); scrollTop(); } else { setPhase("intro"); setIntroPage(1); scrollTop(); } };
  const goToHowItWorks = () => { setPhase("intro"); setIntroPage(1); scrollTop(); };
  const goToTeacherShowcase = () => { window.location.href = "teacher_showcase-tw.html"; };

  // If ?teacher= / ?mode=composite / ?mode=music in URL, skip intro and jump to wizard step 1.
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlTeacher = params.get("teacher");
    const urlMode = params.get("mode");
    if (urlTeacher || urlMode === "composite" || urlMode === "music") { setPhase("wizard"); setStep(0); scrollTop(); }
  }, []);

  // Market from onboarding.html handoff (?market= / phoenix_onboarding_market) or TW default.
  useEffect(() => {
    const market = resolveOnboardingMarket();
    if (market) update({ onboardingMarket: market });
  }, [update]);

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