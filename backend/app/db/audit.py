import sqlite3
from typing import Optional, List, Dict, Any
from app.db.database import DB_PATH

def log_attempt(
    transaction_id: str,
    attempt_number: int,
    failure_type: Optional[str],
    action_taken: str,
    outcome: str,
    reasoning: Optional[str]
):
    """Inserts a single audit log record into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO audit_logs (transaction_id, attempt_number, failure_type, action_taken, outcome, reasoning)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (transaction_id, attempt_number, failure_type, action_taken, outcome, reasoning))
    
    conn.commit()
    conn.close()

def get_audit_trail(transaction_id: str) -> List[Dict[str, Any]]:
    """Retrieves the full step-by-step history for a given transaction."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # To return dict-like objects
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT attempt_number, failure_type, action_taken, outcome, reasoning, timestamp 
        FROM audit_logs 
        WHERE transaction_id = ?
        ORDER BY attempt_number ASC
    ''', (transaction_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_all_transactions() -> List[Dict[str, Any]]:
    """Retrieves a summary of all distinct transactions."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # We want the latest outcome for each transaction
    cursor.execute('''
        SELECT 
            transaction_id, 
            MAX(timestamp) as last_updated,
            (SELECT failure_type FROM audit_logs a2 WHERE a2.transaction_id = a1.transaction_id ORDER BY attempt_number ASC LIMIT 1) as initial_failure,
            (SELECT outcome FROM audit_logs a3 WHERE a3.transaction_id = a1.transaction_id ORDER BY attempt_number DESC LIMIT 1) as final_outcome
        FROM audit_logs a1
        GROUP BY transaction_id
        ORDER BY last_updated DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
