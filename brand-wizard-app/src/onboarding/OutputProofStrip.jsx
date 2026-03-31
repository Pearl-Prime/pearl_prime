import { useMemo } from "react";
import { Sparkles } from "lucide-react";
import { useOnboardingRegistry } from "./useOnboardingRegistry.js";
import { filterExamples, registryPersonaForWizard } from "./exampleRegistryMatch.js";
import { DecisionImpactSummary } from "./DecisionImpactSummary.jsx";

function StatusDot({ status }) {
  const color = status === "ready" ? "bg-emerald-500" : status === "planned" ? "bg-amber-400" : "bg-red-400";
  return <span className={`inline-block w-1.5 h-1.5 rounded-full ${color}`} title={status} />;
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

  const regPersona = registryPersonaForWizard(wizardPersonaId);

  if (!wizardPersonaId) return null;

  return (
    <div className="mt-6 rounded-2xl border border-violet-200 bg-gradient-to-br from-violet-50/90 to-white p-4 shadow-sm">
      <div className="flex items-center gap-2 mb-2">
        <Sparkles size={16} className="text-violet-600" />
        <span className="text-xs font-bold uppercase tracking-wider text-violet-700">What the system can show</span>
      </div>
      <p className="text-[11px] text-violet-900/80 mb-3 leading-relaxed">
        Registry examples aligned to your <strong className="font-semibold text-violet-950">primary reader</strong>
        {formatFocus ? (
          <> and <strong className="font-semibold text-violet-950">{formatFocus === "manga" ? "manga-first" : "book-first"}</strong> packaging bias</>
        ) : null}
        {onboardingLane ? (
          <> in the <strong className="font-semibold text-violet-950">{onboardingLane.replace(/_/g, " ")}</strong> lane</>
        ) : null}
        {market ? (
          <> for market <strong className="font-semibold text-violet-950">{market}</strong></>
        ) : null}
        . Status colors: ready / planned / missing — the gallery uses the same JSON.
      </p>

      {loading && <p className="text-[11px] text-gray-500">Loading registry…</p>}
      {error && <p className="text-[11px] text-red-600">Could not load onboarding JSON: {error}</p>}

      {!loading && !error && !regPersona && (
        <p className="text-[11px] text-amber-800 bg-amber-50 border border-amber-200 rounded-lg px-2 py-2">
          This reader type is not mapped to a registry persona yet, so we can’t list proof IDs here. Open{" "}
          <code className="text-[10px]">lane_examples_gallery.html</code> (repo root, over HTTP) for the full board.
        </p>
      )}

      {!loading && !error && regPersona && matched.length === 0 && (
        <p className="text-[11px] text-gray-600">
          No proof rows for this reader {formatFocus ? "with this format bias " : ""}in the v1 registry — try another primary reader or finish the wizard and revisit after format selection.
        </p>
      )}

      {matched.length > 0 && (
        <>
          <DecisionImpactSummary matchedCount={matched.length} comparisonSetIds={comparisonSetIds} registryPersona={regPersona} />
          <ul className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
            {matched.map((r) => (
              <li key={r.id} className="flex items-start gap-2 text-[11px] text-gray-800 font-mono bg-white/80 rounded-md px-2 py-1 border border-violet-100">
                <StatusDot status={r.status} />
                <span className="break-all flex-1">{r.id}</span>
                <span className="text-[10px] text-gray-500 flex-shrink-0">{r.lane}</span>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
