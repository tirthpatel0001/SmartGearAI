import sqlite3

DB_NAME = "database.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = get_connection()
    cur = conn.cursor()

    # Create table with all required columns
    cur.execute("""
        CREATE TABLE IF NOT EXISTS production_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gear_id TEXT,
            operation TEXT,
            total_steps INTEGER,
            completed_steps INTEGER DEFAULT 0,
            start_time TEXT,
            last_update TEXT,
            machine_id TEXT,
            operator_name TEXT,
            machine_status TEXT DEFAULT 'RUNNING'
        )
    """)

    conn.commit()
    conn.close()
