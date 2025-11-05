"""
Test script for password change functionality
"""
import requests
import time

BASE_URL = "http://localhost:5001/api"

def test_password_change():
    print("\n" + "="*70)
    print("🔐 PASSWORD CHANGE TEST")
    print("="*70)
    
    # Create a test user
    username = f"pwtest_{int(time.time())}"
    password = "TestPass123!"
    new_password = "NewPass456!"
    
    print(f"\n1. Creating test user: {username}")
    signup_response = requests.post(f"{BASE_URL}/auth/signup", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": password
    })
    
    if signup_response.status_code != 201:
        print(f"❌ FAIL: Signup failed - {signup_response.json()}")
        return
    
    token = signup_response.json()['token']
    print(f"✅ User created, token: {token[:20]}...")
    
    # Test 1: Change password with correct current password
    print(f"\n2. Testing password change (correct current password)")
    change_response = requests.post(f"{BASE_URL}/auth/change-password", 
        headers={'Authorization': f'Bearer {token}'},
        json={
            "currentPassword": password,
            "newPassword": new_password
        }
    )
    
    if change_response.status_code == 200:
        print("✅ Password changed successfully!")
    else:
        print(f"❌ FAIL: {change_response.json()}")
        return
    
    # Test 2: Try to login with old password (should fail)
    print(f"\n3. Testing login with OLD password (should fail)")
    old_login = requests.post(f"{BASE_URL}/auth/login", json={
        "username": username,
        "password": password
    })
    
    if old_login.status_code != 200:
        print("✅ Old password rejected (correct!)")
    else:
        print("❌ FAIL: Old password still works (incorrect!)")
        return
    
    # Test 3: Login with new password (should succeed)
    print(f"\n4. Testing login with NEW password (should succeed)")
    new_login = requests.post(f"{BASE_URL}/auth/login", json={
        "username": username,
        "password": new_password
    })
    
    if new_login.status_code == 200:
        print("✅ New password works!")
        new_token = new_login.json()['token']
        print(f"   New token: {new_token[:20]}...")
    else:
        print(f"❌ FAIL: New password doesn't work - {new_login.json()}")
        return
    
    # Test 4: Try to change with wrong current password
    print(f"\n5. Testing password change with WRONG current password (should fail)")
    wrong_change = requests.post(f"{BASE_URL}/auth/change-password", 
        headers={'Authorization': f'Bearer {new_token}'},
        json={
            "currentPassword": "WrongPassword123!",
            "newPassword": "AnotherPass789!"
        }
    )
    
    if wrong_change.status_code != 200:
        print("✅ Wrong current password rejected (correct!)")
        print(f"   Error: {wrong_change.json().get('error', 'Unknown error')}")
    else:
        print("❌ FAIL: Wrong current password accepted (incorrect!)")
        return
    
    # Test 5: Change password again with correct credentials
    print(f"\n6. Testing second password change (correct credentials)")
    final_password = "FinalPass999!"
    second_change = requests.post(f"{BASE_URL}/auth/change-password", 
        headers={'Authorization': f'Bearer {new_token}'},
        json={
            "currentPassword": new_password,
            "newPassword": final_password
        }
    )
    
    if second_change.status_code == 200:
        print("✅ Second password change successful!")
    else:
        print(f"❌ FAIL: {second_change.json()}")
        return
    
    # Final verification
    print(f"\n7. Final verification - login with final password")
    final_login = requests.post(f"{BASE_URL}/auth/login", json={
        "username": username,
        "password": final_password
    })
    
    if final_login.status_code == 200:
        print("✅ Final password works!")
    else:
        print(f"❌ FAIL: Final password doesn't work - {final_login.json()}")
        return
    
    print("\n" + "="*70)
    print("🎉 ALL PASSWORD CHANGE TESTS PASSED!")
    print("="*70)
    print(f"\n✅ Test user: {username}")
    print(f"✅ Original password: {password}")
    print(f"✅ Changed to: {new_password}")
    print(f"✅ Changed again to: {final_password}")
    print(f"✅ All changes verified successfully!")
    
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           PASSWORD CHANGE FUNCTIONALITY TEST                     ║
╚══════════════════════════════════════════════════════════════════╝

Tests:
  1. Create test user
  2. Change password with correct credentials
  3. Verify old password doesn't work
  4. Verify new password works
  5. Reject wrong current password
  6. Allow multiple password changes
  
Requirements:
  - Server running on http://localhost:5001
  - Python requests: pip install requests
  
Starting test...
""")
    
    try:
        test_password_change()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server")
        print("   Make sure chatapp_simple.py is running on port 5001")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
