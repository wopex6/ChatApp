import sqlite3

conn = sqlite3.connect('integrated_users.db')
cursor = conn.cursor()

print('=' * 80)
print('ALL USERS IN DATABASE:')
print('=' * 80)
cursor.execute('''
    SELECT id, username, email, user_role, is_deleted, created_at 
    FROM users 
    ORDER BY created_at DESC
''')

for user in cursor.fetchall():
    user_id, username, email, role, is_deleted, created = user
    status = '[DELETED]' if is_deleted else '✓'
    print(f'{status:10} | ID: {user_id:3} | {username:20} | {role:15} | {email:30}')

print('\n' + '=' * 80)
print('USERS THAT SHOULD APPEAR IN ADMIN LIST:')
print('(Active users, not administrators)')
print('=' * 80)
cursor.execute('''
    SELECT id, username, email, user_role, is_deleted
    FROM users 
    WHERE is_deleted = 0 AND user_role != 'administrator'
    ORDER BY username ASC
''')

results = cursor.fetchall()
if len(results) == 0:
    print('⚠️  NO USERS FOUND - List would be empty!')
else:
    for user in results:
        user_id, username, email, role, is_deleted = user
        print(f'✓ ID: {user_id:3} | {username:20} | {role:15} | {email:30}')

print(f'\nTotal users that should show: {len(results)}')

conn.close()
