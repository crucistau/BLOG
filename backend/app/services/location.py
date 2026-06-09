import os

from ip2region.searcher import new_with_file_only
from ip2region.util import IPv4

# xdb 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "ip2region.xdb")


def ip_to_location(ip: str) -> dict[str, str | None]:
    """将 IP 地址解析为省份和城市"""
    if not os.path.exists(DB_PATH):
        return {"province": None, "city": None}
    try:
        searcher = new_with_file_only(IPv4, DB_PATH)
        result = searcher.search(ip)
        searcher.close()
        # result format: "中国|0|省份|城市|运营商"
        if not result:
            return {"province": None, "city": None}
        parts = result.split("|")
        province = parts[2] if len(parts) > 2 and parts[2] not in ("0", "") else None
        city = parts[3] if len(parts) > 3 and parts[3] not in ("0", "") else None
        return {"province": province, "city": city}
    except Exception:
        return {"province": None, "city": None}
