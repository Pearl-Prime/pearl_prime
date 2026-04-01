import { BookOpen, Image, Newspaper, Wind, Layers } from "lucide-react";

const LANE_THEME = {
  self_help: {
    Icon: BookOpen,
    gradient: "from-violet-500 to-indigo-600",
    softBg: "from-violet-50 to-indigo-50/80",
    accent: "text-violet-700",
  },
  manga: {
    Icon: Image,
    gradient: "from-fuchsia-500 to-pink-600",
    softBg: "from-fuchsia-50 to-pink-50/80",
    accent: "text-fuchsia-700",
  },
  pearl_news: {
    Icon: Newspaper,
    gradient: "from-sky-500 to-blue-600",
    softBg: "from-sky-50 to-blue-50/80",
    accent: "text-sky-700",
  },
  tools: {
    Icon: Wind,
    gradient: "from-teal-500 to-emerald-600",
    softBg: "from-teal-50 to-emerald-50/80",
    accent: "text-teal-700",
  },
  breathwork_tools: {
    Icon: Wind,
    gradient: "from-teal-500 to-cyan-600",
    softBg: "from-teal-50 to-cyan-50/80",
    accent: "text-teal-700",
  },
  hybrid: {
    Icon: Layers,
    gradient: "from-amber-500 to-orange-600",
    softBg: "from-amber-50 to-orange-50/80",
    accent: "text-amber-800",
  },
};

const DEFAULT_THEME = {
  Icon: BookOpen,
  gradient: "from-slate-500 to-slate-700",
  softBg: "from-slate-50 to-gray-50/80",
  accent: "text-slate-700",
};

export function LaneChoiceCard({ laneKey, label, selected, onSelect, hint }) {
  const theme = LANE_THEME[laneKey] || DEFAULT_THEME;
  const Icon = theme.Icon;

  return (
    <button
      type="button"
      onClick={() => onSelect(laneKey)}
      className={[
        "group relative p-4 rounded-2xl border-2 text-left w-full transition-all duration-300",
        selected
          ? `border-gray-900 bg-gradient-to-br ${theme.softBg} shadow-lg shadow-slate-300/40 ring-2 ring-gray-900/10 scale-[1.01]`
          : "border-gray-200/90 bg-white/90 hover:border-gray-300 hover:shadow-md hover:-translate-y-0.5 backdrop-blur-sm",
      ].join(" ")}
    >
      {selected ? (
        <span className="absolute top-3 right-3 flex h-6 w-6 items-center justify-center rounded-full bg-gray-900 text-white shadow-md">
          <span className="h-2 w-2 rounded-full bg-white" />
        </span>
      ) : null}
      <div className="flex items-start gap-3.5">
        <div
          className={[
            "flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br shadow-md transition-transform duration-300",
            `bg-gradient-to-br ${theme.gradient}`,
            selected ? "scale-105 shadow-lg" : "group-hover:scale-105 opacity-90 group-hover:opacity-100",
          ].join(" ")}
        >
          <Icon size={22} className="text-white drop-shadow-sm" />
        </div>
        <div className="min-w-0 flex-1 pt-0.5">
          <div className={`text-sm font-bold ${selected ? "text-gray-900" : "text-gray-800"}`}>{label}</div>
          <p className={`mt-0.5 text-[10px] font-semibold uppercase tracking-wider ${theme.accent} opacity-80`}>{laneKey.replace(/_/g, " ")}</p>
          {hint ? <p className="mt-1.5 text-[11px] leading-relaxed text-gray-500">{hint}</p> : null}
        </div>
      </div>
    </button>
  );
}
