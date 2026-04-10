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

// MARK: - Revenue Forecast (from artifacts/projections/revenue_forecast_{year}.json)

struct RevenueForecast: Codable {
    var year: Int
    var generatedAt: String
    var provenance: String
    var brandsIncluded: Int
    var totalTitlesProjected: Int
    var totalProjectedRevenueLow: Double
    var totalProjectedRevenueMid: Double
    var totalProjectedRevenueHigh: Double
    var blendedAsp: Double
    var baselineConversionRate: Double
    var monthly: [MonthlyRevenue]
    var byLane: [String: LaneRevenue]
    var byFormat: [String: FormatRevenue]

    enum CodingKeys: String, CodingKey {
        case year
        case generatedAt = "generated_at"
        case provenance
        case brandsIncluded = "brands_included"
        case totalTitlesProjected = "total_titles_projected"
        case totalProjectedRevenueLow = "total_projected_revenue_low"
        case totalProjectedRevenueMid = "total_projected_revenue_mid"
        case totalProjectedRevenueHigh = "total_projected_revenue_high"
        case blendedAsp = "blended_asp"
        case baselineConversionRate = "baseline_conversion_rate"
        case monthly
        case byLane = "by_lane"
        case byFormat = "by_format"
    }
}

struct MonthlyRevenue: Codable, Identifiable {
    var id: String { month }
    var month: String
    var monthNum: Int
    var titlesPublished: Int
    var revenueLow: Double
    var revenueMid: Double
    var revenueHigh: Double

    enum CodingKeys: String, CodingKey {
        case month
        case monthNum = "month_num"
        case titlesPublished = "titles_published"
        case revenueLow = "revenue_low"
        case revenueMid = "revenue_mid"
        case revenueHigh = "revenue_high"
    }
}

struct LaneRevenue: Codable {
    var titles: Int
    var revenueMid: Double
    var brandsCount: Int
    var marketMultiplier: Double

    enum CodingKeys: String, CodingKey {
        case titles
        case revenueMid = "revenue_mid"
        case brandsCount = "brands_count"
        case marketMultiplier = "market_multiplier"
    }
}

struct FormatRevenue: Codable {
    var count: Int
    var revenuePct: Double
    var revenueWeight: Double

    enum CodingKeys: String, CodingKey {
        case count
        case revenuePct = "revenue_pct"
        case revenueWeight = "revenue_weight"
    }
}

// MARK: - Manga Series Plan (from config/manga/manga_brand_series_plan.yaml via dump script)

struct MangaBrandPlan: Identifiable, Codable {
    var id: String { brandId }
    var brandId: String
    var teacher: String
    var genre: String
    var primaryLane: String
    var activeSeriesTarget: Int
    var newSeriesPerYear: Int
    var chaptersPerSeriesPerMonth: Int
    var maxChaptersBeforeVolume: Int
    var volumesPerYearTarget: Int
    var topicAllocation: [String: String]
    var webtoonEnabled: Bool
    var platformCadence: [String: String]
    var maxDormantMonths: Int
    var overlapNewOldWeeks: Int

    enum CodingKeys: String, CodingKey {
        case brandId = "brand_id"
        case teacher
        case genre
        case primaryLane = "primary_lane"
        case activeSeriesTarget = "active_series_target"
        case newSeriesPerYear = "new_series_per_year"
        case chaptersPerSeriesPerMonth = "chapters_per_series_per_month"
        case maxChaptersBeforeVolume = "max_chapters_before_volume"
        case volumesPerYearTarget = "volumes_per_year_target"
        case topicAllocation = "topic_allocation"
        case webtoonEnabled = "webtoon_enabled"
        case platformCadence = "platform_cadence"
        case maxDormantMonths = "max_dormant_months"
        case overlapNewOldWeeks = "overlap_new_old_weeks"
    }

    /// Cadence label based on chapters per month.
    var cadenceLabel: String {
        switch chaptersPerSeriesPerMonth {
        case 1: return "monthly"
        case 2: return "bi-weekly"
        case 3: return "tri-weekly"
        case 4...: return "weekly"
        default: return "\(chaptersPerSeriesPerMonth)×/mo"
        }
    }

    /// Annual chapter output across all active series.
    var annualChapters: Int {
        chaptersPerSeriesPerMonth * 12 * activeSeriesTarget
    }
}
