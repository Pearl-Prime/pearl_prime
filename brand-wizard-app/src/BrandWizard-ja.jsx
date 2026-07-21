import { useState, useCallback, useRef, useMemo, useEffect } from "react";
import { useLocale } from "./i18n.jsx";
import { pickJaI18n, pickJaI18nFields, translateVoiceTone10, useJaWizardTranslation } from "./jaI18nGuard.js";
import { appendBrandAssignmentToYAML, brandAssignmentPayload, matchBrand } from "./brandMatch.js";
import { classifyOnboardingSubmitFailure, parseHybridOfferMessage } from "./hybridOffer.js";
import { resolveSeededMarket } from "./markets.js";
import { HybridOfferPanel } from "./onboarding/HybridOfferPanel.jsx";
import { ChevronRight, ChevronLeft, Eye, Sparkles, BookOpen, Mic, Film, Palette, Heart, Target, Zap, Shield, Sun, Moon, Flame, Feather, Brain, Compass, Star, Check, AlertTriangle, Download, Play, PenTool, Image, Layers, ArrowRight, Users, BarChart3, TrendingUp, Radio, Headphones, Tv, Smartphone, BookMarked, GraduationCap, Clock, Rocket, Award, Crown, Globe, Volume2, Brush, Activity, Search, Hash, Tag, Grip, CircleDot, SlidersHorizontal } from "lucide-react";
import { OutputProofStrip } from "./onboarding/OutputProofStrip.jsx";
import { LaneChoiceCard } from "./onboarding/LaneChoiceCard.jsx";
// ─────────────────────────────────────────────────────────────

/** JA wizard default market; ?market= / phoenix_onboarding_market / ?lang= override. */
function resolveOnboardingMarket() {
  const { market } = resolveSeededMarket();
  if (market === "jp" || market === "japan" || market === "ja_jp") return "japan";
  if (market && market !== "us") return market;
  return "japan";
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
    id: "nervous_system", name: "静けさラボ",
    tagline: "身体の叫びが止まらないときに",
    icon: Shield, gradient: "from-indigo-500 to-blue-600",
    bg: "bg-gradient-to-br from-indigo-50 to-blue-50",
    accent: "text-indigo-600", border: "border-indigo-200", activeBorder: "border-indigo-500",
    tags: ["落ち着き", "ソマティック", "調整"],
    coverStyle: "柔らかなグラデーション、落ち着いたトーン、有機的な形",
    proseStyle: "優しく、ペース感があり、呼吸に寄り添う",
    videoStyle: "スローモーションの自然、柔らかなフォーカス、アンビエント",
    sampleTitle: "身体は深夜2時でも記憶している",
    sampleSubtitle: "止まらない心のための自律神経リセット",
    sampleProse: "あなたの体は、心が忘れようとしていることを覚えています。今この瞬間、あなたの肩は昨日の言い争いを抱えています。あごは、言えなかった言葉を噛みしめています。これは欠点ではありません——あなたの神経系が、設計通りに機能しているだけです。",
    sampleExercise: "4-7-8 呼吸リセット：4カウントで吸い、7カウント止め、8カウントでゆっくり吐く。3サイクル。たった57秒で、神経系全体の状態が変わります。",
    coverColors: ["#6366f1", "#818cf8", "#e0e7ff"],
    emotions: ["やっと落ち着ける", "自分の身体の中に安心していられる", "解放されている", "グラウンデッド", "休んでいいという許可"],
    visionVibe: "沈黙が空虚ではなく、満ちている世界。体が檻ではなく、羅針盤となる世界。読者は感覚から逃げることではなく、それに耳を傾けることで、安心感を見つけます。",
  },
  {
    id: "identity_direction", name: "コンパス・スタジオ",
    tagline: "迷っているけれど、壊れてはいない人のために",
    icon: Compass, gradient: "from-emerald-500 to-teal-600",
    bg: "bg-gradient-to-br from-emerald-50 to-teal-50",
    accent: "text-emerald-600", border: "border-emerald-200", activeBorder: "border-emerald-500",
    tags: ["方向性", "アイデンティティ", "目的"],
    coverStyle: "すっきりした線、コンパスのモチーフ、開けた地平線",
    proseStyle: "直接的で、温かく、前向き",
    videoStyle: "タイムラプスの旅、夜明けのシーン、道のイメージ",
    sampleTitle: "遅れているのではなく、積み上げているんだ",
    sampleSubtitle: "みんなが答えを持っているように見える中で、方向性を見つける",
    sampleProse: "フィードをスクロールすると、みんな順調に見えます。キャリア、恋愛、枯れない観葉植物のある部屋。そして自分は、何をしているのかと途方に暮れている。",
    sampleExercise: "正直な棚卸し：今週自分で選んだことを3つ書き出しましょう——ささいなことでも構いません。食事、会話、断ったこと。次に、避けたことを1つ書く。そのパターンが、あなたの羅針盤の針です。",
    coverColors: ["#059669", "#34d399", "#d1fae5"],
    emotions: ["頭がすっきりしている", "目的とつながっている", "希望が持てる", "自信がある", "エネルギーが湧いている"],
    visionVibe: "知らないことが失敗ではなく、始まりである世界。方向性は他者との比較ではなく、正直な自己観察から生まれる世界。読者は小さく勇気ある選択を通じて、自分のアイデンティティを築いていきます。",
  },
  {
    id: "emotional_healing", name: "柔らかなランタン",
    tagline: "悲しみは予定通りには進みません",
    icon: Heart, gradient: "from-rose-500 to-pink-600",
    bg: "bg-gradient-to-br from-rose-50 to-pink-50",
    accent: "text-rose-600", border: "border-rose-200", activeBorder: "border-rose-500",
    tags: ["癒し", "悲嘆", "優しさ"],
    coverStyle: "温かな水彩画、柔らかな光、親密なクローズアップ",
    proseStyle: "優しく、寄り添い、許可を与える",
    videoStyle: "親密な照明、窓の雨、温かなインテリア",
    sampleTitle: "今、大丈夫じゃなくていい",
    sampleSubtitle: "誰も準備してくれなかった悲嘆への伴走",
    sampleProse: "悲しみがこんな形で訪れるとは、誰も教えてくれませんでした——泣くような悲しみではなく、感覚が消えていく悲しみ。部屋に入った理由を忘れ、食べ物に味を感じられず、電話が鳴っても眺めるだけ。",
    sampleExercise: "観察者の実践：片手を胸に当てて。声に出して言いましょう：「これはつらい。この感情を感じていい。今すぐ解決しなくていい。」何かが変わるのを感じてみてください。",
    coverColors: ["#f43f5e", "#fb7185", "#ffe4e6"],
    emotions: ["孤独が和らいでいる", "許された気持ちになれる", "解放されている", "自分の身体の中に安心していられる", "希望が持てる"],
    visionVibe: "痛みが「生産的」である必要のない世界。悲しみが、アドバイスではなく、ただ寄り添いで迎えられる世界。読者は「直されること」ではなく、ようやく「見てもらえること」で癒しを見つけます。",
  },
  {
    id: "performance_focus", name: "クリアマインド・ラボ",
    tagline: "雑音を切り捨てて。大事なことを実行する。",
    icon: Zap, gradient: "from-amber-500 to-orange-600",
    bg: "bg-gradient-to-br from-amber-50 to-orange-50",
    accent: "text-amber-600", border: "border-amber-200", activeBorder: "border-amber-500",
    tags: ["集中", "規律", "実行"],
    coverStyle: "大胆なタイポグラフィ、シャープなコントラスト、幾何学的",
    proseStyle: "直接的で、力強く、行動志向",
    videoStyle: "速いカット、暗い背景、動くテキスト",
    sampleTitle: "スマホがあなたの人生を奪っている",
    sampleSubtitle: "深い集中を取り戻す21日プロトコル",
    sampleProse: "昼になる前にスマートフォンを47回確認した。自制心がないからではありません——あの画面のすべてのアプリが、あなたのドーパミン系を乗っ取るために、博士号を持つチームによって設計されているからです。",
    sampleExercise: "90分ブロック：タイマーを1つセット。タスクを1つ選ぶ。スマートフォンは別の部屋へ。タイマーが鳴ったら終了——完璧でなくても。それを世に出す。",
    coverColors: ["#d97706", "#f59e0b", "#fef3c7"],
    emotions: ["自分でコントロールできている", "頭がすっきりしている", "エネルギーが湧いている", "自信がある", "しなやかに立ち直れる"],
    visionVibe: "明確さが武器になる世界。行動が熟考を上回る世界。読者は情報の洪水を切り抜け、意志力に頼らず動くシステムを構築します。",
  },
  {
    id: "spiritual_awakening", name: "フェニックス・ライジング",
    tagline: "本当の自分が生きるために、古い自分は死ななければならない",
    icon: Flame, gradient: "from-purple-500 to-violet-600",
    bg: "bg-gradient-to-br from-purple-50 to-violet-50",
    accent: "text-purple-600", border: "border-purple-200", activeBorder: "border-purple-500",
    tags: ["目覚め", "意味", "深み"],
    coverStyle: "聖なる幾何学、宇宙的なグラデーション、ゴールドのアクセント",
    proseStyle: "瞑想的で、層が深く、詩的",
    videoStyle: "映画的な自然、宇宙的なイメージ、儀式的な動き",
    sampleTitle: "思考と思考の間の沈黙が神だ",
    sampleSubtitle: "すべてを試して諦めた人のための瞑想",
    sampleProse: "本を読み、アプリをダウンロードし、クッションに座って何かが起きるのを待った。何も起きませんでした——買い物リストが勝手に頭に浮かんできたことを除いて。",
    sampleExercise: "「間」の実践：目を閉じる。ひと息吸う。吸い込みの頂点で、息を吐く前に——その「間」に気づく。そこに留まる。それが扉です。",
    coverColors: ["#7c3aed", "#a78bfa", "#ede9fe"],
    emotions: ["今ここにいられる", "目的とつながっている", "グラウンデッド", "解放されている", "希望が持てる"],
    visionVibe: "日常の中に神聖なものが宿る世界。沈黙が空虚ではなく、輝いている世界。読者は、自分が探し求めていたものが、実は自分を探していたのだと気づきます。",
  },
];

const PERSONAS = [
  { id: "burned_out_pro", label: "燃え尽きたプロフェッショナル", emoji: "💼", desc: "消耗しきって、感覚が鈍く、ガス欠寸前で回している", needs: "リセット、安らぎ、止まっていいという許可", impact: "「日曜の憂鬱」と職場疲弊のナラティブに響くコンテンツフック" },
  { id: "gen_z_seeker", label: "Gen Z ナビゲーター", emoji: "🧭", desc: "圧倒されて、比較して、スクロールしてしまう", needs: "方向性、肯定感、実際に使えるツール", impact: "ショートフォームを優先、TikTokネイティブフック、脱ハッスルなトーン" },
  { id: "gen_alpha", label: "Gen Alpha エクスプローラー", emoji: "🌱", desc: "刺激過多の中で育ち、早くから感情への理解がある", needs: "年齢に合ったツール、感情の語彙、安全なガイダンス", impact: "ビジュアル重視のマンガ形式、ゲーム化されたエクササイズ、保護者にも安心" },
  { id: "grief_carrier", label: "悲嘆を抱える人", emoji: "🕯️", desc: "喪失、無感覚、うまく説明できない", needs: "寄り添い、優しさ、直そうとしないこと", impact: "許可を与える言葉、毒にならないポジティブさ、やわらかいCTA" },
  { id: "anxious_achiever", label: "不安を抱えた達成者", emoji: "⚡", desc: "外では成功しているのに、中では崩れそう", needs: "自律神経のサポート、正直さ", impact: "ハイパフォーマンスの枠組みに脆弱性への裏口を設ける" },
  { id: "spiritual_returner", label: "スピリチュアル・リターナー", emoji: "🌅", desc: "いろいろ試したのに、まだ探し続けている", needs: "深み、本物感、余計な飾りのないこと", impact: "濃密な内省的文体、伝統への敬意、グル否定のスタンス" },
  { id: "new_parent", label: "いっぱいいっぱいの親", emoji: "👶", desc: "アイデンティティを見失い、時間がなく、罪悪感がある", needs: "すぐ使えるツール、セルフコンパッション", impact: "マイクロフォーマット優先、罪悪感なしの枠組み、実践的なエクササイズ" },
];

const MOMENTS = [
  { id: "2am_overthinking", label: "深夜2時 — 考えが止まらない", scene: "暗い部屋、スマートフォンの光、頭の中が止まらない", emoji: "🌙", hookStyle: "眠れない感覚から始まり、思考の渦を肯定し、即効性のあるグラウンディングツールを一つ提示する" },
  { id: "after_breakup", label: "失恋や喪失のあと", scene: "空虚なアパート、静寂、感覚のなさ", emoji: "💔", hookStyle: "特定の悲しみの質感を言語化する——悲しみではなく麻痺感、食べ物に味がしないような感覚" },
  { id: "burnout_cant_quit", label: "燃え尽きているのに辞められない", scene: "会社のトイレ、深呼吸、また仮面をつける", emoji: "🔥", hookStyle: "仮面をつける瞬間に寄り添い、外での演技と内なる崩壊のギャップに語りかける" },
  { id: "feeling_behind", label: "人生で置いていかれている気がする", scene: "フィードをスクロール、みんな順調、自分だけ立ち止まっている", emoji: "📱", hookStyle: "比較スクロールを的確に捉え、「遅れている」を構造的な問題として再定義し、スマートフォン自体をトリガーとして転換する" },
  { id: "panic_spike", label: "パニック発作／不安の急上昇", scene: "胸が締め付けられ、息ができず、世界が狭まっていく", emoji: "😰", hookStyle: "身体感覚から始まる言葉、感情より先に体の感覚を言語化し、即座のソマティック介入を行う" },
  { id: "sunday_dread", label: "月曜前のサンデー・ドレッド", scene: "ソファ、時計の音、胃がずんと沈む", emoji: "⏰", hookStyle: "毎週繰り返される予期不安のサイクルに触れ、沈む感覚を肯定し、日曜日を取り戻す日として再定義する" },
];

const TRADITIONS = [
  "禅仏教", "スーフィー神秘主義", "ヴェーダーンタ", "密教（Vajrayana）", "道教",
  "ストア哲学", "仏教心理学", "ソマティック・セラピー", "ポリヴェーガル理論",
  "観想のキリスト教", "先住民の叡智", "世俗的マインドフルネス",
  "ブレスワーク科学", "深層心理学"
];

const VOICE_SLIDERS = [
  { id: "gentleDirect", left: "やさしい", right: "直接的", default: 50, color: "#6366f1", desc: "文章の柔らかさ、許可の言語と命令的表現のバランスを調整する" },
  { id: "simpleDeep", left: "シンプル", right: "深い", default: 50, color: "#059669", desc: "語彙の密度、メタファーの層、概念的な複雑さを調整する" },
  { id: "emotionalLogical", left: "感情的", right: "論理的", default: 25, color: "#f43f5e", desc: "ストーリーとデータの比率、脆弱性のレベル、分析的な枠組みを調整する" },
  { id: "spiritualPractical", left: "スピリチュアル", right: "実用的", default: 50, color: "#7c3aed", desc: "伝統への参照、神聖な言語、ツール優先と意味優先のバランスを調整する" },
];

const VISUAL_STYLES = [
  {
    id: "calm_minimal", label: "穏やか／ミニマル", desc: "すっきり、空気感があり、余白たっぷり",
    palette: ["#f8fafc", "#e2e8f0", "#94a3b8", "#475569"], mood: "穏やか、広がり、呼吸できる感じ",
    imagePrompt: "Minimalist book cover with vast white space, single delicate ink wash element floating in center, soft grey gradient background, thin sans-serif typography, Japanese zen aesthetic, editorial photography style, muted tones, clean geometric border",
    emotionPrompt: "Abstract soft watercolor wash in pale blue and white, single drop of color expanding outward in calm ripples, zen garden raked sand pattern, misty morning light, feeling of deep exhale and release",
  },
  {
    id: "dark_intense", label: "ダーク／インテンス", desc: "ムーディ、コントラスト強め、ドラマチック",
    palette: ["#1e1b4b", "#312e81", "#6366f1", "#c7d2fe"], mood: "力強い、没入感、映画的",
    imagePrompt: "Dramatic book cover with deep indigo and black, single shaft of violet light cutting through darkness, bold condensed typography, cinematic film grain, high contrast, moody atmospheric fog, Blade Runner color palette",
    emotionPrompt: "Person standing at edge of cliff at night, lightning illuminating the scene, dramatic cloud formations, deep indigo sky with electric violet lightning bolts, feeling of breakthrough power and transformation",
  },
  {
    id: "earthy_organic", label: "アーシー／オーガニック", desc: "自然なテクスチャ、温かいトーン",
    palette: ["#fef3c7", "#d97706", "#92400e", "#451a03"], mood: "地に足がついた、温かみ、テクスチャ感",
    imagePrompt: "Book cover with handmade paper texture, warm amber and brown tones, dried botanical pressed flowers, hand-lettered serif typography, golden hour light, natural linen texture background, artisan craft aesthetic",
    emotionPrompt: "Hands cupping warm soil with a seedling sprouting, golden sunlight filtering through oak leaves, warm terracotta and amber palette, feeling of rootedness and connection to earth, morning garden dew",
  },
  {
    id: "bold_modern", label: "大胆／モダン", desc: "シャープなタイポグラフィ、幾何学的",
    palette: ["#fafafa", "#18181b", "#ef4444", "#fbbf24"], mood: "エネルギッシュ、決断的、印象的",
    imagePrompt: "Bold book cover with stark black and white contrast, oversized helvetica bold typography, single red geometric accent shape, Swiss design grid layout, Bauhaus influence, high energy, magazine editorial style",
    emotionPrompt: "Abstract geometric explosion of red and yellow shapes on white background, sharp angular forms radiating outward, feeling of decisive action and clarity, kinetic energy frozen in motion",
  },
  {
    id: "premium_soft",
    label: "プレミアム／ジオメトリック",
    desc: "洗練、精密、ラグジュアリー寄りの位置づけ",
    palette: ["#fdf4ff", "#d8b4fe", "#7e22ce", "#3b0764"],
    mood: "格調高い、幾何学的、時代を超える",
    imagePrompt:
      "Premium luxury nonfiction book cover with precise geometric layout, thin elegant serif or restrained sans typography, subtle gold line or foil accent, controlled lavender and deep purple planes, editorial grid discipline, aspirational transformation",
    emotionPrompt:
      "Architectural light on refined surfaces, crisp geometric shadows, sense of order and quiet authority, timeless high-end publishing mood",
  },
  {
    id: "sacred_cosmic",
    label: "神秘的／深み",
    desc: "雰囲気があり、内省的で、ほのかに光が差す",
    palette: ["#0f172a", "#7c3aed", "#f59e0b", "#fef3c7"], mood: "興味をそそる、広がりがある、それでも商業性は保つ",
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
  "やっと落ち着ける": "/onboarding/proof/wizard/emotion_finally_calm.png",
  "自分の身体の中に安心していられる": "/onboarding/proof/wizard/emotion_safe_in_body.png",
  "頭がすっきりしている": "/onboarding/proof/wizard/emotion_clear_headed.png",
  "自分でコントロールできている": "/onboarding/proof/wizard/emotion_in_control.png",
  "休んでいいという許可": "/onboarding/proof/wizard/emotion_permission_rest.png",
  "エネルギーが湧いている": "/onboarding/proof/wizard/emotion_energized.png",
  "目的とつながっている": "/onboarding/proof/wizard/emotion_connected_purpose.png",
  "解放されている": "/onboarding/proof/wizard/emotion_released.png",
  "孤独が和らいでいる": "/onboarding/proof/wizard/emotion_less_alone.png",
  "許された気持ちになれる": "/onboarding/proof/wizard/emotion_forgiven.png",
  "グラウンデッド": "/onboarding/proof/wizard/emotion_grounded.png",
  "希望が持てる": "/onboarding/proof/wizard/emotion_hopeful.png",
  "今ここにいられる": "/onboarding/proof/wizard/emotion_present.png",
  "自信がある": "/onboarding/proof/wizard/emotion_confident.png",
  "しなやかに立ち直れる": "/onboarding/proof/wizard/emotion_resilient.png",
};

const TOPIC_TAG_PROOF_URL = Object.fromEntries(
  [
    "anxiety-at-night",
    "考えすぎ",
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
    keywords: ["nervous system regulation audiobook", "燃え尽きからの回復", "stop overthinking at night", "anxiety before sleep", "polyvagal calm"],
  },
  identity_direction: {
    personas: ["Gen Z navigating adulting 18-24 (fastest-growing segment)", "Millennial women career transition 30-44", "Identity rebuilders post-divorce 28-50"],
    topics: ["feeling behind compared to peers", "lost sense of purpose after 30", "quarter-life crisis", "rebuilding identity after breakup", "what to do with your life"],
    keywords: ["feeling lost in life audiobook", "クォーターライフクライシス", "finding purpose", "identity crisis self help", "what am I doing with my life"],
  },
  emotional_healing: {
    personas: ["Grief/loss navigators all ages ($70-100M/yr)", "Trauma-aware millennials body-based recovery", "Parents processing intergenerational patterns"],
    topics: ["grief that doesn't follow a timeline", "healing after toxic relationship", "世代間トラウマ", "失恋からの回復", "感情の麻痺"],
    keywords: ["grief audiobook", "healing after breakup", "trauma recovery self help", "emotional healing", "letting go of past"],
  },
  performance_focus: {
    personas: ["Corporate middle managers 32-50 ($50-80M/yr)", "Entrepreneurs/solopreneurs 28-50 ($60-100M/yr)", "Tech workers seeking focus 25-40"],
    topics: ["phone addiction destroying focus", "can't stick to habits", "decision fatigue as a manager", "ADHD-friendly productivity", "ドーパミンデトックス"],
    keywords: ["focus audiobook", "productivity self help", "習慣の構築", "ADHD focus techniques", "deep work practice"],
  },
  spiritual_awakening: {
    personas: ["Gen X wisdom seekers 45-58 ($165M/yr highest-spending)", "Contemplative professionals seeking meaning", "Post-crisis seekers finding new framework"],
    topics: ["meditation that actually works for beginners", "finding meaning after loss", "spiritual practice without religion", "inner peace in chaos", "mindfulness for skeptics"],
    keywords: ["meditation audiobook", "finding inner peace", "spiritual growth", "mindfulness for beginners", "meaning of life self help"],
  },
};

// V4 Angles
const V4_ANGLES = [
  { id: "debunk", label: "誤解を正す", desc: "主流の通説に挑む —「セラピストが教えてくれないこと」", framing: "逆張りフック、証拠に基づく転換", icon: AlertTriangle },
  { id: "framework", label: "フレームワーク", desc: "システムを与える —「〇〇のための5ステップ」", framing: "構造的・反復可能・ツール優先", icon: Layers },
  { id: "reveal", label: "お披露目", desc: "隠れた真実を暴く —「眠れない本当の理由」", framing: "インサイダーな知識、「誰も話さないこと」", icon: Eye },
  { id: "leverage", label: "活用する", desc: "すでに持っているものを使う —「あなたの不安は超能力だ」", framing: "既存の特性を強みとして再定義", icon: Zap },
  { id: "origin", label: "原点", desc: "根本を辿る —「あなたのパターンが始まった場所」", framing: "ナラティブの深さ、因果の連鎖、「気づき」の瞬間", icon: Search },
];

// V4 Formats
const V4_FORMATS_STRUCTURAL = [
  { id: "F001", label: "スタンダード自己啓発", chapters: "12-16", tier: "full", desc: "演習を織り込んだクラシックな物語構成" },
  { id: "F002", label: "ガイド付きプログラム", chapters: "8-12", tier: "full", desc: "ステップ・バイ・ステップの変容プロトコル" },
  { id: "F003", label: "デイリー・ジャーナル", chapters: "30-90", tier: "micro", desc: "1日1ページ、内省中心" },
  { id: "F004", label: "ソマティック・ワークブック", chapters: "10-14", tier: "full", desc: "身体優先の演習、最小限のナラティブ" },
  { id: "F005", label: "ナラティブ・ジャーニー", chapters: "14-20", tier: "full", desc: "ストーリー主導、深い感情の弧" },
  { id: "F006", label: "凝縮された知恵", chapters: "6-8", tier: "mini", desc: "密度が高く、インパクト大、短時間で読める" },
];

// ═══════════════════════════════════════════════════════════
// VOICE TONE DATA — 10 positions per slider with benefits
// ═══════════════════════════════════════════════════════════

const VOICE_TONE_10 = {
  gentleDirect: [
    {
      position: 1, label: "超優しい",
      technique: "'You might notice...' で始まる — 命令せず、読者と並んで観察するだけ",
      benefits: [
        "TODO_JA:voiceToneBenefits.gentleDirect.p1.b0",
        "TODO_JA:voiceToneBenefits.gentleDirect.p1.b1",
        "TODO_JA:voiceToneBenefits.gentleDirect.p1.b2",
        "TODO_JA:voiceToneBenefits.gentleDirect.p1.b3",
        "TODO_JA:voiceToneBenefits.gentleDirect.p1.b4",
      ],
    },
    {
      position: 2, label: "とても優しい",
      technique: "許可の言語を使う：'It's okay to...'（〜していいんですよ）や'You're allowed to...'（〜が許されています）",
      benefits: [
        "TODO_JA:voiceToneBenefits.gentleDirect.p2.b0",
        "TODO_JA:voiceToneBenefits.gentleDirect.p2.b1",
        "TODO_JA:voiceToneBenefits.gentleDirect.p2.b2",
        "TODO_JA:voiceToneBenefits.gentleDirect.p2.b3",
        "TODO_JA:voiceToneBenefits.gentleDirect.p2.b4",
      ],
    },
    {
      position: 3, label: "やさしい",
      technique: "エクササイズは指示ではなく招待として提示 — 'If you'd like, try...'（よければ、試してみてください）",
      benefits: [
        "TODO_JA:voiceToneBenefits.gentleDirect.p3.b0",
        "TODO_JA:voiceToneBenefits.gentleDirect.p3.b1",
        "エクササイズの完了率が高い — 招待は命令より安心感がある",
        "TODO_JA:voiceToneBenefits.gentleDirect.p3.b2",
        "TODO_JA:voiceToneBenefits.gentleDirect.p3.b3",
      ],
    },
    {
      position: 4, label: "ソフト",
      technique: "意図的な間と呼吸を意識したリズムによる、ゆったりとした文章テンポ",
      benefits: [
        "TODO_JA:voiceToneBenefits.gentleDirect.p4.b0",
        "TODO_JA:voiceToneBenefits.gentleDirect.p4.b1",
        "TODO_JA:voiceToneBenefits.gentleDirect.p4.b2",
        "オーディオブック版はパニック時の落ち着き手段として機能する",
        "TODO_JA:voiceToneBenefits.gentleDirect.p4.b3",
      ],
    },
    {
      position: 5, label: "バランス・やさしめ",
      technique: "方向性を示す前に承認する — まず感情を認め、それから道を提示する",
      benefits: [
        "TODO_JA:voiceToneBenefits.gentleDirect.p5.b0",
        "TODO_JA:voiceToneBenefits.gentleDirect.p5.b1",
        "TODO_JA:voiceToneBenefits.gentleDirect.p5.b2",
        "TODO_JA:voiceToneBenefits.gentleDirect.p5.b3",
        "TODO_JA:voiceToneBenefits.gentleDirect.p5.b4",
      ],
    },
    {
      position: 6, label: "バランス・直接的",
      technique: "温かみを持った明確な真実の表明 — 'Here's what's actually happening'（これが実際に起きていることです）",
      benefits: [
        "TODO_JA:voiceToneBenefits.gentleDirect.p6.b0",
        "TODO_JA:voiceToneBenefits.gentleDirect.p6.b1",
        "TODO_JA:voiceToneBenefits.gentleDirect.p6.b2",
        "TODO_JA:voiceToneBenefits.gentleDirect.p6.b3",
        "TODO_JA:voiceToneBenefits.gentleDirect.p6.b4",
      ],
    },
    {
      position: 7, label: "ファーム",
      technique: "行動優先の文章構成 — まず何をすべきかを示し、理由はその後で説明する",
      benefits: [
        "TODO_JA:voiceToneBenefits.gentleDirect.p7.b0",
        "TODO_JA:voiceToneBenefits.gentleDirect.p7.b1",
        "TODO_JA:voiceToneBenefits.gentleDirect.p7.b2",
        "TODO_JA:voiceToneBenefits.gentleDirect.p7.b3",
        "TODO_JA:voiceToneBenefits.gentleDirect.p7.b4",
      ],
    },
    {
      position: 8, label: "直接的",
      technique: "短くて力強い文章。無駄なし。すべての言葉が役割を果たす。",
      benefits: [
        "TODO_JA:voiceToneBenefits.gentleDirect.p8.b0",
        "TODO_JA:voiceToneBenefits.gentleDirect.p8.b1",
        "TODO_JA:voiceToneBenefits.gentleDirect.p8.b2",
        "TODO_JA:voiceToneBenefits.gentleDirect.p8.b3",
        "TODO_JA:voiceToneBenefits.gentleDirect.p8.b4",
      ],
    },
    {
      position: 9, label: "かなり率直",
      technique: "対立的な誠実さ — 'You already know this. You're avoiding it.'（あなたはすでに知っている。避けているだけだ。）",
      benefits: [
        "TODO_JA:voiceToneBenefits.gentleDirect.p9.b0",
        "TODO_JA:voiceToneBenefits.gentleDirect.p9.b1",
        "TODO_JA:voiceToneBenefits.gentleDirect.p9.b2",
        "TODO_JA:voiceToneBenefits.gentleDirect.p9.b3",
        "TODO_JA:voiceToneBenefits.gentleDirect.p9.b4",
      ],
    },
    {
      position: 10, label: "超率直",
      technique: "命令形と指示 — 'Stop reading. Do this now. Then come back.'（読むのをやめろ。今すぐやれ。それから戻ってこい。）",
      benefits: [
        "TODO_JA:voiceToneBenefits.gentleDirect.p10.b0",
        "TODO_JA:voiceToneBenefits.gentleDirect.p10.b1",
        "オーディオブック版はリアルタイムのコーチングセッションとして機能する",
        "TODO_JA:voiceToneBenefits.gentleDirect.p10.b2",
        "TODO_JA:voiceToneBenefits.gentleDirect.p10.b3",
      ],
    },
  ],
  simpleDeep: [
    {
      position: 1, label: "超シンプル",
      technique: "小学校5年生レベルの読みやすさ — すべての文が完全に明快で専門用語ゼロ",
      benefits: [
        "TODO_JA:voiceToneBenefits.simpleDeep.p1.b0",
        "TODO_JA:voiceToneBenefits.simpleDeep.p1.b1",
        "TODO_JA:voiceToneBenefits.simpleDeep.p1.b2",
        "TODO_JA:voiceToneBenefits.simpleDeep.p1.b3",
        "オーディオブックの理解度が最も高い — 巻き戻す必要がない",
      ],
    },
    {
      position: 2, label: "とてもシンプル",
      technique: "段落ごとに一つの概念 — 小さく明確なブロックで理解を積み上げる",
      benefits: [
        "TODO_JA:voiceToneBenefits.simpleDeep.p2.b0",
        "TODO_JA:voiceToneBenefits.simpleDeep.p2.b1",
        "TODO_JA:voiceToneBenefits.simpleDeep.p2.b2",
        "TODO_JA:voiceToneBenefits.simpleDeep.p2.b3",
        "エクササイズ完了率が高い — 指示が誤解不可能",
      ],
    },
    {
      position: 3, label: "シンプル",
      technique: "日常的な比喩 — 'It's like clearing your browser tabs'（ブラウザのタブを閉じるようなもの）",
      benefits: [
        "TODO_JA:voiceToneBenefits.simpleDeep.p3.b0",
        "TODO_JA:voiceToneBenefits.simpleDeep.p3.b1",
        "TODO_JA:voiceToneBenefits.simpleDeep.p3.b2",
        "TODO_JA:voiceToneBenefits.simpleDeep.p3.b3",
        "TODO_JA:voiceToneBenefits.simpleDeep.p3.b4",
      ],
    },
    {
      position: 4, label: "アクセシブル",
      technique: "時折深みを持つ明確な説明 — 章ごとに一つの新しい用語を導入する",
      benefits: [
        "TODO_JA:voiceToneBenefits.simpleDeep.p4.b0",
        "TODO_JA:voiceToneBenefits.simpleDeep.p4.b1",
        "TODO_JA:voiceToneBenefits.simpleDeep.p4.b2",
        "TODO_JA:voiceToneBenefits.simpleDeep.p4.b3",
        "TODO_JA:voiceToneBenefits.simpleDeep.p4.b4",
      ],
    },
    {
      position: 5, label: "バランス型",
      technique: "平易な言葉と豊かな概念の混在 — 'simply put'（簡単に言えば）のような橋渡し表現を使用",
      benefits: [
        "TODO_JA:voiceToneBenefits.simpleDeep.p5.b0",
        "TODO_JA:voiceToneBenefits.simpleDeep.p5.b1",
        "オーディオブックでの転換がスムーズ — ナレーターが深さの変化を伝えられる",
        "TODO_JA:voiceToneBenefits.simpleDeep.p5.b2",
        "TODO_JA:voiceToneBenefits.simpleDeep.p5.b3",
      ],
    },
    {
      position: 6, label: "思慮深い",
      technique: "複数の文で考えを展開 — 洞察に至る前に論点を積み上げる",
      benefits: [
        "TODO_JA:voiceToneBenefits.simpleDeep.p6.b0",
        "TODO_JA:voiceToneBenefits.simpleDeep.p6.b1",
        "TODO_JA:voiceToneBenefits.simpleDeep.p6.b2",
        "TODO_JA:voiceToneBenefits.simpleDeep.p6.b3",
        "TODO_JA:voiceToneBenefits.simpleDeep.p6.b4",
      ],
    },
    {
      position: 7, label: "リッチ",
      technique: "重層的な意味 — 表面的に読んでも成立するが、再読することでより深い意味が現れる",
      benefits: [
        "TODO_JA:voiceToneBenefits.simpleDeep.p7.b0",
        "TODO_JA:voiceToneBenefits.simpleDeep.p7.b1",
        "音声版は繰り返し聴くことで報われる — リピートエンゲージメントを促進",
        "TODO_JA:voiceToneBenefits.simpleDeep.p7.b2",
        "TODO_JA:voiceToneBenefits.simpleDeep.p7.b3",
      ],
    },
    {
      position: 8, label: "深い",
      technique: "哲学と科学を織り交ぜる — 説教せずに研究を引用する",
      benefits: [
        "TODO_JA:voiceToneBenefits.simpleDeep.p8.b0",
        "TODO_JA:voiceToneBenefits.simpleDeep.p8.b1",
        "TODO_JA:voiceToneBenefits.simpleDeep.p8.b2",
        "TODO_JA:voiceToneBenefits.simpleDeep.p8.b3",
        "TODO_JA:voiceToneBenefits.simpleDeep.p8.b4",
      ],
    },
    {
      position: 9, label: "かなり深い",
      technique: "学際的な総合 — 神経科学、哲学、実践をつなぎ合わせる",
      benefits: [
        "TODO_JA:voiceToneBenefits.simpleDeep.p9.b0",
        "TODO_JA:voiceToneBenefits.simpleDeep.p9.b1",
        "TODO_JA:voiceToneBenefits.simpleDeep.p9.b2",
        "プレミアムオーディオブック価格に見合う — 長時間音声に十分な内容",
        "TODO_JA:voiceToneBenefits.simpleDeep.p9.b3",
      ],
    },
    {
      position: 10, label: "超深い",
      technique: "大学院レベルの概念と独自のフレームワーク — 読者に成長を促す",
      benefits: [
        "TODO_JA:voiceToneBenefits.simpleDeep.p10.b0",
        "TODO_JA:voiceToneBenefits.simpleDeep.p10.b1",
        "TODO_JA:voiceToneBenefits.simpleDeep.p10.b2",
        "TODO_JA:voiceToneBenefits.simpleDeep.p10.b3",
        "TODO_JA:voiceToneBenefits.simpleDeep.p10.b4",
      ],
    },
  ],
  emotionalLogical: [
    {
      position: 1, label: "超感情的",
      technique: "章はストーリーから始まる — すべての概念が実体験の語りを通して登場する",
      benefits: [
        "TODO_JA:voiceToneBenefits.emotionalLogical.p1.b0",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p1.b1",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p1.b2",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p1.b3",
        "オーディオブック版が伴侶になる — リスナーがナレーターと疑似社会的絆を形成する",
      ],
    },
    {
      position: 2, label: "とても感情的",
      technique: "文章に高い脆弱性 — 著者自身の傷が文章の中に見える",
      benefits: [
        "TODO_JA:voiceToneBenefits.emotionalLogical.p2.b0",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p2.b1",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p2.b2",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p2.b3",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p2.b4",
      ],
    },
    {
      position: 3, label: "感情的",
      technique: "エクササイズにはジャーナリングや体感作業が含まれる — 'Notice what arises'（何が湧き上がるかに気づいてください）",
      benefits: [
        "TODO_JA:voiceToneBenefits.emotionalLogical.p3.b0",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p3.b1",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p3.b2",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p3.b3",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p3.b4",
      ],
    },
    {
      position: 4, label: "温かみのある",
      technique: "読者を 'you'（あなた）と親密な口調で呼ぶ — 親しい友人からの手紙のように",
      benefits: [
        "TODO_JA:voiceToneBenefits.emotionalLogical.p4.b0",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p4.b1",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p4.b2",
        "オーディオブックがプライベートなセラピーセッションのように感じられる — 深い個人的つながり",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p4.b3",
      ],
    },
    {
      position: 5, label: "バランス型",
      technique: "感情的な導入、論理的な中盤、統合的な結末 — 各章がひとつの旅",
      benefits: [
        "TODO_JA:voiceToneBenefits.emotionalLogical.p5.b0",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p5.b1",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p5.b2",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p5.b3",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p5.b4",
      ],
    },
    {
      position: 6, label: "論理的",
      technique: "エビデンスに支えられたストーリーテリング — データを説明するためにストーリーを使う（逆ではない）",
      benefits: [
        "TODO_JA:voiceToneBenefits.emotionalLogical.p6.b0",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p6.b1",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p6.b2",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p6.b3",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p6.b4",
      ],
    },
    {
      position: 7, label: "分析的",
      technique: "構造化された論証 — 主張、証拠、示唆、行動",
      benefits: [
        "TODO_JA:voiceToneBenefits.emotionalLogical.p7.b0",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p7.b1",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p7.b2",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p7.b3",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p7.b4",
      ],
    },
    {
      position: 8, label: "論理的",
      technique: "データ主導の章 — 数値・研究・指標がすべての主張の根拠となる",
      benefits: [
        "TODO_JA:voiceToneBenefits.emotionalLogical.p8.b0",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p8.b1",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p8.b2",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p8.b3",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p8.b4",
      ],
    },
    {
      position: 9, label: "かなり論理的",
      technique: "読者を有能な意思決定者として扱う — 知性ある大人として接する",
      benefits: [
        "TODO_JA:voiceToneBenefits.emotionalLogical.p9.b0",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p9.b1",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p9.b2",
        "コンテンツが基調講演に転用できる — 論理的構造がステージで映える",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p9.b3",
      ],
    },
    {
      position: 10, label: "超論理的",
      technique: "変革を測定可能な成果を伴う体系的なスキル習得として位置づける",
      benefits: [
        "TODO_JA:voiceToneBenefits.emotionalLogical.p10.b0",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p10.b1",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p10.b2",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p10.b3",
        "TODO_JA:voiceToneBenefits.emotionalLogical.p10.b4",
      ],
    },
  ],
  spiritualPractical: [
    {
      position: 1, label: "超スピリチュアル",
      technique: "伝統、系譜、聖なる師への言及が随所に織り込まれる",
      benefits: [
        "TODO_JA:voiceToneBenefits.spiritualPractical.p1.b0",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p1.b1",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p1.b2",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p1.b3",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p1.b4",
      ],
    },
    {
      position: 2, label: "とてもスピリチュアル",
      technique: "神聖な言語：'presence'（存在）、'awareness'（気づき）、'witness'（目撃者）、'the great turning'（大いなる転換）",
      benefits: [
        "TODO_JA:voiceToneBenefits.spiritualPractical.p2.b0",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p2.b1",
        "オーディオブック版がガイド付き瞑想として機能する — 二重用途コンテンツ",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p2.b2",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p2.b3",
      ],
    },
    {
      position: 3, label: "スピリチュアル",
      technique: "エクササイズには瞑想、黙想、沈黙を基盤とした実践が含まれる",
      benefits: [
        "TODO_JA:voiceToneBenefits.spiritualPractical.p3.b0",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p3.b1",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p3.b2",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p3.b3",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p3.b4",
      ],
    },
    {
      position: 4, label: "意味優先",
      technique: "意味の創造が主要な目標 — 'Why am I here?'（私はなぜここにいるのか？）に正面から向き合う",
      benefits: [
        "TODO_JA:voiceToneBenefits.spiritualPractical.p4.b0",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p4.b1",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p4.b2",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p4.b3",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p4.b4",
      ],
    },
    {
      position: 5, label: "バランス型",
      technique: "内なる変容を外の行動につなげる — 黙想が実行と出会う",
      benefits: [
        "TODO_JA:voiceToneBenefits.spiritualPractical.p5.b0",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p5.b1",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p5.b2",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p5.b3",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p5.b4",
      ],
    },
    {
      position: 6, label: "グラウンデッド",
      technique: "精神的な洞察を日常の習慣やルーティンに落とし込む",
      benefits: [
        "TODO_JA:voiceToneBenefits.spiritualPractical.p6.b0",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p6.b1",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p6.b2",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p6.b3",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p6.b4",
      ],
    },
    {
      position: 7, label: "実践的",
      technique: "ツール優先の章構成 — テクニックを提示し、使うべき場面を示し、なぜ機能するかを説明する",
      benefits: [
        "TODO_JA:voiceToneBenefits.spiritualPractical.p7.b0",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p7.b1",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p7.b2",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p7.b3",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p7.b4",
      ],
    },
    {
      position: 8, label: "実用的",
      technique: "機能的な言語：'system'（システム）、'protocol'（プロトコル）、'technique'（テクニック）— 伝統への言及はゼロ",
      benefits: [
        "TODO_JA:voiceToneBenefits.spiritualPractical.p8.b0",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p8.b1",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p8.b2",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p8.b3",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p8.b4",
      ],
    },
    {
      position: 9, label: "かなり実用的",
      technique: "行動変容が主要な目標 — 測定可能な成果を追跡する",
      benefits: [
        "TODO_JA:voiceToneBenefits.spiritualPractical.p9.b0",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p9.b1",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p9.b2",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p9.b3",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p9.b4",
      ],
    },
    {
      position: 10, label: "超実用的",
      technique: "純粋なプロトコル — 測定可能な成果を伴う実行可能な内容、各章がインストールすべきシステム",
      benefits: [
        "TODO_JA:voiceToneBenefits.spiritualPractical.p10.b0",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p10.b1",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p10.b2",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p10.b3",
        "TODO_JA:voiceToneBenefits.spiritualPractical.p10.b4",
      ],
    },
  ],
};

// ═══════════════════════════════════════════════════════════
// SHARED COMPONENTS
// ═══════════════════════════════════════════════════════════

function StepHero({ eyebrow, title, subtitle, helper }) {
  const { t } = useJaWizardTranslation();
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
  const isComplete = step === total - 2; // step 7 ("あなたのブランド") only
  const pct = isComplete ? 100 : ((step + 1) / total) * 100;
  return (
    <div className="brand-studio-panel mb-6 px-5 py-4 sm:mb-8">
      {isComplete && (
        <p className="text-center text-3xl font-extrabold mb-3" style={{ color: '#d97706', fontFamily: 'Cormorant Garamond, serif' }}>
          {t("ui", "おめでとうございます — ブランドが100%設定されました！")}
        </p>
      )}
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-wider text-violet-600">
            {isComplete ? t("ui", "完了") : t("ui", "ステップ {n} / {total}").replace("{n}", step + 1).replace("{total}", total)}
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
  const labels = ["感じる", "考える", "Do", "シェアする", "信頼", "リターン"];
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
      systemEffect: "すべてのタイトルにわたり、呼吸を意識したペーシング、身体的エクササイズ、調整優先の構成を文体に設定する",
      emotionalBenefit: "あなたの読者の神経系は最初の段落からダウンレギュレートする。コンテンツは共同調整ツールとして機能する——コルチゾールを下げ、心拍数を遅くし、休むことへの許可を与える。読者は文章そのものに「抱かれている」と感じると報告する。",
    },
    identity_direction: {
      systemEffect: "前進する文体、誠実な内省エクササイズ、反比較フック戦略を有効にする",
      emotionalBenefit: "読者はスクロールをやめて選択し始める。これは「何をすべきか分からない」という麻痺をモメンタムへと変える。各章が小さく勇敢な決断を通じてアイデンティティを再構築する——遅れている恥を打ち消しながら。",
    },
    emotional_healing: {
      systemEffect: "優しさ優先の言語、証人ベースのエクササイズ、悲しみに精通したコンテンツペーシングを可能にする",
      emotionalBenefit: "読者は「修正される」のではなく「見てもらえる」と感じる。これは悲しみと痛みに存在感をもって寄り添う——毒性のあるポジティブさもなく、タイムラインもなく、「もう乗り越えるべき」という言葉もない。多くの読者がかつて持てなかった、思いやりある証人の役割を果たす。",
    },
    performance_focus: {
      systemEffect: "行動優先の文体、プロトコルベースのエクササイズ、ノイズカットフック戦略を取り入れる",
      emotionalBenefit: "読者は情報過負荷を突き抜け、何週間かぶりに初めての本物の行動を取る。これは決断疲労を減らし、意志力ではなく構造で動くシステムを構築し、コントロールしている感覚を取り戻す。",
    },
    spiritual_awakening: {
      systemEffect: "瞑想的な文体の層、ギャップ認識エクササイズ、意味探求フック戦略を有効にする",
      emotionalBenefit: "読者は追い求めてきたものがずっと自分の内側にあったと気づく。これは表面だけの世界に深みのための空間を作り出す——知的なセルフヘルプが届けなかった場所でスピリチュアルな探求者と出会う。",
    },
  },
  personas: {
    burned_out_pro: { systemEffect: "疲弊フック、「日曜の恐怖」ナラティブ、辞めずに回復するフレーミングを中心にタイトルを調整する", emotionalBenefit: "コンテンツはサバイバルモードにある人々に届く——罪悪感もなく、「もっと頑張って」もない。あなたのブランドは「あなたは怠惰ではなく、消耗している」と言い、それを本当に意味する最初の声になる。" },
    gen_z_seeker: { systemEffect: "ショートフォームフック、TikTokネイティブ言語、アンチハッスルトーン、スクロールを止めるオープニングのために最適化する", emotionalBenefit: "あなたのブランドはGen Zのネイティブ言語で出会う——真正性を最優先に。パフォーマティブなウェルネスの海の中で信頼される声となり、恥ずかしさのない本物のツールを提供する。" },
    gen_alpha: { systemEffect: "マンガ優先フォーマット、ビジュアルストーリーテリング、ゲーミファイドなエクササイズ、保護者向け安全コンテンツフィルターを有効にする", emotionalBenefit: "幼少期から感情の語彙を持つ最初の世代のためのコンテンツを構築している。ビジュアルフォーマットは親世代が持てなかったツールを与える——年齢に適切で真に役立つものを。" },
    grief_carrier: { systemEffect: "許可を与える言語、ソフトなCTA、毒性のあるポジティブさなし、証人ベースのエクササイズ構造を設定する", emotionalBenefit: "あなたのブランドは名前のない悲しみの中のコンパニオンになる——誰も彼らに備えさせなかった種類の悲しみの。修正もなく、タイムラインもない。ただ存在と、大丈夫でなくていいという根本的な許可だけ。" },
    anxious_achiever: { systemEffect: "高パフォーマンスのフレーミングと脆弱性への裏口、神経系サポート、インポスター症候群フックを橋渡しする", emotionalBenefit: "外見は問題なく見えて内側が崩れている人々に届く。あなたのブランドは達成言語と脆弱性を橋渡しする——達成者が実際に歩む癒しへの裏口。" },
    spiritual_returner: { systemEffect: "密度の高い瞑想的な文体、伝統を意識した引用、反グル的ポジショニング、深み優先フックを有効にする", emotionalBenefit: "あなたのブランドは何でも試して浅い答えに疲弊した人々に語りかける。彼らの知性を尊重し、その深みに応える、密度のある真正なコンテンツ。" },
    new_parent: { systemEffect: "マイクロフォーマット配信、罪悪感なしのフレーミング、クイックツールエクササイズ、昼寝時間の長さのコンテンツを優先する", emotionalBenefit: "あなたのブランドは盗まれた瞬間の親たちに届く——深夜3時の授乳、昼寝中のスクロール。ゼロ罪悪感のマイクロフォーマットツールが、圧倒感を増やさずにアイデンティティを取り戻す助けをする。" },
  },
  moments: {
    "2am_overthinking": { systemEffect: "感覚ベースの言語で始まり、螺旋状の感覚を肯定し、最初の30秒以内に即座のグラウンディングツールを提供する", emotionalBenefit: "コンテンツは脆弱性のまさにその瞬間に届く——眠れずに横たわり、スマートフォンが光り、思考が駆け回る瞬間に。フックが刺さるのは、今まさに身体で感じていることを言い当てているからだ。" },
    "after_breakup": { systemEffect: "特定の麻痺の種類に名前をつけ、アドバイスを避け、喪失の身体的認識でリードする", emotionalBenefit: "誰も語らない麻痺の中で出会う——泣くような麻痺ではなく、食べ物に味がしないような麻痺に。あなたのブランドは彼らが言葉にできないものに名前をつける、それだけで癒しが始まる。" },
    "burnout_cant_quit": { systemEffect: "「仮面をつける瞬間」を捉え、公と私のギャップに語りかけ、回復をぜいたくではなくスキルとして位置づける", emotionalBenefit: "洗面台の鏡の前と仮面をつけ直す間の瞬間に語りかける。コンテンツはパフォーマンスしている自分と本当の自分のギャップを肯定する——ふりをやめることへの許可を与える。" },
    "feeling_behind": { systemEffect: "比較スクロール行動をターゲットにし、「遅れている」を「構築中」として捉え直し、スマートフォンをトリガーオブジェクトに変える", emotionalBenefit: "比較スクロールを真実で中断する：彼らは遅れていない、構築中だ。スマートフォン自体がトリガーオブジェクトとなり、無意識のスクロールを誠実な自己省察へと変える。" },
    "panic_spike": { systemEffect: "身体感覚から始まる言葉、感情より先に体の感覚を言語化し、即座のソマティック介入を行う within 10 seconds", emotionalBenefit: "心が離れてしまったとき、コンテンツは身体優先の言語を使う。パニックの中では、心が何かを処理できる前に、身体が「あなたを見ている」という言葉を必要としている。これは現実の瞬間に本物の人々を救う。" },
    "sunday_dread": { systemEffect: "週次の不安サイクルに触れ、沈んでいく感覚を肯定し、日曜日をカウントダウンではなく取り戻しとして捉え直す", emotionalBenefit: "何百万人もが感じながらも言葉にできない週次の恐怖感に名前をつける。あなたのブランドは日曜日を不安から取り戻す——沈んでいく感覚を準備とセルフコンパッションの儀式へと変える。" },
  },
  visualStyles: {
    calm_minimal: { systemEffect: "広大な余白、柔らかなインクウォッシュ、禅的美学、ミュートパレットを持つ表紙を生成する", emotionalBenefit: "読者は視覚的な安堵を体験する——余白は「ここで息ができる」というシグナルを発する。表紙は本を開く前から瞑想のように感じられる。刺激過多な読者の視覚的不安を和らげる。" },
    dark_intense: { systemEffect: "深いインディゴ／ブラック、ドラマチックな照明、シネマティックなグレイン、高コントラストを持つ表紙を生成する", emotionalBenefit: "読者は自分自身の変容の重力を感じる。ダークな美学が深みをシグナリングする——これは穏やかなウェルネスではなく、本物の作業だ。柔らかな見た目のセルフヘルプを信頼しない読者を引きつける。" },
    earthy_organic: { systemEffect: "手作りテクスチャー、植物要素、温かいアンバートーン、職人的美学を持つ表紙を生成する", emotionalBenefit: "読者は一言も読む前にグラウンドされた感覚を覚える。自然のテクスチャーがバイオフィリックな落ち着きをトリガーする——脳はオーガニックなビジュアルを「安全」と解釈する。身体的・自然基盤の癒しに強力。" },
    bold_modern: { systemEffect: "極端なコントラスト、特大タイポグラフィ、赤の幾何学的アクセント、スイスデザイングリッドを持つ表紙を生成する", emotionalBenefit: "読者は活力と決断力を感じる。大胆なビジュアルは棚のノイズとスクロール疲れを切り裂く。「これは違う」というシグナルを発し——パステルカラーのウェルネスに飽き飽きした行動指向の読者を引きつける。" },
    premium_soft: { systemEffect: "幾何学的構造、精密なタイポグラフィ階層、ゴールドのアクセントライン、統制されたラグジュアリーパレットを持つ表紙を生成する", emotionalBenefit: "読者は権威あり意図的なものを手にしていると感じる。幾何学的プレミアムは技巧と明確さをシグナリングする——編集としての信頼性を持つ変容を求める購入者を引きつける。" },
    sacred_cosmic: { systemEffect: "神秘的な雰囲気の表紙を生成する——深いブルーとバイオレット、繊細な光、ホラーなき瞑想的な深み", emotionalBenefit: "読者は好奇心と内なる広がりを感じる。神秘的なビジュアルはファンタジーの過負荷なく深みを求める人を惹きつける——棚上でもサムネイルでも磁力を持つ。" },
  },
  formats: {
    manga: { systemEffect: "カタログプランナーはイラストパネル、ショートフォームオーディオブック（15〜30分）、全チャネルにわたるビジュアルストーリーテリングを優先する", emotionalBenefit: "ビジュアル優先の読者はテキストより速く画像を通じて感情を処理する。マンガは読書不安を和らげ、Gen Z／Alphaにネイティブに語りかけ、複雑な心理的概念をストーリーを通じてアクセス可能にする。" },
    book: { systemEffect: "カタログプランナーはフルレングスのナラティブ、深いプログラム、包括的なワークブック、長形式のオーディオブック（3〜8時間）を優先する", emotionalBenefit: "深く読む読者は没入感を渇望する——長形式は彼らにスローダウンして深みに進む許可を与える。フルレングスの本はコンパニオンとなり、持続的な変容をもたらす集中力を育む。" },
  },
};

function SelectionFeedback({ systemEffect, emotionalBenefit, color = "#6366f1" }) {
  if (!systemEffect && !emotionalBenefit) return null;
  return (
    <div className="mt-4 rounded-xl border overflow-hidden" style={{ borderColor: color + '30' }}>
      <div className="px-4 py-2.5 flex items-center gap-2" style={{ backgroundColor: color + '08' }}>
        <Sparkles size={13} style={{ color }} />
        <span className="text-[11px] font-bold" style={{ color }}>これが有効化するもの</span>
      </div>
      <div className="px-4 py-3 bg-white">
        <div className="flex items-start gap-2 mb-2.5">
          <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: color + '15' }}>
            <Zap size={10} style={{ color }} />
          </div>
          <div>
            <div className="text-[9px] font-bold uppercase text-white mb-0.5">システム内で</div>
            <p className="text-[11px] text-white leading-relaxed">{systemEffect}</p>
          </div>
        </div>
        <div className="flex items-start gap-2">
          <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: color + '15' }}>
            <Heart size={10} style={{ color }} />
          </div>
          <div>
            <div className="text-[9px] font-bold uppercase text-white mb-0.5">あなたの読者へ</div>
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
        <span className="text-xs font-bold text-white">{label || "これが変えること"}</span>
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

function PersonaImpactPanel({ state, step = 0, i18n }) {
  const { _A, _P, _M, _V, _PR, _SF, _EC, _AF, _t } = pickJaI18nFields(i18n, {
    _A: "tArchetypes", _P: "tPersonas", _M: "tMoments", _V: "tVisualStyles", _PR: "tProven",
    _SF: "tSelectionFeedback", _EC: "tEmotionCategories", _AF: "tAngleFeedback", _t: "t",
  });
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
        <p className="text-[10px] text-white font-semibold uppercase">{_t("ui", "ブランド確定")}</p>
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
            <span className="text-xs font-bold text-white">これが有効化するもの</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>システム内で：</strong> {_SF.archetypes[arch.id].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>あなたの読者へ：</strong> {_SF.archetypes[arch.id].emotionalBenefit}</div>
        </div>
      )}
      {step === 1 && persona && _SF.personas[persona.id] && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-violet-500" />
            <span className="text-xs font-bold text-white">これが有効化するもの</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>システム内で：</strong> {_SF.personas[persona.id].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>あなたの読者へ：</strong> {_SF.personas[persona.id].emotionalBenefit}</div>
        </div>
      )}
      {step === 1 && persona && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-1">読者</div>
          <div className="flex items-center gap-2"><span className="text-lg">{persona.emoji}</span><div><div className="text-xs font-bold text-white">{persona.label}</div></div></div>
        </div>
      )}
      {step === 1 && persona && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-2">読者プロフィール</div>
          <div className="text-[10px] text-white leading-tight mb-1.5">{persona.desc}</div>
          <div className="text-[10px] text-white leading-tight mb-1.5"><strong>ニーズ：</strong> {persona.needs}</div>
          <div className="text-[10px] text-white leading-tight"><strong>インパクト：</strong> {persona.impact}</div>
        </div>
      )}
      {step === 2 && moment && _SF.moments[moment.id] && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-violet-500" />
            <span className="text-xs font-bold text-white">これが有効化するもの</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>システム内で：</strong> {_SF.moments[moment.id].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>あなたの読者へ：</strong> {_SF.moments[moment.id].emotionalBenefit}</div>
        </div>
      )}
      {step >= 3 && Object.keys(state.voiceSettings || {}).length > 0 && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-2">ボイスプロフィール</div>
          {VOICE_SLIDERS.map((s) => { const val = state.voiceSettings?.[s.id] ?? s.default; return (
            <div key={s.id} className="flex items-center gap-2 mb-1"><span className="text-[9px] text-white w-14">{s.left}</span><div className="flex-1 h-1.5 bg-gray-100 rounded-full"><div className="h-full bg-gray-700 rounded-full transition-all" style={{ width: `${val}%` }} /></div><span className="text-[9px] text-white w-14 text-right">{s.right}</span></div>
          ); })}
        </div>
      )}
      {step === 4 && visual && (
        <div className="bg-white rounded-xl p-3 border border-gray-200">
          <div className="text-[9px] font-bold uppercase text-white mb-2">ビジュアルスタイル</div>
          <div className="flex gap-1.5 mb-1.5">{visual.palette.map((c, i) => <div key={i} className="w-8 h-8 rounded-lg shadow-sm" style={{ backgroundColor: c }} />)}</div>
          <div className="text-[10px] text-white font-medium">{visual.label}</div>
        </div>
      )}
      {step === 4 && state.visualStyle && _SF.visualStyles[state.visualStyle] && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-violet-500" />
            <span className="text-xs font-bold text-white">これが有効化するもの</span>
          </div>
          <div className="text-[10px] text-white leading-relaxed mb-2"><strong>システム内で：</strong> {_SF.visualStyles[state.visualStyle].systemEffect}</div>
          <div className="text-[10px] text-white leading-relaxed"><strong>あなたの読者へ：</strong> {_SF.visualStyles[state.visualStyle].emotionalBenefit}</div>
        </div>
      )}
      {step === 6 && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center gap-2 mb-3">
            <Compass size={14} className="text-indigo-500" />
            <span className="text-xs font-bold text-white">コンテンツアングル</span>
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
                    <p className="text-[9px] text-white/70 italic">トピックを選ぶ…</p>
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
            <span className="text-xs font-bold text-white">セクションへジャンプ</span>
          </div>
          <div className="space-y-0.5">
            {[
              { id: "rev-category", label: "真のカテゴリー", icon: "🎯" },
              { id: "rev-voice", label: "ボイスシグネチャー", icon: "🎙️" },
              { id: "rev-positioning", label: "ポジショニングマップ", icon: "📍" },
              { id: "rev-visual", label: "ビジュアルアイデンティティ", icon: "🎨" },
              { id: "rev-emotion", label: "感情の階段", icon: "📈" },
              { id: "rev-topics", label: "トピック戦略", icon: "🗂️" },
              { id: "rev-engine", label: "コンテンツエンジン", icon: "⚙️" },
              { id: "rev-loop", label: "アドバンテージループ", icon: "🔄" },
              { id: "rev-journey", label: "読者のジャーニー", icon: "🚶" },
              { id: "rev-synergy", label: "声×トピック", icon: "🔗" },
              { id: "rev-radar", label: "ブランド強度", icon: "📊" },
              { id: "rev-synthesis", label: "シンセシス", icon: "✨" },
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
            <span className="text-xs font-bold text-white">感情プロフィール</span>
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

function Step1Archetype({ state, update, i18n }) {
  const _A = pickJaI18n(i18n, "tArchetypes");
  return (
    <div>
      <StepHero
        eyebrow="基盤"
        title="感情の世界を選ぶ"
        subtitle="アーキタイプとは、読者があなたに結びつける感情です——散文、表紙、動画、ソーシャルのすべてにわたって。自分がどう在りたいかに合ったワールドビューを選んでください。"
        helper="各カードには、あなたのブランドが読者を招き入れる世界の短いビジョンが含まれています。"
      />
      <div className="mb-6 rounded-xl border border-indigo-100/80 bg-indigo-50/60 px-4 py-3 backdrop-blur-sm">
        <p className="text-xs font-medium text-indigo-900">{useJaWizardTranslation().t("steps", "これはスタジオで最も影響力の大きな選択です——他のすべては、ここで選ぶ感情的な領域の上に構築されます。")}</p>
      </div>
      <div className="grid grid-cols-1 gap-3">
        {_A.map((arch) => <ArchetypeCard key={arch.id} arch={arch} selected={state.archetype} onClick={(id) => update({ archetype: id })} />)}
      </div>
    </div>
  );
}

function Step2PrimaryReader({ state, update, i18n }) {
  const _P = pickJaI18n(i18n, "tPersonas");
  // Market/lane step removed 2026-06-03 — locale routing happens server-side.

  return (
    <div>
      <StepHero
        eyebrow="読者"
        title="主要読者"
        subtitle="強いブランドにはすべて主人公がいます——あなたが最初にリードする読者です。カタログはすべてのセグメントに届きますが、この選択がまず声、表紙、フックを形作ります。"
      />
      <div className="mb-6 rounded-xl border border-blue-100/80 bg-blue-50/50 p-4 backdrop-blur-sm">
        <p className="text-xs leading-relaxed text-blue-900">
          {useJaWizardTranslation().t("steps", "すべての人に届き続けます。 まずこの読者に合わせてタイトル、パッケージ、エクササイズを調整し、その後アーキタイプの他のセグメントへと適応させます。")}
        </p>
      </div>
      <div className="grid grid-cols-1 gap-2.5">
        {_P.map((p) => <PersonaCard key={p.id} persona={p} selected={state.persona} onClick={(id) => update({ persona: id })} />)}
      </div>
    </div>
  );
}

function Step3TriggerMoment({ state, update, i18n }) {
  const _M = pickJaI18n(i18n, "tMoments");
  return (
    <div>
      <StepHero
        eyebrow="フック"
        title="彼らがあなたに手を伸ばす瞬間"
        subtitle="読者が最も開かれているシーンを選んでください——タイトル、表紙、ソーシャルフックはここから生まれます。"
      />
      <details open className="mb-5 rounded-xl border border-amber-100/90 bg-amber-50/40 px-4 py-2 text-xs text-amber-900 backdrop-blur-sm open:pb-3">
        <summary className="cursor-pointer font-semibold text-amber-900/90 outline-none">なぜこれが重要なのか</summary>
        <p className="mt-2 leading-relaxed text-amber-900/85">
          {useJaWizardTranslation().t("steps", "強いブランドはデモグラフィックだけでなく、瞬間に語りかけます。この選択が最初の一行、表紙の約束、スクロールを止めるフックを方向付けます。")}
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

function Step4VoiceGraphs({ state, update, i18n }) {
  const tVoiceTone = pickJaI18n(i18n, "tVoiceTone");
  const audioRef = useRef(null);
  const audioSrc = VOICE_AUDIO_SRC_JA;
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
        eyebrow="声"
        title="ブランドのトーンを形作る"
        subtitle="4つのスライダー——スライドしてグラフが動くのを見てください。各軸がすべての文章の感触を変えます。"
      />
      <p className="mb-5 text-[11px] text-white">次のステップで、各ポジションが読者にどう作用するかを示します。</p>

      <div className="space-y-6">
        {VOICE_SLIDERS.map((s, idx) => {
          const val = state.voiceSettings?.[s.id] ?? s.default;
          const snapIdx = snap5(val);
          const position = VOICE_5_STOPS[snapIdx];
          const toneData = tVoiceTone[s.id][position - 1];
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
                <span className="text-[10px] text-white">ポジション {position} / 10</span>
              </div>

              {audioSrc[s.id] && (
                <div className="mt-2 flex items-center gap-2">
                  <button onClick={() => playAudio(s.id, position)} className="text-[10px] text-violet-600 hover:text-violet-800 flex items-center gap-1">
                    <Play size={10} /> ポジション {position} を聴く
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

function Step5VoiceEffects({ state, update, i18n }) {
  const tVoiceTone = pickJaI18n(i18n, "tVoiceTone");
  const graphComponents = [PulseWaveGraph, SpectrumBarGraph, EmotionRadarGraph, EnergyGaugeGraph];
  const handleSlider = (id, rawVal) => {
    const idx = snap5(parseInt(rawVal));
    update({ voiceSettings: { ...state.voiceSettings, [id]: VOICE_5_VALUES[idx] } });
  };

  return (
    <div>
      <StepHero
        eyebrow="インパクト"
        title="あなたのトーンが読者にもたらすもの"
        subtitle="スライドして、詳細を読みたい場合は下のインパクトを開いてください。"
      />

      <div className="mb-6 rounded-2xl border border-violet-100 bg-violet-50/50 px-4 py-3">
        <p className="text-[10px] font-bold uppercase tracking-wider text-violet-800">ナレータープレビュー</p>
        <p className="mt-1 text-[11px] leading-relaxed text-white">
          同じ安心の文章、3種類のEdge TTSデモ音声。上のスライダーと合わせてお試しください。
        </p>
        <div className="mt-3 space-y-2">
          <div>
            <span className="text-[10px] font-semibold text-white">調整／落ち着き</span>
            <audio className="mt-1 block h-9 w-full" controls preload="metadata" src="/onboarding/audio/voice_cmp_comfort_voice_regulating_female.mp3" />
          </div>
          <div>
            <span className="text-[10px] font-semibold text-white">温かみのある共感</span>
            <audio className="mt-1 block h-9 w-full" controls preload="metadata" src="/onboarding/audio/voice_cmp_comfort_voice_warm_male.mp3" />
          </div>
          <div>
            <span className="text-[10px] font-semibold text-white">直接的／権威感</span>
            <audio className="mt-1 block h-9 w-full" controls preload="metadata" src="/onboarding/audio/voice_cmp_comfort_voice_direct_authority.mp3" />
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {VOICE_SLIDERS.map((s, idx) => {
          const val = state.voiceSettings?.[s.id] ?? s.default;
          const snapIdx = snap5(val);
          const position = VOICE_5_STOPS[snapIdx];
          const toneData = tVoiceTone[s.id][position - 1];
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
                  <summary className="cursor-pointer text-xs font-bold text-white outline-none">読者へどう届くか</summary>
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

function Step5VisualStyle({ state, update, i18n }) {
  const _V = pickJaI18n(i18n, "tVisualStyles");
  const handleVisual = (id) => update({ visualStyle: id });
  const handleTradition = (val) => update({ tradition: val });
  const selectedVisual = _V.find((v) => v.id === state.visualStyle);

  return (
    <div>
      <StepHero
        eyebrow="見た目と雰囲気"
        title="ビジュアルの世界"
        subtitle="読者があなたのブランドに結びつけるビジュアルアイデンティティを選んでください——表紙、ソーシャル、動画のすべてがここから生まれます。"
      />

      <div className="text-xs font-bold uppercase tracking-wider text-violet-600/90 mb-3">ビジュアルスタイル</div>
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
  { name: "安心と穏やかさ", icon: "🛡️", color: "#6366f1", items: ["やっと落ち着ける", "自分の身体の中に安心していられる", "休んでいいという許可"], impacts: { "やっと落ち着ける": "読者の神経系が落ち着き、身構えるのをやめ、内容を吸収し始める", "自分の身体の中に安心していられる": "最初のページからソマティックな信頼が育まれ、読書中の闘争・逃走反応が和らぐ", "休んでいいという許可": "燃え尽きた読者がセルフヘルプと向き合えなくする罪悪感のループを解消する" } },
  { name: "明確さと方向性", icon: "🧭", color: "#059669", items: ["頭がすっきりしている", "自分でコントロールできている", "目的とつながっている"], impacts: { "頭がすっきりしている": "決断疲れを打ち破り、霧が晴れるような感覚をもたらし、読者が選択を始める", "自分でコントロールできている": "人生に流されていると感じている読者に、主体性を取り戻させる", "目的とつながっている": "「何をすればいいか」と「なぜ重要なのか」の橋渡しをし、読者が推進力を見つける" } },
  { name: "エネルギーと自信", icon: "⚡", color: "#f59e0b", items: ["エネルギーが湧いている", "自信がある", "しなやかに立ち直れる"], impacts: { "エネルギーが湧いている": "受動的な読者を行動する人へと変える——本を閉じて、動き出す", "自信がある": "インポスター症候群と比較文化によって傷ついた自己信頼を再構築する", "しなやかに立ち直れる": "読者が立ち直る力を養い、挫折がアイデンティティではなくデータになる" } },
  { name: "解放と癒し", icon: "🕊️", color: "#f43f5e", items: ["解放されている", "許された気持ちになれる", "孤独が和らいでいる"], impacts: { "解放されている": "悲しみ、怒り、抱えた緊張が、ようやく行き場を見つける——読者は本当の意味で息を吐ける", "許された気持ちになれる": "自己批判に代わり自己慈悲が育まれ、人間であることへの自己罰が止まる", "孤独が和らいでいる": "名前のない感情を言語化し、「自分だけ」だと思っていた痛みが普遍的だと気づき、孤立が解ける" } },
  { name: "今この瞬間にいることと希望", icon: "✨", color: "#7c3aed", items: ["グラウンデッド", "希望が持てる", "今ここにいられる"], impacts: { "グラウンデッド": "読者を体と現在に繋ぎ留め、反芻思考と未来への不安の力を弱める", "希望が持てる": "変化は可能だという信念を再点火する——セルフヘルプにおける最も強力な変革の起点", "今ここにいられる": "読者が後悔や不安の中で生きることをやめ、今ここにいるとはどういうことかを体感する" } },
];

function Step6EmotionalOutcomes({ state, update, i18n }) {
  const _EC = pickJaI18n(i18n, "tEmotionCategories");
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
        eyebrow="約束"
        title="感情的な結果"
        subtitle="これらは読者が持ち帰る感情——彼らが言葉にできる変容です。すべてのタイトル、CTA、マーケティングメッセージがこれらの約束を指し示します。"
      />
      <div className="mb-6 rounded-xl border border-rose-100/80 bg-rose-50/50 p-4 backdrop-blur-sm">
        <p className="text-xs leading-relaxed text-rose-900">
          <strong>各カテゴリーから一つ選んでください。</strong> あなたの選択がブランド全体の感情的な北極星になります。表紙はこれらの感情をビジュアルで約束し、タイトルはそれを言葉にし、エクササイズがそれを届けます。システムはあなたの選択を、生成されるすべてのコンテンツに織り込みます。
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
  { label: "睡眠と不安", icon: "😰", color: "#6366f1", tags: [
    { id: "anxiety-at-night", label: "夜の不安", angle: "framework", bullet: "就寝前の不安プロトコルを提供——コルチゾールの悪循環が始まる前に遮断する、3つのボディスキャン" },
    { id: "overthinking", label: "考えすぎ", angle: "origin", bullet: "考えすぎのパターンを幼少期の生存戦略へと辿る——脳が危険を察知し続け、それを止められなかった理由" },
    { id: "panic-grounding", label: "パニックグラウンディング", angle: "debunk", bullet: "「深呼吸すればいい」という通説を崩す——パニックにはまずソマティック介入、認知的ツールはその後" },
    { id: "sunday-dread", label: "日曜の憂鬱", angle: "leverage", bullet: "日曜の憂鬱を神経系の週次予報として再定義——その憂鬱自体が、変える必要があることへのデータを含んでいる" },
  ]},
  { label: "燃え尽きと仕事", icon: "🔥", color: "#f59e0b", tags: [
    { id: "burnout-recovery", label: "燃え尽き回復", angle: "debunk", bullet: "「休暇を取ればいい」という通説を崩す——燃え尽きはスケジュールの問題ではなく、神経系の状態" },
    { id: "nervous-system-reset", label: "神経系リセット", angle: "framework", bullet: "ポリヴェーガル理論に基づく5日間の迷走神経トーンリセットプロトコルを提供——読者がすぐ実践できる構造" },
    { id: "decision-fatigue", label: "決断疲れ", angle: "reveal", bullet: "決断疲れは意志力の問題ではないことを明かす——古い脅威ソフトウェアを走らせ続ける過負荷の前頭前野" },
    { id: "phone-addiction", label: "スマホ依存", angle: "leverage", bullet: "スマートフォンをバイオフィードバックツールとして再定義——スクロールパターンが神経系の渇望を正確に示している" },
  ]},
  { label: "悲しみと癒し", icon: "🕊️", color: "#f43f5e", tags: [
    { id: "grief-timeline", label: "悲しみのタイムライン", angle: "debunk", bullet: "「悲しみの5段階」モデルを覆す——悲しみは非線形であり、そのことを知れば読者は自分の癒しを病理化しなくなる" },
    { id: "toxic-relationship-healing", label: "有害な関係からの癒し", angle: "origin", bullet: "惹かれるパターンを幼少期のアタッチメントの傷へと辿る——起源を理解することで繰り返しのサイクルが断ち切られる" },
    { id: "intergenerational-trauma", label: "世代間トラウマ", angle: "reveal", bullet: "トラウマがエピジェネティクスと家族の沈黙を通じて伝わる仕組みを明かす——読者の痛みは「気のせい」ではないと理解する" },
    { id: "heartbreak-recovery", label: "失恋からの回復", angle: "framework", bullet: "回復を三段階に整理する：生き延びる、安定する、再建する——道を見失った傷心者に地図を渡す" },
    { id: "emotional-numbness", label: "感情の麻痺", angle: "leverage", bullet: "麻痺感を神経系の最も洗練された防衛として再定義——感情がないのではなく、感情が溢れすぎている" },
  ]},
  { label: "アイデンティティと方向性", icon: "🧭", color: "#059669", tags: [
    { id: "feeling-behind", label: "遅れている感覚", angle: "debunk", bullet: "比較のタイムラインを覆す——「遅れている」などというものは存在せず、誰もがまったく異なる土台の上に構築している" },
    { id: "quarter-life-crisis", label: "クォーターライフクライシス", angle: "leverage", bullet: "クライシスをアイデンティティシステムのアップグレードとして再定義——その不快感は、古い自分を超えつつある証拠" },
    { id: "identity-rebuild", label: "アイデンティティの再構築", angle: "framework", bullet: "4段階のアイデンティティ再構築フレームワークを提供——解体から統合を経て、本物の自己表現へ" },
    { id: "purpose-after-30", label: "30代以降の目的", angle: "origin", bullet: "目的の空白を、受け継いだキャリアの台本へと辿る——誰の夢を生きてきたかが見えれば、自分の夢も見えてくる" },
  ]},
  { label: "集中力とパフォーマンス", icon: "⚡", color: "#0ea5e9", tags: [
    { id: "habit-building", label: "習慣形成", angle: "framework", bullet: "習慣形成を環境デザインとアイデンティティの転換へと体系化——やる気が出ない時でも機能する構造" },
    { id: "ADHD-productivity", label: "ADHD生産性", angle: "leverage", bullet: "ADHDの過集中を戦略的な強みとして再定義——あなたの脳は壊れていない、生産性のアドバイスが別の人向けに設計されているだけ" },
    { id: "dopamine-detox", label: "ドーパミンデトックス", angle: "debunk", bullet: "バズったドーパミンデトックスのトレンドを覆す——本当の問題は報酬感受性であり、解決策は剥奪ではなく再調整" },
    { id: "deep-work", label: "ディープワーク", angle: "reveal", bullet: "不安を抱えた人のディープワークには、意志力やタイマーだけでなく、ブロック間の神経系リセットが必要であることを明かす" },
  ]},
  { label: "意味とスピリチュアリティ", icon: "✨", color: "#7c3aed", tags: [
    { id: "meditation-beginners", label: "瞑想入門", angle: "debunk", bullet: "「頭を空にする」という通説を覆す——瞑想は思考を消すのではなく、気づくこと。この再定義が初心者の挫折を防ぐ" },
    { id: "meaning-after-loss", label: "喪失後の意味", angle: "origin", bullet: "意味の構築を、ナラティブの一貫性という人間の根本的な欲求へと辿る——喪失が物語を壊す時、意味を再構築することが癒しになる" },
    { id: "spiritual-no-religion", label: "宗教なきスピリチュアリティ", angle: "leverage", bullet: "スピリチュアルな飢えを欠如ではなく、特性として再定義——深さと超越にアクセスするために、他者の伝統は必要ない" },
    { id: "inner-peace-chaos", label: "混沌の中の内なる平和", angle: "reveal", bullet: "内なる平和は混沌の不在ではなく、混沌との関係性の変化であることを明かす——騒音はやまない、しかし溺れることをやめる" },
    { id: "mindfulness-skeptics", label: "マインドフルネス懐疑派", angle: "framework", bullet: "神経科学のデータに裏付けられた懐疑派向けの5分間実践を提供——お香も詠唱も不要、ただ計測可能な結果だけ" },
  ]},
];

const ANGLE_FEEDBACK = {
  debunk: { label: "誤解を正す", icon: "🔍", systemEffect: "タイトルは逆張りのフックで始まる——「セラピストが話してくれないこと」", emotionalBenefit: "読者は知的に尊重される感覚を得る。従来のアドバイスが効かないという疑念を肯定する。" },
  framework: { label: "フレームワーク", icon: "🔧", systemEffect: "タイトルは構造で始まる——「〇〇のための5ステッププロトコル」。繰り返せるシステム。", emotionalBenefit: "明確なシステムを見た読者は、思わず息をつく。漠然とした不安を具体的なステップへと変換する。" },
  reveal: { label: "お披露目", icon: "💡", systemEffect: "タイトルは隠された真実を暴く——「眠れない本当の理由」", emotionalBenefit: "読者は「そうか」という気づきを体験し、自分を「壊れている」から「わかってもらえた」へと書き換える。" },
  leverage: { label: "活用する", icon: "🔄", systemEffect: "タイトルは弱みを再定義する——「あなたの不安は超能力だ」", emotionalBenefit: "読者は自分との戦いをやめる。「あなたは壊れていない、ただ才能の使い方が違うだけ」と伝える。" },
  origin: { label: "起源", icon: "🌱", systemEffect: "タイトルは根本原因を辿る——「あなたのパターンが本当に始まった場所」", emotionalBenefit: "パターンがどこから始まったかを理解することで深い安堵が生まれる。過去の自分への慈悲が育まれる。" },
};

// ═══════════════════════════════════════════════════════════
// MARKET DATA — Visual Identity & Topic/Angle research scores
// ═══════════════════════════════════════════════════════════
const VISUAL_MARKET = {
  calm_minimal:      { shelf: 62, trust: 88, social: 70, premium: 78, rank: 5, demo: "30–55, F-lean", superpower: "セラピストや専門家から推薦される——「信頼性」の選択" },
  dark_intense:      { shelf: 84, trust: 68, social: 85, premium: 80, rank: 3, demo: "22–38, neutral", superpower: "最も多くのオーガニックUGCを生み出す——読者がアイデンティティシグナルとしてシェアする" },
  earthy_organic:    { shelf: 65, trust: 82, social: 74, premium: 68, rank: 6, demo: "28–50, F-strong", superpower: "最も深いパラソーシャルな信頼を築く——読者が著者を「自分たちの一人」と感じる" },
  bold_modern:       { shelf: 88, trust: 72, social: 82, premium: 75, rank: 1, demo: "25–40, neutral", superpower: "どんな棚やフィードでも視覚的な雑音を切り抜ける——スクロールを止める王者" },
  premium_soft:      { shelf: 78, trust: 85, social: 76, premium: 92, rank: 2, demo: "30–50, 女性やや多め", superpower: "単に本を買うのではなく、自分自身に投資していると感じさせる" },
  sacred_cosmic:     { shelf: 75, trust: 77, social: 79, premium: 83, rank: 4, demo: "28–45, 女性やや多め", superpower: "熱狂的なファンを育てる——購入した読者がエバンジェリストになる" },
};

const ANGLE_MARKET = {
  debunk:    { viral: 88, trust: 45, conversion: 55, seo: 60, tip: "ファネルの上部に最適——論争が冷たい読者のシェアを促進する" },
  framework: { viral: 55, trust: 82, conversion: 90, seo: 85, tip: "ファネルの中段に最適——行動する準備ができている読者に構造が必要" },
  reveal:    { viral: 80, trust: 65, conversion: 65, seo: 70, tip: "メールフックに最適——好奇心をより深いコンテンツへの橋渡しをする" },
  leverage:  { viral: 75, trust: 70, conversion: 72, seo: 50, tip: "異議の再定義に最適——抵抗を賛同へと変える" },
  origin:    { viral: 50, trust: 92, conversion: 60, seo: 55, tip: "ロングフォームの忠誠心に最適——既存読者との信頼を深める" },
};

const TOPIC_MARKET = {
  "睡眠と不安":       { search: 95, competition: 88, monetization: 82, growth: 75, platform: "YouTube" },
  "燃え尽きと仕事":        { search: 80, competition: 75, monetization: 78, growth: 85, platform: "LinkedIn" },
  "悲しみと癒し":       { search: 55, competition: 40, monetization: 60, growth: 65, platform: "Podcasts" },
  "アイデンティティと方向性":  { search: 60, competition: 55, monetization: 70, growth: 80, platform: "TikTok" },
  "集中力とパフォーマンス":   { search: 85, competition: 82, monetization: 88, growth: 70, platform: "YouTube" },
  "意味とスピリチュアリティ":{ search: 50, competition: 45, monetization: 65, growth: 75, platform: "本" },
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

function Step7Topics({ state, update, i18n }) {
  const _AF = pickJaI18n(i18n, "tAngleFeedback");
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
        eyebrow="テリトリー"
        title="検索テリトリーを確立する"
        subtitle="カテゴリーごとに一つのトピックを選んでください——各選択がそのテリトリーを枠組みするブランドのコンテンツアングルを設定します。選ぶとサイドバーが更新されます。"
      />
      <div className="mb-6 rounded-xl border border-indigo-100/80 bg-indigo-50/50 p-4 backdrop-blur-sm">
        <p className="text-xs leading-relaxed text-indigo-900">
          <strong>カテゴリーごとに一つ。</strong> 各トピックはコンテンツアングルとペアになっています——デバンク、フレームワーク、リビール、レバレッジ、またはオリジン。トピックを切り替えると、サイドバーのアングルと戦略が変わります。
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
      <h2 className="text-2xl font-extrabold text-white tracking-tight">マーケット・インテリジェンス</h2>
      <p className="text-sm text-white mt-1 mb-2">あなたのクリエイティブビジョンはブランドの魂です。しかし魂だけでは生計は立てられません。このページでは、システムがあなたのユニークな方向性を実際の市場データ——実際の検索ボリューム、実証済みのバイヤーペルソナ、高コンバージョンのキーワードテリトリー——とどのようにブレンドし、あなたのカタログがすでに求めているものを探している人々に届くかを示します。</p>
      <p className="text-xs text-white mb-6 italic">ブランドの声やアイデンティティに変わるものは何もありません。ただ、需要がある場所に確実に現れるようにするだけです。</p>

      {/* Gen Z / Gen Alpha FIRST */}
      <div className="rounded-xl border border-violet-200 bg-violet-50 p-5 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Globe size={16} className="text-violet-600" />
          <span className="text-sm font-bold text-violet-800">若年層へのリーチ：Z世代＋α世代</span>
        </div>
        <p className="text-xs text-violet-700 leading-relaxed mb-3">
          パールプライムのすべてのブランドは、追加設定なしでZ世代とα世代の読者に自動的に対応します。システムはコンテンツの年齢適切な適応版を作成します：モバイルファースト消費に合わせたショートフォーマット、スクロール発見に最適化されたビジュアルファーストレイアウト、TikTokとYouTube Shortsのためのプラットフォームネイティブフック、そして段落ではなく画像で思考する読者向けのフルイラストマンガスタイル版。α世代（2010〜2025年生まれ）は初日から感情の語彙を持ちながら育つ最初の世代——以前のどの世代よりも若い年齢でメンタルヘルスコンテンツを検索しています。あなたのブランドは彼らのいる場所で彼らと出会います。
        </p>
        <div className="grid grid-cols-3 gap-2">
          {[
            { icon: Smartphone, label: "ショートフォーム優先", desc: "TikTok、Reels、Shorts対応" },
            { icon: BookMarked, label: "マンガ版", desc: "フルイラストビジュアル形式" },
            { icon: Headphones, label: "マイクロオーディオブック", desc: "モバイル向け15〜30分のリスニング" },
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
          <span className="text-sm font-bold text-emerald-800">ブレンドの仕組み</span>
        </div>
        <p className="text-xs text-emerald-700 leading-relaxed mb-4">
          あなたのクリエイティブな方向性——アーキタイプ、声、トピック、アングル——を、実証済みの高パフォーマンス検索語、読者セグメント、リアルタイムの市場シグナルと組み合わせます。システムがカタログを実際に検索されているトピックへと確実にターゲティングしながら、ブランドアイデンティティは完全に保たれます。つまり、あなたの本は需要がすでにある場所に現れ、タイトルは実際に検索バーに入力されることに合致し、コンテンツは購買力が確認されたバイヤーペルソナに届きます。結果：あなたのユニークな声が最大限の読者に届きます。
        </p>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white rounded-lg p-3">
            <div className="text-[10px] font-bold text-emerald-700 uppercase mb-1">あなたの方向性</div>
            <p className="text-[11px] text-white">アーキタイプ、声、トピック、アングル、ビジュアルスタイル——ブランドのユニークなクリエイティブアイデンティティとして保たれます</p>
          </div>
          <div className="bg-white rounded-lg p-3">
            <div className="text-[10px] font-bold text-emerald-700 uppercase mb-1">マーケット・インテリジェンス</div>
            <p className="text-[11px] text-white">実証済みの収益ペルソナ、トレンド検索語、高コンバージョンキーワード、そしてあなたのアーキタイプにマッチした需要データ</p>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5 mb-6">
        <div className="text-xs font-bold text-white mb-3">あなたのアーキタイプの実証済み収益ペルソナ</div>
        <p className="text-[11px] text-white mb-3">これらは、あなたの感情的テリトリーで確認済みの購買力を持つ読者セグメントです。システムがカタログをすべてに確実に届けます。</p>
        {proven.personas.map((p, i) => (
          <div key={i} className="flex items-start gap-2 mb-2.5">
            <Target size={12} className="text-indigo-500 flex-shrink-0 mt-0.5" />
            <span className="text-[11px] text-white">{p}</span>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <div className="text-xs font-bold text-white mb-3">高パフォーマンスの検索トピック</div>
        <p className="text-[11px] text-white mb-3">これらの検索語は、確認済みの月間ボリュームとコンバージョン率を持っています。あなたのタイトルとキーワードは、カスタム選択と合わせてこれらの語を中心に最適化されます。</p>
        <div className="flex flex-wrap gap-2">
          {proven.topics.map((t, i) => <span key={i} className="text-[11px] bg-gray-100 text-white px-3 py-1 rounded-full">{t}</span>)}
        </div>
      </div>
    </div>
  );
}

function Step9Formats({ state, update, i18n }) {
  const _SF = pickJaI18n(i18n, "tSelectionFeedback");
  const formatFocus = state.formatFocus || null;
  const channels = state.channels || [];
  const setFocus = (focus) => update({ formatFocus: focus });
  const toggleChannel = (ch) => { const next = channels.includes(ch) ? channels.filter((c) => c !== ch) : [...channels, ch]; update({ channels: next }); };

  const CHANNELS = [
    { id: "audiobook", label: "オーディオブック", icon: Headphones, desc: "Audible、Spotify、Apple Booksおよび世界40以上のプラットフォームでのフルナレーションオーディオブック", benefit: "リスナーは通勤、散歩、眠れない夜に癒されます——あなたの声は、最も脆弱なプライベートな瞬間の伴走者になります" },
    { id: "yt_channel", label: "YouTubeチャンネル", icon: Tv, desc: "毎日の動画コンテンツ——ショート動画、ロングフォームトーク、ガイドセッション、可視化されたチャプター", benefit: "ビジュアル学習者は動く画像を通じて感情を処理します——あなたのブランドは彼らのフィードに毎日存在し、一貫した出現を通じて信頼を積み上げます" },
    { id: "tiktok", label: "TikTok", icon: Smartphone, desc: "トレンドオーディオ、テキストオーバーレイ、フック優先の編集を備えたプラットフォームネイティブなショートフォーム動画", benefit: "スクロールの合間、脆弱な瞬間に人々を捉えます——30秒のクリップが、人生の変化への最初の一歩になりうる" },
    { id: "pocket_guide", label: "ポケットガイド", icon: BookOpen, desc: "30〜50ページに凝縮されたクイックリファレンス版——週末の読書で得られる本質的なエッセンス", benefit: "フルブックに取り組めない余裕のない読者に即座の安堵を提供——必須の変容を届ける週末の読み物" },
    { id: "7_day_guide", label: "7日間でやり遂げる方法", icon: Clock, desc: "圧縮した変容プロトコル — 1日1章、明確な日々の行動、早い成功体験", benefit: "構造が圧倒感を軽減します——「気が向いた時に読む」に失敗した読者が、勢いをつける毎日の課題で成功できます" },
    { id: "mastercourse", label: "マスターコースシリーズ", icon: GraduationCap, desc: "段階的に複雑さが増す複数巻の深堀りシリーズ——4〜8冊が互いの上に積み上がる", benefit: "コミットした読者が数ヶ月をかけて深く進みます——各巻が前の巻の上に積み上がり、本当の持続的な変化を駆動する継続的実践を生み出します" },
    { id: "workbook", label: "インタラクティブ・ワークブック", icon: PenTool, desc: "記入欄、トラッキングシート、ガイドされた内省スペースを備えたエクササイズ重視の伴走書", benefit: "書くことは読むこととは異なる脳の経路を活性化します——ワークブックは受動的な消費を能動的な自己発見と統合へと変えます" },
    { id: "daily_journal", label: "デイリー・ジャーナル", icon: BookMarked, desc: "TODO_JA:formats.dailyJournalDesc", benefit: "毎日のプロンプトが自己認識の筋肉を育てます——読者がページをめくるたびに、自分の内なる世界との継続的な関係が育まれます" },
  ];

  return (
    <div>
      <h2 className="text-2xl font-extrabold text-white tracking-tight">フォーマットとチャンネルの選択</h2>
      <p className="text-sm text-white mt-1 mb-2">フォーマットフォーカスがカタログプランナーに、ビジュアル優先のショートフォームコンテンツか、深いロングフォームブックかのどちらに最適化するかを伝えます。チャンネル選択はブランドがどこで公開するかを決定します——各アクティブチャンネルがパイプラインにコンテンツの重みを追加し、より多くのフォーマット、バリエーション、読者とのタッチポイントをもたらします。</p>

      <div className="text-xs font-bold uppercase tracking-wider text-white mb-3 mt-6">主要フォーマットフォーカス</div>
      <p className="text-[11px] text-white mb-3">これは最も重要なフォーマットの決断です。カタログプランナーがブランド全体にどのようにコンテンツを配分するかが変わります。</p>
      <div className="grid grid-cols-2 gap-3 mb-8">
        <button onClick={() => setFocus("manga")}
          className={`p-5 rounded-xl border-2 text-left transition-all ${formatFocus === "manga" ? "border-gray-900 bg-gray-50 shadow-md" : "border-gray-200 bg-white hover:border-gray-300"}`}>
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-rose-500 to-purple-600 flex items-center justify-center mb-3"><Image size={24} className="text-white" /></div>
          <div className="text-sm font-bold text-white">マンガ / ビジュアル</div>
          <p className="text-[11px] text-white mt-1 leading-relaxed">イラストパネル、ビジュアルストーリーテリング、マンガスタイルのレイアウト。オーディオブックはデフォルトでショートフォーマット（15〜30分）。Z世代とα世代のビジュアル優先消費に最適化。</p>
          {formatFocus === "manga" && <div className="mt-2 bg-rose-50 rounded-lg p-2"><p className="text-[10px] text-rose-700">カタログプランナーはすべてのチャンネルを通じて、ショートフォームオーディオブック、ビジュアルコンテンツ、イラスト重視のフォーマットを優先します。</p></div>}
        </button>
        <button onClick={() => setFocus("book")}
          className={`p-5 rounded-xl border-2 text-left transition-all ${formatFocus === "book" ? "border-gray-900 bg-gray-50 shadow-md" : "border-gray-200 bg-white hover:border-gray-300"}`}>
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center mb-3"><BookOpen size={24} className="text-white" /></div>
          <div className="text-sm font-bold text-white">従来型書籍</div>
          <p className="text-[11px] text-white mt-1 leading-relaxed">フルレングスのナラティブブック、深いガイドプログラム、包括的なワークブック。オーディオブックはロングフォーマット（3〜8時間）。深みを求める読者に最適化。</p>
          {formatFocus === "book" && <div className="mt-2 bg-amber-50 rounded-lg p-2"><p className="text-[10px] text-amber-700">カタログプランナーはすべてのチャンネルを通じて、ロングフォームブック、完全なプログラム、深いシリーズを優先します。</p></div>}
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

      <div className="text-xs font-bold uppercase tracking-wider text-white mb-3">パブリッシングチャンネル</div>
      <p className="text-[11px] text-white mb-3">ブランドを通じて公開したいすべてのチャンネルを選択してください。各チャンネルがそのプラットフォームのフォーマット、読者、アルゴリズム要件に適応した専用コンテンツを生成します。</p>
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

function StepBrandReveal({ state, i18n }) {
  const { _A, _P, _M, _V, _EC, _AF, _SF, _PR } = pickJaI18nFields(i18n, {
    _A: "tArchetypes", _P: "tPersonas", _M: "tMoments", _V: "tVisualStyles", _EC: "tEmotionCategories",
    _AF: "tAngleFeedback", _SF: "tSelectionFeedback", _PR: "tProven",
  });
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
    if (v.id === "gentleDirect") return p <= 3 ? "許可を与える" : p >= 8 ? "命令的" : "バランスのとれた";
    if (v.id === "simpleDeep") return p <= 3 ? "親しみやすい" : p >= 8 ? "層のある" : "中程度の深さ";
    if (v.id === "emotionalLogical") return p <= 3 ? "ストーリー主導" : p >= 8 ? "データ駆動" : "バランスのとれた";
    if (v.id === "spiritualPractical") return p <= 3 ? "内省的" : p >= 8 ? "戦術的" : "ブレンドされた";
    return "";
  });

  // Generate true category statement
  const trueCategory = arch && persona
    ? `${arch.name}（${persona.label}向け）${moment ? ` — ${moment.label}の瞬間を捉える` : ""}`
    : arch ? arch.name : "あなたのブランド";

  // Content engine steps derived from voice + angle mix
  const engineSteps = [
    { step: "問題を言語化する", desc: moment ? `「${moment.scene}」で始める — 読者のまさにその瞬間` : "読者のまさにその痛みのポイントで始める", icon: "🎯" },
    { step: "アイデンティティを再定義する", desc: `${uniqueAngles.includes("debunk") ? "誤解を正す" : uniqueAngles.includes("reveal") ? "お披露目" : "根源を辿る"}のアングルで自己ナラティブを書き換える`, icon: "🪞" },
    { step: "マイクロツールを渡す", desc: `${uniqueAngles.includes("framework") ? "今夜から使えるフレームワークを提供する" : "すぐ実践できる行動的な洞察を渡す"}`, icon: "🔧" },
    { step: "感情に着地する", desc: emotions.length > 0 ? `最後は必ずこの感情に着地する：「${emotions[0]}」` : "すべてのコンテンツが約束した感情で終わる", icon: "💫" },
  ];

  // Unfair advantage loop
  const loopSteps = [
    { label: "再定義", desc: "古い物語を壊す", color: "#6366f1" },
    { label: "調整する", desc: "神経系を落ち着かせる", color: "#059669" },
    { label: "回復する", desc: "体から再構築する", color: "#f59e0b" },
    { label: "方向を定める", desc: "新しいアイデンティティへ向ける", color: "#f43f5e" },
  ];

  // Positioning map coords — Gentle↔Direct on X, Simple↔Deep on Y
  const posX = voicePositions.find(v => v.id === "gentleDirect")?.position || 5;
  const posY = voicePositions.find(v => v.id === "simpleDeep")?.position || 5;

  // Emotional staircase — build ascending steps from trigger to each emotion
  const staircaseSteps = [
    { label: moment ? moment.label : "ペインポイント", color: "#f43f5e", sub: "彼らの出発点" },
    ...emotions.slice(0, 5).map((e, i) => {
      const cat = _EC.find(c => c.items.includes(e));
      return { label: e, color: cat?.color || "#6366f1", sub: cat?.name || "" };
    }),
  ];

  return (
    <div>
      <StepHero
        eyebrow="お披露目"
        title="あなたのブランドはこちらです"
        subtitle=""
      />

      {/* ═══ 1. TRUE CATEGORY — gradient banner ═══ */}
      {arch && (
        <div id="rev-category" className={`mb-6 rounded-2xl border-2 p-6 bg-gradient-to-br ${arch.gradient} shadow-lg`}>
          <div className="text-center">
            <div className="text-white/70 text-[10px] font-bold uppercase tracking-[0.3em] mb-2">あなたの真のカテゴリー</div>
            <div className="text-white text-xl font-extrabold mb-2">{trueCategory}</div>
            <div className="text-white/80 text-sm leading-relaxed">{arch.tagline}</div>
            {arch.visionVibe && <p className="mt-3 text-white/70 text-[11px] leading-relaxed max-w-md mx-auto italic">{arch.visionVibe}</p>}
          </div>
        </div>
      )}

      {/* ═══ 2. VOICE SIGNATURE — circular gauges ═══ */}
      {Object.keys(state.voiceSettings || {}).length > 0 && (
        <div id="rev-voice" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">ボイスシグネチャー</div>
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
            あなたの声は <span className="text-white font-semibold">{voiceDesc.join(" · ")}</span>
          </div>
        </div>
      )}

      {/* ═══ 2b. POSITIONING MAP — 2D quadrant ═══ */}
      <div id="rev-positioning" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">ポジショニングマップ</div>
        <div className="text-[10px] text-white/70 mb-3 text-center">市場の中でのあなたの声の位置</div>
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
          <text x="30" y="285" fontSize="9" fill="#9ca3af" fontWeight="bold">やさしい</text>
          <text x="265" y="285" fontSize="9" fill="#9ca3af" fontWeight="bold">直接的</text>
          <text x="5" y="15" fontSize="9" fill="#9ca3af" fontWeight="bold" transform="rotate(-90 10 15)">深い</text>
          <text x="5" y="275" fontSize="9" fill="#9ca3af" fontWeight="bold" transform="rotate(-90 10 275)">シンプル</text>
          {/* Quadrant labels */}
          <text x="95" y="75" textAnchor="middle" fontSize="8" fill="#6366f1" fontWeight="600">賢明な案内者</text>
          <text x="225" y="75" textAnchor="middle" fontSize="8" fill="#059669" fontWeight="600">エキスパートコーチ</text>
          <text x="95" y="210" textAnchor="middle" fontSize="8" fill="#f59e0b" fontWeight="600">温かい友人</text>
          <text x="225" y="210" textAnchor="middle" fontSize="8" fill="#f43f5e" fontWeight="600">大胆なメンター</text>
          {/* Brand dot */}
          {(() => {
            const dotX = 30 + (posX / 10) * 260;
            const dotY = 270 - (posY / 10) * 260;
            return (<>
              <circle cx={dotX} cy={dotY} r="14" fill="#6366f1" fillOpacity="0.15" stroke="#6366f1" strokeWidth="2" />
              <circle cx={dotX} cy={dotY} r="6" fill="#6366f1" />
              <text x={dotX} y={dotY - 20} textAnchor="middle" fontSize="9" fill="#6366f1" fontWeight="bold">あなた</text>
            </>);
          })()}
        </svg>
      </div>

      {/* ═══ 3. VISUAL IDENTITY + MARKET DATA ═══ */}
      {visual && (() => {
        const vm = VISUAL_MARKET[visual.id] || {};
        const bars = [
          { label: "棚での訴求力", val: vm.shelf || 0, color: "#f59e0b" },
          { label: "信頼シグナル", val: vm.trust || 0, color: "#059669" },
          { label: "ソーシャルシェア", val: vm.social || 0, color: "#6366f1" },
          { label: "プレミアム感", val: vm.premium || 0, color: "#7c3aed" },
        ];
        return (
          <div id="rev-visual" className="mb-6 rounded-2xl border border-gray-200 bg-white overflow-hidden shadow-sm">
            <div className="flex items-center gap-0 border-b border-gray-100">
              {visual.palette.map((col, i) => (
                <div key={i} className="flex-1 h-12" style={{ backgroundColor: col }} />
              ))}
            </div>
            <div className="p-4">
              <div className="text-[10px] font-bold uppercase text-white">ビジュアルアイデンティティ</div>
              <div className="mt-1 text-base font-bold text-white">{visual.label}</div>
              <p className="mt-1 text-[11px] text-white italic">{visual.mood}</p>
            </div>
            <div className="px-4 pb-4">
              <div className="text-[9px] font-bold uppercase tracking-wider text-white mb-2">市場スコア</div>
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
                <span className="text-[9px] px-2 py-0.5 rounded-full bg-violet-100 text-white font-bold">ランク #{vm.rank || '—'}</span>
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
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">感情の階段</div>
          <div className="text-[10px] text-white/70 mb-4">読者は痛みから約束へと登っていきます——各ステップが前のステップの上に積み上がる</div>
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
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">トピック×アングル戦略</div>
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
                      { label: "バイラル", val: am.viral, color: "#f43f5e" },
                      { label: "検索", val: tm.search, color: "#0ea5e9" },
                      { label: "コンバージョン", val: am.conversion, color: "#059669" },
                      { label: "成長", val: tm.growth, color: "#f59e0b" },
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
                      コンボスコア: {comboScore}
                    </span>
                    <span className="text-[8px] text-white/70">{tm.platform && `${tm.platform} に最適`}</span>
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
        <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-1">コンテンツエンジンの公式</div>
        <div className="text-[10px] text-white/70 mb-5">すべてのコンテンツがこのシーケンスに従います——あなただけのフライホイール</div>
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
          <span className="text-[9px] font-bold text-white/50 uppercase tracking-wider">↻ すべてのコンテンツで繰り返す</span>
          <div className="h-px flex-1" style={{ background: 'linear-gradient(90deg, transparent, #b4530940, transparent)' }} />
        </div>
      </div>

      {/* ═══ 7. UNFAIR ADVANTAGE LOOP — circular diagram ═══ */}
      <div id="rev-loop" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">アンフェアアドバンテージループ</div>
        <div className="text-[10px] text-white/70 mb-4 text-center">すべてのコンテンツが次のコンテンツを生み出す——各出口は、より深い変容への入口</div>
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
          <text x="160" y="170" textAnchor="middle" fontSize="7" fill="#6b7280">繰り返す</text>
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
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">読者の体験</div>
          <div className="text-[10px] text-white/70 mb-3">{persona.emoji} {persona.label} があなたのブランドを体験する流れ：</div>
          <div className="flex flex-col items-center gap-1.5">
            {[
              { phase: "トリガー", desc: `${moment.emoji} ${moment.scene}`, color: "#f43f5e", bg: "bg-rose-50" },
              { phase: "発見", desc: `読者はあなたのコンテンツを見つける——フックが彼らの痛みをそのまま言語化している`, color: "#f59e0b", bg: "bg-amber-50" },
              { phase: "信頼", desc: `あなたの${voiceDesc[0]}な声が${voiceDesc[2]}と感じさせる — 説教ではなく、理解されていると感じる`, color: "#3b82f6", bg: "bg-blue-50" },
              { phase: "変容", desc: emotions[0] ? `感じ始める：「${emotions[0]}」` : "約束された感情が届く", color: "#059669", bg: "bg-emerald-50" },
              { phase: "リターン", desc: `すべてのコンテンツがより深いレベルで同じ変容を届けるから、読者は戻ってくる`, color: "#7c3aed", bg: "bg-violet-50" },
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
          <div className="text-[10px] font-bold uppercase tracking-wider text-white mb-3">声×トピックのシナジー</div>
          <div className="text-[10px] text-white/70 mb-3">あなたの声のトーンが各コンテンツアングルをどれだけ増幅させるか</div>
          <div className="space-y-3">
            {topicAnglePairs.map((p, i) => {
              const af = _AF[p.angle];
              const score = calcSynergyScore(voicePositions, p.angle);
              const multiplier = (0.5 + (score / 100) * 1.5).toFixed(1);
              const barColor = p.catColor;
              const gentlePos = voicePositions.find(v => v.id === "gentleDirect")?.position || 5;
              const toneWord = gentlePos <= 3 ? "やさしく" : gentlePos >= 8 ? "直接的に" : "明確に";
              return (
                <div key={i} className="rounded-xl bg-white p-3 border border-violet-100">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm">{p.catIcon}</span>
                    <span className="text-[10px] text-white flex-1">
                      あなたは<strong>{toneWord}</strong>{af?.label}する <strong>{p.tagLabel}</strong>
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
                <span className="text-[10px] font-bold text-white">総合ボイスフィット</span>
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
          { label: "ビジュアル", val: visualAvg, color: "#7c3aed" },
          { label: "バイラル", val: avg("viral"), color: "#f43f5e" },
          { label: "信頼", val: avg("trust"), color: "#059669" },
          { label: "コンバージョン", val: avg("conversion"), color: "#f59e0b" },
          { label: "SEO", val: avg("seo"), color: "#0ea5e9" },
          { label: "成長", val: avg("growth"), color: "#6366f1" },
        ];
        const overallScore = Math.round(dims.reduce((s, d) => s + d.val, 0) / dims.length);
        const sides = 6, cx = 150, cy = 110, r = 75;

        return (
          <div id="rev-radar" className="mb-6 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <div className="text-[10px] font-bold uppercase tracking-wider text-white">ブランド強度</div>
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
          <div className="text-violet-300/70 text-[10px] font-bold uppercase tracking-[0.3em] mb-3 text-center">ブランドシンセシス</div>
          <p className="text-center text-white text-sm leading-relaxed font-medium">
            あなたは <strong>{arch.name}</strong> — {voiceDesc[0]}で{voiceDesc[1]}な声が、{" "}
            <strong>{persona.label}</strong>
            {moment && <>の<em>「{moment.label}」</em>の瞬間を捉え</>}、{" "}
            {uniqueAngles.length > 0 && <>{uniqueAngles.map(a => _AF[a]?.label).join(" + ")}のアングルで</>}{" "}
            {emotions.length > 0
              ? <>一つの約束を届ける：<strong>「{emotions[0]}」</strong></>
              : <>変容を届ける</>
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
    { label: "市場性", value: marketability, desc: "TODO_JA:blueprint.scoreMarketabilityDesc" },
    { label: "若年層へのリーチ", value: youthReach, desc: "TODO_JA:blueprint.scoreYouthReachDesc" },
    { label: "人生へのインパクト", value: lifeImpact, desc: "TODO_JA:blueprint.scoreLifeImpactDesc" },
    { label: "プラットフォームリーチ", value: reachScore, desc: "TODO_JA:blueprint.scorePlatformReachDesc" },
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
      ? "卓越したブランドポジショニング。アーキタイプ、読者、トピックの選択が、高収益市場セグメントと強力に一致しています。このブランドは深い読者インパクトを持つ、強い商業的潜在力を備えています。"
      : marketability >= 75
        ? "強固なブランド基盤。あなたの選択が、堅固な市場一致を持つ説得力のあるアイデンティティを生み出しています。あと少しの磨き込みで、卓越した領域へ押し上げることができます。"
        : "良い出発点。ブランドアイデンティティが形作られています——市場ポジションを強化するために、さらにトピックの選択やチャンネルカバレッジの追加を検討してください。";

  return (
    <div>
      <StepHero
        eyebrow="お披露目"
        title="あなたのブランドはこちらです"
        subtitle="TODO_JA:blueprint.subtitle"
      />

      {brandOneSentence ? (
        <p className="mb-8 rounded-2xl border border-violet-300/80 bg-gradient-to-br from-violet-50 via-white to-fuchsia-50/60 px-5 py-6 text-center text-lg font-extrabold leading-snug tracking-tight text-violet-950 shadow-md [text-shadow:0_1px_0_rgba(255,255,255,0.9)] sm:text-xl sm:leading-snug">
          {brandOneSentence}
        </p>
      ) : null}

      <div className="mb-6 rounded-2xl border border-indigo-100 bg-indigo-50/40 px-4 py-3">
        <p className="text-[10px] font-bold uppercase tracking-wider text-indigo-800">TODO_JA:blueprint.audiobookVoicePreview</p>
        <p className="mt-1 text-[11px] text-white">TODO_JA:blueprint.regulatingNarrator (registry: <span className="font-mono text-[10px]">cmp_voice_narrator_contrast_v1</span>).</p>
        <audio className="mt-2 block h-9 w-full max-w-md" controls preload="metadata" src="/onboarding/audio/voice_cmp_comfort_voice_regulating_female.mp3" />
      </div>

      <div className="space-y-8">
        <section className="rounded-2xl border border-slate-200/90 bg-slate-50/50 p-4 shadow-sm ring-1 ring-slate-200/70 sm:p-5">
          <h3 className="mb-4 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">TODO_JA:blueprint.sectionBrandIdentity</h3>
          <div className="space-y-3">
            {arch ? (
              <div className={`rounded-2xl border-2 p-5 ${arch.bg} ${arch.border}`}>
                <div className="text-[10px] font-bold uppercase text-white">TODO_JA:blueprint.emotionalWorld</div>
                <div className="mt-1 text-xl font-bold text-white">{arch.name}</div>
                <p className="mt-1 text-sm text-white">{arch.tagline}</p>
              </div>
            ) : null}
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {persona ? (
                <div className="rounded-2xl border border-violet-200/90 bg-white p-4 shadow-md ring-1 ring-violet-100/80">
                  <div className="text-[10px] font-bold uppercase text-violet-600/90">主要読者</div>
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
                  <div className="text-[10px] font-bold uppercase text-violet-600">ビジュアルスタイル</div>
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
                  <div className="text-[8px] font-bold uppercase text-white">レーン</div>
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
                  <div className="text-[8px] font-bold uppercase text-white">フォーマット</div>
                  <div className="mt-0.5 text-[11px] font-semibold text-white">{state.formatFocus === "manga" ? "漫画／ビジュアル" : "本"}</div>
                </div>
              ) : null}
              {(state.channels || []).length > 0 ? (
                <div className="rounded-xl border border-violet-100/90 bg-white/80 p-2.5 text-center opacity-90">
                  <div className="text-[8px] font-bold uppercase text-white">チャンネル</div>
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
              <span className="text-xs font-bold text-emerald-900">あなたの方向性について読む</span>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-emerald-900/90">{assessmentText}</p>
          </div>
        </section>
      </div>

      {/* Demoted score strip — same numeric logic, after narrative sections */}
      <div className="mt-10 rounded-2xl border border-gray-100 bg-gray-50/60 px-3 py-3 opacity-90">
        <div className="mb-2 text-center text-[9px] font-bold uppercase tracking-wider text-white">シグナルスコア</div>
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

function Step11Launch({ state, update, i18n }) {
  const { _A, _P, _M, _V, _SF } = pickJaI18nFields(i18n, {
    _A: "tArchetypes", _P: "tPersonas", _M: "tMoments", _V: "tVisualStyles", _SF: "tSelectionFeedback",
  });
  const handleField = (field, val) => update({ contact: { ...state.contact, [field]: val } });
  const c = state.contact || {};
  const isReady = c.firstName?.trim() && c.lastName?.trim() && c.email?.trim() && c.email?.includes("@");
  const [submitted, setSubmitted] = useState(false);
  const [yamlOutput, setYamlOutput] = useState("");
  const [showYaml, setShowYaml] = useState(false);
  const [yamlCopied, setYamlCopied] = useState(false);

  const [matched, setMatched] = useState(null);
  const [submissionError, setSubmissionError] = useState("");

  const readTeacherMode = () => {
    try { const raw = localStorage.getItem("phoenix_book_mode"); if (raw) return JSON.parse(raw); } catch (_) {}
    const p = new URLSearchParams(window.location.search);
    const ut = p.get("teacher"), um = p.get("mode");
    if (ut) return { mode: "teacher", teacher: ut };
    if (um === "composite") return { mode: "composite", teacher: null };
    return { mode: "composite", teacher: null };
  };

  const handleLaunch = async () => {
    let wizardYaml = generateYAML(state);
    setYamlOutput(wizardYaml);
    setSubmissionError("");
    setSubmitted(true);
    let m = null;
    try {
      const r = await fetch("brand_admin_brands.json", { cache: "no-store" });
      const brands = r.ok ? await r.json() : {};
      m = matchBrand(state, brands, readTeacherMode());
      if (m) {
        wizardYaml = appendBrandAssignmentToYAML(wizardYaml, m, state.contact || {});
        setYamlOutput(wizardYaml);
      }
      if (m) { setMatched(m); try { localStorage.setItem("phoenix_pending_brand", JSON.stringify(m)); } catch (_) {} }
    } catch (_) {}
    if (m) {
      const c = state.contact || {};
      const assignment = brandAssignmentPayload(m, c);
      try {
        const response = await fetch("api/onboarding/submit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            brand_id: m.brand_id,
            lane: m.lane,
            publication_corp: m.publication_corp,
            ...(assignment || {}),
            brand_email: (c.email || "").trim() || null,
            contact: {
              first_name: c.firstName || "",
              last_name: c.lastName || "",
              phone: ((c.phoneCode || "+81") + " " + (c.phone || "")).trim(),
            },
            wizard_yaml: wizardYaml,
            match_score: typeof m.score === "number" ? m.score : null,
            match_basis: m.basis || null,
          }),
        });
        if (!response.ok) {
          let detail = {};
          try { detail = await response.json(); } catch (_) {}
          const classified = classifyOnboardingSubmitFailure(response.status, detail, {
            onboardingMarket: state.onboardingMarket || "japan",
          });
          if (classified.kind === "brand_claimed" || classified.kind === "teacher_claimed_offer") {
            setMatched(null);
            try { localStorage.removeItem("phoenix_pending_brand"); } catch (_) {}
          }
          setSubmissionError(classified.message);
        }
      } catch (_) {
        setSubmissionError("Live assignment did not persist. Keep this screen open and contact ops before treating this brand as active.");
      }
    } else {
      setSubmissionError("No available unassigned brand matched these choices. Keep this screen open and contact ops for a manual assignment.");
    }
  };

  if (submitted) {
    const arch = _A.find((a) => a.id === state.archetype);
    const persona = _P.find((p) => p.id === state.persona);
    const moment = _M.find((m) => m.id === state.moment);
    const visual = _V.find((v) => v.id === state.visualStyle);

    const choiceAudit = [
      arch && { label: "アーキタイプ", value: arch.name, icon: arch.icon, gradient: arch.gradient, systemEffect: _SF.archetypes[state.archetype]?.systemEffect, emotionalBenefit: _SF.archetypes[state.archetype]?.emotionalBenefit },
      persona && { label: "読者", value: `${persona.emoji} ${persona.label}`, icon: Users, gradient: "from-blue-500 to-cyan-500", systemEffect: _SF.personas[state.persona]?.systemEffect, emotionalBenefit: _SF.personas[state.persona]?.emotionalBenefit },
      moment && { label: "きっかけの瞬間", value: `${moment.emoji} ${moment.label}`, icon: Target, gradient: "from-amber-500 to-orange-500", systemEffect: _SF.moments[state.moment]?.systemEffect, emotionalBenefit: _SF.moments[state.moment]?.emotionalBenefit },
      Object.keys(state.voiceSettings || {}).length > 0 && { label: "声のトーン", value: `${Object.keys(state.voiceSettings).length} 次元を調整済み`, icon: SlidersHorizontal, gradient: "from-indigo-500 to-violet-500", systemEffect: "4つすべての声の次元が、すべての章・オーディオブック・ソーシャル投稿にわたって、散文のリズム、語彙レベル、文章構造、感情温度を調整します", emotionalBenefit: "読者は、自分のために書かれたと感じる声を体験します——彼らが必要とする挑戦と安らぎのちょうどいいブレンド。トーンが彼らの感情的な準備状態に合致しているから、すべての文が届きます。" },
      visual && { label: "ビジュアルスタイル", value: visual.label, icon: Palette, gradient: "from-rose-500 to-pink-500", systemEffect: _SF.visualStyles[state.visualStyle]?.systemEffect, emotionalBenefit: _SF.visualStyles[state.visualStyle]?.emotionalBenefit },
      (state.emotions || []).length > 0 && { label: "感情的な結果", value: state.emotions.join(", "), icon: Heart, gradient: "from-rose-400 to-red-500", systemEffect: `${state.emotions.length} transformation promises woven into every title, CTA, and marketing message`, emotionalBenefit: "これらの感情が、すべてのコンテンツの北極星になります——読者は一言も読む前から、どんな変容が待っているかを正確に知り、希望が生まれます。" },
      state.tradition && { label: "スピリチュアルの基盤", value: state.tradition, icon: Sun, gradient: "from-amber-400 to-yellow-500", systemEffect: "すべてのコンテンツを通じて、語彙、哲学的な基盤、伝統固有の参照に影響を与えます", emotionalBenefit: "この伝統を持つ読者は、認められ尊重されていると感じます。言語は表面的な流用ではなく、本物の系譜の重みを帯びています。" },
      (state.angles || []).length > 0 && { label: "コンテンツアングル", value: state.angles.map(a => V4_ANGLES.find(v => v.id === a)?.label).filter(Boolean).join(", "), icon: Layers, gradient: "from-purple-500 to-indigo-500", systemEffect: `${state.angles.length} framing modes active — every title opens with one of these argumentative strategies`, emotionalBenefit: "各アングルは読者に癒しへの異なる入口を提供します。複数のアングルがあることで、変化への準備状態がどこにある人にも、あなたのブランドが届きます。" },
      (state.topicTags || []).length > 0 && { label: "検索テリトリー", value: `${state.topicTags.length} トピックを確保`, icon: Search, gradient: "from-emerald-500 to-teal-500", systemEffect: `${state.topicTags.length} 検索トピックがタイトル生成、キーワードターゲティング、シリーズ計画、広告キャンペーンに反映されます`, emotionalBenefit: "誰かが検索バーに痛みを入力するまさにその瞬間に、あなたのコンテンツが現れます。これはマーケティングではありません——助けを求める叫びに、ちょうど正しい言葉で答えているのです。" },
      state.onboardingLane && { label: "オンボーディングレーン", value: state.onboardingLane.replace(/_/g, " "), icon: Layers, gradient: "from-fuchsia-500 to-purple-500", systemEffect: "証明ストリップとレジストリのマッチングが選択レーンに制約されるようになり、ステークホルダーが早期に正しいアウトプットファミリーをプレビューできます。", emotionalBenefit: "リードしたいレーンに説得力のある証拠があるかどうかをすぐに確認でき、ローンチ時の予期せぬ事態が減ります。" },
      state.onboardingMarket && { label: "オンボーディング市場", value: state.onboardingMarket, icon: Globe, gradient: "from-sky-500 to-cyan-500", systemEffect: "レジストリのマッチングがオンボーディング中に明示的な市場フィルタリングを使用するようになり、市場をまたいだ誤った自信を回避します。", emotionalBenefit: "あなたのチームが、実際にローンチ予定の市場にマッチした事例をレビューできます。" },
      state.formatFocus && { label: "フォーマットフォーカス", value: state.formatFocus === "manga" ? "マンガ / ビジュアル" : "従来型書籍", icon: BookOpen, gradient: "from-cyan-500 to-blue-500", systemEffect: _SF.formats[state.formatFocus]?.systemEffect, emotionalBenefit: _SF.formats[state.formatFocus]?.emotionalBenefit },
      (state.channels || []).length > 0 && { label: "パブリッシングチャンネル", value: `${state.channels.length} channels active`, icon: Globe, gradient: "from-violet-500 to-purple-500", systemEffect: `Content adapts to ${state.channels.length} platforms — each generates format-specific, algorithm-optimized variations`, emotionalBenefit: "読者はすでに時間を過ごしている場所でどこでもあなたを発見します。午前3時のTikTokスクロールでも、日曜日のオーディオブックウォークでも——あなたのブランドは、正しいフォーマットで、そこにあります。" },
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
              onClick={() => { window.location.href = "/brand_handoff_dashboard.html?brand=" + encodeURIComponent(matched.brand_id); }}
              className="mt-4 inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-7 py-3 text-sm font-bold text-white shadow-lg transition-all hover:-translate-y-0.5 hover:bg-emerald-700"
            >
              {t("ui", "Open Brand Director")} <ArrowRight size={16} />
            </button>
          </div>
        )}
        <HybridOfferPanel
          submissionError={submissionError}
          onboardingMarket={state.onboardingMarket}
          contact={state.contact}
          wizardYaml={yamlOutput}
          onAccepted={(match) => { setMatched(match); setSubmissionError(""); }}
          onError={setSubmissionError}
        />
        {submissionError && !parseHybridOfferMessage(submissionError) && (
          <div className="mb-6 rounded-2xl border border-amber-300 bg-amber-50 p-4 text-sm font-semibold text-amber-900">
            {submissionError}
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
                <span className="text-[8px] font-bold uppercase text-white">総合</span>
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
            <p className="text-lg font-bold text-white mb-1">あなたのブランドの世界が誕生しました。</p>
            <p className="text-sm text-white max-w-md mx-auto leading-relaxed">
              You've made {choiceAudit.length} defining choices that shape everything your brand creates — every book, audiobook, video, cover, and piece of social content. Here's what you've built and how it helps the people who need it most.
            </p>
          </div>
        </div>

        {/* Score Cards */}
        <div className="grid grid-cols-4 gap-2 mb-8">
          {[
            { label: "市場性", value: marketability, color: "#10b981" },
            { label: "若年層へのリーチ", value: youthReach, color: "#8b5cf6" },
            { label: "人生へのインパクト", value: lifeImpact, color: "#ec4899" },
            { label: "プラットフォームリーチ", value: reachScore, color: "#3b82f6" },
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
          <h2 className="text-lg font-extrabold text-white mb-1">あなたのブランドの選択</h2>
          <p className="text-xs text-white mb-4">あなたのすべての選択、システムで何を有効化するか、そして読者の精神面と感情面にどう役立つか。</p>

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
                    <div className="text-[9px] font-bold text-emerald-500 bg-emerald-50 px-2 py-0.5 rounded-full flex-shrink-0">有効</div>
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
              <span className="text-sm font-bold text-purple-800">一文であなたのブランドを表すと</span>
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
              <span className="text-xs font-bold text-white">ブランド設定（YAML）</span>
            </div>
            <ChevronRight size={14} className={`text-white transition-transform ${showYaml ? "rotate-90" : ""}`} />
          </button>
          {showYaml && (
            <div className="bg-gray-900 p-4 overflow-auto max-h-96">
              <div className="flex gap-2 mb-3">
                <button onClick={() => { navigator.clipboard.writeText(yamlOutput); setYamlCopied(true); setTimeout(() => setYamlCopied(false), 2000); }}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-bold transition-colors">
                  <Check size={11} />{yamlCopied ? "コピーしました！" : "コピー"}
                </button>
                <button onClick={() => { const blob = new Blob([yamlOutput], {type: "text/yaml"}); const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "brand-config.yaml"; a.click(); }}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-bold transition-colors">
                  <Download size={11} />ダウンロード .yaml
                </button>
              </div>
              <pre className="text-[11px] text-green-400 font-mono whitespace-pre-wrap">{yamlOutput}</pre>
            </div>
          )}
        </div>

        {/* Final Message */}
        <div className="text-center py-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-50 text-emerald-700 text-xs font-bold mb-3">
            <Check size={12} /> ブランド設定を保存しました
          </div>
          <p className="text-sm text-white max-w-md mx-auto">
            あなたのブランドの世界が完成しました。Pearl Primeシステムがすべての選択を使って、人生を変えるカタログを生成します。
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 rounded-2xl border border-violet-200/80 bg-gradient-to-br from-violet-50/90 via-white to-fuchsia-50/30 px-5 py-6 text-center shadow-sm">
        <h2 className="text-2xl font-extrabold tracking-tight sm:text-3xl" style={{ color: '#d97706', fontFamily: 'Cormorant Garamond, serif' }}>連絡先を入力して「アクティベート」をクリック</h2>
        <p className="mx-auto mt-3 max-w-md text-sm text-white/70">
          すぐにブランドカタログへのアクセスが付与され、投稿を始められます
        </p>
      </div>

      <div
        className="mb-6 flex flex-col items-center gap-2 rounded-xl border border-emerald-100/90 bg-emerald-50/40 px-4 py-3 text-[11px] text-emerald-950/80 sm:flex-row sm:flex-wrap sm:justify-center sm:gap-x-8 sm:gap-y-1"
        role="note"
        aria-label="TODO_JA:launch.beforeYouActivate"
      >
        <span className="inline-flex items-center gap-1.5 font-medium">
          <Check size={14} className="shrink-0 text-emerald-600" strokeWidth={2.5} /> TODO_JA:launch.brandDirectionSet
        </span>
        <span className="inline-flex items-center gap-1.5 font-medium">
          <Check size={14} className="shrink-0 text-emerald-600" strokeWidth={2.5} /> 読者とマーケットを選択済み
        </span>
        <span className="inline-flex items-center gap-1.5 font-medium">
          <Check size={14} className="shrink-0 text-emerald-600" strokeWidth={2.5} /> TODO_JA:launch.launchDetailsReady
        </span>
      </div>

      <div className="mb-6 space-y-6">
        <section className="rounded-2xl border border-gray-200/90 bg-white/90 p-5 shadow-sm backdrop-blur-sm">
          <h3 className="mb-4 text-[10px] font-bold uppercase tracking-[0.15em] text-white">TODO_JA:launch.sectionIdentityContact</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-semibold text-white">名 *</label>
              <input
                type="text"
                placeholder="名"
                className="w-full rounded-xl border border-gray-200 p-3 text-sm outline-none focus:border-gray-500"
                value={c.firstName || ""}
                onChange={(e) => handleField("firstName", e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold text-white">姓 *</label>
              <input
                type="text"
                placeholder="姓"
                className="w-full rounded-xl border border-gray-200 p-3 text-sm outline-none focus:border-gray-500"
                value={c.lastName || ""}
                onChange={(e) => handleField("lastName", e.target.value)}
              />
            </div>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-semibold text-white">メールアドレス *</label>
              <input
                type="email"
                placeholder="you@example.com"
                className="w-full rounded-xl border border-gray-200 p-3 text-sm outline-none focus:border-gray-500"
                value={c.email || ""}
                onChange={(e) => handleField("email", e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold text-white">電話番号</label>
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
          <h3 className="mb-4 text-[10px] font-bold uppercase tracking-[0.15em] text-white">2 · メッセージングチャンネル</h3>
          <p className="mb-3 text-[11px] text-white">任意 — メール以外の連絡方法。</p>
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
            <label className="mb-1 block text-[10px] font-semibold text-white">希望の連絡方法</label>
            <select
              className="w-full rounded-lg border border-gray-200 bg-white p-2.5 text-sm outline-none focus:border-gray-500"
              value={c.preferred || "email"}
              onChange={(e) => handleField("preferred", e.target.value)}
            >
              <option value="email">メールのみ</option>
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
            <div className="text-xs font-bold text-slate-800">安全なプロセス</div>
            <p className="mt-1 text-[11px] leading-relaxed text-slate-600">
              税務番号（SSN/EIN）は承認後の別途安全なステップで収集します。このフォームでは金融の機密データを収集しません。
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
        {isReady ? "有効化" : "名前とメールアドレスを入力して有効化"}
      </button>
      {!isReady ? <p className="mt-2 text-center text-[11px] text-white">名・姓・有効なメールアドレスで有効化できます。</p> : null}
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
  y += `  onboarding_lane: "${state.onboardingLane || "self_help"}"\n  onboarding_market: "${state.onboardingMarket || "japan"}"\n`;
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
  const { t } = useJaWizardTranslation();
  const pillars = [
    { icon: PenTool, label: t("ui", "声"), tint: "from-violet-500 to-indigo-600" },
    { icon: Image, label: t("ui", "ビジュアル"), tint: "from-fuchsia-500 to-pink-600" },
    { icon: Users, label: t("ui", "読者"), tint: "from-sky-500 to-blue-600" },
    { icon: Layers, label: t("ui", "フォーマット"), tint: "from-emerald-500 to-teal-600" },
  ];
  return (
    <div className="brand-studio-bg min-h-screen text-white">
      <div className="mx-auto max-w-3xl px-6 py-16">
        <div className="brand-studio-panel p-10 text-center sm:p-12">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-violet-200/80 bg-violet-50/80 px-4 py-1.5 text-xs font-semibold text-violet-800 backdrop-blur-sm">
            <Sparkles size={12} /> {t("ui", "Pearl Prime ブランドスタジオ")}
          </div>
          <h1 className="text-4xl font-black leading-tight tracking-tight text-white sm:text-5xl">{t("ui", "出版ブランドを立ち上げ、形作る")}</h1>
          <p className="mx-auto mt-4 max-w-lg text-base leading-relaxed text-white">
            {t("ui", "一度のガイドセッション——声、外観、証拠が一致します。")}
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
              {t("ui", "構築を開始")} <ChevronRight size={18} />
            </button>
          </div>
          <p className="mt-8 text-center text-xs">
            <a
              href="https://brand-admin-onboarding-bu2.pages.dev/pearl_prime_v6-3.html"
              className="font-semibold text-orange-400 underline decoration-orange-300 underline-offset-2 hover:text-orange-300"
            >
              {t("ui", "最初に戻る")}
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

function IntroJourney({ onNext, onBack, onChooseTeacher }) {
  const { t } = useJaWizardTranslation();
  const phases = [
    { step: "1", title: t("intro", "基盤"), sub: t("intro", "アーキタイプと読者"), color: "from-indigo-500 to-violet-600" },
    { step: "2", title: t("intro", "声"), sub: t("intro", "トーンとインパクト"), color: "from-violet-500 to-fuchsia-600" },
    { step: "3", title: t("intro", "外観とトピック"), sub: t("intro", "ビジュアル＋テリトリー"), color: "from-rose-500 to-orange-500" },
    { step: "4", title: t("intro", "フォーマット"), sub: t("intro", "チャンネルとパイプライン"), color: "from-sky-500 to-cyan-600" },
    { step: "5", title: t("intro", "お披露目"), sub: t("intro", "ブループリントとローンチ"), color: "from-slate-600 to-gray-900" },
  ];
  return (
    <div className="brand-studio-bg min-h-screen text-white">
      <div className="mx-auto max-w-3xl px-6 py-12">
        <button type="button" onClick={onBack} className="mb-6 flex items-center gap-1 text-xs text-white transition-colors hover:text-white">
          <ChevronLeft size={14} /> {t("ui", "戻る")}
        </button>
        <div className="brand-studio-panel p-8 sm:p-10">
          <div className="text-center">
            <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-violet-600">{t("intro", "使い方")}</p>
            <h1 className="mt-2 text-3xl font-black tracking-tight">{t("intro", "5つのビート、11の選択")}</h1>
            <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-white">
              {t("intro", "基盤 → フォーマット → ブループリント → ローンチ")}
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
              {t("ui", "教師の本")} <ArrowRight size={18} />
            </button>
            <button
              type="button"
              onClick={() => {
                try { localStorage.setItem("phoenix_book_mode", JSON.stringify({ mode: "music", teacher: null })); } catch (_) {}
                window.location.href = "/musician_reflections_survey";
              }}
              className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white shadow-lg transition-all hover:-translate-y-0.5 hover:bg-gray-800"
            >
              {t("ui", "音楽の本")} <ArrowRight size={18} />
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
          <ChevronLeft size={14} /> TODO_JA:ui.back
        </button>
        <div className="brand-studio-panel p-6 sm:p-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 text-indigo-600 text-xs font-semibold mb-4"><PenTool size={12} /> ステップ1プレビュー——ライティングボイス</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">同じトピック。まったく異なる声。</h1>
        <p className="text-white mb-8">二つのブランド、一つのトピック——散文とエネルギーの変化を体感してください。</p>
        <CompareBlock labelA="静けさラボ" labelB="クリアマインド・ラボ" colorA="text-indigo-600" colorB="text-amber-600"
          contentA={<div><div className="flex gap-2 mb-3"><div className="w-14 h-20 rounded-lg shadow-md flex-shrink-0" style={{ background: "linear-gradient(135deg, #6366f1, #818cf8, #e0e7ff)" }} /><div><div className="text-[10px] text-white font-semibold uppercase">静けさラボ</div><div className="text-sm font-bold text-white">身体は深夜2時でも記憶している</div></div></div><p className="text-sm text-white leading-relaxed italic border-l-2 border-indigo-300 pl-3">TODO_JA:showcase.sampleProseEnA</p><div className="mt-3 bg-indigo-50 rounded-lg p-3"><div className="text-[10px] font-bold text-indigo-600 uppercase mb-1">エクササイズ</div><p className="text-xs text-indigo-800">TODO_JA:showcase.sampleExerciseEnA</p></div></div>}
          contentB={<div><div className="flex gap-2 mb-3"><div className="w-14 h-20 rounded-lg shadow-md flex-shrink-0" style={{ background: "linear-gradient(135deg, #d97706, #f59e0b, #fef3c7)" }} /><div><div className="text-[10px] text-white font-semibold uppercase">クリアマインド・ラボ</div><div className="text-sm font-bold text-white">スマートフォンがあなたの睡眠を奪っている</div></div></div><p className="text-sm text-white leading-relaxed italic border-l-2 border-amber-400 pl-3">"天井を見つめているのは、脳が昨日の言い争いをループ再生しているからです。"</p><div className="mt-3 bg-amber-50 rounded-lg p-3"><div className="text-[10px] font-bold text-amber-600 uppercase mb-1">エクササイズ</div><p className="text-xs text-amber-800">"スマートフォンを別の部屋へ。仰向けに寝る。吸うより長く吐く。90秒。さあ。"</p></div></div>}
        />
        <div className="mt-8 text-center">
          <button type="button" onClick={onNext} className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white transition-all hover:bg-gray-800">
            表紙の違いを見る <ChevronRight size={18} />
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
          <ChevronLeft size={14} /> TODO_JA:ui.back
        </button>
        <div className="brand-studio-panel p-6 sm:p-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-50 text-rose-600 text-xs font-semibold mb-4"><Image size={12} /> TODO_JA:showcase.visualStylePreview</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">あなたのビジュアルスタイルがすべてを形作る。</h1>
        <p className="text-white mb-8">一つの選択が表紙とサムネイルに波及します。</p>
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
            TODO_JA:showcase.seeVideoStyles <ChevronRight size={18} />
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
          <ChevronLeft size={14} /> TODO_JA:ui.back
        </button>
        <div className="brand-studio-panel p-6 sm:p-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 text-amber-600 text-xs font-semibold mb-4"><Film size={12} /> 動画とソーシャルのプレビュー</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">毎日のコンテンツ。あなたのシグネチャールック。</h1>
        <p className="text-white mb-8">ショートフォーム動画があなたのパレットとムードを受け継ぎます。</p>
        <div className="grid grid-cols-2 gap-4 mb-8">
          {ARCHETYPES.slice(0, 4).map((arch) => (
            <div key={arch.id} className="rounded-xl overflow-hidden border border-gray-200">
              <div className="h-32 flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${arch.coverColors[0]}88, ${arch.coverColors[1]}66)` }}><div className="text-center"><Play size={24} className="text-white/80 mx-auto mb-1" /><div className="text-[10px] text-white/80 font-bold">{arch.name}</div></div></div>
              <div className="p-3 bg-white"><div className="text-xs font-bold text-white">{arch.videoStyle}</div><div className="text-[10px] text-white mt-0.5">YouTube、TikTok、Instagram、Facebook、X で毎日</div></div>
            </div>
          ))}
        </div>
        <div className="mt-8 text-center">
          <button type="button" onClick={onNext} className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white transition-all hover:bg-gray-800">
            TODO_JA:showcase.seeFormatDiversity <ChevronRight size={18} />
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
          <ChevronLeft size={14} /> TODO_JA:ui.back
        </button>
        <div className="brand-studio-panel p-6 sm:p-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 text-emerald-600 text-xs font-semibold mb-4"><Layers size={12} /> Format Diversity</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">一つのブランド。無限のフォーマット。</h1>
        <p className="text-white mb-8">同じDNA——異なるコンテナ。</p>
        <div className="grid grid-cols-3 gap-3 mb-8">
          {V4_FORMATS_STRUCTURAL.map((f) => (
            <div key={f.id} className="p-4 rounded-xl border border-gray-200 bg-white">
              <div className="text-[10px] text-white font-mono mb-1">{f.id}</div><div className="text-xs font-bold text-white">{f.label}</div><div className="text-[10px] text-white mt-0.5">{f.desc}</div>
              <div className="mt-2 flex items-center gap-2"><span className="text-[9px] bg-gray-100 text-white px-2 py-0.5 rounded-full">{f.chapters} ch</span><span className="text-[9px] bg-gray-100 text-white px-2 py-0.5 rounded-full">{f.tier}</span></div>
            </div>
          ))}
        </div>
        <div className="rounded-xl bg-gray-50 border border-gray-200 p-5 mb-8"><p className="text-xs text-white leading-relaxed">マンガ、オーディオ、コース、ジャーナル、動画——同じコアから自動的に適応されます。</p></div>
        <div className="mt-8 text-center">
          <button type="button" onClick={onNext} className="inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-8 py-3.5 text-sm font-bold text-white transition-all hover:bg-gray-800">
            ブランド構築を開始 <ArrowRight size={18} />
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

const STEP_LABELS = ["アーキタイプ", "読者", "きっかけの瞬間", "声のトーン", "ビジュアルスタイル", "感情的な結果", "トピック", "あなたのブランド", "ローンチ"];

export default function BrandWizard() {
  const { strings } = useLocale();
  const { t, td, to, tv, locale, isEn } = useJaWizardTranslation();
  const tVoiceTone = useMemo(() => translateVoiceTone10(strings, VOICE_TONE_10), [strings]);

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
    onboardingLane: "self_help", onboardingMarket: "japan",
    contact: { firstName: "", lastName: "", email: "", phoneCode: "+81", phone: "", line: "", whatsapp: "", wechat: "", messenger: "", preferred: "email" },
  });

  const update = useCallback((patch) => setState((prev) => ({ ...prev, ...patch })), []);
  const scrollTop = () => window.scrollTo({ top: 0, behavior: "instant" });
  const nextIntro = () => { setIntroPage((p) => p + 1); scrollTop(); };
  const prevIntro = () => { if (introPage > 0) { setIntroPage((p) => p - 1); scrollTop(); } };
  const startWizard = () => { setPhase("wizard"); setStep(0); scrollTop(); };
  const nextStep = () => { if (step < 8) { setStep((s) => s + 1); scrollTop(); } };
  const prevStep = () => { if (step > 0) { setStep((s) => s - 1); scrollTop(); } else { setPhase("intro"); setIntroPage(1); scrollTop(); } };
  const goToHowItWorks = () => { setPhase("intro"); setIntroPage(1); scrollTop(); };
  const goToTeacherShowcase = () => { window.location.href = "teacher_showcase-ja.html"; };

  // If ?teacher= / ?mode=composite / ?mode=music in URL, skip intro and jump to wizard step 1.
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlTeacher = params.get("teacher");
    const urlMode = params.get("mode");
    if (urlTeacher || urlMode === "composite" || urlMode === "music") { setPhase("wizard"); setStep(0); scrollTop(); }
  }, []);

  // Market from onboarding.html handoff (?market= / phoenix_onboarding_market) or JA default.
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

  const i18nData = { tArchetypes, tPersonas, tMoments, tVisualStyles, tEmotionCategories, tAngleFeedback, tSelectionFeedback, tProven, tV4FormatsStructural, tVoiceTone, t };

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
          <ChevronLeft size={14} /> {t("ui", "戻る")}
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
                  <ChevronLeft size={16} /> {t("ui", "戻る")}
                </button>
                {step < 8 ? (
                  <button
                    type="button"
                    onClick={nextStep}
                    disabled={!canNext}
                    className={`flex items-center gap-1.5 rounded-xl px-6 py-2.5 text-sm font-bold transition-all ${canNext ? "bg-gray-900 text-white shadow-md shadow-slate-300/40 hover:bg-gray-800" : "cursor-not-allowed bg-gray-200 text-white"}`}
                  >
                    {t("ui", "次へ")} <ChevronRight size={16} />
                  </button>
                ) : null}
              </div>
            </div>
            <div className="hidden w-72 flex-shrink-0 lg:block">
              <div className="sticky top-8">
                <div className="mb-3 text-[10px] font-bold uppercase tracking-wider text-violet-600/90">{t("ui", "スタジオの洞察")}</div>
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
