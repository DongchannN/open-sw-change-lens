from datetime import UTC, datetime
from threading import Lock
from uuid import uuid4

from app.models import InsightCreateRequest, InsightItem

_insight_lock = Lock()
_insights: list[InsightItem] = []


class DuplicateInsightError(Exception):
    pass


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def list_insights() -> list[InsightItem]:
    with _insight_lock:
        return list(_insights)


def create_insight(payload: InsightCreateRequest) -> InsightItem:
    global _insights

    with _insight_lock:
        if any(insight.link == payload.link for insight in _insights):
            raise DuplicateInsightError("Insight already exists for this link")

        now = _now_iso()
        insight = InsightItem(
            id=str(uuid4()),
            title=payload.title,
            link=payload.link,
            summary=payload.summary,
            published_at=payload.published_at,
            interpretation=payload.interpretation,
            impact=payload.impact,
            action=payload.action,
            created_at=now,
            updated_at=now,
        )
        _insights.append(insight)

    return insight


def clear_insights() -> None:
    global _insights

    with _insight_lock:
        _insights = []
