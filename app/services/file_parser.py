from docx import Document as DocxDocument
from pypdf import PdfReader
import os


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)

    return "\n".join(text)


def extract_text_from_docx(file_path: str) -> str:
    doc = DocxDocument(file_path)
    text = []

    for para in doc.paragraphs:
        if para.text.strip():
            text.append(para.text)

    return "\n".join(text)


def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_text(file_path: str, file_type: str = None) -> str:

    # 🔥 AUTO-DETECT TYPE (BEST PRACTICE)
    if file_type is None:
        file_type = os.path.splitext(file_path)[1].lower().replace(".", "")

    file_type = file_type.lower()

    if file_type in ["pdf"]:
        return extract_text_from_pdf(file_path)

    elif file_type in ["docx"]:
        return extract_text_from_docx(file_path)

    elif file_type in ["txt", "text"]:
        return extract_text_from_txt(file_path)

    else:
        raise ValueError(f"Unsupported file type: {file_type}")