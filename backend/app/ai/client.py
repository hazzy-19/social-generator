"""
Thin HTTP wrapper around the NVIDIA API. Nothing here knows about
prompts, extraction shapes, or the database — just "send text, get text back."
"""
import httpx

from app.core.config import settings

# Shared client — reuses TCP connections across requests. Closed on app
# shutdown via the FastAPI lifespan in main.py.
http_client = httpx.AsyncClient(timeout=120.0)


async def complete(prompt: str, max_tokens: int = 500) -> str:
    response = await http_client.post(
        f"{settings.nvidia_api_base_url}/chat/completions",
        headers={"Authorization": f"Bearer {settings.nvidia_api_key}"},
        json={
            "model": settings.nvidia_model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.95,
            "chat_template_kwargs": {"thinking": False},
        },
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
