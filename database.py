# database.py - Database management

import sqlite3
import json
import logging
from datetime import datetime
from config import DB_FILE, JSON_BACKUP_FILE

class DatabaseManager:
    def __init__(self):
        self.db_file = DB_FILE
        self.json_file = JSON_BACKUP_FILE
        self.init_database()
    
    def init_database(self):
        """Initialize database tables."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    name TEXT,
                    phone TEXT,
                    state TEXT DEFAULT 'start',
                    question_1 TEXT,
                    question_2 TEXT,
                    question_3 TEXT,
                    question_4 TEXT,
                    contact_time TEXT,
                    channel_link TEXT,
                    selected_expert TEXT,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    phone_date TIMESTAMP,
                    is_completed BOOLEAN DEFAULT 0,
                    is_vip BOOLEAN DEFAULT 0,
                    is_hot_lead BOOLEAN DEFAULT 0
                )
            """)
            
            # Table for tracking messages to delete/edit
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_messages (
                    user_id INTEGER,
                    message_id INTEGER,
                    message_type TEXT,
                    PRIMARY KEY (user_id, message_type)
                )
            """)
            
            # Reminder timers
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_timers (
                    user_id INTEGER PRIMARY KEY,
                    first_reminder TIMESTAMP,
                    second_reminder TIMESTAMP,
                    timer_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Final photo timer
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS final_photo_timers (
                    user_id INTEGER PRIMARY KEY,
                    send_time TIMESTAMP,
                    is_sent BOOLEAN DEFAULT 0
                )
            """)
            
            # Add columns if missing (migration)
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN selected_expert TEXT")
            except sqlite3.OperationalError:
                pass 
            
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN is_hot_lead BOOLEAN DEFAULT 0")
            except sqlite3.OperationalError:
                pass 
            
            conn.commit()
            conn.close()
            logging.info("Database initialized successfully")
        except Exception as e:
            logging.error(f"Database initialization error: {e}")
    
    def add_user(self, user_id, username=None, first_name=None, last_name=None):
        """Register a new user."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO users 
                (user_id, username, first_name, last_name) 
                VALUES (?, ?, ?, ?)
            """, (user_id, username, first_name, last_name))
            
            conn.commit()
            conn.close()
            self.backup_to_json()
            return True
        except Exception as e:
            logging.error(f"Error adding user {user_id}: {e}")
            return False
    
    def user_exists(self, user_id):
        """Check if user exists in DB."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            conn.close()
            return result is not None
        except Exception as e:
            logging.error(f"Error checking user existence {user_id}: {e}")
            return False
    
    def update_user_state(self, user_id, state):
        """Update user flow state."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET state = ? WHERE user_id = ?", (state, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error updating user state {user_id}: {e}")
            return False
    
    def update_user_name(self, user_id, name):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET name = ? WHERE user_id = ?", (name, user_id))
            
            conn.commit()
            conn.close()
            self.backup_to_json()
            return True
        except Exception as e:
            logging.error(f"Error updating user name {user_id}: {e}")
            return False
    
    def save_selected_expert(self, user_id, expert):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET selected_expert = ? WHERE user_id = ?", (expert, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error saving selected expert for user {user_id}: {e}")
            return False
    
    def get_selected_expert(self, user_id):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT selected_expert FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            conn.close()
            return result[0] if result and result[0] else "forough"
        except Exception as e:
            logging.error(f"Error getting selected expert for user {user_id}: {e}")
            return "forough"
    
    def update_question_answer(self, user_id, question_num, answer):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            column = f"question_{question_num}"
            cursor.execute(f"UPDATE users SET {column} = ? WHERE user_id = ?", (answer, user_id))
            
            conn.commit()
            conn.close()
            self.backup_to_json()
            return True
        except Exception as e:
            logging.error(f"Error updating question {question_num} for user {user_id}: {e}")
            return False
    
    def update_channel_link(self, user_id, channel_link):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET channel_link = ? WHERE user_id = ?", (channel_link, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error updating channel link for user {user_id}: {e}")
            return False
    
    def update_user_phone(self, user_id, phone):
        """Save phone and mark as VIP."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET phone = ?, phone_date = CURRENT_TIMESTAMP, is_vip = 1 
                WHERE user_id = ?
            """, (phone, user_id))
            
            conn.commit()
            conn.close()
            self.backup_to_json()
            return True
        except Exception as e:
            logging.error(f"Error updating phone for user {user_id}: {e}")
            return False
    
    def set_hot_lead(self, user_id, is_hot_lead=True):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET is_hot_lead = ? WHERE user_id = ?", (is_hot_lead, user_id))
            
            conn.commit()
            conn.close()
            self.backup_to_json()
            return True
        except Exception as e:
            logging.error(f"Error setting hot lead for user {user_id}: {e}")
            return False
    
    def update_contact_time(self, user_id, contact_time):
        """Save preferred contact time and mark complete."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET contact_time = ?, is_completed = 1 
                WHERE user_id = ?
            """, (contact_time, user_id))
            
            conn.commit()
            conn.close()
            self.backup_to_json()
            return True
        except Exception as e:
            logging.error(f"Error updating contact time for user {user_id}: {e}")
            return False
    
    def get_user_data(self, user_id):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            columns = [description[0] for description in cursor.description]
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logging.error(f"Error getting user data {user_id}: {e}")
            return None
    
    def get_user_state(self, user_id):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT state FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            conn.close()
            return result[0] if result else "start"
        except Exception as e:
            logging.error(f"Error getting user state {user_id}: {e}")
            return "start"
    
    def save_message_id(self, user_id, message_id, message_type):
        """Store message ID for later editing/deletion."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_messages 
                (user_id, message_id, message_type) 
                VALUES (?, ?, ?)
            """, (user_id, message_id, message_type))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error saving message ID: {e}")
            return False
    
    def get_message_id(self, user_id, message_type):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT message_id FROM user_messages 
                WHERE user_id = ? AND message_type = ?
            """, (user_id, message_type))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
        except Exception as e:
            logging.error(f"Error getting message ID: {e}")
            return None
    
    def add_timer(self, user_id, first_reminder, second_reminder):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_timers 
                (user_id, first_reminder, second_reminder) 
                VALUES (?, ?, ?)
            """, (user_id, first_reminder, second_reminder))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error adding timer: {e}")
            return False
    
    def add_final_photo_timer(self, user_id, send_time):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO final_photo_timers 
                (user_id, send_time, is_sent) 
                VALUES (?, ?, 0)
            """, (user_id, send_time))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error adding final photo timer: {e}")
            return False
    
    def mark_final_photo_sent(self, user_id):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE final_photo_timers SET is_sent = 1 WHERE user_id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error marking final photo as sent: {e}")
            return False
    
    def get_pending_final_photos(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, send_time FROM final_photo_timers 
                WHERE is_sent = 0 AND send_time <= CURRENT_TIMESTAMP
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            return results
        except Exception as e:
            logging.error(f"Error getting pending final photos: {e}")
            return []
    
    def get_stats(self):
        """Retrieve bot usage statistics."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
            vip_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_hot_lead = 1")
            hot_leads = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE selected_expert = 'forough'")
            forough_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE selected_expert = 'sadegh'")
            sadegh_users = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_users': total_users,
                'vip_users': vip_users,
                'hot_leads': hot_leads,
                'forough_users': forough_users,
                'sadegh_users': sadegh_users
            }
        except Exception as e:
            logging.error(f"Error getting stats: {e}")
            return {
                'total_users': 0,
                'vip_users': 0,
                'hot_leads': 0,
                'forough_users': 0,
                'sadegh_users': 0
            }
    
    def get_all_users(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users ORDER BY registration_date DESC")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            conn.close()
            
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logging.error(f"Error getting all users: {e}")
            return []
    
    def get_hot_leads(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM users 
                WHERE is_hot_lead = 1 
                ORDER BY phone_date DESC
            """)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            conn.close()
            
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logging.error(f"Error getting hot leads: {e}")
            return []
    
    def get_users_by_expert(self, expert_name):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM users 
                WHERE selected_expert = ? 
                ORDER BY registration_date DESC
            """, (expert_name,))
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            conn.close()
            
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logging.error(f"Error getting users by expert: {e}")
            return []
    
    def get_pending_timers(self):
        """Retrieve active reminder timers."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, first_reminder, second_reminder FROM user_timers 
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            pending_timers = {}
            for row in results:
                user_id, first_reminder, second_reminder = row
                first_reminder_dt = datetime.fromisoformat(first_reminder) if first_reminder else None
                second_reminder_dt = datetime.fromisoformat(second_reminder) if second_reminder else None
                pending_timers[user_id] = {
                    'first_reminder': first_reminder_dt,
                    'second_reminder': second_reminder_dt,
                    'chat_id': user_id,
                    'first_sent': False,
                    'second_sent': False
                }
            
            return pending_timers
        except Exception as e:
            logging.error(f"Error getting pending timers: {e}")
            return {}

    def get_pending_final_photo_timers(self):
        """Retrieve pending final photo tasks."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, send_time FROM final_photo_timers 
                WHERE is_sent = 0
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            pending_photos = {}
            for row in results:
                user_id, send_time = row
                send_time_dt = datetime.fromisoformat(send_time)
                pending_photos[user_id] = {
                    'send_time': send_time_dt,
                    'chat_id': user_id,
                    'sent': False 
                }
            
            return pending_photos
        except Exception as e:
            logging.error(f"Error getting pending final photos: {e}")
            return {}

    def backup_to_json(self):
        """Backup current state to JSON."""
        try:
            users = self.get_all_users()
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logging.error(f"Error backing up to JSON: {e}")
    
    def cleanup_old_timers(self, days=7):
        """Remove old timer records."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM user_timers 
                WHERE second_reminder < datetime('now', '-{} days')
            """.format(days))
            
            cursor.execute("""
                DELETE FROM final_photo_timers 
                WHERE is_sent = 1 AND send_time < datetime('now', '-{} days')
            """.format(days))
            
            conn.commit()
            conn.close()
            logging.info(f"Cleaned up old timers older than {days} days")
        except Exception as e:
            logging.error(f"Error cleaning up old timers: {e}")