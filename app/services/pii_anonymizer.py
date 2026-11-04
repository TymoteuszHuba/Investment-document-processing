"""
PII Anonymization Service (Privacy-First Engine).
Detects and sanitizes Personally Identifiable Information (PII) from broker statements
locally before passing the payload to external LLM services.
"""

import re
from dataclasses import dataclass, field


@dataclass
class AnonymizationResult:
    """Result of the PII anonymization process."""
    anonymized_text: str
    detected_pii_count: int
    detected_categories: list[str] = field(default_factory=list)

class PIIAnonymizer:
    """
    Regex-based local anonymizer designed for European & Polish broker statements.
    Ensures that names, addresses, PESEL/tax IDs, bank IBANs, and broker account numbers
    are replaced with secure placeholders while strictly preserving financial figures,
    tickers, dates, and order IDs.
    """

    # 1. Client Name (e.g. "Klient / Client: Jan Kowalski", "Inwestor: Anna Maria Nowak-Jankowska")
    CLIENT_NAME_PATTERN = re.compile(
        r"((?:Klient\s*/\s*Client|Klient|Client|Inwestor|Imi[eę]\s*i\s*nazwisko)\s*[:/]\s*)([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\s\-]+?)(?=\s*(?:Adres|Address|PESEL|Rachunek|Account|Tax|$|\n|\r))",
        re.IGNORECASE | re.UNICODE,
    )

    # 2. Address (e.g. "Adres / Address: ul. Marszalkowska 10/24, 00-590 Warszawa")
    ADDRESS_HEADER_PATTERN = re.compile(
        r"((?:Adres\s*/\s*Address|Adres|Address|Zamieszka[lł]y|Miejsce\s*zamieszkania)\s*[:/]\s*)([^\n\r]+?)(?=\s*(?:PESEL|Tax|Rachunek|Account|$|\n|\r))",
        re.IGNORECASE | re.UNICODE,
    )

    # 3. Tax ID / PESEL (e.g. "PESEL / Tax ID: 88041512345", "PESEL: 88041512345")
    PESEL_HEADER_PATTERN = re.compile(
        r"((?:PESEL\s*/\s*Tax\s*ID|PESEL|Tax\s*ID|Identyfikator\s*podatkowy)\s*[:/]\s*)(\d{11})",
        re.IGNORECASE | re.UNICODE,
    )

    # 4. Broker Account Number (e.g. "Rachunek / Account: 1059281 (PLN)")
    ACCOUNT_HEADER_PATTERN = re.compile(
        r"((?:Rachunek\s*/\s*Account|Rachunek|Account|Numer\s*rachunku|Nr\s*konta|Login)\s*[:/]\s*)(\d{4,12})",
        re.IGNORECASE | re.UNICODE,
    )

    # 5. Bank Account Number / IBAN (Polish standard 26 digits or PL + 26 digits)
    IBAN_PATTERN = re.compile(
        r"\b(?:PL)?\s?(?:\d{4}\s?){6}\d{2}\b|\bPL\d{26}\b",
        re.IGNORECASE,
    )

    # 6. Standalone Polish Street addresses (e.g. "ul. Marszalkowska 10/24, 00-590 Warszawa")
    STANDALONE_ADDRESS_PATTERN = re.compile(
        r"\b(?:ul\.|ulica|al\.|aleja|pl\.|plac)\s+[\w\s\.\-/]+?,\s*\d{2}-\d{3}\s+[\w\s\-]+",
        re.IGNORECASE | re.UNICODE,
    )

    def anonymize(self, text: str) -> AnonymizationResult:
        """
        Executes local PII detection and token replacement on input text.
        
        Args:
            text: Raw extracted text from PDF.
            
        Returns:
            AnonymizationResult containing the sanitized text and statistics.
        """
        if not text:
            return AnonymizationResult(anonymized_text="", detected_pii_count=0, detected_categories=[])

        sanitized = text
        categories_found: set[str] = set()
        total_pii_count = 0

        # 1. Mask Client Name
        def replace_name(match: re.Match) -> str:
            nonlocal total_pii_count
            total_pii_count += 1
            categories_found.add("CLIENT_NAME")
            prefix = match.group(1)
            return f"{prefix}[CLIENT_NAME]"

        sanitized = self.CLIENT_NAME_PATTERN.sub(replace_name, sanitized)

        # 2. Mask Address from Header
        def replace_address_header(match: re.Match) -> str:
            nonlocal total_pii_count
            total_pii_count += 1
            categories_found.add("ADDRESS")
            prefix = match.group(1)
            return f"{prefix}[ADDRESS]"

        sanitized = self.ADDRESS_HEADER_PATTERN.sub(replace_address_header, sanitized)

        # 3. Mask PESEL / Tax ID
        def replace_pesel(match: re.Match) -> str:
            nonlocal total_pii_count
            total_pii_count += 1
            categories_found.add("TAX_ID")
            prefix = match.group(1)
            return f"{prefix}[TAX_ID]"

        sanitized = self.PESEL_HEADER_PATTERN.sub(replace_pesel, sanitized)

        # 4. Mask Broker Account Number
        def replace_account(match: re.Match) -> str:
            nonlocal total_pii_count
            total_pii_count += 1
            categories_found.add("ACCOUNT_NUMBER")
            prefix = match.group(1)
            return f"{prefix}[ACCOUNT_NUMBER]"

        sanitized = self.ACCOUNT_HEADER_PATTERN.sub(replace_account, sanitized)

        # 5. Mask Bank Account Numbers (IBAN)
        def replace_iban(match: re.Match) -> str:
            nonlocal total_pii_count
            matched_val = match.group(0).replace(" ", "")
            # Verify length: exactly 26 digits or PL + 26 digits
            if (matched_val.startswith(("PL", "pl")) and len(matched_val) == 28) or (len(matched_val) == 26 and matched_val.isdigit()):
                total_pii_count += 1
                categories_found.add("BANK_IBAN")
                return "[BANK_IBAN]"
            return match.group(0)

        sanitized = self.IBAN_PATTERN.sub(replace_iban, sanitized)

        # 6. Mask Standalone Street Addresses if any remain
        def replace_standalone_addr(match: re.Match) -> str:
            nonlocal total_pii_count
            # Avoid replacing broker's corporate address (e.g. XTB S.A. ul. Prosta 67)
            if "prosta 67" in match.group(0).lower():
                return match.group(0)
            total_pii_count += 1
            categories_found.add("ADDRESS")
            return "[ADDRESS]"

        sanitized = self.STANDALONE_ADDRESS_PATTERN.sub(replace_standalone_addr, sanitized)

        return AnonymizationResult(
            anonymized_text=sanitized,
            detected_pii_count=total_pii_count,
            detected_categories=sorted(categories_found),
        )
