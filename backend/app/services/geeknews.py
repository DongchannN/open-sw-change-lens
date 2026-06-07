from html import unescape
from html.parser import HTMLParser
import logging

import feedparser

from app.models import NewsItem

GEEKNEWS_RSS_URL = "https://news.hada.io/rss/news"
logger = logging.getLogger(__name__)


class PlainTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str):
        text = data.strip()
        if text:
            self.parts.append(text)

    def get_text(self) -> str:
        return " ".join(self.parts)


def to_plain_text(value: str) -> str:
    parser = PlainTextParser()
    parser.feed(value)
    parser.close()
    return unescape(parser.get_text())


def fetch_geeknews_items() -> list[NewsItem]:
    try:
        feed = feedparser.parse(GEEKNEWS_RSS_URL)
    except Exception:
        logger.exception("Failed to parse GeekNews RSS feed")
        return []

    entries = getattr(feed, "entries", []) or []
    if getattr(feed, "bozo", False) and not entries:
        logger.warning(
            "GeekNews RSS feed is malformed: %s",
            getattr(feed, "bozo_exception", "unknown"),
        )
        return []

    return [
        NewsItem(
            title=entry.get("title", ""),
            link=entry.get("link", ""),
            summary=to_plain_text(entry.get("summary", "")),
            published_at=entry.get("published", None),
        )
        for entry in entries
    ]
