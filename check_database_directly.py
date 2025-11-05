"""
Check database directly to see if password change actually works
"""
import sqlite3
import bcrypt

DB_PATH = "integrated_users.db"  # This is the actual database file used by the app

def check_recent_user():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get most recent user (from our test)
    cursor.execute("""
        SELECT id, username, email, password_hash, created_at 
        FROM users 
        WHERE username LIKE 'pwtest_%'
        ORDER BY created_at DESC 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    
    if not result:
        print("❌ No test user found")
        conn.close()
        return
    
    user_id, username, email, password_hash, created_at = result
    
    print("\n" + "="*70)
    print("🔍 MOST RECENT TEST USER")
    print("="*70)
    print(f"User ID: {user_id}")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Created: {created_at}")
    print(f"Password Hash: {password_hash[:50]}...")
    
    # Test passwords
    test_passwords = {
        "TestPass123!": "Original password",
        "NewPass456!": "New password (should work if change succeeded)"
    }
    
    print("\n" + "="*70)
    print("🔐 PASSWORD VERIFICATION")
    print("="*70)
    
    for password, description in test_passwords.items():
        try:
            matches = bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
            status = "✅ MATCHES" if matches else "❌ NO MATCH"
            print(f"{status} - {description}: '{password}'")
        except Exception as e:
            print(f"❌ ERROR checking '{password}': {e}")
    
    print("\n" + "="*70)
    print("📊 CONCLUSION")
    print("="*70)
    
    # Check which password works
    original_works = bcrypt.checkpw(b"TestPass123!", password_hash.encode('utf-8'))
    new_works = bcrypt.checkpw(b"NewPass456!", password_hash.encode('utf-8'))
    
    if original_works and not new_works:
        print("❌ BUG CONFIRMED: Password change FAILED!")
        print("   The database still has the ORIGINAL password hash.")
        print("   This means the UPDATE statement didn't work or didn't commit.")
    elif new_works and not original_works:
        print("✅ Password change WORKED!")
        print("   The database has the NEW password hash.")
    elif original_works and new_works:
        print("⚠️  WEIRD: Both passwords work (shouldn't happen)")
    else:
        print("⚠️  WEIRD: Neither password works (database corruption?)")
    
    conn.close()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          DATABASE DIRECT CHECK                                   ║
╚══════════════════════════════════════════════════════════════════╝

This will check the actual database to see if password change worked.
Looking for most recent test user (pwtest_XXXXX)...
""")
    
    try:
        check_recent_user()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
