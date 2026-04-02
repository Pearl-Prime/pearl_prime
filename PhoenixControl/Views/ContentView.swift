import SwiftUI

enum TabTag: String, CaseIterable, Identifiable {
    case dashboard
    case pipeline
    case simulation
    case tests
    case observability
    case gates
    case pearlNews
    case manualReview
    case teacher
    case ci
    case credentials
    case video
    case localeParity
    case mlLoop
    case docs

    var id: String { rawValue }

    static let sidebarSections: [(String, [TabTag])] = [
        ("Core", [.dashboard, .pipeline, .simulation]),
        ("Quality", [.tests, .gates, .observability, .teacher]),
        ("Content", [.pearlNews, .manualReview]),
        ("Operations", [.ci, .credentials, .video, .localeParity, .mlLoop, .docs]),
    ]

    var title: String {
        switch self {
        case .dashboard: return "Dashboard"
        case .pipeline: return "Pipeline"
        case .simulation: return "Simulation"
        case .tests: return "Tests"
        case .observability: return "Observability"
        case .gates: return "Gates & Release"
        case .pearlNews: return "Pearl News"
        case .manualReview: return "Manual Review"
        case .teacher: return "Teacher"
        case .ci: return "CI / Workflows"
        case .credentials: return "Credentials"
        case .video: return "Video"
        case .localeParity: return "Locale Parity"
        case .mlLoop: return "ML Loop"
        case .docs: return "Docs & Config"
        }
    }

    var systemImage: String {
        switch self {
        case .dashboard: return "gauge.medium"
        case .pipeline: return "book"
        case .simulation: return "chart.bar"
        case .tests: return "checkmark.circle"
        case .observability: return "waveform.path.ecg"
        case .gates: return "lock.shield"
        case .pearlNews: return "newspaper"
        case .manualReview: return "tray.2"
        case .teacher: return "person.crop.circle"
        case .ci: return "arrow.triangle.2.circlepath"
        case .credentials: return "key.fill"
        case .video: return "play.rectangle"
        case .localeParity: return "globe"
        case .mlLoop: return "brain"
        case .docs: return "doc.text"
        }
    }
}

struct ContentView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    let scriptRunner: ScriptRunner
    let githubService: GitHubService
    @State private var selectedTab: TabTag = .dashboard
    @State private var showingPathSheet = false
    @State private var pathInput: String = ""

    private var startupBlocked: Bool {
        guard let passed = state.healthCheckPassed else { return true }
        return !passed
    }

    var body: some View {
        Group {
            if startupBlocked {
                ErrorStateView(
                    severity: .critical,
                    title: "Repo path not set or invalid.",
                    message: state.healthCheckMessage ?? "The app could not validate the repo path, scripts directory, artifacts/observability, or Python 3.",
                    suggestion: "Open Settings and set a valid repo root path that contains scripts/ and where artifacts/observability can exist. Ensure Python 3 is on PATH.",
                    primaryAction: ("Open Settings", { pathInput = state.repoPath; showingPathSheet = true }),
                    secondaryAction: nil
                )
            } else {
                mainContent
            }
        }
        .onAppear { runStartupHealthCheckIfNeeded() }
        .onChange(of: state.repoPath) { _, _ in runStartupHealthCheckIfNeeded() }
        .sheet(isPresented: $showingPathSheet) {
            pathSheet
        }
        .onChange(of: pathInput) { _, _ in
            if !showingPathSheet { return }
            let (valid, _) = artifactReader.validateRepoPath(pathInput)
            state.repoPathValid = valid
        }
        .onChange(of: showingPathSheet) { _, visible in
            if !visible { runStartupHealthCheckIfNeeded() }
        }
        .alert("Error", isPresented: Binding(
            get: { state.errorMessage != nil },
            set: { if !$0 { state.errorMessage = nil } }
        )) {
            Button("OK") { state.errorMessage = nil }
        } message: {
            if let msg = state.errorMessage {
                Text(msg)
            }
        }
    }

    private var mainContent: some View {
        VStack(spacing: 0) {
            if state.repoPathValid == false {
                ToolbarErrorStrip(message: "Repo path is invalid. Update it in Settings.", openSettings: {
                    pathInput = state.repoPath
                    showingPathSheet = true
                })
            }
            NavigationSplitView {
                List(selection: $selectedTab) {
                    ForEach(TabTag.sidebarSections, id: \.0) { section in
                        Section(header: Text(section.0)) {
                            ForEach(section.1, id: \.self) { tab in
                                Label(tab.title, systemImage: tab.systemImage)
                                    .tag(tab)
                            }
                        }
                    }
                }
                .listStyle(.sidebar)
                .navigationSplitViewColumnWidth(min: 180, ideal: 220)
            } detail: {
                detailContent
                    .frame(minWidth: 500, minHeight: 400)
            }
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    HStack(spacing: 8) {
                        Text(state.repoPath.isEmpty ? "Set repo path" : abbreviatedPath(state.repoPath))
                            .lineLimit(1)
                            .truncationMode(.middle)
                            .foregroundColor(state.repoPath.isEmpty ? .red : .primary)
                        Button(action: { pathInput = state.repoPath; showingPathSheet = true }) {
                            Image(systemName: "folder")
                        }
                    }
                }
            }
        }
    }

    private var detailContent: some View {
        Group {
            switch selectedTab {
            case .dashboard:
                DashboardView(state: state, artifactReader: artifactReader, githubService: githubService, onSelectObservability: { selectedTab = .observability })
            case .pipeline:
                PipelineView(state: state, scriptRunner: scriptRunner)
            case .simulation:
                SimulationView(state: state, scriptRunner: scriptRunner)
            case .tests:
                TestsView(state: state, scriptRunner: scriptRunner)
            case .observability:
                ObservabilityView(state: state, artifactReader: artifactReader, scriptRunner: scriptRunner)
            case .gates:
                GatesReleaseView(state: state, scriptRunner: scriptRunner)
            case .pearlNews:
                PearlNewsView(state: state, scriptRunner: scriptRunner)
            case .manualReview:
                ManualReviewView(state: state, artifactReader: artifactReader, scriptRunner: scriptRunner)
            case .teacher:
                TeacherView(state: state, scriptRunner: scriptRunner)
            case .ci:
                CIWorkflowsView(state: state, githubService: githubService)
            case .credentials:
                CredentialStatusView(state: state, artifactReader: artifactReader)
            case .video:
                VideoPublishView(state: state, artifactReader: artifactReader, githubService: githubService)
            case .localeParity:
                LocaleParityView(state: state, artifactReader: artifactReader)
            case .mlLoop:
                MLLoopMonitorView(state: state, artifactReader: artifactReader, githubService: githubService)
            case .docs:
                DocsConfigView(state: state, artifactReader: artifactReader, scriptRunner: scriptRunner)
            }
        }
    }

    private var pathSheet: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Repo path")
                .font(.headline)
            TextField("e.g. /Users/you/phoenix_omega", text: $pathInput)
                .textFieldStyle(.roundedBorder)
            if !pathInput.isEmpty {
                let result = artifactReader.validateRepoPath(pathInput)
                Text(result.message)
                    .font(.caption)
                    .foregroundColor(result.valid ? .green : .red)
            }
            HStack {
                Button("Cancel") { showingPathSheet = false }
                Button("Set") {
                    state.repoPath = pathInput
                    showingPathSheet = false
                }
                .disabled(pathInput.isEmpty)
            }
            .padding(.top, 8)
        }
        .padding(24)
        .frame(width: 420)
    }

    private func runStartupHealthCheckIfNeeded() {
        if state.repoPath.isEmpty {
            state.healthCheckPassed = false
            state.healthCheckMessage = "Repo path not set."
            state.repoPathValid = false
            return
        }
        let (passed, message) = artifactReader.runStartupHealthCheck(repoPath: state.repoPath)
        state.healthCheckPassed = passed
        state.healthCheckMessage = passed ? nil : message
        state.repoPathValid = passed
        if passed {
            githubService.applyGitRemoteFromRepoRoot(state.repoPath)
        }
    }

    private func abbreviatedPath(_ path: String) -> String {
        let expanded = (path as NSString).expandingTildeInPath
        let home = FileManager.default.homeDirectoryForCurrentUser.path
        if expanded.hasPrefix(home) {
            return "~" + String(expanded.dropFirst(home.count))
        }
        return path
    }
}
