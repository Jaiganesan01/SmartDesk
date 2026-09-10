import streamlit as st


# ── Priority Badges ────────────────────────────────────────────────────────────

_PRIORITY_STYLES = {
    "Critical": "background:rgba(239,68,68,0.15);color:#ef4444;border:1px solid rgba(239,68,68,0.4);",
    "High":     "background:rgba(249,115,22,0.15);color:#f97316;border:1px solid rgba(249,115,22,0.4);",
    "Medium":   "background:rgba(234,179,8,0.15);color:#eab308;border:1px solid rgba(234,179,8,0.4);",
    "Low":      "background:rgba(34,197,94,0.15);color:#22c55e;border:1px solid rgba(34,197,94,0.4);",
}

_STATUS_STYLES = {
    "Pending":          "background:rgba(107,114,128,0.15);color:#9ca3af;border:1px solid rgba(107,114,128,0.35);",
    "Work In Progress": "background:rgba(59,130,246,0.15);color:#3b82f6;border:1px solid rgba(59,130,246,0.35);",
    "Resolved":         "background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.35);",
}

_SENTIMENT_STYLES = {
    "Positive":   "background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);",
    "Neutral":    "background:rgba(107,114,128,0.15);color:#6b7280;border:1px solid rgba(107,114,128,0.3);",
    "Frustrated": "background:rgba(249,115,22,0.15);color:#f97316;border:1px solid rgba(249,115,22,0.3);",
    "Angry":      "background:rgba(239,68,68,0.15);color:#ef4444;border:1px solid rgba(239,68,68,0.3);",
}

_DEPT_ICONS = {
    "Networking Team":            "🌐",
    "Hardware Support Team":      "🖥️",
    "Email & Collaboration Team": "📧",
    "Application Support Team":   "💻",
    "Infrastructure Team":        "🏗️",
    "Cybersecurity Team":         "🔐",
    "Management Team":            "👔",
    "Accounts Team":              "💰",
}

_SENTIMENT_ICONS = {
    "Positive":   "😊",
    "Neutral":    "😐",
    "Frustrated": "😤",
    "Angry":      "😡",
}


def _badge(label: str, style: str) -> str:
    return (
        f'<span style="display:inline-block;padding:4px 14px;border-radius:50px;'
        f'font-size:13px;font-weight:600;{style}">{label}</span>'
    )


def render_priority_badge(priority: str):
    style = _PRIORITY_STYLES.get(priority, _PRIORITY_STYLES["Medium"])
    st.markdown(_badge(priority, style), unsafe_allow_html=True)


def render_status_badge(status: str):
    style = _STATUS_STYLES.get(status, _STATUS_STYLES["Pending"])
    st.markdown(_badge(status, style), unsafe_allow_html=True)


def render_sentiment_badge(sentiment: str):
    icon = _SENTIMENT_ICONS.get(sentiment, "💬")
    style = _SENTIMENT_STYLES.get(sentiment, _SENTIMENT_STYLES["Neutral"])
    st.markdown(_badge(f"{icon} {sentiment}", style), unsafe_allow_html=True)


def dept_icon(dept: str) -> str:
    return _DEPT_ICONS.get(dept, "🏢")


def format_dt(ts: str | None) -> str:
    """Formats a DB timestamp string to a human-readable format."""
    if not ts:
        return "—"
    try:
        from datetime import datetime
        dt = datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return str(ts)[:16]


def kpi_card(value: int | str, label: str, color: str = "#3b82f6") -> str:
    """Returns HTML for a KPI metric card."""
    return f"""
    <div style="background:rgba(128,128,128,0.05);border:1px solid rgba(128,128,128,0.12);
                border-radius:14px;padding:20px;text-align:center;
                box-shadow:0 4px 20px rgba(0,0,0,0.03);">
        <div style="font-size:2.4rem;font-weight:800;color:{color};">{value}</div>
        <div style="font-size:0.75rem;font-weight:700;color:#8892b0;
                    text-transform:uppercase;letter-spacing:0.08em;">{label}</div>
    </div>"""


def info_row(icon: str, label: str, value: str):
    """Renders a labelled info row with icon."""
    st.markdown(
        f'<div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:6px;">'
        f'<span style="font-size:1.1rem">{icon}</span>'
        f'<div><span style="font-size:11px;color:#8892b0;font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.06em;">{label}</span>'
        f'<br><span style="font-weight:600;">{value}</span></div></div>',
        unsafe_allow_html=True
    )
