"""Test the SQL query directly"""
from chatapp_database import ChatAppDatabase

db = ChatAppDatabase()

try:
    print("Testing get_all_users_for_admin()...")
    users = db.get_all_users_for_admin()
    print(f"✅ Success! Got {len(users)} users:")
    for user in users:
        print(f"  - {user['username']} (ID: {user['id']}) - Unread: {user['unread_count']}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
