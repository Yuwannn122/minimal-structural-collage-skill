from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from image_io import SRGB_ICC_BYTES, load_srgb


def unique_destination(output_dir: Path, stem: str, suffix: str) -> Path:
    candidate = output_dir / f"{stem}{suffix}"
    index = 2
    while candidate.exists():
        candidate = output_dir / f"{stem}-{index}{suffix}"
        index += 1
    return candidate


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize phone images (including MPO-disguised JPG files) to an "
            "EXIF-corrected sRGB PNG and/or JPEG without visual enhancement."
        )
    )
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("images", nargs="+", type=Path)
    parser.add_argument(
        "--format",
        choices=("png", "jpeg", "both"),
        default="png",
        help="Output format; PNG is the safest input for image-editing tools.",
    )
    parser.add_argument("--jpeg-quality", type=int, default=95)
    args = parser.parse_args()

    if not 1 <= args.jpeg_quality <= 100:
        parser.error("--jpeg-quality must be between 1 and 100")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for source in args.images:
        if not source.is_file():
            raise FileNotFoundError(source)

        image, metadata = load_srgb(source)
        written: list[Path] = []

        if args.format in ("png", "both"):
            destination = unique_destination(args.output_dir, source.stem, ".png")
            image.save(
                destination,
                format="PNG",
                optimize=True,
                icc_profile=SRGB_ICC_BYTES,
            )
            written.append(destination)
        if args.format in ("jpeg", "both"):
            destination = unique_destination(args.output_dir, source.stem, ".jpg")
            image.save(
                destination,
                format="JPEG",
                quality=args.jpeg_quality,
                subsampling=0,
                optimize=True,
                icc_profile=SRGB_ICC_BYTES,
            )
            written.append(destination)

        print(f"source={source}")
        print(f"detected_format={metadata.detected_format}")
        print(f"frame_count={metadata.frame_count}")
        print(f"color_handling={metadata.color_handling}")
        for destination in written:
            print(f"saved={destination}")
            print(f"size={image.width}x{image.height}")
            print(f"sha256={sha256(destination)}")


if __name__ == "__main__":
    main()
