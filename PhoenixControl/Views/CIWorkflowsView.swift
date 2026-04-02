import SwiftUI

private let workflowCategories: [(title: String, patterns: [String])] = [
    ("Content Production", ["pearl-news", "catalog-book-pipeline", "full-catalog", "max-quality"]),
    ("Video & Media", ["video-daily-publish", "brand-admin-onboarding-pages"]),
    ("Translation", ["translate-atoms-qwen-matrix", "translate-bestseller-atoms", "locale-gate"]),
    ("ML & Quality", ["ml-loop-continuous", "ml-loop-daily-promotion", "ml-loop-weekly-recalibration", "ei-v2-gates"]),
    ("Research", ["research-pipeline-run", "research_feeds_ingest", "research-feeds-ingest"]),
    ("Marketing", ["marketing-briefs-and-proposals", "marketing-config-gate", "marketing_continuous", "marketing-continuous"]),
    ("Testing", ["core-tests", "release-gates", "teacher-gates", "brand-guards", "audiobook-regression", "simulation-10k"]),
    ("Operations", [
        "production-observability", "production-alerts", "change-impact", "github-governance-check",
        "docs-ci", "server-ci", "weekly-pipeline", "pages", "auto-merge-bot-fix", "remote-commit-review",
    ]),
]

private func matchesPattern(stem: String, pattern: String) -> Bool {
    let s = stem.replacingOccurrences(of: "_", with: "-")
    let p = pattern.replacingOccurrences(of: "_", with: "-")
    return s == p || s.contains(p) || p.contains(s)
}

private func findRun(for pattern: String, in map: [String: GitHubService.WorkflowRun]) -> GitHubService.WorkflowRun? {
    let p = pattern.replacingOccurrences(of: "_", with: "-")
    if let exact = map[pattern] ?? map[p] { return exact }
    for (stem, run) in map where matchesPattern(stem: stem, pattern: p) {
        return run
    }
    return nil
}

struct CIWorkflowsView: View {
    @ObservedObject var state: AppState
    let githubService: GitHubService

    @State private var latestByStem: [String: GitHubService.WorkflowRun] = [:]
    @State private var loadError: String?
    @State private var isLoading = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("CI / Workflows")
                    .font(.title2)
                    .foregroundColor(PhoenixColors.phoenixBlue)

                if !githubService.hasToken() {
                    Text("Set a GitHub token (Keychain) to load live workflow runs. Repo owner/name are read from `.git/config` origin.")
                        .foregroundColor(.secondary)
                }
                if let err = loadError {
                    Text(err).foregroundColor(.orange)
                }
                if isLoading { ProgressView().padding(.vertical, 8) }

                ForEach(Array(workflowCategories.enumerated()), id: \.offset) { _, cat in
                    categorySection(title: cat.title, patterns: cat.patterns)
                }
            }
            .padding()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .background(PhoenixColors.phoenixBackground)
        .onAppear { Task { await refresh() } }
    }

    @ViewBuilder
    private func categorySection(title: String, patterns: [String]) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            ForEach(patterns, id: \.self) { pattern in
                workflowRow(pattern: pattern)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    @ViewBuilder
    private func workflowRow(pattern: String) -> some View {
        let run = findRun(for: pattern, in: latestByStem)
        HStack(alignment: .center, spacing: 10) {
            Text(pattern)
                .font(.subheadline)
                .frame(minWidth: 220, alignment: .leading)
            if let run {
                StatusBadge(status: badgeStatus(for: run))
                Text(run.conclusion.capitalized)
                    .font(.caption)
                    .foregroundColor(.secondary)
                if let u = URL(string: run.htmlUrl) {
                    Link("Open run", destination: u)
                        .font(.caption)
                }
            } else {
                Text("No recent run")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }

    private func badgeStatus(for run: GitHubService.WorkflowRun) -> String {
        let s = (run.status ?? "").lowercased()
        let c = run.conclusion.lowercased()
        if s == "queued" || s == "in_progress" || s == "waiting" { return "pending" }
        if c == "success" { return "pass" }
        if c == "failure" { return "fail" }
        if c == "cancelled" || c == "skipped" { return "skip" }
        return "pending"
    }

    private func refresh() async {
        loadError = nil
        isLoading = true
        defer { isLoading = false }
        do {
            let map = try await githubService.latestRunsByWorkflowStem(perPage: 100)
            await MainActor.run {
                latestByStem = map
                state.workflowRuns = Array(map.values).sorted { ($0.updatedAt ?? "") > ($1.updatedAt ?? "") }
            }
        } catch {
            await MainActor.run { loadError = error.localizedDescription }
        }
    }
}
