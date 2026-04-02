import Foundation

struct SimulationAnalysis {
    var passRate: Double
    var totalBooks: Int
    var failures: Int
    var negativeTestsCaught: Int

    static func fromAnalysisJSON(_ data: Data) -> SimulationAnalysis? {
        guard let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { return nil }
        let n = obj["n"] as? Int ?? 0
        let failed = obj["failed"] as? Int ?? 0
        let rate = obj["overall_pass_rate"] as? Double ?? 0
        var neg = 0
        if let p3 = obj["phase3_summary"] as? [String: Any],
           let pf = p3["phase3_failed"] as? Int {
            neg = pf
        }
        return SimulationAnalysis(passRate: rate, totalBooks: n, failures: failed, negativeTestsCaught: neg)
    }
}

struct CredentialSummary: Codable {
    var set: Int
    var missing: Int
    var total: Int
}

struct CredentialItem: Codable {
    var name: String
    var isSet: Bool
    var required: Bool
    var service: String?

    enum CodingKeys: String, CodingKey {
        case name = "env_var"
        case isSet = "set"
        case required
        case service
    }
}

struct CredentialStatus: Codable {
    var summary: CredentialSummary
    var items: [CredentialItem]
}

struct IntegrationEnvJSONPayload: Decodable {
    let summary: SummaryBlock
    let items: [ItemBlock]

    struct SummaryBlock: Decodable {
        let totalRows: Int
        let setCount: Int

        enum CodingKeys: String, CodingKey {
            case totalRows = "total_rows"
            case setCount = "set_count"
        }
    }

    struct ItemBlock: Decodable {
        let envVar: String
        let set: Bool
        let required: Bool
        let service: String?

        enum CodingKeys: String, CodingKey {
            case envVar = "env_var"
            case set
            case required
            case service
        }
    }

    func asCredentialStatus() -> CredentialStatus {
        let missing = summary.totalRows - summary.setCount
        let sum = CredentialSummary(set: summary.setCount, missing: missing, total: summary.totalRows)
        let credItems = items.map {
            CredentialItem(name: $0.envVar, isSet: $0.set, required: $0.required, service: $0.service)
        }
        return CredentialStatus(summary: sum, items: credItems)
    }
}

struct LocaleParityEntry: Identifiable, Hashable {
    var id: String { "\(persona)|\(locale)" }
    var persona: String
    var locale: String
    var coverage: Double
}

struct LocaleParityReport {
    var entries: [LocaleParityEntry]
    var localeColumns: [String]
}

struct VideoPublishStatus: Identifiable, Hashable {
    var id: String { "\(brand)|\(platform)" }
    var brand: String
    var platform: String
    var enabled: Bool
    var lastRun: String?
    var dailyQuota: Int?
}

struct CIHealthSummary {
    var passing: Int
    var failing: Int
    var pending: Int
    var total: Int
}

struct BookPassResult: Identifiable {
    var id: String { bookId ?? path }
    var bookId: String?
    var passed: Bool?
    var path: String
}
