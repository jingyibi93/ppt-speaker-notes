---
name: ppt-speaker-notes
description: Generate natural speaker notes or narration drafts for old PPT/PPTX/PDF slide decks, especially visual/design-heavy presentations. Use when the user wants Codex to analyze the whole deck context, render slides to images when possible, interpret design intent conservatively, choose Chinese/English/bilingual output from the user's request language or explicit language choice, adapt tone and terminology by presenter role, design discipline, and presentation scenario, and produce an independent notes document or a safe copy instead of overwriting the original presentation.
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

## No-Popup Rendering Policy

- Default to a non-interactive pipeline. Do not use PowerPoint or Keynote GUI automation for PPT/PPTX rendering unless the user explicitly requests it after being warned that macOS may show file-access authorization dialogs.
- Do not use LibreOffice/`soffice` to convert PPT/PPTX files for visual analysis. The preferred stable path is user-provided PDF rendering, because it avoids app crashes, layout drift, and macOS permission popups.
- For PPT/PPTX decks that need visual understanding, remind the user to provide a matching PDF exported from the same presentation. Use that PDF for slide-image analysis.
- If Poppler and PyMuPDF are both missing for PDF rendering, ask to install Poppler or PyMuPDF before claiming visual analysis.
- Use PowerPoint/Keynote automation only as an opt-in fallback for users who accept possible popups, timeouts, and local permission prompts.
- For visual/design-heavy decks, rendering is mandatory. Always call `scripts/prepare_ppt_speaker_notes.py` with `--require-render`. If it fails, stop and report the missing render dependencies; do not generate a visually framed speaker script from text alone.

## PPT + PDF Pairing

- When the user provides a PPT/PPTX for a visual/design-heavy deck, remind them that the best input is the original PPT/PPTX plus an exported PDF from the same deck.
- Explain the pairing clearly:
  - Use the PDF for stable per-slide visual understanding.
  - Use the PPT/PPTX for extracting structure and writing notes back into a new `_with_notes.pptx` copy.
- If the user provides both PPT/PPTX and a matching PDF, prefer the PDF for rendering and visual analysis, and use the PPT/PPTX only for text/notes extraction and speaker-note insertion.
- If the user provides only PPT/PPTX and needs visual/design analysis, pause and ask for the matching PDF before producing visual speaker notes. Do not try to convert the PPT/PPTX with LibreOffice/`soffice`.
- Do not require a PDF for text-only drafts, but clearly label the output as text-only if no rendered pages were used.
- Suggested Chinese reminder when only PPT/PPTX is provided: "为了保证视觉理解准确率，请同时提供这份 PPT 导出的同名 PDF。我会用 PDF 看每页画面；如果你需要把讲稿写入备注，再用 PPTX 生成新的带备注副本。"
- Suggested English reminder when only PPT/PPTX is provided: "For reliable visual analysis, please also provide a matching PDF exported from this presentation. I will use the PDF for slide-image analysis, and use the PPTX only when you want the script written back into speaker notes."

## Presentation Profile

Before writing the final notes, determine a presentation profile. The profile affects tone, content organization, and professional terminology.

- Role options:
  - Student: reflective, process-aware, able to explain learning, research, iteration, and design decisions without sounding overly senior.
  - Teacher: explanatory and structured, with more context-setting and concept clarification. Use this only when the user explicitly chooses teacher or the deck is clearly for teaching.
  - Designer: professional, intention-led, focused on rationale, craft, user or audience impact, and design tradeoffs.
  - Working professional: concise, outcome-oriented, stakeholder-aware, with clearer links to goals, constraints, collaboration, and next steps.
- Discipline options:
  - Architecture and interior design: emphasize site/context, spatial sequence, circulation, scale, program, material, structure, atmosphere, light, construction logic, and user scenario.
  - Interaction design: emphasize user needs, tasks, journey, information architecture, interaction flow, feedback, states, usability, accessibility, and product experience.
  - Visual communication: emphasize message hierarchy, visual rhythm, typography, imagery, layout, media, audience perception, and communication effectiveness.
  - Art design: emphasize concept, medium, form, sensory experience, cultural reference, expression, installation or object relationship, and interpretive openness.
  - Graphic design: emphasize grid, typography, composition, contrast, color system, print or screen context, information clarity, and visual consistency.
  - Brand design: emphasize positioning, brand personality, identity system, logo/type/color rules, touchpoints, campaign context, recognition, and brand experience.
- Scenario options:
  - Formal presentation: polished, structured, confident, concise, and suitable for review panels or clients.
  - Classroom teaching: explanatory, slower-paced, with more definition, comparison, and step-by-step reasoning.
  - Portfolio defense: first-person when supported, focused on personal contribution, design process, decisions, results, reflection, and ability.
  - Casual sharing: warmer, lighter, more conversational, with less rigid structure and simpler transitions.
- Infer the profile from the user's request only when it is explicit or strongly implied, such as "for portfolio defense", "for class lecture", "as a brand designer", or "teacher notes".
- If any of role, discipline, scenario, or final output folder is unclear, use a step-by-step selection flow instead of asking for everything at once. Ask only one question at a time, wait for the user's answer, then ask the next missing question.
- Use this Chinese step-by-step flow when the user is working in Chinese:
  1. "请选择讲稿适用的角色：学生 / 老师 / 设计师 / 职场人"
  2. "请选择专业方向：建筑及室内设计 / 交互设计 / 视觉传达 / 艺术设计 / 平面设计 / 品牌设计"
  3. "请选择使用场景：正式汇报 / 课堂讲解 / 作品集答辩 / 轻松分享"
  4. "请选择最终文件保存位置，例如：桌面、原文件同级文件夹，或你指定的文件夹路径。"
- Use this English step-by-step flow when the user is working in English:
  1. "Choose the presenter role: student / teacher / designer / working professional"
  2. "Choose the design discipline: architecture and interior design / interaction design / visual communication / art design / graphic design / brand design"
  3. "Choose the presentation scenario: formal presentation / classroom teaching / portfolio defense / casual sharing"
  4. "Choose the final output folder, for example: Desktop, same folder as the source deck, or a specific folder path."
- If the user already provides one or more choices, do not ask those again. Continue with the next missing step only.
- Do not let the profile override evidence. Use discipline-specific terminology only when the slide content supports it.
- If the user asks to proceed without choosing, default to Designer + Architecture and interior design + Formal presentation for design-heavy spatial decks, or Designer + Visual communication + Formal presentation for general visual/design decks.

## Presentation Style

- Treat the main per-slide output as the actual script, not advice about how to speak. Use the label "讲稿" in Chinese and "Presentation Script" in English.
- Write like a mature presenter moving through a real presentation: use varied openings, transitions, and emphasis. Avoid starting every slide with formulaic phrases such as "这一页...", "这一页主要...", "This slide...", or "On this slide...".
- Make the script sound like one continuous narrative across the deck. Refer back to previous ideas when useful, and explain why the current page matters in the larger story.
- Keep analytical notes separate from the script. "页面理解 / Slide Reading" can summarize evidence briefly, but the "讲稿 / Presentation Script" should read as spoken presentation language.
- For design portfolios or visual decks, the script should not merely describe visible elements. It should connect visual choices to design intention, user experience, site/context, material atmosphere, and the presenter's role when evidence supports it.
- Use first person only when the source deck or user context supports it, especially for portfolios. Otherwise use neutral phrasing.
- Shape the per-slide organization around the selected profile:
  - Formal presentations should move from context to problem, strategy, evidence, and value.
  - Classroom teaching should move from concept explanation to examples, comparison, and takeaway.
  - Portfolio defenses should move from brief context to personal role, process, decision, outcome, and reflection.
  - Casual sharing should move from observation to story, experience, and simple takeaway.
- Match terminology to the selected discipline. Prefer precise professional terms over generic praise, but avoid jargon stacking. When uncertain, use softer phrases such as "it reads as", "it appears to", or "the design seems to".

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
- If the user does not give an output folder, ask for it as the final step of the Presentation Profile selection flow. Do not combine this question with role, discipline, or scenario selection.
- Do not ask again if the user has already provided a folder in the same request.
- Use the same final output folder for both:
  - `<deck-name>_speaker_notes.md`
  - `<deck-name>_with_notes.pptx` for PPTX inputs
- Keep temporary render/extraction materials separate from the final output folder unless the user asks to keep debug materials.

## Dependency Guidance

- Always run `scripts/check_render_environment.py` before processing a deck that needs visual analysis.
- If dependencies are missing, explain what capability is unavailable in plain language:
  - Missing Poppler/PyMuPDF means PDF pages may not render to images.
  - Missing ffmpeg/ffprobe means embedded video previews may not be extracted.
  - Missing Pillow means GIF keyframe sheets and contact sheets may not be created.
- Provide installation guidance when useful, but do not install dependencies unless the user explicitly approves installation.
- If the user wants help installing dependencies, ask for confirmation before running install commands.
- Recommended macOS commands:

```bash
brew install poppler
brew install ffmpeg
python3 -m pip install PyMuPDF pypdf Pillow
```

- For a no-popup workflow on macOS, ask the user to provide a PDF export for visual analysis. Poppler or PyMuPDF is required for stable PDF-to-image rendering. PPTX is only needed when notes should be written back into a new `_with_notes.pptx` copy. ffmpeg is required only for video previews.
- For design-heavy or visual analysis requests, do not continue as a text-only draft when rendering fails unless the user explicitly changes the task to "text-only". The default behavior is to fail clearly and ask to fix the render environment.
- If the user explicitly requests a text-only draft after a render failure, clearly label limitations such as "text-only draft; visual analysis not performed".

## Workflow

1. Determine output language, presentation profile, and final output folder. The presentation profile must include role, discipline, and scenario. If role, discipline, scenario, or output folder is missing, ask for the missing items step by step in this order: role, discipline, scenario, output folder. Ask only one question per assistant turn unless the user explicitly asks to provide all choices at once.

2. If the input is PPT/PPTX and the request depends on visual understanding, check whether the user also provided a matching PDF. If yes, use the PDF for rendering and visual analysis while keeping the PPTX for note insertion. If no, ask the user to provide a matching PDF before producing visual speaker notes. Do not use LibreOffice/`soffice` to convert the PPT/PPTX.

3. Check rendering support before processing design-heavy decks:

```bash
python scripts/check_render_environment.py
```

In Codex Desktop, if regular `python` lacks document/image packages, use the bundled workspace Python runtime when available. It is more likely to include Pillow and PDF text extraction libraries.

If the environment check reports missing tools, follow the Dependency Guidance section before deciding whether to continue, ask for installation approval, or produce a limited draft.

Stable visual analysis requires:

- PDF to images: Poppler `pdftoppm` or Python `PyMuPDF` / `fitz`
- PPT/PPTX visual analysis: matching user-provided PDF from the same deck
- GIF previews: Pillow
- Video previews: `ffmpeg` and `ffprobe`

4. Prepare working materials with the bundled script. Use a temporary output folder by default. For design-heavy decks or any request that depends on visual understanding, require rendering. If a matching PDF is available, run preparation on the PDF for visual materials:

```bash
python scripts/prepare_ppt_speaker_notes.py INPUT_FILE --output /tmp/ppt-speaker-notes-<deck-name> --require-render
```

If this command exits nonzero because no per-page images were produced, stop. Report the missing dependencies from stderr and do not produce final notes unless the user explicitly asks for a text-only fallback.

5. Inspect `OUTPUT_DIR/manifest.json` and `OUTPUT_DIR/deck_context.md`.
6. If `OUTPUT_DIR/contact_sheets/` contains overview images, inspect them first to understand the deck's structure, rhythm, repeated visual language, and section changes before going page by page.
7. If `OUTPUT_DIR/slides/` contains images, inspect the slide images before writing notes. Visual/design-heavy decks must not be handled from extracted text alone.
   - If `deck_context.md` reports GIF animations or video media, remember that PDF/image export usually captures only a static frame or poster frame. Mention this limitation and avoid over-interpreting motion, timing, sound, interaction, or sequence unless the animated media itself is separately inspected.
   - If `OUTPUT_DIR/animated_previews/` contains keyframe images, inspect those previews for GIF/video pages before writing notes.
8. Build a deck-level understanding before writing per-slide notes:
   - likely audience and purpose
   - selected or inferred role, discipline, and scenario
   - narrative arc across sections
   - recurring visual language, product, brand, or scenario
   - what each slide contributes to the flow
9. Generate notes page by page. For design pages, cover:
   - composition and hierarchy
   - style, material, color, lighting, and mood
   - visual focus and user scenario
   - possible design intention and tradeoffs
   - terminology and content structure appropriate to the selected discipline
   - a natural presentation script that explains why the page matters
10. Save the final notes as a standalone Markdown document in the confirmed final output folder unless the user requested another format.
11. For PPTX input, write the final per-slide scripts back into a new PPTX copy in the confirmed final output folder:

```bash
python scripts/write_notes_to_pptx.py INPUT.pptx OUTPUT_FOLDER/<deck-name>_speaker_notes.md --output OUTPUT_FOLDER/<deck-name>_with_notes.pptx
```

12. Clean up temporary material folders after the final Markdown and PPTX copy are verified. Keep the temporary folder only when the user asks for it or when it is needed to explain a rendering limitation.

## If Rendering Is Unavailable

The script attempts rendering only for PDF inputs. Stable rendering depends on local PDF renderers:

- PDF: use Poppler `pdftoppm` or Python `PyMuPDF` / `fitz`.
- PPT/PPTX: provide a matching PDF for visual analysis; use PPTX only for text extraction, media extraction, and writing notes back.

PowerPoint/Keynote automation may be useful as a local fallback, but it is not considered the stable path because macOS automation permissions and application scripting terminology vary by machine. LibreOffice/`soffice` conversion is not part of this skill's default workflow.

If no slide images are produced:

- Do not pretend to have seen visual content.
- For PDF input, ask for the PDF render environment to be fixed.
- For PPT/PPTX input, ask for a matching PDF from the same presentation. If the user also needs notes written back, keep the PPTX for note insertion.
- If `--require-render` was used, treat missing slide images as a blocking failure for visual/design-heavy decks.
- If PDF/PPT text was extracted, use it only as supporting evidence after the user explicitly requests a text-only fallback. Clearly state that visual reading was not performed.
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
