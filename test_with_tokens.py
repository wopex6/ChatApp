"""Test signal storage with actual browser tokens"""
import requests
import time

API = "http://localhost:5001/api"

test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo3Nywicm9sZSI6InVzZXIiLCJleHAiOjE3NjQ4MDY3NDB9.QfPwzKbDwi7IFhTk40cqmrtfxVr_ECeooELXzHCkJ7M"
ken_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo2MCwicm9sZSI6ImFkbWluaXN0cmF0b3IiLCJleHAiOjE3NjQ4MDU3OTl9.0lWFOVS86-SDQsFAv5Y4HtQ30_cUAFs_K6DzyVtVS-k"

print("=" * 60)
print("TESTING SIGNAL FLOW")
print("=" * 60)

# Test user (77) sends signal to Ken (60)
print("\n[1] Test user (77) sending signal to Ken (60)...")
signal_resp = requests.post(f"{API}/call/signal", 
    headers={
        "Authorization": f"Bearer {test_token}", 
        "Content-Type": "application/json"
    },
    json={
        "target_user_id": 60,
        "signal": {"type": "test-from-script", "message": "Direct API test", "timestamp": time.time()}
    }
)
print(f"   Status: {signal_resp.status_code}")
print(f"   Response: {signal_resp.json()}")

# Small delay
time.sleep(0.2)

# Ken (60) retrieves signals
print("\n[2] Ken (60) retrieving signals...")
get_resp = requests.get(f"{API}/call/signals",
    headers={"Authorization": f"Bearer {ken_token}"}
)
print(f"   Status: {get_resp.status_code}")
signals = get_resp.json()
print(f"   Signals: {signals}")
print(f"   Count: {len(signals)}")

print("\n" + "=" * 60)
if len(signals) > 0:
    print("✅ SUCCESS! Signal storage working!")
    print(f"   Signal from user: {signals[0]['from']}")
    print(f"   Signal type: {signals[0]['signal']['type']}")
else:
    print("❌ FAIL! No signals received")
    print("   Possible causes:")
    print("   1. Multiple servers running (requests go to different instances)")
    print("   2. In-memory storage cleared between requests")
    print("   3. Wrong user ID being used")
print("=" * 60)
