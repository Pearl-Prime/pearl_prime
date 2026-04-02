import SwiftUI

enum VideoConfigParser {
    static func statuses(from root: [String: Any]?) -> [VideoPublishStatus] {
        guard let root,
              let map = root["brand_platform_map"] as? [String: Any] else { return [] }
        let platforms = ["youtube", "youtube_shorts", "tiktok", "instagram_reels"]
        var out: [VideoPublishStatus] = []
        for (brandKey, val) in map.sorted(by: { $0.key < $1.key }) {
            guard let brandDict = val as? [String: Any] else { continue }
            for plat in platforms {
                let en = (brandDict[plat] as? Bool) ?? false
                var quota: Int?
                if let plats = root["platforms"] as? [String: Any],
                   let pdef = plats[plat] as? [String: Any],
                   let rl = pdef["rate_limits"] as? [String: Any] {
                    if let m = rl["max_uploads_per_day"] as? Int { quota = m }
                }
                out.append(VideoPublishStatus(
                    brand: brandKey,
                    platform: plat,
                    enabled: en,
                    lastRun: nil,
                    dailyQuota: quota
                ))
            }
        }
        return out
    }
}

struct VideoPublishView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    let githubService: GitHubService

    @State private var videoRun: GitHubService.WorkflowRun?
    @State private var loadErr: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Video publishing")
                    .font(.title2)
                    .foregroundColor(PhoenixColors.phoenixBlue)

                if let err = loadErr { Text(err).foregroundColor(.orange) }

                if let run = videoRun {
                    HStack {
                        StatusBadge(status: run.conclusion == "success" ? "pass" : (run.conclusion == "failure" ? "fail" : "pending"))
                        Text("video-daily-publish — \(run.conclusion)")
                        if let u = URL(string: run.htmlUrl) {
                            Link("Latest run", destination: u)
                        }
                    }
                    .font(.caption)
                } else if githubService.hasToken() {
                    Text("No recent video-daily-publish run in last 100 Actions runs.")
                        .foregroundColor(.secondary)
                }

                Text("Brand × platform (from config/video/upload_config.yaml via dump script)")
                    .font(.headline)
                    .padding(.top, 8)

                let rows = state.videoPublishStatuses.prefix(12)
                if rows.isEmpty {
                    Text("Run dump script or set repo path — no matrix loaded.")
                        .foregroundColor(.secondary)
                } else {
                    LazyVGrid(columns: [GridItem(.adaptive(minimum: 160))], spacing: 8) {
                        ForEach(Array(rows)) { s in
                            VStack(alignment: .leading, spacing: 4) {
                                Text("\(s.brand)")
                                    .font(.caption.bold())
                                Text(s.platform)
                                    .font(.caption2)
                                Text(s.enabled ? "On" : "Off")
                                    .foregroundColor(s.enabled ? .green : .gray)
                                if let q = s.dailyQuota {
                                    Text("cap/day \(q)")
                                        .font(.caption2)
                                        .foregroundColor(.secondary)
                                }
                            }
                            .padding(8)
                            .background(PhoenixColors.phoenixCardTint)
                            .cornerRadius(6)
                        }
                    }
                }

                Text("Credential env vars use brand suffixes (_SP / _CC / _ND) per upload_config.yaml.")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .background(PhoenixColors.phoenixBackground)
        .onAppear { load() }
    }

    private func load() {
        guard !state.repoPath.isEmpty else { return }
        if let json = artifactReader.loadVideoUploadConfigJSON(repoPath: state.repoPath) {
            state.videoPublishStatuses = VideoConfigParser.statuses(from: json)
        }
        Task {
            do {
                let map = try await githubService.latestRunsByWorkflowStem(perPage: 100)
                let keys = map.keys.filter { $0.contains("video-daily-publish") }
                let run = keys.compactMap { map[$0] }.max(by: { ($0.updatedAt ?? "") < ($1.updatedAt ?? "") })
                await MainActor.run { videoRun = run }
            } catch {
                await MainActor.run { loadErr = error.localizedDescription }
            }
        }
    }
}
