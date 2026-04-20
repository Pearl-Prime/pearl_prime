export default function HeroSection() {
  return (
    <div className="min-h-[90vh] flex flex-col items-center justify-center text-center px-6 py-24">
      <p className="text-sm tracking-widest uppercase text-amber-600 mb-4 font-mono">Pearl Prime</p>
      <h1 className="font-serif text-5xl md:text-7xl font-light text-amber-100 mb-6 leading-tight">
        Ancient wisdom.<br />Enlightened intelligence.
      </h1>
      <p className="text-lg text-amber-100/60 max-w-xl leading-relaxed mb-10">
        Content that elevates the next generation and changes the world.
        Ebooks, audiobooks, manga, and podcasts — delivered weekly, across five global markets.
      </p>
      <a
        href="#market"
        className="inline-block border border-amber-700/40 text-amber-400 text-xs font-mono tracking-widest uppercase px-8 py-3 hover:bg-amber-900/20 transition-colors"
      >
        Choose your market →
      </a>
    </div>
  );
}
