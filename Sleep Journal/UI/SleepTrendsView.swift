import Charts
import SwiftUI

struct SleepTrendsView: View {
    @State private var entries: [SleepEntry] = []

    var body: some View {
        List {
            Section("7-Day Sleep Hours") {
                Chart(dayBuckets) { bucket in
                    BarMark(
                        x: .value("Day", bucket.day, unit: .day),
                        y: .value("Hours", bucket.hours)
                    )
                    .foregroundStyle(.indigo.gradient)
                }
                .frame(height: 220)
            }

            Section("Mood Snapshot") {
                ForEach(DailyMood.allCases) { mood in
                    let count = entries.filter { $0.mood == mood }.count
                    HStack {
                        Text(mood.label)
                        Spacer()
                        Text("\(count)")
                            .foregroundStyle(.secondary)
                    }
                }
            }

            Section("Recent Notes") {
                ForEach(entries.prefix(5)) { entry in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(entry.notes.isEmpty ? "No notes" : entry.notes)
                            .font(.body)
                        Text(entry.createdAt.formatted(date: .abbreviated, time: .omitted))
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }
        }
        .navigationTitle("Trends")
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button("Reload") {
                    loadEntries()
                }
            }
        }
        .onAppear {
            loadEntries()
        }
    }

    private var dayBuckets: [SleepDayBucket] {
        let calendar = Calendar.current
        let grouped = Dictionary(grouping: entries) { calendar.startOfDay(for: $0.createdAt) }
        return grouped
            .map { day, dayEntries in
                let total = dayEntries.map(\.sleepHours).reduce(0, +)
                let average = total / Double(max(dayEntries.count, 1))
                return SleepDayBucket(day: day, hours: average)
            }
            .sorted(by: { $0.day < $1.day })
            .suffix(7)
            .map { $0 }
    }

    private func loadEntries() {
        entries = JournalStore.shared.loadEntries()
    }
}

private struct SleepDayBucket: Identifiable {
    let id = UUID()
    let day: Date
    let hours: Double
}
