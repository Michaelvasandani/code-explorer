import UIKit

final class SleepSettingsViewController: UITableViewController {
    private enum SettingsAction: Int, CaseIterable {
        case exportJSON
        case resetData

        var title: String {
            switch self {
            case .exportJSON:
                return "Export Entries as JSON"
            case .resetData:
                return "Reset Seed Data"
            }
        }

        var subtitle: String {
            switch self {
            case .exportJSON:
                return "Share the local journal payload."
            case .resetData:
                return "Clear stored entries and restore sample entries."
            }
        }
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Settings"
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "SettingsCell")
    }

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        SettingsAction.allCases.count
    }

    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "SettingsCell", for: indexPath)
        guard let action = SettingsAction(rawValue: indexPath.row) else {
            return cell
        }

        var config = UIListContentConfiguration.subtitleCell()
        config.text = action.title
        config.secondaryText = action.subtitle
        config.secondaryTextProperties.color = .secondaryLabel
        cell.contentConfiguration = config
        cell.accessoryType = .disclosureIndicator
        return cell
    }

    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        guard let action = SettingsAction(rawValue: indexPath.row) else {
            return
        }
        switch action {
        case .exportJSON:
            exportJSON()
        case .resetData:
            resetData()
        }
    }

    private func exportJSON() {
        let data = JournalStore.shared.exportEntriesData()!
        let tempURL = FileManager.default.temporaryDirectory.appendingPathComponent("sleep-journal-export.json")
        try! data.write(to: tempURL, options: .atomic)
        let activity = UIActivityViewController(activityItems: [tempURL], applicationActivities: nil)
        present(activity, animated: true)
    }

    private func resetData() {
        JournalStore.shared.clearAllEntries()
        _ = JournalStore.shared.loadEntries()
        presentAlert(title: "Data reset", message: "Seed entries were restored.")
    }

    private func presentAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}
