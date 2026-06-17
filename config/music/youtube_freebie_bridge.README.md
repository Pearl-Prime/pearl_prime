# YouTube → Freebie Bridge — wiring README

**Config:** [`config/music/youtube_freebie_bridge.yaml`](./youtube_freebie_bridge.yaml)
**Owner:** Pearl_Marketing (YT publish path: Pearl_Marketing + Pearl_Int, Phase-2 runtime)
**Authority (cap):** `MUSIC-ONBOARDING-SONG-KIT-V1-01` — `docs/PEARL_ARCHITECT_STATE.md`
**Spec:** [`docs/specs/MUSIC_ONBOARDING_SONG_KIT_V1_SPEC.md`](../../docs/specs/MUSIC_ONBOARDING_SONG_KIT_V1_SPEC.md) §5
**Status:** **first-increment** — config schema is populated with the wiring contract + worked
commented examples. **Live YouTube upload is NOT wired** (deferred; see Credential reality below).

> This README documents the **bridge** only — the mapping layer that points a published YouTube
> video at an **existing** music-mode freebie. It does **not** define freebie *types* (those are
> `funnel/music_mode/templates/m1..m5`, cap `MUSIC-MODE-FREEBIE-FUNNEL-V1-02`) and it does **not**
> own brand identity (that is `config/music/music_brand_registry.yaml`, cap
> `MUSIC-MODE-BRAND-INTEGRATION-V1-01`). It reuses both verbatim.

---

## 1. Credential reality (verified — do NOT assume)

Checked against `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` **§13 "YouTube — Video publishing
(per brand: SP, CC, ND)"** on 2026-06-12:

| Field | Value (per registry §13) |
|---|---|
| Env vars | `YT_CLIENT_ID_{SP,CC,ND}`, `YT_CLIENT_SECRET_{SP,CC,ND}`, `YT_REFRESH_TOKEN_{SP,CC,ND}` |
| Consumed by | `scripts/video/uploaders/youtube.py` |
| GitHub workflow | `video-daily-publish.yml` |
| How to obtain | Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client (YouTube Data API v3) |
| **Status** | **`Missing — credentials not yet provisioned`** |
| Detailed docs | `docs/VIDEO_PLATFORM_CREDENTIAL_SETUP.md` |

**Conclusion:** YouTube OAuth creds are **documented but NOT provisioned**. Therefore **no live
upload/poll is wired** in this increment. Provisioning + live publish is **operator / Pearl_Int +
Pearl_Marketing runtime work, gated on the §13 status flipping to provisioned.** This file is a
non-secret routing map only — OAuth lives exclusively in the `YT_*` env vars loaded from macOS
Keychain at runtime (`eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"`), never
in this repo.

---

## 2. What the bridge does

Maps **one published YouTube video** → **an email-gate** → **one existing m1..m5 freebie route**,
so a YouTube viewer who clicks the video's description/pinned-comment link lands on a freebie
email-capture page that hands off to the existing funnel.

```
YouTube video (lyric/visualizer/behind-song/preview)
        │  description first-line + PINNED COMMENT carry CTA + landing link
        ▼
  landing_route  (server-relative, e.g. /free/music/<brand>/companion-song)
        │  email_gate.capture_step = email_capture_before_download_link
        ▼
  freebie delivered by freebie_template_id  (one of m1..m5, reused verbatim)
        │  m1..m5 template's own cross_link_targets sequence the rest
        ▼
  existing music-mode funnel  (bridge does NOT re-implement this)
```

The bridge owns **only** the mapping `video_id → email-gate → freebie template`, keyed on the
composite **`{album_slug}/{landing_url}`**. It mints **no** new freebie assets and replaces **no**
Pearl Prime freebie.

---

## 3. The `{album_slug}/{landing_url}` route key

Every bridge entry is uniquely identified by **`route_key = "{album_slug}/{landing_url}"`**:

- **`album_slug`** — the release-wave slug. It is the same token used by the freebie copy
  placeholders: m1/m3 `copy_blocks` reference `{{album_slug}}` (e.g. m1 body: *"...your confirmation
  path also points at {{album_slug}}..."*). Tying the bridge entry to `album_slug` keeps the YT
  route and the freebie copy on the same release wave.
- **`landing_url`** (== the entry's `landing_route`) — the **server-relative** freebie capture
  route the YouTube link resolves to. It is the same token as m1 `social_share`'s `{{landing_url}}`.
  **NO `file://`, NO scheme** — server-relative only (same rule as the registry's
  `survey_yaml_pointer` convention; see `music_brand_registry.yaml` header rule 4).

`route_key` MUST equal `{album_slug}` + `/` + `landing_route` with the leading slash removed, and
MUST be unique across all entries. A single `youtube_video_id` MAY appear in two entries only if it
legitimately fronts two distinct `(album, freebie)` routes.

---

## 4. The email-gate routing surface (how a published video routes a viewer)

The **YouTube video description first line** and the **pinned comment** are the routing surface:

1. Both carry the **same CTA**, sourced from the mapped m1..m5 template's `copy_blocks.CTA` /
   `copy_blocks.social_share` (e.g. m1 CTA = *"Get my song"*; m5 = *"Hear story"*). Copy is
   **referenced, never inlined** in the bridge config (`description_gate.yt_description_cta_ref`
   points at the m1..m5 file).
2. Both carry the **landing link** = `{origin}{landing_route}` (absolute https). `origin` is
   resolved from env/site-config at runtime — **never hardcoded** in the repo.
3. The viewer clicks → lands on `landing_route` → hits the email gate
   (`email_gate.capture_step = email_capture_before_download_link`, mirroring the m1..m5
   `gating_step`) → submits email → the funnel delivers `freebie_template_id`.

Placeholders (`{{album_slug}}`, `{{landing_url}}`, `{{track_title}}`, `{{artist_name}}`, etc.) are
filled at render time from the brand/release context — the bridge stores the *mapping*, not the
rendered strings.

**Copy generation tier (no paid LLM):** any auto-generated YT title/description copy is
English → Claude subagents (Pearl_Writer); CJK6 → Qwen (Pearl Star/Ollama); unattended/scheduled →
Gemma/Qwen-Ollama. Enforced by CLAUDE.md Tier policy + `scripts/ci/audit_llm_callers.py`. This
config stores zero generated copy.

---

## 5. Bridge contract (anti-drift — reuse, not new freebies)

| Rule | Constraint |
|---|---|
| `freebie_template_id` | MUST be one of the five m1..m5 `template_id`s: `companion_track_download_v1`, `preview_clip_30s_v1`, `sample_ep_bundle_v1`, `lyric_poster_pdf_v1`, `behind_the_song_interview_v1`. **No new freebie types** (that is `MUSIC-MODE-FREEBIE-FUNNEL-V1-02`). |
| `brand_id` | MUST resolve to an **active** music-mode brand in `config/music/music_brand_registry.yaml` (id-space 38+). **No Path X 37** manga brands. Today the registry holds only `_template_music` (inactive placeholder) → real entries land via the wizard + survey-save ws. |
| `email_gate.capture_step` | == `email_capture_before_download_link` (mirrors the m1..m5 `gating_step`). |
| `landing_route` | server-relative, `^/[A-Za-z0-9/_-]+$`. **NO `file://`, NO scheme.** |
| `youtube_video_id` | `null` until §13 creds are provisioned; then 11-char `[A-Za-z0-9_-]`. |
| secrets | **None** in this file. OAuth lives only in `YT_*` env vars from Keychain at runtime. |
| LLM | No paid LLM API anywhere. |

The bridge config encodes this as a `VALIDATION CONTRACT` block (bottom of the YAML) for the
Phase-2 ws loader/validator.

---

## 6. Why entries are commented in this increment

The active `bridge_entries:` list is **`[]`** (empty) and the worked examples are **commented**,
because:

1. **Spec §5.1** ships the file as *"schema + one commented example, no real video ids."*
2. **Anti-drift §5.3 #3:** `brand_id` MUST resolve to an **active** registry brand. Today
   `music_brand_registry.yaml` contains only the inactive `_template_music` placeholder — no real
   `ahjan_music` brand is registered yet (that arrives via the brand-wizard + survey-save
   workstream). Activating an entry now would reference a non-existent brand.
3. **Credentials:** §13 YouTube creds are `Missing — not yet provisioned`, so `youtube_video_id`
   has no legitimate value yet.

The three worked examples (lyric→M1, behind-song→M5, preview→M2) are provided **commented** to
document entry shape and to be validated; the Phase-2 ws un-comments / appends real entries once
**(a)** the music brand is registered **and (b)** §13 creds are provisioned.

---

## 7. Phase-2 runtime work (deferred — gated on credential provisioning)

Owned by **Pearl_Marketing + Pearl_Int**, NOT in this increment:

1. **Provision §13 YouTube OAuth creds** (per brand SP/CC/ND) and flip the registry status; see
   `docs/VIDEO_PLATFORM_CREDENTIAL_SETUP.md`.
2. **Register the real music brand** in `config/music/music_brand_registry.yaml` (wizard +
   survey-save ws) so `brand_id` resolves to an active entry.
3. **Publish** the song's YT asset via `scripts/video/uploaders/youtube.py` (workflow
   `video-daily-publish.yml`); capture the returned 11-char `video_id`.
4. **Activate** the bridge entry: fill `youtube_video_id`, move it from the commented block into the
   active `bridge_entries:` list, and run the loader/validator against the `VALIDATION CONTRACT`.
5. **Set the YT description + pinned comment** to the mapped CTA + `{origin}{landing_route}` link.
6. **Write the loader/validator** that enforces the `VALIDATION CONTRACT` and resolves `brand_id`
   against the active registry + `freebie_template_id` against m1..m5.

---

## 8. Cross-references

- **Spec:** `docs/specs/MUSIC_ONBOARDING_SONG_KIT_V1_SPEC.md` §5 (and §6 LLM tier).
- **Cap:** `MUSIC-ONBOARDING-SONG-KIT-V1-01` in `docs/PEARL_ARCHITECT_STATE.md`.
- **Freebie templates (reused verbatim):** `funnel/music_mode/templates/m1..m5`
  (`MUSIC-MODE-FREEBIE-FUNNEL-V1-02`).
- **Brand SSOT:** `config/music/music_brand_registry.yaml`
  (`MUSIC-MODE-BRAND-INTEGRATION-V1-01`).
- **Topic families:** `config/music/song_kit_topic_families.yaml`.
- **Credentials:** `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §13 (YouTube) +
  `docs/VIDEO_PLATFORM_CREDENTIAL_SETUP.md`.
- **Directory README (different owner/cap):** `config/music/README.md`
  (`MUSIC-MODE-BRAND-INTEGRATION-V1-01`, Pearl_Brand) — that file documents the brand-registry
  directory and is intentionally **not** extended by this bridge.
