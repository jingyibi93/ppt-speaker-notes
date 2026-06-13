#!/usr/bin/env python3
"""Write generated speaker scripts into a safe PPTX copy."""

from __future__ import annotations

import argparse
import html
import posixpath
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

ET.register_namespace("", REL_NS)
ET.register_namespace("p", P_NS)
ET.register_namespace("a", A_NS)
ET.register_namespace("r", R_NS)


def parse_markdown_notes(path: Path, field: str) -> dict[int, str]:
    text = path.read_text(encoding="utf-8")
    notes: dict[int, str] = {}
    slide_pattern = re.compile(r"^##\s+(?:第\s*)?(\d+)\s*(?:页|Slide)?\s*$", re.M)
    matches = list(slide_pattern.finditer(text))
    for idx, match in enumerate(matches):
        slide_no = int(match.group(1))
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[start:end]
        field_match = re.search(
            rf"\*\*{re.escape(field)}：?\*\*\s*(.*?)(?=\n\n\*\*|\n##\s+|\Z)",
            block,
            flags=re.S,
        )
        if not field_match and field == "讲稿":
            field_match = re.search(r"\*\*Presentation Script:?\*\*\s*(.*?)(?=\n\n\*\*|\n##\s+|\Z)", block, flags=re.S)
        if field_match:
            value = cleanup_note_text(field_match.group(1))
            if value:
                notes[slide_no] = value
    return notes


def cleanup_note_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z0-9_-]*\s*|\s*```$", "", text).strip()
    text = text.strip("“”\"")
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def read_zip(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as zf:
        return {name: zf.read(name) for name in zf.namelist()}


def write_zip(path: Path, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)


def parse_xml(data: bytes) -> ET.Element:
    return ET.fromstring(data)


def serialize_xml(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def relationship_root(data: bytes | None = None) -> ET.Element:
    return parse_xml(data) if data else ET.Element(f"{{{REL_NS}}}Relationships")


def next_rid(root: ET.Element) -> str:
    used = []
    for rel in root:
        rid = rel.attrib.get("Id", "")
        if rid.startswith("rId") and rid[3:].isdigit():
            used.append(int(rid[3:]))
    return f"rId{max(used, default=0) + 1}"


def slide_count(files: dict[str, bytes]) -> int:
    return len([name for name in files if re.match(r"ppt/slides/slide\d+\.xml$", name)])


def existing_notes_map(files: dict[str, bytes]) -> dict[int, int]:
    mapping: dict[int, int] = {}
    for name, data in files.items():
        match = re.match(r"ppt/notesSlides/_rels/notesSlide(\d+)\.xml\.rels$", name)
        if not match:
            continue
        notes_no = int(match.group(1))
        root = relationship_root(data)
        for rel in root:
            if rel.attrib.get("Type") == f"{R_NS}/slide":
                target = rel.attrib.get("Target", "")
                slide_match = re.search(r"slide(\d+)\.xml$", target)
                if slide_match:
                    mapping[int(slide_match.group(1))] = notes_no
    return mapping


def max_notes_number(files: dict[str, bytes]) -> int:
    nums = []
    for name in files:
        match = re.match(r"ppt/notesSlides/notesSlide(\d+)\.xml$", name)
        if match:
            nums.append(int(match.group(1)))
    return max(nums, default=0)


def find_notes_master(files: dict[str, bytes]) -> str | None:
    for name in sorted(files):
        if re.match(r"ppt/notesMasters/notesMaster\d+\.xml$", name):
            return name
    return None


def default_notes_slide_xml(note: str) -> bytes:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<p:notes xmlns:a="{A_NS}" xmlns:r="{R_NS}" xmlns:p="{P_NS}">'
        "<p:cSld><p:spTree>"
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Slide Image Placeholder"/><p:cNvSpPr><a:spLocks noGrp="1" noRot="1" noChangeAspect="1"/></p:cNvSpPr><p:nvPr><p:ph type="sldImg" idx="2"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="1371600" y="1143000"/><a:ext cx="4114800" cy="3086100"/></a:xfrm></p:spPr></p:sp>'
        '<p:sp><p:nvSpPr><p:cNvPr id="3" name="Notes Placeholder"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="body" idx="3"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>'
        f"{paragraphs_xml(note)}"
        "</p:txBody></p:sp>"
        "</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>"
    ).encode("utf-8")


def paragraphs_xml(note: str) -> str:
    chunks = []
    for line in note.splitlines() or [""]:
        chunks.append(
            "<a:p><a:r><a:rPr lang=\"zh-CN\"/><a:t>"
            + html.escape(line)
            + "</a:t></a:r><a:endParaRPr lang=\"zh-CN\"/></a:p>"
        )
    return "".join(chunks)


def replace_notes_text(notes_xml: bytes, note: str) -> bytes:
    root = parse_xml(notes_xml)
    body_shape = None
    for shape in root.findall(f".//{{{P_NS}}}sp"):
        ph = shape.find(f".//{{{P_NS}}}ph")
        if ph is not None and ph.attrib.get("type") == "body":
            body_shape = shape
            break
    if body_shape is None:
        return default_notes_slide_xml(note)
    tx_body = body_shape.find(f"{{{P_NS}}}txBody")
    if tx_body is None:
        tx_body = ET.SubElement(body_shape, f"{{{P_NS}}}txBody")
        ET.SubElement(tx_body, f"{{{A_NS}}}bodyPr")
        ET.SubElement(tx_body, f"{{{A_NS}}}lstStyle")
    for child in list(tx_body):
        if child.tag == f"{{{A_NS}}}p":
            tx_body.remove(child)
    for line in note.splitlines() or [""]:
        p = ET.SubElement(tx_body, f"{{{A_NS}}}p")
        r = ET.SubElement(p, f"{{{A_NS}}}r")
        ET.SubElement(r, f"{{{A_NS}}}rPr", {"lang": "zh-CN"})
        t = ET.SubElement(r, f"{{{A_NS}}}t")
        t.text = line
        ET.SubElement(p, f"{{{A_NS}}}endParaRPr", {"lang": "zh-CN"})
    return serialize_xml(root)


def add_content_type(files: dict[str, bytes], notes_no: int) -> None:
    name = "[Content_Types].xml"
    root = parse_xml(files[name])
    part_name = f"/ppt/notesSlides/notesSlide{notes_no}.xml"
    for override in root.findall(f"{{{CT_NS}}}Override"):
        if override.attrib.get("PartName") == part_name:
            files[name] = serialize_xml(root)
            return
    ET.SubElement(
        root,
        f"{{{CT_NS}}}Override",
        {
            "PartName": part_name,
            "ContentType": "application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml",
        },
    )
    files[name] = serialize_xml(root)


def set_slide_notes_relationship(files: dict[str, bytes], slide_no: int, notes_no: int) -> None:
    rel_name = f"ppt/slides/_rels/slide{slide_no}.xml.rels"
    root = relationship_root(files.get(rel_name))
    target = f"../notesSlides/notesSlide{notes_no}.xml"
    for rel in root:
        if rel.attrib.get("Type") == f"{R_NS}/notesSlide":
            rel.set("Target", target)
            files[rel_name] = serialize_xml(root)
            return
    ET.SubElement(
        root,
        f"{{{REL_NS}}}Relationship",
        {"Id": next_rid(root), "Type": f"{R_NS}/notesSlide", "Target": target},
    )
    files[rel_name] = serialize_xml(root)


def notes_slide_rels(slide_no: int, master_name: str | None) -> bytes:
    root = ET.Element(f"{{{REL_NS}}}Relationships")
    ET.SubElement(
        root,
        f"{{{REL_NS}}}Relationship",
        {"Id": "rId2", "Type": f"{R_NS}/slide", "Target": f"../slides/slide{slide_no}.xml"},
    )
    if master_name:
        ET.SubElement(
            root,
            f"{{{REL_NS}}}Relationship",
            {"Id": "rId1", "Type": f"{R_NS}/notesMaster", "Target": f"../notesMasters/{Path(master_name).name}"},
        )
    return serialize_xml(root)


def write_notes(input_pptx: Path, notes_md: Path, output_pptx: Path, field: str) -> int:
    notes = parse_markdown_notes(notes_md, field)
    if not notes:
        raise SystemExit(f"No per-slide notes found in {notes_md}")

    files = read_zip(input_pptx)
    count = slide_count(files)
    mapping = existing_notes_map(files)
    next_notes = max_notes_number(files) + 1
    master = find_notes_master(files)

    for slide_no in range(1, count + 1):
        note = notes.get(slide_no)
        if not note:
            continue
        notes_no = mapping.get(slide_no)
        if notes_no is None:
            notes_no = next_notes
            next_notes += 1
            mapping[slide_no] = notes_no
            files[f"ppt/notesSlides/_rels/notesSlide{notes_no}.xml.rels"] = notes_slide_rels(slide_no, master)
            set_slide_notes_relationship(files, slide_no, notes_no)
            add_content_type(files, notes_no)
            files[f"ppt/notesSlides/notesSlide{notes_no}.xml"] = default_notes_slide_xml(note)
        else:
            note_name = f"ppt/notesSlides/notesSlide{notes_no}.xml"
            files[note_name] = replace_notes_text(files.get(note_name, b""), note)

    output_pptx.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx", dir=str(output_pptx.parent)) as tmp:
        temp_path = Path(tmp.name)
    try:
        write_zip(temp_path, files)
        shutil.move(str(temp_path), output_pptx)
    finally:
        if temp_path.exists():
            temp_path.unlink()
    return len(notes)


def main() -> int:
    parser = argparse.ArgumentParser(description="Write markdown speaker scripts into PPTX speaker notes.")
    parser.add_argument("input_pptx", type=Path)
    parser.add_argument("notes_md", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--field", default="讲稿", help="Markdown field to write into speaker notes")
    args = parser.parse_args()

    input_pptx = args.input_pptx.expanduser().resolve()
    notes_md = args.notes_md.expanduser().resolve()
    output = (args.output or input_pptx.with_name(f"{input_pptx.stem}_with_notes.pptx")).expanduser().resolve()
    written = write_notes(input_pptx, notes_md, output, args.field)
    print(f"Wrote {written} note(s) to: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
