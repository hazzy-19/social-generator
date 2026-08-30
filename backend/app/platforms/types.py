"""
The PlatformType enum is owned here, not in generations/models.py —
platforms/ must have zero dependencies on other modules, and every
other module (generations, ai, images) depends on knowing what a
platform is. Import PlatformType from here everywhere.
"""
import enum


class PlatformType(str, enum.Enum):
    instagram = "instagram"
    linkedin = "linkedin"
    x = "x"
    facebook = "facebook"
