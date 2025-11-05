import sqlite3

# Connect to the database
conn = sqlite3.connect('chatapp.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in chatapp.db:")
for table in tables:
    print(f"  - {table[0]}")
    
    # Show table structure
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    print(f"    Columns:")
    for col in columns:
        print(f"      {col[1]} ({col[2]})")
    
    # Show sample data
    cursor.execute(f"SELECT * FROM {table[0]} LIMIT 3")
    rows = cursor.fetchall()
    if rows:
        print(f"    Sample data: {len(rows)} rows")
        for row in rows:
            print(f"      {row}")
    print()

conn.close()
