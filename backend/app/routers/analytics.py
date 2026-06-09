from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.tracker import record_page_view

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.post("/track", status_code=204)
async def track_page_view(
    request: Request, db: AsyncSession = Depends(get_db)
):
    """前端调用此接口记录页面访问"""
    body = (
        await request.json()
        if request.headers.get("content-type") == "application/json"
        else {}
    )
    ip = request.client.host if request.client else "127.0.0.1"
    # Handle proxy headers
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    path = body.get("path", "/")
    user_agent = request.headers.get("user-agent")
    referer = request.headers.get("referer")
    await record_page_view(
        ip=ip, path=path, user_agent=user_agent, referer=referer, db=db
    )
