# Image Compressor & Converter Skill

A lightweight, local utility to **convert** web/modern images (`.webp`, `.avif`, etc.) into standard formats (**JPG / PNG / WEBP**) and **compress** them with quality control — all on your own machine, with no uploads to external services.

## The Problem It Solves

Developers and creators constantly run into web images in **modern formats** (`.webp`, `.avif`) or with **oversized dimensions / file sizes** that make them incompatible or too heavy to use right away:

- A backend, email client, or CMS that only accepts JPG/PNG.
- A repo or bundle ballooning because image assets are multi-megabyte WEBP/AVIF files.
- A thumbnail pipeline that needs consistent dimensions and quality.

This skill turns those images into ready-to-use JPG/PNG (or back to optimized WEBP) locally, with a `--quality` knob so you keep the size you want and never hit a "quality loss" surprise.

> Built and generated using **IronClaw AI Agent**.

## Features

- ✅ Convert to **JPG**, **PNG**, or **WEBP** (`-f`)
- ✅ Quality-controlled compression **1–100** (`-q`)
- ✅ Batch processing of many files in one call
- ✅ Optional aspect-ratio-preserving **resize** (`-s --max-dimension`)
- ✅ `--mode convert | compress` — change format, or keep it and just shrink the file
- ✅ **100% local** — nothing is uploaded anywhere
- ✅ Deterministic CLI → safe to call from scripts and CI

## Installation & Setup

Requires **Python 3.9+** and **Pillow**.

```bash
# 1. Clone
git clone https://github.com/kirichman5514-lgtm/ironclaw-image-compressor-skill.git
cd ironclaw-image-compressor-skill

# 2. (Recommended) isolated virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install the single dependency
pip install -r requirements.txt
```

No other setup required. Run it directly:

```bash
python image_compressor.py --help
```

## Usage

```bash
# Convert a WEBP to PNG at default quality
python image_compressor.py hero.webp -f png -o out/

# Convert to JPG at 80% quality, shrink longest side to 1200px
python image_compressor.py banner.webp -f jpg -q 80 -s 1200 -o out/

# Keep format, just compress (shrink file without changing extensions)
python image_compressor.py photo.png -m compress -q 60 -o out/

# Batch: many files -> PNG, into one folder
python image_compressor.py a.webp b.webp c.webp -f png -o out/

# Shell globs work too
python image_compressor.py assets/*.webp -f jpg -q 85 -o out/
```

| Option | Short | Meaning | Default |
|--------|-------|---------|---------|
| `--format` | `-f` | `jpg` \| `jpeg` \| `png` \| `webp` | `jpg` |
| `--quality` | `-q` | quality 1–100 (`100` = lossless PNG) | `85` |
| `--output` | `-o` | output dir / single file | `./output` |
| `--max-dimension` | `-s` | resize longest side (px) | unset |
| `--mode` | `-m` | `convert` \| `compress` | `convert` |

## Working Demo (terminal log)

A live run converting and compressing real files (source WEBP ~8.9 MB generated locally for the demo):

```text
$ python image_compressor.py demo_source.webp -f jpg -q 85 -s 1600 -o out_web
Input                                         Output                                     Fmt     In (KB)  Out (KB)     Δ %
demo_source.webp                              out_web/demo_source.jpg                    jpg       8707.0     318.4  -96.3%
Done.
```

Batch compression of two files at quality 50 with the summary row:

```text
$ python image_compressor.py demo_sample.png demo_sample2.jpg -f jpg -q 50 -o out_batch --mode compress
Input                                         Output                                     Fmt     In (KB)  Out (KB)     Δ %
demo_sample.png                               out_batch/demo_sample.jpg                    jpeg      715.1       1.8  -99.7%
demo_sample2.jpg                              out_batch/demo_sample2.jpg                   jpeg       53.7       2.7  -94.9%
-------------------------------------------------------------------------------------------------------------------
TOTAL                                                                                            768.8       4.6  -99.4%
Processed 2 file(s).
Done.
```

## Project Layout

```
ironclaw-image-compressor-skill/
├── image_compressor.py        # The main CLI tool
├── test_image_compressor.py   # Unit tests (built-in unittest)
├── SKILL.md                   # Full skill spec: API, inputs/outputs, dependencies
├── README.md                  # This file
├── requirements.txt           # Pillow dependency
├── .github/workflows/ci.yml   # GitHub Actions CI (test matrix + smoke test)
└── .gitignore
```

## Continuous Integration (CI)

On every push/PR to `main`, GitHub Actions runs the test suite across **Python 3.9 – 3.12**:

```bash
# What CI runs
python -m unittest test_image_compressor.py -v   # unit tests
python image_compressor.py --help                 # CLI smoke test
```

Run the same checks locally:

```bash
python -m unittest test_image_compressor.py -v
```

## Attribution

Built and generated using **IronClaw AI Agent**.