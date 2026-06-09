from sqlalchemy.ext.asyncio import AsyncSession

from app.models.visitor import PageView
from app.services.location import ip_to_location


async def record_page_view(
    ip: str,
    path: str,
    user_agent: str | None,
    referer: str | None,
    db: AsyncSession,
) -> None:
    """记录一次页面访问"""
    location = ip_to_location(ip)
    pv = PageView(
        ip=ip,
        path=path,
        user_agent=user_agent,
        referer=referer,
        province=location["province"],
        city=location["city"],
    )
    db.add(pv)
    await db.flush()
