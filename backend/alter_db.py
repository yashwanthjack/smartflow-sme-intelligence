from sqlalchemy import text
from app.db.database import engine

def add_column():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE entities ADD COLUMN account_category VARCHAR DEFAULT 'BUSINESS'"))
            conn.commit()
            print("Column added successfully.")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("Column already exists.")
            else:
                print(f"Error adding column: {e}")

if __name__ == "__main__":
    add_column()
