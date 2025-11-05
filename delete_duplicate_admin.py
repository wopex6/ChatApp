from chatapp_database import ChatAppDatabase

db = ChatAppDatabase()
conn = db.get_connection()
cursor = conn.cursor()

# Delete the old 'administrator' account (ID 47)
cursor.execute("UPDATE users SET is_deleted = 1 WHERE id = 47")
conn.commit()

print("✅ Deleted duplicate admin account (ID 47)")
print("✅ Only 'Ken Tse' (ID 60) remains as admin")

conn.close()
