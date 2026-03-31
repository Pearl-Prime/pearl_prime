import { Globe } from "lucide-react";

export function MarketChoiceCard({marketKey, label, hint, selected, onSelect}) {
  return (
    <button
      type="button"
      onClick={() => onSelect(marketKey)}
      className={`p-3.5 rounded-xl border-2 text-left w-full transition-all flex items-start gap-3 ${selected ? "border-indigo-600 bg-indigo-50/50" : "border-gray-200 bg-white hover:border-gray-300"}`}
    >
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${selected ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-400"}`}>
        <Globe size={16} />
      </div>
      <div>
        <div className="text-xs font-bold text-gray-900">{label}</div>
        {hint ? <p className="text-[10px] text-gray-500 mt-0.5">{hint}</p> : null}
      </div>
    </button>
  );
}
