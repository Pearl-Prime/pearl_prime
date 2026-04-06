# Brand Admin Platform Onboarding Research

> **Source of truth for the onboarding guide builder.**
> Research date: 2026-04-05 | Covers 12 platforms across publishing, social, and infrastructure.
> All flows verified against current (2025-2026) signup processes.

---

## Table of Contents

1. [STEP 1: Google Account](#step-1-google-account)
2. [STEP 2: YouTube Channel](#step-2-youtube-channel)
3. [STEP 3: Amazon KDP Account](#step-3-amazon-kdp-account)
4. [STEP 4: Google Play Books Partner Center](#step-4-google-play-books-partner-center)
5. [STEP 5: Apple Books for Authors](#step-5-apple-books-for-authors)
6. [STEP 6: Kobo Writing Life](#step-6-kobo-writing-life)
7. [STEP 7: TikTok Business Account](#step-7-tiktok-business-account)
8. [STEP 8: Instagram Business Account](#step-8-instagram-business-account)
9. [STEP 9: Webtoon Canvas](#step-9-webtoon-canvas)
10. [STEP 10: LINE Official Account](#step-10-line-official-account)
11. [STEP 11: Draft2Digital / PublishDrive](#step-11-draft2digital--publishdrive)
12. [STEP 12: Domain & Email (Cloudflare + GHL)](#step-12-domain--email-cloudflare--ghl)
13. [Pre-Fill Templates (All Platforms)](#pre-fill-templates-all-platforms)
14. [Per-Lane Differences Summary](#per-lane-differences-summary)

---

## STEP 1: Google Account

**Foundation for YouTube, Google Play Books, and Google-linked services.**

### Exact Signup URL

- **Primary:** `https://accounts.google.com/signup`
- **Gmail-specific:** `https://accounts.google.com/signup?service=mail`
- **Business/Workspace:** `https://workspace.google.com/` (paid; NOT needed for brand admin MVP)

### Step-by-Step Flow

1. Navigate to `accounts.google.com/signup`
2. Select "For my personal use" or "For work or my business" (select **personal** for brand admin)
3. Enter **First name** and **Last name**
4. Click **Next**
5. Enter **Date of birth** (month, day, year) and **Gender**
6. Click **Next**
7. Google suggests Gmail addresses OR select "Create your own Gmail address"
8. Enter desired username (this becomes `{username}@gmail.com`) -- **permanent, cannot be changed later**
9. Click **Next**
10. Create a **password** (min 8 chars, mix of letters/numbers/symbols recommended)
11. Confirm password
12. Click **Next**
13. **Phone number** -- may be required for verification (sometimes optional depending on region/device)
14. **Recovery email** -- optional but strongly recommended
15. Click **Next**
16. Review account summary
17. Read and accept **Google Terms of Service** and **Privacy Policy**
18. Click **I agree**
19. Account created -- redirected to Gmail or Google homepage

### Required Fields

| Field | Required | Notes |
|-------|----------|-------|
| First name | Yes | Legal or brand name |
| Last name | Yes | Legal or brand name |
| Username | Yes | Becomes Gmail address; permanent |
| Password | Yes | Min 8 characters |
| Date of birth | Yes | Must be 13+ years old |
| Gender | Yes | Can select "Rather not say" |
| Phone number | Conditional | Sometimes required for verification |
| Recovery email | No | Strongly recommended |

### What WE Pre-Fill

- **First name:** `{brand_display_name}` (e.g., "Zenith Yoga")
- **Last name:** "Media" or "Publishing" (e.g., "Zenith Yoga Media")
- **Suggested username:** `{brand_slug}media` or `{brand_slug}publishing` (e.g., `zenithyogamedia@gmail.com`)
- **Recovery email:** brand admin's personal email (provided during onboarding intake)

### 2FA Setup Recommendation

After account creation, immediately:
1. Go to `myaccount.google.com/security`
2. Click **2-Step Verification** > **Get started**
3. Enter phone number for SMS codes
4. Verify with code
5. **Strongly recommend:** Add Google Authenticator app as backup
6. Generate and store **backup codes** (print or save securely)

### Time to Complete

- Account creation: **3-5 minutes**
- 2FA setup: **5 minutes**
- Total: **8-10 minutes**

### Approval Wait Time

- **Instant** -- account is active immediately

### Common Mistakes

- Choosing a username that is already taken (have 3-4 backup options ready)
- Using a personal name instead of brand name
- Skipping 2FA (critical for channel security)
- Forgetting to note down the password securely
- Using a phone number already linked to 4+ Google accounts (Google may block)

### Per-Lane Differences

| Lane | Difference |
|------|------------|
| US | Standard flow; phone verification sometimes skipped |
| JP | Same flow; Japanese locale option available at signup; phone +81 prefix |
| KR | Same flow; Korean locale; phone +82 prefix |
| EU | GDPR consent screen is more detailed; additional data processing acknowledgment |

---

## STEP 2: YouTube Channel

**Requires a Google Account (Step 1).**

### Exact Signup URL

- **YouTube Studio:** `https://studio.youtube.com`
- **Channel creation:** `https://www.youtube.com/channel_switcher` (to create a brand channel)
- **Verify channel:** `https://www.youtube.com/verify`

### Step-by-Step Flow

#### Option A: Personal Channel (simpler, tied to Google Account name)
1. Sign in to YouTube with the Google Account from Step 1
2. Click profile icon (top right) > **Create a channel**
3. YouTube auto-creates a channel using your Google Account name
4. Channel is live immediately

#### Option B: Brand Channel (recommended for brands)
1. Sign in to YouTube
2. Go to `https://www.youtube.com/channel_switcher`
3. Click **Create a new channel**
4. Enter **Brand Account name** (this is the channel name)
5. Click **Create**
6. Channel is created under a Brand Account (can have multiple managers)

#### Channel Customization (both options)
1. Go to YouTube Studio (`studio.youtube.com`)
2. Click **Customization** in left sidebar
3. **Layout tab:**
   - Set channel trailer (for non-subscribers)
   - Set featured video (for returning subscribers)
4. **Branding tab:**
   - Upload **Profile picture** (800x800px, JPG/PNG, <6MB, displayed as circle)
   - Upload **Banner image** (2560x1440px, safe zone 1546x423px center, <6MB)
   - Upload **Video watermark** (150x150px, PNG, <1MB)
5. **Basic info tab:**
   - **Channel name** (editable)
   - **Handle** (@handle) -- unique, like a username
   - **Description** (up to 1000 chars; first 100 chars show in search)
   - **Channel URL** (auto-generated; custom URL after 100 subs)
   - **Links** (up to 5 external links: website, social, etc.)
   - **Contact info** (email for business inquiries)
   - **Language** and **Country**
6. Go to **Settings** > **Channel** > **Keywords** (add channel-level keywords)
7. Go to **Settings** > **Upload defaults**:
   - Default **title prefix**
   - Default **description template**
   - Default **tags**
   - Default **visibility** (public/unlisted/private)
   - Default **language**
   - Default **category**
   - Default **comments** setting

#### Channel Verification
1. Go to `https://www.youtube.com/verify`
2. Enter phone number
3. Receive SMS code
4. Enter code
5. Channel verified -- unlocks: custom thumbnails, videos >15min, live streaming, external links in descriptions

### Required Fields

| Field | Required | Specs |
|-------|----------|-------|
| Channel name | Yes | Max 100 chars |
| Handle (@) | Yes | 3-30 chars, letters/numbers/periods/hyphens/underscores |
| Profile picture | Recommended | 800x800px, JPG/PNG, <6MB |
| Banner image | Recommended | 2560x1440px (safe zone 1546x423px), <6MB |
| Description | Recommended | Up to 1000 chars |
| Country | Yes (for monetization) | Select from dropdown |
| Contact email | Recommended | For business inquiries |
| Category | Per video | Education, Entertainment, etc. |

### What WE Pre-Fill

- **Channel name:** `{brand_display_name}` (e.g., "Zenith Yoga")
- **Handle:** `@{brand_slug}` (e.g., `@zenithyoga`)
- **Description template:**
  ```
  Welcome to {brand_display_name}! {brand_focus_sentence}

  Led by {teacher_name}, we share {content_type} rooted in {tradition}.

  New videos every {upload_schedule}.

  {hashtag_1} {hashtag_2} {hashtag_3}
  ```
- **Default tags:** from KEYWORD_TEMPLATES (e.g., `yoga, meditation, mindfulness, {tradition}, {teacher_name}`)
- **Links:** brand website, Instagram, TikTok
- **Contact email:** the Gmail from Step 1
- **Category:** "Education" (default for most lanes) or "Entertainment" for manga/creative
- **Country:** based on lane (US, JP, KR, etc.)
- **Default upload description template:**
  ```
  {video_title}

  In this video, {teacher_name} from {brand_display_name} shares {topic_summary}.

  Subscribe for more {content_type}: {channel_url}
  Follow us: {instagram_url} | {tiktok_url}

  #shorts #{brand_slug} #{topic_tag}
  ```

### Monetization Requirements (YPP - YouTube Partner Program)

#### Tier 1: Fan Funding (entry-level)
- 500+ subscribers
- 3 public videos uploaded in last 90 days
- EITHER 3,000 watch hours in past 12 months OR 3 million Shorts views in 90 days
- Unlocks: Channel memberships, Super Chats, YouTube Shopping (NO ad revenue)

#### Tier 2: Full YPP (ad revenue)
- 1,000+ subscribers
- EITHER 4,000 public watch hours in past 12 months OR 10 million Shorts views in 90 days
- Linked Google AdSense account
- 2-Step Verification enabled
- Must reside in a supported YPP country
- Unlocks: Pre-roll ads, mid-rolls, overlays, display ads, Premium revenue

**Important notes:**
- Shorts watch time does NOT count toward 4,000 watch hours
- YouTube is increasingly strict on AI-generated content (2026 crackdown on AI scripts + stock footage)
- Must disclose AI/synthetic content via YouTube Studio altered content setting

### Time to Complete

- Channel creation: **2-3 minutes**
- Full customization (branding, description, defaults): **15-20 minutes**
- Channel verification: **2 minutes**
- Total: **20-25 minutes**

### Approval Wait Time

- **Instant** -- channel is live immediately
- Monetization review: **1-4 weeks** after meeting thresholds

### Common Mistakes

- Creating a personal channel instead of a Brand Account channel
- Not verifying the channel (limits features significantly)
- Banner image with text/logos outside the 1546x423px safe zone (gets cropped on mobile)
- Not setting upload defaults (wastes time per video)
- Ignoring the Handle -- @handles are first-come-first-served
- Description too short (missing keywords for discoverability)

### Per-Lane Differences

| Lane | Difference |
|------|------------|
| US | Standard YPP; AdSense in USD |
| JP | YPP available; AdSense in JPY; Japanese description recommended for JP audience |
| KR | YPP available; AdSense in KRW; Korean metadata for KR audience |
| EU | YPP available; VAT considerations for ad revenue; GDPR-compliant descriptions |

---

## STEP 3: Amazon KDP Account

**Primary eBook and print-on-demand publishing platform.**

### Exact Signup URL

- **KDP Portal:** `https://kdp.amazon.com`
- **Direct signup:** `https://kdp.amazon.com/signup`
- **Help page:** `https://kdp.amazon.com/en_US/help/topic/G200620010`

### Step-by-Step Flow

1. Navigate to `https://kdp.amazon.com`
2. Click **Sign up** (or sign in with existing Amazon account)
3. If no Amazon account, create one:
   a. Enter **Name**
   b. Enter **Email address**
   c. Create **Password**
   d. Verify email with code
4. After sign-in, you land on KDP Dashboard
5. Click **Update** next to incomplete account steps (yellow banner)

#### Author/Publisher Information
6. Navigate to **Account** > **Author/Publisher Information**
7. Select **Business type**: Individual or Corporation/Company
8. Enter **Legal name** (must match tax documents)
9. Enter **Mailing address** (street, city, state/province, ZIP, country)
10. Enter **Phone number**

#### Tax Information (REQUIRED before receiving royalties)
11. Navigate to **Account** > **Tax Information**
12. Click **Complete Tax Information**
13. Begin the **Tax Interview**:
    - Question 1: "Are you a U.S. person?" (Yes/No)
    - **If US person:**
      - Select Individual or Business
      - Enter **Legal name**
      - Enter **SSN** (Social Security Number) or **EIN** (Employer Identification Number)
      - Confirm **Address**
      - Sign electronically (W-9 form equivalent)
    - **If Non-US person:**
      - Select Individual or Business
      - Enter **Legal name**
      - Select **Country of citizenship**
      - Enter **Foreign TIN** (Tax Identification Number) or check "I don't have a TIN"
      - Claim **tax treaty benefits** if applicable (reduces withholding from 30% to lower rate)
      - Confirm **Address**
      - Sign electronically (W-8BEN form equivalent)
14. Submit tax interview -- Amazon validates immediately

#### Payment Information (Bank Account)
15. Navigate to **Account** > **Payment Information**
16. Add bank account for EACH marketplace where you want to receive royalties:
    - **Amazon.com (US):** US bank account (routing + account number)
    - **Amazon.co.uk:** UK bank account (sort code + account number)
    - **Amazon.co.jp:** JP bank account (bank code + branch code + account number)
    - **Amazon.de / .fr / .it / .es:** EU bank account (IBAN + SWIFT/BIC)
    - Or use **Payoneer/Wise** for multi-currency receiving
17. Enter **Account holder name** (must match bank records)
18. Enter **Bank name**
19. Enter **Routing number** (US) or equivalent
20. Enter **Account number**
21. Confirm details

### Required Fields Summary

| Field | Required | Notes |
|-------|----------|-------|
| Amazon account (email + password) | Yes | Can use existing Amazon account |
| Legal name | Yes | Must match tax documents |
| Business type | Yes | Individual or Corporation |
| Mailing address | Yes | Full postal address |
| Phone number | Yes | For verification |
| Tax information (W-9 or W-8BEN) | Yes | Required before first royalty payment |
| SSN/EIN/TIN | Yes | Based on country |
| Bank account | Yes | Per marketplace; can add later |

### What WE Pre-Fill

- **Publisher name:** `{brand_display_name} Publishing` or `{brand_display_name} Media`
- **Default categories:** mapped from brand topics (e.g., yoga -> Health & Fitness > Yoga)
- **Default keywords per book:** from KEYWORD_TEMPLATES (up to 7 keywords per book on KDP)
- **Description template per book:**
  ```
  Discover {book_topic} with {teacher_name} from {brand_display_name}.

  This {book_type} covers {key_topics_list}.

  Perfect for {target_audience}.

  Published by {brand_display_name} Publishing.
  ```
- **Author name:** `{teacher_name}` or `{pen_name}`
- **Series name template:** `{brand_display_name} {series_theme} Series`

### AI Disclosure Requirements (Critical for 2025-2026)

Amazon KDP requires disclosure during book setup:
- **AI-generated content:** Text, images, or translations created by AI tools (even if heavily edited afterward) -- MUST check the AI disclosure checkbox
- **AI-assisted content:** Using AI for grammar checks, brainstorming, outlines -- does NOT require disclosure
- **Consequences of non-disclosure:** Book removal from sale, account suspension
- **Visibility:** AI disclosure is NOT shown to buyers (internal to Amazon only)
- **Enforcement:** Amazon uses automated detection + human review; significantly ramped up in 2025-2026
- **Our recommendation:** ALWAYS disclose if any AI tools were used in content generation; err on the side of caution

### Time to Complete

- Account creation: **5 minutes**
- Author/Publisher info: **5 minutes**
- Tax interview: **10-15 minutes** (have SSN/TIN ready)
- Bank setup: **5-10 minutes** (per marketplace)
- Total: **25-35 minutes**

### Approval Wait Time

- **Account creation:** Instant
- **Tax interview validation:** Instant to 24 hours
- **First book review:** 24-72 hours (can take longer for new accounts)

### Common Mistakes

- Legal name not matching tax documents exactly (causes payment delays)
- Skipping the tax interview (cannot receive royalties until completed)
- Bank account holder name mismatch (payment deposits fail)
- Not adding bank accounts for all target marketplaces (royalties accumulate but cannot be paid out)
- Using personal Amazon account instead of a dedicated brand account
- Forgetting AI disclosure (increasingly enforced)
- Setting book price too low (minimum $0.99 for 35% royalty, $2.99 for 70% royalty)

### Per-Lane Differences

| Lane | Difference |
|------|------------|
| US | W-9 form; SSN or EIN; royalties in USD; primary marketplace |
| JP | W-8BEN form; Japanese TIN; Amazon.co.jp marketplace; royalties in JPY |
| KR | W-8BEN form; Korean TIN; no dedicated Korean KDP marketplace (use .com) |
| EU | W-8BEN form; EU TIN; multiple marketplaces (.de, .fr, .it, .es, .nl); IBAN required |

---

## STEP 4: Google Play Books Partner Center

**Google's eBook marketplace. Smaller market share but important for "wide" distribution.**

### Exact Signup URL

- **Partner Center:** `https://play.google.com/books/publish/`
- **Help:** `https://support.google.com/books/partner/answer/4492574`

### Step-by-Step Flow

1. Navigate to `https://play.google.com/books/publish/`
2. Sign in with the Google Account from Step 1
3. Click **Get started** or **Create account**
4. Enter **Account details:**
   - Publisher/imprint name
   - Contact name
   - Contact email
   - Phone number
5. Accept the **Google Play Books Partner Agreement**
6. Click **Create account**
7. Dashboard loads -- account is created but not yet configured for sales

#### Configure for Sales
8. Navigate to **Payment Center** (left sidebar or Settings)
9. Enter **Tax information** (varies by country)
10. Enter **Bank account details** for royalty payments
11. Set **default pricing** (currency, territory pricing)

#### Upload First Book
12. Navigate to **Book Catalog** > **Add Book**
13. Enter book metadata:
    - Title
    - Subtitle
    - Author(s)
    - Description
    - ISBN (recommended but not required for self-publishers)
    - Publisher name
    - Publication date
    - Language
    - Page count
    - Categories (BISAC codes)
14. Upload content files:
    - **EPUB** (preferred; supports 2.0.1, 3.0.1, 3.3)
    - **PDF** (alternative; recommended to provide both)
    - **Cover image** (JPEG or PNG, min 300 DPI, recommended 2560x1600px)
15. Set **pricing** per territory
16. Set **distribution territories**
17. Click **Publish**

### Required Fields

| Field | Required | Notes |
|-------|----------|-------|
| Google Account | Yes | From Step 1 |
| Publisher/imprint name | Yes | Brand name |
| Contact information | Yes | Name, email, phone |
| Tax information | Yes | For sales |
| Bank account | Yes | For royalty payments |
| Book title | Yes | Per book |
| Author name | Yes | Per book |
| Content file (EPUB or PDF) | Yes | EPUB preferred |
| Cover image | Yes | Min 300 DPI |
| Pricing | Yes | Per territory |

### Content Format Requirements

- **EPUB:** Versions 2.0.1, 3.0.1, 3.3 accepted (3.3 preferred)
- **PDF:** Accepted as alternative
- **Both formats recommended** for maximum reader compatibility
- **Minimum:** 4 pages
- **Max file size:** 2 GB per file
- **Cover:** JPEG or PNG, minimum 300 DPI, recommended 2560x1600px

### What WE Pre-Fill

- **Publisher name:** `{brand_display_name} Publishing`
- **Default description template:** Same as KDP template
- **Categories:** Mapped from brand topics to BISAC codes
- **Default territories:** Based on lane (US = worldwide English; JP = Japan + worldwide)
- **Contact email:** Gmail from Step 1

### Time to Complete

- Account creation: **5 minutes**
- Payment/tax setup: **10-15 minutes**
- First book upload: **15-20 minutes**
- Total: **30-40 minutes**

### Approval Wait Time

- **Account creation:** Instant
- **Seller signup eligibility:** Must be in a supported country (see Google's list)
- **Book review:** 1-5 business days

### Common Mistakes

- Not being in a supported seller country (check list first)
- Uploading only PDF without EPUB (limits reader experience)
- Cover image resolution too low (below 300 DPI)
- Missing pricing for key territories
- Not configuring tax information (blocks payments)

### Per-Lane Differences

| Lane | Difference |
|------|------------|
| US | Full support; seller signup available |
| JP | Seller signup supported; JPY pricing |
| KR | Check supported countries list (may need aggregator) |
| EU | Supported; EU VAT handling; DSA compliance |

---

## STEP 5: Apple Books for Authors

**Apple's bookstore. Second-largest eBook marketplace after Amazon.**

### Exact Signup URL

- **Apple Books for Authors:** `https://authors.apple.com`
- **iTunes Connect:** `https://itunesconnect.apple.com` (redirects to App Store Connect)
- **EPUB Upload portal:** `https://authors.apple.com/epub-upload`
- **Account creation help:** `https://authors.apple.com/support/3967-create-itunes-connect-account`

### Step-by-Step Flow

1. Navigate to `https://authors.apple.com`
2. Click **Get started** or **Publish your book**
3. Sign in with **Apple Account** (or create one)

#### Create Apple Account (if needed)
4. Go to `https://appleid.apple.com/account`
5. Enter: Name, Country, Date of birth, Email (becomes Apple ID), Password
6. Verify email and phone number
7. **Enable Two-Factor Authentication** (required for iTunes Connect)
8. **Add a valid credit card** to the Apple Account (required for iTunes Connect even though it is free to publish)

#### iTunes Connect Signup
9. Go to `https://itunesconnect.apple.com`
10. Sign in with Apple Account
11. Select **Publisher Type:**
    - **Individual** -- for sole proprietors / personal brands
    - **Organization** -- for registered companies
12. Enter **Legal entity name** (must be your legal name; can add DBA later)
13. Enter **Contact information** (address, phone, email)
14. Apple sends a **verification email** -- click the link and sign in
15. Account under review -- Apple manually reviews

#### Banking and Tax Setup
16. Once approved, go to **Business** section in iTunes Connect
17. Enter **Bank account details** for royalty payments
18. Complete **Tax forms:**
    - US publishers: W-9
    - Non-US publishers: W-8BEN
19. **EU DSA disclosure:** Must disclose whether you are a "trader" under EU Digital Services Act

#### Publishing a Book
20. Go to `https://authors.apple.com/epub-upload`
21. Upload **EPUB file** (must be valid EPUB 2.0 or 3.0)
22. Enter metadata:
    - Title, Subtitle
    - Author name
    - Description
    - Categories
    - Language
    - Publication date
    - ISBN (optional but recommended)
    - Cover image
23. Set **pricing** by territory
24. Set **distribution territories**
25. Submit for review

### Required Fields

| Field | Required | Notes |
|-------|----------|-------|
| Apple Account | Yes | With 2FA enabled |
| Credit card on file | Yes | Required for iTunes Connect even though publishing is free |
| Legal entity name | Yes | Individual or organization |
| Publisher type | Yes | Individual or Organization |
| Contact info | Yes | Address, phone, email |
| Tax forms | Yes | W-9 (US) or W-8BEN (non-US) |
| Bank account | Yes | For royalties |
| Book title | Yes | Per book |
| EPUB file | Yes | Valid EPUB format |
| Cover image | Yes | High resolution |

### What WE Pre-Fill

- **Publisher name:** `{brand_display_name} Publishing`
- **Author name:** `{teacher_name}`
- **Categories:** Mapped from brand topics to Apple Books categories
- **Description:** Same template as KDP
- **Territories:** Based on lane

### Time to Complete

- Apple Account creation: **5 minutes**
- iTunes Connect signup: **10 minutes**
- Banking/tax setup: **10-15 minutes**
- First book upload: **15-20 minutes**
- Total: **40-50 minutes**

### Approval Wait Time

- **Apple Account:** Instant
- **iTunes Connect approval:** **1-5 business days** (manual review by Apple)
- **Book review:** **1-3 business days** per book

### Common Mistakes

- No credit card on Apple Account (iTunes Connect signup will fail)
- 2FA not enabled (iTunes Connect requires it)
- Using DBA name during signup instead of legal name (account rejected; add DBA after approval)
- EPUB validation errors (Apple is strict; validate EPUB first with epubcheck)
- Missing EU DSA disclosure (required for EU distribution)

### Per-Lane Differences

| Lane | Difference |
|------|------------|
| US | Standard flow; W-9; USD royalties |
| JP | Apple Account with JP region; W-8BEN; JPY royalties; Japanese EPUB supported |
| KR | Apple Account with KR region; W-8BEN; KRW royalties |
| EU | DSA trader disclosure mandatory; W-8BEN; EUR royalties; multiple territory pricing |

---

## STEP 6: Kobo Writing Life

**Rakuten Kobo's self-publishing platform. Strong in Canada, Australia, Europe.**

### Exact Signup URL

- **Kobo Writing Life:** `https://writinglife.kobobooks.com`
- **Help:** `https://kobowritinglife.zendesk.com/hc/en-us/articles/360058975392`

### Step-by-Step Flow

1. Navigate to `https://writinglife.kobobooks.com`
2. Click **Start Writing** or **Sign Up**
3. Review **Terms of Use** and **Privacy Policy**
4. Enter contact information:
   - **First name**
   - **Last name**
   - **Publisher name** (your brand/imprint name)
   - **Email address**
   - **Telephone number**
   - **Mailing address** (full postal address)
5. Create password
6. Submit registration
7. Check email for **confirmation link** -- click to activate account
8. Sign in to KWL dashboard

#### Tax Setup
9. Navigate to account settings
10. Complete **tax interview:**
    - US authors: W-9 (SSN or EIN)
    - Non-US authors: W-8BEN (foreign TIN)
11. Provide relevant tax treaty information for reduced withholding

#### Banking Setup
12. Navigate to **Payment settings**
13. Enter bank account details for royalty payments
14. Minimum payout threshold: **$50 USD** (paid 45 days after month-end)

#### Publish First Book
15. Click **Create New eBook**
16. Enter metadata:
    - **Title** (exact title; no subtitle or series info in this field)
    - **Subtitle** (separate field)
    - **Series name** and **Series number** (if applicable)
    - **Author name** (pre-populated from signup; can add co-authors)
    - **Publisher/Imprint** (pre-populated from signup)
    - **Language**
    - **Description** (HTML supported)
    - **Categories** (BISAC codes, up to 3)
    - **Keywords** (for discoverability)
    - **Publication date**
    - **ISBN** (optional)
17. Upload **EPUB file** (Kobo converts to their format for free)
18. Upload **Cover image** (JPEG or PNG; min 1400x2100px recommended)
19. Set **pricing** per territory (multiple currencies supported)
20. Set **DRM** preference (on or off)
21. Set **distribution territories**
22. Click **Publish**

### Required Metadata Fields Per Book

| Field | Required | Notes |
|-------|----------|-------|
| Title | Yes | Exact title only |
| Subtitle | No | Separate field |
| Series name + number | No | Separate fields |
| Author name | Yes | Pre-populated; can add more |
| Publisher/Imprint | Yes | Pre-populated from signup |
| Language | Yes | Dropdown |
| Description | Yes | HTML supported |
| Categories (BISAC) | Yes | Up to 3 |
| Keywords | Recommended | For search discoverability |
| EPUB file | Yes | Kobo converts for free |
| Cover image | Yes | Min 1400x2100px |
| Price | Yes | Per territory |

### What WE Pre-Fill

- **Publisher name:** `{brand_display_name} Publishing`
- **Author name:** `{teacher_name}`
- **Description:** Same template as KDP/Apple
- **Categories:** Mapped from brand topics to BISAC codes
- **Keywords:** From KEYWORD_TEMPLATES

### Royalty Structure

- **Priced $2.99-$12.99:** 70% royalty
- **Priced $1.99-$2.98 or $12.99+:** 45% royalty
- **Free books:** Can be listed free (promotional tool)
- **No upfront fees** for distribution or conversion
- **Payout:** 45 days after month-end, minimum $50 threshold

### Time to Complete

- Account creation: **5 minutes**
- Tax setup: **10 minutes**
- Banking setup: **5 minutes**
- First book upload: **15-20 minutes**
- Total: **35-40 minutes**

### Approval Wait Time

- **Account creation:** Instant (after email verification)
- **Book review:** **24-72 hours**

### Common Mistakes

- Putting subtitle or series info in the title field (will be rejected)
- Cover image too small (below 1400px wide)
- Not completing tax interview (blocks payments)
- Not reaching $50 minimum for payout (royalties accumulate)

### Per-Lane Differences

| Lane | Difference |
|------|------------|
| US | W-9 form; USD payments |
| JP | W-8BEN; Kobo is operated by Rakuten (Japanese parent company); strong JP presence |
| KR | W-8BEN; limited Korean-language presence |
| EU | W-8BEN; strong in Netherlands, Belgium; EUR payments available |

---

## STEP 7: TikTok Business Account

**Primary short-form video platform. Critical for brand awareness and traffic.**

### Exact Signup URL

- **TikTok (app):** Download from App Store / Google Play
- **TikTok (web):** `https://www.tiktok.com/signup`
- **TikTok Business Center:** `https://business.tiktok.com`
- **TikTok Seller Center (Shop):** `https://seller-us.tiktok.com` (US) or region-specific
- **Business accounts info:** `https://getstarted.tiktok.com/Business-accounts`

### Step-by-Step Flow

#### Create TikTok Account
1. Download TikTok app or go to `tiktok.com/signup`
2. Sign up with **email** or **phone number** (use dedicated brand email from Step 1)
3. Create **password**
4. Enter **date of birth** (must be 18+ for business features)
5. Choose **username** (this is your @handle)
6. Verify email/phone with code

#### Switch to Business Account
7. Open TikTok > go to **Profile** (bottom right)
8. Tap **Menu** (three lines, top right) > **Settings and privacy**
9. Tap **Manage Account** (or **Account**)
10. Tap **Switch to Business Account**
11. Select **Category** that best describes your business:
    - Education
    - Health & Wellness
    - Media & Entertainment
    - Art & Creativity
    - (others available)
12. Confirm switch -- now a Business Account

#### Profile Optimization
13. Edit profile:
    - **Profile photo:** Brand logo (min 200x200px; displayed as circle)
    - **Name:** `{brand_display_name}` (max 30 chars)
    - **Username (@):** `{brand_slug}` (max 24 chars)
    - **Bio:** Up to 80 characters
    - **Website link:** Your brand URL
    - **Email:** Business contact email
    - **Category:** Select appropriate category
14. Enable **Business Suite** tools (analytics, etc.)

#### TikTok Shop Setup (Optional)
15. Go to `https://seller-us.tiktok.com` (or region-specific)
16. Sign up with TikTok Business Account or email
17. Select business type:
    - **Individual** -- personal ID required
    - **Individually-owned Business** -- personal ID + business docs
    - **Corporation** -- business license + representative ID
18. Upload required documents:
    - Government-issued ID (passport, driver's license, or state ID)
    - Business license (for corporations)
    - UBO (Ultimate Beneficial Owner) information for corporations (25%+ ownership)
19. Enter **legal name, date of birth, residential address, SSN/ITIN**
20. Submit **W-9 form** for tax purposes
21. Wait for verification (24-72 hours)
22. Add **bank account** (account name, bank name, account number)
23. Start adding products

### Required Fields

| Field | Required | Notes |
|-------|----------|-------|
| Email or phone | Yes | Use brand email |
| Username (@) | Yes | Max 24 chars; brand slug |
| Name | Yes | Max 30 chars |
| Date of birth | Yes | Must be 18+ |
| Business category | Yes | For business account |
| Profile photo | Recommended | Min 200x200px |
| Bio | Recommended | Max 80 chars |
| Website link | Optional | 1 link allowed |

### TikTok Shop Document Requirements

| Document | Individual | Corporation |
|----------|-----------|-------------|
| Government ID | Required | Required (representative) |
| Business license | Not needed | Required |
| SSN/ITIN | Required | Required (EIN) |
| W-9 form | Required | Required |
| Bank account | Required | Required |
| UBO information | Not needed | Required (25%+ owners) |

### What WE Pre-Fill

- **Name:** `{brand_display_name}` (max 30 chars)
- **Username:** `@{brand_slug}` (max 24 chars)
- **Bio template:**
  ```
  {brand_tagline} | {content_type}
  By {teacher_name} | Link below
  ```
  (max 80 chars total)
- **Category:** "Education" or "Health & Wellness" (based on brand)
- **Website link:** brand landing page URL

### TikTok Shop Availability

Currently available in: US, UK, Ireland, Indonesia, Malaysia, Mexico, Philippines, Singapore, Spain, Thailand, Vietnam.
**NOT available in:** Japan, South Korea, most EU countries (as of 2026).

### Referral Fee

TikTok Shop charges a **6% referral fee** per order for most product categories (2026 rate).

### Time to Complete

- Account creation: **3 minutes**
- Switch to Business: **2 minutes**
- Profile optimization: **10 minutes**
- TikTok Shop setup (if applicable): **15-30 minutes** (depends on document preparation)
- Total (without Shop): **15 minutes**
- Total (with Shop): **30-45 minutes**

### Approval Wait Time

- **Business Account switch:** Instant
- **TikTok Shop verification:** 1-3 business days (some report 19 hours)

### Common Mistakes

- Using personal Facebook/Google login instead of dedicated email (team access issues later)
- Username too long or already taken (prepare alternatives)
- Bio over 80 chars (gets truncated)
- Not switching to Business account (missing analytics and API access)
- Trying to set up TikTok Shop in unsupported country

### Per-Lane Differences

| Lane | Difference |
|------|------------|
| US | Full features; TikTok Shop available; standard flow |
| JP | TikTok available; Shop NOT available (as of 2026); `tiktok.com` works |
| KR | TikTok available; Shop NOT available (as of 2026) |
| EU | TikTok available; Shop available in Ireland, Spain only |

---

## STEP 8: Instagram Business Account

**Meta's visual platform. Essential for brand presence and link-in-bio strategy.**

### Exact Signup URL

- **Instagram (app):** Download from App Store / Google Play
- **Instagram (web):** `https://www.instagram.com/accounts/emailsignup/`
- **Business account info:** `https://help.instagram.com/502981923235522`

### Step-by-Step Flow

#### Create Instagram Account
1. Download Instagram app or go to `instagram.com/accounts/emailsignup/`
2. Enter **Email address** (use brand email from Step 1) or **Phone number**
3. Enter **Full name** (brand name)
4. Create **Username** (this is your @handle)
5. Create **Password**
6. Verify email/phone with code
7. Complete profile basics

#### Convert to Business Account
8. Go to **Profile** > tap **Menu** (three lines) > **Settings and Privacy**
9. Scroll down and tap **For professionals** (or **Account type and tools**)
10. Tap **Switch to Professional Account**
11. Select **Business** (not Creator -- Business gives better analytics for brands)
12. Select **Category** that best describes your business:
    - Education
    - Health/Beauty
    - Media/News/Publishing
    - Art
    - (others available)
13. Review contact info (email, phone, address) -- these appear on your profile
14. **Optional:** Connect to a Facebook Page (recommended for cross-posting and ads)
15. Confirm switch

#### Profile Optimization
16. Edit profile:
    - **Profile photo:** Brand logo (min 320x320px; displayed as 110x110px circle)
    - **Name:** `{brand_display_name}` (max 30 chars; searchable)
    - **Username (@):** `{brand_slug}` (max 30 chars)
    - **Bio:** Up to 150 characters
    - **Website:** Link-in-bio URL (e.g., Linktree, Stan Store, or brand landing page)
    - **Category:** Displayed under name on profile
    - **Contact buttons:** Email, Phone, Address (optional)
    - **Action button:** Book Now, Order Food, Reserve, etc. (optional)
17. Set **content settings:**
    - Posting defaults
    - Close friends list settings
    - Sharing settings

### Required Fields

| Field | Required | Notes |
|-------|----------|-------|
| Email or phone | Yes | Use brand email |
| Full name | Yes | Brand display name; max 30 chars |
| Username (@) | Yes | Brand slug; max 30 chars |
| Password | Yes | Strong password |
| Business category | Yes | For business profile |
| Contact info | At least email | For business profile |
| Profile photo | Recommended | Min 320x320px |
| Bio | Recommended | Max 150 chars |

### What WE Pre-Fill

- **Name:** `{brand_display_name}`
- **Username:** `@{brand_slug}` (same as TikTok if available)
- **Bio template:**
  ```
  {brand_tagline}
  {content_type} by {teacher_name}
  {tradition} | {brand_focus}
  {call_to_action}
  ```
  (max 150 chars total)
- **Category:** "Education" or "Health/Beauty" (based on brand)
- **Website:** Brand landing page URL or link-in-bio service URL
- **Contact email:** Gmail from Step 1

### Link-in-Bio Strategy

Instagram allows only 1 link in bio. Recommended approach:
- **Option A:** Use a link-in-bio service (Linktree, Stan Store, Beacons)
  - URL: `linktr.ee/{brand_slug}` or equivalent
  - Lists all brand links: website, YouTube, books, courses
- **Option B:** Direct to brand landing page (GHL funnel from Step 12)
  - URL: `{brand_domain}` or `{brand_domain}/links`
- **Option C:** Use Instagram's native "Links" feature (add up to 5 links in bio)
  - Available to all accounts as of 2024+

### Content Settings Recommendations

- **Story sharing:** Allow sharing to maximize reach
- **Mentions:** Allow everyone to mention you
- **Tags:** Allow everyone to tag you
- **Comments:** Open (moderate with keyword filters)
- **Reel defaults:** Show on Feed and Profile Grid

### Time to Complete

- Account creation: **3 minutes**
- Convert to Business: **2 minutes**
- Profile optimization: **10 minutes**
- Link-in-bio setup: **10 minutes**
- Total: **25 minutes**

### Approval Wait Time

- **Everything is instant** -- no approval needed
- Facebook Page connection: instant

### Common Mistakes

- Choosing "Creator" instead of "Business" account type (different analytics)
- Username doesn't match other platforms (inconsistent brand)
- Bio too long for the space (plan exact wording)
- Not connecting to Facebook Page (limits ad capabilities)
- Low-resolution profile photo (appears blurry)
- Not setting up link-in-bio (wastes the 1 link slot)

### Per-Lane Differences

| Lane | Difference |
|------|------------|
| US | Full features; Instagram Shopping available; standard flow |
| JP | Full features; Japanese audience prefers LINE but Instagram popular for visual brands |
| KR | Full features; Korean audience uses Instagram heavily |
| EU | Full features; DSA compliance for commercial accounts |

---

## STEP 9: Webtoon Canvas

**Webtoon's open publishing platform for webcomics/manga. Critical for manga lane brands.**

### Exact Signup URL

- **Webtoon main:** `https://www.webtoons.com`
- **Canvas publish:** `https://www.webtoons.com/en/challenge/publish` (or use "Publish" button)
- **Canvas help:** `https://webtooncanvas.zendesk.com/hc/en-us`
- **Creator 101:** `https://www.webtoons.com/en/creators101/webtoon-canvas`

### Step-by-Step Flow

#### Create Webtoon Account
1. Navigate to `https://www.webtoons.com`
2. Click **Sign Up** (or **Log In** > **Sign Up**)
3. Sign up options:
   - **Email** (recommended for brand accounts)
   - Google Account
   - Facebook
   - Apple
   - LINE (popular in JP/Asia)
4. Enter **Email** and **Password**
5. Choose **Nickname** -- this becomes your **Creator Nickname** when you publish
6. Verify email with code
7. Accept Terms of Service

#### Create a Series
8. Navigate to the Webtoon website (NOT the app -- publishing is web-only)
9. Click **Publish** button (top right corner)
10. Click **Create Series**
11. Fill in series information:
    - **Series Title** (the name of your webtoon)
    - **Genre** (select from: Drama, Fantasy, Comedy, Action, Slice of Life, Romance, Superhero, Sci-Fi, Thriller, Supernatural, Mystery, Sports, Historical, Heart-warming, Horror, Informative)
    - **Summary** (description of the series)
    - **Square Thumbnail** (required for discoverability on app/site)
    - **Vertical Thumbnail** (required for certain placements)
12. Set **Upload schedule** (which day(s) of the week)
13. Click **Save**

#### Upload Episodes
14. Within your series, click **Add Episode**
15. Enter **Episode title**
16. Upload **Episode images:**
    - **Format:** JPG, PNG, or GIF
    - **Width:** 800px (max)
    - **Height:** 1280px (max per image panel)
    - System automatically slices/optimizes long vertical images
    - Upload multiple images per episode (they display as a continuous vertical scroll)
17. Upload **Episode thumbnail** (separate from series thumbnail)
18. Click **Save** or **Publish**

#### Creator Profile
19. Creator Profile is **auto-activated** after publishing first series
20. Customize profile with bio, social links, etc.

### Required Fields

| Field | Required | Notes |
|-------|----------|-------|
| Email or social login | Yes | Email recommended for brand accounts |
| Nickname | Yes | Becomes Creator Nickname; choose carefully |
| Series title | Yes | Per series |
| Genre | Yes | Select from list |
| Summary | Yes | Series description |
| Square thumbnail | Yes | For app/site discoverability |
| Vertical thumbnail | Yes | For certain placements |
| Episode images | Yes | 800px width max, JPG/PNG/GIF |
| Episode title | Yes | Per episode |

### Image Specs

| Asset | Dimensions | Format | Notes |
|-------|-----------|--------|-------|
| Episode panels | 800px width (max), 1280px height (max per panel) | JPG, PNG, GIF | Auto-sliced for vertical scroll |
| Square series thumbnail | TBD (check current spec) | JPG, PNG | Used in browse/search |
| Vertical series thumbnail | TBD (check current spec) | JPG, PNG | Used in featured placements |
| Episode thumbnail | TBD (check current spec) | JPG, PNG | Per episode |

### What WE Pre-Fill

- **Nickname:** `{brand_slug}` or `{brand_display_name}`
- **Series title:** `{manga_title}`
- **Genre:** Mapped from brand content (e.g., martial arts -> Action; yoga storytelling -> Slice of Life / Informative)
- **Summary template:**
  ```
  {manga_summary}

  Created by {brand_display_name}.
  New episodes every {upload_day}.
  ```
- **Upload schedule:** Based on brand content calendar

### Monetization (2026 Programs)

- **Super Like Program:** Readers spend "coins" on Super Likes; creators earn revenue share
- **Ad Revenue Sharing Program:** Revenue from ads displayed alongside episodes
- **Patreon Integration:** Link Patreon for subscriber-based support
- **Creator Residency Program:** Launched Q1 2026; selected creators receive stipend + support
- **Payout threshold:** Lowered from $100 to **$25** (January 2026)
- **Eligibility:** Must maintain regular upload schedule and meet minimum readership

### Time to Complete

- Account creation: **3 minutes**
- Series creation: **10 minutes** (with assets ready)
- First episode upload: **10-15 minutes**
- Total: **25-30 minutes** (assuming art assets are prepared)

### Approval Wait Time

- **Account creation:** Instant
- **Series creation:** Instant (auto-publishes)
- **Monetization programs:** Application-based; varies

### Common Mistakes

- Trying to publish from the mobile app (must use website)
- Nickname not matching brand (cannot easily change later)
- Episode images exceeding 800px width (auto-resized, may lose quality)
- Not preparing both square and vertical thumbnails
- Irregular upload schedule (hurts algorithmic recommendation)
- Genre mismatch (affects discoverability)

### Per-Lane Differences

| Lane | Difference |
|------|------------|
| US | English Webtoon platform; Canvas fully available |
| JP | LINE Manga (separate platform, also by LINE/Webtoon parent company); Webtoon Japan available |
| KR | Naver Webtoon (Korean version); dominant platform for Korean webcomics |
| EU | English Webtoon platform; Canvas available; smaller audience |

**Note for JP/KR lanes:** Consider also publishing on LINE Manga (JP) or Naver Webtoon (KR) in addition to Webtoon Canvas (English).

---

## STEP 10: LINE Official Account

**Dominant messaging platform in Japan, Thailand, Taiwan, Indonesia. Essential for JP lane.**

### Exact Signup URL

- **LINE for Business:** `https://www.linebiz.com/` (or region-specific)
- **LINE Official Account Manager:** `https://manager.line.biz`
- **LINE Developers Console:** `https://developers.line.biz/console`
- **Messaging API docs:** `https://developers.line.biz/en/docs/messaging-api/getting-started/`

### Step-by-Step Flow

#### Register Business ID
1. Navigate to `https://www.linebiz.com/` or `https://manager.line.biz`
2. Click **Create a LINE Official Account** (or equivalent)
3. Register for **Business ID** using:
   - **LINE Account** (personal LINE login) -- OR --
   - **Email address** (for those without LINE)
4. If using email: enter email, receive verification code, set password

#### Create LINE Official Account
5. Fill in the **entry form:**
   - **Account name** (your brand name -- displayed to users)
   - **Company/Organization name**
   - **Business category** (select from list)
   - **Sub-category**
   - **Contact email**
   - **Region/Country**
6. Submit form
7. Account created -- access LINE Official Account Manager

#### Set Up Messaging API (for automation)
8. In LINE Official Account Manager, go to **Settings** > **Messaging API**
9. Click **Enable Messaging API**
10. If first time on LINE Developers Console:
    - Register **developer information** (name, email)
    - Create a **developer account**
11. Select or create a **Provider** (organizational entity that manages your LINE channels)
12. A **Messaging API channel** is created automatically
13. Note your **Channel ID**, **Channel Secret**, and generate a **Channel Access Token** (for API integration)

**IMPORTANT (2024+ change):** You can NO longer create Messaging API channels directly from the LINE Developers Console. You must first create a LINE Official Account through the Official Account Manager, then enable the Messaging API from there.

#### Rich Menu Configuration
14. In LINE Official Account Manager, go to **Rich Menu**
15. Create a rich menu (the persistent menu bar at bottom of chat):
    - Design menu layout (up to 6 areas)
    - Upload menu image (2500x1686px or 2500x843px)
    - Set actions for each area (URL link, message, etc.)
16. Set as default rich menu

### Required Fields

| Field | Required | Notes |
|-------|----------|-------|
| Business ID (LINE or email) | Yes | Registration method |
| Account name | Yes | Brand display name |
| Company/Organization | Yes | Legal name |
| Business category | Yes | From dropdown |
| Contact email | Yes | For notifications |
| Region/Country | Yes | Affects features/pricing |

### Pricing (LINE Official Account)

| Plan | Monthly Fee | Free Messages | Additional Messages |
|------|------------|---------------|-------------------|
| Free (Communication) | Free | 200/month | Not available |
| Light | ~$50/month (varies by region) | 5,000/month | ~$0.05/message |
| Standard | ~$150/month (varies by region) | 30,000/month | ~$0.03/message |

**Notes:**
- Pricing varies significantly by country (JP, TH, TW, ID have different price points)
- Free plan is sufficient for starting out
- Broadcast messages count against limits; 1-on-1 chat replies do NOT count
- API messages count against limits

### What WE Pre-Fill

- **Account name:** `{brand_display_name}` (in local language for JP lane)
- **Company name:** `{brand_legal_name}`
- **Category:** Mapped from brand type (Education, Health & Wellness, etc.)
- **Rich menu template:** Pre-designed template with:
  - Latest content
  - Book catalog
  - Course info
  - Social links
  - Contact

### Time to Complete

- Business ID registration: **3 minutes**
- LINE Official Account creation: **5 minutes**
- Messaging API setup: **10 minutes**
- Rich Menu setup: **15-20 minutes**
- Total: **35-40 minutes**

### Approval Wait Time

- **Account creation:** Instant
- **Messaging API:** Instant
- **Premium/Verified account badge:** Application required; 1-4 weeks (requires business verification)

### Common Mistakes

- Trying to create Messaging API channel from Developers Console (must use Official Account Manager first)
- Choosing wrong region (affects pricing and features)
- Not enabling Messaging API (limits automation capabilities)
- Rich menu image wrong dimensions (2500x1686px or 2500x843px only)
- Running out of free messages on Free plan (200/month goes quickly)
- Not planning for upgrade to paid plan as audience grows

### Per-Lane Differences

| Lane | Difference |
|------|------------|
| US | LINE has very small US user base; low priority unless targeting JP diaspora |
| JP | **PRIMARY platform.** 96M+ users in Japan. Essential for JP lane. Japanese interface. JPY pricing. |
| KR | KakaoTalk dominates in Korea (not LINE); skip LINE for KR lane |
| EU | LINE has minimal EU presence; skip for EU lane |

**Recommendation:** LINE Official Account is **JP lane priority only**. For KR lane, investigate KakaoTalk Channel instead.

---

## STEP 11: Draft2Digital / PublishDrive

**Aggregator platforms that distribute to multiple stores from a single upload.**

### Draft2Digital (D2D)

#### Exact Signup URL
- **Main site:** `https://draft2digital.com`
- **Signup:** `https://draft2digital.com/signup`
- **Step-by-step guide:** `https://draft2digital.com/steps/`

#### Step-by-Step Flow
1. Navigate to `https://draft2digital.com`
2. Click **Sign Up Free** (or **Get Started**)
3. Enter:
   - **Name** (legal name)
   - **Pen name** (optional; for publishing)
   - **Email address**
   - **Password**
4. Verify email
5. Complete **Tax documentation:**
   - US: W-9 (SSN or EIN)
   - Non-US: W-8BEN (foreign TIN)
6. Add **Payment method** (bank account or PayPal for royalties)
7. Dashboard ready

#### Publish a Book
8. Click **My Books** > **Add New Book**
9. Upload manuscript (Word, EPUB, or use D2D's formatter)
10. D2D auto-converts to EPUB (free formatting service)
11. Upload cover image
12. Enter metadata:
    - Title, subtitle
    - Author/pen name
    - Description
    - Categories (BISAC)
    - Keywords
    - Language
    - ISBN (optional; D2D provides free ISBN option)
13. Set pricing per retailer/territory
14. Select **distribution channels** (can toggle per-retailer):
    - Apple Books
    - Barnes & Noble (Nook)
    - Kobo
    - Amazon (by invitation only)
    - Tolino (German-language network)
    - Vivlio (French-language)
    - Bibliotheca (libraries)
    - Baker & Taylor (libraries)
    - Hoopla (libraries)
    - OverDrive (libraries)
    - Bookshop.org (as of 2026)
    - Fable (as of 2024)
    - Scribd
    - And more
15. Click **Publish**

#### D2D Distribution Partners (Full List 2026)

**Retailers:**
- Apple Books
- Barnes & Noble (Nook)
- Kobo
- Amazon (invitation only)
- Tolino
- Vivlio
- Scribd
- Bookshop.org (new 2026)
- Fable (2024+)

**Libraries:**
- Bibliotheca
- Baker & Taylor
- Hoopla
- OverDrive

**Print (D2D Print):**
- Amazon (via Ingram)
- Barnes & Noble
- Independent bookstores (via Ingram distribution)

#### D2D Pricing
- **Ebooks:** 10% of retail price (D2D's cut)
- **Print:** Cost varies by trim size and page count (increased February 2026)
- **No upfront fees** for any service
- **Free ISBN** option available
- **Free formatting** (Word to EPUB conversion)
- **Free Universal Book Links** (promotional tool)

### PublishDrive

#### Exact Signup URL
- **Main site:** `https://publishdrive.com`
- **Pricing:** `https://publishdrive.com/pricing.html`

#### Step-by-Step Flow
1. Navigate to `https://publishdrive.com`
2. Click **Start Free** or **Sign Up**
3. Enter name, email, password
4. Choose plan:
   - **Free:** 1 book, 31 channels, ebook only
   - **Starter ($13.99/month annual):** 3 books, 50 channels, ebook + audio + print
   - **Standard ($20.99/month annual):** 6 books, 50 channels
   - **Plus ($41.99/month annual):** 18 books, 50 channels
   - **Custom:** 48+ books
5. Enter payment information (for paid plans)
6. Complete tax documentation
7. Upload books and set distribution

#### PublishDrive Pricing Detail

| Plan | Monthly (Annual) | Monthly (Monthly) | Books | Channels | Commission |
|------|-----------------|-------------------|-------|----------|------------|
| Free | $0 | $0 | 1 | 31 | 0% |
| Starter | $13.99 | $16.99 | 3 | 50 | 0% |
| Standard | $20.99 | $24.99 | 6 | 50 | 0% |
| Plus | $41.99 | $49.99 | 18 | 50 | 0% |
| Custom | Contact | Contact | 48+ | 50 | 0% |

- **0% commission** on all plans (you keep 100% of net royalties)
- Distributes to **400+ retailers and 240K+ libraries** in 100+ countries
- 30-day money-back guarantee on paid plans

### Which Aggregator to Choose?

| Factor | Draft2Digital | PublishDrive |
|--------|--------------|-------------|
| Pricing model | 10% commission | Flat subscription |
| Best for | Small catalog (<10 books) | Larger catalog (10+ books) |
| Free tier | Unlimited books, 10% cut | 1 book, 31 channels |
| Amazon access | Invitation only | Available |
| Library distribution | Extensive | Extensive |
| Formatting | Free DOCX-to-EPUB | No free formatting |
| Print | D2D Print available | Via partners |
| Free ISBN | Yes | Yes |

**Our recommendation:** Start with **Draft2Digital** (free, no subscription) for initial catalog. Switch to **PublishDrive** when catalog exceeds ~10 titles and the math favors flat subscription over 10% commission.

### What WE Pre-Fill (Both Platforms)

- **Author/Pen name:** `{teacher_name}` or `{pen_name}`
- **Publisher name:** `{brand_display_name} Publishing`
- **Description:** Same template as KDP
- **Categories:** Mapped from brand topics
- **Keywords:** From KEYWORD_TEMPLATES
- **Distribution channels:** All available (widest distribution)

### Time to Complete

- D2D signup: **10 minutes**
- PublishDrive signup: **10 minutes**
- Tax documentation: **10 minutes** each
- First book upload: **15-20 minutes** each
- Total per platform: **35-40 minutes**

### Approval Wait Time

- **D2D:** Instant account; books go live in 1-3 days per retailer
- **PublishDrive:** Instant account; books go live in 1-7 days per retailer

---

## STEP 12: Domain & Email (Cloudflare + GHL)

**Brand infrastructure: custom domain, professional email, and marketing funnels.**

### Component A: Domain Registration (Cloudflare)

#### Exact URLs
- **Cloudflare Registrar:** `https://dash.cloudflare.com` > Domain Registration
- **Pricing:** `https://www.cloudflare.com/products/registrar/`

#### Step-by-Step Flow
1. Create Cloudflare account at `https://dash.cloudflare.com/sign-up`
2. Enter **Email** and **Password**
3. Verify email
4. Click **Domain Registration** (left sidebar) > **Register Domain**
5. Search for desired domain: `{brand_slug}.com` (or .co, .io, etc.)
6. Select domain and add to cart
7. Enter **registrant information:**
   - Name
   - Organization (optional)
   - Address
   - Phone
   - Email
8. Pay for domain (Cloudflare charges at-cost, no markup)
9. Domain registered and active on Cloudflare DNS

### Component B: Brand Email Setup

#### Option 1: Cloudflare Email Routing (Free, for forwarding)
1. In Cloudflare Dashboard, select your domain
2. Go to **Email** > **Email Routing**
3. Click **Get started**
4. Add **Custom address:** e.g., `hello@{brand_domain}`, `support@{brand_domain}`
5. Set **Destination address:** the Gmail from Step 1
6. Verify destination email
7. Emails to `hello@{brand_domain}` now forward to Gmail

#### Option 2: Google Workspace (Paid, for full branded email)
1. Go to `https://workspace.google.com`
2. Sign up with domain name
3. Choose plan ($6-$18/user/month)
4. Verify domain ownership (add TXT record to Cloudflare DNS)
5. Create mailboxes: `{name}@{brand_domain}`
6. Full send/receive with brand domain

#### Option 3: Zoho Mail (Free tier available)
1. Go to `https://www.zoho.com/mail/`
2. Sign up with domain
3. Verify domain
4. Free tier: 5 users, 5GB/user
5. Add MX records to Cloudflare DNS

### Component C: GoHighLevel (GHL) Funnel Setup

#### Exact URLs
- **GHL:** `https://www.gohighlevel.com`
- **Signup:** `https://www.gohighlevel.com/pricing` (14-day free trial)

#### Step-by-Step Flow
1. Sign up for GHL at `https://www.gohighlevel.com`
2. Choose plan:
   - **Starter:** $97/month (1 sub-account)
   - **Unlimited:** $297/month (unlimited sub-accounts)
   - **SaaS Pro:** $497/month (full white-label)
3. Start 14-day free trial
4. Complete onboarding wizard

#### Connect Domain to GHL
5. In GHL, go to **Settings** > **Domains**
6. Click **Add Domain** or **Connect a domain**
7. Enter your domain: `{brand_domain}`
8. GHL provides DNS records to add:
   - **A record:** Points to GHL's IP address
   - **CNAME record:** For subdomains (e.g., `www`, `funnels`)
9. In Cloudflare Dashboard:
   - Go to **DNS** > **Records**
   - Add the A record (set Proxy to **DNS Only** / gray cloud -- required for GHL)
   - Add CNAME record (also DNS Only)
10. Wait for DNS propagation (usually 5-30 minutes)
11. Back in GHL, click **Verify** to confirm domain is connected

#### GHL Email Sending Domain
12. In GHL, go to **Settings** > **Domains** > **Connect** (next to Email)
13. Enter subdomain for email: `mail.{brand_domain}` or `email.{brand_domain}`
14. GHL provides 4-6 DNS records:
    - SPF (TXT record)
    - DKIM (CNAME records)
    - DMARC (TXT record)
    - MX records
15. Add all records to Cloudflare DNS (all as **DNS Only**)
16. Verify in GHL
17. Set **"From" name and email** for outgoing marketing emails

#### GHL Funnel/Landing Page Setup
18. In GHL, go to **Sites** > **Funnels**
19. Click **Create New Funnel** (or use a template)
20. Name the funnel: `{brand_display_name} Main Funnel`
21. Build pages:
    - **Landing page** (home/opt-in page)
    - **Thank you page**
    - **Sales page** (for courses/books)
    - **Booking page** (for consultations)
22. Assign domain to funnel pages
23. Test all pages are loading on `{brand_domain}`

### Required Fields

| Field | Required | Notes |
|-------|----------|-------|
| Cloudflare account (email + password) | Yes | Free account |
| Domain name | Yes | e.g., `{brand_slug}.com` |
| Registrant info (name, address, phone) | Yes | For domain registration |
| Payment method | Yes | For domain purchase |
| GHL account | Yes | $97/month minimum |
| DNS records | Yes | A, CNAME, TXT, MX records |

### What WE Pre-Fill

- **Domain suggestions:**
  - Primary: `{brand_slug}.com`
  - Fallbacks: `{brand_slug}.co`, `{brand_slug}.io`, `{brand_slug}media.com`
- **Email addresses to create:**
  - `hello@{brand_domain}` (general inquiries)
  - `support@{brand_domain}` (customer support)
  - `{teacher_firstname}@{brand_domain}` (personal brand email)
- **GHL funnel pages:**
  - Home: `{brand_domain}`
  - Links: `{brand_domain}/links` (replacement for Linktree)
  - Books: `{brand_domain}/books`
  - Courses: `{brand_domain}/courses`
  - Contact: `{brand_domain}/contact`
- **Email "From" settings:**
  - From Name: `{brand_display_name}`
  - From Email: `hello@{brand_domain}`

### Cloudflare DNS Settings for GHL (Critical)

**ALL records pointing to GHL must have Proxy set to DNS Only (gray cloud).** GHL does not support Cloudflare Proxy (orange cloud).

| Record Type | Name | Value | Proxy |
|------------|------|-------|-------|
| A | @ | GHL IP (provided) | DNS Only |
| CNAME | www | GHL target (provided) | DNS Only |
| TXT | @ | SPF record (provided) | N/A (auto) |
| CNAME | various | DKIM records (provided) | DNS Only |
| TXT | _dmarc | DMARC policy | N/A (auto) |

### Time to Complete

- Cloudflare account + domain registration: **10-15 minutes**
- Email routing setup: **10 minutes**
- GHL account + onboarding: **15-20 minutes**
- Domain connection to GHL: **15-20 minutes**
- Email domain setup in GHL: **15-20 minutes**
- Funnel page creation: **30-60 minutes** (depends on complexity)
- Total: **1.5-2.5 hours**

### Approval Wait Time

- **Cloudflare account:** Instant
- **Domain registration:** Instant (most TLDs)
- **DNS propagation:** 5-30 minutes (can take up to 48 hours)
- **GHL account:** Instant (14-day trial)
- **Email verification in GHL:** 5-15 minutes after DNS setup

### Common Mistakes

- Setting Cloudflare Proxy to orange cloud for GHL records (must be gray cloud / DNS Only)
- Not adding DKIM and DMARC records (emails go to spam)
- Domain name too long or hard to spell
- Not testing email deliverability after setup
- GHL trial expiring without upgrading (loses all funnel data)
- Not setting up SPF record (email authentication fails)

### Per-Lane Differences

| Lane | Difference |
|------|------------|
| US | Standard .com domain; GHL fully supported; USD pricing |
| JP | Consider .jp or .co.jp domain; GHL works but JP payment providers limited |
| KR | Consider .kr or .co.kr domain; GHL works for landing pages |
| EU | GDPR compliance required on landing pages; cookie consent banner needed; consider .eu domain |

---

## Pre-Fill Templates (All Platforms)

### Universal Templates

These templates use variables that are filled from the brand onboarding intake form.

#### Channel/Account Name
```
{brand_display_name}
```
Examples: "Zenith Yoga", "Sensei Karate", "MangaFlow Studio"

#### Short Bio (80 chars -- TikTok)
```
{brand_tagline} | {content_type_short}
```
Example: "Ancient yoga for modern life | Videos & Books"

#### Medium Bio (150 chars -- Instagram)
```
{brand_tagline}
{content_type} by {teacher_name}
{tradition} | New content weekly
{call_to_action_short}
```
Example:
```
Ancient yoga for modern life
Video lessons & books by Sarah Chen
Hatha Yoga | New content weekly
Free guide in link below
```

#### Long Description (1000 chars -- YouTube)
```
Welcome to {brand_display_name}!

{brand_focus_paragraph}

Led by {teacher_name}, {teacher_credential_sentence}.

We publish {content_types_list} to help you {audience_benefit}.

New {primary_content_type} every {upload_schedule}.

Connect with us:
Website: {brand_url}
Instagram: @{brand_slug}
TikTok: @{brand_slug}

{hashtag_list}
```

#### Book Description Template (KDP, Apple, Kobo, Google Play, D2D)
```
{book_hook_sentence}

In "{book_title}", {teacher_name} shares {book_value_proposition}.

What you will learn:
- {benefit_1}
- {benefit_2}
- {benefit_3}

{target_audience_sentence}

About the author:
{teacher_name} is {teacher_bio_short}. Through {brand_display_name}, {teacher_pronoun} has helped {audience_impact_statement}.

Published by {brand_display_name} Publishing.
```

#### Default Keywords (by topic area)
```
# Yoga brand example:
yoga, meditation, mindfulness, {tradition}, {teacher_name}, wellness, health, fitness, spiritual, practice, beginner yoga, advanced yoga, yoga teacher, yoga book

# Martial arts brand example:
martial arts, {martial_art_style}, self defense, training, {teacher_name}, discipline, combat, fighting, technique, forms, kata, practice

# Manga brand example:
manga, webtoon, comic, {genre}, {series_name}, Japanese art, graphic novel, webcomic, {character_names}

# Education brand example:
{subject}, learning, education, tutorial, how to, guide, {teacher_name}, online course, study, training, skill development
```

#### Category Mapping
```
# Brand Topic -> Platform Categories

Yoga:
  YouTube: Education
  Amazon KDP: Health, Fitness & Dieting > Yoga
  Apple Books: Health, Mind & Body > Yoga
  Google Play: Health & Fitness > Yoga
  TikTok: Health & Wellness
  Instagram: Health/Beauty

Martial Arts:
  YouTube: Sports
  Amazon KDP: Sports & Outdoors > Martial Arts & Self-Defense
  Apple Books: Sports & Outdoors > Martial Arts
  Google Play: Sports > Martial Arts
  TikTok: Sports & Outdoors
  Instagram: Sports

Manga/Comics:
  YouTube: Entertainment
  Amazon KDP: Comics & Graphic Novels > Manga
  Apple Books: Comics & Graphic Novels
  Google Play: Comics
  TikTok: Art & Creativity
  Instagram: Art
  Webtoon: varies by series genre

Education/General:
  YouTube: Education
  Amazon KDP: varies by subject
  Apple Books: varies by subject
  Google Play: varies by subject
  TikTok: Education
  Instagram: Education
```

#### Profile Photo Requirements Summary

| Platform | Dimensions | Format | Display |
|----------|-----------|--------|---------|
| YouTube | 800x800px | JPG/PNG | Circular crop |
| TikTok | 200x200px (min) | JPG/PNG | Circular crop |
| Instagram | 320x320px (min) | JPG/PNG | Circular crop, displayed 110x110 |
| Webtoon | Per spec | JPG/PNG | Square or circle |
| LINE | 640x640px (recommended) | JPG/PNG | Circular crop |

**Recommendation:** Create ONE master profile image at **800x800px** and resize for each platform.

---

## Per-Lane Differences Summary

### US Lane
- All 12 platforms apply
- Standard tax forms (W-9, SSN/EIN)
- English-language content
- Full TikTok Shop access
- GHL fully supported
- Primary: YouTube, Amazon KDP, Instagram, TikTok

### JP Lane
- All platforms except: skip LINE for non-JP lanes; skip Webtoon Canvas (use LINE Manga instead or both)
- Tax: W-8BEN with Japanese TIN
- **LINE Official Account is CRITICAL** (96M+ JP users)
- Consider .jp domain
- Amazon.co.jp for KDP
- YouTube JP audience (large market)
- TikTok JP available but no Shop
- Instagram popular for visual brands
- Additional platform consideration: LINE Manga for webcomics

### KR Lane
- Skip LINE (use KakaoTalk instead)
- Skip Webtoon Canvas English (use Naver Webtoon Korean instead or both)
- Tax: W-8BEN with Korean TIN
- Amazon.com for KDP (no Korean-specific marketplace)
- YouTube KR audience
- Instagram very popular in KR
- TikTok KR available but no Shop
- Consider .kr or .co.kr domain
- Additional platform consideration: KakaoTalk Channel, Naver Webtoon

### EU Lane
- All standard platforms apply
- Tax: W-8BEN with EU country TIN; tax treaty benefits often available
- GDPR compliance required on all landing pages (cookie consent, privacy policy)
- EU DSA disclosure for Apple Books
- Amazon has multiple EU marketplaces (.de, .fr, .it, .es, .nl)
- VAT considerations for digital products
- Consider .eu domain or country-specific TLD
- LINE not relevant; Webtoon Canvas for English-speaking EU audience

---

## Master Timeline: Full Platform Onboarding

| Step | Platform | Time | Running Total |
|------|----------|------|---------------|
| 1 | Google Account + 2FA | 10 min | 10 min |
| 2 | YouTube Channel (full setup) | 25 min | 35 min |
| 3 | Amazon KDP | 35 min | 70 min |
| 4 | Google Play Books | 35 min | 105 min |
| 5 | Apple Books | 50 min | 155 min |
| 6 | Kobo Writing Life | 35 min | 190 min |
| 7 | TikTok Business | 15 min | 205 min |
| 8 | Instagram Business | 25 min | 230 min |
| 9 | Webtoon Canvas | 30 min | 260 min |
| 10 | LINE Official (JP only) | 40 min | 300 min |
| 11 | Draft2Digital | 35 min | 335 min |
| 12 | Domain + Email + GHL | 120 min | 455 min |

**Total estimated time: ~7.5 hours** (spread across multiple sessions recommended)

**Recommended session breakdown:**
- **Session 1 (Day 1, 2 hours):** Steps 1-3 (Google, YouTube, KDP)
- **Session 2 (Day 2, 2 hours):** Steps 4-6 (Google Play, Apple, Kobo)
- **Session 3 (Day 3, 1.5 hours):** Steps 7-9 (TikTok, Instagram, Webtoon)
- **Session 4 (Day 4, 2 hours):** Steps 10-12 (LINE, D2D, Domain/GHL)

---

## Appendix: Documents to Have Ready Before Starting

The brand admin should prepare these documents/information BEFORE beginning the onboarding process:

### Personal/Legal Information
- [ ] Legal full name (as it appears on tax documents)
- [ ] Date of birth
- [ ] Mailing address (full postal address)
- [ ] Phone number (for verification codes)
- [ ] Personal email (for recovery / not the brand email)

### Tax Information
- [ ] **US persons:** Social Security Number (SSN) or Employer Identification Number (EIN)
- [ ] **Non-US persons:** Foreign Tax Identification Number (TIN) from home country
- [ ] Country of citizenship
- [ ] Tax treaty information (if applicable)

### Banking Information
- [ ] Bank name
- [ ] Account holder name (must match legal name exactly)
- [ ] Routing number (US) / Sort code (UK) / IBAN (EU) / Bank code + Branch code (JP)
- [ ] Account number
- [ ] Optional: Payoneer or Wise account for multi-currency

### Brand Assets (prepared by us)
- [ ] Brand display name
- [ ] Brand slug (for usernames: lowercase, no spaces)
- [ ] Profile photo (800x800px master file)
- [ ] YouTube banner (2560x1440px with safe zone design)
- [ ] Brand description (short, medium, long versions)
- [ ] Keywords list
- [ ] Category mappings
- [ ] Teacher name and bio
- [ ] Brand tagline

### Government ID (for TikTok Shop only)
- [ ] Passport OR Driver's License OR State ID (US)
- [ ] Business license (for corporations)

---

*End of research document. Last updated: 2026-04-05.*
