import Foundation

struct SleepEntry: Codable, Identifiable, Equatable {
    let id: UUID
    let createdAt: Date
    var sleepHours: Double
    var sleepQuality: SleepQuality
    var mood: DailyMood
    var tags: [SleepTag]
    var notes: String
    var weather: WeatherSnapshot?

    var searchBlob: String {
        let tagsText = tags.map(\.label).joined(separator: " ")
        return "\(sleepQuality.label) \(mood.label) \(tagsText) \(notes)".lowercased()
    }
}

enum SleepQuality: String, Codable, CaseIterable, Identifiable {
    case awful
    case poor
    case okay
    case great

    var id: String { rawValue }

    var emoji: String {
        switch self {
        case .awful:
            return "😵‍💫"
        case .poor:
            return "😴"
        case .okay:
            return "🙂"
        case .great:
            return "🤩"
        }
    }

    var label: String {
        switch self {
        case .awful:
            return "\(emoji) Awful"
        case .poor:
            return "\(emoji) Poor"
        case .okay:
            return "\(emoji) Okay"
        case .great:
            return "\(emoji) Great"
        }
    }
}

enum DailyMood: String, Codable, CaseIterable, Identifiable {
    case exhausted
    case groggy
    case neutral
    case energized

    var id: String { rawValue }

    var emoji: String {
        switch self {
        case .exhausted:
            return "🥱"
        case .groggy:
            return "😕"
        case .neutral:
            return "😐"
        case .energized:
            return "⚡️"
        }
    }

    var label: String {
        switch self {
        case .exhausted:
            return "\(emoji) Exhausted"
        case .groggy:
            return "\(emoji) Groggy"
        case .neutral:
            return "\(emoji) Neutral"
        case .energized:
            return "\(emoji) Energized"
        }
    }
}

enum SleepTag: String, Codable, CaseIterable, Identifiable, Hashable {
    case stress
    case exercise
    case caffeine
    case screenTime

    var id: String { rawValue }

    var label: String {
        switch self {
        case .stress:
            return "Stress"
        case .exercise:
            return "Exercise"
        case .caffeine:
            return "Late Caffeine"
        case .screenTime:
            return "Screen Time"
        }
    }

    var emoji: String {
        switch self {
        case .stress:
            return "😬"
        case .exercise:
            return "🏃"
        case .caffeine:
            return "☕️"
        case .screenTime:
            return "📱"
        }
    }
}

struct WeatherSnapshot: Codable, Equatable {
    var summary: String
    var temperatureF: Int?
    var wind: String?
    var fetchedAt: Date
}

extension SleepEntry {
    static func seededEntries(referenceDate: Date = Date()) -> [SleepEntry] {
        let calendar = Calendar.current
        let entries: [(Int, Double, SleepQuality, DailyMood, [SleepTag], String, WeatherSnapshot?)] = [
            (0, 6.0, .poor, .groggy, [.caffeine, .screenTime], "Stayed up doom scrolling and had espresso at 9pm.", WeatherSnapshot(summary: "Clear", temperatureF: 42, wind: "8 mph NW", fetchedAt: referenceDate)),
            (1, 7.5, .okay, .neutral, [.exercise], "Evening walk helped. Still woke up once around 3am.", WeatherSnapshot(summary: "Mostly Cloudy", temperatureF: 38, wind: "5 mph W", fetchedAt: referenceDate)),
            (2, 4.5, .awful, .exhausted, [.stress], "Big deadline tomorrow. Racing thoughts all night.", nil),
            (3, 8.0, .great, .energized, [.exercise], "No screens after 9pm. Best sleep this week.", WeatherSnapshot(summary: "Sunny", temperatureF: 56, wind: "6 mph S", fetchedAt: referenceDate)),
            (4, 5.5, .poor, .groggy, [.stress, .caffeine], "Late meeting and coffee too late in the day.", WeatherSnapshot(summary: "Rain", temperatureF: 47, wind: "12 mph SW", fetchedAt: referenceDate)),
            (5, 7.0, .okay, .neutral, [], "Fell asleep quickly but woke up feeling average.", nil),
            (6, 8.5, .great, .energized, [.exercise], "Strength training day. Slept deeply.", WeatherSnapshot(summary: "Partly Cloudy", temperatureF: 50, wind: "4 mph NE", fetchedAt: referenceDate)),
        ]

        return entries.compactMap { dayOffset, hours, quality, mood, tags, notes, weather in
            guard let createdAt = calendar.date(byAdding: .day, value: -dayOffset, to: referenceDate) else {
                return nil
            }
            return SleepEntry(
                id: UUID(),
                createdAt: createdAt,
                sleepHours: hours,
                sleepQuality: quality,
                mood: mood,
                tags: tags,
                notes: notes,
                weather: weather
            )
        }
    }
}
