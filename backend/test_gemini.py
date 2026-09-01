import asyncio, sys, os
sys.path.insert(0, '.')
from app.ai.client import gemini_client
from app.ai.prompts import full_extraction_prompt
from app.core.config import settings

def _analysis_meta_prompt(prompt_text: str) -> str:
    return f"""You are a prompt engineering expert. Analyze the following AI prompt and break it into individual instructions.

PROMPT TO ANALYZE:
---
{prompt_text}
---

For each distinct instruction or directive in the prompt, output a JSON object with:
- "text": the exact instruction text (or a concise paraphrase)
- "label": one of exactly: essential | redundant | low-impact | conflicting | structural | ambiguous
- "reason": one sentence explaining the label
- "overlap_with": list of 0-based indices of other instructions this overlaps or duplicates

Return ONLY a valid JSON array. No markdown, no preamble, no explanation."""

async def test():
    try:
        sys_prompt = _analysis_meta_prompt(full_extraction_prompt('test', 'twitter', 280))
        
        response = await gemini_client.chat.completions.create(
            model=settings.gemini_model,
            messages=[{'role': 'user', 'content': sys_prompt}],
            max_tokens=1500,
            temperature=1,
            top_p=0.95,
            stream=False
        )
        print('Raw Response:', response)
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    asyncio.run(test())
