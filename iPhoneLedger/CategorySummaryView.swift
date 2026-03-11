import SwiftUI

struct CategorySummaryView: View {
    let expenses: [(TransactionCategory, Double)]
    let formatter: NumberFormatter

    var body: some View {
        if expenses.isEmpty {
            Text("本月暂无支出记录")
                .foregroundStyle(.secondary)
        } else {
            ForEach(expenses, id: \.0.id) { category, total in
                HStack {
                    Text(category.rawValue)
                    Spacer()
                    Text(formatter.string(from: NSNumber(value: total)) ?? "¥0")
                        .fontWeight(.medium)
                }
            }
        }
    }
}
