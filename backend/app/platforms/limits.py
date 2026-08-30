"""
Static platform character limits. Pure lookup, zero dependencies on
any other module. If you later want these editable without a redeploy,
swap this for a query against a platform_limits table.
"""
from app.platforms.types import PlatformType

_CHAR_LIMITS: dict[PlatformType, int] = {
    PlatformType.x: 280,
    PlatformType.instagram: 2200,
    PlatformType.linkedin: 3000,
    PlatformType.facebook: 63206,
}


def get_char_limit(platform: PlatformType) -> int:
    return _CHAR_LIMITS[platform]
