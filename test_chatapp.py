"""
Test script for ChatApp - verify all endpoints work
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_health_check():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"✅ Health Check: {response.json()}")
    return response.status_code == 200

def test_login_ken_tse():
    """Test login as Ken Tse"""
    data = {
        "username": "Ken Tse",
        "password": "KenTse2025!"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Ken Tse Login: Success")
        print(f"   User: {result['user']['username']}")
        print(f"   Role: {result['user']['role']}")
        return result['token']
    else:
        print(f"❌ Ken Tse Login Failed: {response.json()}")
        return None

def test_signup_user():
    """Test user signup"""
    data = {
        "username": "test_user",
        "email": "test@chatapp.com",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/signup", json=data)
    if response.status_code == 201:
        result = response.json()
        print(f"✅ User Signup: Success")
        print(f"   User: {result['user']['username']}")
        return result['token']
    elif response.status_code == 409:
        # User already exists, try login
        print("⚠️  User already exists, attempting login...")
        login_data = {
            "username": "test_user",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ User Login: Success")
            return result['token']
    print(f"❌ User Signup/Login Failed: {response.json()}")
    return None

def test_send_message(token, message_text):
    """Test sending a message"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message_text}
    response = requests.post(f"{BASE_URL}/api/messages/send", json=data, headers=headers)
    if response.status_code == 201:
        print(f"✅ Message Sent: {message_text[:50]}...")
        return True
    else:
        print(f"❌ Send Message Failed: {response.json()}")
        return False

def test_get_messages(token):
    """Test getting messages"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/messages", headers=headers)
    if response.status_code == 200:
        messages = response.json()
        print(f"✅ Get Messages: {len(messages)} messages retrieved")
        return messages
    else:
        print(f"❌ Get Messages Failed: {response.json()}")
        return []

def test_admin_conversations(token):
    """Test getting all conversations (admin only)"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/admin/conversations", headers=headers)
    if response.status_code == 200:
        conversations = response.json()
        print(f"✅ Admin Conversations: {len(conversations)} conversations")
        for conv in conversations[:3]:
            print(f"   - {conv['username']}: {conv['unread_count']} unread")
        return conversations
    else:
        print(f"❌ Admin Conversations Failed: {response.json()}")
        return []

def main():
    """Run all tests"""
    print("=" * 60)
    print("ChatApp API Tests")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. Testing Health Check...")
    test_health_check()
    
    # Test 2: Ken Tse login
    print("\n2. Testing Ken Tse Login...")
    ken_token = test_login_ken_tse()
    
    # Test 3: User signup/login
    print("\n3. Testing User Signup/Login...")
    user_token = test_signup_user()
    
    if user_token:
        # Test 4: User sends message
        print("\n4. Testing User Sends Message...")
        test_send_message(user_token, "Hello Ken Tse! This is a test message from ChatApp.")
        
        # Test 5: User gets messages
        print("\n5. Testing Get Messages...")
        messages = test_get_messages(user_token)
    
    if ken_token:
        # Test 6: Ken Tse views all conversations
        print("\n6. Testing Ken Tse Views Conversations...")
        conversations = test_admin_conversations(ken_token)
        
        # Test 7: Ken Tse replies
        print("\n7. Testing Ken Tse Sends Reply...")
        if conversations:
            user_id = conversations[0]['user_id']
            headers = {"Authorization": f"Bearer {ken_token}"}
            data = {
                "message": "Hi! This is Ken Tse replying to your message.",
                "user_id": user_id
            }
            response = requests.post(f"{BASE_URL}/api/messages/send", json=data, headers=headers)
            if response.status_code == 201:
                print("✅ Ken Tse Reply Sent")
            else:
                print(f"❌ Ken Tse Reply Failed: {response.json()}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server")
        print("   Make sure chatapp_simple.py is running on port 5001")
    except Exception as e:
        print(f"❌ Error: {e}")
