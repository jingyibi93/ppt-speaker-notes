# pptxNoteMaster Review

Repository checked: `https://github.com/marlinpohlman/pptxNoteMaster`

## Summary

- It is a Vite/React front-end app, not a Codex skill.
- It uses Gemini through `@google/genai`.
- It accepts `.pptx` and `.pdf`.
- PDF pages are rendered in the browser.
- PPTX slides are text-extracted with JSZip but not rendered to images.
- It can create a new PPTX with `slide.addNotes(...)`.

## Fit For Design-Heavy Decks

Not ideal as-is. PPTX image-heavy pages become text-only, so the approach is weak for design portfolios, visual concept decks, and animation-heavy presentations.

## Borrowed Lessons

- Generate a new output file rather than overwriting the original.
- Keep per-slide progress and editable notes.
- Use rendered page images whenever visual interpretation matters.
