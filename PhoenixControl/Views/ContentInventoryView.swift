import SwiftUI
import AppKit

/// Loads `artifacts/inventory/content_inventory.json` from the configured repo root.
struct ContentInventoryView: View {
    @ObservedObject var state: AppState
    let scriptRunner: ScriptRunner

    @State private var payload: ContentInventoryPayload?
    @State private var loadError: String?
    @State private var logOutput: String = ""
    @State private var isScanning: Bool = false
    @State private var toast: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 12) {
                Button("Reload JSON") { loadInventory() }
                    .disabled(state.repoPath.isEmpty)
                Button("Scan repo") { runScan() }
                    .disabled(state.repoPath.isEmpty || isScanning)
                if isScanning { ProgressView().scaleEffect(0.85) }
                if let toast {
                    Text(toast).font(.caption).foregroundColor(.green)
                }
            }
            if let loadError {
                Text(loadError).foregroundColor(.red).font(.caption)
            }
            if let payload {
                summaryRow(payload)
                Divider()
                ScrollView {
                    VStack(alignment: .leading, spacing: 16) {
                        typeTable(payload)
                        Divider()
                        teacherTable(payload)
                        Divider()
                        commandsSection(payload)
                        Divider()
                        missingSection(payload)
                    }
                }
            } else if loadError == nil && !state.repoPath.isEmpty {
                Text("Loading…").foregroundColor(.secondary)
            }
            if !logOutput.isEmpty {
                Text("Scan log").font(.headline)
                LiveLogView(logText: $logOutput, isRunning: isScanning)
                    .frame(minHeight: 120, maxHeight: 220)
            }
        }
        .padding()
        .background(PhoenixColors.phoenixBackground)
        .onAppear { loadInventory() }
        .onChange(of: state.repoPath) { _ in loadInventory() }
    }

    private func summaryRow(_ p: ContentInventoryPayload) -> some View {
        let catalog = p.summary.totalConfigured ?? p.summary.catalogRows ?? 0
        let built = p.summary.totalBuilt
        let cov = p.summary.coveragePct
        let miss = p.summary.missingCount
        let builtTypes = p.summary.byType.values.map(\.built).reduce(0, +)
        return HStack(alignment: .top, spacing: 20) {
            VStack(alignment: .leading) {
                Text("Scan date").font(.caption).foregroundColor(.secondary)
                Text(p.scanDate).font(.title3.monospaced())
            }
            VStack(alignment: .leading) {
                Text("Configured").font(.caption).foregroundColor(.secondary)
                Text("\(catalog)").font(.title3.monospaced())
            }
            VStack(alignment: .leading) {
                Text("Built (rollup)").font(.caption).foregroundColor(.secondary)
                Text("\(built.map(String.init) ?? String(builtTypes))").font(.title3.monospaced())
            }
            if let cov {
                VStack(alignment: .leading) {
                    Text("Coverage %").font(.caption).foregroundColor(.secondary)
                    Text(String(format: "%.2f", cov)).font(.title3.monospaced())
                }
            }
            if let miss {
                VStack(alignment: .leading) {
                    Text("Missing").font(.caption).foregroundColor(.secondary)
                    Text("\(miss)").font(.title3.monospaced())
                }
            }
            Spacer()
        }
    }

    private func typeTable(_ p: ContentInventoryPayload) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("By content type").font(.headline)
            Grid(horizontalSpacing: 12, verticalSpacing: 6) {
                GridRow {
                    Text("Type").font(.caption).bold()
                    Text("Built").font(.caption).bold()
                    Text("Configured").font(.caption).bold()
                    Text("%").font(.caption).bold()
                }
                ForEach(Array(p.summary.byType.keys.sorted()), id: \.self) { key in
                    if let st = p.summary.byType[key] {
                        GridRow {
                            Text(key).font(.caption.monospaced())
                            Text("\(st.built)").font(.caption.monospaced())
                            Text("\(st.configured)").font(.caption.monospaced())
                            Text(String(format: "%.1f", st.pct)).font(.caption.monospaced())
                        }
                    }
                }
            }
        }
    }

    private func teacherTable(_ p: ContentInventoryPayload) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Teachers").font(.headline)
            Table(p.teachers) {
                TableColumn("ID") { (t: ContentInventoryTeacher) in Text(t.id).font(.caption.monospaced()) }
                TableColumn("Book") { (t: ContentInventoryTeacher) in flag(t.bookText) }
                TableColumn("EPUB") { (t: ContentInventoryTeacher) in flag(t.epub) }
                TableColumn("Cover") { (t: ContentInventoryTeacher) in flag(t.cover) }
                TableColumn("Manga cv") { (t: ContentInventoryTeacher) in flag(t.mangaCover) }
                TableColumn("Mn pn") { (t: ContentInventoryTeacher) in flag(t.mangaPanels) }
                TableColumn("V plan") { (t: ContentInventoryTeacher) in flag(t.videoPlan) }
                TableColumn("YT") { (t: ContentInventoryTeacher) in flag(t.videoYoutube) }
                TableColumn("TT") { (t: ContentInventoryTeacher) in flag(t.videoTiktok) }
                TableColumn("Audio") { (t: ContentInventoryTeacher) in flag(t.audioPresenter) }
            }
            .frame(minHeight: 280)
        }
    }

    @ViewBuilder
    private func flag(_ ok: Bool) -> some View {
        Text(ok ? "yes" : "no")
            .font(.caption.monospaced())
            .foregroundColor(ok ? .green : .red)
    }

    private func missingSection(_ p: ContentInventoryPayload) -> some View {
        let rows = p.missing ?? p.missingSample ?? []
        return VStack(alignment: .leading, spacing: 8) {
            Text("Missing (first \(rows.count))").font(.headline)
            if rows.isEmpty {
                Text("None").font(.caption).foregroundColor(.secondary)
            } else {
                Table(rows) {
                    TableColumn("Type") { (m: ContentInventoryMissing) in Text(m.type).font(.caption.monospaced()) }
                    TableColumn("Teacher") { m in Text(m.teacher ?? "—").font(.caption) }
                    TableColumn("Action") { m in Text(m.action ?? "").font(.caption2).lineLimit(3) }
                }
                .frame(minHeight: 180)
            }
        }
    }

    private func commandsSection(_ p: ContentInventoryPayload) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Commands").font(.headline)
            ForEach(Array((p.commands ?? [:]).keys.sorted()), id: \.self) { key in
                if let cmd = p.commands?[key] {
                    HStack {
                        Text(key).font(.caption.monospaced()).frame(width: 140, alignment: .leading)
                        Button("Copy") { copy(cmd) }
                        Text(cmd).font(.caption2.monospaced()).lineLimit(3).foregroundColor(.secondary)
                    }
                }
            }
        }
    }

    private func copy(_ s: String) {
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(s, forType: .string)
        toast = "Copied"
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) { toast = nil }
    }

    private func inventoryURL() -> URL? {
        guard !state.repoPath.isEmpty else { return nil }
        let root = (state.repoPath as NSString).expandingTildeInPath
        return URL(fileURLWithPath: root).appendingPathComponent("artifacts/inventory/content_inventory.json")
    }

    private func loadInventory() {
        loadError = nil
        payload = nil
        guard let url = inventoryURL(), FileManager.default.fileExists(atPath: url.path) else {
            loadError = "Missing artifacts/inventory/content_inventory.json — run Scan repo."
            return
        }
        do {
            let data = try Data(contentsOf: url)
            let decoder = JSONDecoder()
            decoder.keyDecodingStrategy = .convertFromSnakeCase
            payload = try decoder.decode(ContentInventoryPayload.self, from: data)
        } catch {
            loadError = error.localizedDescription
        }
    }

    private func runScan() {
        guard !state.repoPath.isEmpty else { return }
        logOutput = ""
        isScanning = true
        Task {
            do {
                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: "scripts/inventory/scan_content_inventory.py",
                    arguments: [],
                    timeoutSeconds: 600,
                    onOutput: { logOutput += $0 + "\n" }
                )
                await MainActor.run {
                    isScanning = false
                    loadInventory()
                    toast = "Scan finished"
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) { toast = nil }
                }
            } catch {
                await MainActor.run {
                    logOutput += "\nError: \(error)"
                    isScanning = false
                }
            }
        }
    }
}

private struct ContentInventoryPayload: Codable {
    let scanDate: String
    let repoRoot: String?
    let summary: ContentInventorySummary
    let teachers: [ContentInventoryTeacher]
    let missing: [ContentInventoryMissing]?
    let missingSample: [ContentInventoryMissing]?
    let commands: [String: String]?
}

private struct ContentInventorySummary: Codable {
    let catalogRows: Int?
    let totalConfigured: Int?
    let totalBuilt: Int?
    let coveragePct: Double?
    let missingCount: Int?
    let totalBuiltAssets: Int?
    let byType: [String: ContentInventoryTypeStat]
}

private struct ContentInventoryTypeStat: Codable {
    let configured: Int
    let built: Int
    let pct: Double
}

private struct ContentInventoryTeacher: Codable, Identifiable {
    let id: String
    let bookText: Bool
    let epub: Bool
    let cover: Bool
    let mangaCover: Bool
    let mangaPanels: Bool
    let videoPlan: Bool
    let videoYoutube: Bool
    let videoTiktok: Bool
    let audioPresenter: Bool
}

private struct ContentInventoryMissing: Codable, Identifiable {
    var id: String { [type, teacher ?? "", topic ?? "", action ?? ""].joined(separator: "|") }
    let type: String
    let teacher: String?
    let topic: String?
    let lane: String?
    let action: String?
}
