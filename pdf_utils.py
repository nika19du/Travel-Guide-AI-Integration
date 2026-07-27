import re
from pathlib import Path

import fitz

import rag_service

SECTION_HEADINGS = (
    "Best Time to Visit",
    "Worst Time to Visit",
    "Cheapest Time to Visit"
)

def extract_pdf_pages(pdf_path: str) -> list[dict]:
    path = Path(pdf_path)
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f'PDF not found: {pdf_path}')

    document = fitz.open(path)

    try:
        pages = []
        for page_index,page in enumerate(document):
            text = page.get_text("text").strip()

            if text:
                pages.append({'page': page_index+1, 'text': text})

        return pages
    finally:
        document.close()

def split_text(
    text: str,
    chunk_size: int = 1200,
    chunk_overlap: int = 200
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size."
        )

    if not text or not text.strip():
        return []

    sections = split_by_headings(text)

    chunks = []

    for section in sections:
        chunks.extend(
            split_by_size(
                text = section,
                chunk_size = chunk_size,
                chunk_overlap = chunk_overlap
            )
        )

    return chunks

def split_by_headings(text: str) -> list[str]:
    headings_pattern = "|".join(
        re.escape(heading) for heading in SECTION_HEADINGS
    )

    pattern = rf"(?=^(?:{headings_pattern})\s*$)"

    sections = re.split(
        pattern,
        text,
        flags=re.IGNORECASE | re.MULTILINE
    )

    return [
        section.strip()
        for section in sections
        if section.strip()
    ]

def split_by_size(
    text: str,
    chunk_size: int,
    chunk_overlap: int
) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    step = chunk_size - chunk_overlap

    for start in range(0, len(text), step):
        chunk = text [
            start: start + chunk_size
        ].strip()

        if chunk:
            chunks.append(chunk)
    return chunks