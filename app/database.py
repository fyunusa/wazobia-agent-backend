"""
Database setup and models using SQLite
"""
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import hashlib
import secrets

DATABASE_PATH = Path(__file__).parent.parent / "users.db"


class Database:
    """SQLite database handler for user management"""
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database with users table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Check if is_admin column exists, add it if not
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'is_admin' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
            conn.commit()
            print("✅ Added is_admin column to users table")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                language TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        """)
        
        conn.commit()
        
        # Create default admin user if not exists
        cursor.execute("SELECT * FROM users WHERE email = ?", ('admin@wazobia.ai',))
        if not cursor.fetchone():
            admin_password = 'admin123'  # Default password - should be changed
            password_hash = self.hash_password(admin_password)
            created_at = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO users (email, username, password_hash, created_at, is_admin)
                VALUES (?, ?, ?, ?, ?)
            """, ('admin@wazobia.ai', 'admin', password_hash, created_at, 1))
            conn.commit()
            print("✅ Default admin user created: admin@wazobia.ai / admin123")
        
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${pwd_hash.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, pwd_hash = password_hash.split('$')
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return new_hash.hex() == pwd_hash
        except Exception:
            return False
    
    def create_user(self, email: str, username: str, password: str, is_admin: bool = False) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            created_at = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO users (email, username, password_hash, created_at, is_admin)
                VALUES (?, ?, ?, ?, ?)
            """, (email, username, password_hash, created_at, 1 if is_admin else 0))
            
            conn.commit()
            user_id = cursor.lastrowid
            
            return {
                'id': user_id,
                'email': email,
                'username': username,
                'created_at': created_at,
                'is_admin': is_admin
            }
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET last_login = ? WHERE id = ?
        """, (datetime.now().isoformat(), user_id))
        
        conn.commit()
        conn.close()
    
    def create_session(self, user_id: int, token: str, expires_at: str):
        """Create a new session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions (user_id, token, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, token, datetime.now().isoformat(), expires_at))
        
        conn.commit()
        conn.close()
    
    def get_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Get session by token"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sessions WHERE token = ?", (token,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def delete_session(self, token: str):
        """Delete a session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()
    
    def create_conversation(self, user_id: int, title: str) -> int:
        """Create a new conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO conversations (user_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, title, now, now))
        
        conn.commit()
        conversation_id = cursor.lastrowid
        conn.close()
        return conversation_id
    
    def get_user_conversations(self, user_id: int) -> list:
        """Get all conversations for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, COUNT(m.id) as message_count 
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            WHERE c.user_id = ?
            GROUP BY c.id
            ORDER BY c.updated_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_conversation(self, conversation_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM conversations 
            WHERE id = ? AND user_id = ?
        """, (conversation_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def add_message(self, conversation_id: int, role: str, content: str, language: Optional[str] = None):
        """Add a message to a conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO messages (conversation_id, role, content, language, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (conversation_id, role, content, language, now))
        
        # Update conversation timestamp
        cursor.execute("""
            UPDATE conversations SET updated_at = ? WHERE id = ?
        """, (now, conversation_id))
        
        conn.commit()
        conn.close()
    
    def get_conversation_messages(self, conversation_id: int) -> list:
        """Get all messages in a conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM messages 
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """, (conversation_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_user_stats(self, user_id: int) -> Dict[str, int]:
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Count conversations
        cursor.execute("SELECT COUNT(*) FROM conversations WHERE user_id = ?", (user_id,))
        conversation_count = cursor.fetchone()[0]
        
        # Count total messages
        cursor.execute("""
            SELECT COUNT(*) FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            WHERE c.user_id = ?
        """, (user_id,))
        message_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'conversation_count': conversation_count,
            'message_count': message_count
        }
    
    def get_admin_stats(self) -> Dict[str, Any]:
        """Get admin statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Active users (logged in within last 30 days)
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE last_login IS NOT NULL 
            AND datetime(last_login) > datetime('now', '-30 days')
        """)
        active_users = cursor.fetchone()[0]
        
        # Total conversations
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_conversations = cursor.fetchone()[0]
        
        # Total messages
        cursor.execute("SELECT COUNT(*) FROM messages")
        total_messages = cursor.fetchone()[0]
        
        # User messages (role='user')
        cursor.execute("SELECT COUNT(*) FROM messages WHERE role='user'")
        user_messages = cursor.fetchone()[0]
        
        # Recent signups (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE datetime(created_at) > datetime('now', '-7 days')
        """)
        recent_signups = cursor.fetchone()[0]
        
        # Recent activity (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) FROM messages 
            WHERE datetime(created_at) > datetime('now', '-1 day')
        """)
        messages_24h = cursor.fetchone()[0]
        
        # Language distribution
        cursor.execute("""
            SELECT language, COUNT(*) as count 
            FROM messages 
            WHERE language IS NOT NULL 
            GROUP BY language 
            ORDER BY count DESC
        """)
        language_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'user_messages': user_messages,
            'recent_signups': recent_signups,
            'messages_24h': messages_24h,
            'language_stats': language_stats
        }


# Global database instance
_db = None

def get_db() -> Database:
    """Get or create database instance"""
    global _db
    if _db is None:
        _db = Database()
    return _db
