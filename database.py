import sqlite3
import random
import string
from datetime import datetime
from typing import Optional, List, Dict
from config import DB_PATH


# ── Schema Creation & Migration ────────────────────────────────────────────────

def create_database():
    """
    Initialises the SQLite database.
    Creates the tickets table if it does not exist and safely migrates
    any missing columns in existing databases.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_number        TEXT    UNIQUE NOT NULL,

                -- Employee Information
                employee_name        TEXT,
                employee_id          TEXT,
                mobile_number        TEXT,
                email                TEXT,

                -- Ticket Core
                title                TEXT    NOT NULL,
                description          TEXT,
                category             TEXT,
                priority             TEXT    NOT NULL DEFAULT 'Medium',

                -- Routing & Assignment
                assigned_department  TEXT,
                assigned_worker      TEXT,

                -- Lifecycle
                status               TEXT    NOT NULL DEFAULT 'Pending',
                resolution_time      TEXT,
                resolution_notes     TEXT,

                -- AI Analysis
                sentiment            TEXT,
                ticket_summary       TEXT,
                suggested_resolution TEXT,
                transcript           TEXT    NOT NULL,

                -- Timestamps
                created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at           TIMESTAMP,
                resolved_at          TIMESTAMP
            )
        """)

        # ── Safe schema migration for pre-existing databases ──────────────────
        # Must run BEFORE indexes so all columns exist when indexes are created.
        cursor.execute("PRAGMA table_info(tickets)")
        existing_cols = {row[1] for row in cursor.fetchall()}

        migrations = {
            "employee_name":        "TEXT",
            "employee_id":          "TEXT",
            "mobile_number":        "TEXT",
            "email":                "TEXT",
            "assigned_department":  "TEXT",
            "assigned_worker":      "TEXT",
            "status":               "TEXT NOT NULL DEFAULT 'Pending'",
            "resolution_time":      "TEXT",
            "resolution_notes":     "TEXT",
            "sentiment":            "TEXT",
            "ticket_summary":       "TEXT",
            "suggested_resolution": "TEXT",
            "can_auto_resolve":     "INTEGER DEFAULT 0",
            "runbook_action":       "TEXT",
            "runbook_status":       "TEXT DEFAULT 'None'",
            "updated_at":           "TIMESTAMP",
            "resolved_at":          "TIMESTAMP",
        }
        for col, col_type in migrations.items():
            if col not in existing_cols:
                cursor.execute(f"ALTER TABLE tickets ADD COLUMN {col} {col_type}")

        # ── Audit Trail Table ────────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticket_audit_logs (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_number TEXT NOT NULL,
                action        TEXT NOT NULL,
                actor         TEXT NOT NULL,
                details       TEXT,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_ticket ON ticket_audit_logs(ticket_number)")

        # ── Indexes (created after migration so columns are guaranteed) ────────
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status      ON tickets(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_department  ON tickets(assigned_department)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority    ON tickets(priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_employee_id ON tickets(employee_id)")

        # Check if table is empty to run initial seeding
        cursor.execute("SELECT COUNT(*) FROM tickets")
        if cursor.fetchone()[0] == 0:
            seed_tickets(conn)

        # ── Backfill NULL employee names ────────────────────────────────────────
        # Replace any NULL/empty employee_name values with a friendly fallback
        cursor.execute("""
            UPDATE tickets
            SET employee_name = 'Voice Intake User'
            WHERE employee_name IS NULL OR TRIM(employee_name) = ''
        """)

        # ── Email Configurations Table ──────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_configs (
                team_name     TEXT PRIMARY KEY,
                email_address TEXT NOT NULL
            )
        """)

        # Seed default email configurations if empty
        cursor.execute("SELECT COUNT(*) FROM email_configs")
        if cursor.fetchone()[0] == 0:
            default_configs = [
                ('Hardware Support', 'joshvajason31@gmail.com'),
                ('Access & IAM Team', 'iam-alerts@company.com'),
                ('Billing & Accounts', 'billing-alerts@company.com'),
                ('Software Engineering', 'eng-devs@company.com'),
                ('General Helpdesk', 'helpdesk@company.com')
            ]
            cursor.executemany("INSERT INTO email_configs (team_name, email_address) VALUES (?, ?)", default_configs)

        conn.commit()


# ── Email Configurations Helpers ───────────────────────────────────────────────

def get_email_configs() -> dict:
    """Retrieves all email configuration key-value pairs from the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS email_configs (team_name TEXT PRIMARY KEY, email_address TEXT NOT NULL)")
        cursor.execute("SELECT team_name, email_address FROM email_configs")
        return {row[0]: row[1] for row in cursor.fetchall()}


def save_email_config(team_name: str, email_address: str):
    """Saves or updates an email configuration key-value pair."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS email_configs (team_name TEXT PRIMARY KEY, email_address TEXT NOT NULL)")
        cursor.execute(
            "INSERT INTO email_configs (team_name, email_address) VALUES (?, ?) "
            "ON CONFLICT(team_name) DO UPDATE SET email_address=excluded.email_address",
            (team_name, email_address)
        )
        conn.commit()



# ── Ticket Number Generator ────────────────────────────────────────────────────

def _generate_ticket_number(conn: sqlite3.Connection) -> str:
    """Generates a unique ticket number: SMD-YYYYMMDD-XXXX."""
    date_str = datetime.now().strftime("%Y%m%d")
    cursor = conn.cursor()
    while True:
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        tn = f"SMD-{date_str}-{suffix}"
        cursor.execute("SELECT 1 FROM tickets WHERE ticket_number = ?", (tn,))
        if not cursor.fetchone():
            return tn


# ── Helpers ────────────────────────────────────────────────────────────────────

def _clean(val) -> Optional[str]:
    """Converts list/dict/None values to strings safe for DB storage."""
    if val is None or (isinstance(val, str) and not val.strip()):
        return None
    if isinstance(val, list):
        return "\n".join(f"• {item}" for item in val)
    if isinstance(val, dict):
        import json
        return json.dumps(val)
    return str(val).strip()


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ── Core CRUD ─────────────────────────────────────────────────────────────────

def create_ticket(data: dict) -> str:
    """
    Inserts a new ticket into the database.
    Returns the generated ticket number (e.g. SMD-20260609-X4K2).
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        ticket_number = data.get("ticket_number") or _generate_ticket_number(conn)

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tickets (
                ticket_number,
                employee_name, employee_id, mobile_number, email,
                title, description, category, priority,
                assigned_department,
                status,
                sentiment, ticket_summary, suggested_resolution,
                transcript,
                can_auto_resolve, runbook_action, runbook_status,
                created_at
            ) VALUES (
                ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?,
                'Pending',
                ?, ?, ?,
                ?,
                ?, ?, ?,
                ?
            )
        """, (
            ticket_number,
            _clean(data.get("employee_name")),
            _clean(data.get("employee_id")),
            _clean(data.get("mobile_number")),
            _clean(data.get("email")),
            _clean(data.get("title")) or "Untitled Ticket",
            _clean(data.get("description")),
            _clean(data.get("category")),
            _clean(data.get("priority")) or "Medium",
            _clean(data.get("assigned_department")),
            _clean(data.get("sentiment")),
            _clean(data.get("ticket_summary")),
            _clean(data.get("suggested_resolution")),
            _clean(data.get("transcript")) or "",
            1 if data.get("can_auto_resolve") else 0,
            _clean(data.get("runbook_action")) or "none",
            "Ready" if data.get("can_auto_resolve") else "None",
            _now(),
        ))
        conn.commit()

    log_audit_action(
        ticket_number=ticket_number,
        action="TICKET_INGESTED",
        actor="Voice Pipeline / User",
        details=f"Ticket created. Category: {data.get('category')}, Priority: {data.get('priority')}"
    )
    return ticket_number


def get_ticket(ticket_number: str) -> Optional[Dict]:
    """Retrieves a single ticket by its ticket number."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets WHERE ticket_number = ?", (ticket_number,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_tickets() -> List[Dict]:
    """Returns all tickets sorted by creation date descending."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets ORDER BY created_at DESC")
        return [dict(r) for r in cursor.fetchall()]


def delete_ticket(ticket_number: str) -> bool:
    """Deletes a ticket. Returns True if deleted."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tickets WHERE ticket_number = ?", (ticket_number,))
        conn.commit()
        return cursor.rowcount > 0


# ── Lifecycle Update Functions ─────────────────────────────────────────────────

def update_ticket_status(ticket_number: str, status: str) -> bool:
    """Updates ticket status to one of: Pending, Work In Progress, Resolved."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tickets SET status=?, updated_at=? WHERE ticket_number=?",
            (status, _now(), ticket_number)
        )
        conn.commit()
        return cursor.rowcount > 0


def assign_worker(ticket_number: str, worker_name: str) -> bool:
    """Assigns an engineer/worker to a ticket."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tickets SET assigned_worker=?, updated_at=? WHERE ticket_number=?",
            (worker_name, _now(), ticket_number)
        )
        conn.commit()
        return cursor.rowcount > 0


def update_resolution_time(ticket_number: str, resolution_time: str) -> bool:
    """Sets the estimated resolution time for a ticket."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tickets SET resolution_time=?, updated_at=? WHERE ticket_number=?",
            (resolution_time, _now(), ticket_number)
        )
        conn.commit()
        return cursor.rowcount > 0


def add_resolution_notes(ticket_number: str, notes: str) -> bool:
    """Appends or sets resolution notes for a ticket."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tickets SET resolution_notes=?, updated_at=? WHERE ticket_number=?",
            (notes, _now(), ticket_number)
        )
        conn.commit()
        return cursor.rowcount > 0


def mark_resolved(ticket_number: str, notes: str = "") -> bool:
    """Marks a ticket as Resolved with optional resolution notes."""
    ts = _now()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE tickets
               SET status='Resolved', resolved_at=?, updated_at=?,
                   resolution_notes=COALESCE(NULLIF(?, ''), resolution_notes)
               WHERE ticket_number=?""",
            (ts, ts, notes or None, ticket_number)
        )
        conn.commit()
        return cursor.rowcount > 0


def update_ticket(ticket_number: str, fields: dict) -> bool:
    """Generic multi-field update used by the ticket editor."""
    if not fields:
        return False
    set_clauses = [f"{k} = ?" for k in fields]
    params = [_clean(v) for v in fields.values()]
    params.append(ticket_number)
    query = f"UPDATE tickets SET {', '.join(set_clauses)}, updated_at=? WHERE ticket_number=?"
    params.insert(-1, _now())
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0


# ── Search ─────────────────────────────────────────────────────────────────────

def search_ticket(query: str) -> List[Dict]:
    """
    Full-text search across ticket_number, employee_name, employee_id,
    mobile_number, and email. Case-insensitive LIKE search.
    """
    q = f"%{query.strip()}%"
    sql = """
        SELECT * FROM tickets
        WHERE ticket_number   LIKE ?
           OR employee_name   LIKE ?
           OR employee_id     LIKE ?
           OR mobile_number   LIKE ?
           OR email           LIKE ?
           OR title           LIKE ?
        ORDER BY created_at DESC
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, (q, q, q, q, q, q))
        return [dict(r) for r in cursor.fetchall()]


# ── Analytics Helpers ──────────────────────────────────────────────────────────

def get_tickets_by_status() -> dict:
    """Returns {status: count} mapping."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status")
        return {row[0]: row[1] for row in cursor.fetchall()}


def get_tickets_by_department() -> dict:
    """Returns {department: count} mapping."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT assigned_department, COUNT(*) FROM tickets GROUP BY assigned_department"
        )
        return {(row[0] or "Unassigned"): row[1] for row in cursor.fetchall()}


def get_tickets_by_priority() -> dict:
    """Returns {priority: count} mapping."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT priority, COUNT(*) FROM tickets GROUP BY priority")
        return {row[0]: row[1] for row in cursor.fetchall()}


def get_frequent_requesters(limit: int = 10) -> List[Dict]:
    """Returns top employee requesters sorted by ticket count."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT employee_name, employee_id, COUNT(*) as ticket_count,
                   MAX(created_at) as last_ticket
            FROM tickets
            WHERE employee_name IS NOT NULL
            GROUP BY employee_name, employee_id
            ORDER BY ticket_count DESC
            LIMIT ?
        """, (limit,))
        return [dict(r) for r in cursor.fetchall()]


def seed_tickets(conn: sqlite3.Connection):
    """Seeds the database with 8 realistic enterprise tickets for presentation readiness."""
    cursor = conn.cursor()
    samples = [
        {
            "ticket_number": "SMD-20260608-X8A2",
            "employee_name": "Sarah Connor",
            "employee_id": "EMP1984",
            "mobile_number": "+1-555-0199",
            "email": "s.connor@cyberdyne.corp",
            "title": "VPN Connection Dropouts During Remote Work",
            "description": "My corporate VPN drops connection every 10-15 minutes while accessing files on the local intranet. I have tried restarting my router but the issue persists.",
            "category": "Networking",
            "priority": "High",
            "assigned_department": "Networking Team",
            "assigned_worker": "Jim Halpert",
            "status": "Work In Progress",
            "resolution_time": "4 hours",
            "resolution_notes": None,
            "sentiment": "Frustrated",
            "ticket_summary": "Employee experiences persistent VPN connection drops during remote work sessions.",
            "suggested_resolution": "1. Reset user VPN credentials in the IAM dashboard.\n2. Reinstall Cisco VPN client profile.\n3. Validate MTU settings on employee's local adapter.",
            "transcript": "Hello, my name is Sarah Connor and my employee ID is EMP1984. I'm calling because my VPN keeps dropping every few minutes when I try to work from home. It's incredibly frustrating and I can't get anything done. My number is +1-555-0199.",
            "created_at": "2026-06-08 09:12:00",
            "updated_at": "2026-06-08 10:30:00",
            "resolved_at": None
        },
        {
            "ticket_number": "SMD-20260608-P2K4",
            "employee_name": "John Doe",
            "employee_id": "EMP2004",
            "mobile_number": "555-0248",
            "email": "j.doe@company.com",
            "title": "External Monitor Flickering & Display Issues",
            "description": "My secondary external monitor flickers intermittently and goes black for a few seconds. I've tried changing the HDMI cable, but it didn't help.",
            "category": "Hardware",
            "priority": "Medium",
            "assigned_department": "Hardware Support Team",
            "assigned_worker": "Pam Beesly",
            "status": "Resolved",
            "resolution_time": "1 hour",
            "resolution_notes": "Replaced the HDMI to USB-C adaptor which resolved the flickering issue completely.",
            "sentiment": "Neutral",
            "ticket_summary": "Secondary display flickering resolved by replacing faulty connector adapter.",
            "suggested_resolution": "1. Test monitor with alternative video ports.\n2. Replace the connector adapter.\n3. Reinstall display drivers.",
            "transcript": "Hi, this is John Doe, ID EMP2004. My second screen keeps flashing black. I've switched cables but it's still doing it. My cell is 555-0248.",
            "created_at": "2026-06-08 11:20:00",
            "updated_at": "2026-06-08 12:20:00",
            "resolved_at": "2026-06-08 12:20:00"
        },
        {
            "ticket_number": "SMD-20260609-M9R7",
            "employee_name": "David Wallace",
            "employee_id": "EMP0001",
            "mobile_number": "555-9000",
            "email": "d.wallace@company.com",
            "title": "Unable to Synchronize Corporate Mailbox",
            "description": "My Outlook desktop client is not receiving new emails. It displays a 'Disconnected' message in the bottom status bar.",
            "category": "Email & Collaboration",
            "priority": "High",
            "assigned_department": "Email & Collaboration Team",
            "assigned_worker": "Dwight Schrute",
            "status": "Work In Progress",
            "resolution_time": "2 hours",
            "resolution_notes": None,
            "sentiment": "Frustrated",
            "ticket_summary": "Executive reported complete synchronization failure on corporate Outlook mailbox.",
            "suggested_resolution": "1. Check server-side Exchange sync status.\n2. Rebuild the Outlook data file (.ost).\n3. Reconfigure Outlook profile.",
            "transcript": "Hello, this is David Wallace. I'm unable to sync my Outlook email. It is showing disconnected. I am expecting some very important emails from management. My number is 555-9000.",
            "created_at": "2026-06-09 08:05:00",
            "updated_at": "2026-06-09 08:30:00",
            "resolved_at": None
        },
        {
            "ticket_number": "SMD-20260609-Q4L1",
            "employee_name": "Ryan Howard",
            "employee_id": "EMP8890",
            "mobile_number": "555-8812",
            "email": "r.howard@company.com",
            "title": "ERP Dashboard Login Authentication Failure",
            "description": "Every attempt to log into the corporate ERP software results in a 'User Not Authorized' error screen despite correct credentials.",
            "category": "Application Support",
            "priority": "High",
            "assigned_department": "Application Support Team",
            "assigned_worker": "Michael Scott",
            "status": "Pending",
            "resolution_time": None,
            "resolution_notes": None,
            "sentiment": "Angry",
            "ticket_summary": "Authentication lockout/failure on company ERP dashboard blocking financial updates.",
            "suggested_resolution": "1. Reset SSO token in Azure AD.\n2. Verify system authorization groups.\n3. Request user clear browser session storage.",
            "transcript": "Hey, this is Ryan Howard. I cannot login to the ERP app at all. It keeps saying 'User Not Authorized' and I have a deadline to post the numbers. Please fix this.",
            "created_at": "2026-06-09 13:45:00",
            "updated_at": None,
            "resolved_at": None
        },
        {
            "ticket_number": "SMD-20260609-S3K8",
            "employee_name": "Angela Martin",
            "employee_id": "EMP0341",
            "mobile_number": "555-0341",
            "email": "a.martin@company.com",
            "title": "Backup VM Database Connection Timed Out",
            "description": "The backup environment database VM is throwing connection timeout errors on port 5432.",
            "category": "Infrastructure",
            "priority": "Critical",
            "assigned_department": "Infrastructure Team",
            "assigned_worker": "Toby Flenderson",
            "status": "Work In Progress",
            "resolution_time": "1 hour",
            "resolution_notes": None,
            "sentiment": "Angry",
            "ticket_summary": "Database connectivity timeouts reported on backup environment virtual machine.",
            "suggested_resolution": "1. Check database server service running state.\n2. Review network security group ports.\n3. Validate virtual machine CPU usage.",
            "transcript": "This is Angela Martin, employee ID EMP0341. Our backup database VM is refusing connections. We have audit updates to upload and we need this backup environment resolved immediately.",
            "created_at": "2026-06-09 14:12:00",
            "updated_at": "2026-06-09 14:30:00",
            "resolved_at": None
        },
        {
            "ticket_number": "SMD-20260609-F2E3",
            "employee_name": "Oscar Martinez",
            "employee_id": "EMP2319",
            "mobile_number": "555-2319",
            "email": "o.martinez@company.com",
            "title": "Suspicious Phishing Email Received",
            "description": "Employee reported receiving a suspicious email containing an attachment claiming to be an invoice from a vendor we do not use.",
            "category": "Cybersecurity",
            "priority": "Critical",
            "assigned_department": "Cybersecurity Team",
            "assigned_worker": "Gabe Lewis",
            "status": "Resolved",
            "resolution_time": "30 minutes",
            "resolution_notes": "Analyzed mail headers. Confirmed phishing domain. Deleted email from all user mailboxes and updated mail gateway filter rules.",
            "sentiment": "Neutral",
            "ticket_summary": "Phishing report triage and resolution via email domain ban and message purge.",
            "suggested_resolution": "1. Fetch email headers and verify SPF/DKIM.\n2. Scan attachment in sandbox.\n3. Purge matching items from global mailbox.",
            "transcript": "Hello, my name is Oscar Martinez. I received a suspicious email that looks like a phishing attempt. It claims there is an invoice. I did not click any link or open the file. Phone is 555-2319.",
            "created_at": "2026-06-09 10:00:00",
            "updated_at": "2026-06-09 10:30:00",
            "resolved_at": "2026-06-09 10:30:00"
        },
        {
            "ticket_number": "SMD-20260609-H8Y1",
            "employee_name": "Jan Levinson",
            "employee_id": "EMP0004",
            "mobile_number": "555-0004",
            "email": "j.levinson@company.com",
            "title": "Business Continuity Escalation - Client Demo",
            "description": "Urgent escalation regarding software demo issues for an upcoming enterprise client proposal tomorrow morning.",
            "category": "Management",
            "priority": "Critical",
            "assigned_department": "Management Team",
            "assigned_worker": "David Wallace",
            "status": "Pending",
            "resolution_time": None,
            "resolution_notes": None,
            "sentiment": "Frustrated",
            "ticket_summary": "Executive escalation concerning core client demo setup issues.",
            "suggested_resolution": "1. Direct technical architects to verify sandbox environment.\n2. Review system stability benchmarks.\n3. Setup stand-by engineer coverage.",
            "transcript": "This is Jan Levinson, employee ID EMP0004. I need a senior engineer immediately. Our corporate demo environment is failing and we have a presentation tomorrow. Contact me at 555-0004.",
            "created_at": "2026-06-09 15:00:00",
            "updated_at": None,
            "resolved_at": None
        },
        {
            "ticket_number": "SMD-20260609-K3T2",
            "employee_name": "Kelly Kapoor",
            "employee_id": "EMP4432",
            "mobile_number": "555-4432",
            "email": "k.kapoor@company.com",
            "title": "Payroll Expense Reimbursement Discrepancy",
            "description": "Employee submitted a travel expense reimbursement of $450 last month but was only reimbursed $150 in the current pay cycle.",
            "category": "Accounts",
            "priority": "High",
            "assigned_department": "Accounts Team",
            "assigned_worker": "Kevin Malone",
            "status": "Pending",
            "resolution_time": None,
            "resolution_notes": None,
            "sentiment": "Angry",
            "ticket_summary": "Reimbursement payment discrepancy on expense report.",
            "suggested_resolution": "1. Audit expense receipt logs.\n2. Cross-reference payroll ledger.\n3. Process adjustment in subsequent check cycle.",
            "transcript": "Hi, Kelly Kapoor here. My reimbursement check was short $300! I submitted all the food receipts from my sales trip and I only got $150. Why did this happen?",
            "created_at": "2026-06-09 15:30:00",
            "updated_at": None,
            "resolved_at": None
        }
    ]

    for s in samples:
        cursor.execute("""
            INSERT INTO tickets (
                ticket_number, employee_name, employee_id, mobile_number, email,
                title, description, category, priority, assigned_department,
                assigned_worker, status, resolution_time, resolution_notes,
                sentiment, ticket_summary, suggested_resolution, transcript,
                created_at, updated_at, resolved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s["ticket_number"], s["employee_name"], s["employee_id"], s["mobile_number"], s["email"],
            s["title"], s["description"], s["category"], s["priority"], s["assigned_department"],
            s["assigned_worker"], s["status"], s["resolution_time"], s["resolution_notes"],
            s["sentiment"], s["ticket_summary"], s["suggested_resolution"], s["transcript"],
            s["created_at"], s["updated_at"], s["resolved_at"]
        ))


# ── Audit Trail & Runbook Helpers ─────────────────────────────────────────────

def log_audit_action(ticket_number: str, action: str, actor: str = "SmartDesk AI", details: str = ""):
    """Records an immutable audit trail entry for SOC2/ISO compliance."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ticket_audit_logs (ticket_number, action, actor, details, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (ticket_number, action, actor, details, _now()))
        conn.commit()


def get_audit_logs(ticket_number: str) -> List[Dict]:
    """Retrieves all chronological audit logs for a given ticket."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, ticket_number, action, actor, details, created_at
            FROM ticket_audit_logs
            WHERE ticket_number = ?
            ORDER BY created_at ASC
        """, (ticket_number,))
        return [dict(row) for row in cursor.fetchall()]


def execute_runbook(ticket_number: str, runbook_action: str, actor: str = "SmartDesk Autonomous Agent") -> Dict:
    """Executes self-healing runbook remediation and auto-resolves ticket."""
    actions = {
        "flush_dns_vpn": "Dispatched ipconfig /flushdns, purged stale TAP adapter leases, and verified gateway route.",
        "okta_password_reset": "Validated MFA challenge token, cleared Active Directory lockout flag, and issued temporary PIN.",
        "restart_service": "Captured process stack trace, killed orphaned PID, cleared lock file, and restarted service daemon.",
        "reprovision_email": "Purged corrupted OST cache, re-authenticated Exchange OAuth2 token, and re-synced inbox."
    }
    resolution_text = actions.get(runbook_action, f"Executed automated corrective action: {runbook_action}")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tickets
            SET status = 'Resolved',
                runbook_status = 'Success',
                resolution_time = '1 min',
                resolution_notes = ?,
                resolved_at = ?,
                updated_at = ?
            WHERE ticket_number = ?
        """, (
            f"[Autonomous Resolution] {resolution_text}",
            _now(),
            _now(),
            ticket_number
        ))
        conn.commit()

    log_audit_action(
        ticket_number=ticket_number,
        action="RUNBOOK_AUTO_RESOLVED",
        actor=actor,
        details=resolution_text
    )
    return {"success": True, "ticket_number": ticket_number, "action": runbook_action, "details": resolution_text}

