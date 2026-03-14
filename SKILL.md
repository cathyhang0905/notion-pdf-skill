---
name: notion-pdf
description: Import a PDF into Notion as a PPT-style slideshow. Each page becomes a full-width image block you can scroll through like a presentation.
---

## notion-pdf

Import a PDF file into your Notion database. Each page is converted to an image and inserted as a full-width image block — scroll through like a PPT slideshow.

### Setup

1. Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

When the user asks to import a PDF into Notion, or says something like:
- "Put this PDF into Notion"
- "Import this PDF to my Articles"
- "Add this PDF as a slideshow in Notion"

Run the following, replacing the path and optional flags:

```bash
python3 notion_pdf_import.py "/path/to/file.pdf"
```

**Optional flags:**
```bash
--title "Custom Title"                    # Override the page title (default: filename)
--status "Reading"                        # Want to Read | Reading | Done (default: Want to Read)
--tags "AI,Research"                      # Comma-separated tags
```

**Full example:**
```bash
python3 notion_pdf_import.py "~/Downloads/report.pdf" --title "Q1 Report" --status "Reading" --tags "Research"
```

### What it does

1. Converts each PDF page to a JPEG image (150 DPI)
2. Uploads each page image to Notion via file upload API
3. Creates a new page in your Notion database with title, status, and tags
4. Sets a unique icon via DiceBear (auto-generated from title)
5. Sets a cover photo from Unsplash (optional — skipped if `UNSPLASH_ACCESS_KEY` not set)
6. Inserts all page images as full-width image blocks (PPT-style)

### Notes

- `UNSPLASH_ACCESS_KEY` is optional — cover image is skipped if not set
- Large PDFs (>5 MB) are handled by converting to images instead of uploading the raw file
- Each page image is deterministically linked to the title, so re-running produces the same cover/icon
