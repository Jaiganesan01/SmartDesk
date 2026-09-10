import os
import random
import tempfile
from groq import Groq
from config import GROQ_API_KEY, USE_MOCK_SERVICES

# Mock transcripts representing all 8 enterprise departments and scenarios
MOCK_TRANSCRIPTS = {
    "networking": (
        "Hi, this is Sarah Connor, employee ID EMP1984. I'm calling because my corporate VPN keeps dropping "
        "every ten or fifteen minutes while I'm trying to work from home. It's really frustrating and preventing me "
        "from accessing internal file servers. You can reach me at +1-555-0199."
    ),
    "hardware": (
        "Hello, this is John Doe, employee ID EMP2004. I need support because my secondary external monitor is flickering "
        "and keeps going completely black. I tried replacing the HDMI cable but it didn't do anything. My number is 555-0248."
    ),
    "email": (
        "Hi, my name is David Wallace and my employee ID is EMP0001. My corporate mailbox in Outlook is not synchronizing. "
        "It says Disconnected in the bottom bar and I am not receiving any incoming emails. My contact number is 555-9000."
    ),
    "application": (
        "Hey, this is Ryan Howard. I'm trying to log in to the ERP application to upload the financial reports, "
        "but it keeps showing a User Not Authorized error. I need this fixed immediately. My cell is 555-8812."
    ),
    "infrastructure": (
        "This is Angela Martin, employee ID EMP0341. The backup database VM is refusing database connections on port 5432, "
        "throwing timeout errors. This is blocking our audit updates. My contact number is 555-0341."
    ),
    "security": (
        "Hello, my name is Oscar Martinez. I just received a highly suspicious email claiming to contain a vendor invoice. "
        "It looks like a phishing attempt. I have not opened the attachment or clicked any link. Please investigate. My phone is 555-2319."
    ),
    "management": (
        "This is Jan Levinson, employee ID EMP0004. We have an urgent escalation. The client demo environment is failing "
        "and we have a major presentation tomorrow morning. I need a senior engineer assigned immediately. My phone is 555-0004."
    ),
    "accounts": (
        "Hi, Kelly Kapoor here. My employee ID is EMP4432. I'm calling because my travel expense reimbursement check was "
        "short by three hundred dollars. I was only paid one hundred and fifty instead of four hundred and fifty. Call me at 555-4432."
    )
}

def get_mock_transcript(filename: str = "") -> str:
    """Helper to select a mock transcript based on keywords in the filename or at random."""
    fn_lower = filename.lower()
    if any(k in fn_lower for k in ["vpn", "wifi", "internet", "network", "dns", "lan"]):
        return MOCK_TRANSCRIPTS["networking"]
    elif any(k in fn_lower for k in ["monitor", "laptop", "screen", "keyboard", "printer", "hardware", "mouse"]):
        return MOCK_TRANSCRIPTS["hardware"]
    elif any(k in fn_lower for k in ["email", "outlook", "mail", "teams", "sync", "mailbox"]):
        return MOCK_TRANSCRIPTS["email"]
    elif any(k in fn_lower for k in ["erp", "crm", "login", "auth", "credential", "application"]):
        return MOCK_TRANSCRIPTS["application"]
    elif any(k in fn_lower for k in ["server", "vm", "cloud", "backup", "db", "database", "infrastructure"]):
        return MOCK_TRANSCRIPTS["infrastructure"]
    elif any(k in fn_lower for k in ["phishing", "security", "malware", "virus", "hack"]):
        return MOCK_TRANSCRIPTS["security"]
    elif any(k in fn_lower for k in ["escalation", "executive", "demo", "management"]):
        return MOCK_TRANSCRIPTS["management"]
    elif any(k in fn_lower for k in ["payroll", "reimbursement", "salary", "accounts", "finance", "expense"]):
        return MOCK_TRANSCRIPTS["accounts"]
    
    # Default to a random one
    return random.choice(list(MOCK_TRANSCRIPTS.values()))

def transcribe_audio(file_bytes: bytes, filename: str = "") -> str:
    """
    Transcribes audio bytes into text.
    If USE_MOCK_SERVICES is True, returns a mock transcript.
    Otherwise, writes the bytes to a temp file and sends it to Groq Whisper API.
    """
    if USE_MOCK_SERVICES:
        return get_mock_transcript(filename)
    
    if not GROQ_API_KEY:
        raise ValueError("Groq API key is missing but USE_MOCK_SERVICES is set to False.")
        
    client = Groq(api_key=GROQ_API_KEY)
    
    # Get file extension from filename or default to mp3
    ext = os.path.splitext(filename)[1] if filename else ".mp3"
    if ext not in [".mp3", ".wav", ".m4a", ".ogg", ".webm"]:
        ext = ".mp3"
        
    # Write to a temporary file
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_audio:
        temp_audio.write(file_bytes)
        temp_audio_path = temp_audio.name
        
    try:
        with open(temp_audio_path, "rb") as audio_file:
            transcript_obj = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file
            )
        return transcript_obj.text
    finally:
        # Clean up temp file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

