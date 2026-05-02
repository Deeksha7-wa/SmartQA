import re

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150):
    """
    Universal chunking for ANY document:
    - CVs
    - PDFs
    - Articles
    - Research papers
    - Notes
    """

    text = clean_text(text)

    # 🔥 Step 1: Split on natural boundaries first
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = ""

    # 🔥 Step 2: build sentence-aware chunks (not raw slicing)
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())

            # overlap handling (keep last part for continuity)
            current_chunk = current_chunk[-overlap:] + " " + sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks