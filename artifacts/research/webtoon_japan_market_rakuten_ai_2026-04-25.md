# Rakuten AI Chat Research — Japanese-Market WEBTOON Intel
## Date: 2026-04-25
## Method: Claude in Chrome plugin → ai.rakuten.co.jp (Fast Response mode, no login)
## Researcher: Pearl_Research (parallel agent to /tmp/webtoon_technical_reference.md)

**Status:** Rakuten AI Chat accessible without login. "Fast Response" mode used (default). Each query took ~20-40s. Submitted in Japanese only (per priority — Japanese yields better local-source coverage; English second-pass deferred to time budget). Rakuten AI cites source URLs inline (manga.line.me, piccoma.com, clipstudio.net, etc.).

**Time budget note:** Of the 20 questions, prioritized 11 per task brief (A1/A2/A4/B6/C9/C10/D12/D13/E14/F17/G19). Two screenshots saved to disk via tool ID references in this session (ss_8470c4z9r initial Rakuten AI homepage; ss_7359t16oh Q1 send confirmation).

---

### Q1. LINE Manga SMARTOON の縦スクロール作品の標準的なエピソード長さ・パネル数・画像幅は何ですか？参考になる公式仕様や数値があれば教えてください。
**English equivalent:** Standard SMARTOON episode length, panel count, image width on LINE Manga? Official specs?

**Rakuten AI Chat raw response (Japanese, verbatim, key sections):**
> 現時点で確認できるLINEマンガ系の公式に近い公開仕様としては、少なくとも LINEマンガ インディーズ の制作ガイドラインに、縦読み作品の画像仕様が明記されています。そこでは作品本体画像（縦読み）について、推奨サイズは横800px、必須条件は横400px以上・縦600px以上・横10000px以下・縦10000px以下、1枚あたり2MB以内、PNG/JPG、最大1000枚までとされています。解像度は72dpi以上、カラーモードはRGB推奨です。したがって、画像幅の標準値としては「800px」が最も確かな公開数値です。(🔗 manga.line.me)
>
> **結論**
> - 画像幅の標準: 横800px
> - 1画像の高さ上限: 縦10000px
> - 1話あたり画像枚数上限: 1000枚
> - 1枚あたり容量: 2MB以内
> - 形式: PNG/JPG
> - 解像度/色: 72dpi以上 / RGB推奨
>
> ただし、「標準的なエピソード長さ」「標準的なパネル数」は公式数値を見つけにくい。1話は1枚の超縦長画像でも、複数画像の連結でも運用可能です。…公式の固定パネル数は見当たらないです。…縦読み漫画の一般的な作り方解説でも、スマホ画面に1〜2コマ程度を意識し、3コマ以上は小さくなりやすいと説明されています。(🔗 clipstudio.net) (🔗 raon-terastorys.com)
>
> **実務上の「標準的」な目安:** 幅800pxで納品・書き出し / 1セグメント800×1280px前後で区切る / 短編で数分、標準話で2〜5分程度の読了感 / パネル数20〜50コマ前後

**English translation of response:** Closest-to-official public specs come from LINE Manga Indies creator guidelines. For vertical-read body images: recommended **800px wide**, required min 400×600 px, max 10000×10000 px, ≤2MB each, **PNG/JPG**, max 1000 images per episode, ≥72dpi, **RGB recommended**. Standard image width = 800px (most reliable public number). Episode length and panel count are NOT officially fixed by LINE Manga; technical max is 1000×10000px images. Industry rule of thumb (not LINE Manga official): 1-2 panels per smartphone screen, ~20-50 panels per episode, 2-5 minute read.

**Cross-check source:** https://manga.line.me (LINE Manga Indies guideline page — Rakuten AI cites repeatedly). Also clipstudio.net, raon-terastorys.com, webtoons.com.
**Confidence:** high (for the 800px / 10000px / 1000 image / 2MB / PNG-JPG / 72dpi / RGB numbers — all sourced to LINE Manga Indies guideline). medium (for the "20-50 panels" rule of thumb — explicitly flagged as industry general, not LINE official).
**Notes for Phoenix engineers:** **The "Indies" guideline is the only public LINE Manga document with hard image specs.** Phoenix should use 800×N (where N ≤ 10000) PNG/JPG, sRGB, ≤2MB, max 1000 segments. SMARTOON's pro-tier (non-Indies) specs are NOT public — confirms the WEBTOON technical reference's gap.

---

### Q4. LINEマンガインディーズ（LINE Manga Indies）で個人作家が縦スクロール作品をアップロードする手順と画像仕様を、公式ページを引用して詳しく教えてください。収益化・ロイヤリティ・審査規定も包含してください。
**English equivalent:** LINE Manga Indies upload workflow + image specs for individual creators? Include monetization, royalty, review rules.

**Rakuten AI Chat raw response (Japanese, verbatim, key extracts):**
> 結論からいうと、縦スクロール作品は公式に対応しており、PCまたはタブレットから作家登録→作品登録→各話アップロード→運営確認後に公開という流れです。
>
> **1. 投稿要件:** LINEアカウント＋メール認証で誰でも投稿可。"LINEマンガ インディーズからの応募は、PCまたはタブレットからのみ可能です。スマートフォンからの応募はできません。"(🔗 manga.line.me)
>
> **2. 手順:** 作家登録 → 作品登録（縦読み/横読み選択）→ 各話アップロード（D&D）→ プレビュー → "運営チームにて投稿ガイドラインに即しているか内容を確認後、公開" (🔗 line-ja.officialblog.jp)
>
> **3. 縦スク画像仕様 (公式表):** PNG or JPG / 推奨横800px / 必須横400px以上・縦600px以上・横10000px以下・縦10000px以下 / 1枚あたり2MB以内 / 1000枚まで / 72dpi以上 / RGB推奨。表紙(横長)348×220px必須、表紙(縦長)240×348px必須、各500KB以内。(🔗 manga.line.me)
>
> **5. 審査:** 違反時"公開を行わず、公開停止または削除し、もしくは利用停止させる場合がある"。2024年改定でジャンル不一致は運営が予告なく変更、再変更すると公開停止リスク。
>
> **5-3. 利用規約:** "投稿コンテンツに関する権利は、お客様に帰属し、当社がこれを取得することはありません" (LINEマンガ利用規約11.3)。ただし11.6で宣伝広告目的の広範な利用許諾と再許諾権を付与、11.12で著作者人格権不行使。(🔗 terms2.line.me)
>
> **6-3. 収益:** 通常投稿だけで自動的に広告収益や閲覧収益が分配される、という公式規約文は今回確認できませんでした。
>
> **報奨金給付プログラム:** 月2話以上+月間読者数・お気に入り登録数に応じて、通常で最大月10万円、**webtoon形式なら2倍で最大月20万円** (🔗 prtimes.jp) (🔗 itmedia.co.jp)
>
> **トライアル連載:** 12週間限定、"1ページ8,000円以上の原稿料"＋"課金売上、広告収益の分配金"。本連載に至らなかった場合は作品の全権利を返還。(🔗 prtimes.jp)
>
> **AI禁止条項:** 最近のテーマ投稿ミッション規約に "生成AIを使用して制作されたと当社が判断した作品（部分的使用含む）は応募対象外" と確認できます。(🔗 terms2.line.me)

**English translation of response:**
- Workflow: PC/tablet only → register author → register work (choose vertical/horizontal viewer) → upload episodes (drag-and-drop) → preview → submit for staff review → publish.
- Image specs (official table): PNG/JPG, recommended 800px wide, required 400×600 to 10000×10000 px, ≤2MB each, max 1000 per episode, ≥72dpi, RGB recommended.
- Cover required: 348×220px (landscape) AND 240×348px (portrait), ≤500KB.
- Rights: copyright stays with creator (Terms 11.3), but creator grants broad promo/sublicensing rights to LINE (11.6) and waives moral rights for those uses (11.12).
- Royalty: **No automatic royalty for regular uploads.** Monetization paths are: (a) reward program — up to ¥100K/month standard, **¥200K/month for webtoon-format** based on episode cadence, readership, favorites; (b) contests/grand prizes; (c) Trial Serialization — 12 weeks at ≥¥8000/page + share of paid sales + ad revenue. If trial doesn't progress to main serialization, all rights returned.
- **Critical: AI-generated works (including partial use) are excluded from theme-submission missions.** Not a blanket ban on regular uploads, but explicit AI exclusion clause exists in newer mission rules.

**Cross-check source:** manga.line.me (official guidelines), line-ja.officialblog.jp (creator onboarding), terms2.line.me (LINE Manga ToS), prtimes.jp (press release on reward program 2x for webtoon), itmedia.co.jp (independent coverage).
**Confidence:** high (specs, workflow, terms 11.3/11.6/11.12, reward program ¥100K/¥200K, trial ¥8000/page all sourced to LINE official or major JP press).
**Notes for Phoenix engineers:**
- **The ¥200K/mo webtoon-format reward (2x bonus vs traditional manga) is real and Phoenix-relevant.**
- **AI-generated works are NOT eligible for LINE Manga theme missions / contests** (per 2024-2025 mission ToS). Regular Indies uploads of AI work appear technically allowed but high risk of staff-review rejection — Phoenix Omega EI characters need clear human-author framing if uploading.
- Contracts: copyright stays with creator; LINE gets broad promo license. Trial serialization terms (¥8000/page+share) are the realistic bestseller path.

---

### Q2. ピッコマ(Piccoma)上の縦スクロール作品の画像仕様（幅・高さ・ファイル形式・容量、必要であればDPIやカラーモード）を、公式ガイドラインや作家向け資料があればそれを引用して教えてください。
**English equivalent:** Piccoma vertical-scroll image specs — width, height, file format, size? Cite official guidelines.

**Rakuten AI Chat raw response (Japanese, verbatim, key sections):**
> 調べた範囲では、ピッコマ（Piccoma）公式サイト上で一般公開されている「縦スクロール作品の画像仕様」を、幅・高さ・ファイル形式・容量・DPI・カラーモードまで明記した作家向けガイドラインとして確認することはできませんでした。
>
> **公式に確認できたこと:**
> - ピッコマには縦スクロール作品として SMARTOON があり、フルカラー・縦スクロール であることは公式・準公式情報で確認できます。
> - ピッコマ公式FAQ: 「SMARTOON（話読み）は全てタテ読みのみとなっており、ヨコ読みはできません。」 (🔗 piccoma.com)
> - ピッコマ関連インタビューでは、SMARTOONは「フルカラー、縦スクロールで読むのが特徴」 (🔗 clipstudio.net)
>
> **公式に確認できなかったこと:** 幅: 不明 / 高さ: 不明 / 1画像あたりの最大容量: 不明 / 対応ファイル形式: 不明 / 推奨DPI: 不明 / 推奨カラーモード: 不明 / 1話あたりの画像分割数上限: 不明 / 余白・セーフエリア・文字サイズなどの正式規定: 不明
>
> CLIP STUDIOのインタビュー記事では、ピッコミックス編集部の説明として、「持ち込み形式について特にこれといった決まりはありません。原作案の文章だけ送ってこられる人もいれば、企画書、ネームや作画サンプルなど、どんな形式であっても、全て見させていただいてます。」(🔗 clipstudio.net) とされており、少なくとも公開段階では、厳密な画像入稿規格を一般公開していない可能性があります。

**English translation of response:** **Piccoma does NOT publish image specs (width/height/format/DPI/color mode) for SMARTOON.** Only public confirmations: SMARTOON = vertical-only, full color (per piccoma.com FAQ + clipstudio.net interview with Piccomics editorial). For "持ち込み" (pitch submission), Piccomics editorial explicitly says "no specific format requirement — text outline, treatment, names, or sample art all accepted." Strict image specs likely shared only AFTER serialization/pitch acceptance via private "制作レギュレーション".

**Cross-check source:** https://piccoma.com FAQ (cited inline by Rakuten AI); https://www.clipstudio.net (Piccomics editorial interview).
**Confidence:** high (for the "specs are not public" finding — Rakuten AI was emphatic and explicitly refused to estimate).
**Notes for Phoenix engineers:** **Major gap vs LINE Manga.** Piccoma keeps creator specs private; you must apply via Piccomics submission to receive them. For Phoenix Omega's outbound pipeline, treat Piccoma specs as "unknown — assume LINE-compatible 800px PNG/JPG until contact established." Rakuten AI explicitly refused to fabricate numbers — strong signal.

---

