# 🏛️ Gujarat Domestic Worker Registration System
### AI-Powered · Government-Grade · DPDP Act 2023 Compliant

A full-lifecycle, AI-native platform connecting domestic workers, the Gujarat Government,
and employers into a single verified ecosystem.

---

## Problem Statement

The domestic worker sector in Gujarat operates informally — no verified identities,
no legal work status, no safety accountability. This exposes workers to exploitation,
denies them legal protections, and makes government oversight impossible.

---

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Worker Portal  │    │  Gov Admin Portal │    │ Employer Portal │
│                 │    │                  │    │                 │
│ Upload Aadhaar  │    │ Review · Approve  │    │ Verified Badge  │
│ Vision AI scan  │    │ Reject · Audit    │    │ Extra hrs req.  │
│ Log holidays    │    │ Dashboar metrics  │    │ NL parsing      │
└────────┬────────┘    └────────┬─────────┘    └────────┬────────┘
         │                      │                       │
         └──────────────────────┼───────────────────────┘
                                │
                    ┌───────────▼──────────┐
                    │   Streamlit App      │
                    │   (app.py)           │
                    └───────────┬──────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
    ┌─────────▼──────┐ ┌───────▼───────┐ ┌──────▼──────────┐
    │  ai_agent.py   │ │  database.py  │ │ translations.py │
    │                │ │               │ │                 │
    │ Gemini Vision  │ │ SQLite        │ │ Gujarati        │
    │ Risk scoring   │ │ Workers       │ │ Hindi           │
    │ Rejection AI   │ │ Employers     │ │ English         │
    │ NL parsing     │ │ Audit Log     │ │                 │
    └────────────────┘ │ Leaves        │ └─────────────────┘
                       └───────────────┘
```

---

## Tech Stack (All Free)

| Component | Tool | Reason |
|-----------|------|--------|
| Frontend UI | Streamlit | Fastest Python-to-web, no JS needed |
| Vision AI | Gemini 1.5 Flash | Free tier, multimodal, best for Indian IDs |
| Text AI | Gemini 1.5 Flash | Same model, rejection notices + NL parsing |
| Database | SQLite | Built into Python, zero config |
| Validation | Pydantic v2 | Strict structured output from AI |
| Language | Python 3.9+ | Industry standard for AI prototypes |

---

## Regulatory Compliance

### DPDP Act 2023 (Digital Personal Data Protection)
- Aadhaar card images are processed **in-memory only** — never written to disk
- Raw Aadhaar numbers are **immediately deleted** after extraction
- Only SHA-256 hashed identifiers are stored in the database
- Worker consent is **explicitly captured** before any data is stored
- `del image_bytes` called immediately after Gemini API call

### UIDAI Guidelines
- Full Aadhaar numbers are **never displayed or stored**
- Only last 4 digits shown: `XXXX XXXX 9012`
- Numbers stored as one-way SHA-256 hash only

### Labour Code 2020
- Maximum 9 hours/day enforced programmatically
- Maximum 48 hours/week enforced with database check
- Extra work requests exceeding limits are rejected before submission
- Live Labour Code compliance indicator on employer portal

### IT Act Section 43A
- Reasonable security practices enforced
- All sensitive operations logged to tamper-evident audit table
- Sensitive data fields limited to minimum necessary

### Child Labour Act 2016
- Age calculated from extracted DOB
- Workers under 18 are **automatically flagged as High Risk**
- AI note includes explicit Child Labour Act reference
- Officer cannot approve without seeing the flag

---

## Human-In-Loop Mandate

**The AI recommends. A human decides. Always.**

```python
# This check exists in database.py — cannot be bypassed
assert officer_id and officer_id.strip(), \
    "COMPLIANCE ERROR: Officer ID required for approval. AI cannot auto-approve."
```

Every approval/rejection requires:
1. A logged-in officer ID
2. A human button click
3. A timestamped audit log entry

---

## Setup Instructions

### 1. Get Free Gemini API Key
- Go to [aistudio.google.com](https://aistudio.google.com)
- Sign in with any Google account
- Click "Get API Key" → "Create API key"
- Copy the key

### 2. Clone and Setup
```bash
git clone <your-repo>
cd gujarat_worker_system
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env and paste your Gemini API key
```

### 4. Run
```bash
streamlit run app.py
```
The app opens at `http://localhost:8501`

---

## Demo Flow

### Role: Worker
1. Select "Worker Portal" in sidebar
2. Upload a photo of an Aadhaar card (front side)
3. Click "Extract" — Gemini reads the card automatically
4. Verify the extracted Name, DOB, Aadhaar (masked)
5. Enter phone and address
6. Check the consent box
7. Submit → get Reference ID

### Role: Government Admin
1. Select "Gov Admin Portal"
2. Enter Officer ID (e.g., `OFF-001`)
3. See dashboard metrics and all pending workers
4. Review AI risk score and notes per worker
5. Click Approve or enter rejection reason
6. Generate AI-drafted rejection notice in worker's language

### Role: Employer
1. Select "Employer Portal"
2. Pick your business from the dropdown
3. See your worker's Government Verified badge
4. Type a natural language extra-hours request
5. System checks Labour Code 2020 compliance live
6. Submit request to worker

---

## Pitch Summary

> "This system addresses Article 23 of the Indian Constitution — prohibition of forced labour —
> by creating an auditable, digital trail for every domestic worker in Gujarat.
> The AI extracts and flags, but a licensed officer always makes the final decision.
> We comply fully with DPDP Act 2023 by processing Aadhaar images in-memory only
> and storing only hashed identifiers. Every screen is in Gujarati first,
> ensuring 100% accessibility for the target population."

---

## File Structure

```
gujarat_worker_system/
├── app.py              ← Main Streamlit UI (all 3 portals)
├── database.py         ← SQLite + all DB functions + seed data
├── ai_agent.py         ← Gemini Vision + risk scoring + NL parsing
├── translations.py     ← Gujarati / Hindi / English strings
├── requirements.txt    ← pip dependencies
├── .env.example        ← API key template
├── .env                ← Your actual keys (gitignored)
└── README.md           ← This file
```

---

*Built for Gujarat Labour & Employment Department · Powered by Google Gemini · © 2025*
