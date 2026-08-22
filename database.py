import os
import json
import gspread
from datetime import datetime

# Google Sheets কানেকশন ইনিশিয়ালাইজেশন
sheet = None

def get_sheet():
    global sheet
    if sheet is not None:
        return sheet

    try:
        if "GOOGLE_CREDENTIALS" in os.environ:
            # Render Environment Variable থেকে ক্রেডেনশিয়াল পড়বে
            creds_info = os.environ["GOOGLE_CREDENTIALS"]
            if isinstance(creds_info, str):
                creds_dict = json.loads(creds_info)
            else:
                creds_dict = creds_info
            gc = gspread.service_account_from_dict(creds_dict)
        else:
            # লোকাল টেস্টিংয়ের জন্য সরাসরি ফাইল থেকে পড়বে
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_path = os.path.join(base_dir, "service_account.json")
            gc = gspread.service_account(filename=json_path)

        sh = gc.open("Cosmic_Astrology_Records")
        sheet = sh.sheet1
        return sheet
    except Exception as e:
        print(f"[GOOGLE SHEETS AUTH ERROR]: {e}")
        return None


def init_excel_db():
    pass  # Google Sheets ক্লাউডে সরাসরি তৈরি থাকে


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
    active_sheet = get_sheet()
    if active_sheet is None:
        print("[SHEET ERROR]: Could not connect to Google Sheet.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean_analysis = analysis_text.replace("\n", " ")

    row_data = [
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
    ]

    try:
        active_sheet.append_row(row_data)
        print("[SHEET SUCCESS]: Record inserted successfully.")
    except Exception as err:
        print(f"[SHEET APPEND ERROR]: {err}")
