from datetime import datetime

from pydantic import BaseModel


class TagBase(BaseModel):
    name: str
    slug: str


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None


class TagResponse(TagBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
