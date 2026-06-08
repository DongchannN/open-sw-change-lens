from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.models import InsightCreateRequest, InsightItem, InsightResponse, NewsResponse
from app.services.geeknews import fetch_geeknews_items
from app.services.insights import (
    DuplicateInsightError,
    InsightNotFoundError,
    create_insight,
    delete_insight,
    list_insights,
)

app = FastAPI(title="ChangeLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/news", response_model=NewsResponse)
def get_news():
    items, cached_at = fetch_geeknews_items()
    return NewsResponse(items=items, cached_at=cached_at)


@app.get("/api/insights", response_model=InsightResponse)
def get_insights():
    return InsightResponse(items=list_insights())


@app.post(
    "/api/insights",
    response_model=InsightItem,
    status_code=status.HTTP_201_CREATED,
)
def post_insight(payload: InsightCreateRequest):
    try:
        return create_insight(payload)
    except DuplicateInsightError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Insight already exists for this link",
        ) from exc


@app.delete("/api/insights/{insight_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_insight(insight_id: str):
    try:
        delete_insight(insight_id)
    except InsightNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found",
        ) from exc
