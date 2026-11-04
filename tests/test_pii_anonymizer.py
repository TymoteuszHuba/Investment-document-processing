"""
Unit tests for the PIIAnonymizer service.
"""

from pathlib import Path

import pytest

from app.services.pdf_parser import PDFParser
from app.services.pii_anonymizer import PIIAnonymizer

SAMPLE_PDF_PATH = Path(__file__).resolve().parent.parent / "samples" / "xtb_statement_sample.pdf"

@pytest.fixture
def anonymizer():
    return PIIAnonymizer()

def test_anonymize_empty_string(anonymizer):
    res = anonymizer.anonymize("")
    assert res.anonymized_text == ""
    assert res.detected_pii_count == 0
    assert res.detected_categories == []

def test_anonymize_client_name(anonymizer):
    text = "Klient / Client: Jan Kowalski\nInwestor: Anna Maria Nowak-Jankowska"
    res = anonymizer.anonymize(text)
    assert "Jan Kowalski" not in res.anonymized_text
    assert "Anna Maria Nowak-Jankowska" not in res.anonymized_text
    assert "Klient / Client: [CLIENT_NAME]" in res.anonymized_text
    assert "Inwestor: [CLIENT_NAME]" in res.anonymized_text
    assert "CLIENT_NAME" in res.detected_categories

def test_anonymize_address(anonymizer):
    text = "Adres / Address: ul. Marszalkowska 10/24, 00-590 Warszawa"
    res = anonymizer.anonymize(text)
    assert "Marszalkowska" not in res.anonymized_text
    assert "00-590" not in res.anonymized_text
    assert "Adres / Address: [ADDRESS]" in res.anonymized_text
    assert "ADDRESS" in res.detected_categories

def test_anonymize_pesel(anonymizer):
    text = "PESEL / Tax ID: 88041512345\nPESEL: 92010198765"
    res = anonymizer.anonymize(text)
    assert "88041512345" not in res.anonymized_text
    assert "92010198765" not in res.anonymized_text
    assert "PESEL / Tax ID: [TAX_ID]" in res.anonymized_text
    assert "PESEL: [TAX_ID]" in res.anonymized_text
    assert "TAX_ID" in res.detected_categories

def test_anonymize_broker_account(anonymizer):
    text = "Rachunek / Account: 1059281 (PLN)"
    res = anonymizer.anonymize(text)
    assert "1059281" not in res.anonymized_text
    assert "[ACCOUNT_NUMBER]" in res.anonymized_text
    assert "(PLN)" in res.anonymized_text  # Currency remains intact
    assert "ACCOUNT_NUMBER" in res.detected_categories

def test_anonymize_bank_iban(anonymizer):
    text = "Przelew mBank PL61114020040000300201234567 kwota 1000"
    res = anonymizer.anonymize(text)
    assert "PL61114020040000300201234567" not in res.anonymized_text
    assert "[BANK_IBAN]" in res.anonymized_text
    assert "BANK_IBAN" in res.detected_categories

def test_anonymize_xtb_sample_pdf_end_to_end(anonymizer):
    """
    End-to-end test verifying that the real sample PDF extracted text
    has all client PII masked while leaving financial data intact.
    """
    raw_text = PDFParser.extract_text(SAMPLE_PDF_PATH)
    res = anonymizer.anonymize(raw_text)

    # 1. Verify all mock PII is gone
    assert "Jan Kowalski" not in res.anonymized_text
    assert "Marszalkowska 10/24" not in res.anonymized_text
    assert "88041512345" not in res.anonymized_text
    assert "1059281" not in res.anonymized_text
    assert "PL61114020040000300201234567" not in res.anonymized_text

    # 2. Verify all tokens are present
    assert "[CLIENT_NAME]" in res.anonymized_text
    assert "[ADDRESS]" in res.anonymized_text
    assert "[TAX_ID]" in res.anonymized_text
    assert "[ACCOUNT_NUMBER]" in res.anonymized_text
    assert "[BANK_IBAN]" in res.anonymized_text

    # 3. Verify financial data and tickers are NOT damaged
    assert "AAPL.US" in res.anonymized_text
    assert "VWCE.DE" in res.anonymized_text
    assert "TSLA.US" in res.anonymized_text
    assert "PKN.PL" in res.anonymized_text
    assert "185.50 USD" in res.anonymized_text
    assert "10.00" in res.anonymized_text
    assert "+95.00 USD" in res.anonymized_text
    assert "4829104" in res.anonymized_text  # Position ID preserved
    assert "2024-01-08" in res.anonymized_text  # Date preserved
    assert "15:45:10" in res.anonymized_text    # Time preserved
    assert "XTB S.A." in res.anonymized_text  # Broker info preserved
    assert "Prosta 67" in res.anonymized_text  # Broker corporate address preserved
