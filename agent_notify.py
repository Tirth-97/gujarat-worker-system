# agent_notify.py
# Notification Specialist Agent
# Generates contextual messages for any system event in Gujarati / Hindi / English
# Uses templates for speed, falls back to AI for complex cases

from datetime import date as date_type

# ── All notification templates ──
# Template keys map to (Gujarati, Hindi, English) messages
TEMPLATES = {
    "REGISTRATION_RECEIVED": {
        "Gujarati": "નોંધણી સ્વીકૃત — સંદર્ભ ક્રમાંક {ref_id}. સરકારી ચકાસણી 2-3 કામકાજી દિવસોમાં પૂર્ણ થશે.",
        "Hindi":    "पंजीकरण प्राप्त — संदर्भ संख्या {ref_id}। सरकारी सत्यापन 2-3 कार्य दिवसों में।",
        "English":  "Registration received — Reference {ref_id}. Government verification in 2-3 working days.",
    },
    "APPROVED": {
        "Gujarati": "અભિનંદન {name}! આપની નોંધણી ({ref_id}) ગુજરાત સરકાર દ્વારા મંjur કરવામાં આવી છે.",
        "Hindi":    "बधाई {name}! आपका पंजीकरण ({ref_id}) गुजरात सरकार द्वारा स्वीकृत किया गया है।",
        "English":  "Congratulations {name}! Your registration ({ref_id}) has been approved by the Gujarat Government.",
    },
    "REJECTED": {
        "Gujarati": "પ્રિય {name}, આપની નોંધણી ({ref_id}) નામjur. કારણ: {reason}. eSeva Center નો સંપર્ક કરો.",
        "Hindi":    "प्रिय {name}, आपका पंजीकरण ({ref_id}) अस्वीकृत। कारण: {reason}। eSeva Center से संपर्क करें।",
        "English":  "Dear {name}, your registration ({ref_id}) has been rejected. Reason: {reason}. Contact eSeva Center.",
    },
    "LEAVE_CONFIRMED": {
        "Gujarati": "{name} ની {date} ની રજા નોંધ લેવામાં આવી છે.",
        "Hindi":    "{name} की {date} की छुट्टी दर्ज की गई है।",
        "English":  "{name}'s leave on {date} has been recorded.",
    },
    "LEAVE_EMPLOYER_NOTIFY": {
        "Gujarati": "સૂચના: {name} {date} ના રોજ ગેરહાજર રહેશે. કારણ: {reason}.",
        "Hindi":    "सूचना: {name} {date} को अनुपस्थित रहेंगी। कारण: {reason}।",
        "English":  "Notice: {name} will be absent on {date}. Reason: {reason}.",
    },
    "EXTRA_HOURS_REQUEST": {
        "Gujarati": "{employer} વતી વિનંતી: {date} ના રોજ {hours} વધારાના કલાક. કારણ: {reason}.",
        "Hindi":    "{employer} की ओर से अनुरोध: {date} को {hours} अतिरिक्त घंटे। कारण: {reason}।",
        "English":  "Request from {employer}: {hours} extra hours on {date}. Reason: {reason}.",
    },
    "HIGH_RISK_FLAG": {
        "Gujarati": "ઉચ્ચ જોખમ: {name} ({ref_id}) ની નોંધણીમાં {issue} — અધિકારી સમીક્ષા જરૂરી.",
        "Hindi":    "उच्च जोखिम: {name} ({ref_id}) के पंजीकरण में {issue} — अधिकारी समीक्षा आवश्यक।",
        "English":  "High risk: {name} ({ref_id}) registration flagged for {issue} — officer review required.",
    },
}


def generate_notification(
    event_type:  str,
    worker:      dict,
    language:    str = "Gujarati",
    **kwargs
) -> str:
    """
    Generate a notification message for any system event.

    Args:
        event_type: One of the TEMPLATES keys above
        worker:     dict with full_name, ref_id, etc.
        language:   "Gujarati", "Hindi", or "English"
        **kwargs:   Extra variables for the template (reason, date, etc.)

    Returns:
        Formatted notification string in the requested language
    """
    template_group = TEMPLATES.get(event_type)
    if not template_group:
        # Unknown event — generate a generic message
        return _generic_message(event_type, worker, language)

    template = template_group.get(language, template_group.get("English", ""))

    # Build format variables from worker dict + kwargs
    format_vars = {
        "name":    worker.get("full_name", ""),
        "ref_id":  worker.get("ref_id", ""),
        "status":  worker.get("status", ""),
        **kwargs
    }

    try:
        return template.format(**format_vars)
    except KeyError as e:
        # Missing variable — return template with placeholder
        return template.replace("{" + str(e).strip("'") + "}", f"[{e}]")


def _generic_message(event_type: str, worker: dict, language: str) -> str:
    """Fallback for unknown event types."""
    name   = worker.get("full_name", "")
    ref_id = worker.get("ref_id", "")
    messages = {
        "Gujarati": f"{name} ({ref_id}): {event_type} નોંધ.",
        "Hindi":    f"{name} ({ref_id}): {event_type} दर्ज।",
        "English":  f"{name} ({ref_id}): {event_type} recorded.",
    }
    return messages.get(language, messages["English"])


def notify_registration(worker: dict, language: str = "Gujarati") -> str:
    return generate_notification("REGISTRATION_RECEIVED", worker, language)

def notify_approved(worker: dict, language: str = "Gujarati") -> str:
    return generate_notification("APPROVED", worker, language)

def notify_rejected(worker: dict, reason: str, language: str = "Gujarati") -> str:
    return generate_notification("REJECTED", worker, language, reason=reason)

def notify_leave(worker: dict, leave_date: str, language: str = "Gujarati") -> str:
    return generate_notification("LEAVE_CONFIRMED", worker, language, date=leave_date)

def notify_employer_leave(worker: dict, leave_date: str,
                           reason: str, language: str = "Gujarati") -> str:
    return generate_notification("LEAVE_EMPLOYER_NOTIFY", worker, language,
                                  date=leave_date, reason=reason)

def notify_extra_hours(worker: dict, employer_name: str,
                        hours: int, req_date: str,
                        reason: str, language: str = "Gujarati") -> str:
    return generate_notification("EXTRA_HOURS_REQUEST", worker, language,
                                  employer=employer_name, hours=hours,
                                  date=req_date, reason=reason)

def notify_high_risk(worker: dict, issue: str, language: str = "Gujarati") -> str:
    return generate_notification("HIGH_RISK_FLAG", worker, language, issue=issue)


def get_all_event_types() -> list[str]:
    """Return all supported notification event types."""
    return list(TEMPLATES.keys())