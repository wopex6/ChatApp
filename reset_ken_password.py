import sqlite3
import bcrypt

# Connect to the database
conn = sqlite3.connect('integrated_users.db')
cursor = conn.cursor()

# Hash the password "123" using bcrypt
password = "123"
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Update Ken Tse's password
cursor.execute("""
    UPDATE users 
    SET password_hash = ? 
    WHERE username = 'Ken Tse' OR username = 'Ken' OR username LIKE '%Ken%'
""", (hashed_password,))

conn.commit()

# Verify the update
cursor.execute("SELECT id, username, email FROM users WHERE username LIKE '%Ken%'")
result = cursor.fetchone()

if result:
    print(f"✓ Password reset successful for user: {result[1]}")
    print(f"  User ID: {result[0]}")
    print(f"  Email: {result[2]}")
    print(f"  New password: 123")
else:
    print("✗ User 'Ken' not found in database")
    # Show all users
    cursor.execute("SELECT id, username, email FROM users")
    all_users = cursor.fetchall()
    print("\nAll users in database:")
    for user in all_users:
        print(f"  ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")

conn.close()
