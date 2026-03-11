#!/usr/bin/env python3
"""每天抓取国际金融市场新闻并推送到飞书群机器人。"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import os
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
DEFAULT_QUERY = "international financial markets OR global stocks OR forex OR bond yields"
DEFAULT_TIMEOUT = 15


@dataclass
class NewsItem:
    title: str
    link: str
    source: str
    published: str


def build_rss_url(query: str) -> str:
    return GOOGLE_NEWS_RSS.format(query=quote_plus(query))


def _get_text(node: ET.Element | None, tag: str) -> str:
    if node is None:
        return ""
    child = node.find(tag)
    return child.text.strip() if child is not None and child.text else ""


def fetch_news(query: str, limit: int = 8, timeout: int = DEFAULT_TIMEOUT) -> list[NewsItem]:
    rss_url = build_rss_url(query)
    request = Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=timeout) as resp:
        xml_data = resp.read()

    root = ET.fromstring(xml_data)
    items = root.findall("./channel/item")

    news_items: list[NewsItem] = []
    for item in items[:limit]:
        source = _get_text(item, "source") or "Unknown"
        news_items.append(
            NewsItem(
                title=_get_text(item, "title") or "(无标题)",
                link=_get_text(item, "link"),
                source=source,
                published=_get_text(item, "pubDate"),
            )
        )

    return news_items


def format_markdown_message(items: Iterable[NewsItem], query: str) -> str:
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    lines = [f"## 🌍 国际金融市场新闻日报（{today}）", f"> 检索关键词：`{query}`", ""]

    count = 0
    for index, item in enumerate(items, start=1):
        count += 1
        lines.append(
            f"{index}. **{item.title}**\n"
            f"   - 来源：{item.source}\n"
            f"   - 时间：{item.published or '未知'}\n"
            f"   - 链接：{item.link}"
        )

    if count == 0:
        lines.append("今天没有抓取到新闻，请检查关键词或网络连接。")

    return "\n".join(lines)


def _http_post_json(url: str, payload: dict, timeout: int) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urlopen(request, timeout=timeout) as resp:
        response_text = resp.read().decode("utf-8")
    return json.loads(response_text)


def push_to_feishu(webhook_url: str, markdown_text: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "国际金融市场新闻摘要",
                    "content": [[{"tag": "md", "text": markdown_text}]],
                }
            }
        },
    }

    body = _http_post_json(webhook_url, payload, timeout)
    if body.get("code") != 0:
        raise RuntimeError(f"飞书推送失败: code={body.get('code')}, msg={body.get('msg')}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取国际金融新闻并推送到飞书")
    parser.add_argument("--query", default=os.getenv("NEWS_QUERY", DEFAULT_QUERY), help="Google News RSS 查询关键词")
    parser.add_argument("--limit", type=int, default=int(os.getenv("NEWS_LIMIT", "8")), help="最多推送多少条新闻")
    parser.add_argument("--webhook", default=os.getenv("FEISHU_WEBHOOK_URL", ""), help="飞书机器人 Webhook 地址")
    parser.add_argument("--dry-run", action="store_true", help="只打印消息，不推送")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    args = parse_args()

    if args.limit <= 0:
        raise ValueError("--limit 必须大于 0")

    news_items = fetch_news(query=args.query, limit=args.limit)
    markdown = format_markdown_message(news_items, query=args.query)

    if args.dry_run:
        print(markdown)
        return

    if not args.webhook:
        raise ValueError("未提供飞书 webhook。请传 --webhook 或设置 FEISHU_WEBHOOK_URL")

    push_to_feishu(args.webhook, markdown)
    logging.info("已成功推送 %d 条新闻到飞书", len(news_items))


if __name__ == "__main__":
    main()
