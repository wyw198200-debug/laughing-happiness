# 国际金融新闻日报推送到飞书

这个小工具会每天抓取国际金融市场相关的新闻（通过 Google News RSS），并自动推送到你的飞书群机器人。

## 功能

- 按关键词抓取国际金融市场新闻
- 支持限制推送条数
- 支持 `dry-run` 本地预览
- 支持 GitHub Actions 每日自动执行

## 1) 准备飞书机器人 Webhook

1. 在飞书群里添加「自定义机器人」。
2. 获取 Webhook 地址，例如：
   `https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx`

## 2) 本地运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export FEISHU_WEBHOOK_URL='https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx'
python src/daily_finance_news_to_feishu.py --limit 8
```

只预览不推送：

```bash
python src/daily_finance_news_to_feishu.py --dry-run
```

## 3) 参数说明

- `--query`：新闻检索关键词（默认：国际金融市场相关关键词）
- `--limit`：推送条数，默认 8
- `--webhook`：飞书机器人 webhook
- `--dry-run`：仅打印内容，不推送

## 4) 每天自动执行（GitHub Actions）

仓库内已提供 `.github/workflows/daily_feishu_news.yml`，默认每天 UTC 00:30 执行。

你只需要在 GitHub 仓库中设置 Secrets：

- `FEISHU_WEBHOOK_URL`（必填）
- `NEWS_QUERY`（可选）
- `NEWS_LIMIT`（可选）

也可以在 Actions 页面手动触发工作流。

## 5) 常见问题

- **推送报错 `code != 0`**：检查机器人权限、Webhook 是否过期。
- **新闻太少/不精准**：修改 `NEWS_QUERY` 或 `--query`。
- **网络报错**：重试，或在可访问 Google News RSS 的网络环境运行。
