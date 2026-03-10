import SwiftUI
import UIKit

final class SleepJournalListViewController: UITableViewController {
    private let viewModel = SleepListViewModel()
    private var filterButtons: [SleepTag: UIButton] = [:]
    private let dateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter
    }()

    private lazy var searchController: UISearchController = {
        let controller = UISearchController(searchResultsController: nil)
        controller.obscuresBackgroundDuringPresentation = false
        controller.searchResultsUpdater = self
        controller.searchBar.delegate = self
        controller.searchBar.placeholder = "Search notes or vibe"
        return controller
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Journal Timeline"
        navigationItem.largeTitleDisplayMode = .always
        navigationItem.searchController = searchController
        navigationItem.leftBarButtonItem = UIBarButtonItem(
            title: "Trends",
            style: .plain,
            target: self,
            action: #selector(trendsTapped)
        )
        navigationItem.rightBarButtonItems = [
            UIBarButtonItem(
                image: UIImage(systemName: "gearshape"),
                style: .plain,
                target: self,
                action: #selector(settingsTapped)
            ),
            UIBarButtonItem(
            barButtonSystemItem: .add,
            target: self,
            action: #selector(addEntryTapped)
            ),
        ]
        navigationItem.backButtonTitle = "Back"
        tableView.tableHeaderView = makeFilterHeaderView()
        tableView.sectionHeaderTopPadding = 4

        definesPresentationContext = true

        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "EntryCell")
        tableView.rowHeight = UITableView.automaticDimension
        tableView.estimatedRowHeight = 72

        refreshControl = UIRefreshControl()
        refreshControl?.addTarget(self, action: #selector(refreshPulled), for: .valueChanged)

        viewModel.loadEntries()
    }

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        guard let header = tableView.tableHeaderView else {
            return
        }

        let targetSize = CGSize(width: tableView.bounds.width, height: UIView.layoutFittingCompressedSize.height)
        let newHeight = header.systemLayoutSizeFitting(
            targetSize,
            withHorizontalFittingPriority: .required,
            verticalFittingPriority: .fittingSizeLevel
        )
        if abs(header.frame.height - newHeight.height) > 0.5 {
            header.frame.size.height = newHeight.height
            tableView.tableHeaderView = header
        }
    }

    override func numberOfSections(in tableView: UITableView) -> Int {
        viewModel.numberOfSections()
    }

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        viewModel.numberOfRows(in: section)
    }

    override func tableView(_ tableView: UITableView, titleForHeaderInSection section: Int) -> String? {
        viewModel.titleForSection(section)
    }

    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "EntryCell", for: indexPath)
        guard let entry = viewModel.entry(at: indexPath) else {
            return cell
        }

        var config = UIListContentConfiguration.subtitleCell()
        let tagsText = entry.tags.isEmpty ? "No tags" : entry.tags.map { "\($0.emoji)" }.joined(separator: " ")
        config.text = "\(entry.sleepQuality.emoji) \(entry.mood.emoji) \(entry.sleepHours.formatted())h • \(tagsText)"

        let dateText = dateFormatter.string(from: entry.createdAt)
        if let weather = entry.weather {
            config.secondaryText = "\(dateText) • \(weather.summary) \(weather.temperatureF.map { "\($0)°F" } ?? "")"
        } else {
            config.secondaryText = "\(dateText) • No weather attached"
        }
        config.secondaryTextProperties.color = .secondaryLabel
        cell.contentConfiguration = config
        cell.accessoryType = .disclosureIndicator
        return cell
    }

    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        guard let entry = viewModel.entry(at: indexPath) else {
            return
        }
        navigationController!.pushViewController(SleepEntryDetailViewController(entry: entry), animated: true)
    }

    override func tableView(_ tableView: UITableView, commit editingStyle: UITableViewCell.EditingStyle, forRowAt indexPath: IndexPath) {
        guard editingStyle == .delete else {
            return
        }
        viewModel.deleteEntry(at: indexPath)
        tableView.reloadData()
    }

    @objc private func addEntryTapped() {
        let formView = SleepEntryFormView { [weak self] entry in
            self?.viewModel.addEntry(entry)
            self?.tableView.reloadData()
        }
        let hostingController = UIHostingController(rootView: formView)
        let navigationController = UINavigationController(rootViewController: hostingController)
        present(navigationController, animated: true)
    }

    @objc private func settingsTapped() {
        navigationController!.pushViewController(SleepSettingsViewController(), animated: true)
    }

    @objc private func trendsTapped() {
        let trendsView = SleepTrendsView()
        navigationController!.pushViewController(UIHostingController(rootView: trendsView), animated: true)
    }

    @objc private func refreshPulled() {
        viewModel.loadEntries()
        tableView.reloadData()
        refreshControl?.endRefreshing()
    }

    @objc private func tagButtonTapped(_ sender: UIButton) {
        guard let tag = SleepTag.allCases.first(where: { $0.rawValue == sender.accessibilityIdentifier }) else {
            return
        }
        sender.isSelected.toggle()
        applyTagButtonStyle(sender)
        viewModel.setTagEnabled(tag, enabled: sender.isSelected)
        tableView.reloadData()
    }

    private func makeFilterHeaderView() -> UIView {
        let container = UIView()
        container.backgroundColor = .clear

        let titleLabel = UILabel()
        titleLabel.text = "Filter by tags"
        titleLabel.font = .preferredFont(forTextStyle: .footnote)
        titleLabel.textColor = .secondaryLabel
        titleLabel.translatesAutoresizingMaskIntoConstraints = false

        let scrollView = UIScrollView()
        scrollView.showsHorizontalScrollIndicator = false
        scrollView.translatesAutoresizingMaskIntoConstraints = false

        let stack = UIStackView()
        stack.axis = .horizontal
        stack.spacing = 8
        stack.translatesAutoresizingMaskIntoConstraints = false

        for tag in SleepTag.allCases {
            let button = UIButton(type: .system)
            button.configuration = .bordered()
            button.setTitle("\(tag.emoji) \(tag.label)", for: .normal)
            button.accessibilityIdentifier = tag.rawValue
            button.addTarget(self, action: #selector(tagButtonTapped(_:)), for: .touchUpInside)
            filterButtons[tag] = button
            applyTagButtonStyle(button)
            stack.addArrangedSubview(button)
        }

        scrollView.addSubview(stack)
        container.addSubview(titleLabel)
        container.addSubview(scrollView)

        NSLayoutConstraint.activate([
            titleLabel.topAnchor.constraint(equalTo: container.topAnchor, constant: 8),
            titleLabel.leadingAnchor.constraint(equalTo: container.leadingAnchor, constant: 16),
            titleLabel.trailingAnchor.constraint(equalTo: container.trailingAnchor, constant: -16),

            scrollView.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 8),
            scrollView.leadingAnchor.constraint(equalTo: container.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: container.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: container.bottomAnchor, constant: -8),
            scrollView.heightAnchor.constraint(equalToConstant: 40),

            stack.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor),
            stack.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor),
            stack.leadingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.leadingAnchor, constant: 16),
            stack.trailingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.trailingAnchor, constant: -16),
            stack.heightAnchor.constraint(equalTo: scrollView.frameLayoutGuide.heightAnchor),
        ])

        return container
    }

    private func applyTagButtonStyle(_ button: UIButton) {
        var config = button.configuration ?? .bordered()
        config.baseBackgroundColor = button.isSelected ? .systemIndigo.withAlphaComponent(0.2) : .clear
        config.baseForegroundColor = button.isSelected ? .systemIndigo : .label
        button.configuration = config
    }
}

extension SleepJournalListViewController: UISearchResultsUpdating {
    func updateSearchResults(for searchController: UISearchController) {
        viewModel.searchText = searchController.searchBar.text ?? ""
        tableView.reloadData()
    }
}

extension SleepJournalListViewController: UISearchBarDelegate {
    func searchBarCancelButtonClicked(_ searchBar: UISearchBar) {}
}
