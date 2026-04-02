import SwiftUI

struct LocaleParityView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader

    @State private var report: LocaleParityReport?
    @State private var sheetPersona: String?
    @State private var sheetLocale: String?
    @State private var sheetCoverage: Double = 0
    @State private var atomFiles: [String] = []

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Locale Parity")
                .font(.title2)
                .foregroundColor(PhoenixColors.phoenixBlue)

            if state.repoPath.isEmpty {
                Text("Set repo path to load artifacts/localization/LOCALE_PARITY_REPORT_*.md")
                    .foregroundColor(.secondary)
            } else if let rep = report {
                ScrollView([.horizontal, .vertical]) {
                    VStack(alignment: .leading, spacing: 0) {
                        HStack(spacing: 0) {
                            Text("Persona")
                                .frame(width: 140, alignment: .leading)
                                .padding(4)
                            ForEach(rep.localeColumns, id: \.self) { loc in
                                Text(loc)
                                    .frame(width: 72, alignment: .center)
                                    .padding(4)
                                    .font(.caption)
                            }
                        }
                        .font(.caption.bold())

                        let personas = Array(Set(rep.entries.map(\.persona))).sorted()
                        ForEach(personas, id: \.self) { persona in
                            HStack(spacing: 0) {
                                Text(persona)
                                    .frame(width: 140, alignment: .leading)
                                    .padding(4)
                                    .font(.caption)
                                ForEach(rep.localeColumns, id: \.self) { loc in
                                    let pct = rep.entries.first { $0.persona == persona && $0.locale == loc }?.coverage ?? 0
                                    Text(String(format: "%.0f%%", pct))
                                        .frame(width: 72, alignment: .center)
                                        .padding(6)
                                        .background(heatColor(pct))
                                        .cornerRadius(4)
                                        .onTapGesture {
                                            sheetPersona = persona
                                            sheetLocale = loc
                                            sheetCoverage = pct
                                            atomFiles = artifactReader.listLocalizedAtomFiles(repoPath: state.repoPath, personaRow: persona, locale: loc)
                                        }
                                }
                            }
                        }

                        Divider().padding(.vertical, 8)
                        Text("Aggregate by locale")
                            .font(.headline)
                        HStack(spacing: 8) {
                            ForEach(rep.localeColumns, id: \.self) { loc in
                                let vals = rep.entries.filter { $0.locale == loc }.map(\.coverage)
                                let avg = vals.isEmpty ? 0 : vals.reduce(0, +) / Double(vals.count)
                                VStack {
                                    Text(loc).font(.caption2)
                                    Text(String(format: "%.0f%%", avg))
                                        .font(.caption.bold())
                                }
                                .padding(8)
                                .background(heatColor(avg).opacity(0.6))
                                .cornerRadius(6)
                            }
                        }
                    }
                    .padding()
                }
            } else {
                Text("No LOCALE_PARITY_REPORT_*.md found under artifacts/localization/.")
                    .foregroundColor(.secondary)
            }
            Spacer()
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .background(PhoenixColors.phoenixBackground)
        .onAppear { loadReport() }
        .sheet(isPresented: Binding(
            get: { sheetPersona != nil && sheetLocale != nil },
            set: { if !$0 { sheetPersona = nil; sheetLocale = nil } }
        )) {
            VStack(alignment: .leading, spacing: 12) {
                if let p = sheetPersona, let l = sheetLocale {
                    Text("\(p) — \(l)")
                        .font(.headline)
                    Text(String(format: "Coverage: %.1f%%", sheetCoverage))
                    Text("Atom files (\(atomFiles.count))")
                        .font(.subheadline)
                    List(atomFiles, id: \.self) { f in
                        Text(f).font(.system(.caption, design: .monospaced))
                    }
                }
                Button("Close") { sheetPersona = nil; sheetLocale = nil }
            }
            .padding()
            .frame(minWidth: 400, minHeight: 300)
        }
    }

    private func heatColor(_ pct: Double) -> Color {
        if pct >= 100 { return .green.opacity(0.35) }
        if pct >= 80 { return .yellow.opacity(0.4) }
        if pct > 0 { return .red.opacity(0.35) }
        return .gray.opacity(0.25)
    }

    private func loadReport() {
        guard !state.repoPath.isEmpty else { return }
        report = artifactReader.loadLocaleParity(repoPath: state.repoPath)
        if let r = report {
            state.localeParityEntries = r.entries
        }
    }
}
