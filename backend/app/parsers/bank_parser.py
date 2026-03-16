# Bank statement parser
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
class BankParser:
    """
    Parses HDFC bank statement XLS files into normalized transactions.
    """
    
    def parse(self, file_path: str, skip_rows: int = 0) -> List[Dict]:
        """
        Parse HDFC bank statement.
        """
        # Read Excel file, without skipping rows initially
        if file_path.endswith('.xls') or file_path.endswith('.xlsx'):
            # Some old .xls files might need openpyxl or xlrd
            try:
                df = pd.read_excel(file_path, header=None)
            except Exception as e:
                df = pd.read_excel(file_path, engine='xlrd', header=None)
        else:
            df = pd.read_csv(file_path, header=None)
            
        # Find the header row dynamically
        header_idx = 0
        for idx, row in df.iterrows():
            row_str = ' '.join(str(val).lower() for val in row.values)
            if 'date' in row_str and ('narration' in row_str or 'description' in row_str or 'particulars' in row_str):
                header_idx = idx
                break
                
        # Set the correct header and drop preceding rows
        df.columns = df.iloc[header_idx]
        df = df.iloc[header_idx + 1:].reset_index(drop=True)
        
        # Determine mapping based on available columns
        col_names = [str(c).lower().strip() for c in df.columns]
        
        # Flexible column mapping
        date_col = next((c for c in df.columns if 'date' in str(c).lower()), None)
        desc_col = next((c for c in df.columns if 'narration' in str(c).lower() or 'description' in str(c).lower() or 'particulars' in str(c).lower()), None)
        ref_col = next((c for c in df.columns if 'ref' in str(c).lower() or 'chq' in str(c).lower()), None)
        withdraw_col = next((c for c in df.columns if 'withdrawal' in str(c).lower() or 'debit' in str(c).lower()), None)
        deposit_col = next((c for c in df.columns if 'deposit' in str(c).lower() or 'credit' in str(c).lower()), None)
        bal_col = next((c for c in df.columns if 'balance' in str(c).lower()), None)
        
        transactions = []
        for _, row in df.iterrows():
            txn = self._parse_row_dynamic(row, date_col, desc_col, ref_col, withdraw_col, deposit_col, bal_col)
            if txn:
                transactions.append(txn)
        
        return transactions
        
    def _parse_row_dynamic(self, row, date_col, desc_col, ref_col, withdraw_col, deposit_col, bal_col) -> Optional[Dict]:
        """Convert a row to transaction dict using dynamic columns."""
        try:
            if not date_col or not desc_col: return None
            
            date_str = str(row[date_col]).strip()
            if not date_str or date_str == 'nan' or date_str.lower() == 'nat':
                return None
            
            # Helper to safely parse localized floats (e.g., 1,000.50)
            def safe_float(val):
                if pd.isna(val): return 0.0
                val_str = str(val).replace(',', '').strip()
                try: return float(val_str)
                except ValueError: return 0.0
            
            withdrawal = safe_float(row[withdraw_col]) if withdraw_col else 0.0
            deposit = safe_float(row[deposit_col]) if deposit_col else 0.0
            balance = safe_float(row[bal_col]) if bal_col else 0.0
            
            # Skip if no money moved and no balance
            if withdrawal == 0 and deposit == 0 and balance == 0:
                return None
                
            return {
                "date": date_str,
                "description": str(row[desc_col]) if pd.notna(row[desc_col]) else "Unknown",
                "reference": str(row[ref_col]) if ref_col and pd.notna(row[ref_col]) else None,
                "inflow": deposit,
                "outflow": withdrawal,
                "amount": deposit - withdrawal,
                "balance": balance
            }
        except Exception as e:
            print(f"BankParser error on row: {row}")
            print(f"Error details: {e}")
            return None
    
