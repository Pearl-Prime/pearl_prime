import SwiftUI

struct DashboardView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    let githubService: GitHubService
    var onSelectObservability: (() -> Void)? = nil

    @State private var mlStemRuns: [String: GitHubService.WorkflowRun] = [:]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                if state.repoPath.isEmpty {
                    Text("Set repo path in Settings (or toolbar) to see status.")
                        .foregroundColor(.secondary)
                        .padding()
                } else {
                    observabilityPhaseCard
                    observabilityCard
                    evidenceCard
                    elevatedCard
                    branchProtectionCard

                    simulationCard
                    localeParityCard
                    videoCard
                    credentialsCard
                    translationCard
                    ciHealthCard
                    mlLoopCard
                }
            }
            .padding()
        }
        .background(PhoenixColors.phoenixBackground)
        .onAppear { refresh() }
        .onChange(of: state.refreshTrigger) { _ in refresh() }
        .task {
            await refreshCIHealth()
            await refreshMLStems()
        }
    }

    // MARK: - Existing cards

    private var observabilityPhaseCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Observability phase status (from repo)")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            if let phase = state.observabilityPhaseStatus {
                HStack(spacing: 16) {
                    phaseRow("P1 Observe", phase.p1Observe.rawValue)
                    phaseRow("P2 Document", phase.p2Document.rawValue)
                    phaseRow("P3 Elevate/fix", phase.p3ElevateFix.rawValue)
                    phaseRow("P4 Learn/enhance", phase.p4LearnEnhance.rawValue)
                }
            } else {
                Text("Run collector once to derive phase status.")
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private func phaseRow(_ label: String, _ value: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label).font(.caption).foregroundColor(.secondary)
            Text(value).font(.subheadline).fontWeight(.medium)
        }
    }

    private var observabilityCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Observability (POLES)")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            if let snap = state.lastSnapshot {
                HStack(spacing: 16) {
                    StatusBadge(status: "pass")
                    Text("\(snap.passed)")
                    StatusBadge(status: "fail")
                    Text("\(snap.failed)")
                    StatusBadge(status: "skip")
                    Text("\(snap.skipped)")
                }
                Text("Last: \(snap.timestamp)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            } else {
                Text("No snapshot yet. Run Collect signals in Observability tab.")
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private var evidenceCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Evidence log")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            if state.evidenceLogRows.isEmpty {
                Text("No evidence log entries. Run collector in Observability tab.")
                    .foregroundColor(.secondary)
            } else {
                Text("Last \(state.evidenceLogRows.count) entries. See Observability tab for full table.")
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private var elevatedCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Elevated failures")
                .font(.headline)
                .foregroundColor(state.elevatedFailures.isEmpty ? PhoenixColors.phoenixBlue : .red)
            if state.elevatedFailures.isEmpty {
                Text("0 failures — system healthy")
                    .foregroundColor(.secondary)
            } else {
                Text("\(state.elevatedFailures.count) failure(s) in elevated_failures.jsonl")
                    .foregroundColor(.red)
                if let onSelect = onSelectObservability {
                    Button("View in Observability tab", action: onSelect)
                        .font(.caption)
                }
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(state.elevatedFailures.isEmpty ? PhoenixColors.phoenixCardTint : Color.red.opacity(0.08))
        .cornerRadius(8)
    }

    private var branchProtectionCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Branch protection")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            Text("1. Settings → Branches → main: require Core tests")
            Text("2. Notifications: Email for Actions failures")
            Text("3. Watch repo: Custom → Actions")
            Text("4. Keep Production observability scheduled")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    // MARK: - New metric cards (7)

    private var simulationCard: some View {
        MetricCard(title: "Simulation pass rate", icon: "chart.bar.fill", accentColor: .blue) {
            if let s = state.simulationAnalysis {
                Text(String(format: "%.1f%%", s.passRate * 100))
                    .font(.system(size: 36, weight: .bold, design: .rounded))
                let ok = s.totalBooks - s.failures
                Text("\(ok) / \(s.totalBooks) books")
                    .foregroundColor(.secondary)
                if s.negativeTestsCaught > 0 {
                    Text("Phase 3 negatives caught: \(s.negativeTestsCaught)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            } else {
                Text("No pearl_prime_sim_*_analysis.json in artifacts/reports/")
                    .foregroundColor(.secondary)
            }
        }
    }

    private var localeParityCard: some View {
        MetricCard(title: "Locale parity", icon: "globe", accentColor: .teal) {
            let entries = state.localeParityEntries
            if entries.isEmpty {
                Text("No parity data — open Locale Parity tab or add LOCALE_PARITY_REPORT_*.md")
                    .foregroundColor(.secondary)
            } else {
                let locales = Array(Set(entries.map(\.locale))).sorted().prefix(6)
                HStack(spacing: 8) {
                    ForEach(Array(locales), id: \.self) { loc in
                        let avg = entries.filter { $0.locale == loc }.map(\.coverage)
                        let v = avg.isEmpty ? 0 : avg.reduce(0, +) / Double(avg.count)
                        VStack {
                            Text(loc).font(.caption2)
                            Text(String(format: "%.0f%%", v)).font(.caption.bold())
                        }
                        .padding(6)
                        .background(Color.teal.opacity(0.15))
                        .cornerRadius(6)
                    }
                }
            }
        }
    }

    private var videoCard: some View {
        MetricCard(title: "Video publishing", icon: "play.rectangle.fill", accentColor: .purple) {
            let preview = state.videoPublishStatuses.prefix(9)
            if preview.isEmpty {
                Text("No upload_config snapshot — ensure dump_video_config_json.py runs.")
                    .foregroundColor(.secondary)
            } else {
                LazyVGrid(columns: [GridItem(.adaptive(minimum: 88))], spacing: 6) {
                    ForEach(Array(preview)) { s in
                        Text(s.enabled ? "✓" : "·")
                            .font(.caption2)
                            .frame(width: 28, height: 28)
                            .background(s.enabled ? Color.green.opacity(0.2) : Color.gray.opacity(0.15))
                            .cornerRadius(4)
                    }
                }
            }
        }
    }

    private var credentialsCard: some View {
        MetricCard(title: "Credentials", icon: "key.fill", accentColor: .orange) {
            if let c = state.credentialStatus {
                let t = max(c.summary.total, 1)
                Text("\(c.summary.set) / \(c.summary.total) set")
                    .font(.title3.bold())
                ProgressView(value: Double(c.summary.set) / Double(t))
            } else {
                Text("Run integration env check (Credentials tab).")
                    .foregroundColor(.secondary)
            }
        }
    }

    private var translationCard: some View {
        MetricCard(title: "Translation pipeline", icon: "character.book.closed", accentColor: .indigo) {
            let counts = artifactReader.loadTranslationLocaleCounts(repoPath: state.repoPath)
            if counts.isEmpty {
                Text("No approved_atoms_localized trees found.")
                    .foregroundColor(.secondary)
            } else {
                ForEach(counts.keys.sorted(), id: \.self) { k in
                    HStack {
                        Text(k).font(.caption)
                        Spacer()
                        Text("\(counts[k] ?? 0) atoms").font(.caption.monospacedDigit())
                    }
                }
            }
        }
    }

    private var ciHealthCard: some View {
        MetricCard(title: "CI health (recent runs)", icon: "arrow.triangle.2.circlepath", accentColor: .cyan) {
            if let h = state.ciHealthSummary {
                HStack(spacing: 12) {
                    Label("\(h.passing) pass", systemImage: "checkmark.circle")
                    Label("\(h.failing) fail", systemImage: "xmark.circle")
                    Label("\(h.pending) pending", systemImage: "clock")
                }
                .font(.caption)
                Text("Sample: last \(h.total) workflow runs")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            } else {
                Text("Needs GitHub token + network (loading…)")
                    .foregroundColor(.secondary)
            }
        }
    }

    private var mlLoopCard: some View {
        MetricCard(title: "ML loop status", icon: "brain", accentColor: .pink) {
            let keys = ["ml-loop-continuous", "ml-loop-daily-promotion", "ml-loop-weekly-recalibration"]
            if mlStemRuns.isEmpty {
                Text("Open ML Loop tab or add GitHub token for live status.")
                    .foregroundColor(.secondary)
            } else {
                ForEach(keys, id: \.self) { k in
                    Group {
                        if let r = mlStemRuns[k] ?? mlStemRuns.first(where: { $0.key.contains(k) })?.value {
                            HStack {
                                Text(k).font(.caption)
                                Spacer()
                                Text(r.conclusion).font(.caption2)
                                Text(r.updatedAt ?? "")
                                    .font(.caption2)
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                }
            }
        }
    }

    private func refresh() {
        guard !state.repoPath.isEmpty else { return }
        state.lastSnapshot = artifactReader.loadLatestSnapshot(repoPath: state.repoPath)
        state.evidenceLogRows = artifactReader.loadEvidenceLog(repoPath: state.repoPath, limit: 20)
        state.elevatedFailures = artifactReader.loadElevatedFailures(repoPath: state.repoPath, limit: 50)
        state.observabilityPhaseStatus = artifactReader.loadObservabilityPhaseStatus(repoPath: state.repoPath)
        state.simulationAnalysis = artifactReader.loadSimulationAnalysis(repoPath: state.repoPath)
        state.credentialStatus = artifactReader.loadCredentialStatus(repoPath: state.repoPath)
        if let rep = artifactReader.loadLocaleParity(repoPath: state.repoPath) {
            state.localeParityEntries = rep.entries
        } else {
            state.localeParityEntries = []
        }
        if let json = artifactReader.loadVideoUploadConfigJSON(repoPath: state.repoPath) {
            state.videoPublishStatuses = VideoConfigParser.statuses(from: json)
        }
    }

    private func refreshCIHealth() async {
        guard githubService.hasToken(), !state.repoPath.isEmpty else { return }
        do {
            let h = try await githubService.ciHealthSummary(perPage: 100)
            await MainActor.run { state.ciHealthSummary = h }
        } catch {
            await MainActor.run { state.githubStatusMessage = error.localizedDescription }
        }
    }

    private func refreshMLStems() async {
        guard githubService.hasToken(), !state.repoPath.isEmpty else { return }
        do {
            let map = try await githubService.latestRunsByWorkflowStem(perPage: 100)
            await MainActor.run { mlStemRuns = map }
        } catch { }
    }
}
