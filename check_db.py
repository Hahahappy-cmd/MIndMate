import sqlite3
import os

db_path = "mindmate.db"
print(f"Checking database at: {os.path.abspath(db_path)}")

if os.path.exists(db_path):
    print("✅ Database file found!")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # List tables and show ALL data
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("\n📋 Tables in database:", tables)

    for table in tables:
        table_name = table[0]
        print(f"\n--- {table_name} ---")

        # Show table structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print("Structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

        # Show ALL data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        print(f"Data ({len(rows)} rows):")
        for row in rows:
            print(f"  {row}")

    conn.close()
else:
    print("❌ Database file not found!")