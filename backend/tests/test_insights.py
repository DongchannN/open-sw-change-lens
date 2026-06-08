import unittest

from fastapi import HTTPException

from app.main import get_insights, post_insight
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

    def test_create_insight_rejects_duplicate_link(self):
        post_insight(InsightCreateRequest(**self.payload))

        with self.assertRaises(HTTPException) as context:
            post_insight(InsightCreateRequest(**self.payload))

        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(
            context.exception.detail,
            "Insight already exists for this link",
        )

    def test_create_insight_validates_impact(self):
        payload = {**self.payload, "impact": "Critical"}

        with self.assertRaises(ValueError):
            InsightCreateRequest(**payload)


if __name__ == "__main__":
    unittest.main()
