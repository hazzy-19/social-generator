"""
Thin HTTP wrapper around the DeepSeek API. Nothing here knows about
prompts, extraction shapes, or the database — just "send text, get text back."
"""
from typing import AsyncGenerator
from openai import AsyncOpenAI
from app.core.config import settings

# Shared client — reuses TCP connections across requests.
deepseek_client = AsyncOpenAI(
    base_url=settings.deepseek_api_base_url,
    api_key=settings.deepseek_api_key or "missing-key",
)


async def complete(prompt: str, max_tokens: int = 8192) -> str:
    response = await deepseek_client.chat.completions.create(
        model=settings.deepseek_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7,
        stream=False,
    )

    content = response.choices[0].message.content
    return content.strip() if content else ""


async def complete_stream(prompt: str, max_tokens: int = 8192) -> AsyncGenerator[str, None]:
    response = await deepseek_client.chat.completions.create(
        model=settings.deepseek_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7,
        stream=True,
    )

    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            yield content
