"""
ChatApp Database - Simplified database for human-to-human messaging
Supports: User authentication, messaging between Ken Tse and users, file attachments
"""

import os
import bcrypt
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

# Try PostgreSQL first (for Railway), fallback to SQLite
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    USE_POSTGRES = bool(os.getenv('DATABASE_URL'))
except ImportError:
    USE_POSTGRES = False

if not USE_POSTGRES:
    import sqlite3
    from pathlib import Path

class ChatAppDatabase:
    """
    Simplified database for ChatApp - one-to-many messaging platform
    Ken Tse can message multiple users individually
    Supports both PostgreSQL (production) and SQLite (local dev)
    """
    
    def __init__(self, db_path: str = "integrated_users.db"):
        self.use_postgres = USE_POSTGRES
        if self.use_postgres:
            self.db_url = os.getenv('DATABASE_URL')
            # Fix Railway's postgres:// to postgresql://
            if self.db_url and self.db_url.startswith('postgres://'):
                self.db_url = self.db_url.replace('postgres://', 'postgresql://', 1)
            print(f"🐘 Using PostgreSQL database")
        else:
            self.db_path = Path(db_path)
            print(f"💾 Using SQLite database: {self.db_path}")
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        if self.use_postgres:
            return psycopg2.connect(self.db_url)
        else:
            return sqlite3.connect(self.db_path)
    
    def _sql(self, sqlite_sql: str) -> str:
        """Convert SQLite SQL to PostgreSQL if needed"""
        if not self.use_postgres:
            return sqlite_sql
        
        # Convert SQLite to PostgreSQL syntax
        pg_sql = sqlite_sql
        pg_sql = pg_sql.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
        pg_sql = pg_sql.replace('DATETIME', 'TIMESTAMP')
        pg_sql = pg_sql.replace('TEXT', 'VARCHAR(500)')
        pg_sql = pg_sql.replace('INTEGER DEFAULT 0', 'INTEGER DEFAULT 0')
        pg_sql = pg_sql.replace('INTEGER DEFAULT 1', 'INTEGER DEFAULT 1')
        return pg_sql
    
    def init_database(self):
        """Initialize all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table for authentication (matches existing schema)
        cursor.execute(self._sql('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_role TEXT DEFAULT 'guest',
                email_verified INTEGER DEFAULT 0,
                verification_code TEXT,
                verification_expires DATETIME,
                is_deleted INTEGER DEFAULT 0
            )
        '''))
        
        # User profiles table - basic info only
        cursor.execute(self._sql('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                first_name TEXT,
                last_name TEXT,
                bio TEXT,
                avatar_url TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        '''))
        
        # Messages table for user-Ken Tse communication
        cursor.execute(self._sql('''
            CREATE TABLE IF NOT EXISTS admin_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                sender_type TEXT NOT NULL CHECK (sender_type IN ('user', 'admin')),
                message TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                file_url TEXT,
                file_name TEXT,
                file_size INTEGER,
                reply_to INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (reply_to) REFERENCES admin_messages (id) ON DELETE SET NULL
            )
        '''))
        
        # User status table for online/offline/busy tracking
        cursor.execute(self._sql('''
            CREATE TABLE IF NOT EXISTS user_status (
                user_id INTEGER PRIMARY KEY,
                status TEXT DEFAULT 'offline' CHECK (status IN ('online', 'offline', 'in_call', 'busy')),
                last_seen DATETIME,
                current_call_with INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (current_call_with) REFERENCES users (id) ON DELETE SET NULL
            )
        '''))
        
        # Call history table for tracking all call attempts
        cursor.execute(self._sql('''
            CREATE TABLE IF NOT EXISTS call_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caller_id INTEGER NOT NULL,
                callee_id INTEGER NOT NULL,
                call_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                call_status TEXT CHECK (call_status IN ('missed', 'answered', 'rejected', 'dropped', 'ongoing')),
                call_duration INTEGER DEFAULT 0,
                answered_at DATETIME,
                ended_at DATETIME,
                seen_by_callee INTEGER DEFAULT 0,
                FOREIGN KEY (caller_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (callee_id) REFERENCES users (id) ON DELETE CASCADE
            )
        '''))
        
        conn.commit()
        conn.close()
    
    # ============= Authentication Methods =============
    
    def create_user(self, username: str, email: str, password: str, role: str = 'user') -> Optional[int]:
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, user_role, email_verified)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, role, 1))
            
            user_id = cursor.lastrowid
            
            # Create default profile
            cursor.execute('''
                INSERT INTO user_profiles (user_id, first_name, last_name, bio)
                VALUES (?, ?, ?, ?)
            ''', (user_id, '', '', ''))
            
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, password_hash, user_role, is_deleted 
            FROM users WHERE username = ?
        ''', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            if user[5]:  # is_deleted
                return None
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[4]
            }
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, user_role, is_deleted 
            FROM users WHERE id = ?
        ''', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user and not user[4]:  # not is_deleted
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[3]
            }
        return None
    
    def get_admin_user(self) -> Optional[Dict[str, Any]]:
        """Get the administrator user (returns the first active admin)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get any administrator account (now there's only one)
        cursor.execute('''
            SELECT id, username, email, user_role 
            FROM users 
            WHERE user_role = 'administrator' AND is_deleted = 0
            ORDER BY id ASC
            LIMIT 1
        ''')
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[3]
            }
        return None
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user password"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            print(f"[DEBUG] Changing password for user_id: {user_id}")
            print(f"[DEBUG] New password hash: {password_hash[:30]}...")
            
            cursor.execute('''
                UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (password_hash, user_id))
            
            rows_affected = cursor.rowcount
            print(f"[DEBUG] Rows affected: {rows_affected}")
            
            conn.commit()
            print(f"[DEBUG] Commit executed")
            
            # Verify the change
            cursor.execute('SELECT password_hash, username FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            if result:
                print(f"[DEBUG] Verified DB - User: {result[1]}, Hash: {result[0][:30]}...")
                if result[0] == password_hash:
                    print(f"[DEBUG] ✅ Password hash matches in DB!")
                else:
                    print(f"[DEBUG] ❌ Password hash MISMATCH in DB!")
            
            return rows_affected > 0
        except Exception as e:
            print(f"[DEBUG] ❌ ERROR in change_password: {e}")
            raise
        finally:
            conn.close()
    
    def update_user_password(self, user_id: int, new_password: str) -> bool:
        """Alias for change_password (for compatibility)"""
        return self.change_password(user_id, new_password)
    
    def get_user_role(self, user_id: int) -> Optional[str]:
        """Get user role"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_role FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def get_all_users_for_admin(self) -> List[Dict[str, Any]]:
        """Get all active users for admin (excluding admin themselves)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.user_role,
                   (SELECT COUNT(*) FROM admin_messages WHERE user_id = u.id) as message_count,
                   (SELECT MAX(timestamp) FROM admin_messages WHERE user_id = u.id) as last_message_time,
                   (SELECT COUNT(*) FROM admin_messages WHERE user_id = u.id AND sender_type = 'user' AND is_read = 0) as unread_count
            FROM users u
            WHERE u.is_deleted = 0 AND u.user_role != 'administrator'
            ORDER BY last_message_time DESC, u.username ASC
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'role': row[3],
                'message_count': row[4] or 0,
                'last_message_time': row[5],
                'unread_count': row[6] or 0
            })
        
        conn.close()
        return users
    
    # ============= Profile Methods =============
    
    def get_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT first_name, last_name, bio, avatar_url
            FROM user_profiles WHERE user_id = ?
        ''', (user_id,))
        profile = cursor.fetchone()
        conn.close()
        
        if profile:
            return {
                'first_name': profile[0] or '',
                'last_name': profile[1] or '',
                'bio': profile[2] or '',
                'avatar_url': profile[3] or ''
            }
        return None
    
    def update_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """Update user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE user_profiles 
                SET first_name = ?, last_name = ?, bio = ?, avatar_url = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (
                profile_data.get('first_name', ''),
                profile_data.get('last_name', ''),
                profile_data.get('bio', ''),
                profile_data.get('avatar_url', ''),
                user_id
            ))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    # ============= Messaging Methods =============
    
    def send_message(self, user_id: int, sender_type: str, message: str, 
                    file_url: str = None, file_name: str = None, 
                    file_size: int = None, reply_to: int = None) -> int:
        """Send a message with optional file attachment and reply"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO admin_messages (user_id, sender_type, message, file_url, file_name, file_size, reply_to)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, sender_type, message, file_url, file_name, file_size, reply_to))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_messages(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, sender_type, message, file_url, file_name, file_size,
                   timestamp, is_read
            FROM admin_messages
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'user_id': row[1],
                'sender_type': row[2],
                'message': row[3],
                'file_url': row[4],
                'file_name': row[5],
                'file_size': row[6],
                'timestamp': row[7],
                'is_read': bool(row[8])
            })
        
        conn.close()
        return list(reversed(messages))  # Return in chronological order
    
    def mark_messages_read(self, user_id: int) -> bool:
        """Mark all admin messages as read for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE admin_messages
                SET is_read = 1
                WHERE user_id = ? AND sender_type = 'admin' AND is_read = 0
            ''', (user_id,))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def mark_user_messages_read_by_admin(self, user_id: int) -> bool:
        """Mark all user messages as read by admin (when admin views user's conversation)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE admin_messages
                SET is_read = 1
                WHERE user_id = ? AND sender_type = 'user' AND is_read = 0
            ''', (user_id,))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_unread_count(self, user_id: int, sender_type: str) -> int:
        """Get count of unread messages"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*)
            FROM admin_messages
            WHERE user_id = ? AND sender_type = ? AND is_read = 0
        ''', (user_id, sender_type))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def delete_message(self, message_id: int, user_id: int, role: str) -> bool:
        """Delete a message"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if role == 'administrator':
                # Ken Tse can delete any message
                cursor.execute('DELETE FROM admin_messages WHERE id = ?', (message_id,))
            else:
                # Regular user can only delete their own messages
                cursor.execute('''
                    DELETE FROM admin_messages
                    WHERE id = ? AND user_id = ? AND sender_type = 'user'
                ''', (message_id, user_id))
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    # ============= Admin Methods (Ken Tse) =============
    
    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """Get all users with message history (for Ken Tse's view)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT u.id, u.username, u.email,
                   (SELECT COUNT(*) FROM admin_messages 
                    WHERE user_id = u.id AND sender_type = 'user' AND is_read = 0) as unread_count,
                   (SELECT MAX(timestamp) FROM admin_messages WHERE user_id = u.id) as last_message
            FROM users u
            INNER JOIN admin_messages am ON u.id = am.user_id
            WHERE u.is_deleted = 0
            ORDER BY last_message DESC
        ''')
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'user_id': row[0],
                'username': row[1],
                'email': row[2],
                'unread_count': row[3],
                'last_message': row[4]
            })
        
        conn.close()
        return conversations
    
    def get_all_users(self, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """Get all users (for Ken Tse's admin view)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        where_clause = '' if include_deleted else 'WHERE u.is_deleted = 0'
        
        cursor.execute(f'''
            SELECT u.id, u.username, u.email, u.user_role, u.created_at,
                   p.first_name, p.last_name, u.is_deleted
            FROM users u
            LEFT JOIN user_profiles p ON u.id = p.user_id
            {where_clause}
            ORDER BY u.created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'role': row[3],
                'created_at': row[4],
                'first_name': row[5] or '',
                'last_name': row[6] or '',
                'is_deleted': bool(row[7])
            })
        
        conn.close()
        return users
    
    # ============= Admin User Management Methods =============
    
    def soft_delete_user(self, user_id: int) -> bool:
        """Soft delete a user (mark as deleted)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def restore_user(self, user_id: int) -> bool:
        """Restore a soft-deleted user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users SET is_deleted = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def permanent_delete_user(self, user_id: int) -> bool:
        """Permanently delete a user and all their data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Delete in order: messages, profile, user
            cursor.execute('DELETE FROM admin_messages WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM user_profiles WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def bulk_delete_deleted_users(self) -> int:
        """Permanently delete all soft-deleted users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get IDs of deleted users
            cursor.execute('SELECT id FROM users WHERE is_deleted = 1')
            deleted_user_ids = [row[0] for row in cursor.fetchall()]
            
            count = 0
            for user_id in deleted_user_ids:
                cursor.execute('DELETE FROM admin_messages WHERE user_id = ?', (user_id,))
                cursor.execute('DELETE FROM user_profiles WHERE user_id = ?', (user_id,))
                cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                count += 1
            
            conn.commit()
            return count
        finally:
            conn.close()
    
    def update_user_role(self, user_id: int, role: str) -> bool:
        """Update user role"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users SET user_role = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (role, user_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    # ============= User Status Methods =============
    
    def update_user_status(self, user_id: int, status: str, current_call_with: Optional[int] = None):
        """Update user online/offline/busy status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_status (user_id, status, last_seen, current_call_with)
                VALUES (?, ?, CURRENT_TIMESTAMP, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    status = excluded.status,
                    last_seen = excluded.last_seen,
                    current_call_with = excluded.current_call_with
            ''', (user_id, status, current_call_with))
            conn.commit()
        finally:
            conn.close()
    
    def get_user_status(self, user_id: int) -> Dict[str, Any]:
        """Get user status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT status, last_seen, current_call_with
                FROM user_status
                WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'status': row[0],
                    'last_seen': row[1],
                    'current_call_with': row[2]
                }
            return {'status': 'offline', 'last_seen': None, 'current_call_with': None}
        finally:
            conn.close()
    
    def heartbeat(self, user_id: int):
        """Update last_seen timestamp (called every 10s by client)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_status (user_id, status, last_seen)
                VALUES (?, 'online', CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    last_seen = CURRENT_TIMESTAMP
            ''', (user_id,))
            conn.commit()
        finally:
            conn.close()
    
    # ============= Call History Methods =============
    
    def log_call_attempt(self, caller_id: int, callee_id: int) -> int:
        """Log a new call attempt, returns call_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO call_history (caller_id, callee_id, call_status)
                VALUES (?, ?, 'ongoing')
            ''', (caller_id, callee_id))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def update_call_status(self, call_id: int, status: str, duration: Optional[int] = None):
        """Update call status (answered, missed, rejected, dropped)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if status == 'answered' and duration is None:
                # Call was just answered
                cursor.execute('''
                    UPDATE call_history
                    SET call_status = ?, answered_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (status, call_id))
            elif duration is not None:
                # Call ended with duration
                cursor.execute('''
                    UPDATE call_history
                    SET call_status = ?, ended_at = CURRENT_TIMESTAMP, call_duration = ?
                    WHERE id = ?
                ''', (status, call_id, duration))
            else:
                # Call missed/rejected
                cursor.execute('''
                    UPDATE call_history
                    SET call_status = ?, ended_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (status, call_id))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_missed_calls(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all missed calls for a user (admin)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT ch.id, ch.caller_id, u.username, ch.call_time, ch.seen_by_callee
                FROM call_history ch
                JOIN users u ON ch.caller_id = u.id
                WHERE ch.callee_id = ? AND ch.call_status = 'missed'
                ORDER BY ch.call_time DESC
                LIMIT 50
            ''', (user_id,))
            
            return [{
                'id': row[0],
                'caller_id': row[1],
                'caller_username': row[2],
                'call_time': row[3],
                'seen': bool(row[4])
            } for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def mark_missed_call_seen(self, call_id: int):
        """Mark missed call as seen"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE call_history
                SET seen_by_callee = 1
                WHERE id = ?
            ''', (call_id,))
            conn.commit()
        finally:
            conn.close()
    
    def get_call_history_for_user(self, user1_id: int, user2_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get call history between two users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, caller_id, callee_id, call_time, call_status, call_duration
                FROM call_history
                WHERE (caller_id = ? AND callee_id = ?) OR (caller_id = ? AND callee_id = ?)
                ORDER BY call_time DESC
                LIMIT ?
            ''', (user1_id, user2_id, user2_id, user1_id, limit))
            
            return [{
                'id': row[0],
                'caller_id': row[1],
                'callee_id': row[2],
                'call_time': row[3],
                'status': row[4],
                'duration': row[5]
            } for row in cursor.fetchall()]
        finally:
            conn.close()
