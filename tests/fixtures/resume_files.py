"""Small generated resume file fixtures for parsing tests."""

from __future__ import annotations

import io

from docx import Document
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_text_pdf(text: str) -> bytes:
    """Build a minimal text-based PDF with extractable content."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)

    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    font_ref = writer._add_object(font)

    escaped = _escape_pdf_text(text)
    stream_data = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET"
    stream = DecodedStreamObject()
    stream.set_data(stream_data.encode("latin-1"))

    page[NameObject("/Resources")] = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): font_ref}),
        }
    )
    page[NameObject("/Contents")] = stream

    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def make_blank_pdf() -> bytes:
    """Build a PDF page with no extractable text (simulates image-only PDF)."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def make_docx(text: str) -> bytes:
    """Build a minimal DOCX containing the given paragraph text."""
    document = Document()
    for paragraph in text.split("\n\n"):
        document.add_paragraph(paragraph)
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()
