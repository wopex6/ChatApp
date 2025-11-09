"""
Check Olha's info in LOCAL database
"""
import sqlite3
import bcrypt

conn = sqlite3.connect('integrated_users.db')
cursor = conn.cursor()

print("=" * 80)
print("CHECKING OLHA IN LOCAL DATABASE")
print("=" * 80)

cursor.execute('''
    SELECT id, username, email, user_role, is_deleted, password_hash, created_at
    FROM users 
    WHERE LOWER(username) = 'olha'
''')

olha = cursor.fetchone()

if olha:
    user_id, username, email, role, is_deleted, pwd_hash, created = olha
    
    print(f"\n✅ Olha found in local database!")
    print(f"   ID: {user_id}")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Role: {role}")
    print(f"   Deleted: {is_deleted}")
    print(f"   Created: {created}")
    print(f"   Password hash: {pwd_hash[:50]}...")
    
    # Test if password is "Olha"
    print("\n" + "=" * 80)
    print("TESTING PASSWORD")
    print("=" * 80)
    
    test_passwords = ['Olha', 'olha', 'OLHA', 'Olha123', 'olha123']
    
    for test_pwd in test_passwords:
        try:
            if bcrypt.checkpw(test_pwd.encode('utf-8'), pwd_hash.encode('utf-8')):
                print(f"✅ PASSWORD IS: '{test_pwd}'")
                print(f"\n💡 Use this password to login as Olha")
                break
        except:
            pass
    else:
        print("❌ Password is NOT any of: " + ", ".join(test_passwords))
        print("\n   The password is something else.")
        print("   Check your records or reset it.")
else:
    print("\n❌ Olha NOT FOUND in local database")
    print("   She doesn't exist locally either!")

conn.close()
