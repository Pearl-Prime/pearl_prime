import SwiftUI

struct MangaStrategyView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader

    @State private var plans: [MangaBrandPlan] = []
    @State private var isLoading: Bool = false
    @State private var loadError: String?
    @State private var searchText: String = ""
    @State private var filterGenre: String = "All"
    @State private var filterLane: String = "All"

    private var genres: [String] {
        var g = Array(Set(plans.map(\.genre))).sorted()
        g.insert("All", at: 0)
        return g
    }

    private var lanes: [String] {
        var l = Array(Set(plans.map(\.primaryLane))).sorted()
        l.insert("All", at: 0)
        return l
    }

    private var filtered: [MangaBrandPlan] {
        plans.filter { plan in
            let matchesSearch = searchText.isEmpty
                || plan.brandId.localizedCaseInsensitiveContains(searchText)
                || plan.teacher.localizedCaseInsensitiveContains(searchText)
                || plan.genre.localizedCaseInsensitiveContains(searchText)
                || plan.topicAllocation.keys.contains(where: { $0.localizedCaseInsensitiveContains(searchText) })
            let matchesGenre = filterGenre == "All" || plan.genre == filterGenre
            let matchesLane = filterLane == "All" || plan.primaryLane == filterLane
            return matchesSearch && matchesGenre && matchesLane
        }
    }

    var body: some View {
        VStack(spacing: 0) {
            toolbarRow
            Divider()
            if isLoading {
                loadingView
            } else if let err = loadError {
                errorView(err)
            } else if plans.isEmpty {
                emptyView
            } else {
                ScrollView {
                    VStack(alignment: .leading, spacing: 12) {
                        summaryCard
                        portfolioOverviewCard
                        LazyVStack(spacing: 12) {
                            ForEach(filtered) { plan in
                                BrandSeriesCard(plan: plan)
                            }
                        }
                    }
                    .padding()
                }
            }
        }
        .background(PhoenixColors.phoenixBackground)
        .onAppear { loadPlans() }
        .onChange(of: state.refreshTrigger) { _ in loadPlans() }
        .onChange(of: state.repoPath) { _ in loadPlans() }
    }

    // MARK: - Toolbar

    private var toolbarRow: some View {
        HStack(spacing: 10) {
            Image(systemName: "books.vertical.fill")
                .foregroundColor(.purple)
            Text("Manga Brand Strategies")
                .font(.headline)
                .foregroundColor(PhoenixColors.phoenixBlue)
            Spacer()
            TextField("Search brand, teacher, topic…", text: $searchText)
                .textFieldStyle(.roundedBorder)
                .frame(width: 220)
            Picker("Genre", selection: $filterGenre) {
                ForEach(genres, id: \.self) { Text($0).tag($0) }
            }
            .frame(width: 130)
            Picker("Lane", selection: $filterLane) {
                ForEach(lanes, id: \.self) { Text($0).tag($0) }
            }
            .frame(width: 140)
            if !plans.isEmpty {
                Text("\(filtered.count) of \(plans.count)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            Button {
                loadPlans()
            } label: {
                Label("Reload", systemImage: "arrow.clockwise")
            }
            .buttonStyle(.bordered)
            .disabled(isLoading)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(PhoenixColors.phoenixCardTint)
    }

    // MARK: - Summary card

    private var summaryCard: some View {
        HStack(spacing: 20) {
            summaryPill(value: "\(plans.count)", label: "Brands", color: .purple)
            summaryPill(value: "\(plans.map(\.activeSeriesTarget).reduce(0, +))", label: "Total active series", color: .blue)
            summaryPill(value: "\(plans.map(\.newSeriesPerYear).reduce(0, +))", label: "New series / year", color: .green)
            summaryPill(value: "\(plans.map(\.annualChapters).reduce(0, +).formatted())", label: "Annual chapters", color: .orange)
            summaryPill(value: "\(plans.map(\.volumesPerYearTarget).reduce(0, +))", label: "Volumes / year", color: .teal)
            Spacer()
        }
        .padding()
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private func summaryPill(value: String, label: String, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(value)
                .font(.system(size: 22, weight: .bold, design: .rounded))
                .foregroundColor(color)
            Text(label)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
    }

    // MARK: - Portfolio overview (genre distribution)

    private var portfolioOverviewCard: some View {
        MetricCard(title: "Genre Distribution", icon: "chart.pie", accentColor: .purple) {
            let genreCounts = Dictionary(grouping: plans, by: \.genre)
                .mapValues(\.count)
                .sorted { $0.value > $1.value }

            HStack(spacing: 6) {
                ForEach(genreCounts, id: \.key) { genre, count in
                    VStack(spacing: 3) {
                        Text("\(count)")
                            .font(.system(size: 20, weight: .bold, design: .rounded))
                            .foregroundColor(genreColor(genre))
                        Text(genre)
                            .font(.caption2)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(genreColor(genre).opacity(0.12))
                    .cornerRadius(6)
                }
            }
        }
    }

    // MARK: - States

    private var loadingView: some View {
        VStack(spacing: 12) {
            ProgressView()
            Text("Loading manga series plans…")
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private func errorView(_ msg: String) -> some View {
        ErrorStateView(
            severity: .warning,
            title: "Could not load manga series plan",
            message: msg,
            suggestion: "Ensure config/manga/manga_brand_series_plan.yaml exists and PyYAML is installed (pip install pyyaml).",
            primaryAction: ("Retry", { loadPlans() })
        )
    }

    private var emptyView: some View {
        ErrorStateView(
            severity: .empty,
            title: "No manga brand plans found",
            message: "config/manga/manga_brand_series_plan.yaml may be missing or empty.",
            suggestion: "Run the projection system first or check the config file.",
            primaryAction: ("Reload", { loadPlans() })
        )
    }

    // MARK: - Data loading

    private func loadPlans() {
        guard !state.repoPath.isEmpty else { return }
        isLoading = true
        loadError = nil
        DispatchQueue.global(qos: .userInitiated).async {
            let result = artifactReader.loadMangaSeriesPlan(repoPath: state.repoPath)
            DispatchQueue.main.async {
                if result.isEmpty {
                    loadError = "No brands returned — check manga_brand_series_plan.yaml and PyYAML."
                } else {
                    plans = result
                    loadError = nil
                }
                isLoading = false
            }
        }
    }

    // MARK: - Helpers

    private func genreColor(_ genre: String) -> Color {
        switch genre {
        case "iyashikei":    return .teal
        case "seinen":       return .indigo
        case "shojo":        return .pink
        case "cultivation":  return .orange
        case "manhwa":       return .blue
        case "isekai":       return .purple
        case "shonen":       return .red
        case "webtoon_romance": return Color(red: 0.9, green: 0.4, blue: 0.6)
        default:             return .gray
        }
    }
}

// MARK: - Brand Series Card

private struct BrandSeriesCard: View {
    let plan: MangaBrandPlan

    @State private var isExpanded: Bool = false

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header row (always visible)
            Button {
                withAnimation(.easeInOut(duration: 0.15)) { isExpanded.toggle() }
            } label: {
                HStack(spacing: 12) {
                    // Genre badge
                    Text(plan.genre)
                        .font(.caption2.bold())
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(genreColor.opacity(0.15))
                        .foregroundColor(genreColor)
                        .cornerRadius(4)

                    VStack(alignment: .leading, spacing: 2) {
                        Text(plan.brandId.replacingOccurrences(of: "_", with: " ").capitalized)
                            .font(.subheadline.bold())
                            .foregroundColor(.primary)
                        Text("Teacher: \(plan.teacher)  ·  \(plan.primaryLane)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    Spacer()

                    // Key metrics chips
                    HStack(spacing: 8) {
                        chip(value: "\(plan.activeSeriesTarget)", label: "active", color: .blue)
                        chip(value: "\(plan.newSeriesPerYear)/yr", label: "new", color: .green)
                        chip(value: plan.cadenceLabel, label: "cadence", color: .orange)
                        chip(value: "\(plan.volumesPerYearTarget) vol/yr", label: "output", color: .purple)
                    }

                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(12)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)

            if isExpanded {
                Divider().padding(.horizontal, 12)
                expandedContent
            }
        }
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(genreColor.opacity(0.25), lineWidth: 1)
        )
    }

    private var expandedContent: some View {
        HStack(alignment: .top, spacing: 24) {
            // Topics
            VStack(alignment: .leading, spacing: 6) {
                Text("Topic allocation")
                    .font(.caption.bold())
                    .foregroundColor(.secondary)
                ForEach(plan.topicAllocation.sorted(by: { $0.key < $1.key }), id: \.key) { topic, value in
                    HStack(spacing: 6) {
                        Circle()
                            .fill(Color.teal.opacity(0.6))
                            .frame(width: 6, height: 6)
                        Text(topic.replacingOccurrences(of: "_", with: " ").capitalized)
                            .font(.caption)
                        Spacer()
                        Text(value)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            .frame(minWidth: 160)

            Divider()

            // Series mechanics
            VStack(alignment: .leading, spacing: 6) {
                Text("Series mechanics")
                    .font(.caption.bold())
                    .foregroundColor(.secondary)
                row("Chapters / series / month", "\(plan.chaptersPerSeriesPerMonth)")
                row("Max chapters → volume",    "\(plan.maxChaptersBeforeVolume)")
                row("Max dormant (months)",     "\(plan.maxDormantMonths)")
                row("Overlap new/old (weeks)",  "\(plan.overlapNewOldWeeks)")
                row("Annual chapters (all series)", "\(plan.annualChapters.formatted())")
            }

            Divider()

            // Platform cadence
            VStack(alignment: .leading, spacing: 6) {
                Text("Webtoon platform cadence")
                    .font(.caption.bold())
                    .foregroundColor(.secondary)
                if plan.platformCadence.isEmpty {
                    Text("—").font(.caption).foregroundColor(.secondary)
                } else {
                    ForEach(plan.platformCadence.sorted(by: { $0.key < $1.key }), id: \.key) { lane, cadence in
                        HStack(spacing: 6) {
                            Image(systemName: "globe")
                                .font(.caption2)
                                .foregroundColor(.blue)
                            Text(lane.replacingOccurrences(of: "_", with: " "))
                                .font(.caption)
                            Spacer()
                            Text(cadence.replacingOccurrences(of: "_", with: "-"))
                                .font(.caption.bold())
                                .foregroundColor(cadenceColor(cadence))
                        }
                    }
                }
            }
        }
        .padding(12)
    }

    private func row(_ label: String, _ value: String) -> some View {
        HStack {
            Text(label).font(.caption).foregroundColor(.secondary)
            Spacer()
            Text(value).font(.caption.monospacedDigit()).fontWeight(.medium)
        }
    }

    private func chip(value: String, label: String, color: Color) -> some View {
        VStack(spacing: 1) {
            Text(value).font(.caption2.bold()).foregroundColor(color)
            Text(label).font(.system(size: 9)).foregroundColor(.secondary)
        }
        .padding(.horizontal, 7)
        .padding(.vertical, 4)
        .background(color.opacity(0.10))
        .cornerRadius(4)
    }

    private func cadenceColor(_ cadence: String) -> Color {
        switch cadence {
        case "weekly":    return .green
        case "bi_weekly", "bi-weekly": return .blue
        case "monthly":   return .orange
        default:          return .secondary
        }
    }

    private var genreColor: Color {
        switch plan.genre {
        case "iyashikei":    return .teal
        case "seinen":       return .indigo
        case "shojo":        return .pink
        case "cultivation":  return .orange
        case "manhwa":       return .blue
        case "isekai":       return .purple
        case "shonen":       return .red
        default:             return .gray
        }
    }
}
