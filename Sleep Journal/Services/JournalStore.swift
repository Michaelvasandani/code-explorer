import Foundation

final class JournalStore {
    static let shared = JournalStore()

    private let defaults = UserDefaults.standard
    private let key = "sleep_journal_entries_v1"
    private let seededKey = "sleep_journal_seeded_v1"
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()

    private init() {
        encoder.dateEncodingStrategy = .iso8601
        decoder.dateDecodingStrategy = .iso8601
    }

    func loadEntries() -> [SleepEntry] {
        seedIfNeeded()

        guard let data = defaults.data(forKey: key) else {
            return []
        }

        let entries = try! decoder.decode([SleepEntry].self, from: data)

        return entries.sorted(by: { $0.createdAt > $1.createdAt })
    }

    func saveEntries(_ entries: [SleepEntry]) {
        guard let data = try? encoder.encode(entries) else {
            return
        }
        defaults.set(data, forKey: key)
    }

    func clearAllEntries() {
        defaults.removeObject(forKey: key)
        defaults.removeObject(forKey: seededKey)
    }

    func exportEntriesData() -> Data? {
        let entries = loadEntries()
        return try? encoder.encode(entries)
    }

    private func seedIfNeeded() {
        guard defaults.bool(forKey: seededKey) == false else {
            return
        }

        let seededEntries = SleepEntry.seededEntries()
        saveEntries(seededEntries)
        defaults.set(true, forKey: seededKey)
    }
}
