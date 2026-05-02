import re

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150):
    """
    Simple overlapping chunking strategy.
    Good balance between performance and retrieval quality.
    """

    text = clean_text(text)

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(chunk)

        start = end - overlap  # overlap for context continuity

        if start < 0:
            start = 0

    return chunks