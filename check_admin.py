from chatapp_database import ChatAppDatabase

db = ChatAppDatabase()
admin = db.get_admin_user()
print(f"Admin user from database: {admin}")

# Get all admin users
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, username, user_role FROM users WHERE user_role = 'administrator' AND is_deleted = 0")
admins = cursor.fetchall()
conn.close()

print(f"\nAll admin users:")
for a in admins:
    print(f"  ID: {a[0]}, Username: {a[1]}, Role: {a[2]}")
