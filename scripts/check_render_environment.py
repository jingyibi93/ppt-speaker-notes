#!/usr/bin/env python3
"""Check whether ppt-speaker-notes has stable rendering support."""

from __future__ import annotations

import importlib.util
import json
import shutil


def main() -> int:
    pdftoppm = shutil.which("pdftoppm")
    libreoffice = shutil.which("libreoffice") or shutil.which("soffice")
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    pymupdf = bool(importlib.util.find_spec("fitz"))
    pillow = bool(importlib.util.find_spec("PIL"))
    pypdf = bool(importlib.util.find_spec("pypdf"))

    stable_pdf = bool(pdftoppm or pymupdf)
    stable_presentation = bool(libreoffice and stable_pdf)
    result = {
        "stable_pdf_rendering": stable_pdf,
        "stable_ppt_or_pptx_rendering": stable_presentation,
        "tools": {
            "pdftoppm_poppler": pdftoppm,
            "pymupdf_fitz": pymupdf,
            "libreoffice_or_soffice": libreoffice,
            "pillow": pillow,
            "pypdf": pypdf,
            "ffmpeg": ffmpeg,
            "ffprobe": ffprobe,
        },
        "recommended_install": {
            "macos_homebrew": [
                "brew install poppler",
                "brew install --cask libreoffice",
                "brew install ffmpeg",
            ],
            "python_fallback_for_pdf": "python3 -m pip install PyMuPDF",
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if stable_pdf else 1


if __name__ == "__main__":
    raise SystemExit(main())
