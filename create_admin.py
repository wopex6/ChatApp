#!/usr/bin/env python3
"""Create admin account for ChatApp on Railway"""

from chatapp_database import ChatAppDatabase
import sys

# Initialize database
db = ChatAppDatabase()

# Check if admin already exists
admin = db.get_admin_user()

if admin:
    print(f"\n✅ Admin account already exists:")
    print(f"   Username: {admin['username']}")
    print(f"   Email: {admin['email']}")
    print(f"\nUse these credentials to login:")
    print(f"   Email: {admin['email']}")
    print(f"   Password: admin123")
    sys.exit(0)

# Create admin account
print("\n🔧 Creating admin account...")

username = "Ken Tse"
email = "ken@chatapp.com"
password = "admin123"

user_id = db.create_user(username, email, password)

if user_id:
    # Set as administrator
    db.update_user_role(user_id, 'administrator')
    
    print(f"\n✅ Admin account created successfully!")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"\n🔐 Login with:")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
else:
    print("\n❌ Failed to create admin account")
