import SwiftUI

struct MetricCard<Content: View>: View {
    let title: String
    let icon: String
    let accentColor: Color
    @ViewBuilder let content: () -> Content

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 8) {
                Image(systemName: icon)
                    .foregroundColor(accentColor)
                Text(title)
                    .font(.headline)
                    .foregroundColor(PhoenixColors.phoenixBlue)
            }
            content()
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PhoenixColors.phoenixCardTint)
        .cornerRadius(8)
    }
}
