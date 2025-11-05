"""
Check what tables exist in the database
"""
import sqlite3

DB_PATH = "integrated_users.db"  # This is the actual database file used by the app

def check_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("🗃️  DATABASE SCHEMA")
    print("="*70)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    if not tables:
        print("❌ No tables found in database!")
        conn.close()
        return
    
    print(f"\n📋 Found {len(tables)} tables:\n")
    
    for (table_name,) in tables:
        print(f"🔹 Table: {table_name}")
        
        # Get columns for this table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for col in columns:
            col_id, name, type, notnull, default, pk = col
            pk_str = " (PRIMARY KEY)" if pk else ""
            print(f"   - {name}: {type}{pk_str}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   📊 Rows: {count}\n")
    
    # Now check for test users
    print("\n" + "="*70)
    print("🔍 LOOKING FOR TEST USERS")
    print("="*70)
    
    # Try different table names that might exist
    possible_tables = ['users', 'chat_users', 'app_users']
    
    for table in possible_tables:
        try:
            cursor.execute(f"""
                SELECT id, username, email 
                FROM {table}
                WHERE username LIKE 'pwtest_%'
                ORDER BY id DESC
                LIMIT 5
            """)
            users = cursor.fetchall()
            
            if users:
                print(f"\n✅ Found {len(users)} test users in '{table}' table:")
                for user in users:
                    print(f"   - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
        except sqlite3.OperationalError:
            pass  # Table doesn't exist
    
    conn.close()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          DATABASE SCHEMA CHECK                                   ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    try:
        check_schema()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
