from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies.auth import User, get_current_user
from app.models.post import Post, PostStatus
from app.models.tag import Tag
from app.schemas.post import PostCreate, PostListItem, PostResponse, PostUpdate
from app.services.markdown import render_markdown

router = APIRouter(
    prefix="/api/v1/admin/posts",
    tags=["admin-posts"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[PostListItem])
async def admin_list_posts(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Post)
        .options(selectinload(Post.tags), selectinload(Post.category))
        .order_by(Post.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=PostResponse, status_code=201)
async def create_post(
    body: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content_html = render_markdown(body.content_md)
    post = Post(
        title=body.title,
        slug=body.slug,
        content_md=body.content_md,
        content_html=content_html,
        summary=body.summary,
        status=PostStatus(body.status) if body.status else PostStatus.DRAFT,
        author_id=current_user.id,
        category_id=body.category_id,
    )
    if body.status == PostStatus.PUBLISHED:
        post.published_at = datetime.now(timezone.utc)

    if body.tag_ids:
        tags_result = await db.execute(select(Tag).where(Tag.id.in_(body.tag_ids)))
        post.tags = list(tags_result.scalars().all())

    db.add(post)
    await db.flush()
    await db.refresh(post)
    return post


@router.get("/{post_id}", response_model=PostResponse)
async def admin_get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Post)
        .where(Post.id == post_id)
        .options(selectinload(Post.tags), selectinload(Post.category))
    )
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    body: PostUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Post)
        .where(Post.id == post_id)
        .options(selectinload(Post.tags), selectinload(Post.category))
    )
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    update_data = body.model_dump(exclude_unset=True)

    if "content_md" in update_data:
        update_data["content_html"] = render_markdown(update_data["content_md"])

    tag_ids = update_data.pop("tag_ids", None)

    for field, value in update_data.items():
        setattr(post, field, value)

    if tag_ids is not None:
        tags_result = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
        post.tags = list(tags_result.scalars().all())

    await db.flush()
    await db.refresh(post)
    return post


@router.put("/{post_id}/publish", response_model=PostResponse)
async def toggle_publish(
    post_id: int,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Post)
        .where(Post.id == post_id)
        .options(selectinload(Post.tags), selectinload(Post.category))
    )
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.status == PostStatus.PUBLISHED:
        post.status = PostStatus.DRAFT
        post.published_at = None
    else:
        post.status = PostStatus.PUBLISHED
        post.published_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Post).where(Post.id == post_id)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    await db.delete(post)
