import SwiftUI

@main
struct PhoenixControlApp: App {
    @StateObject private var state = AppState()
    private let artifactReader = ArtifactReader()
    @StateObject private var scriptRunner = ScriptRunner()
    private let githubService = GitHubService()

    var body: some Scene {
        WindowGroup {
            ContentView(
                state: state,
                artifactReader: artifactReader,
                scriptRunner: scriptRunner,
                githubService: githubService
            )
            .frame(minWidth: 700, minHeight: 500)
        }
        .commands {
            CommandGroup(replacing: .newItem) {}
        }
    }
}
