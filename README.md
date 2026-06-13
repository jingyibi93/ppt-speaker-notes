# ppt-speaker-notes

A Codex skill for generating natural speaker notes from old PPT/PPTX/PDF slide decks.

It is especially useful for visual or design-heavy presentations where slide text alone is not enough. The skill prepares deck context, renders slides when possible, inspects visual materials conservatively, generates a speaker-notes Markdown file, and can write the per-slide script back into a safe PPTX copy.

## Features

- Generate speaker notes for `.pptx`, `.ppt`, and `.pdf` decks.
- Follow the user's request language by default:
  - English request -> English speaker notes.
  - Chinese request -> Chinese speaker notes.
  - Explicit bilingual request -> bilingual notes.
- Analyze the whole deck context before writing per-slide scripts.
- Render slides to images when local tools are available.
- Extract GIF keyframes and video preview frames when possible.
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

You can also specify an output folder:

```text
Use ppt-speaker-notes to generate English speaker notes for this deck and save the outputs to ~/Desktop/notes-output.
```

If you do not specify an output folder, the skill will ask where to save the final Markdown and PPTX copy.

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

## Recommended Environment

The skill can extract text without all rendering tools, but visual understanding is much better when slides can be rendered to images.

Recommended on macOS with Homebrew:

```bash
brew install poppler
brew install --cask libreoffice
brew install ffmpeg
```

Optional Python packages:

```bash
python3 -m pip install PyMuPDF pypdf Pillow
```

Tool roles:

- Poppler `pdftoppm`: render PDF pages to images.
- LibreOffice `soffice`: convert PPT/PPTX to PDF.
- ffmpeg/ffprobe: extract video preview frames.
- Pillow: create GIF keyframe sheets and contact sheets.
- pypdf: extract PDF text when rendering is unavailable.

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

