import SwiftUI

struct ProjectionsView: View {
    @ObservedObject var state: AppState
    let artifactReader: ArtifactReader
    let scriptRunner: ScriptRunner

    @State private var forecast: RevenueForecast?
    @State private var planCount: Int = 0
    @State private var isRunningProjector: Bool = false
    @State private var isRunningPlanner: Bool = false
    @State private var logText: String = ""
    @State private var lastRunExitCode: Int32?
    @State private var selectedYear: Int = 2026

    private var forecastAvailable: Bool { forecast != nil }
    private var isBusy: Bool { isRunningProjector || isRunningPlanner }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                headerCard
                if let f = forecast {
                    annualSummaryCard(f)
                    monthlyCard(f)
                    laneCard(f)
                    formatCard(f)
                    provenanceCard(f)
                } else {
                    emptyStateCard
                }
                if !logText.isEmpty || isBusy {
                    logCard
                }
            }
            .padding()
        }
        .background(PhoenixColors.phoenixBackground)
        .onAppear { refresh() }
        .onChange(of: state.refreshTrigger) { _ in refresh() }
        .onChange(of: selectedYear) { _ in refresh() }
    }

    // MARK: - Header

    private var headerCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                Image(systemName: "chart.line.uptrend.xyaxis")
                    .foregroundColor(.green)
                    .font(.title3)
                Text("Revenue Projections \(selectedYear)")
                    .font(.title2.bold())
                    .foregroundColor(PhoenixColors.phoenixBlue)
                Spacer()
                Picker("Year", selection: $selectedYear) {
                    Text("2026").tag(2026)
                    Text("2027").tag(2027)
                }
                .pickerStyle(.segmented)
                .frame(width: 140)
            }

            HStack(spacing: 12) {
                statPill(
                    label: "Brand plans",
                    value: "\(planCount)",
                    color: planCount > 0 ? .green : .orange
                )
                statPill(
                    label: "Forecast",
                    value: forecastAvailable ? "Available" : "Not generated",
                    color: forecastAvailable ? .green : .red
                )
                Spacer()
                Button {
                    runProjectionPlanner()
                } label: {
                    Label(isRunningPlanner ? "Planning…" : "Run Planner (all brands)", systemImage: "calendar.badge.plus")
                }
                .disabled(isBusy || state.repoPath.isEmpty)
                .buttonStyle(.bordered)

                Button {
                    runRevenueProjector()
                } label: {
                    Label(isRunningProjector ? "Projecting…" : "Generate Forecast", systemImage: "arrow.triangle.2.circlepath")
                }
                .disabled(isBusy || state.repoPath.isEmpty)
                .buttonStyle(.borderedProminent)
                .tint(.green)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    private func statPill(label: String, value: String, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label).font(.caption2).foregroundColor(.secondary)
            Text(value).font(.caption.bold()).foregroundColor(color)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background(color.opacity(0.10))
        .cornerRadius(6)
    }

    // MARK: - Annual Summary

    private func annualSummaryCard(_ f: RevenueForecast) -> some View {
        MetricCard(title: "Annual Revenue Summary", icon: "dollarsign.circle.fill", accentColor: .green) {
            HStack(spacing: 24) {
                scenarioBlock(label: "Low", subtitle: "Conservative", value: f.totalProjectedRevenueLow, color: .orange)
                scenarioBlock(label: "Mid", subtitle: "Expected",      value: f.totalProjectedRevenueMid, color: .green)
                scenarioBlock(label: "High", subtitle: "Optimistic",   value: f.totalProjectedRevenueHigh, color: .blue)
                Divider().frame(height: 60)
                VStack(alignment: .leading, spacing: 4) {
                    Text("\(f.brandsIncluded) brands").font(.caption).foregroundColor(.secondary)
                    Text("\(f.totalTitlesProjected.formatted()) titles").font(.caption).foregroundColor(.secondary)
                    Text("Blended ASP $\(String(format: "%.2f", f.blendedAsp))").font(.caption).foregroundColor(.secondary)
                    Text("Conversion \(String(format: "%.1f%%", f.baselineConversionRate * 100))").font(.caption).foregroundColor(.secondary)
                }
            }
        }
    }

    private func scenarioBlock(label: String, subtitle: String, value: Double, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label).font(.caption).foregroundColor(.secondary)
            Text("$\(Int(value).formatted())")
                .font(.system(size: 28, weight: .bold, design: .rounded))
                .foregroundColor(color)
            Text(subtitle).font(.caption2).foregroundColor(.secondary)
        }
    }

    // MARK: - Monthly

    private func monthlyCard(_ f: RevenueForecast) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 8) {
                Image(systemName: "calendar").foregroundColor(.blue)
                Text("Monthly Breakdown").font(.headline).foregroundColor(PhoenixColors.phoenixBlue)
            }

            // Mini bar chart
            let maxRev = f.monthly.map(\.revenueMid).max() ?? 1
            HStack(alignment: .bottom, spacing: 3) {
                ForEach(f.monthly) { m in
                    VStack(spacing: 2) {
                        Spacer()
                        RoundedRectangle(cornerRadius: 3)
                            .fill(Color.green.opacity(0.65))
                            .frame(width: 18, height: max(4, CGFloat(m.revenueMid / maxRev) * 90))
                        Text(String(m.month.prefix(1)))
                            .font(.system(size: 8))
                            .foregroundColor(.secondary)
                    }
                }
            }
            .frame(height: 110)

            // Table
            VStack(spacing: 0) {
                HStack {
                    Text("Month").frame(width: 40, alignment: .leading)
                    Text("Titles").frame(width: 60, alignment: .trailing)
                    Text("Low").frame(width: 72, alignment: .trailing)
                    Text("Mid ↑").frame(width: 72, alignment: .trailing)
                    Text("High").frame(width: 72, alignment: .trailing)
                }
                .font(.caption.bold())
                .foregroundColor(.secondary)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                Divider()
                ForEach(f.monthly) { m in
                    HStack {
                        Text(m.month).frame(width: 40, alignment: .leading)
                        Text("\(m.titlesPublished.formatted())").frame(width: 60, alignment: .trailing).foregroundColor(.secondary)
                        Text("$\(Int(m.revenueLow).formatted())").frame(width: 72, alignment: .trailing).foregroundColor(.orange)
                        Text("$\(Int(m.revenueMid).formatted())").frame(width: 72, alignment: .trailing).foregroundColor(.green).fontWeight(.semibold)
                        Text("$\(Int(m.revenueHigh).formatted())").frame(width: 72, alignment: .trailing).foregroundColor(.blue)
                    }
                    .font(.caption.monospacedDigit())
                    .padding(.horizontal, 8)
                    .padding(.vertical, 3)
                    if m.monthNum < 12 { Divider().opacity(0.4) }
                }
            }
            .background(Color.white.opacity(0.45))
            .cornerRadius(6)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    // MARK: - By Lane

    private func laneCard(_ f: RevenueForecast) -> some View {
        MetricCard(title: "Revenue by Market (Lane)", icon: "globe", accentColor: .teal) {
            let sorted = f.byLane.sorted { $0.value.revenueMid > $1.value.revenueMid }
            let maxRev = sorted.first?.value.revenueMid ?? 1
            VStack(spacing: 5) {
                ForEach(sorted, id: \.key) { lane, data in
                    HStack(spacing: 8) {
                        Text(lane.replacingOccurrences(of: "_", with: " "))
                            .font(.caption)
                            .frame(width: 120, alignment: .leading)
                        GeometryReader { geo in
                            RoundedRectangle(cornerRadius: 3)
                                .fill(Color.teal.opacity(0.5))
                                .frame(width: max(4, CGFloat(data.revenueMid / maxRev) * geo.size.width))
                        }
                        .frame(height: 14)
                        Text("$\(Int(data.revenueMid).formatted())")
                            .font(.caption.monospacedDigit())
                            .frame(width: 64, alignment: .trailing)
                        Text("\(String(format: "%.2f", data.marketMultiplier))×")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                            .frame(width: 36, alignment: .trailing)
                    }
                }
            }
        }
    }

    // MARK: - By Format

    private func formatCard(_ f: RevenueForecast) -> some View {
        MetricCard(title: "Revenue by Format", icon: "doc.on.doc", accentColor: .indigo) {
            let sorted = f.byFormat.sorted { $0.value.revenuePct > $1.value.revenuePct }
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 190))], spacing: 8) {
                ForEach(sorted, id: \.key) { fmt, data in
                    HStack(spacing: 8) {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(fmt.replacingOccurrences(of: "_", with: " ").capitalized)
                                .font(.caption.bold())
                            Text("\(data.count.formatted()) titles")
                                .font(.caption2).foregroundColor(.secondary)
                        }
                        Spacer()
                        VStack(alignment: .trailing, spacing: 2) {
                            Text(String(format: "%.1f%%", data.revenuePct * 100))
                                .font(.caption.bold()).foregroundColor(.indigo)
                            Text("\(String(format: "%.2f", data.revenueWeight))× weight")
                                .font(.caption2).foregroundColor(.secondary)
                        }
                    }
                    .padding(8)
                    .background(Color.indigo.opacity(0.07))
                    .cornerRadius(6)
                }
            }
        }
    }

    // MARK: - Provenance

    private func provenanceCard(_ f: RevenueForecast) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Label("Data provenance", systemImage: "info.circle")
                .font(.caption.bold()).foregroundColor(.secondary)
            Text(f.provenance).font(.caption).foregroundColor(.secondary)
            Text("Generated: \(f.generatedAt)").font(.caption2).foregroundColor(.secondary)
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.secondary.opacity(0.08))
        .cornerRadius(6)
    }

    // MARK: - Empty state

    private var emptyStateCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("No forecast for \(selectedYear)", systemImage: "exclamationmark.triangle")
                .font(.headline).foregroundColor(.orange)
            Text("artifacts/projections/revenue_forecast_\(selectedYear).json not found.")
                .foregroundColor(.secondary)
            Text("Step 1 — Run Planner (all brands) to generate per-brand 52-week plans.\nStep 2 — Click Generate Forecast to compute revenue projections from those plans.")
                .font(.caption).foregroundColor(.secondary)
            if planCount > 0 {
                Text("\(planCount) brand plan(s) already exist. You can jump straight to Generate Forecast.")
                    .font(.caption).foregroundColor(.green)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.orange.opacity(0.08))
        .cornerRadius(8)
    }

    // MARK: - Log

    private var logCard: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Label("Script output", systemImage: "terminal")
                    .font(.caption.bold()).foregroundColor(.secondary)
                Spacer()
                if isBusy { ProgressView().scaleEffect(0.6) }
                if let code = lastRunExitCode {
                    Text("exit \(code)")
                        .font(.caption2.monospacedDigit())
                        .foregroundColor(code == 0 ? .green : .red)
                }
            }
            ScrollView {
                Text(logText)
                    .font(.system(size: 11, design: .monospaced))
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            .frame(height: 140)
            .background(Color.black.opacity(0.04))
            .cornerRadius(4)
        }
        .padding()
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }

    // MARK: - Data

    private func refresh() {
        guard !state.repoPath.isEmpty else { return }
        forecast = artifactReader.loadRevenueForecast(repoPath: state.repoPath, year: selectedYear)
        planCount = artifactReader.projectionPlanCount(repoPath: state.repoPath, year: selectedYear)
    }

    private func runProjectionPlanner() {
        guard !state.repoPath.isEmpty else { return }
        isRunningPlanner = true
        logText = ""
        lastRunExitCode = nil
        Task {
            do {
                let code = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: "scripts/catalog/projection_planner.py",
                    arguments: ["--all-brands", "--year", "\(selectedYear)"],
                    timeoutSeconds: 300,
                    onOutput: { line in
                        Task { @MainActor in logText += line + "\n" }
                    }
                )
                await MainActor.run {
                    lastRunExitCode = code
                    isRunningPlanner = false
                    refresh()
                }
            } catch {
                await MainActor.run {
                    logText += "\nError: \(error)"
                    isRunningPlanner = false
                }
            }
        }
    }

    private func runRevenueProjector() {
        guard !state.repoPath.isEmpty else { return }
        isRunningProjector = true
        logText = ""
        lastRunExitCode = nil
        Task {
            do {
                let code = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: "scripts/catalog/revenue_projector.py",
                    arguments: ["--year", "\(selectedYear)", "--format", "both"],
                    timeoutSeconds: 180,
                    onOutput: { line in
                        Task { @MainActor in logText += line + "\n" }
                    }
                )
                await MainActor.run {
                    lastRunExitCode = code
                    isRunningProjector = false
                    refresh()
                }
            } catch {
                await MainActor.run {
                    logText += "\nError: \(error)"
                    isRunningProjector = false
                }
            }
        }
    }
}
