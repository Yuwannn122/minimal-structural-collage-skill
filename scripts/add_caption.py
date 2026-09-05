from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageStat


DEFAULT_FONT_CANDIDATES = (
    Path("C:/Windows/Fonts/georgia.ttf"),
    Path("C:/Windows/Fonts/times.ttf"),
    Path("C:/Windows/Fonts/pala.ttf"),
    Path("/System/Library/Fonts/NewYork.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Typeset a small, real English caption into the quiet area of a collage."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--line1", required=True)
    parser.add_argument("--line2", required=True)
    parser.add_argument("--font", type=Path)
    parser.add_argument("--font-size", type=int, default=21)
    parser.add_argument("--color", default="#292925")
    parser.add_argument("--split", type=float, default=0.5)
    parser.add_argument(
        "--position",
        choices=(
            "auto",
            "upper-left",
            "upper-center",
            "upper-right",
            "lower-left",
            "lower-center",
            "lower-right",
        ),
        default="auto",
    )
    return parser.parse_args()


def resolve_font(explicit: Path | None, size: int) -> tuple[ImageFont.FreeTypeFont, Path]:
    candidates = (explicit,) if explicit else DEFAULT_FONT_CANDIDATES
    for path in candidates:
        if path and path.exists():
            return ImageFont.truetype(str(path), size=size), path
    raise FileNotFoundError(
        "No classic serif font found. Pass an existing .ttf/.otf file with --font."
    )


def text_geometry(
    draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, line1: str, line2: str
) -> tuple[int, int, int]:
    boxes = [draw.textbbox((0, 0), line, font=font) for line in (line1, line2)]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    gap = max(7, round(font.size * 0.42))
    return max(widths), sum(heights) + gap, gap


def background_rgb(image: Image.Image, split_y: int) -> tuple[int, int, int]:
    width, height = image.size
    edge = max(24, min(width, height - split_y) // 12)
    samples = [
        image.crop((0, split_y, edge, split_y + edge)),
        image.crop((width - edge, split_y, width, split_y + edge)),
        image.crop((0, height - edge, edge, height)),
        image.crop((width - edge, height - edge, width, height)),
    ]
    strip = Image.new("RGB", (edge * 4, edge))
    for index, sample in enumerate(samples):
        strip.paste(sample.convert("RGB"), (index * edge, 0))
    return tuple(int(value) for value in ImageStat.Stat(strip).median)


def ink_score(image: Image.Image, box: tuple[int, int, int, int], bg: tuple[int, int, int]) -> float:
    crop = image.crop(box).convert("RGB")
    crop.thumbnail((160, 64), Image.Resampling.BILINEAR)
    total = 0.0
    marked = 0
    count = max(1, crop.width * crop.height)
    pixels = (
        crop.get_flattened_data()
        if hasattr(crop, "get_flattened_data")
        else crop.getdata()
    )
    for red, green, blue in pixels:
        distance = math.sqrt(
            (red - bg[0]) ** 2 + (green - bg[1]) ** 2 + (blue - bg[2]) ** 2
        )
        total += distance
        if distance > 42:
            marked += 1
    return (total / count) + 90.0 * (marked / count)


def candidate_box(
    name: str, width: int, height: int, split_y: int, text_w: int, text_h: int
) -> tuple[int, int, int, int, str]:
    panel_h = height - split_y
    margin_x = max(72, round(width * 0.08))
    y_ratio = 0.25 if name.startswith("upper") else 0.76
    center_y = split_y + round(panel_h * y_ratio)
    if name.endswith("left"):
        x = margin_x
        align = "left"
    elif name.endswith("right"):
        x = width - margin_x - text_w
        align = "left"
    else:
        x = (width - text_w) // 2
        align = "center"
    y = center_y - text_h // 2
    pad_x = max(18, round(text_w * 0.08))
    pad_y = max(14, round(text_h * 0.18))
    return (
        max(0, x - pad_x),
        max(split_y, y - pad_y),
        min(width, x + text_w + pad_x),
        min(height, y + text_h + pad_y),
        align,
    )


def main() -> int:
    args = parse_args()
    if not (0.35 <= args.split <= 0.65):
        raise ValueError("--split must be between 0.35 and 0.65")
    if args.font_size < 10:
        raise ValueError("--font-size must be at least 10")

    with Image.open(args.input) as opened:
        icc_profile = opened.info.get("icc_profile")
        image = opened.convert("RGB")

    width, height = image.size
    split_y = round(height * args.split)
    draw = ImageDraw.Draw(image)
    font, font_path = resolve_font(args.font, args.font_size)
    text_w, text_h, gap = text_geometry(draw, font, args.line1, args.line2)

    names = (
        "lower-left",
        "lower-right",
        "upper-left",
        "upper-right",
        "lower-center",
        "upper-center",
    )
    bg = background_rgb(image, split_y)
    choices: list[tuple[float, str, tuple[int, int, int, int, str]]] = []
    for index, name in enumerate(names):
        box = candidate_box(name, width, height, split_y, text_w, text_h)
        preference_penalty = index * 1.4
        choices.append((ink_score(image, box[:4], bg) + preference_penalty, name, box))

    if args.position == "auto":
        score, selected, box = min(choices, key=lambda item: item[0])
    else:
        selected = args.position
        box = candidate_box(selected, width, height, split_y, text_w, text_h)
        score = ink_score(image, box[:4], bg)

    left, top, right, bottom, align = box
    inset_x = max(18, round(text_w * 0.08))
    inset_y = max(14, round(text_h * 0.18))
    if align == "center":
        x1 = (width - draw.textlength(args.line1, font=font)) / 2
        x2 = (width - draw.textlength(args.line2, font=font)) / 2
    else:
        x1 = left + inset_x
        x2 = x1

    first_box = draw.textbbox((0, 0), args.line1, font=font)
    first_height = first_box[3] - first_box[1]
    color = ImageColor.getrgb(args.color)
    draw.text((round(x1), top + inset_y), args.line1, font=font, fill=color)
    draw.text(
        (round(x2), top + inset_y + first_height + gap),
        args.line2,
        font=font,
        fill=color,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    save_kwargs: dict[str, object] = {"format": "PNG", "compress_level": 6}
    if icc_profile:
        save_kwargs["icc_profile"] = icc_profile
    image.save(args.output, **save_kwargs)
    print(f"saved={args.output.resolve()}")
    print(f"caption={args.line1} / {args.line2}")
    print(f"position={selected}")
    print(f"whitespace_score={score:.2f}")
    print(f"font={font_path}")
    print(f"size={width}x{height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
