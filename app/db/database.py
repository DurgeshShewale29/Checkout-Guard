import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "audit_logs.db")

def init_db():
    """Initializes the SQLite database and creates the audit_logs table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''DROP TABLE IF EXISTS audit_logs''')
    cursor.execute('''
        CREATE TABLE audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL,
            attempt_number INTEGER NOT NULL,
            failure_type TEXT,
            action_taken TEXT NOT NULL,
            outcome TEXT NOT NULL,
            reasoning TEXT,
            confidence_score REAL DEFAULT 1.0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize on module import
init_db()
