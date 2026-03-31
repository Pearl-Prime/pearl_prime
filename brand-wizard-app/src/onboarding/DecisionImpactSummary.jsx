export function DecisionImpactSummary({matchedCount, comparisonSetIds, registryPersona}) {
  if (!registryPersona && matchedCount === 0) return null;

  return (
    <div className="rounded-lg bg-slate-50 border border-slate-200 px-3 py-2.5 mb-3">
      <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1">Proof coverage snapshot</div>
      <p className="text-[11px] text-slate-700 leading-relaxed">
        <strong>{matchedCount}</strong> onboarding example{matchedCount === 1 ? "" : "s"} for registry persona{" "}
        <code className="text-[10px] bg-white px-1 rounded border border-slate-200">{registryPersona || "—"}</code>
        {comparisonSetIds.length > 0 ? (
          <>
            {" "}
            spanning <strong>{comparisonSetIds.length}</strong> comparison set{comparisonSetIds.length === 1 ? "" : "s"} (controlled A/B boards).
          </>
        ) : (
          " (standalone gallery rows — no comparison set on these lines)."
        )}
      </p>
    </div>
  );
}
