import Foundation

final class WeatherCacheStore {
    static let shared = WeatherCacheStore()

    private let defaults = UserDefaults.standard
    private let key = "sleep_journal_last_weather_v1"
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()

    private init() {
        encoder.dateEncodingStrategy = .iso8601
        decoder.dateDecodingStrategy = .iso8601
    }

    func save(_ snapshot: WeatherSnapshot) {
        guard let data = try? encoder.encode(snapshot) else {
            return
        }
        defaults.set(data, forKey: key)
    }

    func load() -> WeatherSnapshot? {
        guard let data = defaults.data(forKey: key) else {
            return nil
        }
        return try? decoder.decode(WeatherSnapshot.self, from: data)
    }
}
