"""
Test what file the server is actually serving
"""
import os

# Read the actual file
with open('chatapp_login_only.html', 'r', encoding='utf-8') as f:
    disk_content = f.read()

# Get what the server is serving
import requests
response = requests.get('http://localhost:5001/')
served_content = response.text

# Check if they match
if disk_content == served_content:
    print("✅ Server is serving the CORRECT file from disk")
else:
    print("❌ Server is serving DIFFERENT content than what's on disk!")
    print(f"\nFile on disk size: {len(disk_content)} bytes")
    print(f"Served content size: {len(served_content)} bytes")
    
    # Check for the key difference
    if '<!-- Error/Success Messages (moved below button) -->' in disk_content:
        print("\n✅ Disk file HAS the moved error messages")
    else:
        print("\n❌ Disk file DOES NOT have moved error messages")
        
    if '<!-- Error/Success Messages (moved below button) -->' in served_content:
        print("✅ Served content HAS the moved error messages")
    else:
        print("❌ Served content DOES NOT have moved error messages")
    
    # Find where they differ
    print("\n" + "="*80)
    print("FINDING FIRST DIFFERENCE:")
    print("="*80)
    for i, (c1, c2) in enumerate(zip(disk_content, served_content)):
        if c1 != c2:
            print(f"First difference at character {i}")
            print(f"Disk: ...{disk_content[max(0,i-50):i+50]}...")
            print(f"Server: ...{served_content[max(0,i-50):i+50]}...")
            break
