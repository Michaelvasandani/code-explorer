import UIKit

final class SleepEntryDetailViewController: UIViewController {
    private let entry: SleepEntry
    private let dateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .full
        formatter.timeStyle = .short
        return formatter
    }()

    init(entry: SleepEntry) {
        self.entry = entry
        super.init(nibName: nil, bundle: nil)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        title = "Sleep Details"

        let stack = UIStackView()
        stack.axis = .vertical
        stack.spacing = 12
        stack.translatesAutoresizingMaskIntoConstraints = false

        stack.addArrangedSubview(makeLabel(text: "Date: \(dateFormatter.string(from: entry.createdAt))", style: .body))
        stack.addArrangedSubview(makeLabel(text: "Sleep: \(entry.sleepQuality.label)", style: .title3))
        stack.addArrangedSubview(makeLabel(text: "Mood: \(entry.mood.label)", style: .title3))
        stack.addArrangedSubview(makeLabel(text: "Hours: \(entry.sleepHours.formatted())", style: .title3))
        let tagsText = entry.tags.isEmpty ? "No tags" : entry.tags.map { "\($0.emoji) \($0.label)" }.joined(separator: ", ")
        stack.addArrangedSubview(makeLabel(text: "Tags: \(tagsText)", style: .body))

        if let weather = entry.weather {
            stack.addArrangedSubview(makeLabel(text: "Weather: \(weather.summary)", style: .headline))
            stack.addArrangedSubview(makeLabel(text: "Temperature: \(weather.temperatureF.map { "\($0)°F" } ?? "Unknown")", style: .body))
            stack.addArrangedSubview(makeLabel(text: "Wind: \(weather.wind ?? "Unknown")", style: .body))
        } else {
            stack.addArrangedSubview(makeLabel(text: "Weather: Not captured", style: .headline))
        }

        if !entry.notes.isEmpty {
            stack.addArrangedSubview(makeLabel(text: "Notes: \(entry.notes)", style: .body))
        }

        view.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
            stack.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            stack.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
        ])
    }

    private func makeLabel(text: String, style: UIFont.TextStyle) -> UILabel {
        let label = UILabel()
        label.numberOfLines = 0
        label.font = .preferredFont(forTextStyle: style)
        label.text = text
        return label
    }
}
