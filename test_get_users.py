"""Test get_all_users_for_admin directly"""
import sys
import traceback
from chatapp_database import ChatAppDatabase

db = ChatAppDatabase()

try:
    print("Testing get_all_users_for_admin()...")
    users = db.get_all_users_for_admin()
    print(f"✅ Success! Got {len(users)} users:")
    for user in users:
        print(f"  - ID: {user['id']}, Username: {user['username']}, Unread: {user['unread_count']}, Last msg: {user['last_message_time']}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
