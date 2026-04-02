import SwiftUI

struct MLLoopMonitorView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    let githubService: GitHubService

    private let stems = ["ml-loop-continuous", "ml-loop-daily-promotion", "ml-loop-weekly-recalibration", "editorial-weekly", "editorial_weekly"]

    @State private var runs: [String: GitHubService.WorkflowRun] = [:]
    @State private var error: String?
    @State private var snippet: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("ML loop")
                    .font(.title2)
                    .foregroundColor(PhoenixColors.phoenixBlue)

                if let error { Text(error).foregroundColor(.orange) }

                ForEach(stems, id: \.self) { stem in
                    HStack {
                        Text(stem.replacingOccurrences(of: "_", with: "-"))
                            .frame(minWidth: 200, alignment: .leading)
                            .font(.subheadline)
                        if let r = findRun(stem: stem) {
                            StatusBadge(status: r.conclusion == "success" ? "pass" : (r.conclusion == "failure" ? "fail" : "pending"))
                            Text(r.updatedAt ?? "—")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                            if let u = URL(string: r.htmlUrl) {
                                Link("Run", destination: u).font(.caption)
                            }
                        } else {
                            Text("No run")
                                .foregroundColor(.secondary)
                                .font(.caption)
                        }
                    }
                }

                if let snippet {
                    Text("Latest artifacts/ml_loop JSON (truncated)")
                        .font(.headline)
                        .padding(.top, 8)
                    Text(snippet)
                        .font(.system(.caption, design: .monospaced))
                        .textSelection(.enabled)
                }
            }
            .padding()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .background(PhoenixColors.phoenixBackground)
        .onAppear { refresh() }
    }

    private func findRun(stem: String) -> GitHubService.WorkflowRun? {
        let key = stem.replacingOccurrences(of: "_", with: "-")
        if let r = runs[key] { return r }
        return runs.first { entry in
            entry.key.contains(key) || key.contains(entry.key)
        }?.value
    }

    private func refresh() {
        snippet = artifactReader.loadMLLoopScoreSnippet(repoPath: state.repoPath)
        Task {
            do {
                let map = try await githubService.latestRunsByWorkflowStem(perPage: 100)
                await MainActor.run { runs = map }
            } catch {
                await MainActor.run { self.error = error.localizedDescription }
            }
        }
    }
}
