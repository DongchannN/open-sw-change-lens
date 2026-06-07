import feedparser

from app.models import NewsItem

GEEKNEWS_RSS_URL = "https://news.hada.io/rss/news"


def fetch_geeknews_items() -> list[NewsItem]:
    feed = feedparser.parse(GEEKNEWS_RSS_URL)

    return [
        NewsItem(
            title=entry.get("title", ""),
            link=entry.get("link", ""),
            summary=entry.get("summary", ""),
            published_at=entry.get("published", None),
        )
        for entry in feed.entries
    ]

