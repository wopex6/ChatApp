"""Test signal storage directly via API"""
import requests
import time

API = "http://localhost:5001/api"

# Login as Ken Tse to get token
login_resp = requests.post(f"{API}/auth/login", json={
    "username": "Ken Tse",
    "password": "Ken123"
})
print(f"Ken login response: {login_resp.json()}")
if 'token' not in login_resp.json():
    print("❌ Ken login failed! Check password")
    exit(1)
ken_token = login_resp.json()['token']
print(f"✅ Ken logged in, token: {ken_token[:20]}...")

# Login as test user
login_resp2 = requests.post(f"{API}/auth/login", json={
    "username": "test",
    "password": "test"
})
test_token = login_resp2.json()['token']
print(f"✅ Test user logged in, token: {test_token[:20]}...")

# Test user (77) sends signal to Ken (60)
print("\n--- Sending signal from test user (77) to Ken (60) ---")
signal_resp = requests.post(f"{API}/call/signal", 
    headers={"Authorization": f"Bearer {test_token}", "Content-Type": "application/json"},
    json={
        "target_user_id": 60,
        "signal": {"type": "test-direct", "message": "Hello from script"}
    }
)
print(f"Signal send status: {signal_resp.status_code}")
print(f"Signal send response: {signal_resp.json()}")

# Immediately retrieve as Ken (60)
print("\n--- Ken (60) retrieving signals ---")
time.sleep(0.5)  # Small delay
get_resp = requests.get(f"{API}/call/signals",
    headers={"Authorization": f"Bearer {ken_token}"}
)
print(f"Get signals status: {get_resp.status_code}")
signals = get_resp.json()
print(f"Signals retrieved: {signals}")
print(f"Number of signals: {len(signals)}")

if len(signals) > 0:
    print("\n✅ SUCCESS! Signals are working!")
else:
    print("\n❌ FAIL! No signals received")
