# Weekly brand publish packet automation
_Exported on 4/16/2026 at 19:38:53 GMT+8 from Cursor (3.1.15)_

---

**User**

@docs/DOCS_INDEX.md Use a **weekly publish packet** model: planner creates books, ops reviews advisories, then each brand gets a ready-to-upload bundle.

1. **Plan wave (Sun)**
- Run planner to generate weekly candidates with `program_id/worldview_id/concept_id` and series mix.
- Source: [teacher_portfolio_planner.py](/Users/ahjan/phoenix_omega/phoenix_v4/planning/teacher_portfolio_planner.py), [generate_full_catalog.py](/Users/ahjan/phoenix_omega/scripts/generate_full_catalog.py)

2. **Schedule by brand (Sun)**
- Build weekly schedule per brand (staggered days, no giant same-day spikes).
- Source: [generate_weekly_schedule.py](/Users/ahjan/phoenix_omega/scripts/release/generate_weekly_schedule.py), [release_scheduler.yaml](/Users/ahjan/phoenix_omega/config/release_velocity/release_scheduler.yaml)

3. **Assemble books (Mon/Tue)**
- Compile/render each scheduled title into final upload artifacts.
- Source: [run_pipeline.py](/Users/ahjan/phoenix_omega/scripts/run_pipeline.py)

4. **Advisory review (human-in-loop, no hard blocks except true failures)**
- Show flags for metadata similarity, teacher concentration, velocity shape, QA issues.
- Human decides `approve / hold / rework` in UI.

5. **Brand upload packets (deliverable)**
Per brand, output one folder:
- `upload_manifest.csv` (title, subtitle, description, keywords, category, series #, price)
- `book_files/` (EPUB/PDF/audiobook files as applicable)
- `cover/`
- `advisory_report.json` (all non-blocking warnings)
- `release_day.txt` (assigned upload date)

6. **Weekly upload execution by brand admins**
- Brand admins upload only their packet on assigned day.
- Keep majority series progression, plus minority standalone discovery titles.

7. **Post-upload feedback loop (Fri/Sat)**
- Collect performance + rejection/flag/refund signals per brand/teacher/topic.
- Raise issues in UI for bad trends; no automatic hard stop.
- If performance is strong for 2+ weeks, auto-recommend output increase (ex: +10-15%).

8. **Next-week auto-tuning**
- Use results to rebalance teacher/topic/persona shares and series continuation priority for next wave.

If you want, I can implement the **exact packet export script + folder format** now so each brand gets a one-click weekly handoff. 

Right now: **there is no existing “brand publish packet” file/folder** in the repo.

What exists today:
- Weekly schedule JSON: [artifacts/release_schedule.json](/Users/ahjan/phoenix_omega/artifacts/release_schedule.json) (or lane variants like `release_schedule_en.json`)
- Per-book compiled plan JSONs (metadata + pointers): [artifacts/full_catalog/candidates](/Users/ahjan/phoenix_omega/artifacts/full_catalog/candidates)
- Optional rendered manuscript txt: [artifacts/rendered](/Users/ahjan/phoenix_omega/artifacts/rendered)
- Freebie assets (not full storefront packet): [artifacts/freebies](/Users/ahjan/phoenix_omega/artifacts/freebies)

So your question is correct: admins currently do **not** have a one-click packet to download.

Best setup for admins (recommended):
1. Generate weekly packets under:
- `/Users/ahjan/phoenix_omega/artifacts/brand_packets/YYYY-WW/<brand_id>/`
2. Put inside each brand folder:
- `upload_manifest.csv`
- `book_files/` (epub/pdf/audiobook files)
- `cover/` (jpg/png)
- `advisory_report.json`
- `release_day.txt`
3. Zip each brand folder:
- `YYYY-WW_<brand_id>_packet.zip`
4. Upload zips to shared storage (R2/Drive/S3) and give admins a download link.
5. Admin downloads zip to local laptop, unzips, uploads to Google Play.

Important gap to close:
- You still need the packet-export script; it isn’t implemented yet.
- If you want, I can build `scripts/release/export_brand_packets.py` now and wire it to your weekly schedule output.

can we automate this: Upload zips to shared storage (R2/Drive/S3) and give admins a download link.
Admin downloads zip to local laptop, unzips, uploads to Google Play.

Yes. You can automate everything up to “human clicks Upload in Google Play.”

1. Build packets + zips automatically
- Export per-brand folders, zip them.
- Write to [artifacts/brand_packets](/Users/ahjan/phoenix_omega/artifacts/brand_packets).

2. Upload zips automatically to shared storage
- R2/S3: upload with bucket key like `weekly/YYYY-WW/<brand>/packet.zip`.
- Generate signed download links (24–72h expiry).
- Save links in `download_links.json`.

3. Notify admins automatically
- Send each brand admin their link (email/Slack) with `release_day`.

4. Admin-side one-click download helper
- Small script to download + unzip to laptop:
- `scripts/release/fetch_brand_packet.sh <signed_url>`

5. Google Play step
- Usually still manual in Partner Center unless your account has a feed/integration workflow enabled.

If you want, I can implement this now with:
- `scripts/release/export_brand_packets.py`
- `scripts/release/upload_brand_packets_r2.py`
- `scripts/release/notify_brand_admins.py`
- `scripts/release/fetch_brand_packet.sh`
- and a GitHub workflow to run weekly.

---

**Cursor**

Researching the codebase and docs to draft a plan for the weekly publish-packet automation and R2/notification flow.


Checking how the pipeline gets candidates and where rendered/book files are written:


Checking prepublish report shape, video R2 upload pattern, and release_schedule.json structure:


Checking how the weekly schedule is keyed (week number vs date) and whether run_pipeline writes rendered output by plan_id:


Checking report output structure and release_scheduler brand_days for release_day:


Creating the plan:


---

**User**

for: [is this platform aware? english, spanish, and EU languages  = google play (for now)
[
East Asian Ebook Platforms Guide
英文信北京腔改写
Japanese LLM for Self Help Scripts
Self Help Book Reader Personas
Deep Research Data Gap Analysis
New chat
New chat
Phoenix V4 System Analysis
Self Help Audiobook Script and Marketing
台湾Z世代职场焦虑疗愈脚本模板
台湾Z世代心理内容生成指令
集体主义家庭中心叙事模板总结
台湾Z世代职场焦虑疗愈脚本
治疗性有声书脚本Gen Z/Alpha语音模板
answer this prompt in chinese: #
张明社交焦虑与演讲稿修改
4-7-8与方形呼吸法教学翻译
用户请求翻译呼吸练习文件内容
凤凰协议翻译与保存要求
Heartfelt Letter on Friendship and Collaboration
网络调整中
Transcribing Chinese audio from Descript link.
Understanding Z世代与Alpha世代的灵性挣扎
吴师龙脉教义与地球觉醒
Max Translation Character Limit Inquiry
致袁妙导师的邀请函及活动纲要
Autumn Energy Healing and Spiritual Growth
Ways to Help People Effectively
Drinking Water Safety in Xi'an Hotels
Buying Duty-Free Alcohol in Hong Kong
Spiritual Insights on Global Enlightenment Path
East Asian Ebook Platforms Guide
ebook platforms for china, Hong Kong, Taiwan, Singapore, Japan, korea
Read 10 web pages
Hmm, the user is asking about ebook platforms across multiple East Asian regions - China, Hong Kong, Taiwan, Singapore, Japan, and Korea. This is a fairly broad research question that requires me to identify major platforms in each area. The user likely wants a comprehensive reference for personal or professional use.

I plan to structure my response by region, listing major platforms for each with brief descriptions of their focus. If search results provide sufficient coverage, I can create a comparative table followed by detailed explanations.

Looking at the search results, I have solid coverage across most regions. For China, a university library guide  provides good info on major academic platforms like Chaoxing and Wenjin. The market research report  confirms the dominance of Alibaba, Tencent, and JD.com in the Chinese market.

For Hong Kong/Taiwan, the HyRead app listing  shows it's widely used across Hong Kong, Macau, and Taiwan libraries. Pubu's app page  clearly shows it serves Taiwan, Hong Kong, and Malaysia with extensive magazine content. The SUEP platform  is specifically for Hong Kong publications.

For Singapore, the official Kobo announcements  are highly authoritative, coming directly from the company with CEO quotes. This provides excellent coverage of Kobo Plus subscription service.

For Japan, the Booklive business profile  gives solid information about this major manga-focused platform, though it's from a business database rather than an official source.

For Korea, the RHK app listing  from Google Play shows a direct publisher platform from Random House Korea. I'm missing major Korean platforms like Kyobo or Yes24, which I'll need to acknowledge.

The Taiwan library page  provides additional context about how libraries integrate commercial platforms like udn and Pubu. This adds depth to understanding how users access these platforms.

Some search results are less useful for direct platform listing. The 6Wresearch report  focuses more on market trends than specific platform names. However, it does confirm major players.

I'll organize this as a quick reference table first, then provide more detailed descriptions. This allows users to scan quickly and dive deeper where needed. I should also note limitations in Korean coverage and offer to search further.
Here is a list of ebook platforms across the regions you requested, covering major commercial services and library-based apps.

📚 Ebook Platforms at a Glance

Region	Platform	Key Features / Focus
China	Alibaba, Tencent, JD.com 	Dominant tech conglomerates offering vast ebook selections.
Chaoxing (超星) 	Massive academic ebook collection (138+ million), primarily for institutions.
Wenjin (文泉学堂) 	Academic/educational content,清华大学出版社为核心.
Zhangyue (掌阅) 	Popular general reading app with a large commercial catalog.
Hong Kong	HyRead 	Library-focused platform; borrow ebooks/magazines with a library card.
SUEP (知書閱聽圖書館) 	平台汇集香港出版物, offers ebooks and audiobooks.
Pubu 	Commercial store with subscription and purchase options; content from Taiwan/HK.
Taiwan	HyRead 	Primary library platform; borrow ebooks from public/university libraries.
Pubu 	Popular commercial store; extensive magazines and books.
udn Library 	Content from联合报系; accessible via library partnership or purchase.
iLib Reader 	App for Taiwan's National Library of Public Information platform.
Singapore	Kobo Plus 	Subscription service (SGD 9.99/mo) for 2M+ ebooks and audiobooks.
Pubu 	Commercial store with "All You Can Read" subscription; content from Taiwan/HK.
Japan	Booklive 	Major digital store specializing in manga, light novels, and comics.
Korea	RHK Books 	Publisher-direct app from Random House Korea; extensive Korean literature.
🔍 How to Choose and Use These Platforms

Here are some insights to help you navigate them:

China's Market: The landscape is dominated by Alibaba, Tencent, and JD.com . You'll typically need to use their super-apps (like Taobao or WeChat) to access their ebook services. For academic or professional content, platforms like Chaoxing and Wenjin are the primary resources, though they are often accessed through institutional subscriptions .
The Library Route (HK/TW): In Hong Kong and Taiwan, library-based apps like HyRead are the standard. If you have a library card from a participating public or university library, you can borrow ebooks for free, making it an excellent entry point .
Commercial Stores (HK/TW/SG): For purchasing or subscribing directly, Pubu is a major player. It offers a broad catalog and a unique "All You Can Read" subscription plan . In Singapore, the newly launched Kobo Plus offers a competitive subscription model similar to Kindle Unlimited .
Niche Focus (Japan): While Japan has general ebook stores, Booklive is a key player, particularly for its strength in manga, light novels, and graphic novels .
Do you need more details on any of these platforms, or are you looking for something specific, like academic resources or a particular genre?
give me the upload info for each platform. what do I upload when putting a book each platform? titles  , subtite, (do they let you upload series), what file format? epub? pdf? cover art?  ? what other meta data? for every platform
Read 9 web pages
Hmm, the user previously asked about ebook platforms across multiple Asian regions, and now they want detailed upload specifications for each platform. This is quite a comprehensive technical question about publishing requirements, covering titles, subtitles, series support, file formats, cover art, and metadata for every platform I mentioned earlier.

I'll need to organize this by platform, providing specific upload instructions for each. Since this is technical publishing data, a structured format with tables would make it easy to compare requirements across platforms.

Looking at the search results, I have solid official documentation for Kobo and Pubu. The Kobo support pages are particularly valuable - one covers book details and series fields in detail, and another specifies supported file formats (DOC, DOCX, ODT, EPUB, MOBI) with a 100MB limit. There's also information about Kobo Plus opt-in options.

For Pubu, the official support pages are excellent. They detail the upload process, support for series through the "出版连续性书刊" feature, and PDF specifications including page size consistency, no password protection, and proper left/right binding settings. Another Pubu page mentions EPUB 3.0 support and TOC requirements.

A Danish page about Publizon provides good cover specifications - minimum 1400x2100 pixels at 300 DPI, JPEG or PNG format. This is useful for general cover guidelines.

The search results don't cover China platforms (Alibaba, Tencent, JD.com), Japan (Booklive), or Korea (RHK Books). For those, I'll need to rely on general industry knowledge about ebook publishing standards. Similarly, information about HyRead, SUEP, and iLib Reader isn't in the search results.

One search result about a Chinese AI tool is completely irrelevant to ebook publishing. The Threads post provides minimal information and isn't authoritative.

I'll present this as a comprehensive table showing each platform's requirements for title, subtitle, series support, file formats, cover art specifications, and additional metadata. For the platforms without search result data, I'll note that information is based on general industry knowledge. A summary table at the end will help users quickly compare requirements across all platforms.
Here is a detailed breakdown of the upload requirements for ebook platforms across the regions you specified.

The information is compiled from official support documentation and general publishing guidelines. Please note that for platforms where specific publisher documentation was unavailable (marked with *), the information provided is based on general industry standards for ebook publishing.

📚 Platform Upload Specifications

Region	Platform	Title/Subtitle	Series Support	File Formats	Cover Art Specifications	Key Metadata & Notes
China	Alibaba, Tencent, JD.com *	Standard fields for title and subtitle.	Series support is common on major Chinese platforms.	ePub, PDF are widely accepted.	JPEG, PNG; Minimum size 1000px on the longest side; 300 DPI recommended.	Metadata fields typically include Author, Publisher, ISBN, Language, Description, and Categories/Tags.
Chaoxing (超星) *	Standard fields for title and subtitle.	Series information is typically supported.	PDF (primary format for academic content), ePub.	JPEG, PNG; Minimum size 1400px on the longest side; 300 DPI recommended.	Academic-focused metadata is crucial, including Subject Area, Keywords, and sometimes institutional identifiers.
Wenjin (文泉学堂) *	Standard fields for title and subtitle.	Series information is typically supported.	PDF (primary format), ePub.	JPEG, PNG; Minimum size 1400px on the longest side; 300 DPI recommended.	As an academic platform from Tsinghua University Press, accurate Subject Classification and educational level metadata are very important.
Zhangyue (掌阅) *	Standard fields for title and subtitle.	Series support is available.	ePub, PDF, TXT (common for web novels).	JPEG, PNG; Minimum size 800px on the longest side; 300 DPI recommended.	For a commercial app, metadata like Author, Description, and Categories are key for discoverability.
Hong Kong	HyRead *	Standard fields for title and subtitle.	Series support is typically available for library cataloging.	ePub, PDF.	JPEG, PNG; Minimum size 1400x2100 pixels; 300 DPI recommended .	As a library-focused platform, metadata accuracy for ISBN, Author, Publisher, and Subjects is critical for proper cataloging and discovery .
SUEP (知書閱聽圖書館) *	Standard fields for title and subtitle.	Information not specified; series likely supported.	ePub, PDF, Audiobook formats.	JPEG, PNG; Minimum size 1400x2100 pixels; 300 DPI recommended .	Similar to HyRead, library cataloging standards apply. Unique to SUEP, specific metadata for audiobooks (e.g., narrator, duration) would be required.
Pubu	Yes, both Title and Subtitle are supported .	Yes, a "书刊连续性出版" feature allows for easy management and publication of series, magazines, or serialized content .	ePub (EPUB 3.0 supported), PDF .	You can upload a file or use their online designer. For best results, the image should be clear and include the title and author .	Key Metadata: Author, Publisher, Language, Description/Categories, Price, and Publication Date. Allows setting "non-public" permissions for private sharing .
Taiwan	HyRead	See entry for Hong Kong HyRead.	See entry for Hong Kong HyRead.	See entry for Hong Kong HyRead.	See entry for Hong Kong HyRead.	See entry for Hong Kong HyRead.
Pubu	See entry for Hong Kong Pubu.	See entry for Hong Kong Pubu.	See entry for Hong Kong Pubu.	See entry for Hong Kong Pubu.	See entry for Hong Kong Pubu.
udn Library *	Standard fields for title and subtitle.	Series support is available, especially for content from the 联合报系.	ePub, PDF.	JPEG, PNG; Minimum size 1400x2100 pixels; 300 DPI recommended .	As a library platform, it requires robust cataloging metadata (ISBN, Author, Subjects). Content originating from 联合报系 may have specific categorization needs.
iLib Reader *	Standard fields for title and subtitle.	Series support is likely available.	ePub, PDF.	JPEG, PNG; Minimum size 1400x2100 pixels; 300 DPI recommended .	As the app for Taiwan's National Library of Public Information, it adheres to strict library cataloging standards. ISBN and accurate subject headings are essential.
Singapore	Kobo Plus	Yes, both Title and Subtitle are supported .	Yes, Series Name and Volume Number can be specified .	ePub, DOC, DOCX, ODT, MOBI. Kobo will convert non-ePub files to their format. Max file size: 100MB .	JPG or PNG file. 300 DPI recommended, with a max file size of 5MB. Aim for dimensions around 1448x1072 pixels for optimal display .	Key Metadata: Author, Publisher, ISBN/eISBN, Language, Description, Categories (up to 3), and Digital Rights Management (DRM) on/off. Also allows setting territorial rights and opting into the Kobo Plus subscription program .
Pubu	See entry for Hong Kong Pubu.	See entry for Hong Kong Pubu.	See entry for Hong Kong Pubu.	See entry for Hong Kong Pubu.	See entry for Hong Kong Pubu.
Japan	Booklive *	Standard fields for title and subtitle, likely in Japanese.	Yes, series support is very important for manga and light novels.	ePub (including Fixed Layout for manga/comics), PDF.	JPEG, PNG; Minimum size 1400px on the longest side; 300 DPI recommended.	For manga and comics, accurate metadata for Series, Volume Number, Contributors (Author, Illustrator), and Genres (e.g., Shonen, Shojo, Seinen) is crucial.
Korea	RHK Books *	Standard fields for title and subtitle, likely in Korean.	Yes, series support is common.	ePub, PDF.	JPEG, PNG; Minimum size 1400x2100 pixels; 300 DPI recommended .	As a major publisher's direct app, it requires standard commercial metadata: Title, Subtitle, Author, Publisher (Random House Korea), ISBN, Price, Description, and Categories.
🔍 Key Takeaways for Uploading

File Formats are Key: While most platforms accept ePub and PDF, ePub is the preferred standard for its reflowable text, which provides a better reading experience on different devices . For complex layouts like comics or children's books, a Fixed-Layout ePub or PDF may be necessary .
Cover Art is Critical: Your cover is the first thing a reader sees. Always aim for a high-resolution image, ideally at least 1400px on the shortest side at 300 DPI in JPEG format, to ensure it looks sharp on all devices .
Metadata Drives Discovery: The information you fill out—title, author, series, categories, and description—is how readers will find your book in a crowded store. Take the time to fill this out accurately and completely .
Check Platform Specifics: Always refer to the official "Publisher Help" or "Upload Guide" section of your chosen platform, as requirements can be updated.
I hope this detailed breakdown helps you prepare your books for upload. Do you need me to clarify any of these points or explore another aspect of the publishing process?

]]

do: Short answer: **not fully**.

For your stated scope now (`English + Spanish + EU languages = Google Play only`), that long guide is **too broad** and includes a lot of non-Google platforms and some unverified assumptions.

What “platform-aware” should mean for you right now:
1. **Single-platform profile:** Google Play Books only.
2. **Per-locale metadata packs:** title/subtitle/description/keywords/category per language.
3. **Territory rights matrix:** which countries each language edition is allowed in.
4. **Google-ready files only:** production EPUB (+ cover image), optional PDF if needed.
5. **Series fields enforced:** series name + volume/number consistency.
6. **Upload packet per brand/week:** manifest + files + covers + release date.

So your current writeup is a useful research dump, but for operations it should be reduced to a **Google Play publishing spec** only.  
If you want, I can draft that exact “Google Play Only (EN/ES/EU)” upload spec and packet template next.

---

**Cursor**

Short answer: **not fully.** For your current scope (English, Spanish, EU languages = **Google Play Books only**), the East Asian ebook guide is out of scope and mixes in non‑Google platforms and unverified details. For operations, treat “platform-aware” as **Google Play only** and lock the packet to that.

Below is a concise **Google Play Only (EN/ES/EU)** upload spec and packet template you can drop into docs or a spec file.

---

## Google Play Books only — upload spec (EN / ES / EU)

**Scope:** One storefront — Google Play Books. Locales: EN (en-US and any other EN), ES (es-ES, es-US, etc.), and EU languages (e.g. de-DE, fr-FR, it-IT, hu-HU). No China/HK/TW/SG/JP/KR platforms in this spec.

### 1. Platform profile

- **Platform:** Google Play Books only.
- **Territory rights:** Per locale (e.g. en-US → US/UK/CA; es-ES → Spain; de-DE → DACH), configurable per brand/locale; no automatic worldwide for all languages.

### 2. Per-locale metadata (required in packet)

For each book and each locale you ship:

- **Title** (required)  
- **Subtitle** (optional)  
- **Description** (required)  
- **Keywords** (optional; comma-separated or list)  
- **Category** (Google Play category code or label)  
- **Language** (BCP-47, e.g. en-US, es-ES, de-DE)  
- **Series name** (if part of a series)  
- **Series volume / number** (e.g. 1, 2, 3)  
- **Author / contributor** (display name)  
- **Publisher** (imprint/brand)

So “platform-aware” here = one metadata set per (book × locale), not one set for all platforms.

### 3. Google-ready files (in packet)

- **Primary:** One **EPUB** per book (and per locale if you ship separate locale editions).  
- **Cover:** One **cover image** per book (JPEG or PNG; e.g. min 1400px short side, 300 DPI; max size per Google’s current limits).  
- **Optional:** PDF only if you explicitly need it for a given title (not required for this spec).

No other formats (e.g. MOBI, DOC) in the packet for Google.

### 4. Series rules

- **Series name** must be identical for all books in the same series.  
- **Volume/number** must be unique and ordered (1, 2, 3, …).  
- Packet manifest must expose series name + volume number so uploads stay consistent.

### 5. Upload packet (per brand per week)

One folder (or zip) per brand per week, containing:

| Item | Purpose |
|------|--------|
| **upload_manifest.csv** | One row per book (and optionally per locale): title, subtitle, description, keywords, category, series name, series number, language, price, etc. |
| **book_files/** | EPUB(s) per book (and per locale if separate); optional PDF if needed. |
| **cover/** | One cover image per book (or per edition if different). |
| **release_day.txt** | Single upload date for that brand that week. |
| **advisory_report.json** | Non-blocking advisories only (no change to what you already have). |

So “platform-aware” for this spec = **one packet format, one storefront (Google Play), EN/ES/EU only**, with per-locale metadata and territory controlled outside the packet (e.g. in config or UI).

---

If you want this turned into a repo artifact, we can add a short doc (e.g. `docs/GOOGLE_PLAY_UPLOAD_SPEC.md`) and optionally a schema or example `upload_manifest.csv` and folder layout; that would be a small addition to the weekly brand packet plan (still Google Play only, EN/ES/EU).

---

**User**

This is solid and implementation-ready.  
The flow, boundaries, and file layout are right.

Add these 10 hard requirements before coding:

1. **Idempotency**
- Re-running same week must overwrite deterministically (no duplicate zips/links rows).

2. **Single week key**
- Use one canonical key everywhere: `YYYY-WW` derived once from `week_start`.

3. **Strict manifest schema**
- Add `schemas/release/brand_packet_manifest_v1.schema.json` and validate `upload_manifest.csv`/`advisory_report.json` structure.

4. **Feasibility guard**
- Export fails early if schedule week exists but referenced plan files are missing.

5. **Checksum + size**
- Write `sha256` + bytes for each zip in `download_links.json` so admins can verify integrity.

6. **Signed URL policy**
- Short TTL (24–72h), no public ACL, prefix-scoped keys only (`weekly/YYYY-WW/...`).

7. **Notification resilience**
- Per-brand retry + dead-letter log (`artifacts/brand_packets/YYYY-WW/notify_failures.json`), don’t fail whole run on one brand.

8. **Audit trail**
- Emit one machine-readable run report: `packet_delivery_report.json` (exported, uploaded, notified, failed).

9. **Secrets boundary**
- Keep contacts in config, but SMTP/Slack/R2 credentials only via env/secrets manager (never repo).

10. **Workflow dependency check**
- In workflow, explicitly assert:
  - schedule exists for target week
  - assembled outputs exist (plans/rendered)
  - otherwise stop with actionable error.

If you want, I can implement this now in the order:
`export_brand_packets.py` → `upload_brand_packets_r2.py` → `fetch_brand_packet.sh` → `notify_brand_admins.py` → workflow + docs.

---

**Cursor**

Adding the 10 hard requirements to the plan so they're part of the implementation spec.


Adding the 10 hard requirements as a dedicated section and wiring them into the implementation plan.


Adding the implementation order you specified:


Summary of what was added to the plan:

**New section: “10 hard requirements (before coding)”**  
- **1. Idempotency** — Same week re-run overwrites; no duplicate zips/links.  
- **2. Single week key** — `YYYY-WW` derived once from `week_start`; used everywhere.  
- **3. Strict manifest schema** — `schemas/release/brand_packet_manifest_v1.schema.json`; validate `upload_manifest.csv` and `advisory_report.json`.  
- **4. Feasibility guard** — Export fails early if any referenced plan/rendered path is missing; list missing paths.  
- **5. Checksum + size** — Each zip: `sha256` + `size_bytes` in `download_links.json`.  
- **6. Signed URL policy** — 24–72h TTL, no public ACL, prefix `weekly/YYYY-WW/...` only.  
- **7. Notification resilience** — Per-brand retry + `notify_failures.json`; don’t fail whole run.  
- **8. Audit trail** — Single `packet_delivery_report.json` (export / upload / notify, with errors).  
- **9. Secrets boundary** — Contacts in config; SMTP/Slack/R2 only via env/secrets.  
- **10. Workflow dependency check** — Assert schedule for target week exists and assembled outputs exist; stop with actionable error otherwise.

**Implementation sections** now reference these (e.g. “Requirements tie-in” bullets and concrete steps for feasibility guard, idempotency, checksum, notify_failures, report updates, dependency check).

**File summary** includes `schemas/release/brand_packet_manifest_v1.schema.json` and the workflow dependency check.

**Implementation order** is set to:  
`export_brand_packets.py` → `upload_brand_packets_r2.py` → `fetch_brand_packet.sh` → `notify_brand_admins.py` → workflow + docs (with schema added before or with export).

The plan is updated and ready for implementation in that order whenever you want to start coding.

---

**User**

Proposed weekly flow:

Planner creates week schedule (which books per brand).
Pearl Prime pipeline assembles each book package.
Packet exporter builds per-brand zip.
Uploader sends zips to Cloudflare R2.
System generates signed download links (expire in 24–72h).
Notifier sends each brand admin their link + release day.
How admins get it:

Primary: email (and/or Slack DM/webhook) with signed link.
No R2 login needed if using signed links.
Optional later: admin portal login dashboard, but not required for v1.
So yes: brand admins receive a link, download zip to laptop, unzip, then manually upload to Google Play.

Use this build order:

1. **Create packet exporter**
- Script: `/Users/ahjan/phoenix_omega/scripts/release/export_brand_packets.py`
- Input: `artifacts/release_schedule.json` + selected week.
- Output per brand:
  - `/Users/ahjan/phoenix_omega/artifacts/brand_packets/YYYY-WW/<brand_id>/upload_manifest.csv`
  - `book_files/`, `cover/`, `advisory_report.json`, `release_day.txt`
  - zip: `YYYY-WW_<brand_id>_packet.zip`

2. **Create R2 uploader + signed-link generator**
- Script: `/Users/ahjan/phoenix_omega/scripts/release/upload_brand_packets_r2.py`
- Upload each zip to key: `weekly/YYYY-WW/<brand_id>/packet.zip`
- Generate presigned URLs and write:
  - `/Users/ahjan/phoenix_omega/artifacts/brand_packets/YYYY-WW/download_links.json`

3. **Create notifier (email + Slack webhook)**
- Script: `/Users/ahjan/phoenix_omega/scripts/release/notify_brand_admins.py`
- Contacts config:
  - `/Users/ahjan/phoenix_omega/config/release/brand_admin_contacts.yaml`
- Reads `download_links.json`, sends per-brand message with link + `release_day`.

4. **Create admin fetch helper**
- Script: `/Users/ahjan/phoenix_omega/scripts/release/fetch_brand_packet.sh`
- Usage: `fetch_brand_packet.sh <signed_url> [output_dir]`
- Does `curl` + `unzip`.

5. **Automate in GitHub Actions**
- Workflow: `/Users/ahjan/phoenix_omega/.github/workflows/weekly-brand-packets.yml`
- Steps:
  - export packets
  - upload to R2
  - notify admins
- Trigger: `schedule` + `workflow_dispatch`.

6. **Required secrets**
- `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`
- Email creds (SMTP or provider API key)
- Slack webhook URLs (or bot token).

7. **Safety requirements**
- Idempotent reruns for same week.
- Short URL expiry (24–72h).
- Per-brand retry + failure log.
- Output `packet_delivery_report.json` for audit.

If you want, I can implement all 4 scripts + workflow in this repo now.




---

**Cursor**

Implementing the four scripts, workflow, config, schema, and docs per the plan and your build order.


Creating the schema and export script.


Adding a short docs section and fixing the workflow: dependency-check runs on ubuntu-latest and won't have artifacts from other workflows. Making the dependency check robust:


Checking how catalog-book-pipeline stores its output:


Summary of what was implemented:

---

## 1. **Schema**
- **`schemas/release/brand_packet_manifest_v1.schema.json`** – Documents `upload_manifest.csv` columns and references advisory structure.
- **`schemas/release/advisory_report_v1.schema.json`** – Validates `advisory_report.json` (schema_version, issues array).

## 2. **`scripts/release/export_brand_packets.py`**
- Inputs: `--schedule`, `--week` or `--week-start`, optional `--wave-id`, `--prepublish-report`.
- Single week key: **YYYY-WW** from `week_start` (ISO week).
- **Feasibility guard:** Exits with a list of missing paths if any referenced plan file is missing.
- **Idempotent:** Cleans and recreates `artifacts/brand_packets/YYYY-WW/` (brand dirs and zips).
- Per brand: `upload_manifest.csv` (columns from schema), `book_files/` (plan JSON + rendered), `cover/`, `advisory_report.json`, `release_day.txt` (from `release_scheduler.yaml` `brand_days`).
- Zips: `YYYY-WW_<brand_id>_packet.zip`.
- Writes/updates **`packet_delivery_report.json`** (export section).

## 3. **`scripts/release/upload_brand_packets_r2.py`**
- Inputs: `--packets-dir` or `--week-start`, `--expiry-hours` (24–72), `--dry-run`.
- R2 client from **env only**; bucket/prefix from `config/release/brand_packets_r2.yaml` or env.
- Uploads each zip to **`weekly/YYYY-WW/<brand_id>/packet.zip`**.
- **Checksum:** Adds **sha256** and **size_bytes** per zip in `download_links.json`.
- Presigned GET URLs with chosen TTL; overwrites `download_links.json`.
- Updates **`packet_delivery_report.json`** (upload section).

## 4. **`scripts/release/notify_brand_admins.py`**
- Reads **`config/release/brand_admin_contacts.yaml`** (brand → email / slack_webhook).
- **Secrets:** SMTP and Slack webhook from **env only**.
- Per-brand **retry** (2 attempts with backoff).
- Failures appended to **`notify_failures.json`** (brand, channel, error, timestamp).
- Updates **`packet_delivery_report.json`** (notify section); does not fail the whole run.

## 5. **`scripts/release/fetch_brand_packet.sh`**
- Usage: `fetch_brand_packet.sh <signed_url> [output_dir]`.
- Runs `curl -fSL` then `unzip -o`; executable and dependency-free (curl, unzip).

## 6. **Config**
- **`config/release/brand_admin_contacts.yaml`** – Placeholder entries (no real emails/webhooks); doc points to env.
- **`config/release/brand_packets_r2.yaml`** – Non-secret (prefix `weekly`); bucket/creds from env.

## 7. **`.github/workflows/weekly-brand-packets.yml`**
- Triggers: **schedule** (Tue 02:00 UTC) and **workflow_dispatch** (optional `week_start`, `skip_notify`).
- **Dependency check job:** Resolves week (input or first week in `artifacts/release_schedule.json` if present); errors if week cannot be determined.
- **Export / upload / notify job:** Asserts schedule and assembled outputs exist, then runs export → upload (R2 secrets) → notify (SMTP/Slack secrets). Uploads **`artifacts/brand_packets/`** as a workflow artifact.

## 8. **Docs**
- **`docs/DOCS_INDEX.md`** – New row for “Weekly brand packet delivery” with links to scripts, config, schemas, and workflow.

---

**Required secrets (GitHub / env):**  
`R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`; `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `NOTIFY_FROM_EMAIL`; Slack webhook URLs per brand in config or env (e.g. `SLACK_WEBHOOK_STILLNESS_PRESS`).

---

**User**

do this lite-weight and simple:

1. **Brand Admin Portal (login required)**
- Build a small web app (`/admin/packets`) that lists only that admin’s brands and current week packets.
- Auth via **Cloudflare Access** (Google/Microsoft login + MFA).

2. **Access model**
- Keep mapping in config/db: `admin_user -> allowed_brand_ids`.
- On login, portal filters packets by allowed brands only.

3. **Link generation**
- Do **not** store permanent public links.
- When admin clicks “Get Download,” backend mints a short-lived R2 signed URL (e.g. 15 minutes).

4. **Storage**
- Keep zips in R2 at `weekly/YYYY-WW/<brand_id>/packet.zip`.
- Keep packet metadata in `download_index.json` (week, brand, size, checksum, release_day).

5. **Audit + security**
- Log every request/download: user, brand, week, timestamp, IP.
- Enforce MFA, session timeout, and rate limits.
- Optional one-time token links per click.

6. **Automation stays the same**
- Pipeline still exports packet zips and uploads to R2 automatically.
- Difference: notifications point admins to portal (“log in to download”), not direct signed URLs.

If you want, I can draft the exact portal API/routes and data schema next (minimal v1).

## Minimal V1 Portal Spec (Login-required packet downloads)

### 1. Components
1. **Packet builder job** (already planned): exports zips + metadata weekly.
2. **R2 object store**: holds `packet.zip` files.
3. **Admin portal backend**: auth, brand authorization, signed URL minting.
4. **Admin portal UI**: “My Brands” weekly packet table + download button.
5. **Audit log**: every signed-link issuance + download redirect event.

---

## 2. Data Model

### `brand_admin_users`
- `id` (uuid)
- `email` (unique)
- `display_name`
- `status` (`active|disabled`)
- `created_at`

### `brand_admin_grants`
- `id` (uuid)
- `user_id` (fk)
- `brand_id` (string)
- `role` (`admin|viewer`)
- `created_at`

### `weekly_packets`
- `id` (uuid)
- `week_key` (`YYYY-WW`)
- `brand_id`
- `r2_key` (`weekly/YYYY-WW/<brand_id>/packet.zip`)
- `release_day` (`YYYY-MM-DD`)
- `bytes`
- `sha256`
- `status` (`ready|missing|archived`)
- `created_at`

### `packet_access_audit`
- `id` (uuid)
- `user_id`
- `brand_id`
- `week_key`
- `action` (`list|mint_link|download_click`)
- `ip`
- `user_agent`
- `created_at`
- `result` (`ok|denied|error`)

---

## 3. AuthN/AuthZ
1. **AuthN**: Cloudflare Access (OIDC, MFA required).
2. Backend trusts Access headers/JWT and resolves `email -> user`.
3. **AuthZ**: only packets where `brand_id` is in `brand_admin_grants` for that user.

---

## 4. API Routes (backend)

1. `GET /api/me`
- returns user profile + granted brands.

2. `GET /api/packets?week=YYYY-WW`
- returns only packets for user’s brands.
- includes: brand_id, week_key, release_day, size, sha256, status.

3. `POST /api/packets/{week_key}/{brand_id}/signed-url`
- checks grant.
- mints short TTL R2 signed URL (10–15 min).
- returns `{url, expires_at}`.
- writes `packet_access_audit(action=mint_link)`.

4. `GET /api/audit/recent` (admin-only optional)
- recent access events.

---

## 5. UI Routes

1. `/admin/login` (handled by Cloudflare Access)
2. `/admin/packets`
- week selector (default current)
- table per brand:
  - Brand
  - Release Day
  - File Size
  - SHA256
  - Status
  - `Get Download Link` button
3. button calls signed-url endpoint and then starts download.

---

## 6. Weekly Automation Integration
1. Export zips.
2. Upload zips to R2.
3. Upsert `weekly_packets` rows from upload output.
4. Notify admins: “Packet ready, log into portal” (no direct links).

---

## 7. Security Defaults
1. Signed URLs expire in 15 min.
2. No public bucket ACL.
3. Rate-limit link mint endpoint.
4. Log denied attempts.
5. Disable users by flipping `status`.

---

## 8. File/Code Layout Proposal

- `/Users/ahjan/phoenix_omega/services/admin_portal/`
  - `app.py` (or `main.ts`)
  - `auth.py`
  - `routes_packets.py`
  - `models.py`
- `/Users/ahjan/phoenix_omega/config/release/brand_admin_contacts.yaml` (optional bootstrap)
- `/Users/ahjan/phoenix_omega/scripts/release/sync_packets_to_portal_index.py`

---

If you want, next step I can generate the exact OpenAPI spec + SQL schema + starter backend skeleton.

---

**Cursor**

Implementing the minimal V1 admin portal: SQL schema, FastAPI backend, Cloudflare Access auth, and sync script.


Creating the portal schema, backend, sync script, and minimal UI.


Wiring the sync into the upload script and adding a DOCS_INDEX entry.


Fixing packets_for_week so a user with no grants gets an empty list.


Adding an optional `--portal-url` to the notifier so notifications can point to the portal instead of a direct link.


Summary of what’s in place for the minimal v1 admin portal:

---

## 1. **Data & schema**
- **`services/admin_portal/schema.sql`** — SQLite: `brand_admin_users`, `brand_admin_grants`, `weekly_packets`, `packet_access_audit`.
- **`services/admin_portal/download_index_schema.json`** — JSON schema for optional `download_index.json` (week + packets with brand_id, r2_key, release_day, bytes, sha256, status).

## 2. **Backend**
- **`services/admin_portal/models.py`** — DB helpers: `get_conn`, `init_db`, `user_by_email`, `user_grants`, `packets_for_week`, `upsert_packet`, `insert_audit`, `recent_audit`, `ensure_user_and_grants`.
- **`services/admin_portal/auth.py`** — Reads `Cf-Access-Authenticated-User-Email`; dev: `OVERRIDE_EMAIL`.
- **`services/admin_portal/routes_packets.py`** — FastAPI routes:
  - `GET /api/me` — profile + granted brands.
  - `GET /api/packets?week=YYYY-WW` — packets for user’s brands only.
  - `POST /api/packets/{week_key}/{brand_id}/signed-url` — mint 15‑min R2 URL, rate limit (10/15 min), audit.
  - `GET /api/audit/recent` — recent access events.
- **`services/admin_portal/app.py`** — FastAPI app, mounts `/admin/packets` and `/api`; root and `/admin/login` stubs.

## 3. **UI**
- **`services/admin_portal/templates/packets.html`** — Single page: week input, table (Brand, Release day, Size, SHA256, Status, “Get download link”); calls API and opens signed URL in same tab.

## 4. **Sync & bootstrap**
- **`scripts/release/sync_packets_to_portal_index.py`** — Reads `artifacts/brand_packets/YYYY-WW/download_links.json` and each brand’s `release_day.txt`; upserts into `weekly_packets`; optional `--write-index` to write `download_index.json`.
- **`scripts/release/bootstrap_portal_users.py`** — Reads `config/release/brand_admin_contacts.yaml` (email per brand), builds email → brands, calls `ensure_user_and_grants`.

## 5. **Notify + portal**
- **`scripts/release/notify_brand_admins.py`** — New **`--portal-url`**. When set, email/Slack say “Log in to the portal to download” with that URL instead of a direct signed link.

## 6. **Docs**
- **`services/admin_portal/README.md`** — Run (uvicorn), env (PORTAL_DB_PATH, OVERRIDE_EMAIL, R2_*), bootstrap, weekly flow, security (15‑min URL, rate limit, audit).
- **`docs/DOCS_INDEX.md`** — New “Admin portal” bullet under Weekly brand packet delivery.

---

**Flow**
1. Put the app behind **Cloudflare Access** (e.g. `/admin/*`); Access sets the email header (and MFA).
2. Run **bootstrap_portal_users.py** once (or when contacts change) so `brand_admin_users` / `brand_admin_grants` match config.
3. After each upload to R2, run **sync_packets_to_portal_index.py** so `weekly_packets` is up to date.
4. Notify with **`--portal-url https://your-portal.example.com/admin/packets`** so admins get “log in to download” instead of a direct link.
5. Admins open the portal, pick week, click “Get download link” → backend mints a 15‑min R2 URL and redirects; every mint is audited.

**Run locally**
```bash
pip install -r services/admin_portal/requirements.txt
OVERRIDE_EMAIL=you@example.com uvicorn services.admin_portal.app:app --reload --host 0.0.0.0 --port 8000
```
Then open `http://localhost:8000/admin/packets` and `http://localhost:8000/docs`. Ensure the DB is initialized and users/grants and `weekly_packets` are populated (bootstrap + sync).

---

**User**

Yes. This is production-grade and well-scoped.

Only add these final guardrails before implementation:

1. **Schema split**
- Keep `brand_packet_manifest_v1.schema.json` for JSON artifacts only.
- For `upload_manifest.csv`, add a separate CSV header contract checker (schema for rows after CSV->JSON transform).

2. **ISO week consistency**
- Derive `YYYY-WW` from `week_start` **after normalizing to Monday** to avoid timezone/week-boundary drift.

3. **Rendered-path rule**
- Define exactly what counts as “required rendered output” (e.g. `artifacts/rendered/<plan_id>/book.txt`), otherwise feasibility checks will be ambiguous.

4. **Partial brand handling**
- Choose policy explicitly:
  - strict mode: any missing file fails whole week (recommended now),
  - permissive mode: skip broken brand and continue.
- You currently imply strict; keep that.

5. **Notification idempotency**
- Include `run_id` and `week_key` in `notify_failures.json` and `packet_delivery_report.json` so reruns are traceable.

6. **Workflow wiring**
- Add a hard pre-step that validates `--candidates-dir` was used upstream; this is your current biggest operational gap.

If you want, I can now turn this into concrete files and implement in the exact order you listed.

---

**Cursor**

Implementing the six guardrails: checking the codebase for schedule output shape and where we derive the ISO week.


Implementing all six guardrails.


Adding a shared week-normalization helper and CSV validation, then applying the rest of the guardrails.


Normalizing week_start before computing week_key.


Updating upload script, notify script, sync script, generate_weekly_schedule, and workflow.


Checking how other release scripts import from the repo:


Adding `scripts/__init__.py` and `scripts/release/__init__.py`, and switching export to use the same import pattern.


Removing the duplicate block and fixing the import.


Adding run_id to the upload report and implementing the schedule-source validation in generate_weekly_schedule and the workflow:


Adding a short release guardrails doc and updating the DOCS_INDEX.


Summary of what was implemented:

---

## 1. **Schema split**
- **`schemas/release/upload_manifest_csv_v1.schema.json`** added: `required_headers` and `row_schema` for CSV rows (after CSV→JSON).
- **`schemas/release/brand_packet_manifest_v1.schema.json`** limited to JSON: `upload_manifest_columns` removed; only `advisory_report` kept. CSV contract is documented to live in the CSV schema.

## 2. **ISO week consistency**
- **`scripts/release/week_utils.py`** added with `normalize_week_start_to_monday(week_start)` and `iso_week_from_week_start(week_start)` so YYYY-WW is always derived from the Monday of the week.
- **Export:** Normalizes `week_start` to Monday, then derives `week_key`; uses week_utils (with `sys.path` for script runs).
- **Upload, notify, sync:** Use `iso_week_from_week_start` when deriving `week_key` from `--week-start`.
- **`scripts/__init__.py`** and **`scripts/release/__init__.py`** added so `from scripts.release.week_utils import ...` works when repo root is on `sys.path`.

## 3. **Rendered-path rule**
- **Required rendered output:** `artifacts/rendered/<plan_id>/book.txt` (or wave `.../rendered/<plan_id>/book.txt`). Constant **`REQUIRED_RENDERED_FILE = "book.txt"`** in export script.
- **Feasibility guard:** For each plan, export resolves the rendered dir and requires that file; if missing it’s added to `missing`; in strict mode the run fails.

## 4. **Partial brand handling**
- **`--strict` (default)** and **`--no-strict`** added to export. Docstring and guardrails doc state: strict = any missing plan or required rendered file fails the whole week; permissive = skip broken brand and continue.

## 5. **Notification idempotency**
- **Export:** Generates `run_id` (UUID) and writes it into **`packet_delivery_report.json`** (`run_id`, `week`, export section, timestamp).
- **Notify:** Generates `run_id`; writes **`notify_failures.json`** as `{ "run_id", "week_key", "failures": [...] }`; updates **`packet_delivery_report.json`** notify section with `run_id`, `week_key`.
- **Upload:** Keeps existing `run_id` from report when updating.

## 6. **Workflow: schedule source validation**
- **`scripts/release/generate_weekly_schedule.py`** now writes **`schedule_source`** and **`candidates_dir`** or **`wave`** into the schedule JSON when `--candidates-dir` or `--wave` is used.
- **`.github/workflows/weekly-brand-packets.yml`** has a new pre-step **“Validate schedule source (candidates-dir or wave used upstream)”** that fails if `schedule_source` is not `candidates_dir` or `wave`, or if the corresponding path is missing.

---

**Docs**
- **`docs/RELEASE_PACKET_GUARDRAILS.md`** added: schema split, ISO week, required rendered path, strict/permissive, run_id/week_key, schedule source validation.
- **`docs/DOCS_INDEX.md`** updated: link to upload_manifest_csv schema, to RELEASE_PACKET_GUARDRAILS, and to workflow schedule_source validation.

**CSV headers in export**
- Export uses **`_load_manifest_columns()`** to read **`required_headers`** from `upload_manifest_csv_v1.schema.json` when present; otherwise it falls back to the existing default list.

---

**User**

for UI: Below is a **clear product description / spec** you can give to designers or developers for the **Pearl Prime web app**.

---

# Pearl Prime — Web App UI & Branding Specification

## 1. Application Name & Branding

The web application will be branded **“Pearl Prime.”**

Brand presentation requirements:

* Display the **pearl_prime_icon.png** icon.
* The icon should appear **to the left of the text “Pearl Prime.”**
* The brand should be placed in the **top navigation bar** of the app.

Example header layout:

```
[pearl_prime_icon.png]  Pearl Prime
```

The brand identity should feel:

* calm
* uplifting
* spiritual
* modern and clean

---

# 2. Visual Design Theme

### Background

Primary background color:

```
Light Blue
```

Suggested tone:

```
#EAF6FF
```

### Accent colors

White should be used for:

* panels
* cards
* UI sections
* menu bars

Example:

```
background: light blue
cards: white
text: dark gray / navy
```

### Design style

The design should feel:

* peaceful
* minimalist
* modern spiritual technology
* readable and uncluttered

---

# 3. Bottom Animated Text Ticker

A **horizontal scrolling ticker** will run across the **bottom of the screen**.

### Animation style

* Similar to a **stock market ticker**
* Text moves **right → left continuously**
* Smooth, constant speed
* Infinite loop

### Languages

The ticker can contain:

* English
* Chinese
* Japanese

Languages may rotate or mix.

### English ticker content

```
Spread wisdom to every heart.
Offer hope to the weary.
Let the truth shine everywhere.
Guide spirits toward freedom.
Carry compassion to the world.
Lift hearts with words.
Awaken the light within all.
Share words of healing.
Open paths to inner peace.
Plant seeds of awakening.
Bring clarity to the confused.
Let wisdom flow to all beings.
```

### Ticker behavior

* Sentences should appear sequentially
* When the final sentence finishes, it loops again
* Text spacing should allow comfortable reading

Example visual behavior:

```
→ Spread wisdom to every heart → Offer hope to the weary → Let the truth shine everywhere →
```

---

# 4. Left Side Vertical Word Runner

A **vertical scrolling message column** will appear on the **left side of the screen**.

### Animation style

* Text moves **bottom → top**
* Continuous smooth scrolling
* Infinite loop

Similar to:

* meditation quotes
* news feed
* vertical message stream

### Message content

```
Books that inspire courage
Books that awaken wisdom
Stories that open hearts
Stories that reveal truth
Teachings that guide the path
Teachings that bring clarity
Exercises that calm the mind
Exercises that restore balance
Practices that nurture peace
Practices that build resilience
Words that uplift the spirit
Words that spark transformation
```

### Display behavior

Each phrase should:

* appear individually
* rise upward
* fade out slightly near the top
* new phrases appear from the bottom

This creates a **continuous vertical flow of inspiration.**

---

# 5. Layout Overview

Example UI structure:

```
-----------------------------------------------------
| Pearl Prime logo + icon                           |
-----------------------------------------------------

| LEFT MESSAGE COLUMN |     MAIN CONTENT AREA       |
|                     |                             |
| Books that inspire  |                             |
| courage             |                             |
|                     |                             |
| Stories that open   |                             |
| hearts              |                             |
|                     |                             |
| (vertical scroll)   |                             |
|                     |                             |
-----------------------------------------------------
| horizontal ticker scrolling messages              |
-----------------------------------------------------
```

---

# 6. Motion & Animation Guidelines

Animations should feel:

* calm
* smooth
* not distracting
* meditative

### Speed suggestions

Horizontal ticker:

```
~40–60 seconds per loop
```

Vertical message column:

```
~1 phrase every 3–5 seconds
```

---

# 7. Typography

Recommended style:

Primary font:

```
Clean Sans Serif
```

Examples:

* Inter
* Open Sans
* Lato

Text tone should be:

* readable
* calm
* elegant

---

# 8. Optional Enhancement (Recommended)

Developers may optionally add:

### language rotation

Ticker alternates between:

```
English
Chinese
Japanese
```

### subtle glow animation

Important words such as:

```
wisdom
peace
awakening
clarity
```

may gently brighten.

---

# 9. Design Goals

The Pearl Prime interface should communicate:

* wisdom
* peace
* compassion
* spiritual guidance

The UI should feel like a **modern digital temple of knowledge**, where teachings flow continuously across the screen.

---

If you want, I can also generate a **developer-ready version** that includes:

* **HTML structure**
* **CSS animation code**
* **React / Next.js layout**
* **ticker animation implementation**

so a developer could build this **in under 1 hour.**

Yes, it’s good as a product brief.

For implementation quality, tighten 6 items:

1. **Accessibility**
- Add reduced motion mode (`prefers-reduced-motion`) to pause/slow both tickers.
- Ensure WCAG contrast on light blue/white.

2. **Mobile behavior**
- Define responsive fallback:
  - hide or collapse left vertical runner on small screens,
  - keep bottom ticker single-line with overflow handling.

3. **Content safety**
- Move ticker/runner phrases to config/JSON so they’re editable without code deploy.

4. **Performance**
- Use CSS transforms (`translate3d`) for animation, avoid JS timers where possible.

5. **I18n typography**
- Define CJK font fallback stack for Chinese/Japanese to avoid ugly rendering.

6. **Brand asset spec**
- Add exact icon size and padding (e.g. 28px icon, 10px gap, 56px header height).

If you want, I can turn this into a developer-ready spec + starter React/CSS files next.

---

**Cursor**

Creating a plan for the developer-ready Pearl Prime spec (with the six tightenings) and starter implementation.


---

**User**

Pearl Prime Web App — Developer-Ready Spec and Starter

Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself.

To-do's from the plan have already been created. Do not create them again. Mark them as in_progress as you work, starting with the first one. Don't stop until you have completed all the to-dos.

---

**Cursor**

Implementing the Pearl Prime Web App plan: creating the spec document, then the content config, then the starter implementation.


Creating the starter implementation and copying the icon into `pearl_prime_web/assets/`.


Adding a copy of the config into the web app so it works when served from `pearl_prime_web/`.


Adjusting runner animation to ~4s per phrase (12 phrases × 4s = 48s per set, 96s full loop).


Adding a Pearl Prime web entry to DOCS_INDEX.


Summary of what’s in place:

**1. Spec** — `docs/PEARL_PRIME_WEB_APP_SPEC.md`
- **§1–§9:** Product brief (name/branding, theme, ticker, vertical runner, layout, motion, typography, optional enhancements, design goals).
- **§10:** Accessibility — `prefers-reduced-motion`, WCAG contrast.
- **§11:** Mobile — runner hidden below 768px, ticker single-line.
- **§12:** Content safety — config path and schema.
- **§13:** Performance — `transform: translate3d()`, CSS animation.
- **§14:** I18n typography — CJK fallback (Noto Sans SC/JP).
- **§15:** Brand assets — 28px icon, 10px gap, 56px header, asset path.

**2. Content config** — `config/pearl_prime/ticker_phrases.json`
- `schema_version`, `ticker.en` / `runner.en` with the spec phrases; `ticker.zh`/`ja` and `runner.zh`/`ja` as empty arrays.

**3. Starter** — `pearl_prime_web/`
- **index.html:** Header (icon + “Pearl Prime”), runner column, main area, ticker strip; Google Fonts for Inter + Noto Sans SC/JP.
- **styles.css:** Theme variables (`#EAF6FF`, white cards, dark text), 56px header, 28px icon, 10px gap; CSS `translate3d` animations for ticker (50s) and runner (96s); `prefers-reduced-motion` (200s); runner hidden below 768px; font stack with CJK.
- **app.js:** Fetches `config/pearl_prime/ticker_phrases.json`, builds duplicated ticker/runner DOM for seamless loops, fallback data if fetch fails.
- **assets/pearl_prime_icon.png:** Copy of repo icon.
- **config/pearl_prime/ticker_phrases.json:** Copy so the app works when served from `pearl_prime_web/`.

**4. DOCS_INDEX**
- Task table row for “Pearl Prime web app” and a “Pearl Prime web app (document all)” subsection with spec, starter, config, and run instructions.

To run locally: `cd pearl_prime_web && python3 -m http.server 8080`, then open http://localhost:8080.

---

**User**

Weekly brand packet automation

Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself.

To-do's from the plan have already been created. Do not create them again. Mark them as in_progress as you work, starting with the first one. Don't stop until you have completed all the to-dos.

---

**Cursor**

Implementing the weekly brand packet automation plan. Checking existing todos and codebase.


Checking existing release scripts and schema:


Checking config files, workflow, and docs:


Checking DOCS_INDEX for a "Weekly brand packet" subsection and verifying the workflow's dependency check.


Implementing workflow improvements: normalizing week_start to Monday and adding a dependency check for rendered files (artifacts/rendered/<plan_id>/book.txt).


Summary of what’s in place and what was changed:

**Already implemented (unchanged)**  
The plan’s deliverables were already present:

1. **export_brand_packets.py** — Idempotent export, single week key (YYYY-WW), feasibility guard (strict mode, `book.txt` required), CSV/advisory validation, `packet_delivery_report.json` (export section).
2. **upload_brand_packets_r2.py** — R2 upload, sha256 + size_bytes in `download_links.json`, presigned URLs (24–72h), report update.
3. **fetch_brand_packet.sh** — curl + unzip from signed URL.
4. **notify_brand_admins.py** — Per-brand retry (2), `notify_failures.json`, `run_id`/`week_key`, report (notify section); SMTP/Slack from env.
5. **Config** — `config/release/brand_admin_contacts.yaml`, `config/release/brand_packets_r2.yaml` (no secrets in repo).
6. **Schemas** — `schemas/release/brand_packet_manifest_v1.schema.json`, `schemas/release/upload_manifest_csv_v1.schema.json`.
7. **Workflow** — `.github/workflows/weekly-brand-packets.yml` with dependency-check job, export → upload → notify, R2/SMTP from secrets.
8. **Docs** — DOCS_INDEX task row and “Weekly brand packet delivery” copy that link export, upload, notify, fetch, configs, schemas, and workflow.

**Changes made**  
Two updates were made so the workflow matches the plan’s dependency check and week handling:

1. **Normalize `week_start` to Monday**  
   When `week_start` is given as a workflow input, it is now normalized to the Monday of that week before being used. Schedule rows use Monday as `week_start`, so this ensures the dependency check finds the right row and export uses the same week key.

2. **Dependency check for rendered output**  
   The “Dependency check - assembled outputs exist” step now also requires `artifacts/rendered/<plan_id>/book.txt` for each plan path (in addition to the plan file). If any of these are missing, the workflow fails with an explicit list of missing paths, satisfying the plan’s requirement that “all plan files and rendered dirs exist” before export runs.

The 10 hard requirements (idempotency, single week key, strict manifest schema, feasibility guard, checksum+size, signed URL policy, notification resilience, audit trail, secrets boundary, workflow dependency check) are satisfied by the existing scripts plus these workflow updates.

---

**User**

Proposed weekly flow:

Planner creates week schedule (which books per brand).
Pearl Prime pipeline assembles each book package.
Packet exporter builds per-brand zip.
Uploader sends zips to Cloudflare R2.
System generates signed download links (expire in 24–72h).
Notifier sends each brand admin their link + release day.
How admins get it:

Primary: email (and/or Slack DM/webhook) with signed link.
No R2 login needed if using signed links.
Optional later: admin portal login dashboard, but not required for v1.
So yes: brand admins receive a link, download zip to laptop, unzip, then manually upload to Google Play.

Use this build order:

1. **Create packet exporter**
- Script: `/Users/ahjan/phoenix_omega/scripts/release/export_brand_packets.py`
- Input: `artifacts/release_schedule.json` + selected week.
- Output per brand:
  - `/Users/ahjan/phoenix_omega/artifacts/brand_packets/YYYY-WW/<brand_id>/upload_manifest.csv`
  - `book_files/`, `cover/`, `advisory_report.json`, `release_day.txt`
  - zip: `YYYY-WW_<brand_id>_packet.zip`

2. **Create R2 uploader + signed-link generator**
- Script: `/Users/ahjan/phoenix_omega/scripts/release/upload_brand_packets_r2.py`
- Upload each zip to key: `weekly/YYYY-WW/<brand_id>/packet.zip`
- Generate presigned URLs and write:
  - `/Users/ahjan/phoenix_omega/artifacts/brand_packets/YYYY-WW/download_links.json`

3. **Create notifier (email + Slack webhook)**
- Script: `/Users/ahjan/phoenix_omega/scripts/release/notify_brand_admins.py`
- Contacts config:
  - `/Users/ahjan/phoenix_omega/config/release/brand_admin_contacts.yaml`
- Reads `download_links.json`, sends per-brand message with link + `release_day`.

4. **Create admin fetch helper**
- Script: `/Users/ahjan/phoenix_omega/scripts/release/fetch_brand_packet.sh`
- Usage: `fetch_brand_packet.sh <signed_url> [output_dir]`
- Does `curl` + `unzip`.

5. **Automate in GitHub Actions**
- Workflow: `/Users/ahjan/phoenix_omega/.github/workflows/weekly-brand-packets.yml`
- Steps:
  - export packets
  - upload to R2
  - notify admins
- Trigger: `schedule` + `workflow_dispatch`.

6. **Required secrets**
- `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`
- Email creds (SMTP or provider API key)
- Slack webhook URLs (or bot token).

7. **Safety requirements**
- Idempotent reruns for same week.
- Short URL expiry (24–72h).
- Per-brand retry + failure log.
- Output `packet_delivery_report.json` for audit.

If you want, I can implement all 4 scripts + workflow in this repo now.




do this lite-weight and simple:

1. **Brand Admin Portal (login required)**
- Build a small web app (`/admin/packets`) that lists only that admin’s brands and current week packets.
- Auth via **Cloudflare Access** (Google/Microsoft login + MFA).

2. **Access model**
- Keep mapping in config/db: `admin_user -> allowed_brand_ids`.
- On login, portal filters packets by allowed brands only.

3. **Link generation**
- Do **not** store permanent public links.
- When admin clicks “Get Download,” backend mints a short-lived R2 signed URL (e.g. 15 minutes).

4. **Storage**
- Keep zips in R2 at `weekly/YYYY-WW/<brand_id>/packet.zip`.
- Keep packet metadata in `download_index.json` (week, brand, size, checksum, release_day).

5. **Audit + security**
- Log every request/download: user, brand, week, timestamp, IP.
- Enforce MFA, session timeout, and rate limits.
- Optional one-time token links per click.

6. **Automation stays the same**
- Pipeline still exports packet zips and uploads to R2 automatically.
- Difference: notifications point admins to portal (“log in to download”), not direct signed URLs.

If you want, I can draft the exact portal API/routes and data schema next (minimal v1).

## Minimal V1 Portal Spec (Login-required packet downloads)

### 1. Components
1. **Packet builder job** (already planned): exports zips + metadata weekly.
2. **R2 object store**: holds `packet.zip` files.
3. **Admin portal backend**: auth, brand authorization, signed URL minting.
4. **Admin portal UI**: “My Brands” weekly packet table + download button.
5. **Audit log**: every signed-link issuance + download redirect event.

---

## 2. Data Model

### `brand_admin_users`
- `id` (uuid)
- `email` (unique)
- `display_name`
- `status` (`active|disabled`)
- `created_at`

### `brand_admin_grants`
- `id` (uuid)
- `user_id` (fk)
- `brand_id` (string)
- `role` (`admin|viewer`)
- `created_at`

### `weekly_packets`
- `id` (uuid)
- `week_key` (`YYYY-WW`)
- `brand_id`
- `r2_key` (`weekly/YYYY-WW/<brand_id>/packet.zip`)
- `release_day` (`YYYY-MM-DD`)
- `bytes`
- `sha256`
- `status` (`ready|missing|archived`)
- `created_at`

### `packet_access_audit`
- `id` (uuid)
- `user_id`
- `brand_id`
- `week_key`
- `action` (`list|mint_link|download_click`)
- `ip`
- `user_agent`
- `created_at`
- `result` (`ok|denied|error`)

---

## 3. AuthN/AuthZ
1. **AuthN**: Cloudflare Access (OIDC, MFA required).
2. Backend trusts Access headers/JWT and resolves `email -> user`.
3. **AuthZ**: only packets where `brand_id` is in `brand_admin_grants` for that user.

---

## 4. API Routes (backend)

1. `GET /api/me`
- returns user profile + granted brands.

2. `GET /api/packets?week=YYYY-WW`
- returns only packets for user’s brands.
- includes: brand_id, week_key, release_day, size, sha256, status.

3. `POST /api/packets/{week_key}/{brand_id}/signed-url`
- checks grant.
- mints short TTL R2 signed URL (10–15 min).
- returns `{url, expires_at}`.
- writes `packet_access_audit(action=mint_link)`.

4. `GET /api/audit/recent` (admin-only optional)
- recent access events.

---

## 5. UI Routes

1. `/admin/login` (handled by Cloudflare Access)
2. `/admin/packets`
- week selector (default current)
- table per brand:
  - Brand
  - Release Day
  - File Size
  - SHA256
  - Status
  - `Get Download Link` button
3. button calls signed-url endpoint and then starts download.

---

## 6. Weekly Automation Integration
1. Export zips.
2. Upload zips to R2.
3. Upsert `weekly_packets` rows from upload output.
4. Notify admins: “Packet ready, log into portal” (no direct links).

---

## 7. Security Defaults
1. Signed URLs expire in 15 min.
2. No public bucket ACL.
3. Rate-limit link mint endpoint.
4. Log denied attempts.
5. Disable users by flipping `status`.

---

## 8. File/Code Layout Proposal

- `/Users/ahjan/phoenix_omega/services/admin_portal/`
  - `app.py` (or `main.ts`)
  - `auth.py`
  - `routes_packets.py`
  - `models.py`
- `/Users/ahjan/phoenix_omega/config/release/brand_admin_contacts.yaml` (optional bootstrap)
- `/Users/ahjan/phoenix_omega/scripts/release/sync_packets_to_portal_index.py`

---

If you want, next step I can generate the exact OpenAPI spec + SQL schema + starter backend skeleton.

Yes. This is production-grade and well-scoped.

Only add these final guardrails before implementation:

1. **Schema split**
- Keep `brand_packet_manifest_v1.schema.json` for JSON artifacts only.
- For `upload_manifest.csv`, add a separate CSV header contract checker (schema for rows after CSV->JSON transform).

2. **ISO week consistency**
- Derive `YYYY-WW` from `week_start` **after normalizing to Monday** to avoid timezone/week-boundary drift.

3. **Rendered-path rule**
- Define exactly what counts as “required rendered output” (e.g. `artifacts/rendered/<plan_id>/book.txt`), otherwise feasibility checks will be ambiguous.

4. **Partial brand handling**
- Choose policy explicitly:
  - strict mode: any missing file fails whole week (recommended now),
  - permissive mode: skip broken brand and continue.
- You currently imply strict; keep that.

5. **Notification idempotency**
- Include `run_id` and `week_key` in `notify_failures.json` and `packet_delivery_report.json` so reruns are traceable.

6. **Workflow wiring**
- Add a hard pre-step that validates `--candidates-dir` was used upstream; this is your current biggest operational gap.

If you want, I can now turn this into concrete files and implement in the exact order you listed.

for UI: Below is a **clear product description / spec** you can give to designers or developers for the **Pearl Prime web app**.

---

# Pearl Prime — Web App UI & Branding Specification

## 1. Application Name & Branding

The web application will be branded **“Pearl Prime.”**

Brand presentation requirements:

* Display the **pearl_prime_icon.png** icon.
* The icon should appear **to the left of the text “Pearl Prime.”**
* The brand should be placed in the **top navigation bar** of the app.

Example header layout:

```
[pearl_prime_icon.png]  Pearl Prime
```

The brand identity should feel:

* calm
* uplifting
* spiritual
* modern and clean

---

# 2. Visual Design Theme

### Background

Primary background color:

```
Light Blue
```

Suggested tone:

```
#EAF6FF
```

### Accent colors

White should be used for:

* panels
* cards
* UI sections
* menu bars

Example:

```
background: light blue
cards: white
text: dark gray / navy
```

### Design style

The design should feel:

* peaceful
* minimalist
* modern spiritual technology
* readable and uncluttered

---

# 3. Bottom Animated Text Ticker

A **horizontal scrolling ticker** will run across the **bottom of the screen**.

### Animation style

* Similar to a **stock market ticker**
* Text moves **right → left continuously**
* Smooth, constant speed
* Infinite loop

### Languages

The ticker can contain:

* English
* Chinese
* Japanese

Languages may rotate or mix.

### English ticker content

```
Spread wisdom to every heart.
Offer hope to the weary.
Let the truth shine everywhere.
Guide spirits toward freedom.
Carry compassion to the world.
Lift hearts with words.
Awaken the light within all.
Share words of healing.
Open paths to inner peace.
Plant seeds of awakening.
Bring clarity to the confused.
Let wisdom flow to all beings.
```

### Ticker behavior

* Sentences should appear sequentially
* When the final sentence finishes, it loops again
* Text spacing should allow comfortable reading

Example visual behavior:

```
→ Spread wisdom to every heart → Offer hope to the weary → Let the truth shine everywhere →
```

---

# 4. Left Side Vertical Word Runner

A **vertical scrolling message column** will appear on the **left side of the screen**.

### Animation style

* Text moves **bottom → top**
* Continuous smooth scrolling
* Infinite loop

Similar to:

* meditation quotes
* news feed
* vertical message stream

### Message content

```
Books that inspire courage
Books that awaken wisdom
Stories that open hearts
Stories that reveal truth
Teachings that guide the path
Teachings that bring clarity
Exercises that calm the mind
Exercises that restore balance
Practices that nurture peace
Practices that build resilience
Words that uplift the spirit
Words that spark transformation
```

### Display behavior

Each phrase should:

* appear individually
* rise upward
* fade out slightly near the top
* new phrases appear from the bottom

This creates a **continuous vertical flow of inspiration.**

---

# 5. Layout Overview

Example UI structure:

```
-----------------------------------------------------
| Pearl Prime logo + icon                           |
-----------------------------------------------------

| LEFT MESSAGE COLUMN |     MAIN CONTENT AREA       |
|                     |                             |
| Books that inspire  |                             |
| courage             |                             |
|                     |                             |
| Stories that open   |                             |
| hearts              |                             |
|                     |                             |
| (vertical scroll)   |                             |
|                     |                             |
-----------------------------------------------------
| horizontal ticker scrolling messages              |
-----------------------------------------------------
```

---

# 6. Motion & Animation Guidelines

Animations should feel:

* calm
* smooth
* not distracting
* meditative

### Speed suggestions

Horizontal ticker:

```
~40–60 seconds per loop
```

Vertical message column:

```
~1 phrase every 3–5 seconds
```

---

# 7. Typography

Recommended style:

Primary font:

```
Clean Sans Serif
```

Examples:

* Inter
* Open Sans
* Lato

Text tone should be:

* readable
* calm
* elegant

---

# 8. Optional Enhancement (Recommended)

Developers may optionally add:

### language rotation

Ticker alternates between:

```
English
Chinese
Japanese
```

### subtle glow animation

Important words such as:

```
wisdom
peace
awakening
clarity
```

may gently brighten.

---

# 9. Design Goals

The Pearl Prime interface should communicate:

* wisdom
* peace
* compassion
* spiritual guidance

The UI should feel like a **modern digital temple of knowledge**, where teachings flow continuously across the screen.

---

If you want, I can also generate a **developer-ready version** that includes:

* **HTML structure**
* **CSS animation code**
* **React / Next.js layout**
* **ticker animation implementation**

so a developer could build this **in under 1 hour.**

Yes, it’s good as a product brief.

For implementation quality, tighten 6 items:

1. **Accessibility**
- Add reduced motion mode (`prefers-reduced-motion`) to pause/slow both tickers.
- Ensure WCAG contrast on light blue/white.

2. **Mobile behavior**
- Define responsive fallback:
  - hide or collapse left vertical runner on small screens,
  - keep bottom ticker single-line with overflow handling.

3. **Content safety**
- Move ticker/runner phrases to config/JSON so they’re editable without code deploy.

4. **Performance**
- Use CSS transforms (`translate3d`) for animation, avoid JS timers where possible.

5. **I18n typography**
- Define CJK font fallback stack for Chinese/Japanese to avoid ugly rendering.

6. **Brand asset spec**
- Add exact icon size and padding (e.g. 28px icon, 10px gap, 56px header height).

If you want, I can turn this into a developer-ready spec + starter React/CSS files next.

Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself.

To-do's from the plan have already been created. Do not create them again. Mark them as in_progress as you work, starting with the first one. Don't stop until you have completed all the to-dos.

write this to a new .md file on my laptop in: /Users/ahjan/phoenix_omega/salvage/

Stop making changes for now. Do not push, do not reset, do not rebase, do not run git gc, and do not delete any temp/output/session files.

I need a precise salvage report from your current session. Do not recreate work yet unless I explicitly ask. First preserve anything fragile, then report it.

If you have anything in a temp folder, VM session folder, notebook output, Cowork outputs, /tmp, /sessions, Downloads, Desktop, or another repo that is not safely in git, copy it now to a stable location and keep the original too.

Reply with one block per item using this exact format:

ITEM: <short name>
PATH: <exact absolute path>
REPO: <exact repo path or NONE>
BUCKET: <reachable commit | orphan commit | uncommitted working tree | temp/output folder | other repo>
COMMIT: <exact commit hash or NONE>
BRANCH: <exact branch name or NONE>
STATUS: <present now | already lost | unsure>
SESSION_ALIVE: <yes | no>
REPRODUCIBLE: <yes | no | unsure>
PRESERVE_NOW: <yes | no>
DUPLICATE_SUSPECTED: <yes | no | unsure>
SHASUM: <sha if file exists, otherwise NONE>
NOTES: <one sentence only>

Also answer these 4 questions at the end:

1. What exact work did you produce that is not already safely pushed to GitHub?
2. What exact work exists only in a temp/output/session folder or other repo?
3. What exact work is committed locally but not on any branch?
4. What exact work is still uncommitted in your working tree?

Rules:
- If something is already in git, do not redo it. Report the commit hash.
- If something is only in a fragile location, preserve it now before replying.
- If you think someone else may already have the same work, still report it, but do not recreate it.
- If you are unsure, say unsure rather than guessing.
- Do not summarize. List every file, folder, commit, or output separately.

---

**Cursor**

Writing the plan to `salvage/` and gathering git state for the salvage report.



---

**User**

stuck?

---

**Cursor**

Not stuck on anything that blocks you.

**What actually finished**
- The plan was written to `/Users/ahjan/phoenix_omega/salvage/weekly_brand_packet_automation_plan.md` (that file exists).
- Its SHA-256 was computed successfully: `0bd0888cefb8e9d888db7a13454f816c793c7bc27c51c0de47acabf731599b2c`.

**What looked “stuck”**
- `git status` in this environment was very slow or didn’t return within the tool timeout (common on huge repos or heavy `.git` I/O). That doesn’t mean your repo is broken; it means the automated check didn’t finish here.

**What you can do locally (fast sanity)**
```bash
cd /Users/ahjan/phoenix_omega && git status --short
```

No push, reset, rebase, gc, or deletes were run per your earlier instructions. If you want a fresh salvage-style report with exact `COMMIT` / uncommitted file list, run `git status` and `git rev-parse HEAD` on your machine and paste the output.

