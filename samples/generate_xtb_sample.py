"""
Synthetic XTB Broker Statement PDF Generator.
Generates a realistic statement reflecting the bilingual Polish/English structure
of XTB periodic statements (account details with PII, closed positions, cash operations, summary).
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def generate_xtb_sample_pdf(output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )
    
    styles = getSampleStyleSheet()
    
    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#0D2237"),
        spaceBefore=10,
        spaceAfter=4,
    )
    
    normal_small = ParagraphStyle(
        "NormalSmall",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#2B2B2B"),
    )
    
    bold_small = ParagraphStyle(
        "BoldSmall",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#2B2B2B"),
    )
    
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=8.5,
        alignment=0,
    )
    
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=8.5,
        alignment=0,
    )

    story = []

    # 1. Header (Broker details on left, Client PII on right)
    header_data = [
        [
            Paragraph("<b>XTB S.A.</b><br/>ul. Prosta 67, 00-838 Warszawa<br/>KRS: 0000217580, NIP: 521-31-59-989<br/>Regulowany przez KNF<br/>support@xtb.pl | www.xtb.com", normal_small),
            Paragraph(
                "<b>ZESTAWIENIE KONTA / ACCOUNT STATEMENT</b><br/>"
                "<b>Klient / Client:</b> Jan Kowalski<br/>"
                "<b>Adres / Address:</b> ul. Marszalkowska 10/24, 00-590 Warszawa<br/>"
                "<b>PESEL / Tax ID:</b> 88041512345<br/>"
                "<b>Rachunek / Account:</b> 1059281 (PLN)<br/>"
                "<b>Okres / Period:</b> 01.01.2024 - 31.01.2024<br/>"
                "<b>Data wygenerowania / Date:</b> 2024-02-01 08:30:15",
                normal_small,
            ),
        ]
    ]
    
    header_table = Table(header_data, colWidths=[85 * mm, 100 * mm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#0D2237")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # 2. Section: Closed Positions (Akcje / ETF / Transakcje zamknięte)
    story.append(Paragraph("POZYCJE ZAMKNIĘTE / CLOSED POSITIONS", section_style))
    
    closed_headers = [
        Paragraph("<b>Pozycja<br/>Position</b>", table_cell_bold),
        Paragraph("<b>Symbol<br/>Ticker</b>", table_cell_bold),
        Paragraph("<b>Typ<br/>Type</b>", table_cell_bold),
        Paragraph("<b>Wolumen<br/>Volume</b>", table_cell_bold),
        Paragraph("<b>Czas otwarcia<br/>Open Time</b>", table_cell_bold),
        Paragraph("<b>Cena otw.<br/>Open Price</b>", table_cell_bold),
        Paragraph("<b>Czas zamkn.<br/>Close Time</b>", table_cell_bold),
        Paragraph("<b>Cena zamkn.<br/>Close Price</b>", table_cell_bold),
        Paragraph("<b>Prowizja<br/>Commission</b>", table_cell_bold),
        Paragraph("<b>Wynik brutto<br/>Gross P/L</b>", table_cell_bold),
    ]

    closed_rows = [
        closed_headers,
        [
            Paragraph("4829104", table_cell),
            Paragraph("AAPL.US", table_cell_bold),
            Paragraph("BUY", table_cell),
            Paragraph("10.00", table_cell),
            Paragraph("2024-01-08 15:45:10", table_cell),
            Paragraph("185.50 USD", table_cell),
            Paragraph("2024-01-22 17:10:00", table_cell),
            Paragraph("195.00 USD", table_cell),
            Paragraph("0.00 PLN", table_cell),
            Paragraph("+95.00 USD", table_cell),
        ],
        [
            Paragraph("4830155", table_cell),
            Paragraph("VWCE.DE", table_cell_bold),
            Paragraph("BUY", table_cell),
            Paragraph("25.00", table_cell),
            Paragraph("2024-01-10 10:15:22", table_cell),
            Paragraph("108.20 EUR", table_cell),
            Paragraph("2024-01-29 16:30:11", table_cell),
            Paragraph("112.40 EUR", table_cell),
            Paragraph("0.00 PLN", table_cell),
            Paragraph("+105.00 EUR", table_cell),
        ],
        [
            Paragraph("4839812", table_cell),
            Paragraph("PKN.PL", table_cell_bold),
            Paragraph("BUY", table_cell),
            Paragraph("100.00", table_cell),
            Paragraph("2024-01-15 09:30:00", table_cell),
            Paragraph("62.50 PLN", table_cell),
            Paragraph("2024-01-26 14:20:45", table_cell),
            Paragraph("65.80 PLN", table_cell),
            Paragraph("0.00 PLN", table_cell),
            Paragraph("+330.00 PLN", table_cell),
        ],
        [
            Paragraph("4841209", table_cell),
            Paragraph("TSLA.US", table_cell_bold),
            Paragraph("BUY", table_cell),
            Paragraph("15.00", table_cell),
            Paragraph("2024-01-18 16:00:15", table_cell),
            Paragraph("215.00 USD", table_cell),
            Paragraph("2024-01-25 18:45:00", table_cell),
            Paragraph("198.00 USD", table_cell),
            Paragraph("0.00 PLN", table_cell),
            Paragraph("-255.00 USD", table_cell),
        ],
    ]

    closed_table = Table(
        closed_rows,
        colWidths=[
            14 * mm,  # Position
            16 * mm,  # Ticker
            10 * mm,  # Type
            14 * mm,  # Volume
            24 * mm,  # Open Time
            18 * mm,  # Open Price
            24 * mm,  # Close Time
            18 * mm,  # Close Price
            18 * mm,  # Commission
            22 * mm,  # Gross P/L
        ],
    )
    closed_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F0F4F8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0D2237")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(closed_table)
    story.append(Spacer(1, 10))

    # 3. Section: Operacje finansowe / Cash Operations
    story.append(Paragraph("OPERACJE FINANSOWE / CASH OPERATIONS", section_style))
    
    cash_headers = [
        Paragraph("<b>ID</b>", table_cell_bold),
        Paragraph("<b>Czas / Date</b>", table_cell_bold),
        Paragraph("<b>Typ operacji / Type</b>", table_cell_bold),
        Paragraph("<b>Kwota / Amount</b>", table_cell_bold),
        Paragraph("<b>Komentarz / Description</b>", table_cell_bold),
    ]

    cash_rows = [
        cash_headers,
        [
            Paragraph("981204", table_cell),
            Paragraph("2024-01-02 11:00:00", table_cell),
            Paragraph("Wplata / Deposit", table_cell),
            Paragraph("+10 000.00 PLN", table_cell_bold),
            Paragraph("Przelew mBank PL61114020040000300201234567", table_cell),
        ],
        [
            Paragraph("982311", table_cell),
            Paragraph("2024-01-16 14:00:00", table_cell),
            Paragraph("Dywidenda / Dividend", table_cell),
            Paragraph("+24.00 USD", table_cell_bold),
            Paragraph("AAPL.US Div gross (10 sh @ 2.40 USD)", table_cell),
        ],
        [
            Paragraph("982312", table_cell),
            Paragraph("2024-01-16 14:00:01", table_cell),
            Paragraph("Podatek / Withholding Tax", table_cell),
            Paragraph("-3.60 USD", table_cell),
            Paragraph("WHT 15% AAPL.US", table_cell),
        ],
    ]

    cash_table = Table(
        cash_rows,
        colWidths=[15 * mm, 30 * mm, 35 * mm, 28 * mm, 70 * mm],
    )
    cash_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F0F4F8")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(cash_table)
    story.append(Spacer(1, 10))

    # 4. Summary / Podsumowanie
    story.append(Paragraph("PODSUMOWANIE / ACCOUNT SUMMARY", section_style))
    summary_data = [
        [Paragraph("<b>Saldo poczatkowe / Opening balance:</b>", normal_small), Paragraph("5 420.00 PLN", normal_small)],
        [Paragraph("<b>Suma wplat / Total deposits:</b>", normal_small), Paragraph("10 000.00 PLN", normal_small)],
        [Paragraph("<b>Wynik zamknietych pozycji / Closed P&L:</b>", normal_small), Paragraph("+2 115.30 PLN", normal_small)],
        [Paragraph("<b>Prowizje i oplaty / Total commissions:</b>", normal_small), Paragraph("0.00 PLN", normal_small)],
        [Paragraph("<b>Saldo koncowe / Ending balance:</b>", bold_small), Paragraph("<b>17 535.30 PLN</b>", bold_small)],
    ]
    summary_table = Table(summary_data, colWidths=[70 * mm, 40 * mm])
    summary_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(summary_table)

    doc.build(story)
    print(f"Sample PDF successfully generated at: {output_path}")

if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "xtb_statement_sample.pdf"
    generate_xtb_sample_pdf(out)
