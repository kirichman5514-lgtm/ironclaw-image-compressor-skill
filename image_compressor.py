#!/usr/bin/env python3
"""
Image Compressor & Converter Skill — IronClaw

Converts images to standard formats (JPG / PNG / WEBP) and compresses them
locally with quality control, without any external service uploads.

Built and generated using IronClaw AI Agent.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    sys.exit(
        "Missing dependency: Pillow.\n"
        "Install it with:  pip install Pillow\n"
        f"Original error: {exc}"
    )

# Format identifiers acceptable via --format (lowercased).
ALLOWED_FORMATS = {"jpg", "jpeg", "png", "webp"}

# Canonical file extension per accepted format identifier.
CANONICAL_EXT = {
    "jpg": ".jpg",
    "jpeg": ".jpg",
    "png": ".png",
    "webp": ".webp",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="image_compressor",
        description="Convert and compress images locally (JPG/PNG/WEBP).",
    )
    parser.add_argument(
        "input",
        nargs="+",
        help="Input image path(s). Globs are expanded by your shell.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=sorted(ALLOWED_FORMATS),
        default="jpg",
        help="Target output format. Default: jpg",
    )
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=85,
        help="Compression quality 1-100. Default: 85. Lossless for PNG/Q=100.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help=(
            "Output destination: a directory (created if missing) or a file "
            "path when a single input is given. Default: ./output"
        ),
    )
    parser.add_argument(
        "-s",
        "--max-dimension",
        type=int,
        default=None,
        help="Resize the longest side to this many pixels while preserving aspect ratio.",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["convert", "compress"],
        default="convert",
        help=(
            "convert: change format (resample to RGB for jpg/webp-lossy). "
            "compress: keep format, only adjust quality. Default: convert"
        ),
    )
    return parser.parse_args(argv)


def _normalize_output(path: Path, in_name: str, fmt: str, real_out_is_dir: Path | None) -> Path:
    """Decide the final output file path."""
    ext = CANONICAL_EXT[fmt]

    if real_out_is_dir is not None:
        return real_out_is_dir / f"{in_name}{ext}"

    # User passed a single explicit output file.
    if path.suffix:
        return path
    # User passed a directory-looking path without extension -> treat as dir.
    return path / f"{in_name}{ext}"


def convert_image(
    src: Path,
    dst: Path,
    fmt: str,
    quality: int,
    max_dimension: int | None,
) -> dict[str, object]:
    """Convert/compress one image. Returns processing stats."""
    with Image.open(src) as img:
        img.load()

        # Optional resize, preserving aspect ratio.
        if max_dimension and max(img.size) > max_dimension:
            img.thumbnail((max_dimension, max_dimension))

        # RGB is required for JPEG and for lossy WEBP handling of alpha;
        # PNG keeps alpha natively.
        if fmt in {"jpg", "webp"} and img.mode in {"RGBA", "LA", "P"}:
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background
        if img.mode not in {"RGB", "L", "P"} and fmt == "png":
            img = img.convert("RGBA")

        save_kwargs: dict[str, object] = {}
        if fmt in {"jpg", "webp"}:
            save_kwargs["quality"] = quality
            if fmt == "webp":
                save_kwargs["method"] = 6  # slower, better compression
        else:
            # PNG: treat quality 100 as lossless, otherwise optimize harder.
            save_kwargs["optimize"] = True
            if quality < 100:
                save_kwargs["compress_level"] = max(1, round(9 * quality / 100))

        dst.parent.mkdir(parents=True, exist_ok=True)
        img.save(
            dst,
            format="PNG" if fmt == "png" else ("JPEG" if fmt == "jpg" else "WEBP"),
            **save_kwargs,
        )

    return {
        "input": str(src),
        "output": str(dst),
        "input_bytes": src.stat().st_size,
        "output_bytes": dst.stat().st_size,
        "format": fmt,
        "quality": quality,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not 1 <= args.quality <= 100:
        sys.exit(f"Invalid quality {args.quality}: must be between 1 and 100.")
    fmt = "jpeg" if args.format in {"jpg", "jpeg"} else args.format

    srcs = [Path(p) for p in args.input]
    missing = [str(s) for s in srcs if not s.exists()]
    if missing:
        sys.exit(f"Input file(s) not found: {', '.join(missing)}")

    out_arg = Path(args.output)
    single = len(srcs) == 1
    out_is_dir = None
    if out_arg.is_dir() or (not out_arg.suffix and not single):
        out_is_dir = out_arg
    elif single:
        out_arg.parent.mkdir(parents=True, exist_ok=True)

    results = []
    for src in srcs:
        dst = _normalize_output(out_arg, src.stem, args.format, out_is_dir)
        results.append(convert_image(src, dst, fmt, args.quality, args.max_dimension))

    # Report
    total_in = total_out = 0
    print(f"{'Input':<46}{'Output':<46}{'Fmt':<6}{'In (KB)':>9}{'Out (KB)':>10}{'Δ %':>8}")
    for r in results:
        total_in += r["input_bytes"]
        total_out += r["output_bytes"]
        delta = (
            (r["output_bytes"] - r["input_bytes"]) / r["input_bytes"] * 100.0
            if r["input_bytes"]
            else 0.0
        )
        print(
            f"{r['input'][:46]:<46}{r['output'][:46]:<46}{r['format']:<6}"
            f"{r['input_bytes'] / 1024:>9.1f}{r['output_bytes'] / 1024:>10.1f}{delta:>7.1f}%"
        )

    if len(results) > 1:
        total_delta = (total_out - total_in) / total_in * 100.0 if total_in else 0.0
        print("-" * 115)
        print(
            f"{'TOTAL':<92}{'':<6}{total_in / 1024:>9.1f}{total_out / 1024:>10.1f}{total_delta:>7.1f}%"
        )
        print(f"Processed {len(results)} file(s).")

    print("Done.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        sys.exit(130)