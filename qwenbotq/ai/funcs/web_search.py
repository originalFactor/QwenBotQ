from ... import config, httpClient

WEB_SEARCH_PROMPT = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "从互联网搜索资料",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索词",
                },
                "freshness": {
                    "type": "string",
                    "description": "搜索指定时间范围内的网页。\n"
                    "可填值：\n"
                    "- noLimit，不限（默认）\n"
                    "- oneDay，一天内\n"
                    "- oneWeek，一周内\n"
                    "- oneMonth，一个月内\n"
                    "- oneYear，一年内\n"
                    '- YYYY-MM-DD..YYYY-MM-DD，搜索日期范围，例如："2025-01-01..2025-04-06"\n'
                    '- YYYY-MM-DD，搜索指定日期，例如："2025-04-06"\n'
                    "推荐使用“noLimit”。搜索算法会自动进行时间范围的改写，效果更佳。如果指定时间范围，很有可能出现时间范围内没有相关网页的情况，导致找不到搜索结果。",
                },
                "include": {
                    "type": "string",
                    "description": "指定搜索的网站范围。多个域名使用|或,分隔，最多不能超过100个\n"
                    "可填值：\n"
                    "- 根域名\n"
                    "- 子域名\n"
                    "例如：qq.com|m.163.com",
                },
                "exclude": {
                    "type": "string",
                    "description": "排除搜索的网站范围。多个域名使用|或,分隔，最多不能超过100个\n"
                    "可填值：\n"
                    "- 根域名\n"
                    "- 子域名\n"
                    "例如：qq.com|m.163.com",
                },
                "count": {
                    "type": "string",
                    "description": "返回结果的条数（实际返回结果数量可能会小于count指定的数量）。\n"
                    "- 可填范围：1-50，最大单次搜索返回50条\n"
                    "- 默认为10",
                },
            },
            "required": ["query"],
        },
    },
}


async def web_search(
    query: str,
    freshness: str = "noLimit",
    include: str = "",
    exclude: str = "",
    count: int = 10,
) -> list[dict[str, str]]:
    if not config.search_key:
        return []

    endpoint = "https://api.bocha.cn/v1/web-search"
    headers = {
        "Authorization": f"Bearer {config.search_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "query": query,
        "freshness": freshness,
        "summary": True,
        "include": include,
        "exclude": exclude,
        "count": count,
    }

    resp = await httpClient.post(url=endpoint, headers=headers, json=payload)
    resp.raise_for_status()
    data = resp.json()["data"]["webPages"]["value"]

    return [
        {"title": _["name"], "summary": _["summary"], "publishedAt": _["datePublished"]}
        for _ in data
    ]
