import asyncio
import os
import uuid
import httpx
from app.core.config import settings

FALLBACK_IMAGE_URL = "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"


async def fetch_best_image(query: str, generation_id: uuid.UUID) -> str:
    """Fetches the best image from Pexels API natively in Python."""
    output_filename = f"{generation_id}.jpg"
    output_path = f"uploads/images/{output_filename}"

    os.makedirs("uploads/images", exist_ok=True)

    if not settings.pexels_api_key:
        print("Warning: No PEXELS_API_KEY set, using fallback image.")
        return FALLBACK_IMAGE_URL

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {"Authorization": settings.pexels_api_key}
            params = {"query": query, "per_page": 1, "orientation": "landscape"}
            
            resp = await client.get("https://api.pexels.com/v1/search", headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("photos"):
                print(f"Pexels found no photos for query: '{query}', using fallback.")
                return FALLBACK_IMAGE_URL

            # Get the large image URL
            photo_url = data["photos"][0]["src"]["large2x"]

            # Download the image
            img_resp = await client.get(photo_url)
            img_resp.raise_for_status()

            # Save the image to disk
            with open(output_path, "wb") as f:
                f.write(img_resp.content)

            return f"/static/images/{output_filename}"
            
    except Exception as exc:
        print(f"Error fetching image natively via Pexels API: {exc}")
        return FALLBACK_IMAGE_URL
