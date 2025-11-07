"""
Check users in Railway PostgreSQL database
Requires DATABASE_URL environment variable
"""
import os
import sys

# Set DATABASE_URL for Railway PostgreSQL
# You need to get this from Railway dashboard -> PostgreSQL service -> Variables -> DATABASE_URL
# Example: postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway

# Check if DATABASE_URL is provided
if len(sys.argv) < 2:
    print("=" * 80)
    print("HOW TO USE:")
    print("=" * 80)
    print("1. Go to Railway Dashboard")
    print("2. Click on PostgreSQL service (NOT ChatApp)")
    print("3. Go to 'Variables' tab")
    print("4. Copy the DATABASE_URL value")
    print("5. Run:")
    print('   python check_railway_users.py "postgresql://postgres:..."')
    print("=" * 80)
    sys.exit(1)

DATABASE_URL = sys.argv[1]
os.environ['DATABASE_URL'] = DATABASE_URL

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    print("=" * 80)
    print("CONNECTING TO RAILWAY POSTGRESQL...")
    print("=" * 80)
    
    # Fix Railway's postgres:// to postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("✅ Connected successfully!")
    print("\n" + "=" * 80)
    print("ALL USERS IN RAILWAY DATABASE:")
    print("=" * 80)
    
    cursor.execute('''
        SELECT id, username, email, user_role, is_deleted, created_at 
        FROM users 
        ORDER BY created_at DESC
    ''')
    
    users = cursor.fetchall()
    
    if len(users) == 0:
        print("⚠️  NO USERS FOUND - Database is empty!")
    else:
        for user in users:
            user_id, username, email, role, is_deleted, created = user
            status = '[DELETED]' if is_deleted else '✓'
            print(f'{status:10} | ID: {user_id:3} | {username:20} | {role:15} | {email:30}')
    
    print(f"\nTotal users: {len(users)}")
    
    print("\n" + "=" * 80)
    print("USERS THAT SHOULD APPEAR IN ADMIN LIST:")
    print("(Active users, not administrators)")
    print("=" * 80)
    
    cursor.execute('''
        SELECT id, username, email, user_role
        FROM users 
        WHERE is_deleted = 0 AND user_role != 'administrator'
        ORDER BY username ASC
    ''')
    
    active_users = cursor.fetchall()
    
    if len(active_users) == 0:
        print("⚠️  NO ACTIVE NON-ADMIN USERS - List would be empty!")
    else:
        for user in active_users:
            user_id, username, email, role = user
            print(f'✓ ID: {user_id:3} | {username:20} | {role:15} | {email:30}')
            if username.lower() == 'olha':
                print("   👆 OLHA FOUND! ✅")
    
    print(f"\nTotal users that should show in admin list: {len(active_users)}")
    
    # Check for Olha specifically
    print("\n" + "=" * 80)
    print("SEARCHING FOR 'OLHA':")
    print("=" * 80)
    
    cursor.execute('''
        SELECT id, username, email, user_role, is_deleted
        FROM users 
        WHERE LOWER(username) = 'olha'
    ''')
    
    olha = cursor.fetchone()
    if olha:
        user_id, username, email, role, is_deleted = olha
        status = "DELETED" if is_deleted else "ACTIVE"
        print(f"✅ Found Olha!")
        print(f"   ID: {user_id}")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Role: {role}")
        print(f"   Status: {status}")
        
        if is_deleted:
            print("\n⚠️  Olha is DELETED - won't appear in admin list")
        elif role == 'administrator':
            print("\n⚠️  Olha is ADMINISTRATOR - won't appear in admin list")
        else:
            print("\n✅ Olha SHOULD appear in admin list!")
    else:
        print("❌ Olha NOT FOUND in Railway database")
        print("   She only exists in your local SQLite database")
        print("   You need to create her account again on Railway")
    
    conn.close()
    
except ImportError:
    print("❌ ERROR: psycopg2 not installed")
    print("   Run: pip install psycopg2-binary")
except Exception as e:
    print(f"❌ ERROR: {e}")
