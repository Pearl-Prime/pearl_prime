import SwiftUI

struct PearlPrimeWebView: View {
    private let baseURL = "https://phoenix-command.pages.dev"

    private let pages: [(String, String, String, String)] = [
        ("Pearl Prime Entry", "Choose Your Market — 13 lanes", "flag.fill", "/pearl_prime_entry.html"),
        ("Teacher Selection", "Choose Your Teacher — 13 teachers + Composite", "person.crop.circle", "/teacher_select.html"),
        ("Teacher Showcase", "Full teacher profiles with inline book reader", "person.3", "/teacher_showcase.html"),
        ("Presenter", "Unified deck player — intro, marketing, briefings", "play.rectangle", "/presenter.html"),
        ("Marketing Dashboard", "Ad spend simulator, content heatmap, fleet budget", "chart.bar", "/marketing_dashboard.html"),
        ("Marketing Intelligence", "14-section presenter with TTS narration", "megaphone", "/marketing_intelligence_presenter.html"),
        ("Market Lane Matrix", "Platform availability per market", "tablecells", "/market_lane_matrix.html"),
        ("Output Gallery", "Pipeline examples — books, audio, video, manga", "photo.on.rectangle.angled", "/lane_examples_gallery.html"),
        ("Weekly OS", "Mon–Sun rhythm — what to upload, when, where", "calendar", "/brand_admin_weekly_os.html"),
        ("Brand Admin Onboarding", "Master onboarding flow for brand admins", "person.badge.plus", "/brand_admin_master_onboarding.html"),
    ]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Pearl Prime Web")
                    .font(.largeTitle)
                    .foregroundColor(PhoenixColors.phoenixAmber)

                Text("Your investor-facing and brand-admin web portal. Share this URL with brand operators — they pick a market, choose a teacher, and see the full pipeline in action. No login needed.")
                    .font(.callout)
                    .foregroundColor(.secondary)
                    .fixedSize(horizontal: false, vertical: true)

                Text(baseURL)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .textSelection(.enabled)

                HStack(spacing: 12) {
                    Button("Open Site") {
                        if let url = URL(string: baseURL) {
                            NSWorkspace.shared.open(url)
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(PhoenixColors.phoenixAmber)

                    Button("Copy URL") {
                        NSPasteboard.general.clearContents()
                        NSPasteboard.general.setString(baseURL, forType: .string)
                    }
                    .buttonStyle(.bordered)
                }

                Divider()

                Text("Pages")
                    .font(.headline)
                    .foregroundColor(PhoenixColors.phoenixBlue)

                LazyVGrid(columns: [GridItem(.adaptive(minimum: 280), spacing: 12)], spacing: 12) {
                    ForEach(pages, id: \.0) { page in
                        pageCard(title: page.0, description: page.1, icon: page.2, path: page.3)
                    }
                }
            }
            .padding()
        }
        .background(PhoenixColors.phoenixBackground)
    }

    private func pageCard(title: String, description: String, icon: String, path: String) -> some View {
        Button {
            if let url = URL(string: baseURL + path) {
                NSWorkspace.shared.open(url)
            }
        } label: {
            HStack(spacing: 12) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(PhoenixColors.phoenixAmber)
                    .frame(width: 32)
                VStack(alignment: .leading, spacing: 2) {
                    Text(title)
                        .font(.system(.body, weight: .medium))
                        .foregroundColor(.primary)
                    Text(description)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(2)
                }
                Spacer()
                Image(systemName: "arrow.up.right.square")
                    .foregroundColor(.secondary)
            }
            .padding(12)
            .background(Color(.controlBackgroundColor).opacity(0.5))
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(Color.gray.opacity(0.2), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }
}
