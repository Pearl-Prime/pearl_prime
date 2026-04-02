import { useMemo, useState } from "react";
import { Sparkles, ImageOff } from "lucide-react";
import { useOnboardingRegistry } from "./useOnboardingRegistry.js";
import { filterExamples, registryPersonaForWizard } from "./exampleRegistryMatch.js";
import { DecisionImpactSummary } from "./DecisionImpactSummary.jsx";

/** User-facing tier — maps raw registry fields without exposing internals. */
function exampleTier(row) {
  const s = row.status;
  if (s === "planned" || s === "pending" || s === "missing") return "in_progress";
  if (s !== "ready") return "in_progress";
  if (row.production_fidelity === "production") return "ready";
  return "sample";
}

const TIER_LABEL = {
  ready: { text: "Ready", className: "bg-emerald-50 text-emerald-800 ring-emerald-200/80" },
  in_progress: { text: "In progress", className: "bg-amber-50 text-amber-900 ring-amber-200/80" },
  sample: { text: "Sample", className: "bg-violet-50 text-violet-900 ring-violet-200/80" },
};

function ExampleCard({ row }) {
  const [imgBroken, setImgBroken] = useState(false);
  const tier = exampleTier(row);
  const badge = TIER_LABEL[tier];
  const title = row.caption || row.topic || "Representative example";
  const path = row.asset_path || row.output?.image_path;
  const showPlaceholder = !path || imgBroken;

  return (
    <li className="flex gap-3 rounded-xl border border-violet-100/90 bg-white/95 p-2.5 shadow-sm backdrop-blur-sm">
      <div className="relative h-16 w-12 flex-shrink-0 overflow-hidden rounded-lg bg-gradient-to-br from-slate-100 to-slate-200">
        {!showPlaceholder ? (
          <img src={path} alt="" className="h-full w-full object-cover" onError={() => setImgBroken(true)} />
        ) : null}
        {showPlaceholder ? (
          <div className="flex h-full w-full items-center justify-center">
            <ImageOff size={18} className="text-slate-400" />
          </div>
        ) : null}
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className={`inline-flex rounded-full px-2 py-0.5 text-[9px] font-bold uppercase tracking-wide ring-1 ${badge.className}`}>{badge.text}</span>
        </div>
        <p className="mt-1 text-[11px] font-semibold leading-snug text-gray-900">{title}</p>
        <p className="mt-0.5 font-mono text-[9px] text-gray-400">{row.id}</p>
      </div>
    </li>
  );
}

export function OutputProofStrip({ wizardPersonaId, formatFocus, market = "us", onboardingLane = null }) {
  const { rows, error, loading } = useOnboardingRegistry();

  const matched = useMemo(() => {
    if (!rows || !wizardPersonaId) return [];
    return filterExamples(rows, { wizardPersonaId, formatFocus, market, onboardingLane });
  }, [rows, wizardPersonaId, formatFocus, market, onboardingLane]);

  const comparisonSetIds = useMemo(() => {
    const s = new Set();
    matched.forEach((r) => {
      if (r.comparison_set_id) s.add(r.comparison_set_id);
    });
    return Array.from(s).sort();
  }, [matched]);

  const counts = useMemo(() => {
    let ready = 0;
    let inProgress = 0;
    let sample = 0;
    matched.forEach((r) => {
      const t = exampleTier(r);
      if (t === "ready") ready += 1;
      else if (t === "in_progress") inProgress += 1;
      else sample += 1;
    });
    return { ready, inProgress, sample };
  }, [matched]);

  const regPersona = registryPersonaForWizard(wizardPersonaId);

  if (!wizardPersonaId) return null;

  return (
    <div className="mt-6 rounded-2xl border border-violet-200/80 bg-gradient-to-br from-violet-50/95 via-white/90 to-fuchsia-50/40 p-4 shadow-md shadow-violet-100/50 backdrop-blur-sm">
      <div className="mb-2 flex items-center gap-2">
        <Sparkles size={17} className="text-violet-600" />
        <span className="text-xs font-bold uppercase tracking-wider text-violet-800">Matched examples</span>
      </div>
      <p className="mb-3 text-[11px] leading-relaxed text-violet-950/85">
        Representative proof aligned to your <strong className="font-semibold text-violet-950">primary reader</strong>
        {formatFocus ? (
          <>
            , <strong className="font-semibold text-violet-950">{formatFocus === "manga" ? "manga-first" : "book-first"}</strong> direction
          </>
        ) : null}
        {onboardingLane ? (
          <>
            , <strong className="font-semibold text-violet-950">{onboardingLane.replace(/_/g, " ")}</strong> lane
          </>
        ) : null}
        {market ? (
          <>
            , market <strong className="font-semibold text-violet-950">{market}</strong>
          </>
        ) : null}
        . Some assets may still be demo-grade; your team can refresh samples over time.
      </p>

      <div className="mb-3 grid gap-2 sm:grid-cols-2">
        <div className="rounded-lg border border-violet-100 bg-white/80 px-3 py-2 text-[10px] text-violet-900/90">
          <span className="font-bold text-violet-800">What to look for</span>
          <p className="mt-1 leading-relaxed text-violet-900/80">Do the covers and tone feel right for the reader you chose?</p>
        </div>
        <div className="rounded-lg border border-violet-100 bg-white/80 px-3 py-2 text-[10px] text-violet-900/90">
          <span className="font-bold text-violet-800">What this means</span>
          <p className="mt-1 leading-relaxed text-violet-900/80">These examples preview your direction — not every final asset in the catalog.</p>
        </div>
      </div>

      {loading && <p className="text-[11px] text-gray-500">Loading examples…</p>}
      {error && <p className="text-[11px] text-red-600">Could not load examples. Check your connection and try again.</p>}

      {!loading && !error && !regPersona && (
        <p className="rounded-lg border border-amber-200 bg-amber-50/90 px-3 py-2.5 text-[11px] leading-relaxed text-amber-950">
          We don&apos;t have matched examples for this reader type yet. Try another primary reader, or continue the wizard and revisit after you adjust lane or format.
        </p>
      )}

      {!loading && !error && regPersona && matched.length === 0 && (
        <p className="text-[11px] text-gray-600">
          No examples match this combination yet. Try another reader, lane, or market — or finish the wizard and check back after format selection.
        </p>
      )}

      {matched.length > 0 && (
        <>
          <DecisionImpactSummary
            matchedCount={matched.length}
            readyCount={counts.ready}
            inProgressCount={counts.inProgress}
            sampleCount={counts.sample}
            comparisonGroupCount={comparisonSetIds.length}
          />
          <ul className="max-h-52 space-y-2 overflow-y-auto pr-1">
            {matched.map((r) => (
              <ExampleCard key={r.id} row={r} />
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
