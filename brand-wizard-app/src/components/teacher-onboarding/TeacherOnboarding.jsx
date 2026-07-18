import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  BookOpen,
  CheckCircle2,
  Clipboard,
  ClipboardList,
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

const ACCEPTED_SOURCE_TYPES = ".txt,.md,.pdf,.doc,.docx,.rtf,.csv,.json,.yaml,.yml";

const readinessTargets = [
  {
    key: "teachings",
    label: "Teachings / Doctrine",
    min: 4,
    preferred: 12,
    scale: 100,
    help: "12+ preferred; core principles, doctrine fragments, frameworks, and repeated teaching points.",
  },
  {
    key: "hooks",
    label: "Hooks",
    min: 12,
    preferred: 12,
    scale: 50,
    help: "Openers and attention bridges that sound like the teacher.",
  },
  {
    key: "scenes",
    label: "Scenes",
    min: 12,
    preferred: 12,
    scale: 50,
    help: "Lived scenes, sensory moments, teaching rooms, and real-world examples.",
  },
  {
    key: "stories",
    label: "Teacher Stories",
    min: 20,
    preferred: 20,
    scale: 60,
    help: "Composite, lived, or witnessed stories with beginning/middle/end progression.",
  },
  {
    key: "practices",
    label: "Exercises / Practices",
    min: 12,
    preferred: 40,
    scale: 60,
    help: "40+ preferred; five-layer practices with guidance, aha, integration, and cautions.",
  },
  {
    key: "reflections",
    label: "Reflections",
    min: 12,
    preferred: 12,
    scale: 60,
    help: "Reader-facing reflection prompts in the teacher's idiom.",
  },
  {
    key: "integrations",
    label: "Integrations",
    min: 12,
    preferred: 12,
    scale: 60,
    help: "Bridges from insight into lived next action.",
  },
  {
    key: "pivots",
    label: "Pivots",
    min: 15,
    preferred: 15,
    scale: 15,
    help: "Teacher-specific reframes and turnarounds.",
  },
  {
    key: "threads",
    label: "Threads",
    min: 15,
    preferred: 15,
    scale: 15,
    help: "Recurring themes that can connect chapters and books.",
  },
  {
    key: "permissions",
    label: "Permissions",
    min: 15,
    preferred: 15,
    scale: 15,
    help: "Compassionate permission lines and boundary-setting moves.",
  },
  {
    key: "takeaways",
    label: "Takeaways",
    min: 15,
    preferred: 15,
    scale: 15,
    help: "Portable closing lessons and concise teaching summaries.",
  },
  {
    key: "quotes",
    label: "Quotes / Phrases",
    min: 0,
    preferred: 12,
    scale: 100,
    help: "Recommended, especially if the teacher has public quotes or excerpts.",
  },
  {
    key: "raw_sources",
    label: "Source Files / URLs",
    min: 1,
    preferred: 8,
    scale: 12,
    help: "Books, talks, transcripts, recordings, articles, notes, and pages with provenance.",
  },
];

const starterStory = {
  title: "",
  context: "",
  point: "",
  source: "",
  consent: "owned_or_composite",
};

const starterPractice = {
  name: "",
  origin: "",
  helpsWith: "",
  guidance: "",
  caution: "",
};

const starterQuote = {
  text: "",
  source: "",
  usage: "approved",
};

const starterUrl = {
  label: "",
  url: "",
  kind: "teaching",
};

function slugify(value) {
  return (
    String(value || "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 80) || "teacher"
  );
}

function splitCount(value) {
  return String(value || "")
    .split(/\n{2,}|\n[-*]\s+|\n\d+\.\s+/)
    .map((part) => part.trim())
    .filter((part) => part.length > 24).length;
}

function splitEntries(value) {
  return String(value || "")
    .split(/\n+/)
    .map((part) => part.trim())
    .filter(Boolean);
}

function countFilledRows(rows, fields) {
  return rows.filter((row) => fields.some((field) => String(row[field] || "").trim().length > 0)).length;
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
      className={`min-h-[128px] w-full resize-y rounded-md border border-amber-900/30 bg-black/25 px-3 py-3 text-sm leading-6 text-stone-100 outline-none transition focus:border-amber-600 ${props.className || ""}`}
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

function RowList({ rows, setRows, starter, renderRow, addLabel }) {
  const updateRow = (index, patch) => {
    setRows(rows.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  };
  const removeRow = (index) => {
    setRows(rows.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-3">
      {rows.map((row, index) => (
        <div key={index} className="rounded-md border border-amber-900/20 bg-black/20 p-4">
          <div className="mb-3 flex items-center justify-between gap-3">
            <div className="text-[11px] uppercase tracking-[0.16em] text-stone-500">Entry {index + 1}</div>
            {rows.length > 1 ? (
              <button
                type="button"
                onClick={() => removeRow(index)}
                className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-amber-900/30 text-stone-400 hover:border-amber-700 hover:text-amber-400"
                aria-label={`Remove entry ${index + 1}`}
                title={`Remove entry ${index + 1}`}
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
        onClick={() => setRows([...rows, { ...starter }])}
        className="inline-flex items-center gap-2 rounded-md border border-amber-800/40 px-4 py-2 text-sm text-amber-400 hover:border-amber-500"
      >
        <Plus size={16} />
        {addLabel}
      </button>
    </div>
  );
}

export default function TeacherOnboarding() {
  const [identity, setIdentity] = useState({
    teacherName: "",
    teacherId: "",
    tradition: "",
    languages: "en_US",
    website: "",
    contactName: "",
    contactEmail: "",
    teacherBio: "",
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
  const [teachingsText, setTeachingsText] = useState("");
  const [reflectionText, setReflectionText] = useState("");
  const [topicsText, setTopicsText] = useState("");
  const [voiceText, setVoiceText] = useState("");
  const [forbiddenLanguageText, setForbiddenLanguageText] = useState("");
  const [uploadLinksText, setUploadLinksText] = useState("");
  const [provenanceNotes, setProvenanceNotes] = useState("");
  const [stories, setStories] = useState([{ ...starterStory }]);
  const [practices, setPractices] = useState([{ ...starterPractice }]);
  const [quotes, setQuotes] = useState([{ ...starterQuote }]);
  const [urls, setUrls] = useState([{ ...starterUrl }]);
  const [files, setFiles] = useState([]);
  const [submitState, setSubmitState] = useState({ status: "idle" });
  const [draftMeta, setDraftMeta] = useState({
    draft_id: "",
    edit_token: "",
    status: "",
    resume_path: "",
  });
  const [draftState, setDraftState] = useState({ status: "idle", detail: "" });

  const teacherId = identity.teacherId.trim() || slugify(identity.teacherName);

  const collectUiState = () => ({
    identity,
    rights,
    teacherIdOverridden,
    teachingsText,
    reflectionText,
    topicsText,
    voiceText,
    forbiddenLanguageText,
    uploadLinksText,
    provenanceNotes,
    stories,
    practices,
    quotes,
    urls,
    files,
  });

  const hydrateUiState = (ui) => {
    if (!ui || typeof ui !== "object") return;
    if (ui.identity) setIdentity((current) => ({ ...current, ...ui.identity }));
    if (ui.rights) setRights((current) => ({ ...current, ...ui.rights }));
    if (typeof ui.teacherIdOverridden === "boolean") setTeacherIdOverridden(ui.teacherIdOverridden);
    if (typeof ui.teachingsText === "string") setTeachingsText(ui.teachingsText);
    if (typeof ui.reflectionText === "string") setReflectionText(ui.reflectionText);
    if (typeof ui.topicsText === "string") setTopicsText(ui.topicsText);
    if (typeof ui.voiceText === "string") setVoiceText(ui.voiceText);
    if (typeof ui.forbiddenLanguageText === "string") setForbiddenLanguageText(ui.forbiddenLanguageText);
    if (typeof ui.uploadLinksText === "string") setUploadLinksText(ui.uploadLinksText);
    if (typeof ui.provenanceNotes === "string") setProvenanceNotes(ui.provenanceNotes);
    if (Array.isArray(ui.stories) && ui.stories.length) setStories(ui.stories);
    if (Array.isArray(ui.practices) && ui.practices.length) setPractices(ui.practices);
    if (Array.isArray(ui.quotes) && ui.quotes.length) setQuotes(ui.quotes);
    if (Array.isArray(ui.urls) && ui.urls.length) setUrls(ui.urls);
    if (Array.isArray(ui.files)) setFiles(ui.files);
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

  const counts = useMemo(() => {
    const reflectionCount = splitCount(reflectionText);
    const uploadLinkCount = splitEntries(uploadLinksText).length;
    const urlCount = countFilledRows(urls, ["url"]);
    return {
      teachings: splitCount(teachingsText) + countFilledRows(urls.filter((u) => u.kind === "teaching"), ["url", "label"]),
      hooks: 0,
      scenes: 0,
      stories: countFilledRows(stories, ["title", "context", "point"]),
      practices: countFilledRows(practices, ["name", "origin", "guidance"]),
      quotes: countFilledRows(quotes, ["text", "source"]),
      reflections: reflectionCount,
      integrations: reflectionCount,
      pivots: 0,
      threads: 0,
      permissions: 0,
      takeaways: 0,
      raw_sources: files.length + urlCount + uploadLinkCount,
    };
  }, [teachingsText, reflectionText, stories, practices, quotes, urls, files, uploadLinksText]);

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
        .map((item) => ({ key: item.key, label: item.label, count: item.count, minimum: item.min, missing: item.min - item.count })),
    [targetRows]
  );

  const recommendedGaps = useMemo(
    () =>
      targetRows
        .filter((item) => item.count < item.preferred)
        .map((item) => ({ key: item.key, label: item.label, count: item.count, preferred: item.preferred, missing: item.preferred - item.count })),
    [targetRows]
  );

  const hasMaterial =
    splitCount(teachingsText) > 0 ||
    countFilledRows(urls, ["url"]) > 0 ||
    splitEntries(uploadLinksText).length > 0 ||
    files.length > 0 ||
    countFilledRows(stories, ["title", "context", "point"]) > 0 ||
    countFilledRows(practices, ["name", "guidance"]) > 0;

  const contactEmailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(identity.contactEmail.trim());
  const validationMessages = [
    !identity.teacherName.trim() ? "Teacher name is required." : "",
    !identity.contactEmail.trim() ? "Contact email is required." : "",
    identity.contactEmail.trim() && !contactEmailValid ? "Contact email must be valid." : "",
    !rights.ownsMaterial ? "Own-voice or permission attestation is required." : "",
    !rights.processingConsent ? "Permission to process material into candidate atoms is required." : "",
    !rights.consent ? "Final consent checkbox is required." : "",
    !hasMaterial ? "Add at least one teaching, source URL, source link, file metadata entry, story, or practice." : "",
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
    const sourceUrls = urls
      .map((row) => ({
        label: row.label.trim(),
        url: row.url.trim(),
        kind: row.kind,
      }))
      .filter((row) => row.url || row.label);
    const uploadLinks = splitEntries(uploadLinksText);
    const activeStories = stories.filter((row) => ["title", "context", "point", "source"].some((field) => String(row[field] || "").trim()));
    const activePractices = practices.filter((row) => ["name", "origin", "helpsWith", "guidance", "caution"].some((field) => String(row[field] || "").trim()));
    const activeQuotes = quotes.filter((row) => ["text", "source"].some((field) => String(row[field] || "").trim()));
    return {
      schema_version: "teacher_onboarding_intake_v1",
      submitted_at: now,
      teacher_id: teacherId,
      teacher_name: identity.teacherName.trim(),
      identity: {
        public_teacher_name: identity.teacherName.trim(),
        teacher_id: teacherId,
        tradition_lineage_practice_family: identity.tradition.trim(),
        languages: splitEntries(identity.languages.replaceAll(",", "\n")),
        website: identity.website.trim(),
        contact_name: identity.contactName.trim(),
        contact_email: identity.contactEmail.trim(),
        teacher_bio: identity.teacherBio.trim(),
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
        catalog_scale_target: {
          teachings: "100+ teachings/doctrine fragments",
          stories: "60+ stories across emotional bands",
          practices: "60+ exercises/practices",
          reflections_integrations: "60+ reflections/integrations",
          hooks_scenes: "50+ hooks/scenes",
          quotes: "100+ quotes/source excerpts if available",
          provenance: "source files/URLs with rights/provenance",
        },
      },
      materials: {
        teachings: {
          doctrine_text: teachingsText,
          urls: sourceUrls.filter((row) => row.kind === "teaching").map((row) => row.url),
        },
        reflections_integrations_text: reflectionText,
        topics_personas_text: topicsText,
        voice: {
          language_rules: voiceText,
          forbidden_language: forbiddenLanguageText,
        },
        stories: activeStories,
        practices: activePractices,
        quotes: activeQuotes,
        urls: sourceUrls,
        links: [...sourceUrls.map((row) => row.url).filter(Boolean), ...uploadLinks],
        uploads: {
          links: uploadLinks,
          files,
          rights_provenance_notes: provenanceNotes.trim(),
        },
        files,
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
    teachingsText,
    reflectionText,
    topicsText,
    voiceText,
    forbiddenLanguageText,
    stories,
    practices,
    quotes,
    urls,
    files,
    uploadLinksText,
    provenanceNotes,
  ]);

  const handleFiles = (event) => {
    const selected = Array.from(event.target.files || []).map((file) => ({
      name: file.name,
      size: file.size,
      type: file.type || "unknown",
      last_modified: file.lastModified ? new Date(file.lastModified).toISOString() : null,
      upload_note: "metadata_only_in_v1_attach_or_R2_upload_in_followup_lane",
    }));
    setFiles((current) => [...current, ...selected]);
    event.target.value = "";
  };

  const downloadPacket = () => {
    const blob = new Blob([JSON.stringify(packet, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${teacherId}_teacher_onboarding_packet.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const copyPacket = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(packet, null, 2));
      setSubmitState({ status: "copied", response: { detail: "Teacher intake JSON copied to clipboard." } });
    } catch (_error) {
      setSubmitState({
        status: "copy_failed",
        response: { detail: "Clipboard unavailable. Use the payload preview or download JSON packet." },
      });
    }
  };

  const saveDraft = async () => {
    setDraftState({ status: "saving", detail: "Saving draft…" });
    const payload = {
      teacher_name: identity.teacherName.trim(),
      teacher_id: teacherId,
      ui_state: collectUiState(),
    };
    try {
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
        setDraftState({
          status: response.status === 503 ? "unconfigured" : "error",
          detail: body.detail || `Save failed (${response.status})`,
        });
        return;
      }
      const edit_token = body.edit_token || draftMeta.edit_token;
      const resume_path =
        body.resume_path ||
        `/teacher_onboarding.html?edit_token=${encodeURIComponent(edit_token)}`;
      setDraftMeta({
        draft_id: body.draft_id || draftMeta.draft_id,
        edit_token,
        status: body.status || "draft",
        resume_path,
      });
      const next = new URL(window.location.href);
      next.searchParams.set("edit_token", edit_token);
      window.history.replaceState({}, "", next.toString());
      setDraftState({ status: "saved", detail: `Draft saved. Resume with edit token (keep private).` });
    } catch (err) {
      setDraftState({ status: "error", detail: err.message });
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
      const outbound = {
        ...packet,
        ...(draftMeta.draft_id && draftMeta.edit_token
          ? { draft_id: draftMeta.draft_id, edit_token: draftMeta.edit_token }
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
      if (draftMeta.draft_id) {
        setDraftMeta((current) => ({ ...current, status: "submitted" }));
      }
      setSubmitState({ status: "success", response: body });
    } catch (error) {
      setSubmitState({ status: "error", response: { detail: error.message } });
    }
  };

  return (
    <main className="min-h-screen bg-[#0e0a06] text-stone-100">
      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 lg:grid-cols-[320px_1fr] lg:px-8">
        <aside className="lg:sticky lg:top-6 lg:h-[calc(100vh-3rem)]">
          <div className="rounded-lg border border-amber-900/30 bg-[#1c1009]/80 p-5 shadow-2xl shadow-black/30">
            <div className="mb-5 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-amber-700 text-white">
                <Sparkles size={20} />
              </div>
              <div>
                <div className="text-[10px] uppercase tracking-[0.2em] text-amber-500">Pearl Prime</div>
                <h1 className="text-2xl leading-none">Teacher Onboarding</h1>
              </div>
            </div>

            <p className="text-sm leading-6 text-stone-300">
              Submit the material Pearl_Int needs to turn a real teacher into a reviewed teacher-mode source.
            </p>

            <div className="mt-5 space-y-4">
              <div>
                <div className="mb-2 flex justify-between text-xs text-stone-400">
                  <span>Functional teacher bank</span>
                  <span>{readiness.functional}%</span>
                </div>
                <ProgressBar value={readiness.functional} />
              </div>
              <div>
                <div className="mb-2 flex justify-between text-xs text-stone-400">
                  <span>1000-book scale depth</span>
                  <span>{readiness.scale}%</span>
                </div>
                <ProgressBar value={readiness.scale} />
              </div>
            </div>

            <div className="mt-5 rounded-md border border-amber-900/30 bg-black/20 p-4">
              <div className="text-[10px] uppercase tracking-[0.18em] text-stone-500">Activation truth</div>
              <p className="mt-2 text-sm leading-6 text-stone-300">
                Activate submits intake. Official teacher status still requires source normalization, atom mining,
                human review, and teacher production gates.
              </p>
            </div>

            <div className="mt-5 rounded-md border border-amber-900/30 bg-black/20 p-4" data-testid="draft-panel">
              <div className="text-[10px] uppercase tracking-[0.18em] text-stone-500">Draft portal</div>
              <p className="mt-2 text-xs leading-5 text-stone-400">
                Save and resume with a private edit token. No login. Drafts only are deletable; submissions stay
                immutable. Production atoms are never created here.
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={saveDraft}
                  disabled={draftState.status === "saving"}
                  className="inline-flex items-center gap-1.5 rounded-md border border-amber-700/50 px-3 py-1.5 text-xs text-amber-300 hover:border-amber-500"
                >
                  {draftState.status === "saving" ? <Loader2 className="animate-spin" size={14} /> : <Save size={14} />}
                  Save draft
                </button>
                {draftMeta.edit_token ? (
                  <>
                    <button
                      type="button"
                      onClick={rotateToken}
                      className="rounded-md border border-amber-900/40 px-3 py-1.5 text-xs text-stone-300 hover:border-amber-600"
                    >
                      Rotate token
                    </button>
                    <button
                      type="button"
                      onClick={deleteDraft}
                      className="rounded-md border border-red-900/40 px-3 py-1.5 text-xs text-red-300 hover:border-red-600"
                    >
                      Delete draft
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
                  <div className="break-all">
                    Resume:{" "}
                    <span className="font-mono text-stone-400" data-testid="resume-path">
                      {draftMeta.resume_path}
                    </span>
                  </div>
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
                Operator queue →
              </a>
            </div>

            <nav className="mt-5 grid grid-cols-2 gap-2 text-xs text-stone-400" aria-label="Teacher onboarding sections">
              {[
                ["identity", "Identity"],
                ["rights", "Rights"],
                ["teachings", "Doctrine"],
                ["stories", "Stories"],
                ["practices", "Practices"],
                ["voice", "Language"],
                ["sources", "Sources"],
                ["activate", "Activate"],
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
                          {item.count} / {item.min || "recommended"} minimum · {item.preferred} preferred · {item.scale} scale
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
                <div className="text-[10px] uppercase tracking-[0.22em] text-amber-500">Teacher mode intake</div>
                <h2 className="mt-2 max-w-3xl text-4xl leading-tight">
                  Build the source packet before the system writes in a teacher's voice.
                </h2>
              </div>
              <div className="rounded-md border border-amber-900/25 bg-black/20 px-4 py-3 text-sm text-stone-300">
                <span className="text-stone-500">Teacher ID:</span>{" "}
                <span className="font-mono text-amber-400">{teacherId}</span>
              </div>
            </div>
          </header>

          <Section id="identity" icon={User} kicker="1 / Identity" title="Who is the teacher?">
            <div className="grid gap-4 md:grid-cols-2">
              <Field label="Teacher name">
                <TextInput
                  value={identity.teacherName}
                  onChange={(e) => setIdentity({ ...identity, teacherName: e.target.value })}
                  placeholder="Master Wu"
                />
              </Field>
              <Field label="Teacher ID / slug">
                <TextInput
                  value={identity.teacherId || teacherId}
                  onChange={(e) => {
                    setTeacherIdOverridden(true);
                    setIdentity({ ...identity, teacherId: slugify(e.target.value) });
                  }}
                  placeholder="master_wu"
                />
              </Field>
              <Field label="Tradition, lineage, or domain">
                <TextInput
                  value={identity.tradition}
                  onChange={(e) => setIdentity({ ...identity, tradition: e.target.value })}
                  placeholder="Chan, contemplative psychology, somatic coaching..."
                />
              </Field>
              <Field label="Languages">
                <TextInput
                  value={identity.languages}
                  onChange={(e) => setIdentity({ ...identity, languages: e.target.value })}
                  placeholder="en_US, zh_TW, ja_JP"
                />
              </Field>
              <Field label="Contact name">
                <TextInput
                  value={identity.contactName}
                  onChange={(e) => setIdentity({ ...identity, contactName: e.target.value })}
                  placeholder="Operator or teacher representative"
                />
              </Field>
              <Field label="Contact email">
                <TextInput
                  type="email"
                  value={identity.contactEmail}
                  onChange={(e) => setIdentity({ ...identity, contactEmail: e.target.value })}
                  placeholder="teacher@example.com"
                />
              </Field>
              <Field label="Website or public profile">
                <TextInput
                  value={identity.website}
                  onChange={(e) => setIdentity({ ...identity, website: e.target.value })}
                  placeholder="https://..."
                />
              </Field>
              <Field label="Short teacher bio">
                <TextArea
                  value={identity.teacherBio}
                  onChange={(e) => setIdentity({ ...identity, teacherBio: e.target.value })}
                  placeholder="What should Pearl_Int know about this teacher's work, background, audience, and voice?"
                />
              </Field>
            </div>
          </Section>

          <Section id="rights" icon={ShieldCheck} kicker="2 / Rights" title="What are we allowed to process?">
            <div className="grid gap-4 md:grid-cols-2">
              <label className="flex gap-3 rounded-md border border-amber-900/25 bg-black/20 p-4 text-sm leading-6 text-stone-300">
                <input
                  type="checkbox"
                  checked={rights.ownsMaterial}
                  onChange={(e) => setRights({ ...rights, ownsMaterial: e.target.checked })}
                  className="mt-1 h-4 w-4 accent-amber-600"
                />
                I own or have permission to submit these teachings, recordings, files, and links for processing.
              </label>
              <label className="flex gap-3 rounded-md border border-amber-900/25 bg-black/20 p-4 text-sm leading-6 text-stone-300">
                <input
                  type="checkbox"
                  checked={rights.processingConsent}
                  onChange={(e) => setRights({ ...rights, processingConsent: e.target.checked })}
                  className="mt-1 h-4 w-4 accent-amber-600"
                />
                I consent to Pearl_Int extracting candidate teacher atoms for human review before production use.
              </label>
              <label className="flex gap-3 rounded-md border border-amber-900/25 bg-black/20 p-4 text-sm leading-6 text-stone-300">
                <input
                  type="checkbox"
                  checked={rights.noUnauthorizedCopyright}
                  onChange={(e) => setRights({ ...rights, noUnauthorizedCopyright: e.target.checked })}
                  className="mt-1 h-4 w-4 accent-amber-600"
                />
                I am not submitting unauthorized copyrighted material, and any public excerpts have rights/provenance notes.
              </label>
              <label className="flex gap-3 rounded-md border border-amber-900/25 bg-black/20 p-4 text-sm leading-6 text-stone-300">
                <input
                  type="checkbox"
                  checked={rights.consent}
                  onChange={(e) => setRights({ ...rights, consent: e.target.checked })}
                  className="mt-1 h-4 w-4 accent-amber-600"
                />
                I confirm this intake can be submitted for operator review and future teacher-source activation work.
              </label>
              <Field label="Public boundaries">
                <TextArea
                  value={rights.publicBoundaries}
                  onChange={(e) => setRights({ ...rights, publicBoundaries: e.target.value })}
                  placeholder="What can be quoted, paraphrased, or used publicly?"
                />
              </Field>
              <Field label="Private boundaries">
                <TextArea
                  value={rights.privateBoundaries}
                  onChange={(e) => setRights({ ...rights, privateBoundaries: e.target.value })}
                  placeholder="What should never be used, named, mined, or surfaced?"
                />
              </Field>
            </div>
          </Section>

          <Section id="teachings" icon={BookOpen} kicker="3 / Teachings" title="Give us the teacher's doctrine and teaching material.">
            <div className="grid gap-4 lg:grid-cols-[1fr_280px]">
              <Field
                label="Teaching blocks"
                hint="Paste one teaching per paragraph where possible. For production, Pearl_Int will normalize these into doctrine, main teaching atoms, signature vibe, and content audit assets."
              >
                <TextArea
                  value={teachingsText}
                  onChange={(e) => setTeachingsText(e.target.value)}
                  placeholder={"Example:\nWhen fear appears, do not argue with it. First locate it in the body...\n\nA practice is not a performance. It is a return to direct contact..."}
                  className="min-h-[260px]"
                />
              </Field>
              <div className="rounded-md border border-amber-900/25 bg-black/20 p-4">
                <div className="text-[10px] uppercase tracking-[0.18em] text-amber-500">Depth target</div>
                <p className="mt-3 text-sm leading-6 text-stone-300">
                  A functional teacher can start near 12 doctrine blocks. A teacher meant to support hundreds or
                  thousands of books needs far more: 100+ teachings, many stories, many practices, and clean provenance.
                </p>
              </div>
            </div>
          </Section>

          <Section id="stories" icon={ClipboardList} kicker="4 / Stories" title="Supply real story material, not tiny examples.">
            <RowList
              rows={stories}
              setRows={setStories}
              starter={starterStory}
              addLabel="Add story"
              renderRow={(row, updateRow, index) => (
                <div className="grid gap-3 md:grid-cols-2">
                  <TextInput value={row.title} onChange={(e) => updateRow(index, { title: e.target.value })} placeholder="Story title or person composite" />
                  <TextInput value={row.source} onChange={(e) => updateRow(index, { source: e.target.value })} placeholder="Source: talk, book, interview, lived composite..." />
                  <TextArea value={row.context} onChange={(e) => updateRow(index, { context: e.target.value })} placeholder="What happens? Include scene, pressure, friction, choice, consequence." />
                  <TextArea value={row.point} onChange={(e) => updateRow(index, { point: e.target.value })} placeholder="What therapeutic or teaching function should this story serve?" />
                </div>
              )}
            />
          </Section>

          <Section id="practices" icon={Sparkles} kicker="5 / Practices" title="Add exercises and tools with enough context to become five-layer atoms.">
            <RowList
              rows={practices}
              setRows={setPractices}
              starter={starterPractice}
              addLabel="Add practice"
              renderRow={(row, updateRow, index) => (
                <div className="grid gap-3 md:grid-cols-2">
                  <TextInput value={row.name} onChange={(e) => updateRow(index, { name: e.target.value })} placeholder="Practice name" />
                  <TextInput value={row.origin} onChange={(e) => updateRow(index, { origin: e.target.value })} placeholder="Origin, lineage, or method family" />
                  <TextArea value={row.helpsWith} onChange={(e) => updateRow(index, { helpsWith: e.target.value })} placeholder="What does it help with? What should the reader understand before trying it?" />
                  <TextArea value={row.guidance} onChange={(e) => updateRow(index, { guidance: e.target.value })} placeholder="Steps, timing, body cues, aha, integration, contraindications." />
                  <TextArea value={row.caution} onChange={(e) => updateRow(index, { caution: e.target.value })} placeholder="Safety notes, trauma cautions, medical limits, or when not to use it." className="md:col-span-2" />
                </div>
              )}
            />
          </Section>

          <Section id="voice" icon={BookOpen} kicker="6 / Voice" title="Quotes, phrases, metaphors, and language boundaries.">
            <div className="space-y-5">
              <RowList
                rows={quotes}
                setRows={setQuotes}
                starter={starterQuote}
                addLabel="Add quote"
                renderRow={(row, updateRow, index) => (
                  <div className="grid gap-3 md:grid-cols-[1fr_240px]">
                    <TextArea value={row.text} onChange={(e) => updateRow(index, { text: e.target.value })} placeholder="Quote, phrase, mantra, or source excerpt" />
                    <TextInput value={row.source} onChange={(e) => updateRow(index, { source: e.target.value })} placeholder="Source / permission note" />
                  </div>
                )}
              />
              <div className="grid gap-4 md:grid-cols-2">
                <Field label="Reflection and integration material">
                  <TextArea
                    value={reflectionText}
                    onChange={(e) => setReflectionText(e.target.value)}
                    placeholder="Reflection prompts, integration bridges, permission lines, pivots, closing takeaways..."
                  />
                </Field>
                <Field label="Topics, personas, and boundaries">
                  <TextArea
                    value={topicsText}
                    onChange={(e) => setTopicsText(e.target.value)}
                    placeholder="Topics this teacher can speak to, audiences they understand, topics they should not address..."
                  />
                </Field>
                <Field label="Repeated phrases, metaphors, and voice rules">
                  <TextArea
                    value={voiceText}
                    onChange={(e) => setVoiceText(e.target.value)}
                    placeholder="Phrases they repeat, signature metaphors, rhythm, warmth, humor, formality, spiritual boundaries..."
                  />
                </Field>
                <Field label="Forbidden language / things they would not say">
                  <TextArea
                    value={forbiddenLanguageText}
                    onChange={(e) => setForbiddenLanguageText(e.target.value)}
                    placeholder="Claims, tones, promises, jargon, or positions this teacher would reject."
                  />
                </Field>
              </div>
            </div>
          </Section>

          <Section id="sources" icon={Upload} kicker="7 / Sources" title="Upload metadata and source links.">
            <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
              <div>
                <RowList
                  rows={urls}
                  setRows={setUrls}
                  starter={starterUrl}
                  addLabel="Add URL"
                  renderRow={(row, updateRow, index) => (
                    <div className="grid gap-3 md:grid-cols-[160px_1fr_1fr]">
                      <select
                        value={row.kind}
                        onChange={(e) => updateRow(index, { kind: e.target.value })}
                        className="rounded-md border border-amber-900/30 bg-black/25 px-3 py-3 text-sm text-stone-100 outline-none"
                      >
                        <option value="teaching">Teaching</option>
                        <option value="story">Story</option>
                        <option value="practice">Practice</option>
                        <option value="quote">Quote</option>
                        <option value="bio">Bio</option>
                      </select>
                      <TextInput value={row.label} onChange={(e) => updateRow(index, { label: e.target.value })} placeholder="Label" />
                      <TextInput value={row.url} onChange={(e) => updateRow(index, { url: e.target.value })} placeholder="https://..." />
                    </div>
                  )}
                />
                <div className="mt-5 grid gap-4 md:grid-cols-2">
                  <Field label="Raw source links" hint="One per line; include transcripts, videos, articles, archives, or course pages.">
                    <TextArea
                      value={uploadLinksText}
                      onChange={(e) => setUploadLinksText(e.target.value)}
                      placeholder={"https://example.com/session-transcript\nhttps://example.com/public-talk"}
                    />
                  </Field>
                  <Field label="Rights and provenance notes">
                    <TextArea
                      value={provenanceNotes}
                      onChange={(e) => setProvenanceNotes(e.target.value)}
                      placeholder="Who owns each source, what may be quoted, what is private, and where permission is documented."
                    />
                  </Field>
                </div>
              </div>

              <div className="rounded-md border border-dashed border-amber-800/40 bg-black/20 p-5">
                <FileUp className="mb-3 text-amber-500" size={24} />
                <div className="text-sm font-medium text-stone-100">Files</div>
                <p className="mt-2 text-sm leading-6 text-stone-400">
                  This v1 records file names, sizes, MIME types, and timestamps. Binaries are not uploaded by the client.
                </p>
                <label className="mt-4 inline-flex cursor-pointer items-center gap-2 rounded-md bg-amber-700 px-4 py-2 text-sm text-white hover:bg-amber-600">
                  <Upload size={16} />
                  Select files
                  <input type="file" multiple accept={ACCEPTED_SOURCE_TYPES} className="hidden" onChange={handleFiles} />
                </label>
                {files.length ? (
                  <div className="mt-4 space-y-2">
                    {files.map((file, index) => (
                      <div key={`${file.name}-${index}`} className="flex items-center justify-between gap-2 rounded-md border border-amber-900/20 px-3 py-2 text-xs text-stone-400">
                        <span className="truncate">{file.name}</span>
                        <button
                          type="button"
                          onClick={() => setFiles(files.filter((_, i) => i !== index))}
                          className="text-stone-500 hover:text-amber-400"
                          aria-label={`Remove ${file.name}`}
                          title={`Remove ${file.name}`}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                ) : null}
              </div>
            </div>
          </Section>

          <Section id="activate" icon={Link} kicker="8 / Activate" title="Submit the teacher intake packet.">
            <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
              <div className="space-y-5">
                <div className="rounded-md border border-amber-900/25 bg-black/20 p-5">
                  <div className="flex items-start gap-3">
                    {canSubmit ? <CheckCircle2 className="text-green-400" size={21} /> : <AlertTriangle className="text-amber-500" size={21} />}
                    <div>
                      <h3 className="text-xl">Activation packet</h3>
                      <p className="mt-2 text-sm leading-6 text-stone-300">
                        Submission creates a durable intake record and public-safe pending activation status. Pearl_Int
                        then converts sources into repo assets and approved teacher atoms.
                      </p>
                    </div>
                  </div>
                  <div className="mt-5 grid gap-2 text-sm text-stone-400">
                    <div>Teacher name: {identity.teacherName ? <span className="text-stone-100">{identity.teacherName}</span> : "missing"}</div>
                    <div>Contact email: {contactEmailValid ? <span className="text-stone-100">{identity.contactEmail}</span> : "missing or invalid"}</div>
                    <div>Processing permission: {rights.ownsMaterial && rights.processingConsent ? <span className="text-green-400">ready</span> : "missing"}</div>
                    <div>Final consent: {rights.consent ? <span className="text-green-400">ready</span> : "missing"}</div>
                    <div>Source material: {hasMaterial ? <span className="text-green-400">present</span> : "missing"}</div>
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

                <div className="rounded-md border border-amber-900/25 bg-black/20 p-5">
                  <div className="text-[10px] uppercase tracking-[0.18em] text-amber-500">Missing requirements</div>
                  {missingMinimums.length ? (
                    <div className="mt-3 grid gap-2 text-sm text-stone-300">
                      {missingMinimums.slice(0, 10).map((gap) => (
                        <div key={gap.key} className="flex items-start gap-2">
                          <AlertTriangle className="mt-0.5 shrink-0 text-amber-500" size={15} />
                          <span>
                            {gap.label}: {gap.count}/{gap.minimum}, missing {gap.missing}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="mt-3 text-sm leading-6 text-stone-300">
                      Functional minimum categories are satisfied in the client view. Server and operator review still decide production readiness.
                    </p>
                  )}
                  {recommendedGaps.length ? (
                    <p className="mt-3 text-xs leading-5 text-stone-500">
                      Preferred/catalog gaps remain for {recommendedGaps.length} categories, including hooks, scenes, and quotes when absent.
                    </p>
                  ) : null}
                </div>
              </div>

              <div className="space-y-3">
                <button
                  type="button"
                  onClick={submitPacket}
                  disabled={!canSubmit || submitState.status === "submitting"}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-amber-700 px-5 py-3 text-sm font-medium text-white transition hover:bg-amber-600 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {submitState.status === "submitting" ? <Loader2 className="animate-spin" size={17} /> : <Sparkles size={17} />}
                  Activate teacher intake
                </button>
                <button
                  type="button"
                  onClick={copyPacket}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-md border border-amber-800/40 px-5 py-3 text-sm text-amber-400 hover:border-amber-500"
                >
                  <Clipboard size={17} />
                  Copy JSON packet
                </button>
                <button
                  type="button"
                  onClick={downloadPacket}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-md border border-amber-800/40 px-5 py-3 text-sm text-amber-400 hover:border-amber-500"
                >
                  <FileUp size={17} />
                  Download JSON packet
                </button>
              </div>
            </div>

            {submitState.status !== "idle" && submitState.status !== "submitting" ? (
              <div className="mt-5 rounded-md border border-amber-900/30 bg-black/25 p-4">
                <div className="text-[10px] uppercase tracking-[0.18em] text-amber-500">Submission status</div>
                <pre className="mt-3 max-h-80 overflow-auto whitespace-pre-wrap text-xs leading-5 text-stone-300">
                  {JSON.stringify(submitState.response, null, 2)}
                </pre>
              </div>
            ) : null}

            <div className="mt-5 rounded-md border border-amber-900/30 bg-black/25 p-4">
              <div className="text-[10px] uppercase tracking-[0.18em] text-amber-500">Generated intake payload preview</div>
              <pre className="mt-3 max-h-[560px] overflow-auto whitespace-pre-wrap text-xs leading-5 text-stone-300">
                {JSON.stringify(packet, null, 2)}
              </pre>
            </div>
          </Section>
        </div>
      </div>
    </main>
  );
}
