import SwiftUI

struct PipelineView: View {
    @ObservedObject var state: AppState
    let scriptRunner: ScriptRunner
    @State private var topic: String = "anxiety"
    @State private var persona: String = "gen_alpha_students"
    @State private var teacher: String = ""
    @State private var arc: String = ""
    @State private var seed: String = ""
    @State private var logOutput: String = ""
    @State private var isRunning: Bool = false

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            // Row 1: topic + persona
            HStack(spacing: 8) {
                Text("Topic").frame(width: 50, alignment: .trailing)
                TextField("e.g. grief", text: $topic)
                    .frame(width: 140)
                Text("Persona").frame(width: 54, alignment: .trailing)
                TextField("e.g. gen_z_professionals", text: $persona)
                    .frame(width: 180)
            }
            // Row 2: teacher + arc
            HStack(spacing: 8) {
                Text("Teacher").frame(width: 50, alignment: .trailing)
                TextField("e.g. master_wu (optional)", text: $teacher)
                    .frame(width: 160)
                Text("Arc").frame(width: 28, alignment: .trailing)
                TextField("path/to/arc.yaml (required)", text: $arc)
                    .frame(width: 220)
            }
            // Row 3: seed
            HStack(spacing: 8) {
                Text("Seed").frame(width: 50, alignment: .trailing)
                TextField("determinism seed (optional)", text: $seed)
                    .frame(width: 200)
            }
            // Buttons
            HStack(spacing: 10) {
                Button("▶ Run pipeline") {
                    runPipeline()
                }
                .keyboardShortcut(.return, modifiers: .command)
                .disabled(state.repoPath.isEmpty || topic.trimmingCharacters(in: .whitespaces).isEmpty || arc.trimmingCharacters(in: .whitespaces).isEmpty || isRunning)

                if isRunning {
                    Button("■ Cancel") { scriptRunner.cancel() }
                }

                Spacer()

                if !teacher.trimmingCharacters(in: .whitespaces).isEmpty {
                    Label("Teacher mode", systemImage: "person.fill.checkmark")
                        .font(.caption)
                        .foregroundColor(.orange)
                }
            }
            LiveLogView(logText: $logOutput, isRunning: isRunning)
        }
        .padding()
        .background(PhoenixColors.phoenixBackground)
    }

    private func runPipeline() {
        guard !state.repoPath.isEmpty else { return }
        logOutput = ""
        isRunning = true

        var args = ["--topic", topic.trimmingCharacters(in: .whitespaces),
                    "--persona", persona.trimmingCharacters(in: .whitespaces),
                    "--render-book"]

        let t = teacher.trimmingCharacters(in: .whitespaces)
        if !t.isEmpty {
            args += ["--teacher", t]
        }

        args += ["--arc", arc.trimmingCharacters(in: .whitespaces)]

        let s = seed.trimmingCharacters(in: .whitespaces)
        if !s.isEmpty {
            args += ["--seed", s]
        }

        Task {
            do {
                _ = try await scriptRunner.run(
                    repoPath: state.repoPath,
                    scriptPath: "scripts/run_pipeline.py",
                    arguments: args,
                    timeoutSeconds: 600,
                    onOutput: { logOutput += $0 + "\n" }
                )
                await MainActor.run { isRunning = false }
            } catch {
                await MainActor.run {
                    logOutput += "\nError: \(error)"
                    isRunning = false
                }
            }
        }
    }
}
