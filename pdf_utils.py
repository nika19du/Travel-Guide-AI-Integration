from pathlib import Path

import fitz

def extract_pdf_pages(pdf_path: str) -> list[dict]:
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

    chunks = []
    step = chunk_size - chunk_overlap

    for start in range(0, len(text), chunk_size):
        chunk = text[start:start+chunk_size].strip()

        if chunk:
            chunks.append(chunk)

    return chunks