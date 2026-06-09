from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.post import Post, PostStatus
from app.models.tag import Tag
from app.schemas.post import PostListItem, PostResponse

router = APIRouter(prefix="/api/v1/posts", tags=["posts"])


def _post_list_query():
    return (
        select(Post)
        .where(Post.status == PostStatus.PUBLISHED)
        .options(selectinload(Post.tags), selectinload(Post.category))
        .order_by(Post.published_at.desc())
    )


@router.get("/search", response_model=list[PostListItem])
async def search_posts(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    stmt = _post_list_query().where(Post.title.ilike(f"%{q}%"))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("", response_model=list[PostListItem])
async def list_posts(
    category: str | None = None,
    tag: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = _post_list_query()

    if category:
        from app.models.category import Category

        cat_sub = select(Category.id).where(Category.slug == category).scalar_subquery()
        stmt = stmt.where(Post.category_id == cat_sub)

    if tag:
        tag_sub = select(Tag.id).where(Tag.slug == tag).scalar_subquery()
        stmt = stmt.where(Post.tags.any(Tag.id == tag_sub))

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{slug}", response_model=PostResponse)
async def get_post(slug: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Post)
        .where(Post.slug == slug, Post.status == PostStatus.PUBLISHED)
        .options(selectinload(Post.tags), selectinload(Post.category))
    )
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
