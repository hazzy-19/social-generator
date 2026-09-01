import asyncio
import os
import uuid
from app.core.config import settings

async def fetch_best_image(query: str, generation_id: uuid.UUID) -> str | None:
    """Uses pexelkit to search, score, and download the best image in one step."""
    output_filename = f"{generation_id}.jpg"
    output_path = f"uploads/images/{output_filename}"
    
    os.makedirs("uploads/images", exist_ok=True)
    
    # We pass the PEXELS_API_KEY into the subprocess environment
    env = os.environ.copy()
    env["PEXELS_API_KEY"] = settings.pexels_api_key
    
    # Command: npx -y pexelkit fetch "<query>" --out <path>
    process = await asyncio.create_subprocess_exec(
        "npx", "-y", "pexelkit", "fetch", query, "--out", output_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode == 0 and os.path.exists(output_path):
        return f"/static/images/{output_filename}"
    else:
        print(f"pexelkit error: {stderr.decode()}")
        return "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"

