import Foundation

final class LedgerStore: ObservableObject {
    @Published private(set) var transactions: [Transaction] = [] {
        didSet { save() }
    }

    private let userDefaultsKey = "ledger.transactions"

    init() {
        load()
    }

    func add(transaction: Transaction) {
        transactions.insert(transaction, at: 0)
    }

    func remove(at offsets: IndexSet) {
        transactions.remove(atOffsets: offsets)
    }

    func monthlyTransactions(for month: Date = Date()) -> [Transaction] {
        let calendar = Calendar.current
        return transactions.filter { calendar.isDate($0.date, equalTo: month, toGranularity: .month) }
    }

    func monthlyIncome(for month: Date = Date()) -> Double {
        monthlyTransactions(for: month)
            .filter { $0.type == .income }
            .map(\.amount)
            .reduce(0, +)
    }

    func monthlyExpense(for month: Date = Date()) -> Double {
        monthlyTransactions(for: month)
            .filter { $0.type == .expense }
            .map(\.amount)
            .reduce(0, +)
    }

    func monthlyBalance(for month: Date = Date()) -> Double {
        monthlyIncome(for: month) - monthlyExpense(for: month)
    }

    func expenseByCategory(for month: Date = Date()) -> [(TransactionCategory, Double)] {
        let expenses = monthlyTransactions(for: month).filter { $0.type == .expense }
        let grouped = Dictionary(grouping: expenses, by: \.category)

        return grouped
            .map { (key: TransactionCategory, value: [Transaction]) in
                (key, value.map(\.amount).reduce(0, +))
            }
            .sorted { $0.1 > $1.1 }
    }

    private func save() {
        let encoder = JSONEncoder()
        guard let data = try? encoder.encode(transactions) else { return }
        UserDefaults.standard.set(data, forKey: userDefaultsKey)
    }

    private func load() {
        guard let data = UserDefaults.standard.data(forKey: userDefaultsKey) else { return }
        let decoder = JSONDecoder()
        guard let decoded = try? decoder.decode([Transaction].self, from: data) else { return }
        transactions = decoded
    }
}
