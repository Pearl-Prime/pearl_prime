const PILLARS = [
  { icon: "📚", title: "Weekly Content Delivery", body: "Ebooks, audiobooks, manga, and podcasts — generated weekly by Ei and delivered upload-ready to your platforms." },
  { icon: "🌏", title: "5 Global Markets", body: "United States, Japan, Taiwan, Mainland China, and Korea. Localized for each platform, language, and reader culture." },
  { icon: "🧠", title: "Ei — Enlightened Intelligence", body: "Not generic AI. A novel technique grounded in teacher lineage wisdom, Gen Z psychological research, and somatic modeling." },
  { icon: "📣", title: "48Social Organic Growth", body: "Up to 365 short-form social videos per year. YouTube, TikTok, Instagram. Zero ad spend. Built from your content." },
];

export default function SystemOverview() {
  return (
    <div className="py-24 px-6 bg-amber-950/10">
      <div className="max-w-5xl mx-auto">
        <p className="text-xs font-mono tracking-widest uppercase text-amber-600 mb-2 text-center">Step 3</p>
        <h2 className="font-serif text-4xl text-amber-100 text-center mb-12">How Pearl Prime works</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {PILLARS.map((p) => (
            <div key={p.title} className="p-6 border border-amber-900/30">
              <div className="text-3xl mb-4">{p.icon}</div>
              <h3 className="text-amber-200 font-medium mb-2">{p.title}</h3>
              <p className="text-amber-100/50 text-sm leading-relaxed">{p.body}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
