# ppt-speaker-notes

A Codex skill for generating natural speaker notes from old PPT/PPTX/PDF slide decks.

It is especially useful for visual or design-heavy presentations where slide text alone is not enough. The skill prepares deck context, renders slides when possible, inspects visual materials conservatively, generates a speaker-notes Markdown file, and can write the per-slide script back into a safe PPTX copy.

## Features

- Generate speaker notes for `.pptx`, `.ppt`, and `.pdf` decks.
- For visual PPT/PPTX decks, recommend providing the original PPT/PPTX together with a matching PDF export.
- Follow the user's request language by default:
  - English request -> English speaker notes.
  - Chinese request -> Chinese speaker notes.
  - Explicit bilingual request -> bilingual notes.
- Tune the script by presentation profile:
  - Role: student, teacher, designer, or working professional.
  - Discipline: architecture and interior design, interaction design, visual communication, art design, graphic design, or brand design.
  - Scenario: formal presentation, classroom teaching, portfolio defense, or casual sharing.
- Analyze the whole deck context before writing per-slide scripts.
- Render PDF pages to slide images when local tools are available.
- Extract GIF keyframes and video preview frames when possible.
- Avoid PowerPoint, Keynote, LibreOffice, and `soffice` conversion by default.
- Use conservative wording when visual meaning is uncertain.
- Keep intermediate files temporary by default.
- Never overwrite the original deck.
- For PPTX input, create a new `<deck-name>_with_notes.pptx` copy with speaker notes inserted into each slide.

## Install

Clone or download this repository, then copy the folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R ppt-speaker-notes ~/.codex/skills/ppt-speaker-notes
```

Restart Codex or start a new Codex session so the skill can be discovered.

## Basic Usage

English:

```text
Use ppt-speaker-notes to generate English speaker notes for this deck: my-presentation.pptx
```

Chinese:

```text
用 ppt-speaker-notes 给这个 PPT 生成中文讲稿：我的作品集.pptx
```

Bilingual:

```text
Use ppt-speaker-notes to create bilingual speaker notes for this presentation.
```

With role, discipline, and scenario:

```text
Use ppt-speaker-notes to generate English speaker notes for this deck.
Role: designer.
Discipline: brand design.
Scenario: formal presentation.
Save the outputs to ~/Desktop.
```

Chinese example:

```text
用 ppt-speaker-notes 给这个作品集生成中文讲稿。
角色：学生。
专业：建筑及室内设计。
场景：作品集答辩。
保存到桌面。
```

Best visual-accuracy setup:

```text
Use ppt-speaker-notes with these two files:
- portfolio.pptx
- portfolio.pdf

Use the PDF for visual analysis and write the notes back into a new PPTX copy.
```

You can also specify an output folder:

```text
Use ppt-speaker-notes to generate English speaker notes for this deck and save the outputs to ~/Desktop/notes-output.
```

If you do not specify role, discipline, scenario, or output folder, the skill will ask step by step before creating the final files:

1. Role
2. Discipline
3. Scenario
4. Output folder

It should ask only one question at a time, so the setup feels like a short guided flow instead of a long form.

## Presentation Profiles

The role, discipline, and scenario change both the tone and the organization of the script.

Role:

- Student: more reflective and process-aware.
- Teacher: more explanatory and structured.
- Designer: more professional, intention-led, and tradeoff-aware.
- Working professional: more concise, goal-oriented, and stakeholder-aware.

Discipline:

- Architecture and interior design: site, spatial sequence, circulation, material, scale, light, atmosphere, and user scenario.
- Interaction design: user needs, tasks, flows, information architecture, feedback, states, usability, and accessibility.
- Visual communication: message hierarchy, typography, layout, media, image rhythm, and audience perception.
- Art design: concept, medium, form, sensory experience, cultural reference, and interpretation.
- Graphic design: grid, typography, composition, contrast, color system, print/screen context, and information clarity.
- Brand design: positioning, identity system, brand personality, touchpoints, campaign context, recognition, and brand experience.

Scenario:

- Formal presentation: polished, structured, and confident.
- Classroom teaching: slower, clearer, and more explanatory.
- Portfolio defense: focused on contribution, process, decisions, outcome, and reflection.
- Casual sharing: warmer, lighter, and more conversational.

## Output

For PPTX input, the default final outputs are:

```text
<deck-name>_speaker_notes.md
<deck-name>_with_notes.pptx
```

For PDF input, the default final output is:

```text
<deck-name>_speaker_notes.md
```

PDF files do not have PowerPoint speaker-note fields, so writing notes back requires a PPTX source file.

## PPTX + Matching PDF

For image-heavy or design-heavy presentations, the recommended input is:

```text
deck.pptx
deck.pdf
```

Why this helps:

- The PDF gives the most stable per-slide visual reference.
- The PPTX lets the skill write the generated script back into speaker notes.
- This avoids relying on PowerPoint or Keynote automation.
- It also avoids generating visual analysis from extracted text alone.

When both files are provided, the skill should render and inspect the PDF, then insert the final per-slide notes into a safe `_with_notes.pptx` copy.

If only a PPT/PPTX is provided, the skill should remind the user to provide a matching PDF before visual/design analysis. It should not use LibreOffice/`soffice` to convert the PPT/PPTX.

## Recommended Environment

The skill can extract text without all rendering tools, but visual understanding requires rendered PDF page images.

For the most reliable no-popup workflow, provide both files when you want notes written back:

```text
deck.pdf   -> visual analysis
deck.pptx  -> speaker-note insertion
```

Recommended on macOS with Homebrew:

```bash
brew install poppler
brew install ffmpeg
```

Optional Python packages:

```bash
python3 -m pip install PyMuPDF pypdf Pillow
```

Tool roles:

- Poppler `pdftoppm`: render PDF pages to images.
- ffmpeg/ffprobe: extract video preview frames.
- Pillow: create GIF keyframe sheets and contact sheets.
- pypdf: extract PDF text when rendering is unavailable.

For visual/design-heavy decks, rendering is required. The skill should run:

```bash
python scripts/prepare_ppt_speaker_notes.py INPUT_FILE --output OUTPUT_DIR --require-render
```

If the environment cannot produce per-page slide images, this command should fail clearly instead of silently producing a text-only visual analysis. A text-only draft should be generated only when the user explicitly asks for one after seeing the limitation.

## No-Popup Workflow

The skill is designed to avoid interactive PowerPoint or Keynote automation by default.

Recommended path for PPT/PPTX:

1. The user provides a matching PDF exported from the presentation.
2. Poppler or PyMuPDF renders the PDF into slide images.
3. Codex analyzes the rendered PDF pages and writes the speaker notes Markdown.
4. If a PPTX is also provided, the script creates a new `_with_notes.pptx` copy with notes inserted.

The skill should not call LibreOffice/`soffice` to convert PPT/PPTX files. This avoids app crashes, layout drift, and macOS permission prompts. PowerPoint/Keynote automation should only be used if the user explicitly accepts possible permission prompts.

Stable no-popup rendering requirements:

- `brew install poppler`
- `brew install ffmpeg`

GIF keyframes use Python/Pillow. Video keyframes use ffmpeg.

## Safety

The skill is designed to avoid destructive edits:

- It does not overwrite the original PPT/PPTX/PDF.
- It creates a new `_with_notes.pptx` copy for PPTX inputs.
- It keeps intermediate render/extraction materials temporary by default.
- It uses conservative language when slide meaning is uncertain.

## Notes For Visual And Design Decks

For design-heavy decks, the skill should not rely on extracted text alone. It should inspect rendered slide images whenever possible and consider:

- composition and visual hierarchy
- style, material, color, lighting, and mood
- visual focus and user scenario
- likely design intention and tradeoffs
- how the slide fits into the whole deck narrative

When evidence is uncertain, it should say so rather than inventing details.
