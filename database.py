import sqlite3
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_FILE_PATH = os.path.join(DATA_DIR, "astrology_records.db")


def init_excel_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS astrology_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            mode TEXT,
            category TEXT,
            language TEXT,
            user_name TEXT,
            user_dob TEXT,
            partner_name TEXT,
            partner_dob TEXT,
            compatibility_score TEXT,
            reading_remedies TEXT
        )
    """)
    conn.commit()
    conn.close()


def append_reading_record(
    mode: str,
    category: str,
    language: str,
    user_name: str,
    user_dob: str,
    partner_name: str,
    partner_dob: str,
    score: str,
    analysis_text: str,
):
    init_excel_db()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean_analysis = analysis_text.replace("\n", " ")

    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO astrology_records (
            timestamp,
            mode,
            category,
            language,
            user_name,
            user_dob,
            partner_name,
            partner_dob,
            compatibility_score,
            reading_remedies
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp,
        mode.upper(),
        category,
        language,
        user_name,
        user_dob,
        partner_name if partner_name else "N/A",
        partner_dob if partner_dob else "N/A",
        score if score else "N/A",
        clean_analysis,
    ))
    conn.commit()
    conn.close()
