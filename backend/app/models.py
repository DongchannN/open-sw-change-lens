from pydantic import BaseModel


class NewsItem(BaseModel):
    title: str
    link: str
    summary: str
    published_at: str | None = None


class NewsResponse(BaseModel):
    items: list[NewsItem]

