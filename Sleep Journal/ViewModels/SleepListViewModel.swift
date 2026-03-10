import Foundation
import UIKit

final class SleepListViewModel {
    struct EntrySection {
        let title: String
        let dayStart: Date
        var entries: [SleepEntry]
    }

    private let journalStore: JournalStore
    private let calendar = Calendar.current

    private(set) var allEntries: [SleepEntry] = []
    private(set) var filteredEntries: [SleepEntry] = []
    private(set) var sections: [EntrySection] = []
    private(set) var selectedTags: Set<SleepTag> = []
    var searchText: String = "" {
        didSet {
            applyFilters()
        }
    }

    init(journalStore: JournalStore = .shared) {
        self.journalStore = journalStore
    }

    func loadEntries() {
        allEntries = journalStore.loadEntries()
        applyFilters()
    }

    func addEntry(_ entry: SleepEntry) {
        allEntries.insert(entry, at: 0)
        journalStore.saveEntries(allEntries)
        applyFilters()
    }

    func deleteEntry(at indexPath: IndexPath) {
        guard let entry = entry(at: indexPath) else {
            return
        }
        allEntries.removeAll(where: { $0.id == entry.id })
        journalStore.saveEntries(allEntries)
        applyFilters()
    }

    func entry(at indexPath: IndexPath) -> SleepEntry? {
        guard indexPath.section >= 0, indexPath.section < sections.count else {
            return nil
        }
        let section = sections[indexPath.section]
        guard indexPath.row >= 0, indexPath.row < section.entries.count else {
            return nil
        }
        return section.entries[indexPath.row]
    }

    func numberOfSections() -> Int {
        sections.count
    }

    func numberOfRows(in section: Int) -> Int {
        guard section >= 0, section < sections.count else {
            return 0
        }
        return sections[section].entries.count
    }

    func titleForSection(_ section: Int) -> String? {
        guard section >= 0, section < sections.count else {
            return nil
        }
        return sections[section].title
    }

    func setTagEnabled(_ tag: SleepTag, enabled: Bool) {
        if enabled {
            selectedTags.insert(tag)
        } else {
            selectedTags.remove(tag)
        }
        applyFilters()
    }

    func trendEntries() -> [SleepEntry] {
        allEntries
    }

    private func applyFilters() {
        var result = allEntries

        if !searchText.isEmpty {
            result = result.filter { $0.searchBlob.contains(searchText) }
        }

        if !selectedTags.isEmpty {
            result = result.filter { !selectedTags.isDisjoint(with: Set($0.tags)) }
        }

        filteredEntries = result
        sections = groupedSections(from: filteredEntries)
    }

    private func groupedSections(from entries: [SleepEntry]) -> [EntrySection] {
        let groups = Dictionary(grouping: entries) { entry in
            calendar.startOfDay(for: entry.createdAt)
        }

        let formatter = DateFormatter()
        formatter.dateStyle = .full
        formatter.timeStyle = .none

        return groups
            .map { dayStart, dayEntries in
                EntrySection(
                    title: formatter.string(from: dayStart),
                    dayStart: dayStart,
                    entries: dayEntries.sorted(by: { $0.createdAt > $1.createdAt })
                )
            }
            .sorted(by: { $0.dayStart > $1.dayStart })
    }
}
