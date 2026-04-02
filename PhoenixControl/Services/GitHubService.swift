import Foundation

/// GitHub API for workflow runs and production-alert issues. Token stored in Keychain only.
final class GitHubService {
    static let keychainService = "com.phoenixomega.control"
    static let tokenAccount = "github_token"

    var repoOwner: String = ""
    var repoName: String = ""

    func applyGitRemoteFromRepoRoot(_ repoPath: String) {
        let root = (repoPath as NSString).expandingTildeInPath
        let configURL = URL(fileURLWithPath: root).appendingPathComponent(".git/config")
        guard let text = try? String(contentsOf: configURL, encoding: .utf8) else { return }
        var inOrigin = false
        for line in text.components(separatedBy: .newlines) {
            let t = line.trimmingCharacters(in: .whitespaces)
            if t.hasPrefix("[remote \"origin\"]") { inOrigin = true; continue }
            if t.hasPrefix("[") { inOrigin = false; continue }
            if inOrigin, t.hasPrefix("url = ") {
                let raw = String(t.dropFirst(6)).trimmingCharacters(in: .whitespaces)
                if let pair = Self.parseGitHubOwnerRepo(from: raw) {
                    repoOwner = pair.0
                    repoName = pair.1
                }
                return
            }
        }
    }

    private static func parseGitHubOwnerRepo(from url: String) -> (String, String)? {
        let u = url.trimmingCharacters(in: .whitespaces)
        if u.contains("github.com:") {
            let parts = u.split(separator: ":")
            guard let last = parts.last else { return nil }
            var path = String(last)
            if path.hasSuffix(".git") { path = String(path.dropLast(4)) }
            let bits = path.split(separator: "/")
            guard bits.count >= 2 else { return nil }
            return (String(bits[bits.count - 2]), String(bits[bits.count - 1]))
        }
        if let range = u.range(of: "github.com/") {
            var path = String(u[range.upperBound...])
            if path.hasSuffix(".git") { path = String(path.dropLast(4)) }
            if path.hasSuffix("/") { path = String(path.dropLast()) }
            let bits = path.split(separator: "/")
            guard bits.count >= 2 else { return nil }
            return (String(bits[bits.count - 2]), String(bits[bits.count - 1]))
        }
        return nil
    }

    enum GitHubError: Error {
        case noToken
        case rateLimited(retryAfterSeconds: Int?)
        case offline
        case invalidResponse(statusCode: Int)
    }

    func setToken(_ token: String) -> Bool {
        guard let data = token.data(using: .utf8) else { return false }
        deleteToken()
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: Self.keychainService,
            kSecAttrAccount as String: Self.tokenAccount,
            kSecValueData as String: data,
        ]
        return SecItemAdd(query as CFDictionary, nil) == errSecSuccess
    }

    func hasToken() -> Bool {
        getToken() != nil
    }

    func removeToken() {
        deleteToken()
    }

    private func getToken() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: Self.keychainService,
            kSecAttrAccount as String: Self.tokenAccount,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne,
        ]
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess, let data = result as? Data, let token = String(data: data, encoding: .utf8) else { return nil }
        return token
    }

    private func deleteToken() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: Self.keychainService,
            kSecAttrAccount as String: Self.tokenAccount,
        ]
        SecItemDelete(query as CFDictionary)
    }

    struct WorkflowRun: Identifiable {
        let id: Int
        let name: String
        let conclusion: String
        let htmlUrl: String
        let path: String?
        let status: String?
        let updatedAt: String?
    }

    struct Issue: Identifiable {
        let id: Int
        let title: String
        let url: String
    }

    func fetchWorkflowRuns(limit: Int = 10) async throws -> [WorkflowRun] {
        guard let token = getToken(), !token.isEmpty else { throw GitHubError.noToken }
        guard !repoOwner.isEmpty, !repoName.isEmpty else { return [] }
        let url = URL(string: "https://api.github.com/repos/\(repoOwner)/\(repoName)/actions/runs?per_page=\(limit)")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/vnd.github+json", forHTTPHeaderField: "Accept")
        request.setValue("2022-11-28", forHTTPHeaderField: "X-GitHub-Api-Version")
        let (data, response): (Data, URLResponse)
        do {
            (data, response) = try await URLSession.shared.data(for: request)
        } catch {
            if (error as NSError).code == NSURLErrorNotConnectedToInternet || (error as NSError).code == NSURLErrorNetworkConnectionLost {
                throw GitHubError.offline
            }
            throw error
        }
        guard let http = response as? HTTPURLResponse else { throw GitHubError.invalidResponse(statusCode: 0) }
        if http.statusCode == 403 {
            let retryAfter = http.value(forHTTPHeaderField: "Retry-After").flatMap(Int.init)
            throw GitHubError.rateLimited(retryAfterSeconds: retryAfter)
        }
        if http.statusCode != 200 { throw GitHubError.invalidResponse(statusCode: http.statusCode) }
        struct RunsResponse: Decodable {
            let workflow_runs: [RunEntry]?
            struct RunEntry: Decodable {
                let id: Int
                let name: String?
                let conclusion: String?
                let html_url: String?
                let path: String?
                let status: String?
                let updated_at: String?
            }
        }
        let decoded = try JSONDecoder().decode(RunsResponse.self, from: data)
        return (decoded.workflow_runs ?? []).prefix(limit).map { r in
            let conc = r.conclusion ?? (r.status == "completed" ? "unknown" : (r.status ?? "pending"))
            WorkflowRun(
                id: r.id,
                name: r.name ?? "Workflow",
                conclusion: conc,
                htmlUrl: r.html_url ?? "https://github.com/\(repoOwner)/\(repoName)/actions",
                path: r.path,
                status: r.status,
                updatedAt: r.updated_at
            )
        }
    }

    func latestRunsByWorkflowStem(perPage: Int = 100) async throws -> [String: WorkflowRun] {
        let runs = try await fetchWorkflowRuns(limit: perPage)
        var best: [String: WorkflowRun] = [:]
        for r in runs {
            guard let path = r.path else { continue }
            let stem = Self.workflowStem(from: path)
            guard let existing = best[stem] else {
                best[stem] = r
                continue
            }
            if Self.runIsNewer(r, than: existing) {
                best[stem] = r
            }
        }
        return best
    }

    func ciHealthSummary(perPage: Int = 100) async throws -> CIHealthSummary {
        let runs = try await fetchWorkflowRuns(limit: perPage)
        var passing = 0, failing = 0, pending = 0
        for r in runs {
            let st = (r.status ?? "").lowercased()
            if st == "completed" {
                let c = r.conclusion.lowercased()
                if c == "success" { passing += 1 }
                else if c == "failure" { failing += 1 }
                else { pending += 1 }
            } else {
                pending += 1
            }
        }
        return CIHealthSummary(passing: passing, failing: failing, pending: pending, total: runs.count)
    }

    private static func workflowStem(from path: String) -> String {
        let name = (path as NSString).lastPathComponent.lowercased()
        if name.hasSuffix(".yml") { return String(name.dropLast(4)) }
        if name.hasSuffix(".yaml") { return String(name.dropLast(5)) }
        return name
    }

    private static func runIsNewer(_ a: WorkflowRun, than b: WorkflowRun) -> Bool {
        guard let da = a.updatedAt, let db = b.updatedAt else { return a.id > b.id }
        return da > db
    }

    func fetchProductionAlertIssues(limit: Int = 10) async throws -> [Issue] {
        guard let token = getToken(), !token.isEmpty else { throw GitHubError.noToken }
        guard !repoOwner.isEmpty, !repoName.isEmpty else { return [] }
        let encoded = "repo:\(repoOwner)/\(repoName) label:production-alert is:open".addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
        let url = URL(string: "https://api.github.com/search/issues?q=\(encoded)&per_page=\(limit)")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/vnd.github+json", forHTTPHeaderField: "Accept")
        request.setValue("2022-11-28", forHTTPHeaderField: "X-GitHub-Api-Version")
        let (data, response): (Data, URLResponse)
        do {
            (data, response) = try await URLSession.shared.data(for: request)
        } catch {
            if (error as NSError).code == NSURLErrorNotConnectedToInternet || (error as NSError).code == NSURLErrorNetworkConnectionLost {
                throw GitHubError.offline
            }
            throw error
        }
        guard let http = response as? HTTPURLResponse else { throw GitHubError.invalidResponse(statusCode: 0) }
        if http.statusCode == 403 {
            let retryAfter = http.value(forHTTPHeaderField: "Retry-After").flatMap(Int.init)
            throw GitHubError.rateLimited(retryAfterSeconds: retryAfter)
        }
        if http.statusCode != 200 { throw GitHubError.invalidResponse(statusCode: http.statusCode) }
        struct SearchResponse: Decodable {
            let items: [IssueEntry]?
            struct IssueEntry: Decodable {
                let id: Int
                let title: String?
                let html_url: String?
            }
        }
        let decoded = try JSONDecoder().decode(SearchResponse.self, from: data)
        return (decoded.items ?? []).prefix(limit).map { i in
            Issue(
                id: i.id,
                title: i.title ?? "Issue",
                url: i.html_url ?? "https://github.com/\(repoOwner)/\(repoName)/issues"
            )
        }
    }
}
