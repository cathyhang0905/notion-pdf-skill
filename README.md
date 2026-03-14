# notion-pdf — Claude Code Skill

Import any PDF into Notion as a **PPT-style slideshow**. Each page becomes a full-width image block you can scroll through like a presentation.

![Demo](https://api.dicebear.com/9.x/adventurer/svg?seed=notion-pdf-demo)

## Features

- 📄 Converts every PDF page to a high-quality image
- 🖼️ Inserts pages as image blocks in Notion (scroll like a slideshow)
- 🎨 Auto-generates a unique cover photo (Unsplash) and icon (DiceBear) per document
- 🏷️ Sets title, status, and tags in your Articles database
- 🔐 All API keys loaded from `.env` — nothing hardcoded

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
```

Edit `.env` and fill in:

| Variable | Where to get it |
|---|---|
| `NOTION_TOKEN` | notion.so → Settings → Connections → Create integration |
| `NOTION_DATABASE_ID` | Your database URL: `notion.so/{DATABASE_ID}` |
| `IMGBB_API_KEY` | [imgbb.com](https://imgbb.com) → Account → API (free) |
| `UNSPLASH_ACCESS_KEY` | [unsplash.com/developers](https://unsplash.com/developers) (optional) |

### 3. Install as a Claude Code skill

Copy or symlink `SKILL.md` to your Claude skills directory:

```bash
cp SKILL.md ~/.claude/skills/notion-pdf.md
```

Then use it in Claude Code by saying:
> "Import this PDF into Notion" or `/notion-pdf`

## Usage

```bash
python3 notion_pdf_import.py "/path/to/file.pdf"
```

### Options

```
--title   "Custom Title"           Override page title (default: filename)
--status  "Reading"                Want to Read | Reading | Done
--tags    "AI,Research"            Comma-separated tags
```

### Example

```bash
python3 notion_pdf_import.py "~/Downloads/report.pdf" \
  --title "Q1 AI Research Report" \
  --status "Want to Read" \
  --tags "AI,Research"
```

## How it works

```
PDF file
  └─ PyMuPDF → JPEG images (150 DPI)
       └─ imgbb → hosted image URLs
            └─ Notion API → image blocks in new page
                              + Unsplash cover
                              + DiceBear icon
```

## Requirements

- Python 3.9+
- macOS / Linux / Windows
- Free API accounts: Notion, imgbb, Unsplash (optional)

## License

MIT
