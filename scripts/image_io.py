from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageCms, ImageOps


@dataclass(frozen=True)
class ImageMetadata:
    detected_format: str | None
    frame_count: int
    color_handling: str


_SRGB_PROFILE = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))
SRGB_ICC_BYTES = _SRGB_PROFILE.tobytes()


def _profile_is_srgb(profile: ImageCms.ImageCmsProfile) -> bool:
    try:
        description = ImageCms.getProfileDescription(profile).lower()
        info = ImageCms.getProfileInfo(profile).lower()
    except Exception:
        return False
    return "srgb" in description or "srgb" in info


def _flatten_alpha(image: Image.Image) -> Image.Image:
    if image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    ):
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (243, 238, 223, 255))
        return Image.alpha_composite(background, rgba).convert("RGB")
    return image


def load_srgb(path: Path) -> tuple[Image.Image, ImageMetadata]:
    """Load frame zero, apply EXIF orientation, and normalize embedded color to sRGB."""

    with Image.open(path) as opened:
        detected_format = opened.format
        frame_count = getattr(opened, "n_frames", 1)
        if frame_count > 1:
            opened.seek(0)
        icc_bytes = opened.info.get("icc_profile")
        image = ImageOps.exif_transpose(opened)
        image.load()

    image = _flatten_alpha(image)
    color_handling = "assumed_srgb_no_embedded_profile"

    if icc_bytes:
        try:
            source_profile = ImageCms.ImageCmsProfile(BytesIO(icc_bytes))
            if _profile_is_srgb(source_profile):
                image = image.convert("RGB")
                color_handling = "embedded_srgb_preserved"
            else:
                image = ImageCms.profileToProfile(
                    image,
                    source_profile,
                    _SRGB_PROFILE,
                    outputMode="RGB",
                    renderingIntent=ImageCms.Intent.PERCEPTUAL,
                )
                color_handling = "embedded_profile_converted_to_srgb"
        except Exception as error:
            image = image.convert("RGB")
            color_handling = f"invalid_profile_assumed_srgb:{type(error).__name__}"
    else:
        image = image.convert("RGB")

    return image, ImageMetadata(
        detected_format=detected_format,
        frame_count=frame_count,
        color_handling=color_handling,
    )
