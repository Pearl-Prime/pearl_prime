const PLATFORMS = ["YouTube","TikTok","Instagram","Facebook","LinkedIn","Pinterest","Twitter/X","Threads","Snapchat","Reddit"];

export default function Social48() {
  return (
    <div className="py-24 px-6 bg-amber-950/10">
      <div className="max-w-4xl mx-auto text-center">
        <p className="text-xs font-mono tracking-widest uppercase text-amber-600 mb-2">Step 5</p>
        <h2 className="font-serif text-4xl text-amber-100 mb-4">48Social organic growth</h2>
        <p className="text-amber-100/50 text-sm mb-3 max-w-xl mx-auto">
          A separate company. Pearl Prime's exclusive organic partner. Takes emotional peaks from your books and transforms them into daily short-form content — built from the content itself. Not invented promotional copy.
        </p>
        <div className="text-amber-400 text-2xl font-light mb-8">Up to 365 videos / year · 48 platforms · $0 ad spend</div>
        <div className="flex flex-wrap justify-center gap-2">
          {PLATFORMS.map((p) => (
            <span key={p} className="text-xs font-mono px-3 py-1 border border-amber-900/40 text-amber-100/50">{p}</span>
          ))}
          <span className="text-xs font-mono px-3 py-1 border border-amber-900/40 text-amber-600">+ 38 more</span>
        </div>
      </div>
    </div>
  );
}
