# Bank statement parser
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
class BankParser:
    """
    Parses HDFC bank statement XLS files into normalized transactions.
    """
    
    def parse(self, file_path: str, skip_rows: int = 21) -> List[Dict]:
        """
        Parse HDFC bank statement.
        """
        # Read Excel file, skip header rows
        if file_path.endswith('.xls') or file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path, skiprows=skip_rows)
        else:
            df = pd.read_csv(file_path, skiprows=skip_rows)
        
        # Rename columns to standard names
        df.columns = ['date', 'narration', 'chq_ref', 'value_date', 
                      'withdrawal', 'deposit', 'closing_balance']
        
        transactions = []
        for _, row in df.iterrows():
            txn = self._parse_row(row)
            if txn:
                transactions.append(txn)
        
        return transactions
    
    def _parse_row(self, row) -> Optional[Dict]:
        """Convert a row to transaction dict."""
        try:
            date_str = str(row['date']).strip()
            if not date_str or date_str == 'nan':
                return None
            
            withdrawal = float(row['withdrawal']) if pd.notna(row['withdrawal']) else 0
            deposit = float(row['deposit']) if pd.notna(row['deposit']) else 0
            balance = float(row['closing_balance']) if pd.notna(row['closing_balance']) else 0
            
            return {
                "date": date_str,
                "description": str(row['narration']),
                "reference": str(row['chq_ref']) if pd.notna(row['chq_ref']) else None,
                "inflow": deposit,
                "outflow": withdrawal,
                "amount": deposit - withdrawal,
                "balance": balance
            }
        except Exception:
            return None