/**
 * Pearl Prime i18n -- Internationalization module
 * Supports 13 locales across all 7 pages.
 * Auto-detects language from ?lang= param, localStorage, or browser.
 * Creates a language picker dropdown in the nav bar.
 *
 * Usage: <script src="assets/i18n.js"></script>
 *        -- auto-initializes on DOMContentLoaded --
 */
(function () {
  "use strict";

  /* ══════════════════════════════════════════════════════
     SUPPORTED LOCALES
     ══════════════════════════════════════════════════════ */
  var SUPPORTED = [
    "en-US","ja-JP","zh-TW","zh-CN","ko-KR","fr-FR","de-DE",
    "hu-HU","id-ID","th-TH","vi-VN","pt-BR","es-MX"
  ];

  /* ══════════════════════════════════════════════════════
     TRANSLATIONS
     ══════════════════════════════════════════════════════ */
  var I18N = {};

  // ─── en-US ──────────────────────────────────────────
  I18N["en-US"] = {
    // brand_admin_weekly_os.html (director ops console) keys
    "page.title": "Brand Admin -- Pearl Prime",
    "setup.gmail": "Google Account",
    "setup.youtube": "YouTube Channel",
    "setup.kdp": "Amazon KDP",
    "setup.gplay": "Google Play Books",
    "setup.apple": "Apple Books",
    "setup.kobo": "Kobo Writing Life",
    "setup.tiktok": "TikTok Business",
    "setup.instagram": "Instagram Business",
    "setup.webtoon": "WEBTOON Canvas",
    "setup.d2d": "Draft2Digital",
    "wos.min": "min",
    "wos.pctSuffix": "% complete",
    "wos.phaseOf": "Phase {n} of 3",
    "wos.phaseStatic": "Phase 1 of 3",
    "wos.pctStatic": "0% complete",
    "wos.noBrand": "No brand",
    "wos.copy": "COPY",
    "wos.openTmpl": "Open {n}",
    "wos.stepDone": "I've completed this step",
    "wos.kdpWarnStrong": "AI Disclosure required on every upload.",
    "wos.kdpWarnRest": "Amazon requires you to declare AI-assisted content.",
    "pf.Channel Name": "Channel Name",
    "pf.Description": "Description",
    "pf.Author / Publisher": "Author / Publisher",
    "pf.Keywords": "Keywords",
    "pf.Publisher Name": "Publisher Name",
    "pf.Display Name": "Display Name",
    "pf.Bio (150 chars)": "Bio (150 chars)",
    "pf.Username": "Username",
    "pf.Creator Nickname": "Creator Nickname",
    "pf.Series Summary": "Series Summary",
    "pf.Author / Pen Name": "Author / Pen Name",
    "pf.Email": "Email",
    "pf.Publisher": "Publisher",
    "pf.Author Name": "Author Name",
    "pf.Author": "Author",
    "pf.Title Template": "Title Template",
    "topbar.title": "Brand Admin",
    "nav.setup": "Setup",
    "nav.upload": "Upload",
    "nav.weekly": "Weekly",
    "phase.setup": "Setup",
    "phase.firstUpload": "First Upload",
    "phase.weeklyRhythm": "Weekly Rhythm",
    "phase1.title": "Phase 1: Setup",
    "phase1.subtitle": "Create accounts on each platform. Check off when done.",
    "phase2.title": "Phase 2: First Upload",
    "phase3.title": "Phase 3: Weekly Rhythm",
    "picker.title": "Brand Admin",
    "picker.subtitle": "Select a brand to begin",
    "quicklinks.heading": "Quick Platform Links",
    "quicklinks.kdp": "KDP",
    "quicklinks.googlePlay": "Google Play",
    "quicklinks.appleBooks": "Apple Books",
    "quicklinks.youtube": "YouTube",
    "quicklinks.tiktok": "TikTok",
    "quicklinks.webtoon": "WEBTOON",
    "quicklinks.kobo": "Kobo",
    "quicklinks.d2d": "Draft2Digital",
    "quicklinks.instagram": "Instagram",
    "quicklinks.line": "LINE",
    // Nav
    "nav.brand": "Pearl Prime",
    "nav.markets": "Markets",
    "nav.teachers": "Teachers",
    "nav.showcase": "Showcase",
    "nav.intro": "Intro",
    "nav.marketing": "Marketing",
    "nav.dashboard": "Dashboard",
    "nav.matrix": "Matrix",
    "nav.gallery": "Gallery",
    "nav.admin": "Brand Admin",
    // Entry page (pearl_prime_entry)
    "entry.title": "Pearl Prime",
    "entry.subtitle": "Choose Your Market",
    "entry.learn": "Learn More",
    "entry.learn.desc": "Show me how this works",
    "entry.start": "Start Working",
    "entry.start.desc": "I'm ready to go",
    "entry.back.market": "Change Market",
    "entry.back": "Back",
    "entry.onboarding": "Brand Onboarding",
    "entry.onboarding.desc": "Set up my brand for the first time",
    "entry.operations": "Brand Operations",
    "entry.operations.desc": "Do my weekly uploads",
    // Teacher Select
    "teacher.sidebar.title": "Teachers",
    "teacher.samples.heading": "Pearl News \u2014 Teaching Samples",
    "teacher.stat.atoms": "Atoms",
    "teacher.stat.types": "Types",
    "teacher.stat.topics": "Topics",
    "teacher.stat.news": "News Articles",
    "teacher.audio.label": "Audio narration \u2014 owner will provide MP3 samples per teacher",
    "teacher.btn.briefing": "Briefing",
    "teacher.btn.profile": "Full Profile",
    // Teacher Showcase
    "showcase.sidebar.title": "Pearl Prime",
    "showcase.sidebar.sub": "13 TEACHERS / 13 BRANDS",
    // Brand Admin
    "admin.title": "Brand Admin",
    "admin.phase.overview": "Overview",
    "admin.phase.setup": "Setup",
    "admin.phase.upload": "Upload",
    "admin.phase.weekly": "Weekly",
    "admin.phase.label.overview": "Overview",
    "admin.phase.label.setup": "Setup",
    "admin.phase.label.upload": "First Upload",
    "admin.phase.label.weekly": "Weekly Rhythm",
    "admin.progress": "complete",
    "admin.celebration.title": "Phase Complete",
    "admin.celebration.sub": "Next phase unlocked.",
    "admin.celebration.btn": "Continue",
    "admin.links.title": "Quick Platform Links",
    "admin.btn.change": "Change Brand",
    "admin.btn.docs": "Detailed Setup Docs",
    "admin.creds.title": "Your Credentials",
    "admin.creds.hint": "saved securely \u2014 used to verify your postings",
    // Presenter
    "presenter.title": "Pearl Prime Presenter",
    "presenter.subtitle": "Select a deck to begin",
    "presenter.deck.intro": "Pearl Prime Intro",
    "presenter.deck.intro.desc": "Brand admin onboarding. Revenue, architecture, weekly OS.",
    "presenter.deck.marketing": "Marketing Intelligence",
    "presenter.deck.marketing.desc": "13 markets, ad ROI, content audit, fleet rollout.",
    "presenter.deck.us": "US Briefing",
    "presenter.deck.us.desc": "Platform stack, upload guide, revenue projections.",
    "presenter.deck.jp": "Japan Briefing",
    "presenter.deck.jp.desc": "Manga, audiobook.jp, LINE, Piccoma, Japan-specific.",
    "presenter.deck.kr": "Korea Briefing",
    "presenter.deck.kr.desc": "Naver, Kakao, Millie's Library, Korea-specific.",
    "presenter.status.ready": "Ready \u2014 press \u25B6 Play",
    "presenter.btn.back": "Back to Decks",
    // Marketing Dashboard
    "dashboard.logo": "Pearl Prime",
    "dashboard.subtitle": "Marketing Intelligence Dashboard",
    "dashboard.tab.sim": "Ad Spend Simulator",
    "dashboard.tab.heatmap": "Content Heatmap",
    "dashboard.tab.lanes": "Lane Comparison",
    "dashboard.tab.funnel": "Value Ladder",
    "dashboard.tab.fleet": "Fleet Planner",
    "dashboard.label.budget": "Monthly Budget",
    "dashboard.label.platform": "Platform",
    "dashboard.label.lane": "Lane",
    "dashboard.roas": "ROAS Curve",
    "dashboard.revenue.vs.spend": "Revenue vs Spend",
    "dashboard.heatmap.title": "Content Performance Heatmap \u2014 Topic x Brand Strength",
    "dashboard.lane.revenue": "Estimated Year 1 Revenue by Lane",
    "dashboard.lane.competition": "Competition vs Opportunity",
    "dashboard.greenfield": "Greenfield Opportunity Flags",
    "dashboard.funnel.title": "Value Ladder Funnel",
    "dashboard.ltv": "LTV Calculation",
    "dashboard.fleet.title": "Fleet Budget Planner",
    "dashboard.fleet.budget": "Total Monthly Fleet Budget",
    "dashboard.fleet.timeline": "Phase Timeline",
    "dashboard.fleet.allocation": "Budget Allocation",
    "dashboard.fleet.tiers": "Brand Tier Breakdown",
    "dashboard.btn.close": "Close",
    // Market Lane Matrix
    "matrix.title": "Market \u00D7 Lane Matrix",
    "matrix.desc": "Decision surface: what exists by market and lane, where proof is missing, and which comparison sets touch each cell.",
    "matrix.marketing.desc": "Use this table before committing packaging budget.",
    "matrix.nav.hub": "Hub",
    "matrix.nav.wizard": "Live wizard",
    "matrix.nav.gallery": "Examples Gallery",
    "matrix.nav.onboarding": "Master Onboarding",
    "matrix.nav.weekly": "Weekly OS",
    // Common
    "common.back": "Back",
    "common.next": "Next",
    "common.close": "Close",
    "common.copy": "Copy",
    "common.done": "Done",
    "common.loading": "Loading\u2026",
    "picker.lang": "Language"
  };

  // ─── ja-JP ──────────────────────────────────────────
  I18N["ja-JP"] = {
    // brand_admin_weekly_os.html (director ops console) keys
    "page.title": "ブランド管理 — Pearl Prime",
    "setup.gmail": "Google アカウント",
    "setup.youtube": "YouTube チャンネル",
    "setup.kdp": "Amazon KDP",
    "setup.gplay": "Google Play ブックス",
    "setup.apple": "Apple Books",
    "setup.kobo": "Kobo Writing Life",
    "setup.tiktok": "TikTok ビジネス",
    "setup.instagram": "Instagram ビジネス",
    "setup.webtoon": "WEBTOON Canvas",
    "setup.d2d": "Draft2Digital",
    "wos.min": "分",
    "wos.pctSuffix": "% 完了",
    "wos.phaseOf": "フェーズ {n} / 3",
    "wos.phaseStatic": "フェーズ 1 / 3",
    "wos.pctStatic": "0% 完了",
    "wos.noBrand": "ブランド未選択",
    "wos.copy": "コピー",
    "wos.openTmpl": "{n} を開く",
    "wos.stepDone": "このステップを完了しました",
    "wos.kdpWarnStrong": "アップロードごとにAI開示が必要です。",
    "wos.kdpWarnRest": "AmazonはAI支援コンテンツの申告を求めています。",
    "pf.Channel Name": "チャンネル名",
    "pf.Description": "説明",
    "pf.Author / Publisher": "著者 / 出版社",
    "pf.Keywords": "キーワード",
    "pf.Publisher Name": "出版社名",
    "pf.Display Name": "表示名",
    "pf.Bio (150 chars)": "プロフィール（150文字）",
    "pf.Username": "ユーザー名",
    "pf.Creator Nickname": "クリエイター名",
    "pf.Series Summary": "シリーズ概要",
    "pf.Author / Pen Name": "著者 / ペンネーム",
    "pf.Email": "メールアドレス",
    "pf.Publisher": "出版社",
    "pf.Author Name": "著者名",
    "pf.Author": "著者",
    "pf.Title Template": "タイトルテンプレート",
    "topbar.title": "ブランド管理",
    "nav.setup": "セットアップ",
    "nav.upload": "アップロード",
    "nav.weekly": "週次",
    "phase.setup": "セットアップ",
    "phase.firstUpload": "初回アップロード",
    "phase.weeklyRhythm": "週次リズム",
    "phase1.title": "フェーズ1：セットアップ",
    "phase1.subtitle": "各プラットフォームでアカウントを作成し、完了したらチェックしてください。",
    "phase2.title": "フェーズ2：初回アップロード",
    "phase3.title": "フェーズ3：週次リズム",
    "picker.title": "ブランド管理",
    "picker.subtitle": "開始するブランドを選択してください",
    "quicklinks.heading": "クイックリンク",
    "quicklinks.kdp": "KDP",
    "quicklinks.googlePlay": "Google Play",
    "quicklinks.appleBooks": "Apple Books",
    "quicklinks.youtube": "YouTube",
    "quicklinks.tiktok": "TikTok",
    "quicklinks.webtoon": "WEBTOON",
    "quicklinks.kobo": "Kobo",
    "quicklinks.d2d": "Draft2Digital",
    "quicklinks.instagram": "Instagram",
    "quicklinks.line": "LINE",
    "nav.brand": "Pearl Prime",
    "nav.markets": "\u30DE\u30FC\u30B1\u30C3\u30C8",
    "nav.teachers": "\u6307\u5C0E\u8005",
    "nav.showcase": "\u30B7\u30E7\u30FC\u30B1\u30FC\u30B9",
    "nav.intro": "\u7D39\u4ECB",
    "nav.marketing": "\u30DE\u30FC\u30B1\u30C6\u30A3\u30F3\u30B0",
    "nav.dashboard": "\u30C0\u30C3\u30B7\u30E5\u30DC\u30FC\u30C9",
    "nav.matrix": "\u30DE\u30C8\u30EA\u30C3\u30AF\u30B9",
    "nav.gallery": "\u30AE\u30E3\u30E9\u30EA\u30FC",
    "nav.admin": "\u30D6\u30E9\u30F3\u30C9\u7BA1\u7406",
    "entry.title": "Pearl Prime",
    "entry.subtitle": "\u30DE\u30FC\u30B1\u30C3\u30C8\u3092\u9078\u629E",
    "entry.learn": "\u8A73\u3057\u304F\u898B\u308B",
    "entry.learn.desc": "\u4ED5\u7D44\u307F\u3092\u898B\u305B\u3066\u304F\u3060\u3055\u3044",
    "entry.start": "\u4F5C\u696D\u958B\u59CB",
    "entry.start.desc": "\u6E96\u5099\u304C\u3067\u304D\u307E\u3057\u305F",
    "entry.back.market": "\u30DE\u30FC\u30B1\u30C3\u30C8\u3092\u5909\u66F4",
    "entry.back": "\u623B\u308B",
    "entry.onboarding": "\u30D6\u30E9\u30F3\u30C9\u30AA\u30F3\u30DC\u30FC\u30C7\u30A3\u30F3\u30B0",
    "entry.onboarding.desc": "\u521D\u3081\u3066\u30D6\u30E9\u30F3\u30C9\u3092\u8A2D\u5B9A\u3059\u308B",
    "entry.operations": "\u30D6\u30E9\u30F3\u30C9\u904B\u7528",
    "entry.operations.desc": "\u6BCE\u9031\u306E\u30A2\u30C3\u30D7\u30ED\u30FC\u30C9\u3092\u884C\u3046",
    "teacher.sidebar.title": "\u6307\u5C0E\u8005",
    "teacher.samples.heading": "Pearl News \u2014 \u6559\u3048\u306E\u30B5\u30F3\u30D7\u30EB",
    "teacher.stat.atoms": "\u30A2\u30C8\u30E0",
    "teacher.stat.types": "\u30BF\u30A4\u30D7",
    "teacher.stat.topics": "\u30C8\u30D4\u30C3\u30AF",
    "teacher.stat.news": "\u30CB\u30E5\u30FC\u30B9\u8A18\u4E8B",
    "teacher.audio.label": "\u97F3\u58F0\u30CA\u30EC\u30FC\u30B7\u30E7\u30F3 \u2014 \u30AA\u30FC\u30CA\u30FC\u304CMP3\u30B5\u30F3\u30D7\u30EB\u3092\u63D0\u4F9B\u4E88\u5B9A",
    "teacher.btn.briefing": "\u30D6\u30EA\u30FC\u30D5\u30A3\u30F3\u30B0",
    "teacher.btn.profile": "\u5168\u30D7\u30ED\u30D5\u30A3\u30FC\u30EB",
    "showcase.sidebar.title": "Pearl Prime",
    "showcase.sidebar.sub": "13\u540D\u306E\u6307\u5C0E\u8005 / 13\u30D6\u30E9\u30F3\u30C9",
    "admin.title": "\u30D6\u30E9\u30F3\u30C9\u7BA1\u7406",
    "admin.phase.overview": "\u6982\u8981",
    "admin.phase.setup": "\u30BB\u30C3\u30C8\u30A2\u30C3\u30D7",
    "admin.phase.upload": "\u30A2\u30C3\u30D7\u30ED\u30FC\u30C9",
    "admin.phase.weekly": "\u6BCE\u9031",
    "admin.phase.label.overview": "\u6982\u8981",
    "admin.phase.label.setup": "\u30BB\u30C3\u30C8\u30A2\u30C3\u30D7",
    "admin.phase.label.upload": "\u521D\u56DE\u30A2\u30C3\u30D7\u30ED\u30FC\u30C9",
    "admin.phase.label.weekly": "\u9031\u9593\u30EA\u30BA\u30E0",
    "admin.progress": "\u5B8C\u4E86",
    "admin.celebration.title": "\u30D5\u30A7\u30FC\u30BA\u5B8C\u4E86",
    "admin.celebration.sub": "\u6B21\u306E\u30D5\u30A7\u30FC\u30BA\u304C\u89E3\u9664\u3055\u308C\u307E\u3057\u305F\u3002",
    "admin.celebration.btn": "\u7D9A\u3051\u308B",
    "admin.links.title": "\u30AF\u30A4\u30C3\u30AF\u30D7\u30E9\u30C3\u30C8\u30D5\u30A9\u30FC\u30E0\u30EA\u30F3\u30AF",
    "admin.btn.change": "\u30D6\u30E9\u30F3\u30C9\u3092\u5909\u66F4",
    "admin.btn.docs": "\u8A73\u7D30\u30BB\u30C3\u30C8\u30A2\u30C3\u30D7\u30C9\u30AD\u30E5\u30E1\u30F3\u30C8",
    "admin.creds.title": "\u8A8D\u8A3C\u60C5\u5831",
    "admin.creds.hint": "\u5B89\u5168\u306B\u4FDD\u5B58 \u2014 \u6295\u7A3F\u306E\u78BA\u8A8D\u306B\u4F7F\u7528",
    "presenter.title": "Pearl Prime \u30D7\u30EC\u30BC\u30F3\u30BF\u30FC",
    "presenter.subtitle": "\u30C7\u30C3\u30AD\u3092\u9078\u629E\u3057\u3066\u958B\u59CB",
    "presenter.deck.intro": "Pearl Prime \u7D39\u4ECB",
    "presenter.deck.intro.desc": "\u30D6\u30E9\u30F3\u30C9\u7BA1\u7406\u30AA\u30F3\u30DC\u30FC\u30C7\u30A3\u30F3\u30B0\u3002\u53CE\u76CA\u3001\u30A2\u30FC\u30AD\u30C6\u30AF\u30C1\u30E3\u3001\u9031\u9593OS\u3002",
    "presenter.deck.marketing": "\u30DE\u30FC\u30B1\u30C6\u30A3\u30F3\u30B0\u30A4\u30F3\u30C6\u30EA\u30B8\u30A7\u30F3\u30B9",
    "presenter.deck.marketing.desc": "13\u5E02\u5834\u3001\u5E83\u544AROI\u3001\u30B3\u30F3\u30C6\u30F3\u30C4\u76E3\u67FB\u3001\u30D5\u30EA\u30FC\u30C8\u5C55\u958B\u3002",
    "presenter.deck.us": "\u7C73\u56FD\u30D6\u30EA\u30FC\u30D5\u30A3\u30F3\u30B0",
    "presenter.deck.us.desc": "\u30D7\u30E9\u30C3\u30C8\u30D5\u30A9\u30FC\u30E0\u3001\u30A2\u30C3\u30D7\u30ED\u30FC\u30C9\u30AC\u30A4\u30C9\u3001\u53CE\u76CA\u4E88\u6E2C\u3002",
    "presenter.deck.jp": "\u65E5\u672C\u30D6\u30EA\u30FC\u30D5\u30A3\u30F3\u30B0",
    "presenter.deck.jp.desc": "\u30DE\u30F3\u30AC\u3001audiobook.jp\u3001LINE\u3001Piccoma\u3001\u65E5\u672C\u56FA\u6709\u3002",
    "presenter.deck.kr": "\u97D3\u56FD\u30D6\u30EA\u30FC\u30D5\u30A3\u30F3\u30B0",
    "presenter.deck.kr.desc": "Naver\u3001Kakao\u3001Millie's Library\u3001\u97D3\u56FD\u56FA\u6709\u3002",
    "presenter.status.ready": "\u6E96\u5099\u5B8C\u4E86 \u2014 \u25B6 \u3092\u62BC\u3057\u3066\u518D\u751F",
    "presenter.btn.back": "\u30C7\u30C3\u30AD\u4E00\u89A7\u3078\u623B\u308B",
    "dashboard.logo": "Pearl Prime",
    "dashboard.subtitle": "\u30DE\u30FC\u30B1\u30C6\u30A3\u30F3\u30B0\u30A4\u30F3\u30C6\u30EA\u30B8\u30A7\u30F3\u30B9\u30C0\u30C3\u30B7\u30E5\u30DC\u30FC\u30C9",
    "dashboard.tab.sim": "\u5E83\u544A\u8CBB\u30B7\u30DF\u30E5\u30EC\u30FC\u30BF",
    "dashboard.tab.heatmap": "\u30B3\u30F3\u30C6\u30F3\u30C4\u30D2\u30FC\u30C8\u30DE\u30C3\u30D7",
    "dashboard.tab.lanes": "\u30EC\u30FC\u30F3\u6BD4\u8F03",
    "dashboard.tab.funnel": "\u30D0\u30EA\u30E5\u30FC\u30E9\u30C0\u30FC",
    "dashboard.tab.fleet": "\u30D5\u30EA\u30FC\u30C8\u30D7\u30E9\u30F3\u30CA\u30FC",
    "dashboard.label.budget": "\u6708\u9858\u4E88\u7B97",
    "dashboard.label.platform": "\u30D7\u30E9\u30C3\u30C8\u30D5\u30A9\u30FC\u30E0",
    "dashboard.label.lane": "\u30EC\u30FC\u30F3",
    "dashboard.roas": "ROAS\u30AB\u30FC\u30D6",
    "dashboard.revenue.vs.spend": "\u53CE\u76CA vs \u652F\u51FA",
    "dashboard.heatmap.title": "\u30B3\u30F3\u30C6\u30F3\u30C4\u30D1\u30D5\u30A9\u30FC\u30DE\u30F3\u30B9\u30D2\u30FC\u30C8\u30DE\u30C3\u30D7",
    "dashboard.lane.revenue": "\u30EC\u30FC\u30F3\u5225\u521D\u5E74\u5EA6\u63A8\u5B9A\u53CE\u76CA",
    "dashboard.lane.competition": "\u7AF6\u4E89 vs \u6A5F\u4F1A",
    "dashboard.greenfield": "\u30B0\u30EA\u30FC\u30F3\u30D5\u30A3\u30FC\u30EB\u30C9\u6A5F\u4F1A\u30D5\u30E9\u30B0",
    "dashboard.funnel.title": "\u30D0\u30EA\u30E5\u30FC\u30E9\u30C0\u30FC\u30D5\u30A1\u30CD\u30EB",
    "dashboard.ltv": "LTV\u8A08\u7B97",
    "dashboard.fleet.title": "\u30D5\u30EA\u30FC\u30C8\u4E88\u7B97\u30D7\u30E9\u30F3\u30CA\u30FC",
    "dashboard.fleet.budget": "\u6708\u9855\u30D5\u30EA\u30FC\u30C8\u4E88\u7B97\u5408\u8A08",
    "dashboard.fleet.timeline": "\u30D5\u30A7\u30FC\u30BA\u30BF\u30A4\u30E0\u30E9\u30A4\u30F3",
    "dashboard.fleet.allocation": "\u4E88\u7B97\u914D\u5206",
    "dashboard.fleet.tiers": "\u30D6\u30E9\u30F3\u30C9\u30C6\u30A3\u30A2\u5185\u8A33",
    "dashboard.btn.close": "\u9589\u3058\u308B",
    "matrix.title": "\u30DE\u30FC\u30B1\u30C3\u30C8 \u00D7 \u30EC\u30FC\u30F3\u30DE\u30C8\u30EA\u30C3\u30AF\u30B9",
    "matrix.desc": "\u610F\u601D\u6C7A\u5B9A\u30B5\u30FC\u30D5\u30A7\u30B9\uFF1A\u5E02\u5834\u3068\u30EC\u30FC\u30F3\u3054\u3068\u306E\u5B58\u5728\u72B6\u6CC1\u3001\u8A3C\u62E0\u306E\u6B20\u5982\u3001\u6BD4\u8F03\u30BB\u30C3\u30C8\u3002",
    "matrix.marketing.desc": "\u30D1\u30C3\u30B1\u30FC\u30B8\u30F3\u30B0\u4E88\u7B97\u6295\u5165\u524D\u306B\u3053\u306E\u30C6\u30FC\u30D6\u30EB\u3092\u4F7F\u7528\u3002",
    "matrix.nav.hub": "\u30CF\u30D6",
    "matrix.nav.wizard": "\u30E9\u30A4\u30D6\u30A6\u30A3\u30B6\u30FC\u30C9",
    "matrix.nav.gallery": "\u4F8B\u30AE\u30E3\u30E9\u30EA\u30FC",
    "matrix.nav.onboarding": "\u30DE\u30B9\u30BF\u30FC\u30AA\u30F3\u30DC\u30FC\u30C7\u30A3\u30F3\u30B0",
    "matrix.nav.weekly": "\u9031\u9593OS",
    "common.back": "\u623B\u308B",
    "common.next": "\u6B21\u3078",
    "common.close": "\u9589\u3058\u308B",
    "common.copy": "\u30B3\u30D4\u30FC",
    "common.done": "\u5B8C\u4E86",
    "common.loading": "\u8AAD\u307F\u8FBC\u307F\u4E2D\u2026",
    "picker.lang": "\u8A00\u8A9E"
  };

  // ─── zh-TW ──────────────────────────────────────────
  I18N["zh-TW"] = {
    // brand_admin_weekly_os.html (director ops console) keys
    "page.title": "品牌管理 — Pearl Prime",
    "setup.gmail": "Google 帳號",
    "setup.youtube": "YouTube 頻道",
    "setup.kdp": "Amazon KDP",
    "setup.gplay": "Google Play 圖書（台灣）",
    "setup.apple": "Apple Books（台灣）",
    "setup.kobo": "Kobo Writing Life（台灣）",
    "setup.tiktok": "TikTok 商業帳號",
    "setup.instagram": "Instagram 商業帳號",
    "setup.webtoon": "LINE Webtoon Canvas",
    "setup.d2d": "Draft2Digital",
    "wos.min": "分鐘",
    "wos.pctSuffix": "% 完成",
    "wos.phaseOf": "階段 {n} / 3",
    "wos.phaseStatic": "階段 1 / 3",
    "wos.pctStatic": "0% 完成",
    "wos.noBrand": "尚未選擇品牌",
    "wos.copy": "複製",
    "wos.openTmpl": "開啟 {n}",
    "wos.stepDone": "我已完成此步驟",
    "wos.kdpWarnStrong": "每次上傳都需申報 AI 內容。",
    "wos.kdpWarnRest": "Amazon 要求申報 AI 輔助內容。",
    "pf.Channel Name": "頻道名稱",
    "pf.Description": "簡介",
    "pf.Author / Publisher": "作者 / 出版社",
    "pf.Keywords": "關鍵字",
    "pf.Publisher Name": "出版社名稱",
    "pf.Display Name": "顯示名稱",
    "pf.Bio (150 chars)": "個人簡介（150 字）",
    "pf.Username": "使用者名稱",
    "pf.Creator Nickname": "創作者暱稱",
    "pf.Series Summary": "系列簡介",
    "pf.Author / Pen Name": "作者 / 筆名",
    "pf.Email": "電子郵件",
    "pf.Publisher": "出版社",
    "pf.Author Name": "作者名稱",
    "pf.Author": "作者",
    "pf.Title Template": "書名範本",
    "topbar.title": "品牌管理",
    "nav.setup": "設定",
    "nav.upload": "上傳",
    "nav.weekly": "每週",
    "phase.setup": "設定",
    "phase.firstUpload": "首次上傳",
    "phase.weeklyRhythm": "每週節奏",
    "phase1.title": "階段 1：平台設定",
    "phase1.subtitle": "在各平台上建立帳號，完成後請勾選。",
    "phase2.title": "階段 2：首次上傳",
    "phase3.title": "階段 3：每週節奏",
    "picker.title": "品牌管理",
    "picker.subtitle": "選擇品牌以開始",
    "quicklinks.heading": "平台快速連結",
    "quicklinks.kdp": "KDP",
    "quicklinks.googlePlay": "Google Play",
    "quicklinks.appleBooks": "Apple Books",
    "quicklinks.youtube": "YouTube",
    "quicklinks.tiktok": "TikTok",
    "quicklinks.webtoon": "Webtoon",
    "quicklinks.kobo": "Kobo",
    "quicklinks.d2d": "Draft2Digital",
    "quicklinks.instagram": "Instagram",
    "quicklinks.line": "LINE",
    "nav.brand": "Pearl Prime",
    "nav.markets": "\u5E02\u5834",
    "nav.teachers": "\u5C0E\u5E2B",
    "nav.showcase": "\u5C55\u793A",
    "nav.intro": "\u4ECB\u7D39",
    "nav.marketing": "\u884C\u92B7",
    "nav.dashboard": "\u5100\u8868\u677F",
    "nav.matrix": "\u77E9\u9663",
    "nav.gallery": "\u5C55\u5ECA",
    "nav.admin": "\u54C1\u724C\u7BA1\u7406",
    "entry.title": "Pearl Prime",
    "entry.subtitle": "\u9078\u64C7\u60A8\u7684\u5E02\u5834",
    "entry.learn": "\u77AD\u89E3\u66F4\u591A",
    "entry.learn.desc": "\u544A\u8A34\u6211\u5982\u4F55\u904B\u4F5C",
    "entry.start": "\u958B\u59CB\u5DE5\u4F5C",
    "entry.start.desc": "\u6211\u5DF2\u6E96\u5099\u5C31\u7DD2",
    "entry.back.market": "\u66F4\u63DB\u5E02\u5834",
    "entry.back": "\u8FD4\u56DE",
    "entry.onboarding": "\u54C1\u724C\u5165\u9580",
    "entry.onboarding.desc": "\u9996\u6B21\u8A2D\u5B9A\u6211\u7684\u54C1\u724C",
    "entry.operations": "\u54C1\u724C\u71DF\u904B",
    "entry.operations.desc": "\u57F7\u884C\u6BCF\u9031\u4E0A\u50B3",
    "teacher.sidebar.title": "\u5C0E\u5E2B",
    "teacher.samples.heading": "Pearl News \u2014 \u6559\u5B78\u7BC4\u4F8B",
    "teacher.stat.atoms": "\u539F\u5B50",
    "teacher.stat.types": "\u985E\u578B",
    "teacher.stat.topics": "\u4E3B\u984C",
    "teacher.stat.news": "\u65B0\u805E\u6587\u7AE0",
    "teacher.audio.label": "\u97F3\u983B\u65C1\u767D \u2014 \u64C1\u6709\u8005\u5C07\u63D0\u4F9B\u5404\u5C0E\u5E2BMP3\u6A23\u672C",
    "teacher.btn.briefing": "\u7C21\u5831",
    "teacher.btn.profile": "\u5B8C\u6574\u6A94\u6848",
    "showcase.sidebar.title": "Pearl Prime",
    "showcase.sidebar.sub": "13\u4F4D\u5C0E\u5E2B / 13\u500B\u54C1\u724C",
    "admin.title": "\u54C1\u724C\u7BA1\u7406",
    "admin.phase.overview": "\u6982\u89BD",
    "admin.phase.setup": "\u8A2D\u5B9A",
    "admin.phase.upload": "\u4E0A\u50B3",
    "admin.phase.weekly": "\u6BCF\u9031",
    "admin.phase.label.overview": "\u6982\u89BD",
    "admin.phase.label.setup": "\u8A2D\u5B9A",
    "admin.phase.label.upload": "\u9996\u6B21\u4E0A\u50B3",
    "admin.phase.label.weekly": "\u6BCF\u9031\u7BC0\u594F",
    "admin.progress": "\u5B8C\u6210",
    "admin.celebration.title": "\u968E\u6BB5\u5B8C\u6210",
    "admin.celebration.sub": "\u4E0B\u4E00\u968E\u6BB5\u5DF2\u89E3\u9396\u3002",
    "admin.celebration.btn": "\u7E7C\u7E8C",
    "admin.links.title": "\u5FEB\u901F\u5E73\u53F0\u9023\u7D50",
    "admin.btn.change": "\u66F4\u63DB\u54C1\u724C",
    "admin.btn.docs": "\u8A73\u7D30\u8A2D\u5B9A\u6587\u4EF6",
    "admin.creds.title": "\u60A8\u7684\u6191\u8B49",
    "admin.creds.hint": "\u5B89\u5168\u5132\u5B58 \u2014 \u7528\u65BC\u9A57\u8B49\u60A8\u7684\u767C\u5E03",
    "presenter.title": "Pearl Prime \u7C21\u5831",
    "presenter.subtitle": "\u9078\u64C7\u7C21\u5831\u958B\u59CB",
    "presenter.deck.intro": "Pearl Prime \u4ECB\u7D39",
    "presenter.deck.intro.desc": "\u54C1\u724C\u7BA1\u7406\u5165\u9580\u3002\u53CE\u76CA\u3001\u67B6\u69CB\u3001\u6BCF\u9031OS\u3002",
    "presenter.deck.marketing": "\u884C\u92B7\u667A\u6167",
    "presenter.deck.marketing.desc": "13\u500B\u5E02\u5834\u3001\u5EE3\u544AROI\u3001\u5167\u5BB9\u5BE9\u8A08\u3001\u8ECA\u968A\u5C55\u958B\u3002",
    "presenter.deck.us": "\u7F8E\u570B\u7C21\u5831",
    "presenter.deck.us.desc": "\u5E73\u53F0\u67B6\u69CB\u3001\u4E0A\u50B3\u6307\u5357\u3001\u53CE\u76CA\u9810\u6E2C\u3002",
    "presenter.deck.jp": "\u65E5\u672C\u7C21\u5831",
    "presenter.deck.jp.desc": "\u6F2B\u756B\u3001audiobook.jp\u3001LINE\u3001Piccoma\u3001\u65E5\u672C\u5C08\u5C6C\u3002",
    "presenter.deck.kr": "\u97D3\u570B\u7C21\u5831",
    "presenter.deck.kr.desc": "Naver\u3001Kakao\u3001Millie's Library\u3001\u97D3\u570B\u5C08\u5C6C\u3002",
    "presenter.status.ready": "\u5DF2\u5C31\u7DD2 \u2014 \u6309 \u25B6 \u64AD\u653E",
    "presenter.btn.back": "\u8FD4\u56DE\u7C21\u5831\u5217\u8868",
    "dashboard.logo": "Pearl Prime",
    "dashboard.subtitle": "\u884C\u92B7\u667A\u6167\u5100\u8868\u677F",
    "dashboard.tab.sim": "\u5EE3\u544A\u652F\u51FA\u6A21\u64EC\u5668",
    "dashboard.tab.heatmap": "\u5167\u5BB9\u71B1\u5716",
    "dashboard.tab.lanes": "\u8CFD\u9053\u6BD4\u8F03",
    "dashboard.tab.funnel": "\u50F9\u503C\u968E\u68AF",
    "dashboard.tab.fleet": "\u8ECA\u968A\u898F\u5283",
    "dashboard.label.budget": "\u6708\u9810\u7B97",
    "dashboard.label.platform": "\u5E73\u53F0",
    "dashboard.label.lane": "\u8CFD\u9053",
    "dashboard.roas": "ROAS\u66F2\u7DDA",
    "dashboard.revenue.vs.spend": "\u53CE\u76CA vs \u652F\u51FA",
    "dashboard.heatmap.title": "\u5167\u5BB9\u8868\u73FE\u71B1\u5716",
    "dashboard.lane.revenue": "\u8CFD\u9053\u5225\u7B2C\u4E00\u5E74\u9810\u4F30\u53CE\u76CA",
    "dashboard.lane.competition": "\u7AF6\u722D vs \u6A5F\u6703",
    "dashboard.greenfield": "\u7DA0\u5730\u6A5F\u6703\u6A19\u8A8C",
    "dashboard.funnel.title": "\u50F9\u503C\u968E\u68AF\u6F0F\u6597",
    "dashboard.ltv": "LTV\u8A08\u7B97",
    "dashboard.fleet.title": "\u8ECA\u968A\u9810\u7B97\u898F\u5283",
    "dashboard.fleet.budget": "\u6BCF\u6708\u8ECA\u968A\u7E3D\u9810\u7B97",
    "dashboard.fleet.timeline": "\u968E\u6BB5\u6642\u9593\u7DDA",
    "dashboard.fleet.allocation": "\u9810\u7B97\u5206\u914D",
    "dashboard.fleet.tiers": "\u54C1\u724C\u5C64\u7D1A\u660E\u7D30",
    "dashboard.btn.close": "\u95DC\u9589",
    "matrix.title": "\u5E02\u5834 \u00D7 \u8CFD\u9053\u77E9\u9663",
    "matrix.desc": "\u6C7A\u7B56\u8868\u9762\uFF1A\u5404\u5E02\u5834\u8207\u8CFD\u9053\u7684\u5B58\u5728\u72C0\u614B\u3001\u8B49\u64DA\u7F3A\u53E3\u3001\u6BD4\u8F03\u96C6\u3002",
    "matrix.marketing.desc": "\u5728\u6295\u5165\u5305\u88DD\u9810\u7B97\u4E4B\u524D\u4F7F\u7528\u6B64\u8868\u3002",
    "matrix.nav.hub": "\u4E2D\u5FC3",
    "matrix.nav.wizard": "\u5373\u6642\u7CBE\u9748",
    "matrix.nav.gallery": "\u7BC4\u4F8B\u5C55\u5ECA",
    "matrix.nav.onboarding": "\u4E3B\u5165\u9580",
    "matrix.nav.weekly": "\u6BCF\u9031OS",
    "common.back": "\u8FD4\u56DE",
    "common.next": "\u4E0B\u4E00\u6B65",
    "common.close": "\u95DC\u9589",
    "common.copy": "\u8907\u88FD",
    "common.done": "\u5B8C\u6210",
    "common.loading": "\u8F09\u5165\u4E2D\u2026",
    "picker.lang": "\u8A9E\u8A00"
  };

  // ─── zh-CN ──────────────────────────────────────────
  I18N["zh-CN"] = {
    "nav.brand": "Pearl Prime",
    "nav.markets": "\u5E02\u573A",
    "nav.teachers": "\u5BFC\u5E08",
    "nav.showcase": "\u5C55\u793A",
    "nav.intro": "\u4ECB\u7ECD",
    "nav.marketing": "\u8425\u9500",
    "nav.dashboard": "\u4EEA\u8868\u677F",
    "nav.matrix": "\u77E9\u9635",
    "nav.gallery": "\u5C55\u5ECA",
    "nav.admin": "\u54C1\u724C\u7BA1\u7406",
    "entry.title": "Pearl Prime",
    "entry.subtitle": "\u9009\u62E9\u60A8\u7684\u5E02\u573A",
    "entry.learn": "\u4E86\u89E3\u66F4\u591A",
    "entry.learn.desc": "\u544A\u8BC9\u6211\u5982\u4F55\u8FD0\u4F5C",
    "entry.start": "\u5F00\u59CB\u5DE5\u4F5C",
    "entry.start.desc": "\u6211\u5DF2\u51C6\u5907\u5C31\u7EEA",
    "entry.back.market": "\u66F4\u6362\u5E02\u573A",
    "entry.back": "\u8FD4\u56DE",
    "entry.onboarding": "\u54C1\u724C\u5165\u95E8",
    "entry.onboarding.desc": "\u9996\u6B21\u8BBE\u7F6E\u6211\u7684\u54C1\u724C",
    "entry.operations": "\u54C1\u724C\u8FD0\u8425",
    "entry.operations.desc": "\u6267\u884C\u6BCF\u5468\u4E0A\u4F20",
    "teacher.sidebar.title": "\u5BFC\u5E08",
    "teacher.samples.heading": "Pearl News \u2014 \u6559\u5B66\u8303\u4F8B",
    "teacher.stat.atoms": "\u539F\u5B50",
    "teacher.stat.types": "\u7C7B\u578B",
    "teacher.stat.topics": "\u4E3B\u9898",
    "teacher.stat.news": "\u65B0\u95FB\u6587\u7AE0",
    "teacher.audio.label": "\u97F3\u9891\u65C1\u767D \u2014 \u62E5\u6709\u8005\u5C06\u63D0\u4F9B\u5404\u5BFC\u5E08MP3\u6837\u672C",
    "teacher.btn.briefing": "\u7B80\u62A5",
    "teacher.btn.profile": "\u5B8C\u6574\u6863\u6848",
    "showcase.sidebar.title": "Pearl Prime",
    "showcase.sidebar.sub": "13\u4F4D\u5BFC\u5E08 / 13\u4E2A\u54C1\u724C",
    "admin.title": "\u54C1\u724C\u7BA1\u7406",
    "admin.phase.overview": "\u6982\u89C8",
    "admin.phase.setup": "\u8BBE\u7F6E",
    "admin.phase.upload": "\u4E0A\u4F20",
    "admin.phase.weekly": "\u6BCF\u5468",
    "admin.phase.label.overview": "\u6982\u89C8",
    "admin.phase.label.setup": "\u8BBE\u7F6E",
    "admin.phase.label.upload": "\u9996\u6B21\u4E0A\u4F20",
    "admin.phase.label.weekly": "\u6BCF\u5468\u8282\u594F",
    "admin.progress": "\u5B8C\u6210",
    "admin.celebration.title": "\u9636\u6BB5\u5B8C\u6210",
    "admin.celebration.sub": "\u4E0B\u4E00\u9636\u6BB5\u5DF2\u89E3\u9501\u3002",
    "admin.celebration.btn": "\u7EE7\u7EED",
    "admin.links.title": "\u5FEB\u901F\u5E73\u53F0\u94FE\u63A5",
    "admin.btn.change": "\u66F4\u6362\u54C1\u724C",
    "admin.btn.docs": "\u8BE6\u7EC6\u8BBE\u7F6E\u6587\u6863",
    "admin.creds.title": "\u60A8\u7684\u51ED\u8BC1",
    "admin.creds.hint": "\u5B89\u5168\u5B58\u50A8 \u2014 \u7528\u4E8E\u9A8C\u8BC1\u60A8\u7684\u53D1\u5E03",
    "presenter.title": "Pearl Prime \u6F14\u793A",
    "presenter.subtitle": "\u9009\u62E9\u6F14\u793A\u5F00\u59CB",
    "presenter.deck.intro": "Pearl Prime \u4ECB\u7ECD",
    "presenter.deck.intro.desc": "\u54C1\u724C\u7BA1\u7406\u5165\u95E8\u3002\u6536\u76CA\u3001\u67B6\u6784\u3001\u6BCF\u5468OS\u3002",
    "presenter.deck.marketing": "\u8425\u9500\u667A\u80FD",
    "presenter.deck.marketing.desc": "13\u4E2A\u5E02\u573A\u3001\u5E7F\u544AROI\u3001\u5185\u5BB9\u5BA1\u8BA1\u3001\u8F66\u961F\u5C55\u5F00\u3002",
    "presenter.deck.us": "\u7F8E\u56FD\u7B80\u62A5",
    "presenter.deck.us.desc": "\u5E73\u53F0\u67B6\u6784\u3001\u4E0A\u4F20\u6307\u5357\u3001\u6536\u76CA\u9884\u6D4B\u3002",
    "presenter.deck.jp": "\u65E5\u672C\u7B80\u62A5",
    "presenter.deck.jp.desc": "\u6F2B\u753B\u3001audiobook.jp\u3001LINE\u3001Piccoma\u3001\u65E5\u672C\u4E13\u5C5E\u3002",
    "presenter.deck.kr": "\u97E9\u56FD\u7B80\u62A5",
    "presenter.deck.kr.desc": "Naver\u3001Kakao\u3001Millie's Library\u3001\u97E9\u56FD\u4E13\u5C5E\u3002",
    "presenter.status.ready": "\u5DF2\u5C31\u7EEA \u2014 \u6309 \u25B6 \u64AD\u653E",
    "presenter.btn.back": "\u8FD4\u56DE\u6F14\u793A\u5217\u8868",
    "dashboard.logo": "Pearl Prime",
    "dashboard.subtitle": "\u8425\u9500\u667A\u80FD\u4EEA\u8868\u677F",
    "dashboard.tab.sim": "\u5E7F\u544A\u652F\u51FA\u6A21\u62DF\u5668",
    "dashboard.tab.heatmap": "\u5185\u5BB9\u70ED\u56FE",
    "dashboard.tab.lanes": "\u8D5B\u9053\u6BD4\u8F83",
    "dashboard.tab.funnel": "\u4EF7\u503C\u9636\u68AF",
    "dashboard.tab.fleet": "\u8F66\u961F\u89C4\u5212",
    "dashboard.label.budget": "\u6708\u9884\u7B97",
    "dashboard.label.platform": "\u5E73\u53F0",
    "dashboard.label.lane": "\u8D5B\u9053",
    "dashboard.roas": "ROAS\u66F2\u7EBF",
    "dashboard.revenue.vs.spend": "\u6536\u76CA vs \u652F\u51FA",
    "dashboard.heatmap.title": "\u5185\u5BB9\u8868\u73B0\u70ED\u56FE",
    "dashboard.lane.revenue": "\u8D5B\u9053\u522B\u7B2C\u4E00\u5E74\u9884\u4F30\u6536\u76CA",
    "dashboard.lane.competition": "\u7ADE\u4E89 vs \u673A\u4F1A",
    "dashboard.greenfield": "\u7EFF\u5730\u673A\u4F1A\u6807\u5FD7",
    "dashboard.funnel.title": "\u4EF7\u503C\u9636\u68AF\u6F0F\u6597",
    "dashboard.ltv": "LTV\u8BA1\u7B97",
    "dashboard.fleet.title": "\u8F66\u961F\u9884\u7B97\u89C4\u5212",
    "dashboard.fleet.budget": "\u6BCF\u6708\u8F66\u961F\u603B\u9884\u7B97",
    "dashboard.fleet.timeline": "\u9636\u6BB5\u65F6\u95F4\u7EBF",
    "dashboard.fleet.allocation": "\u9884\u7B97\u5206\u914D",
    "dashboard.fleet.tiers": "\u54C1\u724C\u5C42\u7EA7\u660E\u7EC6",
    "dashboard.btn.close": "\u5173\u95ED",
    "matrix.title": "\u5E02\u573A \u00D7 \u8D5B\u9053\u77E9\u9635",
    "matrix.desc": "\u51B3\u7B56\u8868\u9762\uFF1A\u5404\u5E02\u573A\u4E0E\u8D5B\u9053\u7684\u5B58\u5728\u72B6\u6001\u3001\u8BC1\u636E\u7F3A\u53E3\u3001\u6BD4\u8F83\u96C6\u3002",
    "matrix.marketing.desc": "\u5728\u6295\u5165\u5305\u88C5\u9884\u7B97\u4E4B\u524D\u4F7F\u7528\u6B64\u8868\u3002",
    "matrix.nav.hub": "\u4E2D\u5FC3",
    "matrix.nav.wizard": "\u5373\u65F6\u5411\u5BFC",
    "matrix.nav.gallery": "\u8303\u4F8B\u5C55\u5ECA",
    "matrix.nav.onboarding": "\u4E3B\u5165\u95E8",
    "matrix.nav.weekly": "\u6BCF\u5468OS",
    "common.back": "\u8FD4\u56DE",
    "common.next": "\u4E0B\u4E00\u6B65",
    "common.close": "\u5173\u95ED",
    "common.copy": "\u590D\u5236",
    "common.done": "\u5B8C\u6210",
    "common.loading": "\u52A0\u8F7D\u4E2D\u2026",
    "picker.lang": "\u8BED\u8A00"
  };

  // ─── ko-KR ──────────────────────────────────────────
  I18N["ko-KR"] = {
    "nav.brand": "Pearl Prime",
    "nav.markets": "\uB9C8\uCF13",
    "nav.teachers": "\uAD50\uC0AC",
    "nav.showcase": "\uC1FC\uCF00\uC774\uC2A4",
    "nav.intro": "\uC18C\uAC1C",
    "nav.marketing": "\uB9C8\uCF00\uD305",
    "nav.dashboard": "\uB300\uC2DC\uBCF4\uB4DC",
    "nav.matrix": "\uB9E4\uD2B8\uB9AD\uC2A4",
    "nav.gallery": "\uAC24\uB7EC\uB9AC",
    "nav.admin": "\uBE0C\uB79C\uB4DC \uAD00\uB9AC",
    "entry.title": "Pearl Prime",
    "entry.subtitle": "\uB9C8\uCF13\uC744 \uC120\uD0DD\uD558\uC138\uC694",
    "entry.learn": "\uC790\uC138\uD788 \uBCF4\uAE30",
    "entry.learn.desc": "\uC5B4\uB5BB\uAC8C \uC791\uB3D9\uD558\uB294\uC9C0 \uBCF4\uC5EC\uC8FC\uC138\uC694",
    "entry.start": "\uC791\uC5C5 \uC2DC\uC791",
    "entry.start.desc": "\uC900\uBE44\uAC00 \uB418\uC5C8\uC2B5\uB2C8\uB2E4",
    "entry.back.market": "\uB9C8\uCF13 \uBCC0\uACBD",
    "entry.back": "\uB4A4\uB85C",
    "entry.onboarding": "\uBE0C\uB79C\uB4DC \uC628\uBCF4\uB529",
    "entry.onboarding.desc": "\uCC98\uC74C\uC73C\uB85C \uBE0C\uB79C\uB4DC \uC124\uC815",
    "entry.operations": "\uBE0C\uB79C\uB4DC \uC6B4\uC601",
    "entry.operations.desc": "\uC8FC\uAC04 \uC5C5\uB85C\uB4DC \uC2E4\uD589",
    "teacher.sidebar.title": "\uAD50\uC0AC",
    "teacher.samples.heading": "Pearl News \u2014 \uAD50\uC721 \uC0D8\uD50C",
    "teacher.stat.atoms": "\uC544\uD1B0",
    "teacher.stat.types": "\uC720\uD615",
    "teacher.stat.topics": "\uC8FC\uC81C",
    "teacher.stat.news": "\uB274\uC2A4 \uAE30\uC0AC",
    "teacher.audio.label": "\uC624\uB514\uC624 \uB0B4\uB808\uC774\uC158 \u2014 \uC18C\uC720\uC790\uAC00 \uAD50\uC0AC\uBCC4 MP3 \uC0D8\uD50C \uC81C\uACF5 \uC608\uC815",
    "teacher.btn.briefing": "\uBE0C\uB9AC\uD551",
    "teacher.btn.profile": "\uC804\uCCB4 \uD504\uB85C\uD544",
    "showcase.sidebar.title": "Pearl Prime",
    "showcase.sidebar.sub": "13\uBA85\uC758 \uAD50\uC0AC / 13\uAC1C \uBE0C\uB79C\uB4DC",
    "admin.title": "\uBE0C\uB79C\uB4DC \uAD00\uB9AC",
    "admin.phase.overview": "\uAC1C\uC694",
    "admin.phase.setup": "\uC124\uC815",
    "admin.phase.upload": "\uC5C5\uB85C\uB4DC",
    "admin.phase.weekly": "\uC8FC\uAC04",
    "admin.phase.label.overview": "\uAC1C\uC694",
    "admin.phase.label.setup": "\uC124\uC815",
    "admin.phase.label.upload": "\uCCAB \uC5C5\uB85C\uB4DC",
    "admin.phase.label.weekly": "\uC8FC\uAC04 \uB9AC\uB4EC",
    "admin.progress": "\uC644\uB8CC",
    "admin.celebration.title": "\uB2E8\uACC4 \uC644\uB8CC",
    "admin.celebration.sub": "\uB2E4\uC74C \uB2E8\uACC4\uAC00 \uD574\uC81C\uB418\uC5C8\uC2B5\uB2C8\uB2E4.",
    "admin.celebration.btn": "\uACC4\uC18D",
    "admin.links.title": "\uBE60\uB978 \uD50C\uB7AB\uD3FC \uB9C1\uD06C",
    "admin.btn.change": "\uBE0C\uB79C\uB4DC \uBCC0\uACBD",
    "admin.btn.docs": "\uC0C1\uC138 \uC124\uC815 \uBB38\uC11C",
    "admin.creds.title": "\uC778\uC99D \uC815\uBCF4",
    "admin.creds.hint": "\uC548\uC804\uD558\uAC8C \uC800\uC7A5 \u2014 \uAC8C\uC2DC\uBB3C \uD655\uC778\uC5D0 \uC0AC\uC6A9",
    "presenter.title": "Pearl Prime \uD504\uB808\uC820\uD130",
    "presenter.subtitle": "\uB371\uC744 \uC120\uD0DD\uD558\uC5EC \uC2DC\uC791",
    "presenter.deck.intro": "Pearl Prime \uC18C\uAC1C",
    "presenter.deck.intro.desc": "\uBE0C\uB79C\uB4DC \uAD00\uB9AC \uC628\uBCF4\uB529. \uC218\uC775, \uC544\uD0A4\uD14D\uCC98, \uC8FC\uAC04 OS.",
    "presenter.deck.marketing": "\uB9C8\uCF00\uD305 \uC778\uD154\uB9AC\uC804\uC2A4",
    "presenter.deck.marketing.desc": "13\uAC1C \uC2DC\uC7A5, \uAD11\uACE0 ROI, \uCF58\uD150\uCE20 \uAC10\uC0AC, \uD50C\uB9BF \uC804\uAC1C.",
    "presenter.deck.us": "\uBBF8\uAD6D \uBE0C\uB9AC\uD551",
    "presenter.deck.us.desc": "\uD50C\uB7AB\uD3FC, \uC5C5\uB85C\uB4DC \uAC00\uC774\uB4DC, \uC218\uC775 \uC608\uCE21.",
    "presenter.deck.jp": "\uC77C\uBCF8 \uBE0C\uB9AC\uD551",
    "presenter.deck.jp.desc": "\uB9CC\uD654, audiobook.jp, LINE, Piccoma, \uC77C\uBCF8 \uC804\uC6A9.",
    "presenter.deck.kr": "\uD55C\uAD6D \uBE0C\uB9AC\uD551",
    "presenter.deck.kr.desc": "Naver, Kakao, \uBC00\uB9AC\uC758 \uC11C\uC7AC, \uD55C\uAD6D \uC804\uC6A9.",
    "presenter.status.ready": "\uC900\uBE44 \uC644\uB8CC \u2014 \u25B6 \uB20C\uB7EC \uC7AC\uC0DD",
    "presenter.btn.back": "\uB371 \uBAA9\uB85D\uC73C\uB85C \uB3CC\uC544\uAC00\uAE30",
    "dashboard.logo": "Pearl Prime",
    "dashboard.subtitle": "\uB9C8\uCF00\uD305 \uC778\uD154\uB9AC\uC804\uC2A4 \uB300\uC2DC\uBCF4\uB4DC",
    "dashboard.tab.sim": "\uAD11\uACE0\uBE44 \uC2DC\uBBAC\uB808\uC774\uD130",
    "dashboard.tab.heatmap": "\uCF58\uD150\uCE20 \uD788\uD2B8\uB9F5",
    "dashboard.tab.lanes": "\uB808\uC778 \uBE44\uAD50",
    "dashboard.tab.funnel": "\uAC00\uCE58 \uC0AC\uB2E4\uB9AC",
    "dashboard.tab.fleet": "\uD50C\uB9BF \uD50C\uB798\uB108",
    "dashboard.label.budget": "\uC6D4 \uC608\uC0B0",
    "dashboard.label.platform": "\uD50C\uB7AB\uD3FC",
    "dashboard.label.lane": "\uB808\uC778",
    "dashboard.roas": "ROAS \uACE1\uC120",
    "dashboard.revenue.vs.spend": "\uC218\uC775 vs \uC9C0\uCD9C",
    "dashboard.heatmap.title": "\uCF58\uD150\uCE20 \uC131\uACFC \uD788\uD2B8\uB9F5",
    "dashboard.lane.revenue": "\uB808\uC778\uBCC4 1\uB144\uCC28 \uC608\uC0C1 \uC218\uC775",
    "dashboard.lane.competition": "\uACBD\uC7C1 vs \uAE30\uD68C",
    "dashboard.greenfield": "\uADF8\uB9B0\uD544\uB4DC \uAE30\uD68C \uD50C\uB798\uADF8",
    "dashboard.funnel.title": "\uAC00\uCE58 \uC0AC\uB2E4\uB9AC \uD37C\uB110",
    "dashboard.ltv": "LTV \uACC4\uC0B0",
    "dashboard.fleet.title": "\uD50C\uB9BF \uC608\uC0B0 \uD50C\uB798\uB108",
    "dashboard.fleet.budget": "\uC6D4\uAC04 \uD50C\uB9BF \uCD1D \uC608\uC0B0",
    "dashboard.fleet.timeline": "\uB2E8\uACC4 \uD0C0\uC784\uB77C\uC778",
    "dashboard.fleet.allocation": "\uC608\uC0B0 \uBC30\uBD84",
    "dashboard.fleet.tiers": "\uBE0C\uB79C\uB4DC \uD2F0\uC5B4 \uBA85\uC138",
    "dashboard.btn.close": "\uB2EB\uAE30",
    "matrix.title": "\uB9C8\uCF13 \u00D7 \uB808\uC778 \uB9E4\uD2B8\uB9AD\uC2A4",
    "matrix.desc": "\uC758\uC0AC\uACB0\uC815 \uC11C\uD53C\uC2A4: \uC2DC\uC7A5\uACFC \uB808\uC778\uBCC4 \uD604\uD669, \uC99D\uAC70 \uACB0\uD578, \uBE44\uAD50 \uC138\uD2B8.",
    "matrix.marketing.desc": "\uD328\uD0A4\uC9D5 \uC608\uC0B0 \uD22C\uC785 \uC804\uC5D0 \uC774 \uD45C\uB97C \uC0AC\uC6A9\uD558\uC138\uC694.",
    "matrix.nav.hub": "\uD5C8\uBE0C",
    "matrix.nav.wizard": "\uB77C\uC774\uBE0C \uC704\uC800\uB4DC",
    "matrix.nav.gallery": "\uC608\uC2DC \uAC24\uB7EC\uB9AC",
    "matrix.nav.onboarding": "\uB9C8\uC2A4\uD130 \uC628\uBCF4\uB529",
    "matrix.nav.weekly": "\uC8FC\uAC04 OS",
    "common.back": "\uB4A4\uB85C",
    "common.next": "\uB2E4\uC74C",
    "common.close": "\uB2EB\uAE30",
    "common.copy": "\uBCF5\uC0AC",
    "common.done": "\uC644\uB8CC",
    "common.loading": "\uB85C\uB529 \uC911\u2026",
    "picker.lang": "\uC5B8\uC5B4"
  };

  // ─── fr-FR ──────────────────────────────────────────
  I18N["fr-FR"] = {
    "nav.brand": "Pearl Prime",
    "nav.markets": "March\u00E9s",
    "nav.teachers": "Enseignants",
    "nav.showcase": "Vitrine",
    "nav.intro": "Intro",
    "nav.marketing": "Marketing",
    "nav.dashboard": "Tableau de bord",
    "nav.matrix": "Matrice",
    "nav.gallery": "Galerie",
    "nav.admin": "Admin Marque",
    "entry.title": "Pearl Prime",
    "entry.subtitle": "Choisissez votre march\u00E9",
    "entry.learn": "En savoir plus",
    "entry.learn.desc": "Montrez-moi comment \u00E7a fonctionne",
    "entry.start": "Commencer",
    "entry.start.desc": "Je suis pr\u00EAt",
    "entry.back.market": "Changer de march\u00E9",
    "entry.back": "Retour",
    "entry.onboarding": "Int\u00E9gration de marque",
    "entry.onboarding.desc": "Configurer ma marque pour la premi\u00E8re fois",
    "entry.operations": "Op\u00E9rations de marque",
    "entry.operations.desc": "Faire mes t\u00E9l\u00E9chargements hebdomadaires",
    "teacher.sidebar.title": "Enseignants",
    "teacher.samples.heading": "Pearl News \u2014 Exemples d'enseignement",
    "teacher.stat.atoms": "Atomes",
    "teacher.stat.types": "Types",
    "teacher.stat.topics": "Sujets",
    "teacher.stat.news": "Articles",
    "teacher.audio.label": "Narration audio \u2014 le propri\u00E9taire fournira les MP3",
    "teacher.btn.briefing": "Briefing",
    "teacher.btn.profile": "Profil complet",
    "showcase.sidebar.title": "Pearl Prime",
    "showcase.sidebar.sub": "13 ENSEIGNANTS / 13 MARQUES",
    "admin.title": "Admin Marque",
    "admin.phase.overview": "Aper\u00E7u",
    "admin.phase.setup": "Configuration",
    "admin.phase.upload": "T\u00E9l\u00E9chargement",
    "admin.phase.weekly": "Hebdomadaire",
    "admin.phase.label.overview": "Aper\u00E7u",
    "admin.phase.label.setup": "Configuration",
    "admin.phase.label.upload": "Premier t\u00E9l\u00E9chargement",
    "admin.phase.label.weekly": "Rythme hebdomadaire",
    "admin.progress": "termin\u00E9",
    "admin.celebration.title": "Phase termin\u00E9e",
    "admin.celebration.sub": "Phase suivante d\u00E9verrouill\u00E9e.",
    "admin.celebration.btn": "Continuer",
    "admin.links.title": "Liens rapides des plateformes",
    "admin.btn.change": "Changer de marque",
    "admin.btn.docs": "Documentation d\u00E9taill\u00E9e",
    "admin.creds.title": "Vos identifiants",
    "admin.creds.hint": "sauvegard\u00E9s en s\u00E9curit\u00E9 \u2014 utilis\u00E9s pour v\u00E9rifier vos publications",
    "presenter.title": "Pr\u00E9sentateur Pearl Prime",
    "presenter.subtitle": "S\u00E9lectionnez un deck pour commencer",
    "presenter.deck.intro": "Intro Pearl Prime",
    "presenter.deck.intro.desc": "Int\u00E9gration admin marque. Revenus, architecture, OS hebdo.",
    "presenter.deck.marketing": "Intelligence Marketing",
    "presenter.deck.marketing.desc": "13 march\u00E9s, ROI pub, audit contenu, d\u00E9ploiement flotte.",
    "presenter.deck.us": "Briefing US",
    "presenter.deck.us.desc": "Stack plateformes, guide upload, projections revenus.",
    "presenter.deck.jp": "Briefing Japon",
    "presenter.deck.jp.desc": "Manga, audiobook.jp, LINE, Piccoma, sp\u00E9cifique Japon.",
    "presenter.deck.kr": "Briefing Cor\u00E9e",
    "presenter.deck.kr.desc": "Naver, Kakao, Millie's Library, sp\u00E9cifique Cor\u00E9e.",
    "presenter.status.ready": "Pr\u00EAt \u2014 appuyez sur \u25B6 Lecture",
    "presenter.btn.back": "Retour aux decks",
    "dashboard.logo": "Pearl Prime",
    "dashboard.subtitle": "Tableau de bord Marketing Intelligence",
    "dashboard.tab.sim": "Simulateur de d\u00E9penses pub",
    "dashboard.tab.heatmap": "Carte thermique contenu",
    "dashboard.tab.lanes": "Comparaison de lanes",
    "dashboard.tab.funnel": "\u00C9chelle de valeur",
    "dashboard.tab.fleet": "Planificateur de flotte",
    "dashboard.label.budget": "Budget mensuel",
    "dashboard.label.platform": "Plateforme",
    "dashboard.label.lane": "Lane",
    "dashboard.roas": "Courbe ROAS",
    "dashboard.revenue.vs.spend": "Revenus vs D\u00E9penses",
    "dashboard.heatmap.title": "Carte thermique de performance du contenu",
    "dashboard.lane.revenue": "Revenus estim\u00E9s an 1 par lane",
    "dashboard.lane.competition": "Concurrence vs Opportunit\u00E9",
    "dashboard.greenfield": "Indicateurs d'opportunit\u00E9 vierge",
    "dashboard.funnel.title": "Entonnoir de valeur",
    "dashboard.ltv": "Calcul LTV",
    "dashboard.fleet.title": "Planificateur budget flotte",
    "dashboard.fleet.budget": "Budget mensuel total flotte",
    "dashboard.fleet.timeline": "Calendrier des phases",
    "dashboard.fleet.allocation": "R\u00E9partition du budget",
    "dashboard.fleet.tiers": "D\u00E9tail par niveau de marque",
    "dashboard.btn.close": "Fermer",
    "matrix.title": "Matrice March\u00E9 \u00D7 Lane",
    "matrix.desc": "Surface de d\u00E9cision : ce qui existe par march\u00E9 et lane, preuves manquantes, ensembles de comparaison.",
    "matrix.marketing.desc": "Utilisez ce tableau avant d'engager un budget packaging.",
    "matrix.nav.hub": "Hub",
    "matrix.nav.wizard": "Assistant en direct",
    "matrix.nav.gallery": "Galerie d'exemples",
    "matrix.nav.onboarding": "Int\u00E9gration principale",
    "matrix.nav.weekly": "OS hebdomadaire",
    "common.back": "Retour",
    "common.next": "Suivant",
    "common.close": "Fermer",
    "common.copy": "Copier",
    "common.done": "Termin\u00E9",
    "common.loading": "Chargement\u2026",
    "picker.lang": "Langue"
  };

  // ─── de-DE ──────────────────────────────────────────
  I18N["de-DE"] = {
    "nav.brand": "Pearl Prime",
    "nav.markets": "M\u00E4rkte",
    "nav.teachers": "Lehrer",
    "nav.showcase": "Showcase",
    "nav.intro": "Einf\u00FChrung",
    "nav.marketing": "Marketing",
    "nav.dashboard": "Dashboard",
    "nav.matrix": "Matrix",
    "nav.gallery": "Galerie",
    "nav.admin": "Marken-Admin",
    "entry.title": "Pearl Prime",
    "entry.subtitle": "W\u00E4hlen Sie Ihren Markt",
    "entry.learn": "Mehr erfahren",
    "entry.learn.desc": "Zeigen Sie mir, wie es funktioniert",
    "entry.start": "Arbeit beginnen",
    "entry.start.desc": "Ich bin bereit",
    "entry.back.market": "Markt wechseln",
    "entry.back": "Zur\u00FCck",
    "entry.onboarding": "Marken-Onboarding",
    "entry.onboarding.desc": "Meine Marke erstmalig einrichten",
    "entry.operations": "Markenbetrieb",
    "entry.operations.desc": "Meine w\u00F6chentlichen Uploads durchf\u00FChren",
    "teacher.sidebar.title": "Lehrer",
    "teacher.samples.heading": "Pearl News \u2014 Lehrbeispiele",
    "teacher.stat.atoms": "Atome",
    "teacher.stat.types": "Typen",
    "teacher.stat.topics": "Themen",
    "teacher.stat.news": "Nachrichtenartikel",
    "teacher.audio.label": "Audio-Erz\u00E4hlung \u2014 Eigent\u00FCmer stellt MP3-Beispiele bereit",
    "teacher.btn.briefing": "Briefing",
    "teacher.btn.profile": "Vollst\u00E4ndiges Profil",
    "showcase.sidebar.title": "Pearl Prime",
    "showcase.sidebar.sub": "13 LEHRER / 13 MARKEN",
    "admin.title": "Marken-Admin",
    "admin.phase.overview": "\u00DCbersicht",
    "admin.phase.setup": "Einrichtung",
    "admin.phase.upload": "Upload",
    "admin.phase.weekly": "W\u00F6chentlich",
    "admin.phase.label.overview": "\u00DCbersicht",
    "admin.phase.label.setup": "Einrichtung",
    "admin.phase.label.upload": "Erster Upload",
    "admin.phase.label.weekly": "Wochenrhythmus",
    "admin.progress": "abgeschlossen",
    "admin.celebration.title": "Phase abgeschlossen",
    "admin.celebration.sub": "N\u00E4chste Phase freigeschaltet.",
    "admin.celebration.btn": "Weiter",
    "admin.links.title": "Schnelle Plattform-Links",
    "admin.btn.change": "Marke wechseln",
    "admin.btn.docs": "Detaillierte Setup-Dokumentation",
    "admin.creds.title": "Ihre Zugangsdaten",
    "admin.creds.hint": "sicher gespeichert \u2014 zur Verifizierung Ihrer Beitr\u00E4ge",
    "presenter.title": "Pearl Prime Presenter",
    "presenter.subtitle": "W\u00E4hlen Sie ein Deck zum Starten",
    "presenter.deck.intro": "Pearl Prime Einf\u00FChrung",
    "presenter.deck.intro.desc": "Marken-Admin Onboarding. Umsatz, Architektur, Wochen-OS.",
    "presenter.deck.marketing": "Marketing-Intelligenz",
    "presenter.deck.marketing.desc": "13 M\u00E4rkte, Werbe-ROI, Content-Audit, Flotten-Rollout.",
    "presenter.deck.us": "US-Briefing",
    "presenter.deck.us.desc": "Plattform-Stack, Upload-Leitfaden, Umsatzprognosen.",
    "presenter.deck.jp": "Japan-Briefing",
    "presenter.deck.jp.desc": "Manga, audiobook.jp, LINE, Piccoma, Japan-spezifisch.",
    "presenter.deck.kr": "Korea-Briefing",
    "presenter.deck.kr.desc": "Naver, Kakao, Millie's Library, Korea-spezifisch.",
    "presenter.status.ready": "Bereit \u2014 dr\u00FCcken Sie \u25B6 Abspielen",
    "presenter.btn.back": "Zur\u00FCck zu Decks",
    "dashboard.logo": "Pearl Prime",
    "dashboard.subtitle": "Marketing-Intelligenz-Dashboard",
    "dashboard.tab.sim": "Werbeausgaben-Simulator",
    "dashboard.tab.heatmap": "Content-Heatmap",
    "dashboard.tab.lanes": "Lane-Vergleich",
    "dashboard.tab.funnel": "Wertleiter",
    "dashboard.tab.fleet": "Flottenplaner",
    "dashboard.label.budget": "Monatsbudget",
    "dashboard.label.platform": "Plattform",
    "dashboard.label.lane": "Lane",
    "dashboard.roas": "ROAS-Kurve",
    "dashboard.revenue.vs.spend": "Umsatz vs Ausgaben",
    "dashboard.heatmap.title": "Content-Performance-Heatmap",
    "dashboard.lane.revenue": "Gesch\u00E4tzter Jahresumsatz nach Lane",
    "dashboard.lane.competition": "Wettbewerb vs Chance",
    "dashboard.greenfield": "Greenfield-Chance-Flags",
    "dashboard.funnel.title": "Wertleiter-Trichter",
    "dashboard.ltv": "LTV-Berechnung",
    "dashboard.fleet.title": "Flotten-Budgetplaner",
    "dashboard.fleet.budget": "Monatliches Gesamtflottenbudget",
    "dashboard.fleet.timeline": "Phasen-Zeitplan",
    "dashboard.fleet.allocation": "Budgetverteilung",
    "dashboard.fleet.tiers": "Marken-Tier-Aufschl\u00FCsselung",
    "dashboard.btn.close": "Schlie\u00DFen",
    "matrix.title": "Markt \u00D7 Lane Matrix",
    "matrix.desc": "Entscheidungsfl\u00E4che: was pro Markt und Lane existiert, fehlende Nachweise, Vergleichssets.",
    "matrix.marketing.desc": "Verwenden Sie diese Tabelle vor der Budgetvergabe.",
    "matrix.nav.hub": "Hub",
    "matrix.nav.wizard": "Live-Assistent",
    "matrix.nav.gallery": "Beispielgalerie",
    "matrix.nav.onboarding": "Master-Onboarding",
    "matrix.nav.weekly": "Wochen-OS",
    "common.back": "Zur\u00FCck",
    "common.next": "Weiter",
    "common.close": "Schlie\u00DFen",
    "common.copy": "Kopieren",
    "common.done": "Fertig",
    "common.loading": "Laden\u2026",
    "picker.lang": "Sprache"
  };

  // ─── hu-HU (nav + CTAs, others fallback to en-US) ──
  I18N["hu-HU"] = {
    "nav.brand": "Pearl Prime",
    "nav.markets": "Piacok",
    "nav.teachers": "Tan\u00EDt\u00F3k",
    "nav.showcase": "Bemutat\u00F3",
    "nav.intro": "Bevezet\u00E9s",
    "nav.marketing": "Marketing",
    "nav.dashboard": "Ir\u00E1ny\u00EDt\u00F3pult",
    "nav.matrix": "M\u00E1trix",
    "nav.gallery": "Gal\u00E9ria",
    "nav.admin": "M\u00E1rka Admin",
    "entry.subtitle": "V\u00E1lassza ki a piac\u00E1t",
    "entry.learn": "Tudj meg t\u00F6bbet",
    "entry.start": "Munka megkezd\u00E9se",
    "entry.back.market": "Piac v\u00E1lt\u00E1sa",
    "entry.back": "Vissza",
    "entry.onboarding": "M\u00E1rka bevezet\u00E9s",
    "entry.operations": "M\u00E1rka \u00FCzemeltet\u00E9s",
    "admin.title": "M\u00E1rka Admin",
    "admin.phase.overview": "\u00C1ttekint\u00E9s",
    "admin.phase.setup": "Be\u00E1ll\u00EDt\u00E1s",
    "admin.phase.upload": "Felt\u00F6lt\u00E9s",
    "admin.phase.weekly": "Heti",
    "admin.celebration.btn": "Folytat\u00E1s",
    "common.back": "Vissza",
    "common.next": "K\u00F6vetkez\u0151",
    "common.close": "Bez\u00E1r\u00E1s",
    "common.copy": "M\u00E1sol\u00E1s",
    "common.done": "K\u00E9sz",
    "picker.lang": "Nyelv"
  };

  // ─── id-ID (nav + CTAs) ─────────────────────────────
  I18N["id-ID"] = {
    "nav.brand": "Pearl Prime",
    "nav.markets": "Pasar",
    "nav.teachers": "Guru",
    "nav.showcase": "Pameran",
    "nav.intro": "Pengantar",
    "nav.marketing": "Pemasaran",
    "nav.dashboard": "Dasbor",
    "nav.matrix": "Matriks",
    "nav.gallery": "Galeri",
    "nav.admin": "Admin Merek",
    "entry.subtitle": "Pilih Pasar Anda",
    "entry.learn": "Pelajari Lebih Lanjut",
    "entry.start": "Mulai Bekerja",
    "entry.back.market": "Ganti Pasar",
    "entry.back": "Kembali",
    "entry.onboarding": "Onboarding Merek",
    "entry.operations": "Operasi Merek",
    "admin.title": "Admin Merek",
    "admin.phase.overview": "Ringkasan",
    "admin.phase.setup": "Pengaturan",
    "admin.phase.upload": "Unggah",
    "admin.phase.weekly": "Mingguan",
    "admin.celebration.btn": "Lanjutkan",
    "common.back": "Kembali",
    "common.next": "Berikutnya",
    "common.close": "Tutup",
    "common.copy": "Salin",
    "common.done": "Selesai",
    "picker.lang": "Bahasa"
  };

  // ─── th-TH (nav + CTAs) ─────────────────────────────
  I18N["th-TH"] = {
    "nav.brand": "Pearl Prime",
    "nav.markets": "\u0E15\u0E25\u0E32\u0E14",
    "nav.teachers": "\u0E04\u0E23\u0E39",
    "nav.showcase": "\u0E42\u0E0A\u0E27\u0E4C\u0E40\u0E04\u0E2A",
    "nav.intro": "\u0E41\u0E19\u0E30\u0E19\u0E33",
    "nav.marketing": "\u0E01\u0E32\u0E23\u0E15\u0E25\u0E32\u0E14",
    "nav.dashboard": "\u0E41\u0E14\u0E0A\u0E1A\u0E2D\u0E23\u0E4C\u0E14",
    "nav.matrix": "\u0E40\u0E21\u0E17\u0E23\u0E34\u0E01\u0E0B\u0E4C",
    "nav.gallery": "\u0E41\u0E01\u0E25\u0E40\u0E25\u0E2D\u0E23\u0E35",
    "nav.admin": "\u0E41\u0E2D\u0E14\u0E21\u0E34\u0E19\u0E41\u0E1A\u0E23\u0E19\u0E14\u0E4C",
    "entry.subtitle": "\u0E40\u0E25\u0E37\u0E2D\u0E01\u0E15\u0E25\u0E32\u0E14\u0E02\u0E2D\u0E07\u0E04\u0E38\u0E13",
    "entry.learn": "\u0E40\u0E23\u0E35\u0E22\u0E19\u0E23\u0E39\u0E49\u0E40\u0E1E\u0E34\u0E48\u0E21\u0E40\u0E15\u0E34\u0E21",
    "entry.start": "\u0E40\u0E23\u0E34\u0E48\u0E21\u0E17\u0E33\u0E07\u0E32\u0E19",
    "entry.back.market": "\u0E40\u0E1B\u0E25\u0E35\u0E48\u0E22\u0E19\u0E15\u0E25\u0E32\u0E14",
    "entry.back": "\u0E01\u0E25\u0E31\u0E1A",
    "entry.onboarding": "\u0E40\u0E23\u0E34\u0E48\u0E21\u0E15\u0E49\u0E19\u0E41\u0E1A\u0E23\u0E19\u0E14\u0E4C",
    "entry.operations": "\u0E14\u0E33\u0E40\u0E19\u0E34\u0E19\u0E07\u0E32\u0E19\u0E41\u0E1A\u0E23\u0E19\u0E14\u0E4C",
    "admin.title": "\u0E41\u0E2D\u0E14\u0E21\u0E34\u0E19\u0E41\u0E1A\u0E23\u0E19\u0E14\u0E4C",
    "admin.celebration.btn": "\u0E14\u0E33\u0E40\u0E19\u0E34\u0E19\u0E01\u0E32\u0E23\u0E15\u0E48\u0E2D",
    "common.back": "\u0E01\u0E25\u0E31\u0E1A",
    "common.next": "\u0E16\u0E31\u0E14\u0E44\u0E1B",
    "common.close": "\u0E1B\u0E34\u0E14",
    "common.copy": "\u0E04\u0E31\u0E14\u0E25\u0E2D\u0E01",
    "common.done": "\u0E40\u0E2A\u0E23\u0E47\u0E08",
    "picker.lang": "\u0E20\u0E32\u0E29\u0E32"
  };

  // ─── vi-VN (nav + CTAs) ─────────────────────────────
  I18N["vi-VN"] = {
    "nav.brand": "Pearl Prime",
    "nav.markets": "Th\u1ECB tr\u01B0\u1EDDng",
    "nav.teachers": "Gi\u00E1o vi\u00EAn",
    "nav.showcase": "Tr\u01B0ng b\u00E0y",
    "nav.intro": "Gi\u1EDBi thi\u1EC7u",
    "nav.marketing": "Ti\u1EBFp th\u1ECB",
    "nav.dashboard": "B\u1EA3ng \u0111i\u1EC1u khi\u1EC3n",
    "nav.matrix": "Ma tr\u1EADn",
    "nav.gallery": "Th\u01B0 vi\u1EC7n",
    "nav.admin": "Qu\u1EA3n l\u00FD th\u01B0\u01A1ng hi\u1EC7u",
    "entry.subtitle": "Ch\u1ECDn th\u1ECB tr\u01B0\u1EDDng c\u1EE7a b\u1EA1n",
    "entry.learn": "T\u00ECm hi\u1EC3u th\u00EAm",
    "entry.start": "B\u1EAFt \u0111\u1EA7u l\u00E0m vi\u1EC7c",
    "entry.back.market": "\u0110\u1ED5i th\u1ECB tr\u01B0\u1EDDng",
    "entry.back": "Quay l\u1EA1i",
    "entry.onboarding": "Kh\u1EDFi t\u1EA1o th\u01B0\u01A1ng hi\u1EC7u",
    "entry.operations": "V\u1EADn h\u00E0nh th\u01B0\u01A1ng hi\u1EC7u",
    "admin.title": "Qu\u1EA3n l\u00FD th\u01B0\u01A1ng hi\u1EC7u",
    "admin.celebration.btn": "Ti\u1EBFp t\u1EE5c",
    "common.back": "Quay l\u1EA1i",
    "common.next": "Ti\u1EBFp theo",
    "common.close": "\u0110\u00F3ng",
    "common.copy": "Sao ch\u00E9p",
    "common.done": "Xong",
    "picker.lang": "Ng\u00F4n ng\u1EEF"
  };

  // ─── pt-BR (nav + CTAs) ─────────────────────────────
  I18N["pt-BR"] = {
    "nav.brand": "Pearl Prime",
    "nav.markets": "Mercados",
    "nav.teachers": "Professores",
    "nav.showcase": "Vitrine",
    "nav.intro": "Introdu\u00E7\u00E3o",
    "nav.marketing": "Marketing",
    "nav.dashboard": "Painel",
    "nav.matrix": "Matriz",
    "nav.gallery": "Galeria",
    "nav.admin": "Admin da Marca",
    "entry.subtitle": "Escolha seu mercado",
    "entry.learn": "Saiba mais",
    "entry.start": "Come\u00E7ar a trabalhar",
    "entry.back.market": "Mudar mercado",
    "entry.back": "Voltar",
    "entry.onboarding": "Onboarding da marca",
    "entry.operations": "Opera\u00E7\u00F5es da marca",
    "admin.title": "Admin da Marca",
    "admin.celebration.btn": "Continuar",
    "common.back": "Voltar",
    "common.next": "Pr\u00F3ximo",
    "common.close": "Fechar",
    "common.copy": "Copiar",
    "common.done": "Conclu\u00EDdo",
    "picker.lang": "Idioma"
  };

  // ─── es-MX (nav + CTAs) ─────────────────────────────
  I18N["es-MX"] = {
    "nav.brand": "Pearl Prime",
    "nav.markets": "Mercados",
    "nav.teachers": "Maestros",
    "nav.showcase": "Escaparate",
    "nav.intro": "Introducci\u00F3n",
    "nav.marketing": "Marketing",
    "nav.dashboard": "Panel",
    "nav.matrix": "Matriz",
    "nav.gallery": "Galer\u00EDa",
    "nav.admin": "Admin de Marca",
    "entry.subtitle": "Elige tu mercado",
    "entry.learn": "Conocer m\u00E1s",
    "entry.start": "Empezar a trabajar",
    "entry.back.market": "Cambiar mercado",
    "entry.back": "Atr\u00E1s",
    "entry.onboarding": "Incorporaci\u00F3n de marca",
    "entry.operations": "Operaciones de marca",
    "admin.title": "Admin de Marca",
    "admin.celebration.btn": "Continuar",
    "common.back": "Atr\u00E1s",
    "common.next": "Siguiente",
    "common.close": "Cerrar",
    "common.copy": "Copiar",
    "common.done": "Hecho",
    "picker.lang": "Idioma"
  };

  /* ══════════════════════════════════════════════════════
     LOCALE MATCHING
     ══════════════════════════════════════════════════════ */
  var LANE_TO_LOCALE = {
    en_US:"en-US", ja_JP:"ja-JP", zh_TW:"zh-TW", zh_CN:"zh-CN", ko_KR:"ko-KR",
    fr_FR:"fr-FR", de_DE:"de-DE", hu_HU:"hu-HU", id_ID:"id-ID", th_TH:"th-TH",
    vi_VN:"vi-VN", pt_BR:"pt-BR", es_MX:"es-MX",
    zh_HK:"zh-TW", zh_SG:"zh-CN", es_US:"es-MX", es_ES:"es-MX", it_IT:"en-US"
  };

  function matchLocale(raw) {
    if (!raw) return "en-US";
    // Exact match
    var norm = raw.replace(/_/g, "-");
    if (I18N[norm]) return norm;
    // Try common mappings
    var map = {
      "ja":"ja-JP","ko":"ko-KR","fr":"fr-FR","de":"de-DE","hu":"hu-HU",
      "id":"id-ID","th":"th-TH","vi":"vi-VN","pt":"pt-BR","es":"es-MX",
      "zh-Hant":"zh-TW","zh-Hans":"zh-CN","zh-TW":"zh-TW","zh-CN":"zh-CN","zh":"zh-CN"
    };
    // Check prefix matches
    for (var k in map) {
      if (norm === k || norm.indexOf(k + "-") === 0) return map[k];
    }
    return "en-US";
  }

  /* ══════════════════════════════════════════════════════
     LANGUAGE DETECTION
     ══════════════════════════════════════════════════════ */
  function detectLanguage() {
    // 1. URL param ?lang=ja-JP
    var params = new URLSearchParams(location.search);
    if (params.has("lang")) return matchLocale(params.get("lang"));
    // 1b. Derive locale from the brand's lane suffix (?brand=..._ja_jp → ja-JP)
    if (params.has("brand")) {
      var bm = String(params.get("brand")).toLowerCase().match(/_([a-z]{2})_([a-z]{2})$/);
      if (bm) {
        var laneKey = bm[1] + "_" + bm[2].toUpperCase();
        if (LANE_TO_LOCALE[laneKey]) return LANE_TO_LOCALE[laneKey];
      }
    }
    // 2. localStorage (from lane picker)
    var lane = localStorage.getItem("phoenix_lane") || localStorage.getItem("pearl_prime_lane");
    if (lane && LANE_TO_LOCALE[lane]) return LANE_TO_LOCALE[lane];
    // 3. Saved i18n preference
    var saved = localStorage.getItem("pearl_prime_locale");
    if (saved && I18N[saved]) return saved;
    // 4. Browser language
    var nav = navigator.language || "en-US";
    return matchLocale(nav);
  }

  /* ══════════════════════════════════════════════════════
     TRANSLATION FUNCTIONS
     ══════════════════════════════════════════════════════ */
  var currentLocale = detectLanguage();

  function t(key) {
    var dict = I18N[currentLocale];
    if (dict && dict[key] != null) return dict[key];
    var fallback = I18N["en-US"];
    if (fallback && fallback[key] != null) return fallback[key];
    return key;
  }

  function applyTranslations(locale) {
    if (locale) currentLocale = locale;
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      var val = t(key);
      if (val && val !== key) el.textContent = val;
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
      var key = el.getAttribute("data-i18n-placeholder");
      var val = t(key);
      if (val && val !== key) el.setAttribute("placeholder", val);
    });
    document.querySelectorAll("[data-i18n-title]").forEach(function (el) {
      var key = el.getAttribute("data-i18n-title");
      var val = t(key);
      if (val && val !== key) el.setAttribute("title", val);
    });
    // Update html lang attribute
    document.documentElement.setAttribute("lang", currentLocale);
  }

  /* ══════════════════════════════════════════════════════
     LANGUAGE PICKER
     ══════════════════════════════════════════════════════ */
  var LOCALE_LABELS = {
    "en-US":"English","ja-JP":"\u65E5\u672C\u8A9E","zh-TW":"\u7E41\u9AD4\u4E2D\u6587",
    "zh-CN":"\u7B80\u4F53\u4E2D\u6587","ko-KR":"\uD55C\uAD6D\uC5B4","fr-FR":"Fran\u00E7ais",
    "de-DE":"Deutsch","hu-HU":"Magyar","id-ID":"Bahasa","th-TH":"\u0E44\u0E17\u0E22",
    "vi-VN":"Ti\u1EBFng Vi\u1EC7t","pt-BR":"Portugu\u00EAs","es-MX":"Espa\u00F1ol"
  };

  function createLanguagePicker() {
    var nav = document.querySelector("[data-nav='universal']");
    if (!nav) return;
    // Don't create if one already exists
    if (nav.querySelector(".i18n-picker")) return;

    var wrap = document.createElement("span");
    wrap.className = "i18n-picker";
    wrap.style.cssText = "margin-left:6px;display:inline-flex;align-items:center;flex-shrink:0";

    var sel = document.createElement("select");
    sel.style.cssText = [
      "font-family:'DM Mono',monospace",
      "font-size:.42rem",
      "letter-spacing:.04em",
      "background:rgba(180,83,9,.15)",
      "color:#d97706",
      "border:1px solid rgba(180,83,9,.25)",
      "border-radius:3px",
      "padding:2px 4px",
      "cursor:pointer",
      "outline:none",
      "-webkit-appearance:none",
      "appearance:none"
    ].join(";");

    SUPPORTED.forEach(function (loc) {
      var opt = document.createElement("option");
      opt.value = loc;
      opt.textContent = LOCALE_LABELS[loc] || loc;
      if (loc === currentLocale) opt.selected = true;
      sel.appendChild(opt);
    });

    sel.addEventListener("change", function () {
      currentLocale = sel.value;
      localStorage.setItem("pearl_prime_locale", currentLocale);
      applyTranslations();
    });

    wrap.appendChild(sel);
    nav.appendChild(wrap);
  }

  /* ══════════════════════════════════════════════════════
     AUTO-INIT
     ══════════════════════════════════════════════════════ */
  function translateTree(root) {
    if (!root || !root.querySelectorAll) return;
    root.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      var val = t(key);
      if (!val || val === key) return;
      var cur = (el.textContent || "").trim();
      var enVal = (I18N["en-US"] && I18N["en-US"][key]) || "";
      // Only translate static fallback text; never clobber interpolated/dynamic values.
      if (cur === "" || cur === key || cur === enVal || cur === val) el.textContent = val;
    });
  }

  function init() {
    applyTranslations();
    createLanguagePicker();
    // Re-translate [data-i18n] content rendered by JS after load (phase bodies, etc.)
    if (typeof MutationObserver !== "undefined" && document.body) {
      var scheduled = false;
      new MutationObserver(function () {
        if (scheduled) return;
        scheduled = true;
        var run = function () { scheduled = false; translateTree(document.body); };
        if (window.requestAnimationFrame) window.requestAnimationFrame(run); else setTimeout(run, 0);
      }).observe(document.body, { childList: true, subtree: true });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  /* ══════════════════════════════════════════════════════
     PUBLIC API (window.i18n)
     ══════════════════════════════════════════════════════ */
  window.i18n = {
    t: t,
    locale: function () { return currentLocale; },
    setLocale: function (loc) {
      currentLocale = matchLocale(loc);
      localStorage.setItem("pearl_prime_locale", currentLocale);
      applyTranslations();
      // Update picker if it exists
      var sel = document.querySelector(".i18n-picker select");
      if (sel) sel.value = currentLocale;
    },
    applyTranslations: applyTranslations,
    I18N: I18N,
    SUPPORTED: SUPPORTED
  };
})();
