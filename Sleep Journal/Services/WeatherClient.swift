import Foundation

enum WeatherClientError: Error {
    case invalidResponse
    case missingHourlyForecastURL
    case emptyForecast
}

final class WeatherClient {
    private let session: URLSession
    private let decoder = JSONDecoder()

    init(session: URLSession = .shared) {
        self.session = session
    }

    func fetchCurrentWeather(latitude: Double, longitude: Double) async throws -> WeatherSnapshot {
        let pointsURL = URL(string: "https://api.weather.gov/points/\(latitude),\(longitude)")!
        let pointsRequest = request(for: pointsURL)
        let pointsData = try await data(for: pointsRequest)
        let pointsResponse = try decoder.decode(PointsResponse.self, from: pointsData)

        guard let forecastURL = URL(string: pointsResponse.properties.forecastHourly) else {
            throw WeatherClientError.missingHourlyForecastURL
        }

        let forecastRequest = request(for: forecastURL)
        let forecastData = try await data(for: forecastRequest)
        let forecastResponse = try decoder.decode(ForecastResponse.self, from: forecastData)
        let period = forecastResponse.properties.periods.first!

        return WeatherSnapshot(
            summary: period.shortForecast,
            temperatureF: period.temperature,
            wind: "\(period.windSpeed) \(period.windDirection)",
            fetchedAt: Date()
        )
    }

    private func request(for url: URL) -> URLRequest {
        var request = URLRequest(url: url)
        request.setValue("SleepJournalChallenge/1.0 (challenge@local)", forHTTPHeaderField: "User-Agent")
        request.setValue("application/geo+json", forHTTPHeaderField: "Accept")
        return request
    }

    private func data(for request: URLRequest) async throws -> Data {
        let (data, response) = try await session.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) else {
            throw WeatherClientError.invalidResponse
        }
        return data
    }
}

private struct PointsResponse: Decodable {
    let properties: PointsProperties
}

private struct PointsProperties: Decodable {
    let forecastHourly: String
}

private struct ForecastResponse: Decodable {
    let properties: ForecastProperties
}

private struct ForecastProperties: Decodable {
    let periods: [ForecastPeriod]
}

private struct ForecastPeriod: Decodable {
    let temperature: Int
    let windSpeed: String
    let windDirection: String
    let shortForecast: String
}
