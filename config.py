import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ── Core API & Storage ─────────────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
DB_PATH: str = os.getenv("DB_PATH", "tickets.db")

# Parse mock service flag (default True if no API key)
_mock_str = os.getenv("USE_MOCK_SERVICES", "False").strip().lower()
USE_MOCK_SERVICES: bool = _mock_str in ("true", "1", "yes") or not GROQ_API_KEY

# ── Ticket Lifecycle ───────────────────────────────────────────────────────────
STATUSES = ["Pending", "Work In Progress", "Resolved"]

PRIORITIES = ["Critical", "High", "Medium", "Low"]

SENTIMENTS = ["Positive", "Neutral", "Frustrated", "Angry"]

# ── Supported Departments ──────────────────────────────────────────────────────
DEPARTMENTS = [
    "Networking Team",
    "Hardware Support Team",
    "Email & Collaboration Team",
    "Application Support Team",
    "Infrastructure Team",
    "Cybersecurity Team",
    "Management Team",
    "Accounts Team",
]

# ── Categories (mapped from departments for analytics) ─────────────────────────
CATEGORIES = [
    "Networking",
    "Hardware",
    "Email & Collaboration",
    "Application Support",
    "Infrastructure",
    "Cybersecurity",
    "Management",
    "Accounts",
]
# ── Email Service SMTP Defaults ───────────────────────────────────────────────
SMTP_HOST: str = os.getenv("SMTP_HOST", "")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
SMTP_SENDER: str = os.getenv("SMTP_SENDER", "")


def get_config_summary() -> dict:
    """Returns a safe (non-sensitive) summary for display in the UI."""
    return {
        "DB_PATH": DB_PATH,
        "USE_MOCK_SERVICES": USE_MOCK_SERVICES,
        "HAS_API_KEY": bool(GROQ_API_KEY),
        "GROQ_MODEL_WHISPER": "whisper-large-v3",
        "GROQ_MODEL_LLM": "llama-3.1-8b-instant",
    }
