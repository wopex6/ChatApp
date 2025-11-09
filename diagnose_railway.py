"""
Comprehensive Railway PostgreSQL diagnosis
Run this to check what's actually in the database
"""
import sys
import os

if len(sys.argv) < 2:
    print("=" * 80)
    print("USAGE: python diagnose_railway.py <DATABASE_URL>")
    print("=" * 80)
    print("\nGet DATABASE_URL from:")
    print("  Railway Dashboard → PostgreSQL service → Variables → DATABASE_URL")
    print("\nExample:")
    print('  python diagnose_railway.py "postgresql://postgres:..."')
    sys.exit(1)

DATABASE_URL = sys.argv[1]

try:
    import psycopg2
    
    # Fix Railway's postgres:// to postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    print("=" * 80)
    print("CONNECTING TO RAILWAY POSTGRESQL")
    print("=" * 80)
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print("✅ Connected!\n")
    
    # 1. Check if tables exist
    print("=" * 80)
    print("1. CHECKING TABLES")
    print("=" * 80)
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    if tables:
        for table in tables:
            print(f"  ✅ {table[0]}")
    else:
        print("  ❌ NO TABLES FOUND!")
        print("  Database might not be initialized!")
        conn.close()
        sys.exit(1)
    
    # 2. Check users table
    print("\n" + "=" * 80)
    print("2. ALL USERS IN DATABASE")
    print("=" * 80)
    cursor.execute("""
        SELECT id, username, email, user_role, is_deleted, created_at 
        FROM users 
        ORDER BY created_at DESC
    """)
    users = cursor.fetchall()
    
    if len(users) == 0:
        print("❌ NO USERS IN DATABASE!")
        print("\nThis explains:")
        print("  - Why user list is empty")
        print("  - Why Olha can't login (doesn't exist)")
        print("  - Why signup might fail (if trying duplicate from local)")
        print("\n💡 SOLUTION: You need to create users in Railway!")
    else:
        print(f"Total users: {len(users)}\n")
        for user in users:
            user_id, username, email, role, is_deleted, created = user
            status = '[DELETED]' if is_deleted else '✓'
            print(f'{status:10} | ID:{user_id:3} | {username:20} | {role:15} | {email:30}')
    
    # 3. Check for Olha specifically
    print("\n" + "=" * 80)
    print("3. SEARCHING FOR 'OLHA'")
    print("=" * 80)
    cursor.execute("""
        SELECT id, username, email, user_role, is_deleted, password_hash
        FROM users 
        WHERE LOWER(username) = 'olha'
    """)
    olha = cursor.fetchone()
    
    if olha:
        user_id, username, email, role, is_deleted, pwd_hash = olha
        print(f"✅ Olha EXISTS in Railway!")
        print(f"   ID: {user_id}")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Role: {role}")
        print(f"   Deleted: {is_deleted}")
        print(f"   Password hash: {pwd_hash[:50]}...")
        
        if is_deleted:
            print("\n⚠️  Olha is DELETED! Restore her to login.")
    else:
        print("❌ Olha DOES NOT EXIST in Railway!")
        print("\nThis means:")
        print("  - Olha only exists in your LOCAL database")
        print("  - You need to SIGNUP Olha again on Railway")
        print("  - Or admin needs to create the account")
    
    # 4. Check admin users
    print("\n" + "=" * 80)
    print("4. ADMINISTRATOR ACCOUNTS")
    print("=" * 80)
    cursor.execute("""
        SELECT id, username, email, is_deleted
        FROM users 
        WHERE user_role = 'administrator'
        ORDER BY id
    """)
    admins = cursor.fetchall()
    
    if len(admins) == 0:
        print("❌ NO ADMIN ACCOUNTS!")
        print("   You won't be able to access admin features!")
    else:
        for admin in admins:
            admin_id, username, email, is_deleted = admin
            status = '[DELETED]' if is_deleted else '✓'
            print(f'{status:10} | ID:{admin_id:3} | {username:20} | {email:30}')
    
    # 5. Test the admin query
    print("\n" + "=" * 80)
    print("5. TESTING ADMIN USER LIST QUERY")
    print("=" * 80)
    try:
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.user_role,
                   (SELECT COUNT(*) FROM admin_messages WHERE user_id = u.id) as message_count,
                   (SELECT MAX(timestamp) FROM admin_messages WHERE user_id = u.id) as last_message_time,
                   (SELECT COUNT(*) FROM admin_messages WHERE user_id = u.id AND sender_type = 'user' AND is_read = 0) as unread_count
            FROM users u
            WHERE u.is_deleted = 0 AND u.user_role != 'administrator'
            ORDER BY 
                CASE WHEN (SELECT MAX(timestamp) FROM admin_messages WHERE user_id = u.id) IS NULL THEN 0 ELSE 1 END,
                (SELECT MAX(timestamp) FROM admin_messages WHERE user_id = u.id) DESC, 
                u.username ASC
        ''')
        results = cursor.fetchall()
        print(f"✅ Query succeeded! Returned {len(results)} users")
        
        if len(results) == 0:
            print("   List is empty because:")
            print("   - No non-admin users exist")
            print("   - OR all users are deleted")
            print("   - OR all users are administrators")
        else:
            print("\n   Users that should appear in admin list:")
            for row in results:
                print(f"   - {row[1]} ({row[3]})")
    except Exception as e:
        print(f"❌ Query FAILED: {e}")
        print("   This is why the admin user list is empty!")
    
    # 6. Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if len(users) == 0:
        print("🔴 DATABASE IS EMPTY")
        print("\n   Next steps:")
        print("   1. Use Railway signup to create Olha")
        print("   2. Password will be whatever you choose during signup")
        print("   3. Olha will then appear in admin user list")
    elif olha:
        print("🟢 OLHA EXISTS")
        if is_deleted:
            print("   ⚠️  But she's deleted - restore her first")
        else:
            print("   ✅ Should be able to login")
            print("   Password: Whatever was set when account was created")
            print("   (NOT necessarily 'Olha' - check your records)")
    else:
        print("🟡 DATABASE HAS USERS, BUT NOT OLHA")
        print(f"   Found {len(users)} other users")
        print("   Create Olha account via signup")
    
    conn.close()
    
except ImportError:
    print("❌ psycopg2 not installed")
    print("   Run: pip install psycopg2-binary")
except Exception as e:
    print(f"❌ ERROR: {e}")
