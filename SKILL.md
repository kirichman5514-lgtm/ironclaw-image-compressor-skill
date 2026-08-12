# Image Compressor & Converter Skill

Converts images to standard formats (JPG / PNG / WEBP) and compresses them locally with quality control — no external uploads, no quality-blind downscaling.

- **Skill Name:** `image-compressor`
- **Entry point:** `image_compressor.py`
- **Framework:** Python 3.9+ / Pillow
- **Attribution:** Built and generated using IronClaw AI Agent.

---

## Purpose for an AI Agent (System Instructions / API)

This skill is a local, dependency-light command-line utility that an AI agent (or a human) can invoke to convert image files between formats and/or reduce their size. It is designed to be driven programmatically, so the agent should treat `image_compressor.py` as a deterministic CLI **API** with the contract below.

### When to use

Use this skill when the user:
- has an image in a web/modern format (`.webp`, `.avif`) that needs to be JPG/PNG or that is too large,
- needs a local, private conversion without uploading to an external service,
- needs batch conversion/compression of many files,
- needs quality-controlled compression (lossy for JPG/WEBP, lossless or aggressed for PNG).

### CLI API definition

```
python image_compressor.py <input...> [options]
```

| Argument | Alias | Type | Default | Description |
|----------|-------|------|---------|-------------|
| `input` | — | file path (repeatable) | — | Input image path(s). Shell globs are supported. **Required.** |
| `--format` | `-f` | `jpg` \| `jpeg` \| `png` \| `webp` | `jpg` | Target output format. `jpeg` maps to JPG. |
| `--quality` | `-q` | int 1–100 | `85` | Compression quality. `100` = lossless for PNG. |
| `--output` | `-o` | path | `./output` | Destination directory (or a single file path when one input is given). Created if missing. |
| `--max-dimension` | `-s` | int | unset | Resize the longest side to this many pixels (aspect ratio preserved). |
| `--mode` | `-m` | `convert` \| `compress` | `convert` | `convert` changes format; `compress` keeps the source format and only adjusts quality/optimization. |

### Behavior / Outputs

- On success, prints a table per file: input path, output path, target format, input size (KB), output size (KB), and size delta (%). For multiple files it prints a TOTAL row and a summary line.
- Exit codes: `0` success, `1` on errors (missing dependencies, missing input files, invalid quality), `2` on CLI/argparse errors (e.g. unknown format), `130` on Ctrl+C.
- Output format selection: PNG saves native alpha; JPG and lossy WEBP flatten alpha onto a white background and always produce RGB output.

### Error handling the agent must anticipate

- **Missing Pillow** → script exits `1` with an install hint (`pip install Pillow`).
- **Input file not found** → exits `1` listing all missing paths.
- **Quality outside 1–100** → exits `1` with an explicit message (plus argparse rejects non-integers).
- **Unknown format** → argparse rejects with exit code `2`.
- The tool never overwrites an input file; it always writes to `--output`.

### Tests / CI
- Unit tests live in `test_image_compressor.py` (built-in `unittest`, no framework needed). Run with `python -m unittest test_image_compressor.py -v`.
- GitHub Actions CI (`.github/workflows/ci.yml`) runs the tests and a CLI smoke test on every push/PR to `main` across Python 3.9–3.12.

---

## Inputs, Outputs, Dependencies

### Inputs
- One or more existing image files in any format Pillow can decode (JPEG, PNG, WEBP, GIF, BMP, TIFF, HEIF via Pillow codecs, etc.).
- Command-line parameters: target format, quality percentage, optional max-dimension resize, optional mode.

### Outputs
- Converted/compressed image files in the target directory.
- A human- and machine-readable summary table on stdout.

### Dependencies
| Dependency | Version | Purpose |
|-----------|---------|---------|
| Python | 3.9+ | Runtime. |
| Pillow | ≥ 9.0 (tested on 12.3) | Image decode/encode. Install via `pip install -r requirements.txt` or `pip install Pillow`. |

---

## Attribution

Built and generated using **IronClaw AI Agent**.