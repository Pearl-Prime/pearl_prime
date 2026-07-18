import Foundation

/// Reads observability artifacts from repo path: snapshot, evidence_log.jsonl, elevated_failures.jsonl.
final class ArtifactReader {
    private let fileManager = FileManager.default

    /// Resolved repo root URL (expands tilde).
    func repoURL(repoPath: String) -> URL {
        URL(fileURLWithPath: (repoPath as NSString).expandingTildeInPath)
    }

    /// Latest signal snapshot from artifacts/observability/signal_snapshot*.json
    func loadLatestSnapshot(repoPath: String) -> ObservabilitySnapshot? {
        let observabilityDir = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/observability")
        guard let contents = try? fileManager.contentsOfDirectory(at: observabilityDir, includingPropertiesForKeys: [.contentModificationDateKey], options: .skipsHiddenFiles) else { return nil }
        let snapshots = contents.filter { $0.lastPathComponent.hasPrefix("signal_snapshot") && $0.pathExtension == "json" }
        guard let latest = snapshots.sorted(by: { a, b in
            ((try? a.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate) ?? .distantPast) >
            ((try? b.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate) ?? .distantPast)
        }).first else { return nil }
        guard let data = try? Data(contentsOf: latest) else { return nil }
        return try? JSONDecoder().decode(ObservabilitySnapshot.self, from: data)
    }

    /// Parse JSONL file into rows. Returns last `limit` lines (tail).
    func loadEvidenceLog(repoPath: String, limit: Int = 500) -> [EvidenceLogRow] {
        let path = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/observability/evidence_log.jsonl")
        return loadJSONL(path: path, limit: limit)
    }

    func loadElevatedFailures(repoPath: String, limit: Int = 200) -> [EvidenceLogRow] {
        let path = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/observability/elevated_failures.jsonl")
        return loadJSONL(path: path, limit: limit)
    }

    /// System governance report from artifacts/governance/system_governance_report.json
    func loadSystemGovernanceReport(repoPath: String) -> SystemGovernanceReport? {
        let path = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/governance/system_governance_report.json")
        guard let data = try? Data(contentsOf: path) else { return nil }
        return try? JSONDecoder().decode(SystemGovernanceReport.self, from: data)
    }

    /// Content coverage report from artifacts/content_coverage_report.json
    func loadContentCoverageReport(repoPath: String) -> ContentCoverageReport? {
        let path = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/content_coverage_report.json")
        guard let data = try? Data(contentsOf: path) else { return nil }
        return try? JSONDecoder().decode(ContentCoverageReport.self, from: data)
    }

    private func loadJSONL(path: URL, limit: Int) -> [EvidenceLogRow] {
        guard let content = try? String(contentsOf: path, encoding: .utf8) else { return [] }
        let lines = content.split(separator: "\n", omittingEmptySubsequences: true)
        let decoder = JSONDecoder()
        var rows: [EvidenceLogRow] = []
        for line in lines.suffix(limit) {
            guard let data = String(line).data(using: .utf8),
                  let row = try? decoder.decode(EvidenceLogRow.self, from: data) else { continue }
            rows.append(row)
        }
        return rows
    }

    /// Validate repo path: exists, contains scripts/ and artifacts (or key dirs).
    func validateRepoPath(_ path: String) -> (valid: Bool, message: String) {
        let expanded = (path as NSString).expandingTildeInPath
        guard !expanded.isEmpty else { return (false, "Repo path is empty") }
        var isDir: ObjCBool = false
        guard fileManager.fileExists(atPath: expanded, isDirectory: &isDir), isDir.boolValue else {
            return (false, "Path does not exist or is not a directory")
        }
        let url = URL(fileURLWithPath: expanded)
        let scripts = url.appendingPathComponent("scripts")
        let artifacts = url.appendingPathComponent("artifacts")
        guard fileManager.fileExists(atPath: scripts.path) else { return (false, "Missing scripts/ directory") }
        return (true, "OK")
    }

    /// Startup health check per plan: repo path set, dir exists, scripts/ present, artifacts/observability present or creatable, Python 3 resolvable.
    /// Returns (passed, message). Steps 1–4 must pass before tabs are enabled.
    func runStartupHealthCheck(repoPath: String) -> (passed: Bool, message: String) {
        guard !repoPath.isEmpty else { return (false, "Repo path not set.") }
        let expanded = (repoPath as NSString).expandingTildeInPath
        var isDir: ObjCBool = false
        guard fileManager.fileExists(atPath: expanded, isDirectory: &isDir), isDir.boolValue else {
            return (false, "Repo path not found or is not a directory.")
        }
        let url = URL(fileURLWithPath: expanded)
        let scripts = url.appendingPathComponent("scripts")
        guard fileManager.fileExists(atPath: scripts.path) else {
            return (false, "Missing scripts/ directory.")
        }
        let observabilityDir = url.appendingPathComponent("artifacts/observability")
        if !fileManager.fileExists(atPath: observabilityDir.path) {
            do {
                try fileManager.createDirectory(at: observabilityDir, withIntermediateDirectories: true)
            } catch {
                return (false, "artifacts/observability/ missing and could not be created.")
            }
        }
        guard checkPython3Resolvable() else {
            return (false, "Python 3 not found on PATH.")
        }
        return (true, "OK")
    }

    private func checkPython3Resolvable() -> Bool {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = ["python3", "--version"]
        process.standardOutput = FileHandle.nullDevice
        process.standardError = FileHandle.nullDevice
        do {
            try process.run()
            process.waitUntilExit()
            return process.terminationStatus == 0
        } catch {
            return false
        }
    }

    /// Real POLES phase status derived from repo files/runs (not static text).
    struct ObservabilityPhaseStatus {
        var p1Observe: PhaseState   // collector exists, snapshot present
        var p2Document: PhaseState  // evidence_log.jsonl has entries
        var p3ElevateFix: PhaseState // elevated_failures.jsonl + collector auto-fix
        var p4LearnEnhance: PhaseState // weekly trend / baseline learning automation

        enum PhaseState: String {
            case done = "Done"
            case partial = "Partial"
            case notYet = "Not yet"
        }
    }

    func loadObservabilityPhaseStatus(repoPath: String) -> ObservabilityPhaseStatus {
        let base = repoURL(repoPath: repoPath)
        let obsDir = base.appendingPathComponent("artifacts/observability")
        let collectorExists = fileManager.fileExists(atPath: base.appendingPathComponent("scripts/observability/collect_signals.py").path)
        let snapshot = loadLatestSnapshot(repoPath: repoPath)
        let evidenceRows = loadEvidenceLog(repoPath: repoPath, limit: 1)
        let elevatedRows = loadElevatedFailures(repoPath: repoPath, limit: 1)
        let evidenceFileExists = fileManager.fileExists(atPath: obsDir.appendingPathComponent("evidence_log.jsonl").path)
        let elevatedFileExists = fileManager.fileExists(atPath: obsDir.appendingPathComponent("elevated_failures.jsonl").path)
        // P4: no weekly trend / baseline learning automation in repo yet
        let p4AutomationExists = fileManager.fileExists(atPath: base.appendingPathComponent("scripts/observability/weekly_trend_report.py").path)
            || fileManager.fileExists(atPath: base.appendingPathComponent("scripts/observability/baseline_learning.py").path)

        let p1: ObservabilityPhaseStatus.PhaseState = (collectorExists && snapshot != nil) ? .done : (collectorExists ? .partial : .notYet)
        let p2: ObservabilityPhaseStatus.PhaseState = evidenceFileExists ? (evidenceRows.isEmpty ? .partial : .done) : .notYet
        let p3: ObservabilityPhaseStatus.PhaseState = (elevatedFileExists || (snapshot?.failed ?? 0) > 0) ? .partial : (collectorExists ? .partial : .notYet)
        let p4: ObservabilityPhaseStatus.PhaseState = p4AutomationExists ? .partial : .notYet

        return ObservabilityPhaseStatus(p1Observe: p1, p2Document: p2, p3ElevateFix: p3, p4LearnEnhance: p4)
    }

    // MARK: - Dashboard artifacts

    func loadSimulationAnalysis(repoPath: String) -> SimulationAnalysis? {
        let dir = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/reports")
        guard let contents = try? fileManager.contentsOfDirectory(at: dir, includingPropertiesForKeys: [.contentModificationDateKey], options: .skipsHiddenFiles) else { return nil }
        let matches = contents.filter { $0.lastPathComponent.hasPrefix("pearl_prime_sim_") && $0.lastPathComponent.hasSuffix("_analysis.json") }
        guard let latest = matches.sorted(by: modDateDesc).first,
              let data = try? Data(contentsOf: latest) else { return nil }
        return SimulationAnalysis.fromAnalysisJSON(data)
    }

    func loadLocaleParity(repoPath: String) -> LocaleParityReport? {
        let dir = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/localization")
        guard let contents = try? fileManager.contentsOfDirectory(at: dir, includingPropertiesForKeys: [.contentModificationDateKey], options: .skipsHiddenFiles) else { return nil }
        let reports = contents.filter { $0.lastPathComponent.hasPrefix("LOCALE_PARITY_REPORT_") && $0.lastPathComponent.hasSuffix(".md") }
        guard let latest = reports.sorted(by: modDateDesc).first,
              let text = try? String(contentsOf: latest, encoding: .utf8) else { return nil }
        return Self.parseLocaleParityMarkdown(text)
    }

    func loadFeedTrends(repoPath: String) -> String? {
        let dir = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/feeds")
        guard let contents = try? fileManager.contentsOfDirectory(at: dir, includingPropertiesForKeys: [.contentModificationDateKey], options: .skipsHiddenFiles) else { return nil }
        let files = contents.filter { $0.lastPathComponent.hasPrefix("daily_trend_summary_") && $0.lastPathComponent.hasSuffix(".md") }
        guard let latest = files.sorted(by: modDateDesc).first,
              let text = try? String(contentsOf: latest, encoding: .utf8) else { return nil }
        return text
    }

    func loadBookPassResults(repoPath: String) -> [BookPassResult] {
        let dir = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/book_pass")
        guard let contents = try? fileManager.contentsOfDirectory(at: dir, includingPropertiesForKeys: nil, options: .skipsHiddenFiles) else { return [] }
        var out: [BookPassResult] = []
        for url in contents where url.pathExtension == "json" {
            guard let data = try? Data(contentsOf: url),
                  let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { continue }
            let bid = obj["book_id"] as? String ?? obj["bookId"] as? String
            let passed = obj["passed"] as? Bool ?? obj["book_pass"] as? Bool
            out.append(BookPassResult(bookId: bid, passed: passed, path: url.path))
        }
        return out
    }

    func loadCredentialStatus(repoPath: String) -> CredentialStatus? {
        guard let data = runPythonScriptCaptureStdout(repoPath: repoPath, script: "scripts/ci/check_integration_env.py", arguments: ["--json"]) else { return nil }
        guard let payload = try? JSONDecoder().decode(IntegrationEnvJSONPayload.self, from: data) else { return nil }
        return payload.asCredentialStatus()
    }

    func loadVideoUploadConfigJSON(repoPath: String) -> [String: Any]? {
        guard let data = runPythonScriptCaptureStdout(repoPath: repoPath, script: "scripts/ci/dump_video_config_json.py", arguments: []) else { return nil }
        return (try? JSONSerialization.jsonObject(with: data)) as? [String: Any]
    }

    func loadTranslationLocaleCounts(repoPath: String) -> [String: Int] {
        let root = repoURL(repoPath: repoPath).appendingPathComponent("SOURCE_OF_TRUTH/teacher_banks")
        guard let personas = try? fileManager.contentsOfDirectory(at: root, includingPropertiesForKeys: nil, options: .skipsHiddenFiles) else { return [:] }
        var counts: [String: Int] = [:]
        for p in personas {
            var isDir: ObjCBool = false
            guard fileManager.fileExists(atPath: p.path, isDirectory: &isDir), isDir.boolValue else { continue }
            let locRoot = p.appendingPathComponent("approved_atoms_localized")
            guard let locales = try? fileManager.contentsOfDirectory(at: locRoot, includingPropertiesForKeys: nil, options: .skipsHiddenFiles) else { continue }
            for loc in locales {
                var isL: ObjCBool = false
                guard fileManager.fileExists(atPath: loc.path, isDirectory: &isL), isL.boolValue else { continue }
                let code = loc.lastPathComponent
                let sub = (try? fileManager.subpathsOfDirectory(atPath: loc.path)) ?? []
                let n = sub.filter { $0.hasSuffix(".yaml") || $0.hasSuffix(".yml") }.count
                counts[code, default: 0] += n
            }
        }
        return counts
    }

    func loadMLLoopScoreSnippet(repoPath: String) -> String? {
        let dir = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/ml_loop")
        guard let contents = try? fileManager.contentsOfDirectory(at: dir, includingPropertiesForKeys: [.contentModificationDateKey], options: .skipsHiddenFiles) else { return nil }
        let jsons = contents.filter { $0.pathExtension == "json" }
        guard let latest = jsons.sorted(by: modDateDesc).first,
              let data = try? Data(contentsOf: latest),
              let obj = try? JSONSerialization.jsonObject(with: data),
              let pretty = try? JSONSerialization.data(withJSONObject: obj, options: [.prettyPrinted, .sortedKeys]),
              let s = String(data: pretty, encoding: .utf8) else { return nil }
        return s.count > 4000 ? String(s.prefix(4000)) + "\n…" : s
    }

    /// YAML filenames under `approved_atoms_localized/<locale>/` for a teacher bank folder (matches `persona` row loosely).
    func listLocalizedAtomFiles(repoPath: String, personaRow: String, locale: String) -> [String] {
        let banks = repoURL(repoPath: repoPath).appendingPathComponent("SOURCE_OF_TRUTH/teacher_banks")
        guard let dirs = try? fileManager.contentsOfDirectory(at: banks, includingPropertiesForKeys: nil, options: .skipsHiddenFiles) else { return [] }
        let key = personaRow.lowercased().replacingOccurrences(of: " ", with: "_")
        let match = dirs.first { dir in
            let name = dir.lastPathComponent.lowercased()
            return name == key || name.contains(key) || key.contains(name)
        }
        guard let base = match?.appendingPathComponent("approved_atoms_localized").appendingPathComponent(locale) else { return [] }
        guard let sub = try? fileManager.subpathsOfDirectory(atPath: base.path) else { return [] }
        return sub.filter { $0.hasSuffix(".yaml") || $0.hasSuffix(".yml") }.sorted()
    }

    // MARK: - Projections

    /// Load revenue_forecast_{year}.json from artifacts/projections/.
    func loadRevenueForecast(repoPath: String, year: Int = 2026) -> RevenueForecast? {
        let path = repoURL(repoPath: repoPath)
            .appendingPathComponent("artifacts/projections/revenue_forecast_\(year).json")
        guard let data = try? Data(contentsOf: path) else { return nil }
        return try? JSONDecoder().decode(RevenueForecast.self, from: data)
    }

    /// Scan artifacts/projections/ for all per-brand plan JSON files (not revenue_forecast).
    func projectionPlanCount(repoPath: String, year: Int = 2026) -> Int {
        let dir = repoURL(repoPath: repoPath).appendingPathComponent("artifacts/projections")
        guard let contents = try? fileManager.contentsOfDirectory(at: dir, includingPropertiesForKeys: nil, options: .skipsHiddenFiles) else { return 0 }
        return contents.filter {
            $0.pathExtension == "json"
            && !$0.lastPathComponent.hasPrefix("revenue_forecast")
            && !$0.lastPathComponent.hasPrefix("adjustment_log")
            && $0.lastPathComponent.hasSuffix("_\(year).json")
        }.count
    }

    // MARK: - Manga Series Plan

    /// Load manga series plan via dump_manga_series_plan_json.py → [MangaBrandPlan].
    func loadMangaSeriesPlan(repoPath: String) -> [MangaBrandPlan] {
        guard let data = runPythonScriptCaptureStdout(
            repoPath: repoPath,
            script: "scripts/catalog/dump_manga_series_plan_json.py",
            arguments: []
        ) else { return [] }
        return (try? JSONDecoder().decode([MangaBrandPlan].self, from: data)) ?? []
    }

    private func modDateDesc(_ a: URL, _ b: URL) -> Bool {
        let da = (try? a.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate) ?? .distantPast
        let db = (try? b.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate) ?? .distantPast
        return da > db
    }

    private func runPythonScriptCaptureStdout(repoPath: String, script: String, arguments: [String]) -> Data? {
        let repo = URL(fileURLWithPath: (repoPath as NSString).expandingTildeInPath)
        let scriptURL = repo.appendingPathComponent(script)
        guard fileManager.fileExists(atPath: scriptURL.path) else { return nil }
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = ["python3", scriptURL.path] + arguments
        process.currentDirectoryURL = repo
        var env = ProcessInfo.processInfo.environment
        env["PYTHONPATH"] = repo.path
        process.environment = env
        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = FileHandle.nullDevice
        do {
            try process.run()
            process.waitUntilExit()
        } catch {
            return nil
        }
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        return data.isEmpty ? nil : data
    }

    private static func parseLocaleParityMarkdown(_ text: String) -> LocaleParityReport? {
        let lines = text.components(separatedBy: .newlines)
        var headerLocales: [String] = []
        var entries: [LocaleParityEntry] = []
        var inTable = false
        for line in lines {
            let t = line.trimmingCharacters(in: .whitespaces)
            guard t.contains("|") else { continue }
            let cells = t.split(separator: "|").map { $0.trimmingCharacters(in: .whitespaces) }
            let row = cells.filter { !$0.isEmpty }
            if row.isEmpty { continue }
            if row.count >= 2, row[0].lowercased().contains("persona") {
                headerLocales = Array(row.dropFirst())
                inTable = true
                continue
            }
            guard inTable, !headerLocales.isEmpty else { continue }
            if row[0].allSatisfy({ $0 == "-" || $0 == ":" || $0 == " " }) { continue }
            let persona = row[0]
            for (i, loc) in headerLocales.enumerated() where i + 1 < row.count {
                let cell = row[i + 1].replacingOccurrences(of: "%", with: "")
                if let pct = Double(cell) {
                    entries.append(LocaleParityEntry(persona: persona, locale: loc, coverage: pct))
                }
            }
        }
        if entries.isEmpty { return nil }
        return LocaleParityReport(entries: entries, localeColumns: headerLocales)
    }
}
