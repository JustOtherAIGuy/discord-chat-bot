import sqlite3
import datetime
import os

# Default to the src directory if not specified
DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), 'bot_interactions.db')

def get_db_path():
    return os.environ.get('DISCORD_BOT_DB_PATH', DEFAULT_DB_PATH)

def get_connection():
    return sqlite3.connect(get_db_path())

def init_db():
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_id TEXT,
                channel_id TEXT,
                question TEXT,
                response TEXT,
                feedback TEXT,
                thread_id TEXT
            )
        ''')
        conn.commit()
    finally:
        conn.close()

def log_interaction(user_id, channel_id, question, response, thread_id=None):
    conn = get_connection()
    c = conn.cursor()
    try:
        timestamp = datetime.datetime.now().isoformat()
        c.execute('''
            INSERT INTO interactions (timestamp, user_id, channel_id, question, response, thread_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, str(user_id), str(channel_id), question, response, str(thread_id) if thread_id else None))
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()

def store_feedback(interaction_id, feedback):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            UPDATE interactions
            SET feedback = ?
            WHERE id = ?
        ''', (feedback, interaction_id))
        conn.commit()
    finally:
        conn.close()