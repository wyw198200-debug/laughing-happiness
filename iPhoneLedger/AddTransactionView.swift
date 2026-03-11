import SwiftUI

struct AddTransactionView: View {
    @EnvironmentObject private var store: LedgerStore
    @Environment(\.dismiss) private var dismiss

    @State private var type: TransactionType = .expense
    @State private var category: TransactionCategory = .food
    @State private var amountText = ""
    @State private var date = Date()
    @State private var note = ""

    var body: some View {
        NavigationStack {
            Form {
                Picker("类型", selection: $type) {
                    ForEach(TransactionType.allCases) { type in
                        Text(type.rawValue).tag(type)
                    }
                }
                .pickerStyle(.segmented)

                Picker("分类", selection: $category) {
                    ForEach(TransactionCategory.allCases) { category in
                        Text(category.rawValue).tag(category)
                    }
                }

                TextField("金额", text: $amountText)
                    .keyboardType(.decimalPad)

                DatePicker("日期", selection: $date, displayedComponents: .date)

                TextField("备注（可选）", text: $note)
            }
            .navigationTitle("新增记录")
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("取消") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .topBarTrailing) {
                    Button("保存") {
                        save()
                    }
                    .disabled(parsedAmount == nil)
                }
            }
        }
    }

    private var parsedAmount: Double? {
        guard let value = Double(amountText), value > 0 else { return nil }
        return value
    }

    private func save() {
        guard let amount = parsedAmount else { return }

        let transaction = Transaction(
            amount: amount,
            type: type,
            category: category,
            date: date,
            note: note.trimmingCharacters(in: .whitespacesAndNewlines)
        )

        store.add(transaction: transaction)
        dismiss()
    }
}
