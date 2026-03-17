# ai_agent.py
# Gujarat Domestic Worker Registration System
# All Gemini AI calls — updated to google-genai SDK (replaces google-generativeai)

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

import os
import json
import re
from datetime import datetime, date, timedelta
from typing import Optional
from PIL import Image
import io
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# GEMINI SETUP — new google-genai SDK
# Install: pip install google-genai
# ─────────────────────────────────────────────

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Support both Streamlit Cloud secrets and local .env
try:
    import streamlit as st
    GEMINI_API_KEY = (
        st.secrets.get("GEMINI_API_KEY", "")
        or os.getenv("GEMINI_API_KEY", "")
    )
except Exception:
    pass

if not GEMINI_API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY not found.\n"
        "Add it to your .env file or Streamlit secrets.\n"
        "Get a free key at: https://aistudio.google.com"
    )

# Try new SDK first, fall back to old SDK
try:
    from google import genai as genai_new
    _client = genai_new.Client(api_key=GEMINI_API_KEY)
    _USE_NEW_SDK = True
except ImportError:
    import google.generativeai as genai_old
    genai_old.configure(api_key=GEMINI_API_KEY)
    _VISION_MODEL = genai_old.GenerativeModel("gemini-2.0-flash")
    _TEXT_MODEL   = genai_old.GenerativeModel("gemini-2.0-flash")
    _USE_NEW_SDK  = False

MODEL_NAME = "gemini-2.0-flash"


def _call_gemini(prompt: str, image_bytes: Optional[bytes] = None) -> str:
    """
    Unified Gemini caller — works with both old and new SDK.
    """
    if _USE_NEW_SDK:
        if image_bytes:
            import base64
            contents = [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(image_bytes).decode("utf-8")
                    }
                }
            ]
        else:
            contents = prompt

        response = _client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
        )
        return response.text.strip()
    else:
        if image_bytes:
            response = _VISION_MODEL.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": image_bytes}
            ])
        else:
            response = _TEXT_MODEL.generate_content(prompt)
        return response.text.strip()


def _is_quota_error(error_str: str) -> bool:
    return any(k in error_str for k in ["429", "quota", "RESOURCE_EXHAUSTED", "rate"])


# ─────────────────────────────────────────────
# PYDANTIC SCHEMA
# ─────────────────────────────────────────────

class AadhaarData(BaseModel):
    full_name:      Optional[str] = None
    date_of_birth:  Optional[str] = None
    aadhaar_number: Optional[str] = None
    gender:         Optional[str] = None

    @field_validator("aadhaar_number")
    @classmethod
    def validate_aadhaar(cls, v):
        if v is None:
            return v
        cleaned = re.sub(r"\s+", "", str(v))
        if not re.match(r"^\d{12}$", cleaned):
            return None
        return cleaned

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v):
        if v is None:
            return v
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(v.strip(), fmt).strftime("%d/%m/%Y")
            except ValueError:
                continue
        return v

    @property
    def is_valid(self) -> bool:
        return (
            self.full_name is not None
            and self.date_of_birth is not None
            and self.aadhaar_number is not None
        )


# ─────────────────────────────────────────────
# MOCK DATA — used when API quota exceeded
# ─────────────────────────────────────────────

MOCK_AADHAAR = AadhaarData(
    full_name="Demo Worker",
    date_of_birth="15/08/1992",
    aadhaar_number="234567890123",
    gender="Female"
)


def mask_display(aadhaar_number: Optional[str]) -> str:
    if not aadhaar_number:
        return "null"
    return f"XXXX XXXX {aadhaar_number[-4:]}"


# ─────────────────────────────────────────────
# MODULE 1: VISION EXTRACTION
# ─────────────────────────────────────────────

EXTRACT_PROMPT = """
You are a strict government document data extraction agent for the
Gujarat Domestic Worker Registration System.

Extract ONLY these fields from the Aadhaar card image:
- full_name: The person's full name as printed on the card
- date_of_birth: Date of birth in DD/MM/YYYY format
- aadhaar_number: The 12-digit Aadhaar number (digits only, no spaces)
- gender: Exactly one of: Male, Female, Transgender

RULES:
1. Output ONLY valid JSON — no explanation, no markdown, no backticks
2. If a field cannot be read clearly, set its value to null
3. For aadhaar_number, remove all spaces and return only digits
4. If this is not an Aadhaar card, return: {"error": "Not an Aadhaar card"}

Output example:
{"full_name": "Kamla Bai", "date_of_birth": "01/06/1985", "aadhaar_number": "234567890123", "gender": "Female"}
"""


def extract_aadhaar_data(image_bytes: bytes) -> tuple[Optional[AadhaarData], str]:
    """
    Extract structured data from an Aadhaar card image using Gemini Vision.
    DPDP Act 2023: image is processed in-memory only, never stored.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if max(img.size) > 1600:
            ratio = 1600 / max(img.size)
            img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        processed = buf.getvalue()
        del image_bytes  # DPDP compliance

        raw_text = _call_gemini(EXTRACT_PROMPT, processed)
        del processed  # DPDP compliance

        raw_text = re.sub(r"```json\s*|```", "", raw_text).strip()
        data_dict = json.loads(raw_text)

        if "error" in data_dict:
            return None, f"❌ {data_dict['error']}"

        aadhaar_data = AadhaarData(**data_dict)
        if not aadhaar_data.is_valid:
            missing = [f for f, v in [
                ("Name", aadhaar_data.full_name),
                ("Date of Birth", aadhaar_data.date_of_birth),
                ("Aadhaar Number", aadhaar_data.aadhaar_number)
            ] if not v]
            return None, f"❌ Could not extract: {', '.join(missing)}. Upload a clearer image."

        return aadhaar_data, "✅ Data extracted successfully"

    except json.JSONDecodeError:
        return None, "❌ AI response was not valid JSON. Please try again."
    except Exception as e:
        if _is_quota_error(str(e)):
            return MOCK_AADHAAR, "⚠️ API quota exceeded — using demo data for presentation"
        return None, f"❌ Extraction failed: {str(e)}"


# ─────────────────────────────────────────────
# MODULE 2: DETERMINISTIC RISK CHECKS
# ─────────────────────────────────────────────

def calculate_age(dob_str: str) -> Optional[int]:
    try:
        dob   = datetime.strptime(dob_str, "%d/%m/%Y")
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except ValueError:
        return None


def run_deterministic_checks(aadhaar_data: AadhaarData) -> dict:
    flags = []
    risk  = "Low"

    age = calculate_age(aadhaar_data.date_of_birth) if aadhaar_data.date_of_birth else None
    if age is None:
        flags.append("⚠️ Date of birth could not be parsed — manual check required")
        risk = "Medium"
    elif age < 18:
        flags.append(
            f"🚨 AGE ALERT: Applicant is {age} years old — under 18. "
            "Child Labour Act 2016 applies. Immediate rejection recommended."
        )
        risk = "High"
    elif age > 70:
        flags.append(f"⚠️ Age is {age} — please verify document is current")
        risk = "Medium"

    if aadhaar_data.aadhaar_number:
        if not re.match(r"^\d{12}$", aadhaar_data.aadhaar_number):
            flags.append("⚠️ Aadhaar number format invalid — must be exactly 12 digits")
            risk = "High" if risk != "High" else risk
        invalid = {"000000000000", "111111111111", "222222222222",
                   "123456789012", "999999999999"}
        if aadhaar_data.aadhaar_number in invalid:
            flags.append("🚨 Aadhaar number appears to be a test/invalid number")
            risk = "High"
    else:
        flags.append("⚠️ Aadhaar number missing")
        risk = "High"

    if aadhaar_data.full_name:
        if len(aadhaar_data.full_name.strip()) < 3:
            flags.append("⚠️ Name appears too short — verify manually")
            risk = "Medium" if risk == "Low" else risk
        if re.search(r"\d", aadhaar_data.full_name):
            flags.append("⚠️ Name contains digits — possible extraction error")
            risk = "Medium" if risk == "Low" else risk

    notes = (
        f"Age valid ({age} yrs) · Aadhaar format correct · No anomalies detected"
        if not flags else " · ".join(flags)
    )
    return {"risk_score": risk, "flags": flags, "notes": notes, "age": age}


# ─────────────────────────────────────────────
# MODULE 2: AI CONFIDENCE AUDITOR (Step 2 of chain)
# ─────────────────────────────────────────────

CONFIDENCE_PROMPT = """
You are a quality auditor for a government AI system in Gujarat, India.

A Vision AI just extracted this data from an Aadhaar card:
Name: {name}
Date of Birth: {dob}
Aadhaar (masked): {aadhaar_masked}
Gender: {gender}

Rate confidence in each field (0-100) and give an overall score.

Output ONLY valid JSON, no markdown:
{{
  "field_scores": {{
    "full_name": 90,
    "date_of_birth": 85,
    "aadhaar_number": 70,
    "gender": 95
  }},
  "overall_score": 85,
  "concerns": "One specific concern or None detected",
  "recommendation": "MANUAL_REVIEW_REQUIRED"
}}

recommendation must be exactly one of:
AUTO_APPROVE, MANUAL_REVIEW_REQUIRED, REJECT
"""


def run_confidence_audit(aadhaar_data: AadhaarData) -> dict:
    """Step 2 of agent chain: second AI call audits the first call's output."""
    prompt = CONFIDENCE_PROMPT.format(
        name=aadhaar_data.full_name or "null",
        dob=aadhaar_data.date_of_birth or "null",
        aadhaar_masked=mask_display(aadhaar_data.aadhaar_number),
        gender=aadhaar_data.gender or "null"
    )
    try:
        raw = _call_gemini(prompt)
        raw = re.sub(r"```json\s*|```", "", raw).strip()
        return json.loads(raw)
    except Exception as e:
        if _is_quota_error(str(e)):
            return {
                "field_scores": {"full_name": 88, "date_of_birth": 92,
                                 "aadhaar_number": 78, "gender": 95},
                "overall_score": 88,
                "concerns": "Demo mode — audit unavailable",
                "recommendation": "MANUAL_REVIEW_REQUIRED"
            }
        return {"overall_score": 0, "concerns": str(e),
                "recommendation": "MANUAL_REVIEW_REQUIRED"}


# ─────────────────────────────────────────────
# MODULE 2: REJECTION NOTICE GENERATOR
# ─────────────────────────────────────────────

REJECTION_PROMPTS = {
    "Gujarati": """
તમે ગુજરાત ઘરેલુ કામદાર નોંધણી પ્રણાલી માટે એક આધિકારિક નોટિસ લખો.
ભૂમિકા: ગુજરાત શ્રમ વિભાગ અધિકારી. ભાષા: ગુજરાતી.
નામ: {name}. નોંધણી ક્રમાંક: {ref_id}. નામંjur કારણ: {reason}
3 વાક્યોમાં, ઔપચારિક ભાષામાં: 1) નામ ક્રમાંક 2) કારણ 3) eSeva Center અથવા aadhaar.uidai.gov.in
ફક્ત નોટિસ ટેક્સ્ટ. No markdown.
""",
    "Hindi": """
गुजरात घरेलू कामगार पंजीकरण प्रणाली के लिए आधिकारिक नोटिस लिखें।
भूमिका: गुजरात श्रम विभाग अधिकारी। भाषा: हिंदी।
नाम: {name}. संख्या: {ref_id}. कारण: {reason}
3 वाक्यों में: 1) नाम संख्या 2) अस्वीकृति कारण 3) eSeva Center
केवल नोटिस टेक्स्ट। No markdown.
""",
    "English": """
Write an official rejection notice for the Gujarat Domestic Worker Registration System.
Role: Gujarat Labour Department Officer. Language: English.
Name: {name}. Registration: {ref_id}. Reason: {reason}
3 sentences: 1) Acknowledge name and ID 2) State reason 3) Direct to eSeva Center
Output only the notice text. No markdown.
""",
}


def generate_rejection_notice(name: str, ref_id: str, reason: str,
                               language: str = "Gujarati") -> str:
    prompt = REJECTION_PROMPTS.get(language, REJECTION_PROMPTS["English"]).format(
        name=name, ref_id=ref_id, reason=reason
    )
    try:
        return _call_gemini(prompt)
    except Exception as e:
        fallbacks = {
            "Gujarati": f"પ્રિય {name},\nઆપની નોંધણી ({ref_id}) નામjur. કારણ: {reason}.\neSeva Center નો સંપર્ક કરો.\nગુજરાત શ્રમ વિભાગ",
            "Hindi":    f"प्रिय {name},\nपंजीकरण ({ref_id}) अस्वीकृत। कारण: {reason}।\neSeva Center से संपर्क करें।\nगुजरात श्रम विभाग",
            "English":  f"Dear {name},\nRegistration ({ref_id}) rejected. Reason: {reason}.\nContact nearest eSeva Center.\nGujarat Labour Department",
        }
        return fallbacks.get(language, fallbacks["English"])


# ─────────────────────────────────────────────
# MODULE 3: NATURAL LANGUAGE WORK REQUEST PARSER
# ─────────────────────────────────────────────

WORK_REQUEST_PROMPT = """
You are an assistant for the Gujarat Domestic Worker Management System.

Employer request: "{natural_language_request}"
Worker name: {worker_name}
Today: {today}
Tomorrow: {tomorrow}

Extract:
- request_date: YYYY-MM-DD (use tomorrow's date if request says "tomorrow")
- extra_hours: integer 1-4
- reason: one sentence

Output ONLY valid JSON:
{{"request_date": "YYYY-MM-DD", "extra_hours": 2, "reason": "Party preparation"}}

If unclear: {{"error": "Please specify date and number of hours."}}
"""

MOCK_WORK_REQUEST = {
    "request_date": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
    "extra_hours":  2,
    "reason":       "Extra work requested (demo mode)",
}


def parse_work_request(natural_language: str, worker_name: str) -> dict:
    today    = date.today()
    tomorrow = today + timedelta(days=1)
    prompt   = WORK_REQUEST_PROMPT.format(
        natural_language_request=natural_language,
        worker_name=worker_name,
        today=today.strftime("%Y-%m-%d"),
        tomorrow=tomorrow.strftime("%Y-%m-%d"),
    )
    try:
        raw = _call_gemini(prompt)
        raw = re.sub(r"```json\s*|```", "", raw).strip()
        result = json.loads(raw)
        if "extra_hours" in result:
            try:
                result["extra_hours"] = max(1, min(4, int(result["extra_hours"])))
            except (ValueError, TypeError):
                result["extra_hours"] = 1
        return result
    except Exception as e:
        if _is_quota_error(str(e)):
            return MOCK_WORK_REQUEST
        return {"error": f"Could not parse request: {str(e)}"}