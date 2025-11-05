"""Test with debug endpoint"""
import requests
import time

API = "http://localhost:5001/api"
test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo3Nywicm9sZSI6InVzZXIiLCJleHAiOjE3NjQ4MDY3NDB9.QfPwzKbDwi7IFhTk40cqmrtfxVr_ECeooELXzHCkJ7M"

print("1. Check initial state:")
r = requests.get(f"{API}/debug/signals")
print(f"   {r.json()}\n")

print("2. Send signal from user 77 to user 60:")
r = requests.post(f"{API}/call/signal", 
    headers={"Authorization": f"Bearer {test_token}", "Content-Type": "application/json"},
    json={"target_user_id": 60, "signal": {"type": "test", "data": "hello"}}
)
print(f"   Status: {r.status_code}, Response: {r.json()}\n")

print("3. Check signals in memory IMMEDIATELY after send:")
r = requests.get(f"{API}/debug/signals")
print(f"   {r.json()}\n")

print("✅ If you see user_id 60 in keys with 1 signal, storage is working!")
print("❌ If keys is empty, signals are not being stored!")
