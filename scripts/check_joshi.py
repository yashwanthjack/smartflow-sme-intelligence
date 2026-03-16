import psycopg2

DB = "postgresql://postgres:yash%401234@localhost:5432/smartflow"
conn = psycopg2.connect(DB)
cur = conn.cursor()

# Step 1: Get user + entity_id
cur.execute("SELECT id, email, full_name, entity_id FROM users WHERE email ILIKE %s", ("%joshi%",))
user = cur.fetchone()
print(f"USER: id={user[0]}, email={user[1]}, entity_id={user[3]}")

entity_id = user[3]
if not entity_id:
    print("ERROR: No entity_id linked to this user!")
    cur.close(); conn.close(); exit()

# Step 2: Check entity
cur.execute("SELECT id, name, entity_type FROM entities WHERE id = %s", (entity_id,))
entity = cur.fetchone()
print(f"ENTITY: {entity}")

# Step 3: Ledger summary
cur.execute("""
    SELECT COUNT(*), MIN(ledger_date), MAX(ledger_date), SUM(amount)
    FROM ledger_entries WHERE entity_id = %s
""", (entity_id,))
row = cur.fetchone()
print(f"\nLEDGER ENTRIES: count={row[0]}, from={row[1]}, to={row[2]}, sum={row[3]}")

# Step 4: Recent entries
cur.execute("""
    SELECT ledger_date, description, amount, category, source_type
    FROM ledger_entries WHERE entity_id = %s
    ORDER BY ledger_date DESC LIMIT 10
""", (entity_id,))
rows = cur.fetchall()
print(f"\nRECENT ENTRIES:")
for r in rows:
    print(f"  {r}")

# Step 5: Accounts
cur.execute("SELECT bank_name, account_number, current_balance FROM accounts WHERE entity_id = %s", (entity_id,))
print(f"\nACCOUNTS:")
for r in cur.fetchall():
    print(f"  {r}")

# Step 6: All entities with ledger counts (to verify where data landed)
cur.execute("""
    SELECT e.name, e.id, COUNT(l.id) as cnt
    FROM entities e
    LEFT JOIN ledger_entries l ON l.entity_id = e.id
    GROUP BY e.id, e.name
    ORDER BY cnt DESC
""")
print(f"\nALL ENTITIES + LEDGER COUNT:")
for r in cur.fetchall():
    print(f"  {r}")

cur.close()
conn.close()
print("\nDone.")
