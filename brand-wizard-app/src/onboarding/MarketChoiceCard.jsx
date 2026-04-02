import { Globe } from "lucide-react";

const MARKET_ACCENT = {
  us: { gradient: "from-indigo-500 to-violet-600", soft: "from-indigo-50/90 to-violet-50/70", label: "text-indigo-700" },
  japan: { gradient: "from-rose-500 to-red-600", soft: "from-rose-50/90 to-red-50/60", label: "text-rose-700" },
  taiwan: { gradient: "from-emerald-500 to-teal-600", soft: "from-emerald-50/90 to-teal-50/60", label: "text-emerald-700" },
};

const DEFAULT_MARKET = {
  gradient: "from-slate-500 to-slate-700",
  soft: "from-slate-50 to-gray-50/80",
  label: "text-slate-700",
};

export function MarketChoiceCard({ marketKey, label, hint, selected, onSelect }) {
  const a = MARKET_ACCENT[marketKey] || DEFAULT_MARKET;

  return (
    <button
      type="button"
      onClick={() => onSelect(marketKey)}
      className={[
        "group relative flex w-full items-start gap-3 rounded-2xl border-2 p-3.5 text-left transition-all duration-300",
        selected
          ? `border-gray-900 bg-gradient-to-br ${a.soft} shadow-lg shadow-slate-300/35 ring-2 ring-gray-900/10`
          : "border-gray-200/90 bg-white/90 hover:border-gray-300 hover:shadow-md hover:-translate-y-0.5 backdrop-blur-sm",
      ].join(" ")}
    >
      {selected ? (
        <span className="absolute right-2.5 top-2.5 flex h-5 w-5 items-center justify-center rounded-full bg-gray-900">
          <span className="h-1.5 w-1.5 rounded-full bg-white" />
        </span>
      ) : null}
      <div
        className={[
          "flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br shadow-md transition-transform duration-300",
          a.gradient,
          selected ? "scale-105" : "opacity-90 group-hover:scale-105 group-hover:opacity-100",
        ].join(" ")}
      >
        <Globe size={18} className="text-white drop-shadow-sm" />
      </div>
      <div className="min-w-0 flex-1 pr-5">
        <div className={`text-xs font-bold ${selected ? "text-gray-900" : "text-gray-800"}`}>{label}</div>
        <p className={`mt-0.5 text-[9px] font-semibold uppercase tracking-wider ${a.label}`}>{marketKey}</p>
        {hint ? <p className="mt-1 text-[10px] leading-snug text-gray-500">{hint}</p> : null}
      </div>
    </button>
  );
}
