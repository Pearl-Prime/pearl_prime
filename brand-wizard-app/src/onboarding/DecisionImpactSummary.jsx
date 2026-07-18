/**
 * Product-facing summary for matched onboarding examples (not internal registry language).
 */
export function DecisionImpactSummary({
  matchedCount,
  readyCount = 0,
  inProgressCount = 0,
  sampleCount = 0,
  comparisonGroupCount = 0,
}) {
  if (matchedCount === 0) return null;

  return (
    <div className="mb-4 rounded-xl border border-slate-200/80 bg-white/90 px-4 py-3 shadow-sm backdrop-blur-sm">
      <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500">What&apos;s ready for this direction</div>
      <p className="mt-1.5 text-[11px] leading-relaxed text-slate-700">
        <strong className="text-slate-900">{matchedCount}</strong> matched example{matchedCount === 1 ? "" : "s"} for your reader, lane, and market.
        {comparisonGroupCount > 0 ? (
          <>
            {" "}
            You can compare side-by-side across <strong>{comparisonGroupCount}</strong> style group
            {comparisonGroupCount === 1 ? "" : "s"}.
          </>
        ) : null}
      </p>
      <div className="mt-2.5 flex flex-wrap gap-2">
        {readyCount > 0 ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-800 ring-1 ring-emerald-200/80">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Ready {readyCount}
          </span>
        ) : null}
        {inProgressCount > 0 ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-900 ring-1 ring-amber-200/80">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />
            In progress {inProgressCount}
          </span>
        ) : null}
        {sampleCount > 0 ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-violet-50 px-2 py-0.5 text-[10px] font-semibold text-violet-900 ring-1 ring-violet-200/80">
            <span className="h-1.5 w-1.5 rounded-full bg-violet-500" />
            Sample / demo {sampleCount}
          </span>
        ) : null}
      </div>
    </div>
  );
}
