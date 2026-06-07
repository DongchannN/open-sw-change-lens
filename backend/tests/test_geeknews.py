import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from app.models import NewsItem
from app.services import geeknews


class FetchGeeknewsItemsTest(unittest.TestCase):
    def setUp(self):
        self.cached_at = datetime(2026, 6, 7, 9, 0, tzinfo=UTC)
        self.cached_item = NewsItem(
            title="cached",
            link="https://example.com/cached",
            summary="cached summary",
            published_at=None,
        )
        self.fresh_item = NewsItem(
            title="fresh",
            link="https://example.com/fresh",
            summary="fresh summary",
            published_at=None,
        )

        geeknews._cached_items = None
        geeknews._cached_at = None

    def tearDown(self):
        geeknews._cached_items = None
        geeknews._cached_at = None

    def test_fetch_geeknews_items_ttl_hit(self):
        geeknews._cached_items = [self.cached_item]
        geeknews._cached_at = self.cached_at

        with (
            patch("app.services.geeknews.datetime") as datetime_mock,
            patch("app.services.geeknews._fetch_geeknews_items_from_rss") as fetch_mock,
        ):
            datetime_mock.now.return_value = self.cached_at + timedelta(minutes=1)

            items, cached_at = geeknews.fetch_geeknews_items()

        self.assertEqual(items, [self.cached_item])
        self.assertEqual(cached_at, "2026-06-07T09:00:00Z")
        fetch_mock.assert_not_called()

    def test_fetch_geeknews_items_rss_failure_returns_stale_cache(self):
        geeknews._cached_items = [self.cached_item]
        geeknews._cached_at = self.cached_at

        with (
            patch(
                "app.services.geeknews._fetch_geeknews_items_from_rss",
                side_effect=geeknews.GeekNewsFetchError,
            ),
            patch("app.services.geeknews.logger.exception"),
            patch("app.services.geeknews.datetime") as datetime_mock,
        ):
            datetime_mock.now.return_value = self.cached_at + timedelta(minutes=10)

            items, cached_at = geeknews.fetch_geeknews_items()

        self.assertEqual(items, [self.cached_item])
        self.assertEqual(cached_at, "2026-06-07T09:00:00Z")

    def test_fetch_geeknews_items_no_cache_on_failure_returns_empty(self):
        with (
            patch(
                "app.services.geeknews._fetch_geeknews_items_from_rss",
                side_effect=geeknews.GeekNewsFetchError,
            ),
            patch("app.services.geeknews.logger.exception"),
            patch("app.services.geeknews.datetime") as datetime_mock,
        ):
            datetime_mock.now.return_value = self.cached_at

            items, cached_at = geeknews.fetch_geeknews_items()

        self.assertEqual(items, [])
        self.assertIsNone(cached_at)

    def test_fetch_geeknews_items_empty_refresh_preserves_stale_cache(self):
        geeknews._cached_items = [self.cached_item]
        geeknews._cached_at = self.cached_at

        with (
            patch("app.services.geeknews._fetch_geeknews_items_from_rss", return_value=[]),
            patch("app.services.geeknews.datetime") as datetime_mock,
        ):
            datetime_mock.now.return_value = self.cached_at + timedelta(minutes=10)

            items, cached_at = geeknews.fetch_geeknews_items()

        self.assertEqual(items, [self.cached_item])
        self.assertEqual(cached_at, "2026-06-07T09:00:00Z")
        self.assertEqual(geeknews._cached_items, [self.cached_item])
        self.assertEqual(geeknews._cached_at, self.cached_at)

    def test_fetch_geeknews_items_empty_refresh_without_cache_updates_cache(self):
        with (
            patch("app.services.geeknews._fetch_geeknews_items_from_rss", return_value=[]),
            patch("app.services.geeknews.datetime") as datetime_mock,
        ):
            datetime_mock.now.return_value = self.cached_at

            items, cached_at = geeknews.fetch_geeknews_items()

        self.assertEqual(items, [])
        self.assertEqual(cached_at, "2026-06-07T09:00:00Z")
        self.assertEqual(geeknews._cached_items, [])
        self.assertEqual(geeknews._cached_at, self.cached_at)


if __name__ == "__main__":
    unittest.main()
