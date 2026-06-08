from typing import Literal

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


ImpactLevel = Literal["Low", "Medium", "High"]


class InsightCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(min_length=1)
    link: str = Field(min_length=1)
    summary: str = ""
    published_at: str | None = Field(default=None, alias="publishedAt")
    interpretation: str = ""
    impact: ImpactLevel = "Medium"
    action: str = ""


class InsightItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    link: str
    summary: str
    published_at: str | None = Field(default=None, alias="publishedAt")
    interpretation: str
    impact: ImpactLevel
    action: str
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")


class InsightResponse(BaseModel):
    items: list[InsightItem]
