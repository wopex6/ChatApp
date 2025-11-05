"""
Test login directly with API to see what's happening
"""
import requests

BASE_URL = "http://localhost:5001/api"
TEST_USERNAME = "pwtest_1762147033"  # Most recent test user
PASSWORDS = {
    "old": "TestPass123!",
    "new": "NewPass456!"
}

print("\n" + "="*70)
print("🔐 DIRECT LOGIN TEST")
print("="*70)
print(f"\nTesting login for user: {TEST_USERNAME}")

for label, password in PASSWORDS.items():
    print(f"\n📝 Trying {label} password: '{password}'")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": TEST_USERNAME,
            "password": password
        })
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ LOGIN SUCCESSFUL!")
            print(f"   Token: {data.get('token', '')[:30]}...")
            print(f"   User: {data.get('user', {}).get('username')}")
        else:
            error = response.json().get('error', 'Unknown error')
            print(f"   ❌ LOGIN FAILED: {error}")
    
    except requests.exceptions.ConnectionError:
        print(f"   ❌ ERROR: Cannot connect to server")
        break
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

print("\n" + "="*70)
print("📊 SUMMARY")
print("="*70)
print("\n✅ Database shows: NEW password is stored correctly")
print("🧪 Now testing if login API works with that password...")
