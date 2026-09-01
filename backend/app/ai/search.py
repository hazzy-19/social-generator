import httpx

from app.shared.exceptions import ExternalServiceError

TAVILY_URL = "https://api.tavily.com/search"


async def search_web(query: str, api_key: str, max_results: int = 4) -> list[dict]:
    """Returns a list of {"title", "content", "url"} dicts."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                TAVILY_URL,
                json={
                    "api_key": api_key,
                    "query": query,
                    "max_results": max_results,
                    "search_depth": "basic",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                {"title": r["title"], "content": r["content"], "url": r["url"]}
                for r in data.get("results", [])
            ]
    except Exception as exc:
        raise ExternalServiceError(f"Web search failed: {exc}") from exc


async def build_grounded_context(topic: str, api_key: str) -> str:
    """Fetches current web results on `topic` and formats them as a context
    block. Returns "" if search fails or finds nothing — callers should treat
    that as non-fatal and fall back to the original source_content alone."""
    try:
        results = await search_web(topic, api_key)
    except ExternalServiceError:
        return ""

    if not results:
        return ""

    lines = ["Verified current information (use this over your own assumptions if they conflict):"]
    for r in results:
        lines.append(f"- {r['title']}: {r['content'][:300]}")
    return "\n".join(lines)
