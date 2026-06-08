import unittest

from fastapi import HTTPException

from app.main import (
    delete_saved_insight,
    get_insights,
    get_saved_news,
    post_insight,
)
from app.models import InsightCreateRequest
from app.services.insights import clear_insights


class InsightApiTest(unittest.TestCase):
    def setUp(self):
        clear_insights()
        self.payload = {
            "title": "뉴스 제목",
            "link": "https://news.hada.io/topic?id=1",
            "summary": "뉴스 요약",
            "publishedAt": "2026-06-08T10:00:00+09:00",
            "interpretation": "내 해석",
            "impact": "High",
            "action": "다음 행동",
        }

    def tearDown(self):
        clear_insights()

    def test_create_insight(self):
        insight = post_insight(InsightCreateRequest(**self.payload))

        self.assertTrue(insight.id)
        self.assertEqual(insight.title, self.payload["title"])
        self.assertEqual(insight.link, self.payload["link"])
        self.assertEqual(insight.published_at, self.payload["publishedAt"])
        self.assertEqual(insight.impact, "High")
        self.assertTrue(insight.created_at.endswith("Z"))
        self.assertEqual(insight.created_at, insight.updated_at)

    def test_list_insights(self):
        post_insight(InsightCreateRequest(**self.payload))

        response = get_insights()

        self.assertEqual(len(response.items), 1)
        self.assertEqual(response.items[0].link, self.payload["link"])

    def test_list_saved_news_with_insight(self):
        post_insight(InsightCreateRequest(**self.payload))

        response = get_saved_news()

        self.assertEqual(len(response.items), 1)
        saved_news = response.items[0]
        self.assertEqual(saved_news.title, self.payload["title"])
        self.assertEqual(saved_news.link, self.payload["link"])
        self.assertEqual(saved_news.summary, self.payload["summary"])
        self.assertEqual(saved_news.published_at, self.payload["publishedAt"])
        self.assertEqual(saved_news.insight, self.payload["interpretation"])
        self.assertEqual(saved_news.impact, self.payload["impact"])
        self.assertEqual(saved_news.action, self.payload["action"])
        self.assertTrue(saved_news.saved_at.endswith("Z"))

    def test_create_insight_rejects_duplicate_link(self):
        post_insight(InsightCreateRequest(**self.payload))

        with self.assertRaises(HTTPException) as context:
            post_insight(InsightCreateRequest(**self.payload))

        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(
            context.exception.detail,
            "Insight already exists for this link",
        )

    def test_delete_insight(self):
        insight = post_insight(InsightCreateRequest(**self.payload))

        response = delete_saved_insight(insight.id)

        self.assertIsNone(response)
        self.assertEqual(get_insights().items, [])

    def test_delete_insight_returns_404_when_missing(self):
        with self.assertRaises(HTTPException) as context:
            delete_saved_insight("missing-id")

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Insight not found")

    def test_delete_insight_twice_returns_404_on_second_attempt(self):
        insight = post_insight(InsightCreateRequest(**self.payload))

        delete_saved_insight(insight.id)

        with self.assertRaises(HTTPException) as context:
            delete_saved_insight(insight.id)

        self.assertEqual(context.exception.status_code, 404)

    def test_delete_insight_removes_only_target_item(self):
        insight1 = post_insight(InsightCreateRequest(**self.payload))
        payload2 = {**self.payload, "link": "https://news.hada.io/topic?id=2"}
        insight2 = post_insight(InsightCreateRequest(**payload2))

        delete_saved_insight(insight1.id)

        remaining = get_insights().items
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].id, insight2.id)

    def test_create_insight_validates_impact(self):
        payload = {**self.payload, "impact": "Critical"}

        with self.assertRaises(ValueError):
            InsightCreateRequest(**payload)


if __name__ == "__main__":
    unittest.main()
