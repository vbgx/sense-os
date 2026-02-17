from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field


class VerticalMetaOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    audience: str | None = None
    function: str | None = None
    industry: str | None = None
    cluster: str | None = None
    member: str | None = None
    persona: str | None = None
    variant: str | None = None


class VerticalOut(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: str
    name: str
    title: str | None = None
    description: str | None = None
    enabled: bool | None = True
    tags: List[str] = Field(default_factory=list)
    meta: VerticalMetaOut | None = None
    tier: Literal["core", "experimental", "long_tail"] | None = None
    taxonomy_version: str | None = None


class VerticalListOut(BaseModel):
    items: List[VerticalOut]
