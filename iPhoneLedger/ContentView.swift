import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var store: LedgerStore
    @State private var showingAddSheet = false

    private var monthTitle: String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "zh_CN")
        formatter.dateFormat = "yyyy年M月"
        return formatter.string(from: Date())
    }

    private var currencyFormatter: NumberFormatter {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.currencyCode = "CNY"
        formatter.maximumFractionDigits = 2
        return formatter
    }

    var body: some View {
        NavigationStack {
            List {
                Section("\(monthTitle) 汇总") {
                    SummaryRow(title: "收入", value: store.monthlyIncome(), color: .green, formatter: currencyFormatter)
                    SummaryRow(title: "支出", value: store.monthlyExpense(), color: .red, formatter: currencyFormatter)
                    SummaryRow(title: "结余", value: store.monthlyBalance(), color: .blue, formatter: currencyFormatter)
                }

                Section("支出分类") {
                    CategorySummaryView(expenses: store.expenseByCategory(), formatter: currencyFormatter)
                }

                Section("最新记录") {
                    if store.transactions.isEmpty {
                        Text("暂无记录，点击右上角 + 添加一笔")
                            .foregroundStyle(.secondary)
                    } else {
                        ForEach(store.transactions) { transaction in
                            TransactionRow(transaction: transaction, formatter: currencyFormatter)
                        }
                        .onDelete(perform: store.remove)
                    }
                }
            }
            .navigationTitle("记账本")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        showingAddSheet = true
                    } label: {
                        Image(systemName: "plus.circle.fill")
                    }
                    .accessibilityLabel("添加记录")
                }
            }
            .sheet(isPresented: $showingAddSheet) {
                AddTransactionView()
                    .environmentObject(store)
            }
        }
    }
}

private struct SummaryRow: View {
    let title: String
    let value: Double
    let color: Color
    let formatter: NumberFormatter

    var body: some View {
        HStack {
            Text(title)
            Spacer()
            Text(formatter.string(from: NSNumber(value: value)) ?? "¥0")
                .foregroundStyle(color)
                .fontWeight(.semibold)
        }
    }
}

private struct TransactionRow: View {
    let transaction: Transaction
    let formatter: NumberFormatter

    var body: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(transaction.type == .income ? Color.green.opacity(0.2) : Color.red.opacity(0.2))
                .frame(width: 36, height: 36)
                .overlay {
                    Image(systemName: transaction.type == .income ? "arrow.down.left" : "arrow.up.right")
                        .foregroundStyle(transaction.type == .income ? .green : .red)
                }

            VStack(alignment: .leading, spacing: 4) {
                Text(transaction.category.rawValue)
                    .font(.headline)
                if !transaction.note.isEmpty {
                    Text(transaction.note)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                Text(transaction.date, style: .date)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            Text(formattedAmount)
                .fontWeight(.bold)
                .foregroundStyle(transaction.type == .income ? .green : .red)
        }
        .padding(.vertical, 2)
    }

    private var formattedAmount: String {
        let sign = transaction.type == .income ? "+" : "-"
        let amount = formatter.string(from: NSNumber(value: transaction.amount)) ?? "¥0"
        return "\(sign)\(amount)"
    }
}
