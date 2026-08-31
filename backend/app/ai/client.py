"""
Thin HTTP wrapper around the NVIDIA API. Nothing here knows about
prompts, extraction shapes, or the database — just "send text, get text back."
"""
from openai import AsyncOpenAI
from app.core.config import settings

# Shared client — reuses TCP connections across requests.
client = AsyncOpenAI(
    base_url=settings.nvidia_api_base_url,
    api_key=settings.nvidia_api_key,
)

async def complete(prompt: str, max_tokens: int = 500) -> str:
    response = await client.chat.completions.create(
        model=settings.nvidia_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=1,
        top_p=0.95,
        seed=42,
        extra_body={"chat_template_kwargs": {"thinking": False}},
        stream=False
    )
    return response.choices[0].message.content.strip()
