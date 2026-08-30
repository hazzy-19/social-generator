"""
Calls the Node image-service (which wraps pexelkit) over HTTP.
This module never imports pexelkit or Node code directly, and never
knows about Postgres or SocialGeneration.
"""
import httpx

from app.core.config import settings

# Shared client — reuses TCP connections across requests. Closed on app
# shutdown via the FastAPI lifespan in main.py.
http_client = httpx.AsyncClient(timeout=15.0)


async def fetch_best_image(query: str) -> str | None:
    """Returns a photo URL for the given description, or None if nothing matched."""
    try:
        response = await http_client.get(f"{settings.image_service_url}/search", params={"q": query})
        response.raise_for_status()
        data = response.json()
        return data.get("url")
    except httpx.HTTPError:
        return "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
