from ip2region import Ip2Region


def ip_to_location(ip: str) -> dict[str, str | None]:
    """将 IP 地址解析为省份和城市"""
    try:
        with Ip2Region() as searcher:
            result = searcher.search(ip)
            # result format: "中国|0|省份|城市|运营商"
            parts = result.get("region", "").split("|")
            province = parts[2] if len(parts) > 2 and parts[2] != "0" else None
            city = parts[3] if len(parts) > 3 and parts[3] != "0" else None
            return {"province": province, "city": city}
    except Exception:
        return {"province": None, "city": None}
