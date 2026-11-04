"""
Unit tests for the PDFParser service.
"""

from pathlib import Path

import pytest

from app.services.pdf_parser import EmptyPDFError, PDFParser, PDFParserError

SAMPLE_PDF_PATH = Path(__file__).resolve().parent.parent / "samples" / "xtb_statement_sample.pdf"

def test_extract_text_from_valid_path():
    assert SAMPLE_PDF_PATH.exists(), "Sample PDF must exist for this test."
    text = PDFParser.extract_text(SAMPLE_PDF_PATH)
    
    assert isinstance(text, str)
    assert len(text) > 0
    assert "XTB S.A." in text
    assert "POZYCJE ZAMKNI" in text or "CLOSED POSITIONS" in text
    assert "AAPL.US" in text

def test_extract_text_from_bytes():
    assert SAMPLE_PDF_PATH.exists(), "Sample PDF must exist for this test."
    with open(SAMPLE_PDF_PATH, "rb") as f:
        pdf_bytes = f.read()

    text = PDFParser.extract_text(pdf_bytes)
    assert "XTB S.A." in text
    assert "AAPL.US" in text

def test_extract_page_count():
    assert SAMPLE_PDF_PATH.exists()
    count = PDFParser.extract_page_count(SAMPLE_PDF_PATH)
    assert count == 1

def test_extract_from_non_existent_path():
    non_existent = Path("non_existent_file.pdf")
    with pytest.raises(FileNotFoundError):
        PDFParser.extract_text(non_existent)

def test_extract_from_empty_bytes():
    with pytest.raises(EmptyPDFError):
        PDFParser.extract_text(b"")

def test_extract_from_invalid_bytes():
    with pytest.raises(PDFParserError):
        PDFParser.extract_text(b"not a valid pdf content")
