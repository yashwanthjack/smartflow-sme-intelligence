import psycopg2

conn = psycopg2.connect("postgresql://postgres:yash%401234@localhost:5432/smartflow")
cur = conn.cursor()

ENTITY = "d9ff0ba0-0369-4e7c-8828-f153866594b6"

# Delete rows with invalid date (year > 2100) or description == 'nan'
cur.execute("""
    DELETE FROM ledger_entries
    WHERE entity_id = %s
    AND (
        EXTRACT(year FROM ledger_date) > 2100
        OR description = 'nan'
        OR description IS NULL
    )
""", (ENTITY,))
deleted = cur.rowcount
conn.commit()
print(f"Deleted {deleted} bad rows")

# Show final stats
cur.execute("""
    SELECT COUNT(*), MIN(ledger_date), MAX(ledger_date), ROUND(SUM(amount)::numeric, 2)
    FROM ledger_entries WHERE entity_id = %s
""", (ENTITY,))
row = cur.fetchone()
print(f"Final: count={row[0]}, from={row[1]}, to={row[2]}, net_balance=₹{row[3]}")

cur.close()
conn.close()
