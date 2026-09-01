"""
Thin HTTP wrapper around the NVIDIA API. Nothing here knows about
prompts, extraction shapes, or the database — just "send text, get text back."
"""
from openai import AsyncOpenAI
from app.core.config import settings

# Shared clients — reuses TCP connections across requests.
nvidia_client = AsyncOpenAI(
    base_url=settings.nvidia_api_base_url,
    api_key=settings.nvidia_api_key,
)

gemini_client = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=settings.gemini_api_key,
)

async def complete(prompt: str, max_tokens: int = 8192) -> str:
    if settings.ai_provider.lower() == "gemini":
        client = gemini_client
        model = settings.gemini_model
    else:
        client = nvidia_client
        model = settings.nvidia_model

    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=1,
        top_p=0.95,
        stream=False
    )
    
    content = response.choices[0].message.content
    return content.strip() if content else ""

from typing import AsyncGenerator

async def complete_stream(prompt: str, max_tokens: int = 8192) -> AsyncGenerator[str, None]:
    if settings.ai_provider.lower() == "gemini":
        client = gemini_client
        model = settings.gemini_model
    else:
        client = nvidia_client
        model = settings.nvidia_model

    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=1,
        top_p=0.95,
        stream=True
    )
    
    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            yield content
