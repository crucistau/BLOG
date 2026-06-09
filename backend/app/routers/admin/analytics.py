from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.visitor import PageView

router = APIRouter(
    prefix="/api/v1/admin/analytics",
    tags=["Admin Analytics"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/overview")
async def get_overview(db: AsyncSession = Depends(get_db)):
    """UV/PV 概览: 今日/昨日/本周/本月"""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)

    # PV counts
    today_pv = await db.scalar(
        func.count(PageView.id).where(PageView.created_at >= today_start)
    )
    yesterday_pv = await db.scalar(
        func.count(PageView.id).where(
            PageView.created_at >= yesterday_start,
            PageView.created_at < today_start,
        )
    )
    week_pv = await db.scalar(
        func.count(PageView.id).where(PageView.created_at >= week_start)
    )
    month_pv = await db.scalar(
        func.count(PageView.id).where(PageView.created_at >= month_start)
    )

    # UV counts (distinct IP)
    today_uv = await db.scalar(
        func.count(func.distinct(PageView.ip)).where(
            PageView.created_at >= today_start
        )
    )
    yesterday_uv = await db.scalar(
        func.count(func.distinct(PageView.ip)).where(
            PageView.created_at >= yesterday_start,
            PageView.created_at < today_start,
        )
    )
    week_uv = await db.scalar(
        func.count(func.distinct(PageView.ip)).where(
            PageView.created_at >= week_start
        )
    )
    month_uv = await db.scalar(
        func.count(func.distinct(PageView.ip)).where(
            PageView.created_at >= month_start
        )
    )

    return {
        "today": {"pv": today_pv or 0, "uv": today_uv or 0},
        "yesterday": {"pv": yesterday_pv or 0, "uv": yesterday_uv or 0},
        "week": {"pv": week_pv or 0, "uv": week_uv or 0},
        "month": {"pv": month_pv or 0, "uv": month_uv or 0},
    }


@router.get("/trend")
async def get_trend(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    """UV/PV 折线图数据 - 按天聚合"""
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)

    # 按天分组统计 PV 和 UV
    stmt = text(
        """
        SELECT
            DATE(created_at) as date,
            COUNT(*) as pv,
            COUNT(DISTINCT ip) as uv
        FROM page_views
        WHERE created_at >= :start
        GROUP BY DATE(created_at)
        ORDER BY date ASC
    """
    )
    result = await db.execute(stmt, {"start": start})
    rows = result.fetchall()

    # 填充缺失的日期
    data = []
    current = start.date()
    end = now.date()
    row_map = {row[0]: row for row in rows}

    while current <= end:
        row = row_map.get(current)
        data.append(
            {
                "date": current.isoformat(),
                "pv": row[1] if row else 0,
                "uv": row[2] if row else 0,
            }
        )
        current += timedelta(days=1)

    return data


@router.get("/region")
async def get_region(
    db: AsyncSession = Depends(get_db),
):
    """省份访客分布 - 用于地图展示"""
    stmt = text(
        """
        SELECT
            COALESCE(province, '未知') as province,
            COUNT(*) as pv,
            COUNT(DISTINCT ip) as uv
        FROM page_views
        GROUP BY province
        ORDER BY pv DESC
    """
    )
    result = await db.execute(stmt)
    rows = result.fetchall()
    return [
        {"province": row[0], "pv": row[1], "uv": row[2]} for row in rows
    ]


@router.get("/cities")
async def get_cities(
    province: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    """指定省份下的城市访客分布"""
    stmt = text(
        """
        SELECT
            COALESCE(city, '未知') as city,
            COUNT(*) as pv,
            COUNT(DISTINCT ip) as uv
        FROM page_views
        WHERE province = :province
        GROUP BY city
        ORDER BY pv DESC
    """
    )
    result = await db.execute(stmt, {"province": province})
    rows = result.fetchall()
    return [{"city": row[0], "pv": row[1], "uv": row[2]} for row in rows]


@router.get("/popular-pages")
async def get_popular_pages(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """热门页面排行"""
    stmt = text(
        """
        SELECT path, COUNT(*) as pv, COUNT(DISTINCT ip) as uv
        FROM page_views
        GROUP BY path
        ORDER BY pv DESC
        LIMIT :limit
    """
    )
    result = await db.execute(stmt, {"limit": limit})
    rows = result.fetchall()
    return [{"path": row[0], "pv": row[1], "uv": row[2]} for row in rows]


@router.get("/devices")
async def get_devices(db: AsyncSession = Depends(get_db)):
    """访客设备/浏览器分布"""
    stmt = text(
        """
        SELECT
            CASE
                WHEN user_agent LIKE '%Mobile%' OR user_agent LIKE '%Android%' THEN 'Mobile'
                WHEN user_agent LIKE '%iPad%' THEN 'Tablet'
                ELSE 'Desktop'
            END as device_type,
            COUNT(*) as count
        FROM page_views
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY device_type
        ORDER BY count DESC
    """
    )
    result = await db.execute(stmt)
    rows = result.fetchall()
    return [{"name": row[0], "value": row[1]} for row in rows]


@router.get("/referers")
async def get_referers(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """访客来源分布"""
    stmt = text(
        """
        SELECT
            CASE
                WHEN referer IS NULL OR referer = '' THEN '直接访问'
                WHEN referer LIKE '%google%' THEN 'Google'
                WHEN referer LIKE '%baidu%' THEN '百度'
                WHEN referer LIKE '%bing%' THEN 'Bing'
                WHEN referer LIKE '%github%' THEN 'GitHub'
                ELSE '其他'
            END as source,
            COUNT(*) as count
        FROM page_views
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY source
        ORDER BY count DESC
        LIMIT :limit
    """
    )
    result = await db.execute(stmt, {"limit": limit})
    rows = result.fetchall()
    return [{"name": row[0], "value": row[1]} for row in rows]
