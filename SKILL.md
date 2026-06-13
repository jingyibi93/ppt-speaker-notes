---
name: ppt-speaker-notes
description: Generate natural speaker notes or narration drafts for old PPT/PPTX/PDF slide decks, especially visual/design-heavy presentations. Use when the user wants Codex to analyze the whole deck context, render slides to images when possible, interpret design intent conservatively, choose Chinese/English/bilingual output from the user's request language or explicit language choice, and produce an independent notes document or a safe copy instead of overwriting the original presentation.
---

# PPT Speaker Notes

Use this skill to create speaker notes for an existing presentation that has little or no presenter notes.

## Default Output

- Choose the output language before writing notes:
  - Use the language explicitly requested by the user.
  - If no language is explicitly requested, follow the language of the user's request. English requests should produce English notes; Chinese requests should produce Chinese notes.
  - If the user asks for bilingual output, translation, or both Chinese and English, make the bilingual structure explicit.
- Use natural spoken language in the requested output language, suitable for a presenter to read or lightly adapt as a mature presentation script.
- Write for a broad design-professional context. Do not assume the presenter is a teacher or the audience is students unless the source deck or user explicitly says so. In Chinese, prefer neutral terms such as "听众", "观众", "团队", "汇报时", "展示时", or "这一页可以说明". In English, prefer neutral terms such as "the audience", "viewers", "the team", "in this presentation", "this slide suggests", or "we can use this slide to discuss".
- Prefer an independent Markdown document named like `<deck-name>_speaker_notes.md`.
- For PPTX input, also create a safe copy named like `<deck-name>_with_notes.pptx` with each slide's script inserted into that slide's speaker notes, unless the user asks for Markdown only.
- Confirm the final output folder before creating final files. If the user did not specify where to save the Markdown and PPTX copy, ask one concise question before generating final outputs.
- Keep intermediate render/extraction files temporary by default. Do not leave material folders in the user's working directory unless the user asks to keep debug materials, rendering fails and evidence needs inspection, or the intermediate assets are explicitly part of the requested deliverable.
- Do not overwrite the original PPT/PPTX/PDF. If the user asks for notes written back into PPT, create a copy first.
- When evidence is uncertain, use conservative wording. In Chinese, use phrases such as "这一页看起来是在强调..." or "从画面上看，可能是在表达...". In English, use phrases such as "This slide appears to emphasize...", "From the visual evidence, it may be suggesting...", or "It seems likely that the intention here is...".

## Presentation Style

- Treat the main per-slide output as the actual script, not advice about how to speak. Use the label "讲稿" in Chinese and "Presentation Script" in English.
- Write like a mature presenter moving through a real presentation: use varied openings, transitions, and emphasis. Avoid starting every slide with formulaic phrases such as "这一页...", "这一页主要...", "This slide...", or "On this slide...".
- Make the script sound like one continuous narrative across the deck. Refer back to previous ideas when useful, and explain why the current page matters in the larger story.
- Keep analytical notes separate from the script. "页面理解 / Slide Reading" can summarize evidence briefly, but the "讲稿 / Presentation Script" should read as spoken presentation language.
- For design portfolios or visual decks, the script should not merely describe visible elements. It should connect visual choices to design intention, user experience, site/context, material atmosphere, and the presenter's role when evidence supports it.
- Use first person only when the source deck or user context supports it, especially for portfolios. Otherwise use neutral phrasing.

## Language Handling

- Use a lightweight language selection flow:
  1. If the user explicitly names a language, use it.
  2. If the user asks in English and does not name a language, generate English notes.
  3. If the user asks in Chinese and does not name a language, generate Chinese notes.
  4. If the user mixes languages and the desired output language is unclear, ask one concise question before generating: "Should I write the speaker notes in English, Chinese, or both?"
- Follow explicit user language requests over inferred language, including requests like "英文讲稿", "English notes", "make it suitable for an English presentation", "for an overseas interview", or "给海外面试用".
- If the deck text is Chinese but the user asks for English notes, translate the meaning naturally instead of mirroring the slide text word for word.
- If the deck text is English but the user asks in Chinese, produce Chinese notes while preserving important English names, terms, brands, and quoted slide titles.
- If the deck text is Chinese but the user asks in English, produce English notes with natural translation and conservative interpretation.
- For English notes, use clear spoken presentation English: concise sentences, natural transitions, and professional but not academic wording.
- Do not invent cultural context, market claims, design rationale, or technical details just to make the English sound polished.

## Output Location

- Determine the final output folder before writing the Markdown notes or PPTX copy.
- If the user gives an output folder, use it.
- If the user does not give an output folder, ask one concise question before final generation, for example:
  - Chinese: "你希望最终的讲稿 Markdown 和带备注 PPTX 保存到哪个文件夹？"
  - English: "Which folder should I save the final Markdown notes and PPTX copy to?"
- Do not ask again if the user has already provided a folder in the same request.
- Use the same final output folder for both:
  - `<deck-name>_speaker_notes.md`
  - `<deck-name>_with_notes.pptx` for PPTX inputs
- Keep temporary render/extraction materials separate from the final output folder unless the user asks to keep debug materials.

## Workflow

1. Determine output language and final output folder. If either is unclear and cannot be safely inferred from the request, ask one concise question before generating final files.

2. Check rendering support before processing design-heavy decks:

```bash
python scripts/check_render_environment.py
```

In Codex Desktop, if regular `python` lacks document/image packages, use the bundled workspace Python runtime when available. It is more likely to include Pillow and PDF text extraction libraries.

Stable visual analysis requires:

- PDF to images: Poppler `pdftoppm` or Python `PyMuPDF` / `fitz`
- PPT/PPTX to PDF: LibreOffice / `soffice`
- GIF previews: Pillow
- Video previews: `ffmpeg` and `ffprobe`

3. Prepare working materials with the bundled script. Use a temporary output folder by default. For design-heavy decks, require rendering:

```bash
python scripts/prepare_ppt_speaker_notes.py INPUT_FILE --output /tmp/ppt-speaker-notes-<deck-name> --require-render
```

4. Inspect `OUTPUT_DIR/manifest.json` and `OUTPUT_DIR/deck_context.md`.
5. If `OUTPUT_DIR/contact_sheets/` contains overview images, inspect them first to understand the deck's structure, rhythm, repeated visual language, and section changes before going page by page.
6. If `OUTPUT_DIR/slides/` contains images, inspect the slide images before writing notes. Visual/design-heavy decks must not be handled from extracted text alone.
   - If `deck_context.md` reports GIF animations or video media, remember that PDF/image export usually captures only a static frame or poster frame. Mention this limitation and avoid over-interpreting motion, timing, sound, interaction, or sequence unless the animated media itself is separately inspected.
   - If `OUTPUT_DIR/animated_previews/` contains keyframe images, inspect those previews for GIF/video pages before writing notes.
7. Build a deck-level understanding before writing per-slide notes:
   - likely audience and purpose
   - narrative arc across sections
   - recurring visual language, product, brand, or scenario
   - what each slide contributes to the flow
8. Generate notes page by page. For design pages, cover:
   - composition and hierarchy
   - style, material, color, lighting, and mood
   - visual focus and user scenario
   - possible design intention and tradeoffs
   - a natural presentation script that explains why the page matters
9. Save the final notes as a standalone Markdown document in the confirmed final output folder unless the user requested another format.
10. For PPTX input, write the final per-slide scripts back into a new PPTX copy in the confirmed final output folder:

```bash
python scripts/write_notes_to_pptx.py INPUT.pptx OUTPUT_FOLDER/<deck-name>_speaker_notes.md --output OUTPUT_FOLDER/<deck-name>_with_notes.pptx
```

11. Clean up temporary material folders after the final Markdown and PPTX copy are verified. Keep the temporary folder only when the user asks for it or when it is needed to explain a rendering limitation.

## If Rendering Is Unavailable

The script attempts automatic rendering, but stable rendering depends on local converters:

- PDF: use Poppler `pdftoppm` or Python `PyMuPDF` / `fitz`.
- PPT/PPTX: use LibreOffice / `soffice` to convert to PDF, then render the PDF.

PowerPoint/Keynote automation may be useful as a local fallback, but it is not considered the stable path because macOS automation permissions and application scripting terminology vary by machine. Check `manifest.json` for `pptx_export_attempts`.

If no slide images are produced:

- Do not pretend to have seen visual content.
- Ask for the render environment to be fixed, or ask for a PDF export/rendered slide images if the deck is visual/design-heavy.
- If PDF text was extracted, use it only as supporting evidence. Clearly state that the visual reading is limited until pages can be rendered as images.
- If the user still wants a text-only draft, clearly label it as text-only and use cautious language.
- For PPTX files with GIFs, embedded videos, or other animations, ask for exported video/GIF assets or a screen recording when motion, sound, timing, or interaction is important.
- If `animated_media/` and `animated_previews/` exist, use them as evidence for animation pages. GIF previews are keyframe contact sheets; video previews require `ffmpeg`/`ffprobe`.

## Notes Format

Use this Chinese structure unless the user asks otherwise or requests English:

```markdown
# <Deck title> 讲稿

## 整体理解
...

## 第 1 页
**页面理解：** ...

**讲稿：**
...

**不确定点：** ...
```

For English notes, use this structure unless the user asks otherwise:

```markdown
# <Deck title> Speaker Notes

## Overall Understanding
...

## Slide 1
**Slide Reading:** ...

**Presentation Script:**
...

**Uncertainties:** ...
```

For bilingual notes, use a predictable side-by-side section structure:

```markdown
## Slide 1
**中文讲稿：**
...

**English Presentation Script:**
...

**不确定点 / Uncertainties:** ...
```

Keep each slide concise enough to present. Avoid turning notes into a dense essay unless the user asks for detailed training material.

## Clean Output

- Default final outputs:
  - `OUTPUT_FOLDER/<deck-name>_speaker_notes.md`
  - `OUTPUT_FOLDER/<deck-name>_with_notes.pptx` for PPTX inputs
- Default temporary materials:
  - `manifest.json`
  - `deck_context.md`
  - rendered slide images
  - contact sheets
  - extracted GIF/video previews
- Store temporary materials outside the user's visible project folder when practical, such as under `/tmp`.
- Delete temporary materials after final verification. Do not delete source presentations or final outputs.
- For PDF input, only produce the Markdown notes unless the user also provides a PPTX to receive notes.

## Safety Rules

- Never delete or overwrite the source presentation.
- Keep generated assets in a temporary or separate output folder, and clean them up by default after final outputs are produced.
- Before writing notes back to PPT, make a duplicate named `<deck-name>_with_notes.pptx`.
- Do not invent facts, metrics, brand claims, product capabilities, or exact design rationale that are not visible in the slide or supported by user-provided context.
- If using outside knowledge, tell the user and cite sources when practical.
