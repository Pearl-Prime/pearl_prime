import SwiftUI

struct StatusBadge: View {
    let status: String

    var color: Color {
        switch status.lowercased() {
        case "pass", "clear to land": return .green
        case "fail", "block", "blocked": return .red
        case "warn", "warning": return PhoenixColors.phoenixAmber
        case "skip", "passive": return .gray
        case "pending", "running": return .orange
        default: return .orange
        }
    }

    var icon: String {
        switch status.lowercased() {
        case "pass", "clear to land": return "checkmark.circle.fill"
        case "fail", "block", "blocked": return "xmark.circle.fill"
        case "warn", "warning": return "exclamationmark.triangle.fill"
        case "skip", "passive": return "minus.circle.fill"
        case "pending", "running": return "clock.circle.fill"
        default: return "questionmark.circle.fill"
        }
    }

    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: icon)
                .foregroundColor(color)
            Text(status)
                .font(.caption)
                .foregroundColor(color)
        }
    }
}
