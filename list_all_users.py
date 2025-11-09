"""
List all users in the database
"""
import sqlite3

DB_PATH = 'chatapp.db'

def list_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, user_role, is_deleted 
        FROM users 
        ORDER BY username
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        print("❌ No users found in database")
        return
    
    print(f"\n📋 All Users ({len(users)} total):\n")
    print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Role':<15} {'Status'}")
    print("=" * 85)
    
    for user in users:
        user_id, username, email, role, is_deleted = user
        status = '❌ DELETED' if is_deleted else '✅ Active'
        print(f"{user_id:<5} {username:<20} {email:<30} {role:<15} {status}")
    
    print()

if __name__ == '__main__':
    try:
        list_users()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
