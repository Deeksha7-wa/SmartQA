import re

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120):
    """
    Universal chunking for:
    - CVs (FIXED)
    - PDFs
    - Articles
    - Research papers
    """

    text = clean_text(text)

    # 🔥 STEP 1: PRIORITIZE STRUCTURE (CV FIX)
    structured_splits = re.split(
        r'(WORK EXPERIENCE|EDUCATION|SKILLS|PROJECTS|EXPERIENCE)',
        text,
        flags=re.IGNORECASE
    )

    chunks = []
    buffer = ""

    # 🔥 STEP 2: preserve section integrity first
    for part in structured_splits:
        part = part.strip()
        if not part:
            continue

        # sentence fallback inside section
        sentences = re.split(r'(?<=[.!?])\s+', part)

        for sentence in sentences:
            if len(buffer) + len(sentence) <= chunk_size:
                buffer += " " + sentence
            else:
                if buffer.strip():
                    chunks.append(buffer.strip())

                buffer = buffer[-overlap:] + " " + sentence

    if buffer.strip():
        chunks.append(buffer.strip())

    return chunks