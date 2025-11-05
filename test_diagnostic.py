"""
Quick Diagnostic Test - Checks if ChatApp basic functionality is working
No Playwright needed - uses requests library for API testing
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001/api"
TEST_USER = f"diagtest_{int(time.time())}"
TEST_PASSWORD = "DiagTest123!"
ADMIN_USER = "Ken Tse"
ADMIN_PASSWORD = "KenTse2025!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}🧪 {name}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def print_pass(message):
    print(f"{Colors.GREEN}✅ PASS: {message}{Colors.RESET}")

def print_fail(message):
    print(f"{Colors.RED}❌ FAIL: {message}{Colors.RESET}")

def print_info(message):
    print(f"   {message}")

def test_api():
    results = {'passed': 0, 'failed': 0}
    
    print("\n" + "="*60)
    print("🔍 CHATAPP DIAGNOSTIC TEST")
    print("="*60)
    
    # TEST 1: Health Check
    print_test("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_pass("Server is responding")
            results['passed'] += 1
        else:
            print_fail(f"Server returned {response.status_code}")
            results['failed'] += 1
    except Exception as e:
        print_fail(f"Cannot connect to server: {e}")
        results['failed'] += 1
        print("\n⚠️  Server may not be running. Start with: python chatapp_simple.py")
        return results
    
    # TEST 2: User Signup
    print_test("User Signup")
    try:
        signup_data = {
            'username': TEST_USER,
            'email': f'{TEST_USER}@test.com',
            'password': TEST_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data, timeout=5)
        
        if response.status_code in [200, 201]:
            data = response.json()
            user_token = data.get('token')
            if user_token:
                print_pass(f"User signup successful")
                print_info(f"Username: {TEST_USER}")
                print_info(f"Token received: {user_token[:20]}...")
                results['passed'] += 1
            else:
                print_fail("No token received")
                results['failed'] += 1
                user_token = None
        else:
            print_fail(f"Signup failed: {response.status_code}")
            print_info(f"Response: {response.text}")
            results['failed'] += 1
            user_token = None
    except Exception as e:
        print_fail(f"Signup error: {e}")
        results['failed'] += 1
        user_token = None
    
    # TEST 3: Admin Login
    print_test("Admin Login")
    try:
        login_data = {
            'username': ADMIN_USER,
            'password': ADMIN_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            admin_token = data.get('token')
            if admin_token:
                print_pass("Admin login successful")
                print_info(f"Token received: {admin_token[:20]}...")
                results['passed'] += 1
            else:
                print_fail("No token received")
                results['failed'] += 1
                admin_token = None
        else:
            print_fail(f"Login failed: {response.status_code}")
            print_info(f"Response: {response.text}")
            results['failed'] += 1
            admin_token = None
    except Exception as e:
        print_fail(f"Login error: {e}")
        results['failed'] += 1
        admin_token = None
    
    # TEST 4: User Sends Message
    if user_token:
        print_test("User Sends Message")
        try:
            message_data = {
                'message': f"Test message from user at {time.time()}"
            }
            headers = {'Authorization': f'Bearer {user_token}'}
            response = requests.post(f"{BASE_URL}/messages/send", json=message_data, headers=headers, timeout=5)
            
            if response.status_code in [200, 201]:
                print_pass("Message sent successfully")
                results['passed'] += 1
            else:
                print_fail(f"Message send failed: {response.status_code}")
                print_info(f"Response: {response.text}")
                results['failed'] += 1
        except Exception as e:
            print_fail(f"Send error: {e}")
            results['failed'] += 1
    else:
        print_test("User Sends Message")
        print_fail("Skipped - No user token")
        results['failed'] += 1
    
    # TEST 5: Admin Gets Conversations
    if admin_token:
        print_test("Admin Gets Conversations")
        try:
            headers = {'Authorization': f'Bearer {admin_token}'}
            response = requests.get(f"{BASE_URL}/admin/conversations", headers=headers, timeout=5)
            
            if response.status_code == 200:
                conversations = response.json()
                print_pass(f"Retrieved {len(conversations)} conversations")
                
                # Check if our test user is in the list
                found_user = any(c.get('username') == TEST_USER for c in conversations)
                if found_user:
                    print_info(f"Test user '{TEST_USER}' found in conversations")
                else:
                    print_info(f"Test user '{TEST_USER}' not yet in conversations (may need time)")
                
                results['passed'] += 1
            else:
                print_fail(f"Failed: {response.status_code}")
                results['failed'] += 1
        except Exception as e:
            print_fail(f"Error: {e}")
            results['failed'] += 1
    else:
        print_test("Admin Gets Conversations")
        print_fail("Skipped - No admin token")
        results['failed'] += 1
    
    # TEST 6: User Gets Messages
    if user_token:
        print_test("User Gets Messages")
        try:
            headers = {'Authorization': f'Bearer {user_token}'}
            response = requests.get(f"{BASE_URL}/messages", headers=headers, timeout=5)
            
            if response.status_code == 200:
                messages = response.json()
                print_pass(f"Retrieved {len(messages)} messages")
                results['passed'] += 1
            else:
                print_fail(f"Failed: {response.status_code}")
                results['failed'] += 1
        except Exception as e:
            print_fail(f"Error: {e}")
            results['failed'] += 1
    else:
        print_test("User Gets Messages")
        print_fail("Skipped - No user token")
        results['failed'] += 1
    
    # TEST 7: Admin Gets User List
    if admin_token:
        print_test("Admin Gets User List")
        try:
            headers = {'Authorization': f'Bearer {admin_token}'}
            response = requests.get(f"{BASE_URL}/admin/users", headers=headers, timeout=5)
            
            if response.status_code == 200:
                users = response.json()
                print_pass(f"Retrieved {len(users)} users")
                
                # Check if our test user exists
                found = any(u.get('username') == TEST_USER for u in users)
                if found:
                    print_info(f"Test user '{TEST_USER}' exists in database")
                
                results['passed'] += 1
            else:
                print_fail(f"Failed: {response.status_code}")
                results['failed'] += 1
        except Exception as e:
            print_fail(f"Error: {e}")
            results['failed'] += 1
    else:
        print_test("Admin Gets User List")
        print_fail("Skipped - No admin token")
        results['failed'] += 1
    
    # Summary
    print("\n" + "="*60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*60)
    total = results['passed'] + results['failed']
    print(f"\nTotal Tests: {total}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.RESET}")
    
    if results['failed'] == 0:
        print(f"\n{Colors.GREEN}{'='*60}")
        print("✅ ALL API TESTS PASSED!")
        print("Core functionality is working correctly.")
        print(f"{'='*60}{Colors.RESET}\n")
    else:
        print(f"\n{Colors.YELLOW}{'='*60}")
        print(f"⚠️  {results['failed']} test(s) failed")
        print("Check the errors above for details.")
        print(f"{'='*60}{Colors.RESET}\n")
    
    return results

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║          CHATAPP DIAGNOSTIC TEST                          ║
║                                                           ║
║  Quick API test to verify core functionality             ║
║  No browser automation needed                            ║
╚══════════════════════════════════════════════════════════╝

⚠️  Requirements:
   - ChatApp server running on http://localhost:5001
   - Python requests library: pip install requests

Starting diagnostic tests...
""")
    
    test_api()
    
    print("\n💡 Next Steps:")
    print("   - If tests passed: Use MANUAL_TEST_CHECKLIST.md for full testing")
    print("   - If tests failed: Check server logs and error messages above")
    print("   - For browser testing: Open http://localhost:5001 manually")
