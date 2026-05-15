# Brand-Wizard Composite-Mode Browser Verification — 2026-05-14

Branch: `agent/brand-wizard-composite-mode-20260514`
Preview server: `vite preview` serving `brand-wizard-app/dist` on port 4173 (built from this branch)
Tool: Claude_Preview MCP (preview_inspect + preview_screenshot + preview_eval)
Verifier: Pearl_Dev session `claude/xenodochial-sutherland-5a824b`

## Verification matrix

| Locale | Composite-banner text (inspect) | Banner render | Click flow |
|--------|---------------------------------|---------------|------------|
| en     | "Author all books for this brand without a teacher voice" / "Composite mode (no teacher) →" | ✅ screenshot in chat | ✅ click → localStorage `{"mode":"composite","teacher":null}` → URL `wizard.html?mode=composite` → wizard skipped intro and landed at **STEP 1 OF 9 — Emotional World / Choose your emotional world** (book mode, archetype selector). No teacher UI. |
| ja     | "この銘柄の全ての書籍を、教師の声なしで執筆" / "コンポジット（教師なし） →" | ✅ screenshot in chat | ✅ banner + chooseTeacher labels rendered in JA ("選択する AHJAN", "表示中 — ", "このティーチャーを選ぶ →") |
| zh     | "为该品牌创作所有书籍，不使用教师之声" / "综合模式（无教师） →" | ✅ screenshot in chat | ✅ banner + chooseTeacher labels rendered in ZH ("选择 AHJAN", "正在查看 — ", "选择此老师 →") |
| tw     | "為此品牌創作所有書籍，不使用教師之聲" / "綜合模式（無教師） →" | ✅ screenshot in chat | ✅ banner + chooseTeacher labels rendered in TW ("選擇 AHJAN", "正在查看 — ", "選擇此老師 →") |

## End-to-end flow proven (en)

```
localStorage.removeItem('phoenix_book_mode');
document.getElementById('composite-banner-btn').click();
// → { ls: "{\"mode\":\"composite\",\"teacher\":null}", url: "http://localhost:4173/teacher_showcase.html" }
// (async navigation) → 1.5s later:
// → { ls: "{\"mode\":\"composite\",\"teacher\":null}", url: "http://localhost:4173/wizard.html?mode=composite" }
// → wizard body text begins with: "STEP 1 OF 9 — Emotional World — Choose your emotional world ... MODE Book mode ..."
```

## YAML emit contract (already correct pre-change, regression check)

`BrandWizard.jsx:3299` (and locale-equivalent line 3253) emits, when `teacherMode.teacher` is falsy:

```yaml
teacher_mode:
  mode: composite
  selected_teacher: null
  teacher_boost_pct: 0
```

The composite path sets `teacherMode = { mode: 'composite', teacher: null }` → `teacherMode.teacher` is null → composite YAML block emitted unchanged. Matches `config/catalog_planning/teacher_mode_config.yaml:24-28` composite mode definition.

## CI deployment

Local Cloudflare deploy blocked by IP-restricted token (CI-only by design, intentional security posture). The workflow at `.github/workflows/brand-admin-onboarding-pages.yml` auto-deploys on `push: branches: [main]` for any change in `brand-wizard-app/**`. Operator merge → production deploy to `brand-admin-onboarding.pages.dev` for:

- https://brand-admin-onboarding.pages.dev/teacher_showcase.html
- https://brand-admin-onboarding.pages.dev/wizard.html
- https://brand-admin-onboarding.pages.dev/wizard-ja.html
- https://brand-admin-onboarding.pages.dev/wizard-zh.html
- https://brand-admin-onboarding.pages.dev/wizard-tw.html

Screenshots from the live URLs should be captured post-merge for the production record.
