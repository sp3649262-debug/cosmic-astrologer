import csv
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_FILE_PATH = os.path.join(DATA_DIR, "astrology_records.csv")


def init_excel_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_FILE_PATH):
        with open(
            CSV_FILE_PATH, mode="w", newline="", encoding="utf-8-sig"
        ) as file:
            writer = csv.writer(file)
            writer.writerow([
                "Timestamp",
                "Mode",
                "Category / Focus",
                "Language",
                "User Name",
                "User DOB",
                "Partner Name",
                "Partner DOB",
                "Compatibility Score",
                "Reading / Remedies",
            ])


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

    with open(
        CSV_FILE_PATH, mode="a", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.writer(file)
        writer.writerow([
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
        ])