import json
import logging
import re
from groq import Groq
from config import GROQ_API_KEY, USE_MOCK_SERVICES, DEPARTMENTS, PRIORITIES, SENTIMENTS, CATEGORIES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── System Prompt ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are SmartDesk AI — an enterprise IT Service Desk analyst AI.
Read the following employee support call transcript and extract structured information.

Return ONLY a valid JSON object with these exact keys (no extra text, no markdown):

{
  "employee_name":       "Full name if the employee explicitly stated it (e.g. 'my name is John Smith'). Empty string if not mentioned.",
  "employee_id":         "Employee ID if explicitly stated (e.g. EMP1001, E-2034). Empty string if not mentioned.",
  "mobile_number":       "Phone/mobile number if explicitly provided. Empty string if not mentioned.",
  "email":               "Email address if explicitly provided. Empty string if not mentioned.",

  "title":               "Short, descriptive issue title (max 8 words)",
  "description":         "Full, detailed problem description extracted from the transcript",

  "category":            "Exactly one of: Networking, Hardware, Email & Collaboration, Application Support, Infrastructure, Cybersecurity, Management, Accounts",

  "priority":            "Exactly one of: Critical, High, Medium, Low",

  "assigned_department": "Exactly one of: Networking Team, Hardware Support Team, Email & Collaboration Team, Application Support Team, Infrastructure Team, Cybersecurity Team, Management Team, Accounts Team",

  "sentiment":           "Exactly one of: Positive, Neutral, Frustrated, Angry",

  "ticket_summary":      "1-2 sentence AI-generated summary of the issue",

  "suggested_resolution":"Numbered action checklist (2-3 steps) for the support engineer"
}

DEPARTMENT ROUTING RULES:
- VPN / WiFi / Internet / DNS / Network failures → Networking Team
- Laptop / Desktop / Printer / Monitor / Physical hardware → Hardware Support Team
- Outlook / Email sync / Teams / Shared mailbox → Email & Collaboration Team
- ERP / CRM / App crashes / Login failures / Software bugs → Application Support Team
- Server / Cloud / VM / Storage / Backup failures → Infrastructure Team
- Malware / Phishing / Ransomware / Unauthorized access / Security alerts → Cybersecurity Team
- Executive escalation / Business-critical approvals → Management Team
- Payroll / Reimbursement / Finance / Salary issues → Accounts Team

PRIORITY RULES:
- Critical: Security incident, major outage, business interruption, data loss risk
- High: Affects multiple employees or blocks a team's work
- Medium: Single employee affected, workaround may exist
- Low: Information request, minor issue, feature question

IMPORTANT: employee_name, employee_id, mobile_number, email must be empty strings if the employee did NOT explicitly state them. Do NOT invent or guess personal information."""


# ── Regex patterns for personal info detection ─────────────────────────────────

_NAME_RE = [
    r"\bmy name is\b", r"\bthis is\b", r"\bi['']?m\b", r"\bi am\b",
    r"\bspeaking\b", r"\bcalling from\b", r"\bcalling on behalf\b"
]
_ID_RE = [
    r"\bemp(?:loyee)?\s*(?:id|number|code|#)[\s:is]*[a-z0-9\-]+",
    r"\bstaff\s+id\b", r"\bemployee\s+number\b"
]
_PHONE_RE = [
    r"\b\+?[\d][\d\s\-\.]{7,}\d\b",
    r"\bmy\s+(?:phone|mobile|number|contact|cell)\b"
]
_EMAIL_RE = [r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b"]


def _has_personal_info(transcript: str) -> bool:
    """Returns True if transcript contains signals of real personal information."""
    text = transcript.lower()
    for pattern_list in [_NAME_RE, _ID_RE, _PHONE_RE, _EMAIL_RE]:
        if any(re.search(p, text) for p in pattern_list):
            return True
    return False


# ── Mock Extraction (offline / demo mode) ─────────────────────────────────────

_MOCK_SCENARIOS = [
    {
        "keywords": ["vpn", "wifi", "internet", "network", "dns", "connectivity"],
        "category": "Networking",
        "priority": "High",
        "assigned_department": "Networking Team",
        "title": "VPN Connection Failure After System Update",
        "ticket_summary": "Employee unable to connect to corporate VPN after a Windows update, blocking remote work.",
        "suggested_resolution": "1. Ask employee to reinstall VPN client and restart.\n2. Check if split-tunnel policy changed post-update.\n3. Escalate to network admin if issue persists.",
        "sentiment": "Frustrated",
    },
    {
        "keywords": ["laptop", "desktop", "monitor", "printer", "screen", "keyboard", "hardware"],
        "category": "Hardware",
        "priority": "Medium",
        "assigned_department": "Hardware Support Team",
        "title": "Laptop Not Powering On",
        "ticket_summary": "Employee's laptop fails to boot; power LED not illuminating despite multiple restart attempts.",
        "suggested_resolution": "1. Perform hard reset (hold power 10s).\n2. Check battery/charger with another unit.\n3. Arrange hardware swap if no improvement.",
        "sentiment": "Frustrated",
    },
    {
        "keywords": ["outlook", "email", "teams", "mailbox", "calendar", "sync"],
        "category": "Email & Collaboration",
        "priority": "Medium",
        "assigned_department": "Email & Collaboration Team",
        "title": "Outlook Not Syncing Emails",
        "ticket_summary": "Outlook inbox not updating; employee is missing critical client communications.",
        "suggested_resolution": "1. Run Outlook repair tool (ScanPST).\n2. Re-add Exchange mailbox profile.\n3. Check mail server connectivity from admin portal.",
        "sentiment": "Frustrated",
    },
    {
        "keywords": ["crash", "freeze", "bug", "error", "software", "application", "erp", "crm", "login"],
        "category": "Application Support",
        "priority": "High",
        "assigned_department": "Application Support Team",
        "title": "Application Crashing on Report Export",
        "ticket_summary": "Desktop ERP application crashes every time user attempts to export weekly reports.",
        "suggested_resolution": "1. Update application to latest patch.\n2. Check crash logs for memory/dependency errors.\n3. Roll back last deployment if issue is version-specific.",
        "sentiment": "Angry",
    },
    {
        "keywords": ["server", "cloud", "vm", "backup", "storage", "database", "outage"],
        "category": "Infrastructure",
        "priority": "Critical",
        "assigned_department": "Infrastructure Team",
        "title": "Production Server Outage Affecting All Users",
        "ticket_summary": "Primary production server is down; all users are unable to access business systems.",
        "suggested_resolution": "1. Initiate failover to standby server immediately.\n2. Alert all department heads.\n3. Begin root-cause analysis in parallel.",
        "sentiment": "Angry",
    },
    {
        "keywords": ["malware", "virus", "phishing", "ransomware", "hacked", "security", "breach", "unauthorized"],
        "category": "Cybersecurity",
        "priority": "Critical",
        "assigned_department": "Cybersecurity Team",
        "title": "Suspected Phishing Attack on Employee Account",
        "ticket_summary": "Employee received a suspicious email containing malicious links; possible credential compromise.",
        "suggested_resolution": "1. Immediately disable employee account and reset credentials.\n2. Isolate device from network.\n3. Run full endpoint security scan and review email gateway logs.",
        "sentiment": "Frustrated",
    },
    {
        "keywords": ["payroll", "salary", "reimbursement", "finance", "accounts", "payment", "invoice"],
        "category": "Accounts",
        "priority": "High",
        "assigned_department": "Accounts Team",
        "title": "Payroll Not Processed for Current Month",
        "ticket_summary": "Employee reports salary not credited for the current pay cycle, requesting immediate resolution.",
        "suggested_resolution": "1. Verify payroll run status in finance system.\n2. Check if bank account details are updated correctly.\n3. Process manual payment if systemic delay confirmed.",
        "sentiment": "Angry",
    },
]


def get_mock_extraction(transcript: str) -> dict:
    """Keyword-based mock extraction for offline/demo mode."""
    text = transcript.lower()
    matched = None
    for scenario in _MOCK_SCENARIOS:
        if any(kw in text for kw in scenario["keywords"]):
            matched = scenario
            break

    if not matched:
        matched = {
            "category": "Application Support",
            "priority": "Low",
            "assigned_department": "Application Support Team",
            "title": "General IT Support Request",
            "ticket_summary": "Employee submitted a general IT support request requiring assistance.",
            "suggested_resolution": "1. Review employee's request in detail.\n2. Assign to appropriate engineer.\n3. Follow up within 24 hours.",
            "sentiment": "Neutral",
        }

    has_personal = _has_personal_info(transcript)

    # Extract personal details from transcript using regex if present
    emp_name = ""
    emp_id = ""
    mobile = ""
    email_addr = ""

    if has_personal:
        # Email (most reliable)
        email_match = re.search(r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b", transcript, re.I)
        if email_match:
            email_addr = email_match.group(0)

        # Phone
        phone_match = re.search(r"\b(\+?[\d][\d\s\-\.]{7,}\d)\b", transcript)
        if phone_match:
            mobile = phone_match.group(1).strip()

        # Employee ID
        id_match = re.search(r"\b(EMP\d+|E-\d{3,}|STAFF-?\d+)\b", transcript, re.I)
        if id_match:
            emp_id = id_match.group(1).upper()

    return {
        "employee_name": emp_name,
        "employee_id": emp_id,
        "mobile_number": mobile,
        "email": email_addr,
        "title": matched["title"],
        "description": transcript,
        "category": matched["category"],
        "priority": matched["priority"],
        "assigned_department": matched["assigned_department"],
        "sentiment": matched["sentiment"],
        "ticket_summary": matched["ticket_summary"],
        "suggested_resolution": matched["suggested_resolution"],
        "has_personal_details": has_personal,
    }


# ── Live LLM Extraction ────────────────────────────────────────────────────────

def extract_ticket_info(transcript: str) -> dict:
    """
    Extracts structured ticket information from a raw support call transcript.
    Uses Groq LLaMA-3 when USE_MOCK_SERVICES=False, mock otherwise.
    """
    if not transcript or not transcript.strip():
        raise ValueError("Transcript cannot be empty.")

    if USE_MOCK_SERVICES:
        logger.info("Using mock extraction service.")
        return get_mock_extraction(transcript)

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing. Set USE_MOCK_SERVICES=True for demo mode.")

    logger.info("Initiating Groq LLaMA extraction.")
    client = Groq(api_key=GROQ_API_KEY)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Extract ticket info from this support call transcript:\n\n{transcript}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        raw = response.choices[0].message.content
        data = json.loads(raw)

        # ── Post-validation ────────────────────────────────────────────────────
        # Required fields — ensure non-empty
        for field in ["title", "description", "category", "priority"]:
            if not data.get(field, "").strip():
                data[field] = "Unknown" if field != "priority" else "Medium"

        # Validate category
        if data.get("category") not in CATEGORIES:
            cat = data.get("category", "").lower()
            if any(k in cat for k in ["network", "vpn", "wifi", "dns"]):
                data["category"] = "Networking"
            elif any(k in cat for k in ["hardware", "laptop", "printer"]):
                data["category"] = "Hardware"
            elif any(k in cat for k in ["email", "outlook", "teams"]):
                data["category"] = "Email & Collaboration"
            elif any(k in cat for k in ["server", "cloud", "infra", "vm"]):
                data["category"] = "Infrastructure"
            elif any(k in cat for k in ["security", "cyber", "malware"]):
                data["category"] = "Cybersecurity"
            elif any(k in cat for k in ["account", "payroll", "finance"]):
                data["category"] = "Accounts"
            else:
                data["category"] = "Application Support"

        # Validate department
        if data.get("assigned_department") not in DEPARTMENTS:
            data["assigned_department"] = "Application Support Team"

        # Validate priority & sentiment
        if data.get("priority") not in PRIORITIES:
            data["priority"] = "Medium"
        if data.get("sentiment") not in SENTIMENTS:
            data["sentiment"] = "Neutral"

        # Determine personal details flag
        has_personal = _has_personal_info(transcript)
        data["has_personal_details"] = has_personal

        # Clear personal fields if nothing was detected
        if not has_personal:
            data["employee_name"] = ""
            data["employee_id"] = ""
            data["mobile_number"] = ""
            data["email"] = ""

        return data

    except Exception as e:
        logger.error(f"LLM extraction failed: {e}. Falling back to mock.")
        fallback = get_mock_extraction(transcript)
        fallback["title"] = f"[Recovery] {fallback['title']}"
        return fallback
