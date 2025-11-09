"""Check what's in the Conversations tab user list"""
import sys
import psycopg2

if len(sys.argv) < 2:
    print("Usage: python check_conversations_tab.py <DATABASE_URL>")
    sys.exit(1)

db_url = sys.argv[1]

print("=" * 80)
print("CHECKING CONVERSATIONS TAB USER LIST")
print("=" * 80)

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # This is the EXACT query used by /admin/users endpoint (without include_deleted)
    query = '''
        SELECT u.id, u.username, u.email, u.user_role, u.is_deleted,
               (SELECT COUNT(*) FROM admin_messages WHERE user_id = u.id) as message_count,
               (SELECT MAX(timestamp) FROM admin_messages WHERE user_id = u.id) as last_message_time,
               (SELECT COUNT(*) FROM admin_messages WHERE user_id = u.id AND sender_type = 'user' AND is_read = 0) as unread_count
        FROM users u
        WHERE u.user_role != 'administrator' AND u.is_deleted = 0
        ORDER BY 
            u.is_deleted ASC,
            CASE WHEN (SELECT MAX(timestamp) FROM admin_messages WHERE user_id = u.id) IS NULL THEN 0 ELSE 1 END,
            (SELECT MAX(timestamp) FROM admin_messages WHERE user_id = u.id) DESC, 
            u.username ASC
    '''
    
    cursor.execute(query)
    users = cursor.fetchall()
    
    print(f"\n📊 RESULT: {len(users)} active non-admin users\n")
    
    if len(users) == 0:
        print("❌ NO USERS FOUND!")
        print("   This is why the Conversations tab shows 'No users yet'")
        print()
        
        # Check if there are ANY users at all
        cursor.execute("SELECT id, username, user_role, is_deleted FROM users")
        all_users = cursor.fetchall()
        print(f"\n📋 ALL USERS IN DATABASE ({len(all_users)}):")
        for user in all_users:
            status = "DELETED" if user[3] else "ACTIVE"
            print(f"   {user[0]:3} | {user[1]:20} | {user[2]:15} | {status}")
    else:
        print("✅ USERS AVAILABLE FOR CONVERSATIONS:")
        for user in users:
            print(f"\n   User ID: {user[0]}")
            print(f"   Username: {user[1]}")
            print(f"   Email: {user[2]}")
            print(f"   Messages: {user[5]}")
            print(f"   Last Message: {user[6]}")
            print(f"   Unread: {user[7]}")
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
