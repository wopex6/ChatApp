import sqlite3

conn = sqlite3.connect('integrated_users.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM users WHERE is_deleted = 0')
active_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM users WHERE is_deleted = 1')
deleted_count = cursor.fetchone()[0]

print(f'📊 User Statistics:')
print(f'   Active users: {active_count}')
print(f'   Deleted users: {deleted_count}')
print(f'   Total: {active_count + deleted_count}')

print(f'\n👥 Recent Users (last 10):')
print('-' * 90)
cursor.execute('''
    SELECT username, email, user_role, created_at, is_deleted 
    FROM users 
    ORDER BY created_at DESC 
    LIMIT 10
''')

for user in cursor.fetchall():
    username, email, role, created, is_deleted = user
    status = '[DELETED]' if is_deleted else '✓'
    created_str = created[:19] if created else 'Unknown'
    print(f'{status:10} | {username[:20]:20} | {email[:30]:30} | {role:10} | {created_str}')

conn.close()
