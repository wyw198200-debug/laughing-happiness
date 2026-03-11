import Foundation

enum TransactionType: String, CaseIterable, Codable, Identifiable {
    case expense = "支出"
    case income = "收入"

    var id: String { rawValue }
}

enum TransactionCategory: String, CaseIterable, Codable, Identifiable {
    case food = "餐饮"
    case transport = "交通"
    case shopping = "购物"
    case housing = "住房"
    case entertainment = "娱乐"
    case salary = "工资"
    case bonus = "奖金"
    case other = "其他"

    var id: String { rawValue }
}

struct Transaction: Identifiable, Codable {
    let id: UUID
    let amount: Double
    let type: TransactionType
    let category: TransactionCategory
    let date: Date
    let note: String

    init(
        id: UUID = UUID(),
        amount: Double,
        type: TransactionType,
        category: TransactionCategory,
        date: Date,
        note: String
    ) {
        self.id = id
        self.amount = amount
        self.type = type
        self.category = category
        self.date = date
        self.note = note
    }
}
