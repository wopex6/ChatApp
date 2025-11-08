"""Test if online status is being returned by the API"""
import requests
import json

# Railway URL
BASE_URL = "https://chatapp-production-0762.up.railway.app/api"

print("=" * 80)
print("TESTING ONLINE STATUS IN ADMIN USER LIST")
print("=" * 80)

# First, login as admin to get token
admin_username = input("Enter admin username (default: Ken Tse): ").strip() or "Ken Tse"
admin_password = input("Enter admin password: ").strip()

print(f"\n1. Logging in as {admin_username}...")
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": admin_username,
    "password": admin_password
})

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()['token']
print(f"✅ Login successful! Token: {token[:20]}...")

# Get admin users list
print(f"\n2. Fetching admin users list...")
headers = {'Authorization': f'Bearer {token}'}
users_response = requests.get(f"{BASE_URL}/admin/users", headers=headers)

if users_response.status_code != 200:
    print(f"❌ Failed to fetch users: {users_response.status_code}")
    print(users_response.text)
    exit(1)

users = users_response.json()
print(f"✅ Fetched {len(users)} users\n")

# Display each user with status
print("=" * 80)
print("USER LIST WITH STATUS:")
print("=" * 80)

for user in users:
    status = user.get('status', 'NOT_FOUND')
    last_seen = user.get('last_seen', 'NOT_FOUND')
    
    status_icon = "🟢" if status == 'online' else "⚪" if status == 'offline' else "❓"
    
    print(f"\n{status_icon} User: {user['username']}")
    print(f"   ID: {user['id']}")
    print(f"   Email: {user['email']}")
    print(f"   Status: {status}")
    print(f"   Last Seen: {last_seen}")
    print(f"   Unread: {user.get('unread_count', 0)}")
    print(f"   Last Message: {user.get('last_message_time', 'None')}")

print("\n" + "=" * 80)
print("ANALYSIS:")
print("=" * 80)

# Check if status field exists
users_with_status = [u for u in users if 'status' in u]
users_online = [u for u in users if u.get('status') == 'online']

if len(users_with_status) == 0:
    print("❌ PROBLEM: No users have 'status' field!")
    print("   Backend is NOT returning status data")
    print("   Deployment may not have completed yet")
elif len(users_online) == 0:
    print("⚠️  All users are OFFLINE (no green dots will show)")
    print("   Make sure at least one regular user is logged in")
else:
    print(f"✅ {len(users_online)} user(s) are ONLINE")
    print(f"   Online users: {', '.join([u['username'] for u in users_online])}")

print("\n" + "=" * 80)
print("RAW JSON RESPONSE:")
print("=" * 80)
print(json.dumps(users, indent=2))
