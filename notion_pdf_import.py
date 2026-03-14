#!/usr/bin/env python3
"""
notion_pdf_import.py
Import a PDF into Notion Articles database as a PPT-style slideshow.
Each page becomes an image block — scroll through like a presentation.

Usage:
    python3 notion_pdf_import.py "/path/to/file.pdf"
    python3 notion_pdf_import.py "/path/to/file.pdf" --title "Custom Title" --status "Reading" --tags "AI"

Requirements:
    pip install notion-client requests PyMuPDF python-dotenv

Environment variables (set in .env or shell):
    NOTION_TOKEN         — Notion integration token (required)
    NOTION_DATABASE_ID   — Target Notion database ID (required)
    UNSPLASH_ACCESS_KEY  — Unsplash API key for cover images (optional)
"""

import argparse
import hashlib
import io
import os
import sys
import time

import fitz
import requests
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

# ─── Config from environment ──────────────────────────────────────────────────

NOTION_TOKEN        = os.environ.get("NOTION_TOKEN")
DATABASE_ID         = os.environ.get("NOTION_DATABASE_ID")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")  # optional

IMAGE_DPI    = 150
JPEG_QUALITY = 85

ICON_STYLES = [
    "adventurer", "fun-emoji", "lorelei", "bottts", "micah",
    "thumbs", "adventurer-neutral", "croodles", "pixel-art", "notionists",
]
VISUAL_QUERIES = [
    "misty mountain minimal", "abstract architecture light", "ocean waves aerial view",
    "forest sunlight minimal", "desert landscape aerial", "geometric minimal abstract",
    "city skyline dusk", "white marble texture", "neon light abstract",
    "autumn leaves minimal", "concrete texture urban", "lake reflection minimal",
    "dark abstract gradient", "cherry blossom minimal", "sand dunes aerial",
    "night sky stars", "green moss texture", "vintage paper texture",
    "rainy window blur", "wooden texture minimal", "fog mountain landscape",
    "black white architecture", "coral reef underwater", "snow landscape minimal",
    "industrial loft interior", "tropical leaf minimal", "sunrise horizon minimal",
    "glass reflection abstract", "stone wall texture", "wildflower field aerial",
]

# ──────────────────────────────────────────────────────────────────────────────


def check_env():
    missing = [k for k in ["NOTION_TOKEN", "NOTION_DATABASE_ID"]
               if not os.environ.get(k)]
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("   Copy .env.example to .env and fill in your keys.")
        sys.exit(1)


def pdf_to_images(pdf_path: str) -> list:
    """Convert each PDF page to JPEG bytes."""
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=IMAGE_DPI, alpha=False)
        images.append(pix.tobytes("jpeg", jpg_quality=JPEG_QUALITY))
    return images


def upload_image_to_notion(image_bytes: bytes, filename: str) -> str:
    """Upload image bytes to Notion file upload API, return file_upload_id."""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
    }

    # Step 1: Create upload session
    r1 = requests.post(
        "https://api.notion.com/v1/file_uploads",
        headers={**headers, "Content-Type": "application/json"},
        json={"filename": filename, "content_type": "image/jpeg"},
        timeout=15,
    )
    r1.raise_for_status()
    data = r1.json()
    upload_url = data["upload_url"]
    file_upload_id = data["id"]

    # Step 2: Upload file bytes
    r2 = requests.post(
        upload_url,
        headers=headers,
        files={"file": (filename, io.BytesIO(image_bytes), "image/jpeg")},
        timeout=30,
    )
    r2.raise_for_status()

    return file_upload_id


def get_cover_url(title: str) -> str | None:
    """Fetch a unique cover photo from Unsplash based on title hash."""
    if not UNSPLASH_ACCESS_KEY:
        return None
    h = int(hashlib.md5(title.encode()).hexdigest(), 16)
    query = VISUAL_QUERIES[h % len(VISUAL_QUERIES)]
    result_index = (h >> 32) % 10
    try:
        resp = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": query, "orientation": "landscape", "per_page": 15},
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            timeout=15,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if results:
            return results[min(result_index, len(results) - 1)]["urls"]["regular"]
    except Exception:
        pass
    return None


def get_icon_url(title: str) -> str:
    """Generate a unique DiceBear icon URL based on title hash."""
    h = int(hashlib.md5(title.encode()).hexdigest(), 16)
    style = ICON_STYLES[h % len(ICON_STYLES)]
    seed = hashlib.md5((title + "icon").encode()).hexdigest()
    return f"https://api.dicebear.com/9.x/{style}/svg?seed={seed}"


def main():
    check_env()

    parser = argparse.ArgumentParser(
        description="Import a PDF into Notion as a PPT-style slideshow"
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--title", help="Page title (defaults to filename)")
    parser.add_argument("--status", default="Want to Read",
                        choices=["Want to Read", "Reading", "Done"])
    parser.add_argument("--tags", default="", help="Comma-separated tags, e.g. AI,Research")
    args = parser.parse_args()

    pdf_path = os.path.expanduser(args.pdf_path)
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)

    title = args.title or os.path.splitext(os.path.basename(pdf_path))[0]
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    print(f"📄 File:   {os.path.basename(pdf_path)}")
    print(f"📝 Title:  {title}")
    print(f"🏷  Status: {args.status}  Tags: {tags or 'none'}\n")

    notion = Client(auth=NOTION_TOKEN)

    # Step 1: Convert PDF to images
    print("🔄 [1/4] Converting PDF pages to images...")
    images = pdf_to_images(pdf_path)
    print(f"   {len(images)} pages found")

    # Step 2: Upload images to Notion
    print("☁️  [2/4] Uploading images to Notion...")
    file_upload_ids = []
    for i, img_bytes in enumerate(images):
        uid = upload_image_to_notion(img_bytes, f"page_{i+1}.jpg")
        file_upload_ids.append(uid)
        print(f"   Page {i+1}/{len(images)} ✅")
        time.sleep(0.2)

    # Step 3: Cover & icon
    print("🎨 [3/4] Fetching cover and icon...")
    cover_url = get_cover_url(title)
    icon_url = get_icon_url(title)

    # Step 4: Create Notion page
    print("📋 [4/4] Creating Notion page...")

    create_kwargs = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "Status": {"select": {"name": args.status}},
            "Source Type": {"select": {"name": "Paper"}},
        },
        "icon": {"type": "external", "external": {"url": icon_url}},
    }
    if cover_url:
        create_kwargs["cover"] = {"type": "external", "external": {"url": cover_url}}
    if tags:
        create_kwargs["properties"]["Tags"] = {
            "multi_select": [{"name": t} for t in tags]
        }

    page = notion.pages.create(**create_kwargs)
    page_id = page["id"]
    page_url = page["url"]

    # Insert image blocks (max 50 per request)
    image_blocks = [
        {
            "object": "block",
            "type": "image",
            "image": {"type": "file_upload", "file_upload": {"id": uid}},
        }
        for uid in file_upload_ids
    ]
    for i in range(0, len(image_blocks), 50):
        notion.blocks.children.append(
            block_id=page_id,
            children=image_blocks[i:i+50]
        )

    print(f"\n🎉 Done! {len(images)} pages imported.")
    print(f"   → {page_url}")


if __name__ == "__main__":
    main()
