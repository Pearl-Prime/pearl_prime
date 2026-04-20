const ANGLES = [
  { id: "nervous", label: "Nervous System", desc: "Stress, anxiety, burnout, somatic work. Highest search volume in self-help." },
  { id: "identity", label: "Identity & Direction", desc: "Gen Z's primary search intent. Who am I. Where am I going." },
  { id: "emotional", label: "Emotional Healing", desc: "Trauma, grief, repair, resilience. Deep reader loyalty." },
  { id: "performance", label: "Performance & Focus", desc: "Premium audiences. High willingness to pay." },
  { id: "spiritual", label: "Spiritual Awakening", desc: "The deeper current. Longevity in catalogue." },
];

export default function TeacherExpression() {
  return (
    <div className="py-24 px-6 bg-amber-950/10">
      <div className="max-w-4xl mx-auto">
        <p className="text-xs font-mono tracking-widest uppercase text-amber-600 mb-2 text-center">Step 9</p>
        <h2 className="font-serif text-4xl text-amber-100 text-center mb-4">Your brand angle</h2>
        <p className="text-amber-100/50 text-sm text-center mb-12 max-w-xl mx-auto">
          Choose one angle. Go deep. This is your market positioning, your content spine, your reader promise.
        </p>
        <div className="space-y-3">
          {ANGLES.map((a) => (
            <div key={a.id} className="flex items-start gap-5 p-5 border border-amber-900/30 hover:border-amber-700/50 hover:bg-amber-900/10 transition-all cursor-pointer">
              <div className="w-1.5 h-1.5 rounded-full bg-amber-600 mt-2 shrink-0" />
              <div>
                <div className="text-amber-200 font-medium mb-1">{a.label}</div>
                <div className="text-xs text-amber-100/50">{a.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
