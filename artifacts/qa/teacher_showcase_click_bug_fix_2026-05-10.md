# QA — Teacher sidebar click / in-page navigation (`teacher_showcase.html`)

**Project:** PRJ-PEARL-PRIME-ONBOARDING-V6  
**Subsystem:** brand_admin  
**Date:** 2026-05-10  

## Root cause

1. **Invalid HTML (primary):** Each sidebar teacher row was an `<a href="#…">` that wrapped an **interactive** `<input type="radio">`. The HTML content model disallows interactive descendants inside `<a>`. In practice, several browsers mishandle activation of the link (in-page hash navigation / scroll-to-section appears to do nothing or behaves inconsistently) when the row contains a form control.

2. **Fragile reliance on default anchor alone:** Even with valid markup, an explicit `scrollIntoView` + `history.replaceState` for the fragment makes navigation reliable across engines.

## Fix applied

**File:** `brand-wizard-app/public/teacher_showcase.html`

1. Replaced each sidebar `<input type="radio" class="nav-radio" …>` with a non-interactive **`<span class="nav-radio" aria-hidden="true"></span>`** so the sidebar link is valid phrasing content. Visual state continues to follow **`.nav-item.active .nav-radio`** (existing CSS).

2. **`chooseTeacher`:** Removed `querySelector('.nav-radio[value="…"]')` / `checked` logic (no longer valid). Sync sidebar highlight by toggling **`.active`** on `.nav-item[data-teacher="…"]`.

3. **`IntersectionObserver`:** Removed `radio.checked = true` (obsolete).

4. **New `wireSidebarTeacherNav()`** (called from `DOMContentLoaded`): For each `.sidebar a.nav-item[data-teacher]`, on click — `preventDefault`, `scrollIntoView({ behavior: 'smooth', block: 'start' })`, and `history.replaceState` to `#<teacherId>`.

No separate `teacher_showcase.js` file was introduced.

## Operator verification (browser)

1. From repo: `cd brand-wizard-app/public && python3 -m http.server 4322`
2. Open `http://localhost:4322/teacher_showcase.html`
3. Click several names in the **left sidebar**; the main column should scroll to the matching `<section id="…">` and the URL hash should update (e.g. `#junko`).
4. Click **Select …** on a teacher; sticky bar should update; **Choose This Teacher →** should still navigate to the wizard URL.

**Note:** Below **900px** width, CSS still hides the sidebar (`.sidebar { display: none }`). On narrow viewports there is no sidebar to click; use a wider window or zoom out for this test.

## Programmatic check (optional)

Confirm the shipped HTML contains the new hook and markup:

```bash
grep -q 'function wireSidebarTeacherNav' brand-wizard-app/public/teacher_showcase.html && \
grep -q 'span class="nav-radio"' brand-wizard-app/public/teacher_showcase.html && \
echo OK
```

## Deployment (operator only — not automated)

From the project root (or any checkout that contains this `public/` tree):

```bash
cd /Users/ahjan/phoenix_omega/brand-wizard-app/public
npx wrangler pages deploy . --project-name brand-admin-onboarding
```

Cloudflare Pages will pick up the updated `teacher_showcase.html` on the next deploy.

## Edge case: “no bug” retest

If a retest shows clicks working before deploy, capture the exact URL (with/without `.html`, hash, redirect) and viewport width; a **ghost / cached** asset or **mobile hidden nav** can look like “clicks do nothing.”
