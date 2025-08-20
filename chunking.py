#!/usr/bin/env python3
"""
Step 1 — Portfolio Ingestion & Section-based Chunking
-----------------------------------------------------
This script ingests your portfolio .txt file and creates chunks based on sections
like Experience, Technical Skills, Soft Skills, and Projects instead of splitting
by character length.

Usage:
  python ingest_portfolio.py

Input:
  portfolio.txt   # your single portfolio file

Output:
  chunks.jsonl    # JSON Lines file where each line is a section chunk
  {
    "id": "chunk-Experience-abc12345",
    "text": "...",                # section text
    "metadata": {
        "source": "portfolio.txt",
        "section": "Experience"
    }
  }
"""

import json
import re
import hashlib
from pathlib import Path


# ---------- Helpers ----------
def normalize_whitespace(text: str) -> str:
    """Clean up whitespace and newlines."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)  # collapse many newlines
    text = re.sub(r"[ \u00A0]{2,}", " ", text)  # collapse multiple spaces
    return text.strip()


def stable_id(section: str, text: str) -> str:
    """Create stable ID from section name + hash of text."""
    h = hashlib.sha1(text.encode("utf-8")).hexdigest()
    return f"chunk-{section}-{h[:8]}"


def split_by_sections(text: str):
    """
    Split portfolio text into predefined sections:
    - Experience
    - Technical Skills
    - Soft Skills
    - Projects
    """
    sections = ["Introduction","Experience", "Skills", "Soft Skills","Certifications","Education", "Projects","Contact"]
    chunks = {}
    current_section = None
    buffer = []

    for line in text.splitlines():
        line_stripped = line.strip()

        if not line_stripped:
            continue

        # Check if line matches a section heading
        matched_section = None
        for sec in sections:
            if line_stripped.lower().startswith(sec.lower()):
                matched_section = sec
                break

        if matched_section:
            # save previous section if any
            if current_section and buffer:
                chunks[current_section] = "\n".join(buffer).strip()
            current_section = matched_section
            buffer = [line_stripped]
        else:
            buffer.append(line_stripped)

    # save last section
    if current_section and buffer:
        chunks[current_section] = "\n".join(buffer).strip()

    return chunks


def process_txt_file(input_path: str, out_path: str):
    """Process the portfolio.txt into section-based chunks."""
    text = Path(input_path).read_text(encoding="utf-8", errors="ignore")
    text = normalize_whitespace(text)
    sections = split_by_sections(text)

    with open(out_path, "w", encoding="utf-8") as f:
        for sec, content in sections.items():
            record = {
                "id": stable_id(sec, content),
                "text": content,
                "metadata": {
                    "source": Path(input_path).name,
                    "section": sec
                }
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"✅ Wrote {len(sections)} section chunks to {out_path}")


# ---------- Main ----------
if __name__ == "__main__":
    process_txt_file("portfolio.txt", "chunks.jsonl")
