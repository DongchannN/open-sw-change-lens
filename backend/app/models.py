from pydantic import BaseModel, ConfigDict, Field


class NewsItem(BaseModel):
    title: str
    link: str
    summary: str
    published_at: str | None = None


class NewsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[NewsItem]
    cached_at: str | None = Field(default=None, alias="cachedAt")
