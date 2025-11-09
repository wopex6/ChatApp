"""
Fix Olha login issue - check if user exists and reset password if needed
"""
import sqlite3
import bcrypt
import sys

DB_PATH = 'chatapp.db'

def check_and_fix_user():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    username = 'Olha'
    
    # Check if user exists
    cursor.execute('SELECT id, username, is_deleted FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if not user:
        print(f"❌ User '{username}' does not exist in database")
        print(f"\n💡 Options:")
        print(f"1. Create new user 'Olha'")
        print(f"2. Check if username is spelled differently")
        
        choice = input(f"\nCreate user 'Olha'? (y/n): ").strip().lower()
        
        if choice == 'y':
            # Get password
            password = input("Enter password for Olha: ").strip()
            if not password:
                print("❌ Password cannot be empty")
                return
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create user
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, user_role, is_deleted)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, f'{username.lower()}@example.com', password_hash, 'user', 0))
            
            conn.commit()
            print(f"✅ User '{username}' created successfully!")
            print(f"   Username: {username}")
            print(f"   Password: {password}")
            print(f"   Role: user")
        else:
            # List all users
            cursor.execute('SELECT username, user_role, is_deleted FROM users ORDER BY username')
            users = cursor.fetchall()
            print(f"\n📋 Existing users:")
            for u in users:
                status = '(DELETED)' if u[2] else ''
                print(f"   - {u[0]} ({u[1]}) {status}")
    
    elif user[2]:  # is_deleted
        print(f"❌ User '{username}' exists but is DELETED")
        restore = input(f"Restore user '{username}'? (y/n): ").strip().lower()
        
        if restore == 'y':
            cursor.execute('UPDATE users SET is_deleted = 0 WHERE username = ?', (username,))
            conn.commit()
            print(f"✅ User '{username}' restored!")
            
            # Option to reset password
            reset_pwd = input("Reset password? (y/n): ").strip().lower()
            if reset_pwd == 'y':
                new_password = input("Enter new password: ").strip()
                if new_password:
                    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (password_hash, username))
                    conn.commit()
                    print(f"✅ Password reset for '{username}'")
                    print(f"   New password: {new_password}")
    
    else:
        print(f"✅ User '{username}' exists and is active")
        print(f"   User ID: {user[0]}")
        
        # Option to reset password
        reset_pwd = input("Reset password? (y/n): ").strip().lower()
        if reset_pwd == 'y':
            new_password = input("Enter new password: ").strip()
            if new_password:
                password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (password_hash, username))
                conn.commit()
                print(f"✅ Password reset for '{username}'")
                print(f"   New password: {new_password}")
        else:
            print(f"\n💡 If password is forgotten, run this script again and choose 'y' to reset")
    
    conn.close()

if __name__ == '__main__':
    print("🔍 Checking Olha's account...\n")
    try:
        check_and_fix_user()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
