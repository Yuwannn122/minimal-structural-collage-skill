from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import ImageChops, ImageColor

from assemble_collage import (
    clamp_unit,
    extract_artwork,
    make_top_panel,
    prepare_artwork_panel,
    validate_geometry,
)
from image_io import load_srgb


def same_pixels(first, second) -> bool:
    return (
        first.size == second.size
        and ImageChops.difference(first, second).getbbox() is None
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Verify canvas geometry, original-photo fidelity, and optional "
            "lower-panel provenance. Reuse the same options used for assembly."
        )
    )
    parser.add_argument("collage", type=Path)
    parser.add_argument("--original", type=Path)
    parser.add_argument("--artwork", type=Path)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1536)
    parser.add_argument("--split", type=float, default=0.5)
    parser.add_argument("--focus-x", type=float, default=0.5)
    parser.add_argument("--focus-y", type=float, default=0.5)
    parser.add_argument(
        "--top-mode", choices=("cover", "contain", "extend"), default="cover"
    )
    parser.add_argument(
        "--artwork-mode", choices=("auto", "full", "panel"), default="auto"
    )
    parser.add_argument("--art-focus-x", type=float, default=0.5)
    parser.add_argument("--art-focus-y", type=float, default=0.5)
    parser.add_argument("--allow-crop-artwork", action="store_true")
    parser.add_argument("--paper-color", default="#F3EEDF")
    args = parser.parse_args()

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

    paper = ImageColor.getrgb(args.paper_color)
    if len(paper) != 3:
        parser.error("--paper-color must be an opaque RGB color")

    collage, collage_metadata = load_srgb(args.collage)
    failures: list[str] = []
    expected_size = (args.width, args.height)
    top_height = round(args.height * args.split)
    lower_height = args.height - top_height

    if collage.size != expected_size:
        failures.append(
            f"expected {args.width}x{args.height}, got {collage.width}x{collage.height}"
        )

    ratio_error = abs((collage.width / collage.height) - (2 / 3))
    if ratio_error > 0.001:
        failures.append("canvas is not an exact 2:3 portrait ratio")

    if args.original and collage.size == expected_size:
        original, _ = load_srgb(args.original)
        if args.top_mode == "extend":
            # Only the protected source-photo rectangle must be pixel-identical;
            # the surrounding scaffold is intentionally generated background.
            expected_layer, _, protected_rect = make_top_panel(
                original,
                (args.width, top_height),
                "contain",
                args.focus_x,
                args.focus_y,
                paper,
            )
            if protected_rect is None:
                failures.append("could not reconstruct protected top rectangle")
            else:
                actual_region = collage.crop(protected_rect)
                expected_region = expected_layer.crop(protected_rect)
                if not same_pixels(actual_region, expected_region):
                    failures.append(
                        "protected original-photo region differs from deterministic source"
                    )
                else:
                    print("top_original_fidelity=PASS")
                    print(f"top_protected_rect={protected_rect}")
        else:
            expected_top, _, _ = make_top_panel(
                original,
                (args.width, top_height),
                args.top_mode,
                args.focus_x,
                args.focus_y,
                paper,
            )
            actual_top = collage.crop((0, 0, args.width, top_height))
            if not same_pixels(actual_top, expected_top):
                failures.append(
                    "top panel differs from the deterministic original-photo composition"
                )
            else:
                print("top_original_fidelity=PASS")

    if args.artwork and collage.size == expected_size:
        artwork, _ = load_srgb(args.artwork)
        lower_source, _, resolved_mode = extract_artwork(
            artwork, args.artwork_mode, args.split
        )
        expected_lower, _ = prepare_artwork_panel(
            lower_source,
            (args.width, lower_height),
            args.allow_crop_artwork,
            args.art_focus_x,
            args.art_focus_y,
        )
        actual_lower = collage.crop(
            (0, top_height, args.width, args.height)
        )
        if not same_pixels(actual_lower, expected_lower):
            failures.append("lower panel differs from the supplied artwork")
        else:
            print("lower_artwork_fidelity=PASS")
            print(f"artwork_mode={resolved_mode}")

    print(f"canvas={collage.width}x{collage.height}")
    print(f"ratio_2_3={'PASS' if ratio_error <= 0.001 else 'FAIL'}")
    print(f"split_y={top_height}")
    print(f"color={collage_metadata.color_handling}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        raise SystemExit(1)

    print("verification=PASS")


if __name__ == "__main__":
    main()
