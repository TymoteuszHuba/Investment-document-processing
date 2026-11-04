"""
PDF Text Ingestion Service using PyMuPDF.
Supports both file paths and in-memory byte streams from HTTP uploads.
"""

from pathlib import Path

import pymupdf


class PDFParserError(Exception):
    """Base exception for PDF parsing errors."""

class EmptyPDFError(PDFParserError):
    """Raised when the PDF file has no pages or contains no text."""

class PDFParser:
    """Service responsible for extracting text from broker statement PDFs."""

    @staticmethod
    def extract_text(source: Path | str | bytes) -> str:
        """
        Extracts all textual content from a PDF file or bytes buffer.
        
        Args:
            source: Path to PDF file or raw bytes of a PDF.
            
        Returns:
            Concatenated clean raw text from all pages.
            
        Raises:
            EmptyPDFError: If the document is empty or contains no extractable text.
            PDFParserError: If parsing fails due to corruption or invalid format.
        """
        try:
            if isinstance(source, (str, Path)):
                path = Path(source)
                if not path.exists():
                    raise FileNotFoundError(f"PDF file not found: {path}")
                doc = pymupdf.open(path)
            elif isinstance(source, bytes):
                if not source:
                    raise EmptyPDFError("Provided PDF byte buffer is empty.")
                doc = pymupdf.open(stream=source, filetype="pdf")
            else:
                raise TypeError(f"Unsupported source type: {type(source)}")

            if len(doc) == 0:
                doc.close()
                raise EmptyPDFError("The PDF document contains 0 pages.")

            extracted_pages: list[str] = []
            for page_index in range(len(doc)):
                page = doc[page_index]
                text = page.get_text("text")
                if text.strip():
                    extracted_pages.append(text.strip())

            doc.close()

            if not extracted_pages:
                raise EmptyPDFError("No extractable text found in the PDF document.")

            return "\n\n".join(extracted_pages)

        except (EmptyPDFError, FileNotFoundError, TypeError):
            raise
        except Exception as exc:
            raise PDFParserError(f"Failed to parse PDF document: {exc!s}") from exc

    @staticmethod
    def extract_page_count(source: Path | str | bytes) -> int:
        """Returns the total number of pages in the PDF document."""
        try:
            if isinstance(source, (str, Path)):
                doc = pymupdf.open(Path(source))
            else:
                doc = pymupdf.open(stream=source, filetype="pdf")
            count = len(doc)
            doc.close()
            return count
        except Exception as exc:
            raise PDFParserError(f"Failed to get page count: {exc!s}") from exc
