"""
Unit tests for SmartFlow file parsers.
Tests BankParser and LedgerParser with synthetic data.
"""
import os
import pytest
import pandas as pd
import tempfile

from app.parsers.bank_parser import BankParser
from app.parsers.ledger_parser import LedgerParser


class TestBankParser:
    """Test HDFC bank statement parser."""

    @pytest.fixture
    def sample_bank_csv(self, tmp_path):
        """Create a sample CSV mimicking HDFC bank statement format."""
        csv_content = """,,,,,,
,HDFC Bank Statement,,,,,
Date,Narration,Chq./Ref.No.,Value Dt,Withdrawal Amt.,Deposit Amt.,Closing Balance
01/06/2025,NEFT-VENDOR-SUPPLIES,REF001,01/06/2025,"15,000.00",,485000.00
02/06/2025,UPI-CLIENT-PAYMENT,REF002,02/06/2025,,"50,000.00",535000.00
03/06/2025,RENT-PAYMENT,REF003,03/06/2025,"25,000.00",,510000.00
04/06/2025,SALARY-CREDIT,REF004,04/06/2025,,"1,00,000.00",610000.00
"""
        filepath = tmp_path / "test_bank.csv"
        filepath.write_text(csv_content)
        return str(filepath)

    def test_parse_returns_list(self, sample_bank_csv):
        parser = BankParser()
        result = parser.parse(sample_bank_csv)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_parsed_transactions_have_required_fields(self, sample_bank_csv):
        parser = BankParser()
        result = parser.parse(sample_bank_csv)

        for txn in result:
            assert "date" in txn
            assert "description" in txn
            assert "amount" in txn
            assert "balance" in txn

    def test_inflow_outflow_signs(self, sample_bank_csv):
        """Deposits should be positive amounts, withdrawals negative."""
        parser = BankParser()
        result = parser.parse(sample_bank_csv)

        # At least one positive (deposit) and one negative (withdrawal) expected
        amounts = [txn["amount"] for txn in result]
        has_positive = any(a > 0 for a in amounts)
        has_negative = any(a < 0 for a in amounts)
        assert has_positive, "Expected at least one deposit (positive amount)"
        assert has_negative, "Expected at least one withdrawal (negative amount)"


class TestLedgerParser:
    """Test Tally ledger CSV parser."""

    @pytest.fixture
    def sample_ledger_csv(self, tmp_path):
        """Create a sample Tally-format ledger CSV."""
        csv_content = """Date,Voucher Type,Voucher No,Particulars,Debit,Credit
01-Jun-2025,Sales,V001,Client ABC,,75000
02-Jun-2025,Purchase,V002,Vendor XYZ,30000,
03-Jun-2025,Payment,V003,Rent Payment,25000,
04-Jun-2025,Receipt,V004,Customer DEF,,50000
"""
        filepath = tmp_path / "test_ledger.csv"
        filepath.write_text(csv_content)
        return str(filepath)

    def test_parse_returns_list(self, sample_ledger_csv):
        parser = LedgerParser()
        result = parser.parse(sample_ledger_csv)
        assert isinstance(result, list)
        assert len(result) == 4

    def test_parsed_entries_have_required_fields(self, sample_ledger_csv):
        parser = LedgerParser()
        result = parser.parse(sample_ledger_csv)

        for entry in result:
            assert "date" in entry
            assert "voucher_type" in entry
            assert "particulars" in entry
            assert "debit" in entry
            assert "credit" in entry

    def test_debit_credit_are_numeric(self, sample_ledger_csv):
        parser = LedgerParser()
        result = parser.parse(sample_ledger_csv)

        for entry in result:
            assert isinstance(entry["debit"], (int, float))
            assert isinstance(entry["credit"], (int, float))
            assert entry["debit"] >= 0
            assert entry["credit"] >= 0

    def test_unsupported_format_raises_error(self, tmp_path):
        """Parser should reject unsupported file formats."""
        filepath = tmp_path / "data.json"
        filepath.write_text('{"key": "value"}')

        parser = LedgerParser()
        with pytest.raises(ValueError, match="Unsupported"):
            parser.parse(str(filepath))
