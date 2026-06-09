from datetime import datetime

from pydantic import BaseModel

from app.schemas.category import CategoryResponse
from app.schemas.tag import TagResponse


class PostBase(BaseModel):
    title: str
    slug: str
    content_md: str
    summary: str | None = None
    category_id: int | None = None
    tag_ids: list[int] = []


class PostCreate(PostBase):
    status: str = "draft"


class PostUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    content_md: str | None = None
    summary: str | None = None
    status: str | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None


class PostListItem(BaseModel):
    id: int
    title: str
    slug: str
    summary: str | None
    status: str
    category: CategoryResponse | None = None
    tags: list[TagResponse] = []
    created_at: datetime
    published_at: datetime | None = None

    model_config = {"from_attributes": True}


class PostResponse(PostListItem):
    content_md: str
    content_html: str
    updated_at: datetime

    model_config = {"from_attributes": True}
