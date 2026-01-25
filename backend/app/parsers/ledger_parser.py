import pandas as pd
from typing import List, Dict, Optional
class LedgerParser:
    def parse(self, file_path: str) -> List[Dict]:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xls') or file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format")
        df.columns=df.columns.str.lower().str.strip()
        entries=[]
        for _,row in df.iterrows():
            entry=self._parse_row(row)
            if entry:
                entries.append(entry)
        return entries
    def _parse_row(self,row)->Optional[Dict]:
        try:
            return{
                   "date": str(row.get('date', '')),
                   "voucher_type": str(row.get('voucher type', '')),
                   "voucher_no": str(row.get('voucher no', '')),
                   "particulars": str(row.get('particulars', '')),
                   "debit": float(row.get('debit', 0))
                   if pd.notna(row.get('debit')) else 0,
                   "credit": float(row.get('credit', 0))
                   if pd.notna(row.get('credit')) else 0
                   }
        except Exception:
            return None