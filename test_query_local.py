"""Test the get_all_users_for_admin query locally"""
from chatapp_database import ChatAppDatabase

db = ChatAppDatabase()

print("=" * 80)
print("TESTING get_all_users_for_admin LOCALLY")
print("=" * 80)

try:
    print("\n1. Without deleted users:")
    users = db.get_all_users_for_admin(include_deleted=False)
    print(f"   Found {len(users)} active users")
    for u in users:
        print(f"   - {u['username']} (deleted={u['is_deleted']})")
    
    print("\n2. With deleted users:")
    users = db.get_all_users_for_admin(include_deleted=True)
    print(f"   Found {len(users)} total users")
    for u in users:
        status = '[DELETED]' if u['is_deleted'] else 'ACTIVE'
        print(f"   - {status:10} {u['username']:20}")
    
    print("\n✅ Query works locally!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
