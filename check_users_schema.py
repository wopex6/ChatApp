import sqlite3

conn = sqlite3.connect('integrated_users.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(users)')
print("Users table schema:")
for row in cursor.fetchall():
    print(row)
conn.close()
