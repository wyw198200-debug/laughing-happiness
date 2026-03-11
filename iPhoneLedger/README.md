# iPhoneLedger（iPhone 14 Pro 记账软件）

这是一个基于 **SwiftUI + UserDefaults 持久化** 的轻量记账应用，适用于 iPhone 14 Pro（iOS 16+）。

## 功能
- 记录收入/支出（金额、分类、时间、备注）
- 按月汇总：总收入、总支出、结余
- 支出分类占比
- 本地离线保存（无需网络）
- 删除记账记录

## 使用方式
1. 用 Xcode 新建 `App` 项目（iOS, SwiftUI）。
2. 将本目录下 `.swift` 文件加入项目，替换同名文件。
3. 运行目标设备选择 iPhone 14 Pro 模拟器或真机。

## 目录
- `iPhoneLedgerApp.swift`：应用入口
- `Transaction.swift`：数据模型
- `LedgerStore.swift`：数据存储与统计
- `ContentView.swift`：主界面（汇总 + 列表）
- `AddTransactionView.swift`：新增记账页面
- `CategorySummaryView.swift`：分类统计视图
