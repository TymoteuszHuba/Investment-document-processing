"""
Inspector script to extract raw text and layout blocks from a PDF statement
using PyMuPDF (fitz), mimicking the first ingestion stage of our IDP pipeline.
"""

import sys
from pathlib import Path
import fitz  # PyMuPDF

def inspect_pdf(pdf_path: Path):
    if not pdf_path.exists():
        print(f"Error: File not found at {pdf_path}")
        sys.exit(1)

    print(f"=" * 70)
    print(f"INSPECTING PDF: {pdf_path.name}")
    print(f"=" * 70)

    doc = fitz.open(pdf_path)
    print(f"Page count: {len(doc)}\n")

    for page_num in range(len(doc)):
        page = doc[page_num]
        print(f"--- PAGE {page_num + 1} RAW TEXT ---")
        raw_text = page.get_text("text")
        print(raw_text)
        print("-" * 50)
        
        # Also inspect blocks (gives idea of column/table flow)
        blocks = page.get_text("blocks")
        print(f"--- PAGE {page_num + 1} DETECTED TEXT BLOCKS (Total: {len(blocks)}) ---")
        for i, b in enumerate(blocks):
            # b: (x0, y0, x1, y1, text, block_no, block_type)
            block_text = b[4].strip().replace("\n", " | ")
            print(f"Block {i:02d} [{b[0]:.1f}, {b[1]:.1f} - {b[2]:.1f}, {b[3]:.1f}]: {block_text}")
        print(f"=" * 70)

if __name__ == "__main__":
    default_sample = Path(__file__).resolve().parent / "xtb_statement_sample.pdf"
    target_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_sample
    inspect_pdf(target_path)
