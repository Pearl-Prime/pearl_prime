import SwiftUI

/// Phase 1 Operator Cockpit — Mandatory Preflight + Drift Detectors (read/analysis only).
struct PreflightGatesView: View {
    @ObservedObject var state: AppState
    let scriptRunner: ScriptRunner

    @State private var rows: [GateRowState] = GateCatalog.allRows.map { GateRowState(def: $0) }
    @State private var branchName: String = "—"
    @State private var aheadBehind: String = "—"
    @State private var isRefreshingGit: Bool = false
    @State private var isRunningAll: Bool = false
    @State private var activeRowID: String?

    private var overallVerdict: GateVerdict? {
        let finished = rows.compactMap(\.verdict)
        guard !finished.isEmpty, finished.count == rows.count else { return nil }
        if finished.contains(.block) { return .block }
        if finished.contains(.warn) { return .warn }
        return .pass
    }

    private var anyRunning: Bool {
        isRunningAll || activeRowID != nil
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            headerBar
            Divider()
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    gitStatusStrip
                    overallBanner
                    sectionBlock(
                        title: "Mandatory Preflight",
                        subtitle: "CLAUDE.md checks — run before any land. Read/analysis only.",
                        ids: GateCatalog.preflightIDs
                    )
                    sectionBlock(
                        title: "Drift Detectors",
                        subtitle: "Required-check set — stub-as-done, listing-as-story, unwired-config, chord, native-check, claim-language.",
                        ids: GateCatalog.driftIDs
                    )
                }
                .padding()
            }
        }
        .background(PhoenixColors.phoenixBackground)
        .onAppear { refreshGitStrip() }
        .onChange(of: state.repoPath) { _ in refreshGitStrip() }
    }

    // MARK: - Header

    private var headerBar: some View {
        HStack(spacing: 12) {
            Text("Preflight & Gates")
                .font(.title2.bold())
            Spacer()
            if anyRunning {
                Button("Cancel") { scriptRunner.cancel() }
            }
            Button("Refresh git") { refreshGitStrip() }
                .disabled(state.repoPath.isEmpty || isRefreshingGit)
            Button(isRunningAll ? "Running all…" : "Run all") {
                runAll()
            }
            .disabled(state.repoPath.isEmpty || anyRunning)
            .keyboardShortcut("r", modifiers: [.command, .shift])
        }
        .padding(.horizontal)
        .padding(.vertical, 10)
    }

    // MARK: - Git strip

    private var gitStatusStrip: some View {
        HStack(spacing: 24) {
            VStack(alignment: .leading, spacing: 2) {
                Text("Branch").font(.caption).foregroundColor(.secondary)
                Text(branchName).font(.body.monospaced())
            }
            VStack(alignment: .leading, spacing: 2) {
                Text("origin/main…HEAD (left=behind / right=ahead)")
                    .font(.caption).foregroundColor(.secondary)
                Text(aheadBehind).font(.body.monospaced())
            }
            if isRefreshingGit {
                ProgressView().scaleEffect(0.7)
            }
            Spacer()
        }
        .padding(12)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    // MARK: - Banner

    @ViewBuilder
    private var overallBanner: some View {
        if let verdict = overallVerdict {
            let clear = verdict != .block
            HStack {
                Image(systemName: clear ? "checkmark.seal.fill" : "xmark.octagon.fill")
                    .foregroundColor(clear ? .green : .red)
                Text(clear ? "CLEAR TO LAND" : "BLOCKED")
                    .font(.headline)
                    .foregroundColor(clear ? .green : .red)
                if verdict == .warn {
                    Text("(WARN present — non-blocking)")
                        .font(.caption)
                        .foregroundColor(PhoenixColors.phoenixAmber)
                }
                Spacer()
                StatusBadge(status: clear ? "CLEAR TO LAND" : "BLOCKED")
            }
            .padding(12)
            .background((clear ? Color.green : Color.red).opacity(0.12))
            .cornerRadius(8)
        } else {
            HStack {
                Image(systemName: "shield.lefthalf.filled")
                    .foregroundColor(.secondary)
                Text("Run checks to get a land verdict. Exit 0 = PASS; nonzero = BLOCK; WARN in output + exit 0 = WARN.")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
            }
            .padding(12)
            .background(Color.secondary.opacity(0.08))
            .cornerRadius(8)
        }
    }

    // MARK: - Sections

    private func sectionBlock(title: String, subtitle: String, ids: [String]) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(title).font(.headline)
            Text(subtitle).font(.caption).foregroundColor(.secondary)
            ForEach(ids, id: \.self) { id in
                if let idx = rows.firstIndex(where: { $0.id == id }) {
                    gateRow(index: idx)
                }
            }
        }
    }

    private func gateRow(index: Int) -> some View {
        let row = rows[index]
        let running = activeRowID == row.id
        return VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline, spacing: 12) {
                VStack(alignment: .leading, spacing: 2) {
                    Text(row.def.name).font(.subheadline.bold())
                    Text(row.def.catches).font(.caption).foregroundColor(.secondary)
                    Text(row.def.scriptPath)
                        .font(.caption2.monospaced())
                        .foregroundColor(.secondary)
                }
                Spacer()
                if let verdict = row.verdict {
                    StatusBadge(status: verdict.badgeLabel)
                } else if running {
                    StatusBadge(status: "RUNNING")
                } else {
                    StatusBadge(status: "PENDING")
                }
                Button("Run") { runOne(id: row.id) }
                    .disabled(state.repoPath.isEmpty || anyRunning)
            }
            if !row.log.isEmpty || running {
                LiveLogView(logText: Binding(
                    get: { rows[index].log },
                    set: { rows[index].log = $0 }
                ), isRunning: running, exitCode: row.exitCode)
                .frame(minHeight: 80, maxHeight: 160)
            }
        }
        .padding(12)
        .background(PhoenixColors.phoenixWhite)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(PhoenixColors.phoenixBlue.opacity(0.2), lineWidth: 1)
        )
        .cornerRadius(8)
    }

    // MARK: - Actions

    private func refreshGitStrip() {
        guard !state.repoPath.isEmpty else {
            branchName = "—"
            aheadBehind = "—"
            return
        }
        isRefreshingGit = true
        let repo = (state.repoPath as NSString).expandingTildeInPath
        DispatchQueue.global(qos: .userInitiated).async {
            let branch = Self.runGit(repo: repo, args: ["branch", "--show-current"]).trimmingCharacters(in: .whitespacesAndNewlines)
            let lr = Self.runGit(repo: repo, args: ["rev-list", "--left-right", "--count", "origin/main...HEAD"])
                .trimmingCharacters(in: .whitespacesAndNewlines)
            DispatchQueue.main.async {
                branchName = branch.isEmpty ? "(detached / unknown)" : branch
                aheadBehind = lr.isEmpty ? "(unavailable — fetch origin?)" : lr
                isRefreshingGit = false
            }
        }
    }

    private func runAll() {
        guard !state.repoPath.isEmpty, !anyRunning else { return }
        isRunningAll = true
        Task {
            for def in GateCatalog.allRows {
                await execute(def: def)
            }
            await MainActor.run {
                isRunningAll = false
                activeRowID = nil
                refreshGitStrip()
            }
        }
    }

    private func runOne(id: String) {
        guard !state.repoPath.isEmpty, !anyRunning else { return }
        guard let def = GateCatalog.allRows.first(where: { $0.id == id }) else { return }
        Task {
            await execute(def: def)
            await MainActor.run {
                activeRowID = nil
                refreshGitStrip()
            }
        }
    }

    @MainActor
    private func resetRow(_ id: String) {
        guard let idx = rows.firstIndex(where: { $0.id == id }) else { return }
        rows[idx].log = ""
        rows[idx].verdict = nil
        rows[idx].exitCode = nil
        activeRowID = id
    }

    private func execute(def: GateCheckDef) async {
        await MainActor.run { resetRow(def.id) }
        let args = def.argumentsBuilder()
        var captured = ""
        do {
            let code = try await scriptRunner.run(
                repoPath: state.repoPath,
                scriptPath: def.scriptPath,
                arguments: args,
                timeoutSeconds: def.timeoutSeconds,
                onOutput: { chunk in
                    DispatchQueue.main.async {
                        if let idx = rows.firstIndex(where: { $0.id == def.id }) {
                            rows[idx].log += chunk
                            if !chunk.hasSuffix("\n") { rows[idx].log += "\n" }
                        }
                    }
                    captured += chunk
                }
            )
            let verdict = GateVerdict.from(exitCode: code, output: captured)
            await MainActor.run {
                if let idx = rows.firstIndex(where: { $0.id == def.id }) {
                    rows[idx].exitCode = code
                    rows[idx].verdict = verdict
                    rows[idx].log += "\n— exit \(code) → \(verdict.badgeLabel)\n"
                }
                if activeRowID == def.id { activeRowID = nil }
            }
        } catch {
            await MainActor.run {
                if let idx = rows.firstIndex(where: { $0.id == def.id }) {
                    rows[idx].log += "\nError: \(error)\n"
                    rows[idx].verdict = .block
                    rows[idx].exitCode = -1
                }
                if activeRowID == def.id { activeRowID = nil }
            }
        }
    }

    /// Read-only git helper (not via ScriptRunner — no allowlist needed for git itself).
    private static func runGit(repo: String, args: [String]) -> String {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/git")
        process.arguments = args
        process.currentDirectoryURL = URL(fileURLWithPath: repo)
        var env = ProcessInfo.processInfo.environment
        env["GIT_LFS_SKIP_SMUDGE"] = "1"
        process.environment = env
        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = Pipe()
        do {
            try process.run()
            process.waitUntilExit()
        } catch {
            return ""
        }
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        return String(data: data, encoding: .utf8) ?? ""
    }
}

// MARK: - Models

enum GateVerdict: Equatable {
    case pass
    case warn
    case block

    var badgeLabel: String {
        switch self {
        case .pass: return "PASS"
        case .warn: return "WARN"
        case .block: return "BLOCK"
        }
    }

    /// Exit 0 = PASS; nonzero = BLOCK. WARN/warning in output + exit 0 = WARN.
    /// Never infer PASS from output text alone.
    static func from(exitCode: Int32, output: String) -> GateVerdict {
        if exitCode != 0 { return .block }
        let lower = output.lowercased()
        if lower.contains("warn") || lower.contains("warning") {
            return .warn
        }
        return .pass
    }
}

struct GateCheckDef: Identifiable {
    let id: String
    let name: String
    let catches: String
    let scriptPath: String
    let timeoutSeconds: Int
    let argumentsBuilder: () -> [String]
}

struct GateRowState: Identifiable {
    let def: GateCheckDef
    var id: String { def.id }
    var log: String = ""
    var verdict: GateVerdict?
    var exitCode: Int32?
}

enum GateCatalog {
    static let preflightIDs = ["push_guard", "preflight_push", "health_check", "rap", "pr_gov"]
    static let driftIDs = [
        "render_bytes", "manga_story", "manga_wiring",
        "canonical_chord", "native_check", "claim_language",
    ]

    static let allRows: [GateCheckDef] = [
        GateCheckDef(
            id: "push_guard",
            name: "push_guard.py",
            catches: "Push safety — branch base, file caps, LFS, forbidden patterns.",
            scriptPath: "scripts/git/push_guard.py",
            timeoutSeconds: 120,
            argumentsBuilder: { [] }
        ),
        GateCheckDef(
            id: "preflight_push",
            name: "preflight_push.sh",
            catches: "Local preflight before push — hooks and readiness surface.",
            scriptPath: "scripts/ci/preflight_push.sh",
            timeoutSeconds: 300,
            argumentsBuilder: { [] }
        ),
        GateCheckDef(
            id: "health_check",
            name: "health_check.sh",
            catches: "Hourly repo health — branch/status/fetch hygiene.",
            scriptPath: "scripts/git/health_check.sh",
            timeoutSeconds: 180,
            argumentsBuilder: { [] }
        ),
        GateCheckDef(
            id: "rap",
            name: "check_rap_compliance.py",
            catches: "RAP — warns on direct ComfyUI/Ollama bypass of queue-first dispatch.",
            scriptPath: "scripts/ci/check_rap_compliance.py",
            timeoutSeconds: 120,
            argumentsBuilder: { [] }
        ),
        GateCheckDef(
            id: "pr_gov",
            name: "pr_governance_review.py",
            catches: "PR governance — mass deletion, size, subsystem scope, freeze.",
            scriptPath: "scripts/ci/pr_governance_review.py",
            timeoutSeconds: 180,
            argumentsBuilder: { [] }
        ),
        GateCheckDef(
            id: "render_bytes",
            name: "check_render_progress_bytes.py",
            catches: "stub-as-done — RENDER_PROGRESS ok/done with bytes < 50_000.",
            scriptPath: "scripts/ci/check_render_progress_bytes.py",
            timeoutSeconds: 180,
            argumentsBuilder: { [] }
        ),
        GateCheckDef(
            id: "manga_story",
            name: "check_manga_story_authored.py",
            catches: "listing-as-story — series_plan without authored handoff panels.",
            scriptPath: "scripts/ci/check_manga_story_authored.py",
            timeoutSeconds: 180,
            argumentsBuilder: { [] }
        ),
        GateCheckDef(
            id: "manga_wiring",
            name: "check_manga_wiring.py",
            catches: "unwired-config-as-working — config/manga with no consumer.",
            scriptPath: "scripts/ci/check_manga_wiring.py",
            timeoutSeconds: 180,
            argumentsBuilder: { [] }
        ),
        GateCheckDef(
            id: "canonical_chord",
            name: "check_canonical_pipeline_path.py",
            catches: "bestseller four-piece chord — incomplete production run_pipeline invocations.",
            scriptPath: "scripts/ci/check_canonical_pipeline_path.py",
            timeoutSeconds: 180,
            argumentsBuilder: { [] }
        ),
        GateCheckDef(
            id: "native_check",
            name: "check_native_check.py",
            catches: "translation native-check — bootstrap-mode JSON probe.",
            scriptPath: "scripts/ci/check_native_check.py",
            timeoutSeconds: 300,
            argumentsBuilder: {
                let tmp = FileManager.default.temporaryDirectory
                    .appendingPathComponent("phoenix_native_check_\(UUID().uuidString).json")
                return ["--bootstrap-mode", "--json-out", tmp.path]
            }
        ),
        GateCheckDef(
            id: "claim_language",
            name: "check_acceptance_claim_language.py",
            catches: "claim-language G-CLAIM — bestseller/shippable without acceptance layer.",
            scriptPath: "scripts/ci/check_acceptance_claim_language.py",
            timeoutSeconds: 180,
            argumentsBuilder: { [] }
        ),
    ]
}
