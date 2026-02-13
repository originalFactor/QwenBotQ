from ... import config, httpClient

WEB_SEARCH_PROMPT = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "从互联网搜索资料，仅在绝对必须时使用。返回标题、摘要和发布时间。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索词",
                },
                "freshness": {
                    "type": "string",
                    "description": "时间范围。可填`noLimit`（默认）|`oneDay`|`oneWeek`|`oneMonth`|`oneYear`|`YYYY-MM-DD..YYYY-MM-DD`",
                },
                "include": {
                    "type": "string",
                    "description": "限制范围。多个域名使用|或,分隔，最多不能超过100个",
                },
                "exclude": {
                    "type": "string",
                    "description": "排除范围。多个域名使用|或,分隔，最多不能超过100个",
                },
                "count": {
                    "type": "string",
                    "description": "结果数量限制，默认为10，最大不能超过50",
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
    assert config.ai and config.ai.tools.bocha
    bocha = config.ai.tools.bocha

    headers = {
        "Authorization": f"Bearer {bocha.token}",
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

    resp = await httpClient.post(url=bocha.endpoint, headers=headers, json=payload)
    resp.raise_for_status()
    data = resp.json()["data"]["webPages"]["value"]

    return [
        {"title": _["name"], "summary": _["summary"], "publishedAt": _["datePublished"]}
        for _ in data
    ]
