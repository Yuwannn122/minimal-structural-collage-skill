from __future__ import annotations

import argparse
import hashlib
import math
from pathlib import Path
from typing import Literal

from PIL import Image, ImageColor, ImageOps

from image_io import SRGB_ICC_BYTES, load_srgb

TopMode = Literal["cover", "contain", "extend"]
ArtworkMode = Literal["auto", "full", "panel"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clamp_unit(value: float, label: str) -> float:
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{label} must be a finite number between 0 and 1")
    return value


def validate_geometry(width: int, height: int, split: float) -> None:
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    if abs((width / height) - (2 / 3)) > 0.001:
        raise ValueError("canvas width and height must form an exact 2:3 ratio")
    if not math.isfinite(split) or not 0.48 <= split <= 0.52:
        raise ValueError("split must stay between 0.48 and 0.52")


def cover_crop_box(
    source_size: tuple[int, int],
    target_size: tuple[int, int],
    focus_x: float,
    focus_y: float,
) -> tuple[int, int, int, int]:
    source_width, source_height = source_size
    target_width, target_height = target_size
    target_ratio = target_width / target_height
    source_ratio = source_width / source_height

    if source_ratio > target_ratio:
        crop_height = source_height
        crop_width = min(source_width, round(crop_height * target_ratio))
        max_left = source_width - crop_width
        left = max(0, min(max_left, round(max_left * focus_x)))
        top = 0
    else:
        crop_width = source_width
        crop_height = min(source_height, round(crop_width / target_ratio))
        max_top = source_height - crop_height
        left = 0
        top = max(0, min(max_top, round(max_top * focus_y)))

    return left, top, left + crop_width, top + crop_height


def cover_panel(
    source: Image.Image,
    target_size: tuple[int, int],
    focus_x: float,
    focus_y: float,
) -> tuple[Image.Image, tuple[int, int, int, int]]:
    crop_box = cover_crop_box(source.size, target_size, focus_x, focus_y)
    cropped = source.crop(crop_box)
    # BICUBIC avoids the mild ringing that can resemble artificial sharpening.
    return cropped.resize(target_size, Image.Resampling.BICUBIC), crop_box


def contain_layer(
    source: Image.Image,
    target_size: tuple[int, int],
    focus_x: float,
    focus_y: float,
) -> tuple[Image.Image, tuple[int, int, int, int]]:
    contained = ImageOps.contain(source, target_size, Image.Resampling.BICUBIC)
    max_left = target_size[0] - contained.width
    max_top = target_size[1] - contained.height
    left = max(0, min(max_left, round(max_left * focus_x)))
    top = max(0, min(max_top, round(max_top * focus_y)))
    return contained, (left, top, left + contained.width, top + contained.height)


def resolve_artwork_mode(source: Image.Image, mode: ArtworkMode) -> Literal["full", "panel"]:
    if mode != "auto":
        return mode
    ratio = source.width / source.height
    if abs(ratio - (2 / 3)) <= 0.08:
        return "full"
    if abs(ratio - (4 / 3)) <= 0.12:
        return "panel"
    raise ValueError(
        "cannot infer artwork mode from aspect ratio; pass --artwork-mode full or panel"
    )


def extract_artwork(
    source: Image.Image,
    mode: ArtworkMode,
    split: float,
) -> tuple[Image.Image, Image.Image | None, Literal["full", "panel"]]:
    resolved_mode = resolve_artwork_mode(source, mode)
    if resolved_mode == "full":
        split_y = round(source.height * split)
        top_scaffold = source.crop((0, 0, source.width, split_y))
        lower = source.crop((0, split_y, source.width, source.height))
        return lower, top_scaffold, resolved_mode
    return source, None, resolved_mode


def prepare_artwork_panel(
    source: Image.Image,
    target_size: tuple[int, int],
    allow_crop: bool,
    focus_x: float,
    focus_y: float,
) -> tuple[Image.Image, tuple[int, int, int, int] | None]:
    source_ratio = source.width / source.height
    target_ratio = target_size[0] / target_size[1]
    if abs(source_ratio - target_ratio) <= 0.005:
        # Preserve the full designed panel and all of its negative space.
        return source.resize(target_size, Image.Resampling.BICUBIC), None
    if not allow_crop:
        raise ValueError(
            "artwork aspect ratio does not match its destination; regenerate at the "
            "correct ratio or pass --allow-crop-artwork explicitly"
        )
    return cover_panel(source, target_size, focus_x, focus_y)


def make_top_panel(
    original: Image.Image,
    target_size: tuple[int, int],
    mode: TopMode,
    focus_x: float,
    focus_y: float,
    paper: tuple[int, int, int],
    scaffold: Image.Image | None = None,
) -> tuple[
    Image.Image,
    tuple[int, int, int, int] | None,
    tuple[int, int, int, int] | None,
]:
    if mode == "cover":
        panel, crop_box = cover_panel(original, target_size, focus_x, focus_y)
        return panel, crop_box, (0, 0, target_size[0], target_size[1])

    original_layer, original_rect = contain_layer(
        original, target_size, focus_x, focus_y
    )
    if mode == "contain":
        panel = Image.new("RGB", target_size, paper)
    else:
        if scaffold is None:
            raise ValueError(
                "--top-mode extend requires a full 2:3 artwork draft whose top "
                "contains background-only extensions"
            )
        panel, _ = cover_panel(scaffold, target_size, 0.5, 0.5)

    panel.paste(original_layer, (original_rect[0], original_rect[1]))
    return panel, None, original_rect


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build a 2:3 collage while preserving the top subject as a direct, "
            "proportionally resized/cropped copy of the original photograph."
        )
    )
    parser.add_argument("original", type=Path)
    parser.add_argument("artwork", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1536)
    parser.add_argument("--split", type=float, default=0.5)
    parser.add_argument("--focus-x", type=float, default=0.5)
    parser.add_argument("--focus-y", type=float, default=0.5)
    parser.add_argument(
        "--top-mode", choices=("cover", "contain", "extend"), default="cover"
    )
    parser.add_argument(
        "--artwork-mode",
        choices=("auto", "full", "panel"),
        default="auto",
        help="Whether artwork is a full 2:3 draft or an independent lower panel.",
    )
    parser.add_argument("--art-focus-x", type=float, default=0.5)
    parser.add_argument("--art-focus-y", type=float, default=0.5)
    parser.add_argument(
        "--allow-crop-artwork",
        action="store_true",
        help="Explicitly allow an off-ratio illustration to be cover-cropped.",
    )
    parser.add_argument(
        "--paper-color",
        default="#F3EEDF",
        help="Background used for contain fitting.",
    )
    args = parser.parse_args()

    output_resolved = args.output.resolve()
    if output_resolved in {args.original.resolve(), args.artwork.resolve()}:
        parser.error("output must not overwrite the original or artwork source")

    try:
        validate_geometry(args.width, args.height, args.split)
        for value, label in (
            (args.focus_x, "--focus-x"),
            (args.focus_y, "--focus-y"),
            (args.art_focus_x, "--art-focus-x"),
            (args.art_focus_y, "--art-focus-y"),
        ):
            clamp_unit(value, label)
    except ValueError as error:
        parser.error(str(error))
    if args.output.suffix.lower() != ".png":
        parser.error("output must use a .png extension")

    paper = ImageColor.getrgb(args.paper_color)
    if len(paper) != 3:
        parser.error("--paper-color must be an opaque RGB color")

    original, original_metadata = load_srgb(args.original)
    artwork_source, artwork_metadata = load_srgb(args.artwork)
    top_height = round(args.height * args.split)
    lower_height = args.height - top_height
    try:
        lower_source, top_scaffold, resolved_artwork_mode = extract_artwork(
            artwork_source, args.artwork_mode, args.split
        )
        top, source_crop, protected_rect = make_top_panel(
            original,
            (args.width, top_height),
            args.top_mode,
            args.focus_x,
            args.focus_y,
            paper,
            top_scaffold,
        )
        lower, artwork_crop = prepare_artwork_panel(
            lower_source,
            (args.width, lower_height),
            args.allow_crop_artwork,
            args.art_focus_x,
            args.art_focus_y,
        )
    except ValueError as error:
        parser.error(str(error))

    result = Image.new("RGB", (args.width, args.height), paper)
    result.paste(top, (0, 0))
    result.paste(lower, (0, top_height))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(
        args.output,
        format="PNG",
        optimize=True,
        icc_profile=SRGB_ICC_BYTES,
    )

    print(f"saved={args.output}")
    print(f"sha256={sha256(args.output)}")
    print(f"size={result.width}x{result.height}")
    print(f"split_y={top_height}")
    print(f"top_mode={args.top_mode}")
    print(f"top_source_crop={source_crop}")
    print(f"top_protected_rect={protected_rect}")
    print(f"artwork_mode={resolved_artwork_mode}")
    print(f"artwork_crop={artwork_crop}")
    print(f"original_color={original_metadata.color_handling}")
    print(f"artwork_color={artwork_metadata.color_handling}")


if __name__ == "__main__":
    main()
