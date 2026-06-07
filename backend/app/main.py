from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import NewsResponse
from app.services.geeknews import fetch_geeknews_items

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
    return NewsResponse(items=fetch_geeknews_items())
