"""
Manual test to see what happens with password change
"""
import requests

BASE_URL = "http://localhost:5001/api"

# Use Ken Tse to test
USERNAME = "Ken Tse"
CURRENT_PASSWORD = "KenTse2025!"
NEW_PASSWORD = "TestNewPass123!"

print("\n" + "="*70)
print("🔐 MANUAL PASSWORD CHANGE TEST FOR KEN TSE")
print("="*70)

# Step 1: Login
print(f"\n1. Logging in as {USERNAME}")
response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": USERNAME,
    "password": CURRENT_PASSWORD
})

if response.status_code != 200:
    print(f"❌ Login failed: {response.json()}")
    exit(1)

data = response.json()
token = data['token']
print(f"✅ Login successful, token: {token[:30]}...")

# Step 2: Attempt password change
print(f"\n2. Attempting to change password")
print(f"   Current: {CURRENT_PASSWORD}")
print(f"   New: {NEW_PASSWORD}")

change_response = requests.post(f"{BASE_URL}/auth/change-password",
    headers={'Authorization': f'Bearer {token}'},
    json={
        "currentPassword": CURRENT_PASSWORD,
        "newPassword": NEW_PASSWORD
    }
)

print(f"\n📊 Response Status: {change_response.status_code}")
print(f"📊 Response Body: {change_response.json()}")

if change_response.status_code == 200:
    print("\n✅ Password change request accepted")
    
    # Step 3: Try new password
    print(f"\n3. Testing NEW password")
    test_response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": USERNAME,
        "password": NEW_PASSWORD
    })
    
    if test_response.status_code == 200:
        print("✅ NEW password works!")
        
        # Change back
        print(f"\n4. Changing back to original password")
        new_token = test_response.json()['token']
        restore_response = requests.post(f"{BASE_URL}/auth/change-password",
            headers={'Authorization': f'Bearer {new_token}'},
            json={
                "currentPassword": NEW_PASSWORD,
                "newPassword": CURRENT_PASSWORD
            }
        )
        
        if restore_response.status_code == 200:
            print("✅ Password restored to original")
        else:
            print(f"⚠️  Could not restore: {restore_response.json()}")
    else:
        print(f"❌ NEW password doesn't work: {test_response.json()}")
else:
    print(f"\n❌ Password change failed: {change_response.json()}")
