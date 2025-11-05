"""Test the /api/admin/users endpoint"""
import requests

# Login as Ken - try different passwords
passwords = ["admin123", "Ken123", "password"]
token = None

for pwd in passwords:
    login_resp = requests.post("http://localhost:5001/api/auth/login", json={
        "username": "Ken Tse",
        "password": pwd
    })
    if login_resp.status_code == 200:
        token = login_resp.json()['token']
        print(f"✅ Logged in as Ken Tse with password: {pwd}")
        break

if not token:
    print(f"❌ Login failed with all passwords")
    exit(1)

# Get users
users_resp = requests.get("http://localhost:5001/api/admin/users", 
    headers={"Authorization": f"Bearer {token}"}
)

print(f"\nStatus: {users_resp.status_code}")
print(f"Response: {users_resp.json()}")
