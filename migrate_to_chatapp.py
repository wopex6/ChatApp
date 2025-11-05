"""
Migration script to convert AI-powered platform to simple ChatApp
- Removes AI-related tables
- Updates sender_type from 'admin' to 'ken_tse' (optional - keeping 'admin' works too)
- Backs up current database
- Creates Ken Tse account
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
import bcrypt

def backup_database(db_path):
    """Create a backup of the current database"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"✅ Database backed up to: {backup_path}")
    return backup_path

def remove_ai_tables(db_path):
    """Remove AI-related tables from database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables_to_remove = [
        'ai_conversations',
        'messages',  # AI messages, not admin_messages
        'psychology_traits',
        'user_interactions',
        'ai_chat_sessions'
    ]
    
    for table in tables_to_remove:
        try:
            cursor.execute(f'DROP TABLE IF EXISTS {table}')
            print(f"✅ Removed table: {table}")
        except sqlite3.Error as e:
            print(f"⚠️  Error removing {table}: {e}")
    
    conn.commit()
    conn.close()

def create_ken_tse_account(db_path, password="KenTse2025!"):
    """Create Ken Tse administrator account"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if Ken Tse already exists
    cursor.execute('SELECT id FROM users WHERE username = ?', ('Ken Tse',))
    existing = cursor.fetchone()
    
    if existing:
        print(f"⚠️  Ken Tse account already exists (ID: {existing[0]})")
        # Update to administrator role
        cursor.execute('UPDATE users SET user_role = ? WHERE username = ?', ('administrator', 'Ken Tse'))
        conn.commit()
        conn.close()
        return existing[0]
    
    # Create Ken Tse account
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, user_role, email_verified)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Ken Tse', 'ken@chatapp.com', password_hash, 'administrator', 1))
    
    user_id = cursor.lastrowid
    
    # Create profile
    cursor.execute('''
        INSERT INTO user_profiles (user_id, first_name, last_name, bio)
        VALUES (?, ?, ?, ?)
    ''', (user_id, 'Ken', 'Tse', 'ChatApp Administrator'))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Created Ken Tse account (ID: {user_id})")
    print(f"   Username: Ken Tse")
    print(f"   Email: ken@chatapp.com")
    print(f"   Password: {password}")
    print(f"   ⚠️  CHANGE THIS PASSWORD AFTER FIRST LOGIN!")
    
    return user_id

def verify_migration(db_path):
    """Verify migration was successful"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n📊 Migration Verification:")
    print("-" * 50)
    
    # Check remaining tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"✅ Remaining tables: {', '.join([t[0] for t in tables])}")
    
    # Check admin_messages table
    cursor.execute("SELECT COUNT(*) FROM admin_messages")
    msg_count = cursor.fetchone()[0]
    print(f"✅ Admin messages count: {msg_count}")
    
    # Check users count
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"✅ Total users: {user_count}")
    
    # Check if Ken Tse exists
    cursor.execute("SELECT id, username, email, user_role FROM users WHERE username = 'Ken Tse'")
    ken_tse = cursor.fetchone()
    if ken_tse:
        print(f"✅ Ken Tse account: ID={ken_tse[0]}, Email={ken_tse[2]}, Role={ken_tse[3]}")
    else:
        print("⚠️  Ken Tse account not found!")
    
    conn.close()

def main():
    """Main migration function"""
    db_path = "integrated_users.db"
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        print("   Creating new database...")
        # The database will be created when app starts
        return
    
    print("🚀 Starting ChatApp Migration")
    print("=" * 50)
    
    # Step 1: Backup
    print("\n📦 Step 1: Backing up database...")
    backup_database(db_path)
    
    # Step 2: Remove AI tables
    print("\n🗑️  Step 2: Removing AI-related tables...")
    remove_ai_tables(db_path)
    
    # Step 3: Create Ken Tse account
    print("\n👤 Step 3: Creating Ken Tse account...")
    create_ken_tse_account(db_path)
    
    # Step 4: Verify
    verify_migration(db_path)
    
    print("\n" + "=" * 50)
    print("✅ Migration completed successfully!")
    print("\n📝 Next steps:")
    print("   1. Update requirements: pip install -r requirements_simple.txt")
    print("   2. Review app.py for any AI endpoint references")
    print("   3. Update frontend to rename 'Admin' to 'Ken Tse'")
    print("   4. Test the messaging system")

if __name__ == "__main__":
    main()
