#!/usr/bin/env python3
"""Check whether ppt-speaker-notes has stable rendering support."""

from __future__ import annotations

import importlib.util
import json
import shutil


def main() -> int:
    pdftoppm = shutil.which("pdftoppm")
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    pymupdf = bool(importlib.util.find_spec("fitz"))
    pillow = bool(importlib.util.find_spec("PIL"))
    pypdf = bool(importlib.util.find_spec("pypdf"))

    stable_pdf = bool(pdftoppm or pymupdf)
    result = {
        "stable_pdf_rendering": stable_pdf,
        "stable_ppt_or_pptx_visual_analysis": "requires matching PDF input",
        "tools": {
            "pdftoppm_poppler": pdftoppm,
            "pymupdf_fitz": pymupdf,
            "pillow": pillow,
            "pypdf": pypdf,
            "ffmpeg": ffmpeg,
            "ffprobe": ffprobe,
        },
        "recommended_install": {
            "macos_homebrew": [
                "brew install poppler",
                "brew install ffmpeg",
            ],
            "python_fallback_for_pdf": "python3 -m pip install PyMuPDF",
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if stable_pdf else 1


if __name__ == "__main__":
    raise SystemExit(main())
