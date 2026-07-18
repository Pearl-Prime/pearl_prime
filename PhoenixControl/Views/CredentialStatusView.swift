import SwiftUI

struct CredentialStatusView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader

    @State private var isRefreshing = false
    @State private var lastError: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("Credentials")
                    .font(.title2)
                    .foregroundColor(PhoenixColors.phoenixBlue)
                Spacer()
                Button(action: { refresh() }) {
                    Label("Refresh", systemImage: "arrow.clockwise")
                }
                .disabled(state.repoPath.isEmpty || isRefreshing)
            }

            if state.repoPath.isEmpty {
                Text("Set repo path to run scripts/ci/check_integration_env.py --json")
                    .foregroundColor(.secondary)
            } else if isRefreshing {
                ProgressView("Checking environment…")
            } else if let err = lastError {
                Text(err).foregroundColor(.orange)
            }

            if let cred = state.credentialStatus {
                let total = max(cred.summary.total, 1)
                let frac = Double(cred.summary.set) / Double(total)
                VStack(alignment: .leading, spacing: 8) {
                    Text("\(cred.summary.set) of \(cred.summary.total) env vars set")
                        .font(.subheadline)
                    ProgressView(value: frac)
                    Text("Missing (any): \(cred.summary.missing)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(.bottom, 8)

                let grouped = Dictionary(grouping: cred.items) { $0.service ?? "Other" }
                ForEach(grouped.keys.sorted(), id: \.self) { svc in
                    Text(svc)
                        .font(.headline)
                        .padding(.top, 8)
                    ForEach(grouped[svc] ?? [], id: \.name) { item in
                        HStack {
                            Image(systemName: item.isSet ? "checkmark.circle.fill" : "xmark.circle.fill")
                                .foregroundColor(item.isSet ? .green : .red)
                            Text(item.name)
                                .font(.system(.body, design: .monospaced))
                            Spacer()
                            Text(item.required ? "required" : "optional")
                                .font(.caption2)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(item.required ? Color.red.opacity(0.15) : Color.gray.opacity(0.15))
                                .cornerRadius(4)
                        }
                    }
                }
            } else if !state.repoPath.isEmpty && !isRefreshing && lastError == nil {
                Text("No credential report (script missing or PyYAML/registry issue).")
                    .foregroundColor(.secondary)
            }
            Spacer()
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .background(PhoenixColors.phoenixBackground)
        .onAppear { refresh() }
    }

    private func refresh() {
        guard !state.repoPath.isEmpty else { return }
        isRefreshing = true
        lastError = nil
        Task.detached { [repoPath = state.repoPath] in
            let reader = ArtifactReader()
            let c = reader.loadCredentialStatus(repoPath: repoPath)
            await MainActor.run {
                state.credentialStatus = c
                if c == nil {
                    lastError = "Could not parse check_integration_env.py --json output."
                }
                isRefreshing = false
            }
        }
    }
}
