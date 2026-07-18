const STREAMS = [
  { source: "Amazon KDP / Google Play", type: "Royalty", note: "70% royalty on ebooks $2.99–$9.99" },
  { source: "INaudio / Findaway", type: "Royalty", note: "Audiobooks reach Apple, Spotify, Kobo, libraries" },
  { source: "楽天Kobo / Audiobook.jp", type: "Royalty", note: "JPY payments, withholding handled" },
  { source: "Ximalaya / WeChat Reading", type: "Royalty", note: "345M Ximalaya users alone" },
  { source: "Naver Series / Kakao Page", type: "Royalty", note: "₩70 CPC organic growth via Naver" },
  { source: "Foreign Rights", type: "Licensing", note: "Year 2+ — catalogue becomes an asset" },
];

export default function RevenueModel() {
  return (
    <div className="py-24 px-6">
      <div className="max-w-4xl mx-auto">
        <p className="text-xs font-mono tracking-widest uppercase text-amber-600 mb-2 text-center">Step 6</p>
        <h2 className="font-serif text-4xl text-amber-100 text-center mb-12">Revenue streams</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-amber-900/30">
                <th className="text-left pb-3 text-amber-600 font-mono text-xs uppercase tracking-wider">Platform</th>
                <th className="text-left pb-3 text-amber-600 font-mono text-xs uppercase tracking-wider">Type</th>
                <th className="text-left pb-3 text-amber-600 font-mono text-xs uppercase tracking-wider">Note</th>
              </tr>
            </thead>
            <tbody>
              {STREAMS.map((s, i) => (
                <tr key={i} className="border-b border-amber-900/20 hover:bg-amber-900/10 transition-colors">
                  <td className="py-3 pr-6 text-amber-200">{s.source}</td>
                  <td className="py-3 pr-6 text-amber-100/50">{s.type}</td>
                  <td className="py-3 text-amber-100/40 text-xs">{s.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
