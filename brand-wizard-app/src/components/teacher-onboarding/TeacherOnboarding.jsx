import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  BookOpen,
  CheckCircle2,
  ClipboardList,
  Copy,
  FileUp,
  Link,
  Loader2,
  Plus,
  Save,
  ShieldCheck,
  Sparkles,
  Trash2,
  Upload,
  User,
} from "lucide-react";
import FlagLocaleGate from "./FlagLocaleGate.jsx";
import { useTeacherOnboardingI18n } from "../../i18n-teacher-onboarding.jsx";

const ACCEPTED_SOURCE_TYPES = ".txt,.md,.pdf,.doc,.docx,.rtf,.csv,.json,.yaml,.yml,.mp3,.mp4,.m4a,.wav";

/** Canonical 14-locale roster (en-US + 13). */
const REPO_LANGUAGES = [
  { code: "en-US", label: "English (US)" },
  { code: "ja-JP", label: "Japanese" },
  { code: "zh-TW", label: "Traditional Chinese (Taiwan)" },
  { code: "zh-CN", label: "Simplified Chinese (Mainland)" },
  { code: "ko-KR", label: "Korean" },
  { code: "zh-HK", label: "Traditional Chinese (Hong Kong)" },
  { code: "zh-SG", label: "Simplified Chinese (Singapore)" },
  { code: "es-US", label: "Spanish (US / LatAm)" },
  { code: "es-ES", label: "Spanish (Spain)" },
  { code: "fr-FR", label: "French (France)" },
  { code: "de-DE", label: "German" },
  { code: "it-IT", label: "Italian" },
  { code: "hu-HU", label: "Hungarian" },
  { code: "pt-BR", label: "Portuguese (Brazil)" },
];

const STORY_TYPES = [
  "Lived / composite",
  "Witnessed",
  "Teaching room",
  "Student journey",
  "Myth / parable",
  "Other",
];

const PRACTICE_TYPES = [
  "Breath",
  "Somatic",
  "Meditation",
  "Journaling",
  "Movement",
  "Inquiry / dialogue",
  "Other",
];

const LANGUAGE_ROW_TYPES = [
  { id: "quote", label: "Quote / phrase / mantra" },
  { id: "reflection", label: "Reflection & integration" },
  { id: "topics", label: "Topics, personas & boundaries" },
  { id: "voice_rules", label: "Repeated phrases, metaphors & voice rules" },
  { id: "forbidden", label: "Forbidden language / would not say" },
];

const readinessTargets = [
  { key: "teachings", label: "Teachings / Doctrine", min: 4, preferred: 12, scale: 100 },
  { key: "hooks", label: "Hooks", min: 12, preferred: 12, scale: 50 },
  { key: "scenes", label: "Scenes", min: 12, preferred: 12, scale: 50 },
  { key: "stories", label: "Teacher Stories", min: 20, preferred: 20, scale: 60 },
  { key: "practices", label: "Exercises / Practices", min: 12, preferred: 40, scale: 60 },
  { key: "reflections", label: "Reflections", min: 12, preferred: 12, scale: 60 },
  { key: "integrations", label: "Integrations", min: 12, preferred: 12, scale: 60 },
  { key: "pivots", label: "Pivots", min: 15, preferred: 15, scale: 15 },
  { key: "threads", label: "Threads", min: 15, preferred: 15, scale: 15 },
  { key: "permissions", label: "Permissions", min: 15, preferred: 15, scale: 15 },
  { key: "takeaways", label: "Takeaways", min: 15, preferred: 15, scale: 15 },
  { key: "quotes", label: "Quotes / Phrases", min: 0, preferred: 12, scale: 100 },
  { key: "raw_sources", label: "Source Files / URLs", min: 1, preferred: 8, scale: 12 },
];

function emptyContent() {
  return { text: "", url: "", files: [] };
}

function starterTeaching() {
  return emptyContent();
}

function starterStory() {
  return { type: STORY_TYPES[0], ...emptyContent() };
}

function starterPractice() {
  return { type: PRACTICE_TYPES[0], ...emptyContent() };
}

function starterLanguageRow(typeId = "quote") {
  return { kind: typeId, note: "", ...emptyContent() };
}

function slugify(value) {
  return (
    String(value || "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 80) || "teacher"
  );
}

function contentFilled(entry) {
  if (!entry || typeof entry !== "object") return false;
  return (
    String(entry.text || "").trim().length > 0 ||
    String(entry.url || "").trim().length > 0 ||
    (Array.isArray(entry.files) && entry.files.length > 0)
  );
}

function countContentBlocks(entry) {
  if (!contentFilled(entry)) return 0;
  const text = String(entry.text || "").trim();
  if (!text) return 1;
  const blocks = text
    .split(/\n{2,}|\n[-*]\s+|\n\d+\.\s+/)
    .map((part) => part.trim())
    .filter((part) => part.length > 24);
  return Math.max(1, blocks.length);
}

function fileMetaFromList(fileList) {
  return Array.from(fileList || []).map((file) => ({
    name: file.name,
    size: file.size,
    type: file.type || "unknown",
    last_modified: file.lastModified ? new Date(file.lastModified).toISOString() : null,
    upload_note: "metadata_only_in_v1_attach_or_R2_upload_in_followup_lane",
  }));
}

function collectAllFiles(entries) {
  const out = [];
  for (const entry of entries) {
    if (Array.isArray(entry?.files)) out.push(...entry.files);
  }
  return out;
}

function ProgressBar({ value }) {
  return (
    <div className="h-2 overflow-hidden rounded-full border border-amber-900/40 bg-black/30">
      <div
        className="h-full rounded-full bg-amber-600 transition-all"
        style={{ width: `${value > 0 ? Math.max(4, Math.min(100, value)) : 0}%` }}
      />
    </div>
  );
}

function Field({ label, children, hint }) {
  return (
    <label className="block">
      <span className="mb-2 block text-[11px] uppercase tracking-[0.18em] text-stone-400">{label}</span>
      {children}
      {hint ? <span className="mt-2 block text-xs leading-5 text-stone-500">{hint}</span> : null}
    </label>
  );
}

function TextInput(props) {
  return (
    <input
      {...props}
      className={`w-full rounded-md border border-amber-900/30 bg-black/25 px-3 py-3 text-sm text-stone-100 outline-none transition focus:border-amber-600 ${props.className || ""}`}
    />
  );
}

function TextArea(props) {
  return (
    <textarea
      {...props}
      className={`min-h-[112px] w-full resize-y rounded-md border border-amber-900/30 bg-black/25 px-3 py-3 text-sm leading-6 text-stone-100 outline-none transition focus:border-amber-600 ${props.className || ""}`}
    />
  );
}

function SelectInput(props) {
  return (
    <select
      {...props}
      className={`w-full rounded-md border border-amber-900/30 bg-black/25 px-3 py-3 text-sm text-stone-100 outline-none transition focus:border-amber-600 ${props.className || ""}`}
    />
  );
}

function Section({ id, icon: Icon, kicker, title, children }) {
  return (
    <section id={id} className="scroll-mt-6 rounded-lg border border-amber-900/25 bg-[#1c1009]/70 p-5 shadow-xl shadow-black/20">
      <div className="mb-5 flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md border border-amber-800/40 bg-amber-950/40 text-amber-500">
          <Icon size={18} />
        </div>
        <div>
          <div className="text-[10px] uppercase tracking-[0.2em] text-amber-500">{kicker}</div>
          <h2 className="mt-1 text-2xl">{title}</h2>
        </div>
      </div>
      {children}
    </section>
  );
}

/** Text · URL · Upload for a single content slot. */
function ContentEntryInput({ value, onChange, textPlaceholder, hint }) {
  const entry = value || emptyContent();
  const onFiles = (event) => {
    const added = fileMetaFromList(event.target.files);
    onChange({ ...entry, files: [...(entry.files || []), ...added] });
    event.target.value = "";
  };
  return (
    <div className="space-y-3">
      <TextArea
        value={entry.text || ""}
        onChange={(e) => onChange({ ...entry, text: e.target.value })}
        placeholder={textPlaceholder || "Paste or type content…"}
      />
      <div className="grid gap-3 md:grid-cols-[1fr_auto]">
        <TextInput
          value={entry.url || ""}
          onChange={(e) => onChange({ ...entry, url: e.target.value })}
          placeholder="https://… (optional URL)"
        />
        <label className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-md border border-amber-800/40 px-4 py-3 text-sm text-amber-400 hover:border-amber-500">
          <Upload size={15} />
          Upload
          <input type="file" multiple accept={ACCEPTED_SOURCE_TYPES} className="hidden" onChange={onFiles} />
        </label>
      </div>
      {(entry.files || []).length ? (
        <div className="flex flex-wrap gap-2">
          {entry.files.map((file, index) => (
            <span
              key={`${file.name}-${index}`}
              className="inline-flex items-center gap-2 rounded-md border border-amber-900/25 bg-black/30 px-2.5 py-1 text-xs text-stone-400"
            >
              <FileUp size={12} className="text-amber-600" />
              <span className="max-w-[180px] truncate">{file.name}</span>
              <button
                type="button"
                onClick={() =>
                  onChange({ ...entry, files: entry.files.filter((_, i) => i !== index) })
                }
                className="text-stone-500 hover:text-amber-400"
                aria-label={`Remove ${file.name}`}
              >
                <Trash2 size={12} />
              </button>
            </span>
          ))}
        </div>
      ) : null}
      {hint ? <p className="text-xs leading-5 text-stone-500">{hint}</p> : null}
    </div>
  );
}

function RowList({ rows, setRows, starter, renderRow, addLabel, minRows = 1 }) {
  const updateRow = (index, patch) => {
    setRows(rows.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  };
  const removeRow = (index) => {
    if (rows.length <= minRows) return;
    setRows(rows.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-3">
      {rows.map((row, index) => (
        <div key={index} className="rounded-md border border-amber-900/20 bg-black/20 p-4">
          <div className="mb-3 flex items-center justify-between gap-3">
            <div className="text-[11px] uppercase tracking-[0.16em] text-stone-500">Row {index + 1}</div>
            {rows.length > minRows ? (
              <button
                type="button"
                onClick={() => removeRow(index)}
                className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-amber-900/30 text-stone-400 hover:border-amber-700 hover:text-amber-400"
                aria-label={`Remove row ${index + 1}`}
              >
                <Trash2 size={15} />
              </button>
            ) : null}
          </div>
          {renderRow(row, updateRow, index)}
        </div>
      ))}
      <button
        type="button"
        onClick={() => setRows([...rows, typeof starter === "function" ? starter() : { ...starter }])}
        className="inline-flex items-center gap-2 rounded-md border border-amber-800/40 px-4 py-2 text-sm text-amber-400 hover:border-amber-500"
      >
        <Plus size={16} />
        {addLabel}
      </button>
    </div>
  );
}

function migrateLegacyUi(ui) {
  if (!ui || typeof ui !== "object") return ui;
  const next = { ...ui };
  // Legacy flat bio string → content entry
  if (typeof next.identity?.teacherBio === "string") {
    next.identity = {
      ...next.identity,
      teacherBio: { text: next.identity.teacherBio, url: "", files: [] },
      language: (next.identity.languages || "en-US").split(/[,\n]/)[0].trim().replace("_", "-") || "en-US",
    };
  }
  if (typeof next.teachingsText === "string" && !Array.isArray(next.teachings)) {
    next.teachings = next.teachingsText.trim()
      ? [{ text: next.teachingsText, url: "", files: [] }]
      : [starterTeaching()];
  }
  if (Array.isArray(next.stories) && next.stories[0] && "title" in next.stories[0] && !("type" in next.stories[0])) {
    next.stories = next.stories.map((s) => ({
      type: s.title || STORY_TYPES[0],
      text: [s.context, s.point].filter(Boolean).join("\n\n"),
      url: s.source || "",
      files: [],
    }));
    while (next.stories.length < 3) next.stories.push(starterStory());
  }
  if (Array.isArray(next.practices) && next.practices[0] && "name" in next.practices[0] && !("type" in next.practices[0])) {
    next.practices = next.practices.map((p) => ({
      type: p.name || PRACTICE_TYPES[0],
      text: [p.helpsWith, p.guidance, p.caution].filter(Boolean).join("\n\n"),
      url: p.origin || "",
      files: [],
    }));
    while (next.practices.length < 3) next.practices.push(starterPractice());
  }
  if (!Array.isArray(next.languageRows)) {
    const rows = LANGUAGE_ROW_TYPES.map((t) => starterLanguageRow(t.id));
    if (Array.isArray(next.quotes)) {
      next.quotes.forEach((q, i) => {
        if (i === 0) rows[0] = { kind: "quote", note: q.source || "", text: q.text || "", url: "", files: [] };
        else rows.push({ kind: "quote", note: q.source || "", text: q.text || "", url: "", files: [] });
      });
    }
    if (next.reflectionText) rows[1] = { ...rows[1], text: next.reflectionText };
    if (next.topicsText) rows[2] = { ...rows[2], text: next.topicsText };
    if (next.voiceText) rows[3] = { ...rows[3], text: next.voiceText };
    if (next.forbiddenLanguageText) rows[4] = { ...rows[4], text: next.forbiddenLanguageText };
    next.languageRows = rows;
  }
  return next;
}

function TeacherOnboardingForm({ locale, t, clearLocale }) {
  const [identity, setIdentity] = useState({
    teacherName: "",
    teacherId: "",
    tradition: "",
    language: "en-US",
    website: "",
    contactName: "",
    contactEmail: "",
    teacherBio: emptyContent(),
  });
  const [rights, setRights] = useState({
    ownsMaterial: false,
    processingConsent: false,
    noUnauthorizedCopyright: false,
    consent: false,
    publicBoundaries: "",
    privateBoundaries: "",
    humanReview: true,
  });
  const [teacherIdOverridden, setTeacherIdOverridden] = useState(false);

  // Keep teaching-language data field in sync with display locale only when still at starter default.
  useEffect(() => {
    if (!locale) return;
    setIdentity((prev) => {
      if (prev.language && prev.language !== "en-US" && prev.language !== locale) return prev;
      return { ...prev, language: locale };
    });
  }, [locale]);
  const [teachings, setTeachings] = useState([starterTeaching()]);
  const [stories, setStories] = useState([starterStory(), starterStory(), starterStory()]);
  const [practices, setPractices] = useState([starterPractice(), starterPractice(), starterPractice()]);
  const [languageRows, setLanguageRows] = useState(LANGUAGE_ROW_TYPES.map((t) => starterLanguageRow(t.id)));
  const [submitState, setSubmitState] = useState({ status: "idle" });
  const [draftMeta, setDraftMeta] = useState({
    draft_id: "",
    edit_token: "",
    status: "",
    resume_path: "",
  });
  const [draftState, setDraftState] = useState({ status: "idle", detail: "" });
  const [copiedUrl, setCopiedUrl] = useState(false);

  const teacherId = identity.teacherId.trim() || slugify(identity.teacherName);

  const collectUiState = () => ({
    identity,
    rights,
    teacherIdOverridden,
    teachings,
    stories,
    practices,
    languageRows,
  });

  const hydrateUiState = (ui) => {
    const migrated = migrateLegacyUi(ui);
    if (!migrated || typeof migrated !== "object") return;
    if (migrated.identity) {
      setIdentity((current) => {
        const merged = { ...current, ...migrated.identity };
        if (merged.teacherBio && typeof merged.teacherBio === "string") {
          merged.teacherBio = { text: merged.teacherBio, url: "", files: [] };
        }
        if (!merged.teacherBio) merged.teacherBio = emptyContent();
        if (!merged.language && merged.languages) {
          merged.language = String(merged.languages).split(/[,\n]/)[0].trim().replace("_", "-") || "en-US";
        }
        return merged;
      });
    }
    if (migrated.rights) setRights((current) => ({ ...current, ...migrated.rights }));
    if (typeof migrated.teacherIdOverridden === "boolean") setTeacherIdOverridden(migrated.teacherIdOverridden);
    if (Array.isArray(migrated.teachings) && migrated.teachings.length) setTeachings(migrated.teachings);
    if (Array.isArray(migrated.stories) && migrated.stories.length) setStories(migrated.stories);
    if (Array.isArray(migrated.practices) && migrated.practices.length) setPractices(migrated.practices);
    if (Array.isArray(migrated.languageRows) && migrated.languageRows.length) setLanguageRows(migrated.languageRows);
  };

  useEffect(() => {
    if (teacherIdOverridden) return;
    const generated = slugify(identity.teacherName);
    setIdentity((current) => {
      if (current.teacherId === generated) return current;
      return { ...current, teacherId: generated };
    });
  }, [identity.teacherName, teacherIdOverridden]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = (params.get("edit_token") || params.get("token") || "").trim();
    if (!token) return;
    let cancelled = false;
    (async () => {
      setDraftState({ status: "loading", detail: "Resuming draft…" });
      try {
        const response = await fetch(
          `/api/teacher-onboarding/drafts?edit_token=${encodeURIComponent(token)}`
        );
        const body = await response.json().catch(() => ({}));
        if (cancelled) return;
        if (!response.ok) {
          setDraftState({ status: "error", detail: body.detail || `Resume failed (${response.status})` });
          return;
        }
        hydrateUiState(body.ui_state);
        setDraftMeta({
          draft_id: body.draft_id || "",
          edit_token: body.edit_token || token,
          status: body.status || "draft",
          resume_path: `/teacher_onboarding.html?edit_token=${encodeURIComponent(body.edit_token || token)}`,
        });
        setDraftState({ status: "resumed", detail: `Draft resumed (${body.draft_id}).` });
      } catch (err) {
        if (!cancelled) setDraftState({ status: "error", detail: err.message });
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const allContentEntries = useMemo(
    () => [
      identity.teacherBio,
      ...teachings,
      ...stories,
      ...practices,
      ...languageRows,
    ],
    [identity.teacherBio, teachings, stories, practices, languageRows]
  );

  const counts = useMemo(() => {
    const teachingCount = teachings.reduce((sum, t) => sum + countContentBlocks(t), 0);
    const storyCount = stories.filter(contentFilled).length;
    const practiceCount = practices.filter(contentFilled).length;
    const quoteCount = languageRows.filter((r) => r.kind === "quote" && contentFilled(r)).length;
    const reflectionCount = languageRows.filter(
      (r) => (r.kind === "reflection" || r.kind === "topics") && contentFilled(r)
    ).length;
    const urlCount = allContentEntries.filter((e) => String(e?.url || "").trim()).length;
    const fileCount = collectAllFiles(allContentEntries).length;
    return {
      teachings: teachingCount,
      hooks: 0,
      scenes: 0,
      stories: storyCount,
      practices: practiceCount,
      quotes: quoteCount,
      reflections: reflectionCount,
      integrations: reflectionCount,
      pivots: 0,
      threads: 0,
      permissions: 0,
      takeaways: 0,
      raw_sources: urlCount + fileCount,
    };
  }, [teachings, stories, practices, languageRows, allContentEntries]);

  const targetRows = useMemo(
    () =>
      readinessTargets.map((item) => {
        const count = counts[item.key] || 0;
        const preferred = item.preferred || item.min || 1;
        return {
          ...item,
          count,
          preferred,
          minRatio: Math.min(1, count / (item.min || preferred)),
          preferredRatio: Math.min(1, count / preferred),
          scaleRatio: Math.min(1, count / item.scale),
        };
      }),
    [counts]
  );

  const readiness = useMemo(() => {
    const minTotal = targetRows.reduce((sum, item) => sum + item.minRatio, 0);
    const scaleTotal = targetRows.reduce((sum, item) => sum + item.scaleRatio, 0);
    return {
      functional: Math.round((minTotal / targetRows.length) * 100),
      scale: Math.round((scaleTotal / targetRows.length) * 100),
    };
  }, [targetRows]);

  const missingMinimums = useMemo(
    () =>
      targetRows
        .filter((item) => item.min > 0 && item.count < item.min)
        .map((item) => ({
          key: item.key,
          label: item.label,
          count: item.count,
          minimum: item.min,
          missing: item.min - item.count,
        })),
    [targetRows]
  );

  const recommendedGaps = useMemo(
    () =>
      targetRows
        .filter((item) => item.count < item.preferred)
        .map((item) => ({
          key: item.key,
          label: item.label,
          count: item.count,
          preferred: item.preferred,
          missing: item.preferred - item.count,
        })),
    [targetRows]
  );

  const hasMaterial =
    teachings.some(contentFilled) ||
    stories.some(contentFilled) ||
    practices.some(contentFilled) ||
    languageRows.some(contentFilled) ||
    contentFilled(identity.teacherBio);

  const contactEmailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(identity.contactEmail.trim());
  const validationMessages = [
    !identity.teacherName.trim() ? t("validation.teacher_name_required") : "",
    !identity.contactEmail.trim() ? t("validation.contact_email_required") : "",
    identity.contactEmail.trim() && !contactEmailValid ? t("validation.contact_email_invalid") : "",
    !rights.ownsMaterial ? t("validation.owns_required") : "",
    !rights.processingConsent ? t("validation.processing_required") : "",
    !rights.consent ? t("validation.consent_required") : "",
    !hasMaterial ? t("validation.material_required") : "",
  ].filter(Boolean);

  const canSubmit =
    identity.teacherName.trim() &&
    contactEmailValid &&
    rights.ownsMaterial &&
    rights.processingConsent &&
    rights.consent &&
    hasMaterial;

  const packet = useMemo(() => {
    const now = new Date().toISOString();
    const filledTeachings = teachings.filter(contentFilled);
    const filledStories = stories.filter(contentFilled);
    const filledPractices = practices.filter(contentFilled);
    const filledLanguage = languageRows.filter(contentFilled);
    const allFiles = collectAllFiles(allContentEntries);
    const allUrls = allContentEntries.map((e) => String(e?.url || "").trim()).filter(Boolean);

    const doctrineText = filledTeachings.map((t) => t.text.trim()).filter(Boolean).join("\n\n");
    const teachingUrls = filledTeachings.map((t) => t.url.trim()).filter(Boolean);
    const bio = identity.teacherBio || emptyContent();

    const quoteRows = filledLanguage.filter((r) => r.kind === "quote");
    const reflectionBits = filledLanguage
      .filter((r) => r.kind === "reflection")
      .map((r) => r.text.trim())
      .filter(Boolean);
    const topicsBits = filledLanguage
      .filter((r) => r.kind === "topics")
      .map((r) => r.text.trim())
      .filter(Boolean);
    const voiceBits = filledLanguage
      .filter((r) => r.kind === "voice_rules")
      .map((r) => r.text.trim())
      .filter(Boolean);
    const forbiddenBits = filledLanguage
      .filter((r) => r.kind === "forbidden")
      .map((r) => r.text.trim())
      .filter(Boolean);

    return {
      schema_version: "teacher_onboarding_intake_v2",
      submitted_at: now,
      teacher_id: teacherId,
      teacher_name: identity.teacherName.trim(),
      identity: {
        public_teacher_name: identity.teacherName.trim(),
        teacher_id: teacherId,
        tradition_lineage_practice_family: identity.tradition.trim(),
        languages: [identity.language || "en-US"],
        website: identity.website.trim(),
        contact_name: identity.contactName.trim(),
        contact_email: identity.contactEmail.trim(),
        teacher_bio: bio.text.trim(),
        teacher_bio_url: bio.url.trim(),
        teacher_bio_files: bio.files || [],
      },
      rights: {
        own_voice_or_original_material: rights.ownsMaterial,
        permission_to_process_into_atoms: rights.processingConsent,
        no_unauthorized_copyrighted_material: rights.noUnauthorizedCopyright,
        final_consent_to_submit_intake: rights.consent,
        public_source_boundaries: rights.publicBoundaries.trim(),
        private_source_boundaries: rights.privateBoundaries.trim(),
        human_review_required: rights.humanReview,
      },
      readiness: {
        counts,
        functional_percent: readiness.functional,
        catalog_scale_percent: readiness.scale,
        missing_minimums: missingMinimums,
        recommended_gaps: recommendedGaps,
        client_readiness_is_guidance_only: true,
        activation_status: "intake_submitted_pending_pearl_int_processing",
      },
      targets: {
        functional_minimums: readinessTargets,
      },
      materials: {
        teachings: {
          doctrine_text: doctrineText,
          blocks: filledTeachings,
          urls: teachingUrls,
        },
        reflections_integrations_text: reflectionBits.join("\n\n"),
        topics_personas_text: topicsBits.join("\n\n"),
        voice: {
          language_rules: voiceBits.join("\n\n"),
          forbidden_language: forbiddenBits.join("\n\n"),
        },
        stories: filledStories.map((s) => ({
          title: s.type,
          type: s.type,
          context: s.text,
          point: "",
          source: s.url,
          files: s.files || [],
        })),
        practices: filledPractices.map((p) => ({
          name: p.type,
          type: p.type,
          origin: p.url,
          helpsWith: "",
          guidance: p.text,
          caution: "",
          files: p.files || [],
        })),
        quotes: quoteRows.map((q) => ({
          text: q.text,
          source: q.note || q.url,
          url: q.url,
          files: q.files || [],
          usage: "approved",
        })),
        language_rows: filledLanguage,
        urls: allUrls.map((url) => ({ label: "", url, kind: "teaching" })),
        links: allUrls,
        uploads: {
          links: allUrls,
          files: allFiles,
          rights_provenance_notes: "",
        },
        files: allFiles,
      },
      operator_next_steps: [
        "Verify rights, consent, public/private source boundaries, and provenance.",
        "Pearl_Int normalizes raw sources into teacher bank intake assets.",
        "Pearl Writer mines candidate doctrine, story, practice, quote, reflection, and integration atoms.",
        "Human/operator approval promotes candidate atoms into approved_atoms.",
        "Teacher production gates verify no placeholders, no runtime LLM, and enough slot coverage.",
        "Do not create production teacher atoms in this client.",
      ],
    };
  }, [
    teacherId,
    identity,
    rights,
    counts,
    readiness,
    missingMinimums,
    recommendedGaps,
    teachings,
    stories,
    practices,
    languageRows,
    allContentEntries,
  ]);

  const resumeAbsoluteUrl = useMemo(() => {
    if (!draftMeta.edit_token) return "";
    const path =
      draftMeta.resume_path ||
      `/teacher_onboarding.html?edit_token=${encodeURIComponent(draftMeta.edit_token)}`;
    try {
      return new URL(path, window.location.origin).toString();
    } catch {
      return `${window.location.origin}${path.startsWith("/") ? "" : "/"}${path}`;
    }
  }, [draftMeta]);

  const persistDraft = async () => {
    const payload = {
      teacher_name: identity.teacherName.trim(),
      teacher_id: teacherId,
      ui_state: collectUiState(),
    };
    let response;
    if (draftMeta.draft_id && draftMeta.edit_token) {
      response = await fetch(`/api/teacher-onboarding/drafts/${encodeURIComponent(draftMeta.draft_id)}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "X-Edit-Token": draftMeta.edit_token,
        },
        body: JSON.stringify({ ...payload, edit_token: draftMeta.edit_token }),
      });
    } else {
      response = await fetch("/api/teacher-onboarding/drafts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    }
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(body.detail || `Save failed (${response.status})`);
    }
    const edit_token = body.edit_token || draftMeta.edit_token;
    const resume_path =
      body.resume_path ||
      `/teacher_onboarding.html?edit_token=${encodeURIComponent(edit_token)}`;
    const meta = {
      draft_id: body.draft_id || draftMeta.draft_id,
      edit_token,
      status: body.status || "draft",
      resume_path,
    };
    setDraftMeta(meta);
    const next = new URL(window.location.href);
    next.searchParams.set("edit_token", edit_token);
    window.history.replaceState({}, "", next.toString());
    return meta;
  };

  const saveDraft = async () => {
    setDraftState({ status: "saving", detail: "Saving draft…" });
    try {
      await persistDraft();
      setDraftState({ status: "saved", detail: "Draft saved. Keep your private resume link." });
    } catch (err) {
      setDraftState({
        status: err.message?.includes("503") ? "unconfigured" : "error",
        detail: err.message,
      });
    }
  };

  const deleteDraft = async () => {
    if (!draftMeta.draft_id || !draftMeta.edit_token) return;
    if (!window.confirm("Delete this draft? Submissions are never deleted from this action.")) return;
    setDraftState({ status: "deleting", detail: "Deleting draft…" });
    try {
      const response = await fetch(
        `/api/teacher-onboarding/drafts/${encodeURIComponent(draftMeta.draft_id)}?edit_token=${encodeURIComponent(draftMeta.edit_token)}`,
        { method: "DELETE", headers: { "X-Edit-Token": draftMeta.edit_token } }
      );
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        setDraftState({ status: "error", detail: body.detail || "Delete failed" });
        return;
      }
      setDraftMeta({ draft_id: "", edit_token: "", status: "", resume_path: "" });
      const next = new URL(window.location.href);
      next.searchParams.delete("edit_token");
      next.searchParams.delete("token");
      window.history.replaceState({}, "", next.toString());
      setDraftState({ status: "deleted", detail: "Draft deleted." });
    } catch (err) {
      setDraftState({ status: "error", detail: err.message });
    }
  };

  const rotateToken = async () => {
    if (!draftMeta.draft_id || !draftMeta.edit_token) return;
    setDraftState({ status: "rotating", detail: "Rotating edit token…" });
    try {
      const response = await fetch(
        `/api/teacher-onboarding/drafts/${encodeURIComponent(draftMeta.draft_id)}/rotate-token`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-Edit-Token": draftMeta.edit_token },
          body: JSON.stringify({ edit_token: draftMeta.edit_token }),
        }
      );
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        setDraftState({ status: "error", detail: body.detail || "Rotate failed" });
        return;
      }
      setDraftMeta({
        draft_id: body.draft_id || draftMeta.draft_id,
        edit_token: body.edit_token,
        status: "draft",
        resume_path: body.resume_path,
      });
      const next = new URL(window.location.href);
      next.searchParams.set("edit_token", body.edit_token);
      window.history.replaceState({}, "", next.toString());
      setDraftState({ status: "rotated", detail: "Edit token rotated. Old resume links no longer work." });
    } catch (err) {
      setDraftState({ status: "error", detail: err.message });
    }
  };

  const submitPacket = async () => {
    if (!canSubmit) return;
    setSubmitState({ status: "submitting" });
    try {
      let meta = draftMeta;
      try {
        meta = await persistDraft();
      } catch (err) {
        // Draft save may fail if R2 unconfigured; still attempt submit.
        console.warn("draft persist before activate:", err.message);
      }

      const outbound = {
        ...packet,
        ...(meta.draft_id && meta.edit_token
          ? { draft_id: meta.draft_id, edit_token: meta.edit_token }
          : {}),
      };
      const response = await fetch("/api/teacher-onboarding/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(outbound),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        setSubmitState({
          status: response.status === 503 ? "unconfigured" : "error",
          response: body,
        });
        return;
      }
      if (meta.draft_id) {
        setDraftMeta((current) => ({ ...current, ...meta, status: "submitted" }));
      }
      setSubmitState({ status: "success", response: body, resumeMeta: meta });
    } catch (error) {
      setSubmitState({ status: "error", response: { detail: error.message } });
    }
  };

  const copyResumeUrl = async () => {
    if (!resumeAbsoluteUrl) return;
    try {
      await navigator.clipboard.writeText(resumeAbsoluteUrl);
      setCopiedUrl(true);
      setTimeout(() => setCopiedUrl(false), 2000);
    } catch {
      /* ignore */
    }
  };

  if (submitState.status === "success") {
    const url =
      resumeAbsoluteUrl ||
      (submitState.resumeMeta?.edit_token
        ? new URL(
            submitState.resumeMeta.resume_path ||
              `/teacher_onboarding.html?edit_token=${encodeURIComponent(submitState.resumeMeta.edit_token)}`,
            window.location.origin
          ).toString()
        : "");
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#0e0a06] px-4 text-stone-100">
        <div className="w-full max-w-xl rounded-2xl border border-amber-900/30 bg-[#1c1009]/90 p-8 text-center shadow-2xl shadow-black/40">
          <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-full bg-amber-700/30 text-amber-400">
            <CheckCircle2 size={32} />
          </div>
          <div className="text-[10px] uppercase tracking-[0.22em] text-amber-500">{t("success.kicker")}</div>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight text-stone-50">{t("success.heading")}</h1>
          <p className="mt-3 text-sm leading-6 text-stone-300">
            {t("success.body_prefix")}{" "}
            <span className="font-medium text-amber-300">{identity.teacherName || teacherId}</span>{" "}
            {t("success.body_suffix")}
          </p>
          {url ? (
            <div className="mt-6 rounded-lg border border-amber-900/35 bg-black/30 p-4 text-left">
              <div className="text-[10px] uppercase tracking-[0.18em] text-stone-500">{t("success.return_url_kicker")}</div>
              <p className="mt-2 break-all font-mono text-xs leading-5 text-amber-300">{url}</p>
              <button
                type="button"
                onClick={copyResumeUrl}
                className="mt-3 inline-flex items-center gap-2 rounded-md border border-amber-800/40 px-3 py-2 text-xs text-amber-400 hover:border-amber-500"
              >
                <Copy size={14} />
                {copiedUrl ? t("success.copied") : t("success.copy_link")}
              </button>
            </div>
          ) : (
            <p className="mt-6 text-sm text-amber-400">
              {t("success.no_url")}
            </p>
          )}
          <div className="mt-6 flex flex-col gap-2 sm:flex-row sm:justify-center">
            {url ? (
              <a
                href={url}
                className="inline-flex items-center justify-center gap-2 rounded-md bg-amber-700 px-5 py-3 text-sm font-medium text-white hover:bg-amber-600"
              >
                {t("success.continue_editing")}
              </a>
            ) : null}
            <a
              href="/teacher_onboarding.html"
              className="inline-flex items-center justify-center gap-2 rounded-md border border-amber-800/40 px-5 py-3 text-sm text-amber-400 hover:border-amber-500"
            >
              {t("success.start_another")}
            </a>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#0e0a06] text-stone-100">
      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 lg:grid-cols-[320px_1fr] lg:px-8">
        <aside className="lg:sticky lg:top-6 lg:h-[calc(100vh-3rem)] lg:overflow-y-auto">
          <div className="rounded-lg border border-amber-900/30 bg-[#1c1009]/80 p-5 shadow-2xl shadow-black/30">
            <div className="mb-5 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-amber-700 text-white">
                <Sparkles size={20} />
              </div>
              <div>
                <div className="text-[10px] uppercase tracking-[0.2em] text-amber-500">{t("chrome.brand_kicker")}</div>
                <h1 className="text-2xl leading-none">{t("chrome.brand_title")}</h1>
              </div>
            </div>

            <p className="text-sm leading-6 text-stone-300">
              {t("chrome.brand_blurb")}
            </p>

            <div className="mt-5 space-y-4">
              <div>
                <div className="mb-2 flex justify-between text-xs text-stone-400">
                  <span>{t("chrome.functional_label")}</span>
                  <span>{readiness.functional}%</span>
                </div>
                <ProgressBar value={readiness.functional} />
              </div>
              <div>
                <div className="mb-2 flex justify-between text-xs text-stone-400">
                  <span>{t("chrome.scale_label")}</span>
                  <span>{readiness.scale}%</span>
                </div>
                <ProgressBar value={readiness.scale} />
              </div>
            </div>

            <div className="mt-5 rounded-md border border-amber-900/30 bg-black/20 p-4">
              <div className="text-[10px] uppercase tracking-[0.18em] text-stone-500">{t("chrome.activation_truth_kicker")}</div>
              <p className="mt-2 text-sm leading-6 text-stone-300">
                {t("chrome.activation_truth_body")}
              </p>
            </div>

            <div className="mt-5 rounded-md border border-amber-900/30 bg-black/20 p-4" data-testid="draft-panel">
              <div className="text-[10px] uppercase tracking-[0.18em] text-stone-500">{t("chrome.draft_kicker")}</div>
              <p className="mt-2 text-xs leading-5 text-stone-400">
                {t("chrome.draft_blurb")}
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={saveDraft}
                  disabled={draftState.status === "saving"}
                  className="inline-flex items-center gap-1.5 rounded-md border border-amber-700/50 px-3 py-1.5 text-xs text-amber-300 hover:border-amber-500"
                >
                  {draftState.status === "saving" ? <Loader2 className="animate-spin" size={14} /> : <Save size={14} />}
                  {t("chrome.save_draft")}
                </button>
                {draftMeta.edit_token ? (
                  <>
                    <button
                      type="button"
                      onClick={rotateToken}
                      className="rounded-md border border-amber-900/40 px-3 py-1.5 text-xs text-stone-300 hover:border-amber-600"
                    >
                      {t("chrome.rotate_token")}
                    </button>
                    <button
                      type="button"
                      onClick={deleteDraft}
                      className="rounded-md border border-red-900/40 px-3 py-1.5 text-xs text-red-300 hover:border-red-600"
                    >
                      {t("chrome.delete_draft")}
                    </button>
                  </>
                ) : null}
              </div>
              {draftMeta.draft_id ? (
                <div className="mt-3 space-y-1 text-[11px] text-stone-500" data-testid="draft-meta">
                  <div>
                    Draft: <span className="font-mono text-stone-300">{draftMeta.draft_id}</span>
                  </div>
                  <div>
                    Status: <span className="text-amber-400">{draftMeta.status || "draft"}</span>
                  </div>
                  {resumeAbsoluteUrl ? (
                    <div className="break-all">
                      Resume:{" "}
                      <span className="font-mono text-stone-400" data-testid="resume-path">
                        {resumeAbsoluteUrl}
                      </span>
                    </div>
                  ) : null}
                </div>
              ) : null}
              {draftState.status !== "idle" ? (
                <p className="mt-2 text-xs text-stone-300" data-testid="draft-status">
                  {draftState.detail}
                </p>
              ) : null}
              <a
                href="/teacher_operator_queue.html"
                className="mt-3 inline-block text-xs text-amber-500/90 hover:text-amber-400"
              >
                {t("chrome.operator_queue")}
              </a>
            </div>

            <button
              type="button"
              onClick={clearLocale}
              className="mt-5 w-full rounded-md border border-amber-900/30 px-3 py-2 text-left text-xs text-amber-400 hover:border-amber-600"
              data-testid="change-display-language"
            >
              {t("chrome.change_language")} ({locale})
            </button>
            <nav className="mt-5 grid grid-cols-2 gap-2 text-xs text-stone-400" aria-label={t("chrome.nav_aria")}>
              {[
                ["identity", t("chrome.nav_identity")],
                ["rights", t("chrome.nav_rights")],
                ["teachings", t("chrome.nav_teachings")],
                ["stories", t("chrome.nav_stories")],
                ["practices", t("chrome.nav_practices")],
                ["voice", t("chrome.nav_voice")],
                ["activate", t("chrome.nav_activate")],
              ].map(([id, label]) => (
                <a
                  key={id}
                  href={`#${id}`}
                  className="rounded-md border border-amber-900/25 bg-black/20 px-3 py-2 hover:border-amber-700 hover:text-amber-400"
                >
                  {label}
                </a>
              ))}
            </nav>

            <div className="mt-5 space-y-2">
              {targetRows.map((item) => {
                const minPct = Math.min(100, Math.round(item.minRatio * 100));
                return (
                  <div key={item.key} className="rounded-md border border-amber-900/20 bg-black/20 p-3">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="text-sm text-stone-100">{item.label}</div>
                        <div className="mt-1 text-xs text-stone-500">
                          {item.count} / {item.min || "recommended"} minimum · {item.preferred} preferred
                        </div>
                      </div>
                      {item.min === 0 || item.count >= item.min ? (
                        <CheckCircle2 className="mt-0.5 text-green-400" size={17} />
                      ) : (
                        <AlertTriangle className="mt-0.5 text-amber-500" size={17} />
                      )}
                    </div>
                    <div className="mt-3">
                      <ProgressBar value={minPct} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </aside>

        <div className="space-y-6">
          <header className="rounded-lg border border-amber-900/25 bg-[#1c1009]/70 p-6">
            <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
              <div>
                <div className="text-[10px] uppercase tracking-[0.22em] text-amber-500">{t("header.kicker")}</div>
                <h2 className="mt-2 max-w-3xl text-4xl leading-tight">
                  {t("header.title")}
                </h2>
              </div>
              <div className="rounded-md border border-amber-900/25 bg-black/20 px-4 py-3 text-sm text-stone-300">
                <span className="text-stone-500">{t("header.teacher_id_label")}</span>{" "}
                <span className="font-mono text-amber-400">{teacherId}</span>
              </div>
            </div>
          </header>

          <Section id="identity" icon={User} kicker={t("identity.kicker")} title={t("identity.heading")}>
            <div className="grid gap-4 md:grid-cols-2">
              <Field label={t("identity.teacher_name")}>
                <TextInput
                  value={identity.teacherName}
                  onChange={(e) => setIdentity({ ...identity, teacherName: e.target.value })}
                  placeholder={t("identity.name_placeholder")}
                />
              </Field>
              <Field label={t("identity.teacher_id")}>
                <TextInput
                  value={identity.teacherId || teacherId}
                  onChange={(e) => {
                    setTeacherIdOverridden(true);
                    setIdentity({ ...identity, teacherId: slugify(e.target.value) });
                  }}
                  placeholder={t("identity.id_placeholder")}
                />
              </Field>
              <Field label={t("identity.tradition")}>
                <TextInput
                  value={identity.tradition}
                  onChange={(e) => setIdentity({ ...identity, tradition: e.target.value })}
                  placeholder={t("identity.tradition_placeholder")}
                />
              </Field>
              <Field label={t("identity.language_label")} hint={t("identity.language_hint")}>
                <SelectInput
                  value={identity.language}
                  onChange={(e) => setIdentity({ ...identity, language: e.target.value })}
                >
                  {REPO_LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.label} ({lang.code})
                    </option>
                  ))}
                </SelectInput>
              </Field>
              <Field label={t("identity.contact_name")}>
                <TextInput
                  value={identity.contactName}
                  onChange={(e) => setIdentity({ ...identity, contactName: e.target.value })}
                  placeholder={t("identity.contact_name_placeholder")}
                />
              </Field>
              <Field label={t("identity.contact_email")}>
                <TextInput
                  type="email"
                  value={identity.contactEmail}
                  onChange={(e) => setIdentity({ ...identity, contactEmail: e.target.value })}
                  placeholder={t("identity.contact_email_placeholder")}
                />
              </Field>
              <Field label={t("identity.website")}>
                <TextInput
                  value={identity.website}
                  onChange={(e) => setIdentity({ ...identity, website: e.target.value })}
                  placeholder={t("identity.website_placeholder")}
                />
              </Field>
            </div>
            <div className="mt-4">
              <Field
                label={t("identity.bio_label")}
                hint={t("identity.bio_hint")}
              >
                <ContentEntryInput
                  value={identity.teacherBio}
                  onChange={(next) => setIdentity({ ...identity, teacherBio: next })}
                  textPlaceholder={t("identity.bio_placeholder")}
                />
              </Field>
            </div>
          </Section>

          <Section id="rights" icon={ShieldCheck} kicker={t("rights.kicker")} title={t("rights.heading")}>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="flex gap-3 rounded-md border border-amber-900/25 bg-black/20 p-4 text-sm leading-6 text-stone-300">
                <input
                  type="checkbox"
                  checked={rights.ownsMaterial}
                  onChange={(e) => setRights({ ...rights, ownsMaterial: e.target.checked })}
                  className="mt-1 h-4 w-4 accent-amber-600"
                />
                {t("rights.owns_material")}
              </label>
              <label className="flex gap-3 rounded-md border border-amber-900/25 bg-black/20 p-4 text-sm leading-6 text-stone-300">
                <input
                  type="checkbox"
                  checked={rights.processingConsent}
                  onChange={(e) => setRights({ ...rights, processingConsent: e.target.checked })}
                  className="mt-1 h-4 w-4 accent-amber-600"
                />
                {t("rights.processing_consent")}
              </label>
              <label className="flex gap-3 rounded-md border border-amber-900/25 bg-black/20 p-4 text-sm leading-6 text-stone-300">
                <input
                  type="checkbox"
                  checked={rights.noUnauthorizedCopyright}
                  onChange={(e) => setRights({ ...rights, noUnauthorizedCopyright: e.target.checked })}
                  className="mt-1 h-4 w-4 accent-amber-600"
                />
                {t("rights.no_unauthorized")}
              </label>
              <label className="flex gap-3 rounded-md border border-amber-900/25 bg-black/20 p-4 text-sm leading-6 text-stone-300">
                <input
                  type="checkbox"
                  checked={rights.consent}
                  onChange={(e) => setRights({ ...rights, consent: e.target.checked })}
                  className="mt-1 h-4 w-4 accent-amber-600"
                />
                {t("rights.final_consent")}
              </label>
              <Field label={t("rights.public_boundaries")}>
                <TextArea
                  value={rights.publicBoundaries}
                  onChange={(e) => setRights({ ...rights, publicBoundaries: e.target.value })}
                  placeholder={t("rights.public_placeholder")}
                />
              </Field>
              <Field label={t("rights.private_boundaries")}>
                <TextArea
                  value={rights.privateBoundaries}
                  onChange={(e) => setRights({ ...rights, privateBoundaries: e.target.value })}
                  placeholder={t("rights.private_placeholder")}
                />
              </Field>
            </div>
          </Section>

          <Section id="teachings" icon={BookOpen} kicker={t("teachings.kicker")} title={t("teachings.heading")}>
            <p className="mb-4 text-sm leading-6 text-stone-400">
              {t("teachings.blurb")}
            </p>
            <RowList
              rows={teachings}
              setRows={setTeachings}
              starter={starterTeaching}
              addLabel={t("teachings.add_label")}
              renderRow={(row, updateRow, index) => (
                <ContentEntryInput
                  value={row}
                  onChange={(next) => updateRow(index, next)}
                  textPlaceholder={t("teachings.placeholder")}
                  hint={t("teachings.hint")}
                />
              )}
            />
          </Section>

          <Section id="stories" icon={ClipboardList} kicker={t("stories.kicker")} title={t("stories.heading")}>
            <p className="mb-4 text-sm leading-6 text-stone-400">
              {t("stories.blurb")}
            </p>
            <RowList
              rows={stories}
              setRows={setStories}
              starter={starterStory}
              addLabel={t("stories.add_label")}
              minRows={3}
              renderRow={(row, updateRow, index) => (
                <div className="space-y-3">
                  <Field label={t("stories.type_label")}>
                    <SelectInput value={row.type} onChange={(e) => updateRow(index, { type: e.target.value })}>
                      {STORY_TYPES.map((t) => (
                        <option key={t} value={t}>
                          {t}
                        </option>
                      ))}
                    </SelectInput>
                  </Field>
                  <ContentEntryInput
                    value={row}
                    onChange={(next) => updateRow(index, next)}
                    textPlaceholder={t("stories.placeholder")}
                  />
                </div>
              )}
            />
          </Section>

          <Section id="practices" icon={Sparkles} kicker={t("practices.kicker")} title={t("practices.heading")}>
            <p className="mb-4 text-sm leading-6 text-stone-400">
              {t("practices.blurb")}
            </p>
            <RowList
              rows={practices}
              setRows={setPractices}
              starter={starterPractice}
              addLabel={t("practices.add_label")}
              minRows={3}
              renderRow={(row, updateRow, index) => (
                <div className="space-y-3">
                  <Field label={t("practices.type_label")}>
                    <SelectInput value={row.type} onChange={(e) => updateRow(index, { type: e.target.value })}>
                      {PRACTICE_TYPES.map((t) => (
                        <option key={t} value={t}>
                          {t}
                        </option>
                      ))}
                    </SelectInput>
                  </Field>
                  <ContentEntryInput
                    value={row}
                    onChange={(next) => updateRow(index, next)}
                    textPlaceholder={t("practices.placeholder")}
                  />
                </div>
              )}
            />
          </Section>

          <Section id="voice" icon={BookOpen} kicker={t("voice.kicker")} title={t("voice.heading")}>
            <p className="mb-4 text-sm leading-6 text-stone-400">
              {t("voice.blurb")}
            </p>
            <RowList
              rows={languageRows}
              setRows={setLanguageRows}
              starter={() => starterLanguageRow("quote")}
              addLabel={t("voice.add_label")}
              minRows={5}
              renderRow={(row, updateRow, index) => (
                <div className="space-y-3">
                  <Field label={t("voice.entry_type")}>
                    <SelectInput value={row.kind} onChange={(e) => updateRow(index, { kind: e.target.value })}>
                      {LANGUAGE_ROW_TYPES.map((t) => (
                        <option key={t.id} value={t.id}>
                          {t.label}
                        </option>
                      ))}
                    </SelectInput>
                  </Field>
                  {row.kind === "quote" ? (
                    <Field label={t("voice.source_note")}>
                      <TextInput
                        value={row.note || ""}
                        onChange={(e) => updateRow(index, { note: e.target.value })}
                        placeholder={t("voice.source_placeholder")}
                      />
                    </Field>
                  ) : null}
                  <ContentEntryInput
                    value={row}
                    onChange={(next) => updateRow(index, next)}
                    textPlaceholder={
                      LANGUAGE_ROW_TYPES.find((rowType) => rowType.id === row.kind)?.label ||
                      t("voice.content_placeholder")
                    }
                  />
                </div>
              )}
            />
          </Section>

          <Section id="activate" icon={Link} kicker={t("activate.kicker")} title={t("activate.heading")}>
            <div className="space-y-5">
              <div className="rounded-md border border-amber-900/25 bg-black/20 p-5">
                <div className="flex items-start gap-3">
                  {canSubmit ? (
                    <CheckCircle2 className="text-green-400" size={21} />
                  ) : (
                    <AlertTriangle className="text-amber-500" size={21} />
                  )}
                  <div>
                    <h3 className="text-xl">{t("activate.ready_title")}</h3>
                    <p className="mt-2 text-sm leading-6 text-stone-300">
                      {t("activate.ready_body")}
                    </p>
                  </div>
                </div>
                <div className="mt-5 grid gap-2 text-sm text-stone-400">
                  <div>
                    {t("activate.teacher_name")}{" "}
                    {identity.teacherName ? (
                      <span className="text-stone-100">{identity.teacherName}</span>
                    ) : (
                      t("activate.missing")
                    )}
                  </div>
                  <div>
                    {t("activate.contact_email")}{" "}
                    {contactEmailValid ? (
                      <span className="text-stone-100">{identity.contactEmail}</span>
                    ) : (
                      t("activate.missing_or_invalid")
                    )}
                  </div>
                  <div>
                    {t("activate.processing_permission")}{" "}
                    {rights.ownsMaterial && rights.processingConsent ? (
                      <span className="text-green-400">{t("activate.ready")}</span>
                    ) : (
                      t("activate.missing")
                    )}
                  </div>
                  <div>
                    {t("activate.final_consent")}{" "}{rights.consent ? <span className="text-green-400">{t("activate.ready")}</span> : t("activate.missing")}
                  </div>
                  <div>
                    {t("activate.source_material")}{" "}{hasMaterial ? <span className="text-green-400">{t("activate.present")}</span> : t("activate.missing")}
                  </div>
                </div>
                {validationMessages.length ? (
                  <div className="mt-4 grid gap-2 text-sm text-amber-400">
                    {validationMessages.map((message) => (
                      <div key={message} className="flex items-start gap-2">
                        <AlertTriangle className="mt-0.5 shrink-0" size={15} />
                        <span>{message}</span>
                      </div>
                    ))}
                  </div>
                ) : null}
              </div>

              {missingMinimums.length ? (
                <div className="rounded-md border border-amber-900/25 bg-black/20 p-5">
                  <div className="text-[10px] uppercase tracking-[0.18em] text-amber-500">{t("activate.depth_kicker")}</div>
                  <p className="mt-2 text-xs text-stone-500">
                    {t("activate.depth_blurb")}
                  </p>
                  <div className="mt-3 grid gap-2 text-sm text-stone-300">
                    {missingMinimums.slice(0, 8).map((gap) => (
                      <div key={gap.key} className="flex items-start gap-2">
                        <AlertTriangle className="mt-0.5 shrink-0 text-amber-500" size={15} />
                        <span>
                          {gap.label}: {gap.count}/{gap.minimum}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}

              <button
                type="button"
                onClick={submitPacket}
                disabled={!canSubmit || submitState.status === "submitting"}
                className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-amber-700 px-5 py-3 text-sm font-medium text-white transition hover:bg-amber-600 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {submitState.status === "submitting" ? (
                  <Loader2 className="animate-spin" size={17} />
                ) : (
                  <Sparkles size={17} />
                )}
                {t("activate.submit")}
              </button>

              {submitState.status === "error" || submitState.status === "unconfigured" ? (
                <div className="rounded-md border border-red-900/40 bg-black/25 p-4 text-sm text-red-300">
                  {submitState.response?.detail || t("activate.submit_failed")}
                </div>
              ) : null}
            </div>
          </Section>
        </div>
      </div>
    </main>
  );
}


export default function TeacherOnboarding() {
  const { locale, t, clearLocale, ready } = useTeacherOnboardingI18n();

  // Flag-first gate: no sidebar / sections until a market locale is chosen.
  if (!locale) {
    return <FlagLocaleGate />;
  }
  if (!ready) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#0e0a06] text-stone-300" data-testid="teacher-onboarding-locale-loading">
        <Loader2 className="animate-spin text-amber-500" size={28} />
      </main>
    );
  }

  return <TeacherOnboardingForm locale={locale} t={t} clearLocale={clearLocale} />;
}
