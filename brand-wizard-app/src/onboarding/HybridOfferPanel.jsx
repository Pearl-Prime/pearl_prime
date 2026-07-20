import { parseHybridOfferMessage, acceptHybridAndAssign } from "../hybridOffer.js";

/**
 * Surfaces the teacher_claimed → generalized hybrid accept path.
 * Accept creates the hybrid brand and immediately resubmits onboarding/assign.
 */
export function HybridOfferPanel({
  submissionError,
  onboardingMarket,
  contact,
  wizardYaml,
  onAccepted,
  onError,
}) {
  const offer = parseHybridOfferMessage(submissionError);
  if (!offer) return null;
  const { teacherId, arches } = offer;

  return (
    <div className="mb-6 rounded-2xl border border-violet-300 bg-violet-50 p-5 text-sm text-violet-950" data-testid="hybrid-offer-panel">
      <div className="font-bold">This teacher is already claimed in this market.</div>
      <p className="mt-2 font-normal leading-6">
        You can still continue with a <strong>generalized hybrid brand</strong> — that teacher&apos;s doctrine
        without naming them, angled through one of the 40 archetypes ({arches.length} still available).
      </p>
      {!arches.length ? (
        <p className="mt-3 font-semibold text-violet-900">All hybrid archetype slots are used. Contact ops.</p>
      ) : (
        <div className="mt-4 flex flex-wrap gap-2">
          {arches.map((arch) => (
            <button
              key={arch}
              type="button"
              className="rounded-lg border border-violet-400 bg-white px-3 py-2 font-mono text-xs font-semibold text-violet-800 hover:bg-violet-100"
              onClick={async () => {
                try {
                  const { match } = await acceptHybridAndAssign({
                    teacherId,
                    archetypeId: arch,
                    lane: onboardingMarket || "us",
                    contact,
                    wizardYaml: wizardYaml || "",
                  });
                  onAccepted?.(match);
                } catch (err) {
                  onError?.(err?.message || "Hybrid accept failed — check API and retry.");
                }
              }}
            >
              Accept · {arch}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
