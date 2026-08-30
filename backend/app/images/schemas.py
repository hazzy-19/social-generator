"""
Response shape from the image-service. Kept separate from generations/schemas.py
since this module doesn't know about SocialGeneration.
"""
from pydantic import BaseModel


class ImageSearchResult(BaseModel):
    url: str
    photographer: str | None = None
    source: str = "pexels"
