from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.tag import Tag
from app.schemas.tag import TagResponse

router = APIRouter(prefix="/api/v1/tags", tags=["tags"])


@router.get("", response_model=list[TagResponse])
async def list_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).order_by(Tag.name))
    return result.scalars().all()


@router.get("/{slug}", response_model=TagResponse)
async def get_tag(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.slug == slug))
    tag = result.scalar_one_or_none()
    if tag is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Tag not found")
    return tag
