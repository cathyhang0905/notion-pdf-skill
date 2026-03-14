# notion-pdf

A standalone Python tool to import PDFs into Notion as **PPT-style slideshows**. Each page becomes a full-width image block you can scroll through like a presentation.

Also works as a **Claude Code skill** — just copy `SKILL.md` and Claude will handle it conversationally.

## Features

- 📄 Converts every PDF page to a high-quality image
- 🖼️ Inserts pages as image blocks in Notion (scroll like a slideshow)
- 🎨 Auto-generates a unique cover photo (Unsplash) and icon (DiceBear) per document
- 🏷️ Sets title, status, and tags in your Notion database
- 🔐 All API keys loaded from `.env` — nothing hardcoded

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

| Variable | Required | Where to get it |
|---|---|---|
| `NOTION_TOKEN` | ✅ | notion.so → Settings → Connections → Create integration |
| `NOTION_DATABASE_ID` | ✅ | Your database URL: `notion.so/{DATABASE_ID}` |
| `UNSPLASH_ACCESS_KEY` | Optional | [unsplash.com/developers](https://unsplash.com/developers) — for cover images |

### 3. Run

```bash
python3 notion_pdf_import.py "/path/to/file.pdf"
```

That's it. No Claude Code required.

## Usage

```bash
python3 notion_pdf_import.py "/path/to/file.pdf" [options]
```

| Option | Default | Description |
|---|---|---|
| `--title` | filename | Override the Notion page title |
| `--status` | `Want to Read` | `Want to Read` / `Reading` / `Done` |
| `--tags` | — | Comma-separated tags, e.g. `AI,Research` |

**Example:**
```bash
python3 notion_pdf_import.py "~/Downloads/report.pdf" \
  --title "Q1 AI Research Report" \
  --status "Reading" \
  --tags "AI,Research"
```

## Using as a Claude Code Skill (optional)

If you use [Claude Code](https://claude.ai/code), you can install this as a skill so Claude handles it conversationally:

```bash
cp SKILL.md ~/.claude/skills/notion-pdf.md
```

Then just tell Claude:
> "Import this PDF into Notion"

Claude will ask for the file path and run the script automatically.

## How it works

```
PDF file
  └─ PyMuPDF → JPEG images (150 DPI)
       └─ Notion file upload API → hosted image URLs
            └─ Notion API → image blocks in new page
                              + Unsplash cover photo
                              + DiceBear icon
```

## Requirements

- Python 3.9+
- macOS / Linux / Windows
- Free API accounts: Notion, Unsplash (optional)

## License

MIT
