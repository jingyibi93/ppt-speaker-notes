#!/usr/bin/env python3
"""Prepare PPT/PDF materials for Codex speaker-note generation."""

from __future__ import annotations

import argparse
import json
import math
import posixpath
import re
import shutil
import subprocess
import sys
import zipfile
from html import unescape
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

try:
    from PIL import Image, ImageDraw, ImageFile, ImageSequence

    ImageFile.LOAD_TRUNCATED_IMAGES = True
    HAS_PILLOW = True
except Exception:
    Image = ImageDraw = ImageFile = ImageSequence = None  # type: ignore[assignment]
    HAS_PILLOW = False

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}
VIDEO_EXTENSIONS = (".mp4", ".mov", ".m4v", ".avi", ".wmv", ".mpg", ".mpeg", ".webm")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(text)).strip()


def text_from_xml(xml: bytes) -> str:
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return ""
    return normalize_text(" ".join(node.text or "" for node in root.findall(".//a:t", NS)))


def read_slide_media_refs(zf: zipfile.ZipFile, slide_number: int) -> list[str]:
    rels_name = f"ppt/slides/_rels/slide{slide_number}.xml.rels"
    if rels_name not in zf.namelist():
        return []
    try:
        root = ET.fromstring(zf.read(rels_name))
    except ET.ParseError:
        return []
    refs = []
    for rel in root:
        target = rel.attrib.get("Target", "")
        if "media/" in target:
            resolved = posixpath.normpath(posixpath.join("ppt/slides", target))
            refs.append(resolved if resolved.startswith("ppt/media/") else target)
    return refs


def read_pptx(path: Path) -> list[dict[str, Any]]:
    slides: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as zf:
        slide_names = sorted(
            [n for n in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)],
            key=lambda n: int(re.search(r"slide(\d+)\.xml", n).group(1)),  # type: ignore[union-attr]
        )
        notes_names = {
            int(re.search(r"notesSlide(\d+)\.xml", n).group(1)): n  # type: ignore[union-attr]
            for n in zf.namelist()
            if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", n)
        }
        for index, name in enumerate(slide_names, start=1):
            media_refs = read_slide_media_refs(zf, index)
            slides.append(
                {
                    "slide_number": index,
                    "text": text_from_xml(zf.read(name)),
                    "existing_notes": text_from_xml(zf.read(notes_names[index])) if index in notes_names else "",
                    "media_refs": media_refs,
                    "gif_refs": [ref for ref in media_refs if ref.lower().endswith(".gif")],
                    "video_refs": [ref for ref in media_refs if ref.lower().endswith(VIDEO_EXTENSIONS)],
                    "gif_assets": [],
                    "video_assets": [],
                    "image": None,
                }
            )
    return slides


def read_pdf_text(path: Path) -> list[dict[str, Any]]:
    """Extract per-page PDF text when pypdf is available."""
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return []

    try:
        reader = PdfReader(str(path))
    except Exception:
        return []

    pages: list[dict[str, Any]] = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            text = normalize_text(page.extract_text() or "")
        except Exception:
            text = ""
        pages.append(
            {
                "slide_number": index,
                "text": text,
                "existing_notes": "",
                "media_refs": [],
                "gif_refs": [],
                "video_refs": [],
                "gif_assets": [],
                "video_assets": [],
                "image": None,
            }
        )
    return pages


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def stable_pdf_renderer_available() -> bool:
    if command_exists("pdftoppm"):
        return True
    try:
        import fitz  # type: ignore  # noqa: F401

        return True
    except Exception:
        return False


def missing_render_dependencies(input_file: Path) -> list[str]:
    missing: list[str] = []
    suffix = input_file.suffix.lower()
    if suffix in {".ppt", ".pptx"}:
        missing.append("A matching PDF exported from the same PPT/PPTX is required for visual analysis")
    if not stable_pdf_renderer_available():
        missing.append("Poppler pdftoppm or Python PyMuPDF/fitz is required to render PDF pages to PNG")
    return missing


def render_pdf_to_images(pdf_file: Path, slides_dir: Path, width: int) -> list[Path]:
    slides_dir.mkdir(parents=True, exist_ok=True)
    if command_exists("pdftoppm"):
        prefix = slides_dir / "slide"
        result = subprocess.run(
            ["pdftoppm", "-png", "-scale-to-x", str(width), "-scale-to-y", "-1", str(pdf_file), str(prefix)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode == 0:
            images = sorted(slides_dir.glob("slide-*.png"))
            for idx, img in enumerate(images, start=1):
                img.rename(slides_dir / f"slide_{idx:03d}.png")
            return sorted(slides_dir.glob("slide_*.png"))

    try:
        import fitz  # type: ignore

        images = []
        doc = fitz.open(pdf_file)
        for idx, page in enumerate(doc, start=1):
            scale = width / page.rect.width
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            target = slides_dir / f"slide_{idx:03d}.png"
            pix.save(target)
            images.append(target)
        return images
    except Exception:
        return []


def create_gif_keyframe_sheet(gif_file: Path, output_file: Path, max_frames: int = 8) -> int:
    if not HAS_PILLOW:
        raise RuntimeError("Pillow not found")
    with Image.open(gif_file) as img:
        frames = [frame.convert("RGBA") for frame in ImageSequence.Iterator(img)]
    if not frames:
        raise ValueError("GIF contains no frames")
    if len(frames) <= max_frames:
        indices = list(range(len(frames)))
    else:
        indices = sorted({round(i * (len(frames) - 1) / (max_frames - 1)) for i in range(max_frames)})
    selected = [frames[i].convert("RGB") for i in indices]
    thumb_w, label_h, gap = 240, 28, 12
    cols = min(4, len(selected))
    rows = (len(selected) + cols - 1) // cols
    thumbs = []
    for frame_index, frame in zip(indices, selected):
        ratio = thumb_w / frame.width
        thumb = frame.resize((thumb_w, max(1, int(frame.height * ratio))))
        canvas = Image.new("RGB", (thumb_w, thumb.height + label_h), "white")
        canvas.paste(thumb, (0, label_h))
        ImageDraw.Draw(canvas).text((8, 7), f"frame {frame_index + 1}/{len(frames)}", fill=(0, 0, 0))
        thumbs.append(canvas)
    cell_h = max(t.height for t in thumbs)
    sheet = Image.new("RGB", (cols * thumb_w + (cols + 1) * gap, rows * cell_h + (rows + 1) * gap), (245, 245, 245))
    for idx, thumb in enumerate(thumbs):
        row, col = divmod(idx, cols)
        sheet.paste(thumb, (gap + col * (thumb_w + gap), gap + row * (cell_h + gap)))
    sheet.save(output_file, quality=90)
    return len(frames)


def create_image_contact_sheets(
    images: list[Path],
    output_dir: Path,
    prefix: str,
    labels: list[str] | None = None,
    thumb_width: int = 260,
    max_per_sheet: int = 24,
) -> list[Path]:
    if not images or not HAS_PILLOW:
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    sheets: list[Path] = []
    label_h, gap = 30, 12
    for sheet_index, start in enumerate(range(0, len(images), max_per_sheet), start=1):
        batch = images[start : start + max_per_sheet]
        cols = min(6, len(batch))
        rows = math.ceil(len(batch) / cols)
        thumbs: list[Image.Image] = []

        for batch_index, image_path in enumerate(batch):
            image_index = start + batch_index + 1
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                ratio = thumb_width / max(1, img.width)
                thumb = img.resize((thumb_width, max(1, int(img.height * ratio))))
            canvas = Image.new("RGB", (thumb_width, thumb.height + label_h), "white")
            canvas.paste(thumb, (0, label_h))
            label = labels[image_index - 1] if labels and image_index - 1 < len(labels) else f"slide {image_index}"
            ImageDraw.Draw(canvas).text((8, 8), label[:44], fill=(0, 0, 0))
            thumbs.append(canvas)

        cell_h = max(t.height for t in thumbs)
        sheet = Image.new("RGB", (cols * thumb_width + (cols + 1) * gap, rows * cell_h + (rows + 1) * gap), (245, 245, 245))
        for idx, thumb in enumerate(thumbs):
            row, col = divmod(idx, cols)
            sheet.paste(thumb, (gap + col * (thumb_width + gap), gap + row * (cell_h + gap)))

        target = output_dir / f"{prefix}_{sheet_index:02d}.jpg"
        sheet.save(target, quality=88)
        sheets.append(target)
    return sheets


def create_video_keyframes(video_file: Path, output_dir: Path, max_frames: int = 6) -> list[Path]:
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise RuntimeError("ffmpeg/ffprobe not found")
    output_dir.mkdir(parents=True, exist_ok=True)
    probe = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(video_file)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    duration = max(0.1, float(probe.stdout.strip()))
    frames = []
    for idx in range(max_frames):
        seconds = duration * idx / max(1, max_frames - 1)
        target = output_dir / f"frame_{idx + 1:02d}.jpg"
        result = subprocess.run(
            [ffmpeg, "-y", "-ss", f"{seconds:.3f}", "-i", str(video_file), "-frames:v", "1", "-q:v", "2", str(target)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode == 0 and target.exists():
            frames.append(target)
    if not frames:
        raise RuntimeError("ffmpeg did not produce preview frames")
    return frames


def copy_animated_media(input_file: Path, output_dir: Path, slides: list[dict[str, Any]]) -> list[str]:
    if input_file.suffix.lower() != ".pptx":
        return []
    media_dir = output_dir / "animated_media"
    gif_preview_dir = output_dir / "animated_previews" / "gifs"
    video_preview_dir = output_dir / "animated_previews" / "videos"
    media_dir.mkdir(parents=True, exist_ok=True)
    gif_preview_dir.mkdir(parents=True, exist_ok=True)
    video_preview_dir.mkdir(parents=True, exist_ok=True)
    status: list[str] = []
    with zipfile.ZipFile(input_file) as zf:
        available = set(zf.namelist())
        for slide in slides:
            slide_no = int(slide["slide_number"])
            for ref in slide.get("gif_refs", []):
                if ref not in available:
                    status.append(f"slide {slide_no}: missing GIF {ref}")
                    continue
                target = media_dir / f"slide_{slide_no:03d}_{Path(ref).name}"
                target.write_bytes(zf.read(ref))
                preview = gif_preview_dir / f"{target.stem}_keyframes.jpg"
                info = {"source": ref, "file": str(target)}
                try:
                    info.update({"preview": str(preview), "frame_count": create_gif_keyframe_sheet(target, preview)})
                except Exception as exc:
                    status.append(f"slide {slide_no}: GIF preview failed for {ref}: {exc}")
                slide["gif_assets"].append(info)
            for ref in slide.get("video_refs", []):
                if ref not in available:
                    status.append(f"slide {slide_no}: missing video {ref}")
                    continue
                target = media_dir / f"slide_{slide_no:03d}_{Path(ref).name}"
                target.write_bytes(zf.read(ref))
                preview_dir = video_preview_dir / target.stem
                info = {"source": ref, "file": str(target)}
                try:
                    info.update({"preview_frames": [str(p) for p in create_video_keyframes(target, preview_dir)]})
                except Exception as exc:
                    status.append(f"slide {slide_no}: video preview skipped for {ref}: {exc}")
                slide["video_assets"].append(info)
    if not any(s.get("gif_assets") or s.get("video_assets") for s in slides):
        status.append("no GIF or video media extracted")
    return status


def write_context(output_dir: Path, input_file: Path, slides: list[dict[str, Any]], render_status: str, media_status: list[str], export_attempts: list[str]) -> None:
    lines = [
        f"# Deck Context: {input_file.name}",
        "",
        f"- Source file: `{input_file}`",
        f"- Slide count: {len(slides)}",
        f"- Render status: {render_status}",
        f"- Animated media status: {'; '.join(media_status) if media_status else 'not applicable'}",
        f"- PPT export attempts: {'; '.join(export_attempts) if export_attempts else 'not applicable'}",
        f"- Contact sheets: {', '.join(str(p) for p in sorted((output_dir / 'contact_sheets').glob('*.jpg'))) or 'none'}",
        "",
        "## Slide Inventory",
        "",
    ]
    for slide in slides:
        image = slide.get("image") or ""
        lines.extend(
            [
                f"### Slide {slide['slide_number']}",
                f"- Rendered image: `{image}`" if image else "- Rendered image: unavailable",
                f"- Media references in PPTX: {len(slide.get('media_refs', []))}",
                f"- GIF animations: {', '.join(slide.get('gif_refs', []))}" if slide.get("gif_refs") else "- GIF animations: none detected",
                f"- Video media: {', '.join(slide.get('video_refs', []))}" if slide.get("video_refs") else "- Video media: none detected",
                f"- GIF previews: {', '.join(a.get('preview', '') for a in slide.get('gif_assets', []) if a.get('preview'))}" if slide.get("gif_assets") else "- GIF previews: none",
                f"- Video preview frames: {', '.join(f for a in slide.get('video_assets', []) for f in a.get('preview_frames', []))}" if slide.get("video_assets") else "- Video preview frames: none",
                "",
                "**Extracted text:**",
                "",
                slide.get("text") or "(none)",
                "",
                "**Existing notes:**",
                "",
                slide.get("existing_notes") or "(none)",
                "",
            ]
        )
    (output_dir / "deck_context.md").write_text("\n".join(lines), encoding="utf-8")


def collect_environment() -> dict[str, Any]:
    return {
        "stable_pdf_renderer_available": stable_pdf_renderer_available(),
        "stable_ppt_or_pptx_visual_analysis": "requires matching PDF input",
        "pdftoppm": shutil.which("pdftoppm"),
        "ffmpeg": shutil.which("ffmpeg"),
        "ffprobe": shutil.which("ffprobe"),
        "pillow": HAS_PILLOW,
        "pypdf": _module_available("pypdf"),
        "recommended_install": {
            "macos_homebrew": [
                "brew install poppler",
                "brew install ffmpeg",
            ],
            "python_fallback_for_pdf": "python3 -m pip install PyMuPDF",
            "python_text_extraction": "python3 -m pip install pypdf",
        },
    }


def _module_available(name: str) -> bool:
    try:
        __import__(name)
        return True
    except Exception:
        return False


def write_manifest(
    output_dir: Path,
    input_file: Path,
    render_status: str,
    media_status: list[str],
    export_attempts: list[str],
    slides: list[dict[str, Any]],
    contact_sheets: list[Path],
) -> None:
    environment = collect_environment()
    (output_dir / "render_environment.json").write_text(json.dumps(environment, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = {
        "source": str(input_file),
        "output_dir": str(output_dir),
        "render_status": render_status,
        "animated_media_status": media_status,
        "ppt_export_attempts": export_attempts,
        "contact_sheets": [str(path) for path in contact_sheets],
        "environment": environment,
        "slides": slides,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare presentation materials for speaker-note generation.")
    parser.add_argument("input", type=Path, help="Input .ppt, .pptx, or .pdf file")
    parser.add_argument("--output", type=Path, help="Output folder")
    parser.add_argument("--width", type=int, default=1600, help="Rendered image width")
    parser.add_argument("--require-render", action="store_true", help="Fail if per-page images cannot be produced")
    args = parser.parse_args()

    input_file = args.input.expanduser().resolve()
    if not input_file.exists():
        print(f"Input not found: {input_file}", file=sys.stderr)
        return 2

    output_dir = (args.output or input_file.with_name(f"{input_file.stem}_speaker_note_materials")).resolve()
    slides_dir = output_dir / "slides"
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = input_file.suffix.lower()
    slides: list[dict[str, Any]] = []
    media_status: list[str] = []
    export_attempts: list[str] = []
    pdf_for_render: Path | None = None
    render_status = "not attempted"

    if suffix == ".pptx":
        slides = read_pptx(input_file)
        media_status = copy_animated_media(input_file, output_dir, slides)
        render_status = "pptx input; visual rendering skipped; provide a matching PDF for slide images"
    elif suffix == ".ppt":
        render_status = "ppt input; visual rendering skipped; provide a matching PDF for slide images"
    elif suffix == ".pdf":
        pdf_for_render = input_file
        slides = read_pdf_text(input_file)
        render_status = "pdf input"
    else:
        print("Only .ppt, .pptx, and .pdf are supported.", file=sys.stderr)
        return 2

    rendered_images = render_pdf_to_images(pdf_for_render, slides_dir, args.width) if pdf_for_render else []
    if rendered_images:
        render_status += f"; rendered {len(rendered_images)} image(s)"
    elif pdf_for_render:
        render_status += "; pdf rendering tool unavailable"

    if suffix == ".pdf":
        if not slides:
            slides = [
                {
                    "slide_number": idx,
                    "text": "",
                    "existing_notes": "",
                    "media_refs": [],
                    "gif_refs": [],
                    "video_refs": [],
                    "gif_assets": [],
                    "video_assets": [],
                    "image": None,
                }
                for idx in range(1, len(rendered_images) + 1)
            ]
        if len(slides) < len(rendered_images):
            for idx in range(len(slides) + 1, len(rendered_images) + 1):
                slides.append(
                    {
                        "slide_number": idx,
                        "text": "",
                        "existing_notes": "",
                        "media_refs": [],
                        "gif_refs": [],
                        "video_refs": [],
                        "gif_assets": [],
                        "video_assets": [],
                        "image": None,
                    }
                )
        for slide, image in zip(slides, rendered_images):
            slide["image"] = str(image)
    else:
        for slide, image in zip(slides, rendered_images):
            slide["image"] = str(image)

    contact_sheets = create_image_contact_sheets(
        rendered_images,
        output_dir / "contact_sheets",
        "slides",
        labels=[f"slide {idx}" for idx in range(1, len(rendered_images) + 1)],
    )
    preview_images = sorted(
        [
            path
            for path in (output_dir / "animated_previews").rglob("*")
            if path.suffix.lower() in {".jpg", ".jpeg", ".png"}
        ]
    )
    contact_sheets.extend(
        create_image_contact_sheets(
            preview_images,
            output_dir / "contact_sheets",
            "animated_previews",
            labels=[path.stem for path in preview_images],
        )
    )
    write_manifest(output_dir, input_file, render_status, media_status, export_attempts, slides, contact_sheets)
    write_context(output_dir, input_file, slides, render_status, media_status, export_attempts)
    print(f"Wrote: {output_dir / 'manifest.json'}")
    print(f"Wrote: {output_dir / 'deck_context.md'}")
    if contact_sheets:
        print(f"Contact sheets: {output_dir / 'contact_sheets'}")
    if rendered_images:
        print(f"Rendered images: {slides_dir}")
    else:
        print("No slide images rendered. Provide a matching PDF for PPT/PPTX visual analysis, or install PDF render dependencies for PDF input.")
        if args.require_render:
            print("Rendering is required but no per-page images were produced.", file=sys.stderr)
            for item in missing_render_dependencies(input_file):
                print(f"- {item}", file=sys.stderr)
            print("Recommended macOS setup:", file=sys.stderr)
            print("  brew install poppler", file=sys.stderr)
            print("  brew install ffmpeg", file=sys.stderr)
            print("  python3 -m pip install PyMuPDF pypdf Pillow", file=sys.stderr)
            return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
