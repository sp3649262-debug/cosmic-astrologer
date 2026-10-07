import os
import re
from typing import Optional
from database import append_reading_record, init_excel_db
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from groq import AsyncGroq
from pydantic import BaseModel

app = FastAPI(title="Cosmic AI Astrologer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AstroPayload(BaseModel):
    mode: str
    category: str
    language: str
    user_name: str
    user_dob: str
    partner_name: Optional[str] = None
    partner_dob: Optional[str] = None

@app.on_event("startup")
def on_startup():
    init_excel_db()

def extract_clean_reading(raw_text: str) -> str:
    """Removes thinking traces and extracts cleanly formatted astrological text."""
    text = re.sub(r"<think>[\s\S]*?</think>", "", raw_text, flags=re.IGNORECASE).strip()

    markers = ["🌟", "💖", "[COMPATIBILITY_SCORE", "**১.", "**1."]
    for marker in markers:
        idx = text.rfind(marker)
        if idx != -1:
            candidate = text[idx:].strip()
            if not any(
                skip in candidate[:80].lower()
                for skip in ["analyze user", "draft content", "thinking"]
            ):
                return candidate
    return text

@app.post("/api/v1/analyze")
async def analyze_astrology(data: AstroPayload, background_tasks: BackgroundTasks):
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is missing. Please configure environment variable.",
        )

    # Async client non-blocking execution ke liye
    client = AsyncGroq(api_key=api_key)

    lang_configs = {
        "Bengali": {
            "rule": "Write strictly in 100% native Bengali script (বাংলা হরফ).",
            "sec1": "🌟 **১. গ্রহাবস্থান ও ভাগ্য বিশ্লেষণ**",
            "sec2": "🔮 **২. ভবিষ্যৎ পূর্বাভাস ও শুভ সময়**",
            "sec3": "⚠️ **৩. বাধা ও প্রতিকূলতা**",
            "sec4": "🌿 **৪. বৈদিক প্রতিকার ও শুভ নির্দেশনা**",
            "c_sec1": "💖 **১. মনের টান ও সম্পর্কের মিলন**",
            "c_sec2": "⚠️ **২. মতভেদ ও সতর্কবার্তা**",
            "c_sec3": "🌿 **৩. সম্পর্ক মজবুত করার প্রতিকার**",
        },
        "Banglish": {
            "rule": "Write in conversational Banglish (Bengali with English alphabet).",
            "sec1": "🌟 **1. Graha Obostha O Bhaggo Bishleshon**",
            "sec2": "🔮 **2. Bhobisshot Forecast O Shuvo Shomoy**",
            "sec3": "⚠️ **3. Badha O Shobar Jonyo Shotorkota**",
            "sec4": "🌿 **4. Vedic Protikar O Shuvo Tips**",
            "c_sec1": "💖 **1. Moner Tan O Relation Dynamics**",
            "c_sec2": "⚠️ **2. Motobhed O Challenges**",
            "c_sec3": "🌿 **3. Shomporko Valo Rakhar Upay**",
        },
        "Hindi": {
            "rule": "Write strictly in native Hindi Devanagari script (हिंदी लिपि).",
            "sec1": "🌟 **१. ग्रह स्थिति एवं भाग्य विश्लेषण**",
            "sec2": "🔮 **२. भविष्यफल एवं शुभ समय**",
            "sec3": "⚠️ **३. बाधाएं एवं सावधानियां**",
            "sec4": "🌿 **४. वैदिक उपाय एवं शुभ सुझाव**",
            "c_sec1": "💖 **१. प्रेम एवं भावनात्मक संबंध**",
            "c_sec2": "⚠️ **२. मतभेद एवं चुनौतियाँ**",
            "c_sec3": "🌿 **३. संबंध सुधार के वैदिक उपाय**",
        },
        "Hinglish": {
            "rule": "Write in conversational Hinglish (Hindi with English alphabet).",
            "sec1": "🌟 **1. Kundali Analysis & Grah Stithi**",
            "sec2": "🔮 **2. Future Predictions & Shubh Samay**",
            "sec3": "⚠️ **3. Challenges & Savdhani**",
            "sec4": "🌿 **4. Vedic Upay & Remedies**",
            "c_sec1": "💖 **1. Love & Mutual Chemistry**",
            "c_sec2": "⚠️ **2. Clashes & Friction**",
            "c_sec3": "🌿 **3. Rishta Majboot Karne Ke Upay**",
        },
        "English": {
            "rule": "Write strictly in fluent, professional English.",
            "sec1": "🌟 **1. Planetary Alignment & Blueprint**",
            "sec2": "🔮 **2. Future Timeline & Opportunities**",
            "sec3": "⚠️ **3. Obstacles & Precautions**",
            "sec4": "🌿 **4. Vedic Remedies & Lucky Elements**",
            "c_sec1": "💖 **1. Emotional Bond & Compatibility**",
            "c_sec2": "⚠️ **2. Friction Points & Challenges**",
            "c_sec3": "🌿 **3. Remedies for Lifelong Harmony**",
        },
    }

    cfg = lang_configs.get(data.language, lang_configs["English"])

    if data.mode == "single":
        prompt = f"""
        Generate a Vedic Horoscope Reading.
        Name: {data.user_name}
        DOB: {data.user_dob}
        Focus Area: {data.category}

        Language Instruction: {cfg['rule']}

        Format your output strictly with these sections:
        {cfg['sec1']} ({data.category})
        Detailed planetary analysis and traits.

        {cfg['sec2']}
        Favorable periods and predictions.

        {cfg['sec3']}
        Precautions and planetary warnings.

        {cfg['sec4']}
        Lucky colors, lucky gemstones, and practical remedies.
        """
    else:
        prompt = f"""
        Generate a Vedic Synastry Compatibility Report.
        Person 1: {data.user_name} ({data.user_dob})
        Person 2: {data.partner_name} ({data.partner_dob})
        Focus Area: {data.category}

        Language Instruction: {cfg['rule']}

        Format strictly:
        [COMPATIBILITY_SCORE: 88%]

        {cfg['c_sec1']}
        Bond and connection.

        {cfg['c_sec2']}
        Challenges and friction.

        {cfg['c_sec3']}
        Remedies to enhance love and understanding.
        """

    raw_text = None
    try:
        completion = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a Vedic Astrologer. Output ONLY the final reading directly. Never output thinking process, planning notes, or English drafting text.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )
        if completion.choices and completion.choices[0].message.content:
            raw_text = completion.choices[0].message.content.strip()
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(err)}")

    clean_text = extract_clean_reading(raw_text)

    score = "N/A"
    if data.mode == "couple":
        score_match = re.search(r"\[COMPATIBILITY_SCORE:\s*(\d+%)\]", clean_text)
        if score_match:
            score = score_match.group(1)
        else:
            pct_match = re.search(r"(\d+%)", clean_text)
            score = pct_match.group(1) if pct_match else "85%"
        clean_text = re.sub(r"\[COMPATIBILITY_SCORE:\s*\d+%\]\n*", "", clean_text).strip()

    # Google Sheets operation background task mein chalao taaki user ko wait na karna pade
    background_tasks.add_task(
        append_reading_record,
        mode=data.mode,
        category=data.category,
        language=data.language,
        user_name=data.user_name,
        user_dob=data.user_dob,
        partner_name=data.partner_name,
        partner_dob=data.partner_dob,
        score=score,
        analysis_text=clean_text,
    )

    return {"status": "success", "score": score, "analysis": clean_text}
