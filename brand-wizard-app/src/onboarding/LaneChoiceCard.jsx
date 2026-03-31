import { BookOpen, Image } from "lucide-react";

export function LaneChoiceCard({laneKey, label, selected, onSelect, hint}) {
  const isManga = laneKey === "manga";
  const Icon = isManga ? Image : BookOpen;
  return (
    <button
      type="button"
      onClick={() => onSelect(laneKey)}
      className={`p-4 rounded-xl border-2 text-left w-full transition-all ${selected ? "border-gray-900 bg-gray-50 shadow-md" : "border-gray-200 bg-white hover:border-gray-300"}`}
    >
      <div className="flex items-start gap-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${selected ? "bg-gray-900 text-white" : "bg-gray-100 text-gray-500"}`}>
          <Icon size={20} />
        </div>
        <div>
          <div className="text-sm font-bold text-gray-900">{label}</div>
          {hint ? <p className="text-[11px] text-gray-500 mt-1 leading-relaxed">{hint}</p> : null}
        </div>
      </div>
    </button>
  );
}
