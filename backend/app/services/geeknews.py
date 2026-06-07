from html import unescape
from html.parser import HTMLParser
import logging
from datetime import UTC, datetime, timedelta
from threading import Lock
from urllib.error import URLError
from urllib.request import urlopen

import feedparser

from app.models import NewsItem

GEEKNEWS_RSS_URL = "https://news.hada.io/rss/news"
GEEKNEWS_CACHE_TTL = timedelta(minutes=5)
GEEKNEWS_REQUEST_TIMEOUT_SECONDS = 5
logger = logging.getLogger(__name__)

_cache_lock = Lock()
_cached_items: list[NewsItem] | None = None
_cached_at: datetime | None = None


class GeekNewsFetchError(Exception):
    pass


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


def _format_cached_at(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat().replace("+00:00", "Z")


def _fetch_geeknews_items_from_rss() -> list[NewsItem]:
    try:
        with urlopen(GEEKNEWS_RSS_URL, timeout=GEEKNEWS_REQUEST_TIMEOUT_SECONDS) as response:
            feed = feedparser.parse(response.read())
    except (OSError, URLError) as exc:
        raise GeekNewsFetchError("Failed to fetch GeekNews RSS feed") from exc
    except Exception as exc:
        raise GeekNewsFetchError("Failed to parse GeekNews RSS feed") from exc

    entries = getattr(feed, "entries", []) or []
    if getattr(feed, "bozo", False) and not entries:
        raise GeekNewsFetchError(
            f"GeekNews RSS feed is malformed: {getattr(feed, 'bozo_exception', 'unknown')}"
        )

    return [
        NewsItem(
            title=entry.get("title", ""),
            link=entry.get("link", ""),
            summary=to_plain_text(entry.get("summary", "")),
            published_at=entry.get("published", None),
        )
        for entry in entries
    ]


def fetch_geeknews_items() -> tuple[list[NewsItem], str | None]:
    global _cached_at, _cached_items

    now = datetime.now(UTC)
    with _cache_lock:
        if _cached_items is not None and _cached_at is not None:
            if now - _cached_at < GEEKNEWS_CACHE_TTL:
                return list(_cached_items), _format_cached_at(_cached_at)

    try:
        items = _fetch_geeknews_items_from_rss()
    except GeekNewsFetchError:
        logger.exception("Failed to refresh GeekNews RSS feed")
        with _cache_lock:
            if _cached_items is None:
                return [], None
            return list(_cached_items), _format_cached_at(_cached_at)

    cached_at = datetime.now(UTC)
    with _cache_lock:
        if not items and _cached_items is not None:
            return list(_cached_items), _format_cached_at(_cached_at)

        _cached_items = items
        _cached_at = cached_at

    return list(items), _format_cached_at(cached_at)
