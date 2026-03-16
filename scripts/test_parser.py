import sys
sys.path.insert(0, r"d:\1.Education\smartflow-sme-intelligence\backend")

from app.parsers.bank_parser import BankParser

file_path = r"d:\1.Education\smartflow-sme-intelligence\Acct Statement_1521_24012026_17.54.20.xls"

parser = BankParser()
print("Running parser with skip_rows=21...")
try:
    txns = parser.parse(file_path)
    print(f"Total transactions parsed: {len(txns)}")
    for t in txns[:5]:
        print(f"  {t}")
except Exception as e:
    print(f"PARSER ERROR: {e}")

# Also try different skip rows to find data
import pandas as pd
print("\n=== Finding header row automatically ===")
df_raw = pd.read_excel(file_path, skiprows=0, header=None)
for i, row in df_raw.iterrows():
    row_str = " ".join([str(v) for v in row.values])
    if "Date" in row_str or "Narration" in row_str or "Withdrawal" in row_str:
        print(f"HEADER FOUND at row {i}: {list(row.values)}")
        break
