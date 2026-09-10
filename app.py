import streamlit as st
import pandas as pd
import time
from datetime import datetime
import database
import transcription
import ticket_extractor
import config

# Set page configuration with a modern title and icon
st.set_page_config(
    page_title="SmartDesk AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on startup
database.create_database()

# Inject Custom CSS for Premium styling
# Inject Custom CSS for Premium styling
def inject_custom_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Apply fonts and force global dark theme */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Inter', sans-serif;
        }
        .stApp {
            background-color: #090d16 !important;
            color: #f8fafc !important;
        }
        
        /* Header Title Gradient */
        .title-gradient {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #3b82f6, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
            padding-bottom: 5px;
            opacity: 0;
            animation: slideInFade 0.5s ease-out forwards;
        }
        
        .subtitle-text {
            color: #94a3b8;
            font-size: 1.05rem;
            margin-top: 0;
            margin-bottom: 25px;
            opacity: 0;
            animation: slideInFade 0.5s ease-out 0.1s forwards;
        }
        
        /* Sidebar container overrides */
        [data-testid="stSidebar"] {
            background-color: #0b0f19 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Pulsing Status Light */
        .pulsing-dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px #10b981;
            animation: pulse-animation 2s infinite;
            margin-right: 8px;
        }
        @keyframes pulse-animation {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        
        /* Sidebar Headers */
        .sidebar-header {
            display: flex;
            align-items: center;
            font-size: 1.45rem;
            font-weight: 800;
            background: linear-gradient(135deg, #3b82f6, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 2px;
            opacity: 0;
            animation: slideInFade 0.4s ease-out forwards;
        }
        .sidebar-subheader {
            font-size: 0.8rem;
            color: #64748b;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            opacity: 0;
            animation: slideInFade 0.4s ease-out 0.05s forwards;
        }
        
        /* Custom Sidebar Button Styles */
        div[data-testid="stSidebar"] button[data-baseweb="button"] {
            background-color: rgba(30, 41, 59, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            color: #94a3b8 !important;
            border-radius: 8px !important;
            text-align: left !important;
            justify-content: flex-start !important;
            padding-left: 15px !important;
            height: 42px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
            opacity: 0;
            animation: slideInFade 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        div[data-testid="stSidebar"] button[data-baseweb="button"]:hover {
            border-color: rgba(59, 130, 246, 0.3) !important;
            background-color: rgba(59, 130, 246, 0.08) !important;
            color: #f8fafc !important;
            transform: translateX(2px);
        }
        
        /* Active Sidebar Button style */
        div[data-testid="stSidebar"] button[data-baseweb="button"][type="primary"] {
            background: linear-gradient(135deg, #3b82f6, #10b981) !important;
            border: none !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2) !important;
        }
        
        /* Glassmorphism Card containers */
        .glass-card {
            background: rgba(15, 23, 42, 0.65) !important;
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 16px !important;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
            opacity: 0;
            transform: translateY(15px);
            animation: fadeInUp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }

        .stat-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #f8fafc;
        }

        .stat-label {
            font-size: 0.85rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Success Banner */
        @keyframes slideDown {
            0%   { opacity:0; transform:translateY(-20px) scale(0.98); }
            100% { opacity:1; transform:translateY(0) scale(1); }
        }
        .success-banner {
            animation: slideDown 0.4s ease-out both;
            background: linear-gradient(135deg, #064e3b 0%, #047857 100%);
            border: 1px solid rgba(16, 185, 129, 0.4);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .sb-inner {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .sb-icon {
            font-size: 1.8rem;
        }
        .sb-title {
            font-size: 0.75rem;
            font-weight: 800;
            color: #a7f3d0;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }
        .sb-main {
            font-size: 1.2rem;
            font-weight: 800;
            color: #ffffff;
        }
        
        /* Hide Default Sidebar Navigation */
        div[data-testid="stSidebarNav"] {display: none;}
        
        /* Premium KPI Cards */
        .kpi-container {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .kpi-card {
            background: rgba(15, 23, 42, 0.45);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 16px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            flex: 1 1 210px;
            opacity: 0;
            transform: translateY(15px);
            animation: fadeInUp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }
        
        .kpi-card:hover {
            transform: translateY(-2px);
        }
        
        .kpi-icon-wrapper {
            width: 44px;
            height: 44px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.35rem;
        }
        
        .kpi-card.total { border-left: 3px solid #3b82f6; }
        .kpi-card.total:hover { border-color: rgba(59, 130, 246, 0.8); box-shadow: 0 0 15px rgba(59, 130, 246, 0.25); }
        .kpi-card.total .kpi-icon-wrapper { background: rgba(59, 130, 246, 0.15); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.25); }
        
        .kpi-card.pending { border-left: 3px solid #f97316; }
        .kpi-card.pending:hover { border-color: rgba(249, 115, 22, 0.8); box-shadow: 0 0 15px rgba(249, 115, 22, 0.25); }
        .kpi-card.pending .kpi-icon-wrapper { background: rgba(249, 115, 22, 0.15); color: #f97316; border: 1px solid rgba(249, 115, 22, 0.25); }
        
        .kpi-card.wip { border-left: 3px solid #a855f7; }
        .kpi-card.wip:hover { border-color: rgba(168, 85, 247, 0.8); box-shadow: 0 0 15px rgba(168, 85, 247, 0.25); }
        .kpi-card.wip .kpi-icon-wrapper { background: rgba(168, 85, 247, 0.15); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.25); }
        
        .kpi-card.resolved { border-left: 3px solid #10b981; }
        .kpi-card.resolved:hover { border-color: rgba(16, 185, 129, 0.8); box-shadow: 0 0 15px rgba(16, 185, 129, 0.25); }
        .kpi-card.resolved .kpi-icon-wrapper { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.25); }
        
        .kpi-info {
            display: flex;
            flex-direction: column;
        }
        
        .kpi-num {
            font-size: 1.7rem;
            font-weight: 800;
            color: #ffffff;
            line-height: 1.15;
        }
        
        .kpi-lbl {
            font-size: 0.75rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 700;
            margin-top: 1px;
        }
        
        /* Recent Ticket Rows */
        .ticket-row {
            background: rgba(15, 23, 42, 0.45);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 14px 20px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            opacity: 0;
            transform: translateY(10px);
            animation: fadeInUp 0.4s ease-out forwards;
        }
        
        .ticket-row:hover {
            transform: translateY(-2px);
            background: rgba(30, 41, 59, 0.45);
            border-color: rgba(59, 130, 246, 0.25);
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);
        }
        
        /* Left border priority accents */
        .ticket-row.prio-critical { border-left: 4px solid #ef4444; }
        .ticket-row.prio-high { border-left: 4px solid #f97316; }
        .ticket-row.prio-medium { border-left: 4px solid #eab308; }
        .ticket-row.prio-low { border-left: 4px solid #10b981; }
        
        .ticket-left {
            display: flex;
            align-items: center;
            gap: 15px;
            flex-grow: 1;
        }
        
        .ticket-id {
            font-family: monospace;
            font-weight: 700;
            color: #94a3b8;
            font-size: 0.8rem;
            background: rgba(0,0,0,0.3);
            padding: 4px 10px;
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .ticket-main-title {
            font-weight: 600;
            color: #f1f5f9;
            font-size: 0.95rem;
        }
        
        .ticket-right {
            display: flex;
            align-items: center;
            gap: 12px;
            width: 320px;
            justify-content: flex-end;
        }

        /* Ingestion Pipeline Stepper */
        .pipeline-container {
            padding: 10px 5px;
        }
        .pipeline-step {
            display: flex;
            align-items: flex-start;
            gap: 15px;
            margin-bottom: 22px;
            position: relative;
        }
        .pipeline-step:not(:last-child)::after {
            content: '';
            position: absolute;
            left: 17px;
            top: 36px;
            bottom: -24px;
            width: 2px;
            background: rgba(255, 255, 255, 0.08);
        }
        .pipeline-step.completed:not(:last-child)::after {
            background: #10b981;
            box-shadow: 0 0 8px #10b981;
        }
        .pipeline-badge {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 700;
            z-index: 10;
            transition: all 0.3s ease;
        }
        .pipeline-step.pending .pipeline-badge {
            background: #1e293b;
            border: 2px solid #475569;
            color: #64748b;
        }
        .pipeline-step.active .pipeline-badge {
            background: rgba(59, 130, 246, 0.2);
            border: 2px solid #3b82f6;
            color: #3b82f6;
            box-shadow: 0 0 12px rgba(59, 130, 246, 0.6);
            animation: pipeline-pulse 1.5s infinite alternate;
        }
        .pipeline-step.completed .pipeline-badge {
            background: rgba(16, 185, 129, 0.2);
            border: 2px solid #10b981;
            color: #10b981;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
        }
        .pipeline-content {
            flex-grow: 1;
        }
        .pipeline-title {
            font-size: 0.95rem;
            font-weight: 600;
            color: #64748b;
            margin: 0;
        }
        .pipeline-step.pending .pipeline-title {
            color: #64748b;
        }
        .pipeline-step.active .pipeline-title {
            color: #3b82f6;
        }
        .pipeline-step.completed .pipeline-title {
            color: #10b981;
        }
        .pipeline-desc {
            font-size: 0.8rem;
            color: #475569;
            margin: 2px 0 0 0;
        }
        .pipeline-step.active .pipeline-desc {
            color: #cbd5e1;
        }
        .pipeline-step.completed .pipeline-desc {
            color: #94a3b8;
        }
        @keyframes pipeline-pulse {
            0% { transform: scale(1); box-shadow: 0 0 4px rgba(59, 130, 246, 0.4); }
            100% { transform: scale(1.05); box-shadow: 0 0 15px rgba(59, 130, 246, 0.8); }
        }

        /* Demo launch buttons styling */
        .demo-btn-container {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            margin-bottom: 5px;
        }
        
        /* Subsections in uploader page */
        .section-header-styled {
            font-size: 1.1rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-top: 15px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 6px;
        }

        /* Database Page Stat Cards */
        .db-stat-card {
            background: rgba(15, 23, 42, 0.45);
            backdrop-filter: blur(12px);
            border-radius: 10px;
            padding: 10px 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            opacity: 0;
            transform: translateY(10px);
            animation: fadeInUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }
        .db-stat-card:hover {
            transform: translateY(-2px);
        }
        .db-stat-card.shown { border: 1px solid rgba(59, 130, 246, 0.25); background: rgba(59, 130, 246, 0.06); }
        .db-stat-card.pending { border: 1px solid rgba(249, 115, 22, 0.25); background: rgba(249, 115, 22, 0.06); }
        .db-stat-card.wip { border: 1px solid rgba(168, 85, 247, 0.25); background: rgba(168, 85, 247, 0.06); }
        .db-stat-card.resolved { border: 1px solid rgba(16, 185, 129, 0.25); background: rgba(16, 185, 129, 0.06); }

        /* ── ANIMATED QUICK DASHBOARD STYLES ──────────────────────────────────── */
        .quick-db-container {
            background: rgba(15, 23, 42, 0.55);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 16px;
            margin-top: 15px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
            font-size: 13px;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            opacity: 0;
            animation: slideInFade 0.4s ease-out 0.3s forwards;
        }
        .quick-db-container:hover {
            border-color: rgba(59, 130, 246, 0.25);
            box-shadow: 0 8px 30px rgba(59, 130, 246, 0.12);
        }
        
        .quick-db-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 8px;
        }
        .quick-db-icon {
            font-size: 1.1rem;
        }
        .quick-db-title {
            font-weight: 700;
            color: #94a3b8;
            letter-spacing: 0.05em;
            font-size: 0.75rem;
            text-transform: uppercase;
        }
        
        .quick-db-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            padding: 4px 0;
            opacity: 0;
            transform: translateX(-15px);
            animation: slideInFade 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }
        
        .quick-db-row-lbl {
            color: #cbd5e1;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .quick-db-row-val {
            font-weight: 700;
            color: #f8fafc;
        }
        .total-val {
            color: #3b82f6;
            text-shadow: 0 0 8px rgba(59, 130, 246, 0.3);
        }
        
        .quick-db-progress-wrapper {
            margin: 12px 0 14px 0;
            opacity: 0;
            transform: scaleY(0.5);
            animation: scaleInY 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) 0.15s forwards;
        }
        .quick-db-progress-bar {
            height: 6px;
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
            display: flex;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.03);
        }
        
        .progress-segment {
            height: 100%;
            transform-origin: left;
            animation: growBar 1s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }
        .progress-segment.pending {
            background: linear-gradient(90deg, #f97316, #fdba74);
            box-shadow: 0 0 8px rgba(249, 115, 22, 0.45);
        }
        .progress-segment.wip {
            background: linear-gradient(90deg, #a855f7, #c084fc);
            box-shadow: 0 0 8px rgba(168, 85, 247, 0.45);
        }
        .progress-segment.resolved {
            background: linear-gradient(90deg, #10b981, #34d399);
            box-shadow: 0 0 8px rgba(16, 185, 129, 0.45);
        }
        
        .dot-indicator {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            display: inline-block;
        }
        .dot-indicator.pending {
            background-color: #f97316;
            box-shadow: 0 0 6px #f97316;
        }
        .dot-indicator.wip {
            background-color: #a855f7;
            box-shadow: 0 0 6px #a855f7;
        }
        .dot-indicator.resolved {
            background-color: #10b981;
            box-shadow: 0 0 6px #10b981;
        }
        
        /* Entrance animation timing delays */
        .anim-delay-1 { animation-delay: 0.1s; }
        .anim-delay-2 { animation-delay: 0.2s; }
        .anim-delay-3 { animation-delay: 0.3s; }
        .anim-delay-4 { animation-delay: 0.4s; }
        .anim-delay-5 { animation-delay: 0.5s; }
        
        /* Keyframe Animations */
        @keyframes slideInFade {
            0% { opacity: 0; transform: translateX(-15px); }
            100% { opacity: 1; transform: translateX(0); }
        }
        @keyframes fadeInUp {
            0% { opacity: 0; transform: translateY(15px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes scaleInY {
            0% { opacity: 0; transform: scaleY(0); }
            100% { opacity: 1; transform: scaleY(1); }
        }
        @keyframes growBar {
            0% { transform: scaleX(0); }
            100% { transform: scaleX(1); }
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_styles()

# Helper badge rendering functions
def render_badge(text: str, color_scheme: str):
    schemes = {
        "red": "background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3);",
        "orange": "background: rgba(249, 115, 22, 0.15); color: #f97316; border: 1px solid rgba(249, 115, 22, 0.3);",
        "yellow": "background: rgba(234, 179, 8, 0.15); color: #eab308; border: 1px solid rgba(234, 179, 8, 0.3);",
        "green": "background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3);",
        "blue": "background: rgba(59, 130, 246, 0.15); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.3);",
        "purple": "background: rgba(168, 85, 247, 0.15); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.3);",
        "gray": "background: rgba(107, 114, 128, 0.15); color: #9ca3af; border: 1px solid rgba(107, 114, 128, 0.3);"
    }
    style = schemes.get(color_scheme, schemes["gray"])
    return f'<span style="display: inline-block; padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: 600; {style}">{text}</span>'

def st_badge(text: str, color_scheme: str):
    st.markdown(render_badge(text, color_scheme), unsafe_allow_html=True)

def priority_color(prio: str) -> str:
    return {"Critical": "red", "High": "orange", "Medium": "yellow", "Low": "green"}.get(prio, "gray")

def status_color(status: str) -> str:
    return {"Pending": "orange", "Work In Progress": "blue", "Resolved": "green"}.get(status, "gray")

def sentiment_color(sent: str) -> str:
    return {"Positive": "green", "Neutral": "gray", "Frustrated": "orange", "Angry": "red"}.get(sent, "gray")

# Initialize Session State Router
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"
if "last_created_ticket" not in st.session_state:
    st.session_state.last_created_ticket = None

# Query database metrics for quick dashboard
tickets_sidebar = database.get_all_tickets()
total_sidebar = len(tickets_sidebar)
status_counts_sidebar = database.get_tickets_by_status()

pending_count = status_counts_sidebar.get("Pending", 0)
wip_count = status_counts_sidebar.get("Work In Progress", 0)
resolved_count = status_counts_sidebar.get("Resolved", 0)

pending_pct = (pending_count / total_sidebar * 100) if total_sidebar > 0 else 0
wip_pct = (wip_count / total_sidebar * 100) if total_sidebar > 0 else 0
resolved_pct = (resolved_count / total_sidebar * 100) if total_sidebar > 0 else 0

# Sidebar Custom Navigation
with st.sidebar:
    st.markdown('<div class="sidebar-header"><span class="pulsing-dot"></span>SmartDesk AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subheader">Enterprise ITSM Console</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("#### Navigation")
    
    if st.button("🏠 Home", use_container_width=True, type="primary" if st.session_state.current_page == "Home" else "secondary"):
        st.session_state.current_page = "Home"
        st.rerun()
        
    if st.button("🎫 Ticket Generator", use_container_width=True, type="primary" if st.session_state.current_page == "Ticket Generator" else "secondary"):
        st.session_state.current_page = "Ticket Generator"
        st.rerun()
        
    if st.button("🗄️ Database", use_container_width=True, type="primary" if st.session_state.current_page == "Database" else "secondary"):
        st.session_state.current_page = "Database"
        st.rerun()

    # Quick Dashboard Section at the bottom
    st.markdown("---")
    st.markdown(f"""<div class="quick-db-container">
<div class="quick-db-header">
<span class="quick-db-icon">📊</span>
<span class="quick-db-title">Quick Dashboard</span>
</div>
<div class="quick-db-row anim-delay-1">
<span class="quick-db-row-lbl">Total Volume</span>
<span class="quick-db-row-val total-val">{total_sidebar}</span>
</div>
<div class="quick-db-progress-wrapper">
<div class="quick-db-progress-bar">
<div class="progress-segment pending" style="width: {pending_pct}%;"></div>
<div class="progress-segment wip" style="width: {wip_pct}%;"></div>
<div class="progress-segment resolved" style="width: {resolved_pct}%;"></div>
</div>
</div>
<div class="quick-db-row anim-delay-2">
<span class="quick-db-row-lbl"><span class="dot-indicator pending"></span>Pending</span>
<span class="quick-db-row-val">{pending_count}</span>
</div>
<div class="quick-db-row anim-delay-3">
<span class="quick-db-row-lbl"><span class="dot-indicator wip"></span>In Progress</span>
<span class="quick-db-row-val">{wip_count}</span>
</div>
<div class="quick-db-row anim-delay-4">
<span class="quick-db-row-lbl"><span class="dot-indicator resolved"></span>Resolved</span>
<span class="quick-db-row-val">{resolved_count}</span>
</div>
</div>""", unsafe_allow_html=True)


# ── PAGE 1: HOME PAGE ──────────────────────────────────────────────────────────
if st.session_state.current_page == "Home":
    st.markdown('<div class="title-gradient">SmartDesk AI Dashboard</div>', unsafe_allow_html=True)
    
    # Premium Diagnostics Hero Card
    st.markdown("""
        <div class="glass-card" style="margin-bottom: 25px; padding: 18px 24px; border-left: 4px solid #3b82f6;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                <div>
                    <h4 style="margin: 0; color: #f1f5f9; font-size: 1.15rem; font-weight: 700;">Intelligent ITSM Control Center</h4>
                    <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.85rem;">Autonomous voice ingestion and cognitive routing engine. Analyzing employee call records in real-time.</p>
                </div>
                <div style="display: flex; align-items: center; gap: 15px; background: rgba(0,0,0,0.2); padding: 8px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.03);">
                    <span class="pulsing-dot"></span>
                    <span style="font-size: 0.85rem; font-weight: 600; color: #10b981; letter-spacing: 0.05em; text-transform: uppercase;">System Operational</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    tickets = database.get_all_tickets()
    total = len(tickets)
    status_counts = database.get_tickets_by_status()
    
    # Render interactive premium KPI cards with secondary detail labels
    st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-card total anim-delay-1">
                <div class="kpi-icon-wrapper">📁</div>
                <div class="kpi-info">
                    <span class="kpi-num">{total}</span>
                    <span class="kpi-lbl">Total Volume</span>
                    <span style="font-size: 0.65rem; color: #64748b; font-weight: 500; margin-top: 2px;">Ingested calls list</span>
                </div>
            </div>
            <div class="kpi-card pending anim-delay-2">
                <div class="kpi-icon-wrapper">🕒</div>
                <div class="kpi-info">
                    <span class="kpi-num">{status_counts.get("Pending", 0)}</span>
                    <span class="kpi-lbl">Pending Queue</span>
                    <span style="font-size: 0.65rem; color: #64748b; font-weight: 500; margin-top: 2px;">Waiting triage</span>
                </div>
            </div>
            <div class="kpi-card wip anim-delay-3">
                <div class="kpi-icon-wrapper">⚙️</div>
                <div class="kpi-info">
                    <span class="kpi-num">{status_counts.get("Work In Progress", 0)}</span>
                    <span class="kpi-lbl">In Progress</span>
                    <span style="font-size: 0.65rem; color: #64748b; font-weight: 500; margin-top: 2px;">Under engineering review</span>
                </div>
            </div>
            <div class="kpi-card resolved anim-delay-4">
                <div class="kpi-icon-wrapper">✅</div>
                <div class="kpi-info">
                    <span class="kpi-num">{status_counts.get("Resolved", 0)}</span>
                    <span class="kpi-lbl">Resolved Tickets</span>
                    <span style="font-size: 0.65rem; color: #64748b; font-weight: 500; margin-top: 2px;">100% Ingestion SLA</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
        
    # Recent Tickets Feed
    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    st.subheader("📋 Recent Activity Queue")
    
    if not tickets:
        st.info("No tickets found in the database. Head to 'Ticket Generator' to upload call audio files.")
    else:
        for idx, t in enumerate(tickets[:5]):
            prio = t.get("priority", "Medium")
            prio_color_val = priority_color(prio)
            prio_html = render_badge(prio, prio_color_val)
            stat_html = render_badge(t.get("status", "Pending"), status_color(t.get("status", "Pending")))
            
            # Format datetime nicely
            date_str = t.get("created_at") or ""
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                formatted_date = dt.strftime("%b %d, %H:%M")
            except:
                formatted_date = date_str
            
            category_icon = {
                "Networking": "🌐",
                "Hardware": "💻",
                "Email & Collaboration": "📧",
                "Application Support": "⚙️",
                "Infrastructure": "🗄️",
                "Cybersecurity": "🛡️",
                "Management": "👔",
                "Accounts": "💵"
            }.get(t.get("category", ""), "🎫")
            
            emp_display_name = t.get("employee_name") or "Voice Intake User"
            emp_id_display = t.get("employee_id") or "No ID"
            st.markdown(f"""
                <div class="ticket-row prio-{prio.lower()} anim-delay-{idx+1}">
                    <div class="ticket-left">
                        <span class="ticket-id">{t.get("ticket_number")}</span>
                        <div style="font-size: 1.15rem; margin-right: 5px;">{category_icon}</div>
                        <div>
                            <span class="ticket-main-title">{t.get("title")}</span>
                            <div style="font-size: 0.78rem; color: #64748b; margin-top: 3px;">
                                👤 <strong style="color: #cbd5e1;">{emp_display_name}</strong> ({emp_id_display}) • 🏢 <span style="color: #94a3b8;">{t.get("assigned_department")}</span>
                            </div>
                        </div>
                    </div>
                    <div class="ticket-right">
                        {prio_html}
                        {stat_html}
                        <span style="font-size: 0.8rem; color: #64748b; width: 80px; text-align: right; font-weight: 500;">{formatted_date}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Injected Analytics Charts at the bottom of the Home page
        st.markdown("---")
        st.subheader("📊 Workload Metrics")
        
        priority_counts = database.get_tickets_by_priority()
        dept_counts = database.get_tickets_by_department()
        
        col_chart_1, col_chart_2 = st.columns(2)
        with col_chart_1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.write("**Workload distribution by Department**")
            if dept_counts:
                df_dept = pd.DataFrame(list(dept_counts.items()), columns=["Department", "Ticket Volume"])
                st.bar_chart(df_dept.set_index("Department"))
            else:
                st.write("No department data available.")
            st.markdown('</div>', unsafe_allow_html=True)
                
        with col_chart_2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.write("**Workload distribution by Priority**")
            if priority_counts:
                df_prio = pd.DataFrame(list(priority_counts.items()), columns=["Priority", "Ticket Volume"])
                st.bar_chart(df_prio.set_index("Priority"))
            else:
                st.write("No priority data available.")
            st.markdown('</div>', unsafe_allow_html=True)


# ── PAGE 2: TICKET GENERATOR PAGE ──────────────────────────────────────────────
elif st.session_state.current_page == "Ticket Generator":
    st.markdown('<div class="title-gradient">Voice-to-Ticket Ingestion Console</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">Upload a support call recording — AI transcribes, classifies, and creates a ticket autonomously.</div>', unsafe_allow_html=True)

    def render_pipeline_stepper(step: int) -> str:
        """Renders a visual stepper representing the ingestion pipeline steps."""
        steps_info = [
            ("🎙️", "Voice Ingestion", "Parsing WAV/MP3 audio file", 1),
            ("📝", "Speech-to-Text", "Transcribing audio via Whisper", 2),
            ("🧠", "AI Analysis", "Extracting info via LLaMA-3", 3),
            ("🗄️", "DB Ingestion", "Seeding ticket in SQLite", 4),
            ("✅", "Complete", "Ticket created & alerts dispatched", 5),
        ]
        html = '<div class="pipeline-container">'
        for icon, label, desc, s_num in steps_info:
            if step > s_num or step == 5:
                state_class = "completed"
                badge = "✓"
            elif step == s_num:
                state_class = "active"
                badge = icon
            else:
                state_class = "pending"
                badge = str(s_num)
            html += f'<div class="pipeline-step {state_class}">'
            html += f'<div class="pipeline-badge">{badge}</div>'
            html += '<div class="pipeline-content">'
            html += f'<div class="pipeline-title">{label}</div>'
            html += f'<div class="pipeline-desc">{desc}</div>'
            html += '</div></div>'
        html += '</div>'
        return html

    # ── File & State Resolution ────────────────────────────────────────────────
    if "active_test_file" not in st.session_state:
        st.session_state.active_test_file = None

    # Hidden file uploader (rendered via custom HTML zone below)
    uploaded_file = st.file_uploader(
        "Upload audio", type=["wav", "mp3"],
        label_visibility="collapsed",
        key="tg_uploader"
    )
    if uploaded_file:
        st.session_state.active_test_file = None

    file_name = None
    file_bytes = None

    if uploaded_file:
        file_name = uploaded_file.name
        file_bytes = uploaded_file.read()
    elif st.session_state.get("active_test_file"):
        file_name = st.session_state.active_test_file
        try:
            with open(file_name, "rb") as f:
                file_bytes = f.read()
        except:
            file_bytes = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"

    # ── Two Column Layout ──────────────────────────────────────────────────────
    col_left, col_right = st.columns([11, 9])

    # ── LEFT COLUMN ────────────────────────────────────────────────────────────
    with col_left:

        # ── Upload Zone ────────────────────────────────────────────────────────
        if file_bytes and file_name:
            st.markdown(f"""
            <div style="background: rgba(16,185,129,0.06); border: 1.5px solid rgba(16,185,129,0.35); border-radius: 14px; padding: 18px 22px; margin-bottom: 14px;">
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
                    <div style="width:40px; height:40px; border-radius:10px; background:rgba(16,185,129,0.15); display:flex; align-items:center; justify-content:center; font-size:1.2rem; border:1px solid rgba(16,185,129,0.3);">🎵</div>
                    <div>
                        <div style="font-size:0.75rem; color:#10b981; text-transform:uppercase; letter-spacing:0.08em; font-weight:700;">File Loaded — Ready to Process</div>
                        <div style="font-size:1rem; font-weight:700; color:#f1f5f9; margin-top:2px;">{file_name}</div>
                    </div>
                    <div style="margin-left:auto; background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.25); border-radius:20px; padding:4px 12px; font-size:0.72rem; color:#10b981; font-weight:700;">● READY</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.audio(file_bytes)
            if st.button("🗑️  Clear File & Reset", use_container_width=True):
                for k in list(st.session_state.keys()):
                    if k.startswith("proc_"):
                        del st.session_state[k]
                st.session_state.active_test_file = None
                st.session_state.last_created_ticket = None
                st.rerun()
        else:
            st.markdown("""
            <div style="border: 2px dashed rgba(59,130,246,0.3); border-radius: 14px; padding: 32px 20px; text-align:center; background: rgba(59,130,246,0.04); margin-bottom:14px;">
                <div style="font-size:2.2rem; margin-bottom:10px;">🎙️</div>
                <div style="font-size:1rem; font-weight:700; color:#f1f5f9; margin-bottom:6px;">Drop your support call recording here</div>
                <div style="font-size:0.8rem; color:#64748b;">WAV or MP3 &nbsp;•&nbsp; Max 25 MB</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

        # ── Demo Launchers ─────────────────────────────────────────────────────
        st.markdown("""
        <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.1em; color:#64748b; font-weight:700; margin-bottom:8px;">⚡ Quick Demo Scenarios</div>
        """, unsafe_allow_html=True)
        dc1, dc2 = st.columns(2)
        with dc1:
            if st.button("🔌  VPN Issue Demo", use_container_width=True):
                st.session_state.active_test_file = "test_vpn.wav"
                st.session_state.last_created_ticket = None
                for k in list(st.session_state.keys()):
                    if "test_vpn" in k: del st.session_state[k]
                st.rerun()
        with dc2:
            if st.button("🖥️  Hardware Issue Demo", use_container_width=True):
                st.session_state.active_test_file = "test_laptop.wav"
                st.session_state.last_created_ticket = None
                for k in list(st.session_state.keys()):
                    if "test_laptop" in k: del st.session_state[k]
                st.rerun()

        st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

        # ── Routing Matrix ─────────────────────────────────────────────────────
        st.markdown("""
        <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 18px 20px;">
            <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.1em; color:#64748b; font-weight:700; margin-bottom:14px;">🗂️ Autonomous Routing Matrix</div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                <div style="background:rgba(59,130,246,0.07); border:1px solid rgba(59,130,246,0.15); border-radius:10px; padding:10px 12px;">
                    <div style="font-size:0.85rem; font-weight:700; color:#93c5fd;">🌐 Networking</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:3px;">VPN, Wi-Fi, DNS failures</div>
                </div>
                <div style="background:rgba(168,85,247,0.07); border:1px solid rgba(168,85,247,0.15); border-radius:10px; padding:10px 12px;">
                    <div style="font-size:0.85rem; font-weight:700; color:#c4b5fd;">💻 Hardware</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:3px;">Laptop, monitor, printer</div>
                </div>
                <div style="background:rgba(16,185,129,0.07); border:1px solid rgba(16,185,129,0.15); border-radius:10px; padding:10px 12px;">
                    <div style="font-size:0.85rem; font-weight:700; color:#6ee7b7;">📧 Email &amp; Collab</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:3px;">Outlook, Teams, sync</div>
                </div>
                <div style="background:rgba(249,115,22,0.07); border:1px solid rgba(249,115,22,0.15); border-radius:10px; padding:10px 12px;">
                    <div style="font-size:0.85rem; font-weight:700; color:#fdba74;">⚙️ Application</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:3px;">ERP, CRM, login errors</div>
                </div>
                <div style="background:rgba(239,68,68,0.07); border:1px solid rgba(239,68,68,0.15); border-radius:10px; padding:10px 12px;">
                    <div style="font-size:0.85rem; font-weight:700; color:#fca5a5;">🗄️ Infrastructure</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:3px;">Server, VM, DB timeouts</div>
                </div>
                <div style="background:rgba(234,179,8,0.07); border:1px solid rgba(234,179,8,0.15); border-radius:10px; padding:10px 12px;">
                    <div style="font-size:0.85rem; font-weight:700; color:#fde047;">🛡️ Cybersecurity</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:3px;">Phishing, malware, breach</div>
                </div>
                <div style="background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.15); border-radius:10px; padding:10px 12px;">
                    <div style="font-size:0.85rem; font-weight:700; color:#a5b4fc;">👔 Management</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:3px;">Executive escalations</div>
                </div>
                <div style="background:rgba(20,184,166,0.07); border:1px solid rgba(20,184,166,0.15); border-radius:10px; padding:10px 12px;">
                    <div style="font-size:0.85rem; font-weight:700; color:#5eead4;">💵 Accounts</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:3px;">Payroll, reimbursements</div>
                </div>
            </div>
            <div style="margin-top:12px; font-size:0.72rem; color:#475569; text-align:center;">Powered by Groq LLaMA-3 · Whisper STT · SQLite</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Run Ingestion Pipeline ─────────────────────────────────────────────
        if file_bytes and file_name:
            file_key = f"proc_{file_name}_{len(file_bytes)}"
            if file_key not in st.session_state:
                try:
                    with col_right:
                        pipe_ph = st.empty()
                        pipe_ph.markdown(f'<div class="glass-card"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:#3b82f6;font-weight:700;margin-bottom:14px;">⚙️ PIPELINE RUNNING</div>{render_pipeline_stepper(1)}</div>', unsafe_allow_html=True)
                    time.sleep(0.8)
                    with col_right:
                        pipe_ph.markdown(f'<div class="glass-card"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:#3b82f6;font-weight:700;margin-bottom:14px;">⚙️ PIPELINE RUNNING</div>{render_pipeline_stepper(2)}</div>', unsafe_allow_html=True)
                    transcript = transcription.transcribe_audio(file_bytes, file_name)
                    with col_right:
                        pipe_ph.markdown(f'<div class="glass-card"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:#3b82f6;font-weight:700;margin-bottom:14px;">⚙️ PIPELINE RUNNING</div>{render_pipeline_stepper(3)}</div>', unsafe_allow_html=True)
                    extracted = ticket_extractor.extract_ticket_info(transcript)
                    with col_right:
                        pipe_ph.markdown(f'<div class="glass-card"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:#3b82f6;font-weight:700;margin-bottom:14px;">⚙️ PIPELINE RUNNING</div>{render_pipeline_stepper(4)}</div>', unsafe_allow_html=True)
                    db_data = {
                        "employee_name": extracted.get("employee_name") or "Voice Intake User",
                        "employee_id": extracted.get("employee_id"),
                        "mobile_number": extracted.get("mobile_number"),
                        "email": extracted.get("email"),
                        "title": extracted.get("title", "Voice Intake Support Ticket"),
                        "description": extracted.get("description", transcript),
                        "category": extracted.get("category", "Application Support"),
                        "priority": extracted.get("priority", "Medium"),
                        "assigned_department": extracted.get("assigned_department", "Application Support Team"),
                        "sentiment": extracted.get("sentiment", "Neutral"),
                        "ticket_summary": extracted.get("ticket_summary", ""),
                        "suggested_resolution": extracted.get("suggested_resolution", ""),
                        "transcript": transcript
                    }
                    ticket_num = database.create_ticket(db_data)
                    with col_right:
                        pipe_ph.markdown(f'<div class="glass-card"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:#10b981;font-weight:700;margin-bottom:14px;">✅ PIPELINE COMPLETE</div>{render_pipeline_stepper(5)}</div>', unsafe_allow_html=True)
                    time.sleep(0.8)
                    st.session_state[file_key] = ticket_num
                    st.session_state.last_created_ticket = ticket_num
                    st.rerun()
                except Exception as e:
                    with col_right:
                        st.error(f"❌ Ingestion failed: {e}")

    # ── RIGHT COLUMN ───────────────────────────────────────────────────────────
    with col_right:
        if st.session_state.get("last_created_ticket"):
            ticket = database.get_ticket(st.session_state.last_created_ticket)
            if ticket:
                prio = ticket.get("priority", "Medium")
                prio_colors = {"Critical": ("#ef4444","rgba(239,68,68,0.15)"), "High": ("#f97316","rgba(249,115,22,0.15)"), "Medium": ("#eab308","rgba(234,179,8,0.15)"), "Low": ("#10b981","rgba(16,185,129,0.15)")}
                prio_c, prio_bg = prio_colors.get(prio, ("#94a3b8","rgba(148,163,184,0.15)"))
                stat = ticket.get("status", "Pending")
                stat_colors = {"Pending": "#f97316", "Work In Progress": "#3b82f6", "Resolved": "#10b981"}
                stat_c = stat_colors.get(stat, "#94a3b8")
                sent = ticket.get("sentiment", "Neutral")
                sent_icons = {"Positive": "😊", "Neutral": "😐", "Frustrated": "😤", "Angry": "😡"}
                sent_icon = sent_icons.get(sent, "😐")
                cat_icons = {"Networking": "🌐", "Hardware": "💻", "Email & Collaboration": "📧", "Application Support": "⚙️", "Infrastructure": "🗄️", "Cybersecurity": "🛡️", "Management": "👔", "Accounts": "💵"}
                cat_icon = cat_icons.get(ticket.get("category", ""), "🎫")
                emp_name = ticket.get("employee_name") or "Voice Intake User"
                emp_id = ticket.get("employee_id") or "—"
                emp_mobile = ticket.get("mobile_number") or "—"
                emp_email = ticket.get("email") or "—"

                # Success banner
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#064e3b,#047857); border:1px solid rgba(16,185,129,0.4); border-radius:14px; padding:16px 20px; margin-bottom:14px;">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <div style="font-size:1.8rem;">🎫</div>
                        <div>
                            <div style="font-size:0.68rem; font-weight:800; color:#a7f3d0; text-transform:uppercase; letter-spacing:0.12em;">Autonomous Action Complete</div>
                            <div style="font-size:1.1rem; font-weight:800; color:#fff; margin-top:2px;">{ticket['ticket_number']}</div>
                        </div>
                        <div style="margin-left:auto; font-size:0.72rem; color:#6ee7b7; font-weight:600; background:rgba(0,0,0,0.2); padding:4px 12px; border-radius:20px;">NEW</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 4-attribute badge row
                st.markdown(f"""
                <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px;">
                    <div style="background:{prio_bg}; border:1px solid {prio_c}44; border-radius:8px; padding:8px 14px; flex:1; min-width:80px; text-align:center;">
                        <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.06em; font-weight:700;">Priority</div>
                        <div style="font-size:0.9rem; font-weight:800; color:{prio_c}; margin-top:3px;">{prio}</div>
                    </div>
                    <div style="background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.25); border-radius:8px; padding:8px 14px; flex:1; min-width:80px; text-align:center;">
                        <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.06em; font-weight:700;">Status</div>
                        <div style="font-size:0.9rem; font-weight:800; color:{stat_c}; margin-top:3px;">{stat}</div>
                    </div>
                    <div style="background:rgba(168,85,247,0.1); border:1px solid rgba(168,85,247,0.25); border-radius:8px; padding:8px 14px; flex:1; min-width:80px; text-align:center;">
                        <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.06em; font-weight:700;">Sentiment</div>
                        <div style="font-size:0.9rem; font-weight:800; color:#c4b5fd; margin-top:3px;">{sent_icon} {sent}</div>
                    </div>
                    <div style="background:rgba(59,130,246,0.06); border:1px solid rgba(59,130,246,0.15); border-radius:8px; padding:8px 14px; flex:1; min-width:80px; text-align:center;">
                        <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.06em; font-weight:700;">Category</div>
                        <div style="font-size:0.9rem; font-weight:800; color:#93c5fd; margin-top:3px;">{cat_icon} {ticket.get('category','—')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Caller info card
                st.markdown(f"""
                <div style="background:rgba(15,23,42,0.5); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:14px 18px; margin-bottom:12px;">
                    <div style="font-size:0.68rem; text-transform:uppercase; letter-spacing:0.1em; color:#64748b; font-weight:700; margin-bottom:10px;">👤 Caller Information</div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                        <div><div style="font-size:0.72rem; color:#64748b;">Name</div><div style="font-size:0.9rem; font-weight:600; color:#f1f5f9;">{emp_name}</div></div>
                        <div><div style="font-size:0.72rem; color:#64748b;">Employee ID</div><div style="font-size:0.9rem; font-weight:600; color:#f1f5f9;">{emp_id}</div></div>
                        <div><div style="font-size:0.72rem; color:#64748b;">Mobile</div><div style="font-size:0.9rem; font-weight:600; color:#f1f5f9;">{emp_mobile}</div></div>
                        <div><div style="font-size:0.72rem; color:#64748b;">Email</div><div style="font-size:0.9rem; font-weight:600; color:#f1f5f9; word-break:break-all;">{emp_email}</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Issue summary + routing card
                st.markdown(f"""
                <div style="background:rgba(15,23,42,0.5); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:14px 18px; margin-bottom:12px;">
                    <div style="font-size:0.68rem; text-transform:uppercase; letter-spacing:0.1em; color:#64748b; font-weight:700; margin-bottom:8px;">📋 Issue Summary</div>
                    <div style="font-size:1rem; font-weight:700; color:#f1f5f9; margin-bottom:8px;">{ticket.get('title','Untitled Ticket')}</div>
                    <div style="font-size:0.82rem; color:#94a3b8; line-height:1.55; margin-bottom:10px;">{ticket.get('ticket_summary','')}</div>
                    <div style="display:flex; align-items:center; gap:8px; background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.2); border-radius:8px; padding:8px 12px;">
                        <span style="font-size:0.72rem; color:#64748b; font-weight:600; text-transform:uppercase;">Routed To</span>
                        <span style="font-size:0.85rem; font-weight:700; color:#93c5fd;">{ticket.get('assigned_department','—')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Resolution checklist
                if ticket.get("suggested_resolution"):
                    res_lines = ticket.get("suggested_resolution", "").strip().split("\n")
                    res_html = "".join([
                        f'<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:8px;"><span style="color:#10b981;font-weight:800;font-size:0.9rem;flex-shrink:0;">›</span><span style="font-size:0.82rem;color:#94a3b8;line-height:1.5;">{line.lstrip("0123456789. •›").strip()}</span></div>'
                        for line in res_lines if line.strip()
                    ])
                    st.markdown(f"""
                    <div style="background:rgba(15,23,42,0.5); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:14px 18px; margin-bottom:12px;">
                        <div style="font-size:0.68rem; text-transform:uppercase; letter-spacing:0.1em; color:#64748b; font-weight:700; margin-bottom:10px;">🔧 Resolution Checklist</div>
                        {res_html}
                    </div>
                    """, unsafe_allow_html=True)

                # Autonomous Runbook Execution Box
                if ticket.get("can_auto_resolve") and ticket.get("status") != "Resolved":
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(16,185,129,0.1)); border:1px solid rgba(99,102,241,0.4); border-radius:12px; padding:14px 18px; margin-bottom:12px;">
                        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                            <span style="font-size:1.1rem;">⚡</span>
                            <span style="font-size:0.75rem; font-weight:800; color:#818cf8; text-transform:uppercase; letter-spacing:0.08em;">Self-Healing Candidate Detected</span>
                        </div>
                        <div style="font-size:0.8rem; color:#cbd5e1; margin-bottom:10px;">
                            Action: <code style="background:rgba(0,0,0,0.3); padding:2px 6px; border-radius:4px; color:#34d399;">{ticket.get('runbook_action','flush_dns_vpn')}</code>. Zero human touch required.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("⚡ Execute Self-Healing Runbook", key=f"runbook_{ticket['ticket_number']}", type="primary", use_container_width=True):
                        res = database.execute_runbook(ticket["ticket_number"], ticket.get("runbook_action", "flush_dns_vpn"))
                        st.success(f"✅ Autonomous Runbook executed: {res['details']}")
                        time.sleep(1)
                        st.rerun()

                # Transcript expander
                with st.expander("📝 View Raw Transcript"):
                    st.markdown(f'<div style="font-size:0.85rem; color:#94a3b8; line-height:1.7; background:rgba(0,0,0,0.2); padding:14px; border-radius:8px;">{ticket.get("transcript","")}</div>', unsafe_allow_html=True)

                # SOC2 Compliance Audit Trail
                with st.expander("🛡️ View SOC2 Immutable Audit Trail"):
                    audit_logs = database.get_audit_logs(ticket["ticket_number"])
                    if audit_logs:
                        for al in audit_logs:
                            st.markdown(f"""
                            <div style="font-size:0.75rem; padding:6px 10px; background:rgba(0,0,0,0.3); border-left:2px solid #3b82f6; margin-bottom:6px; border-radius:4px;">
                                <div style="display:flex; justify-content:space-between; color:#94a3b8;">
                                    <strong style="color:#60a5fa;">{al.get('action')}</strong>
                                    <span>{al.get('created_at')}</span>
                                </div>
                                <div style="color:#cbd5e1; margin-top:2px;">Actor: {al.get('actor')}</div>
                                <div style="color:#64748b; font-size:0.7rem;">{al.get('details')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No audit entries recorded yet.")

        elif not file_bytes or not file_name:
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:16px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.1em; color:#64748b; font-weight:700;">🎙️ Ingestion Diagnostics Pipeline</div>
                    <div style="font-size:0.68rem; color:#64748b; font-weight:600; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); padding:3px 10px; border-radius:20px;">STANDBY</div>
                </div>
                <div style="font-size:0.82rem; color:#64748b; margin-bottom:18px; line-height:1.5;">Upload a call recording on the left or launch a demo scenario to begin autonomous ticket creation.</div>
                {render_pipeline_stepper(0)}
            </div>
            """, unsafe_allow_html=True)


# ── PAGE 3 + 4: COMBINED DATABASE & OPERATIONS PAGE ─────────────────────────
elif st.session_state.current_page == "Transcript History" or st.session_state.current_page == "Database":
    st.session_state.current_page = "Database"

    st.markdown('<div class="title-gradient">Database & Operations Console</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">Search, filter and manage all support tickets — update status, assign engineers, and export records.</div>', unsafe_allow_html=True)

    # ── Load all tickets ────────────────────────────────────────────────────────
    all_tickets = database.get_all_tickets()

    # ── Search + Filter Controls ────────────────────────────────────────────────
    st.markdown("""
    <div style="background:rgba(15,23,42,0.5); border:1px solid rgba(255,255,255,0.06); border-radius:14px; padding:16px 20px; margin-bottom:18px;">
        <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.1em; color:#64748b; font-weight:700; margin-bottom:12px;">🔍 Search & Filter</div>
    """, unsafe_allow_html=True)

    sf1, sf2, sf3, sf4 = st.columns([3, 1, 1, 1])
    with sf1:
        search_q = st.text_input("Search", placeholder="Ticket #, employee name, title, email, phone...", label_visibility="collapsed")
    with sf2:
        filter_status = st.selectbox("Status", ["All Statuses", "Pending", "Work In Progress", "Resolved"], label_visibility="collapsed")
    with sf3:
        filter_priority = st.selectbox("Priority", ["All Priorities", "Critical", "High", "Medium", "Low"], label_visibility="collapsed")
    with sf4:
        depts = sorted(set((t.get("assigned_department") or "").strip() for t in all_tickets if t.get("assigned_department")))
        filter_dept = st.selectbox("Department", ["All Departments"] + depts, label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Apply filters ───────────────────────────────────────────────────────────
    tickets_list = database.search_ticket(search_q.strip()) if search_q.strip() else list(all_tickets)
    if filter_status != "All Statuses":
        tickets_list = [t for t in tickets_list if t.get("status") == filter_status]
    if filter_priority != "All Priorities":
        tickets_list = [t for t in tickets_list if t.get("priority") == filter_priority]
    if filter_dept != "All Departments":
        tickets_list = [t for t in tickets_list if t.get("assigned_department") == filter_dept]

    # ── Stats Bar ───────────────────────────────────────────────────────────────
    total_shown = len(tickets_list)
    pend_c = sum(1 for t in tickets_list if t.get("status") == "Pending")
    wip_c  = sum(1 for t in tickets_list if t.get("status") == "Work In Progress")
    res_c  = sum(1 for t in tickets_list if t.get("status") == "Resolved")

    st.markdown(f"""
    <div style="display:flex; gap:10px; margin-bottom:18px; flex-wrap:wrap;">
        <div class="db-stat-card shown anim-delay-1">
            <span style="font-size:1.25rem; font-weight:800; color:#93c5fd;">{total_shown}</span>
            <span style="font-size:0.72rem; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Shown</span>
        </div>
        <div class="db-stat-card pending anim-delay-2">
            <span style="font-size:1.25rem; font-weight:800; color:#f97316;">{pend_c}</span>
            <span style="font-size:0.72rem; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Pending</span>
        </div>
        <div class="db-stat-card wip anim-delay-3">
            <span style="font-size:1.25rem; font-weight:800; color:#c084fc;">{wip_c}</span>
            <span style="font-size:0.72rem; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">In Progress</span>
        </div>
        <div class="db-stat-card resolved anim-delay-4">
            <span style="font-size:1.25rem; font-weight:800; color:#10b981;">{res_c}</span>
            <span style="font-size:0.72rem; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Resolved</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Two column layout: Ticket Feed | Manager Panel ──────────────────────────
    col_feed, col_mgr = st.columns([6, 4])

    # ── LEFT: Ticket Feed ───────────────────────────────────────────────────────
    with col_feed:
        if not tickets_list:
            st.markdown("""
            <div style="background:rgba(15,23,42,0.5); border:1px solid rgba(255,255,255,0.06); border-radius:14px; padding:40px; text-align:center;">
                <div style="font-size:2rem; margin-bottom:10px;">🔎</div>
                <div style="font-size:1rem; font-weight:700; color:#f1f5f9; margin-bottom:6px;">No tickets match your filters</div>
                <div style="font-size:0.82rem; color:#64748b;">Try adjusting search or clearing filters.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            prio_border = {"Critical":"#ef4444","High":"#f97316","Medium":"#eab308","Low":"#10b981"}
            prio_badge  = {
                "Critical":"background:rgba(239,68,68,0.15);color:#ef4444;border:1px solid rgba(239,68,68,0.35);",
                "High":    "background:rgba(249,115,22,0.15);color:#f97316;border:1px solid rgba(249,115,22,0.35);",
                "Medium":  "background:rgba(234,179,8,0.15);color:#eab308;border:1px solid rgba(234,179,8,0.35);",
                "Low":     "background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.35);",
            }
            stat_badge = {
                "Pending":          "background:rgba(249,115,22,0.15);color:#f97316;border:1px solid rgba(249,115,22,0.35);",
                "Work In Progress": "background:rgba(59,130,246,0.15);color:#3b82f6;border:1px solid rgba(59,130,246,0.35);",
                "Resolved":         "background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.35);",
            }
            cat_icons = {"Networking":"🌐","Hardware":"💻","Email & Collaboration":"📧","Application Support":"⚙️","Infrastructure":"🗄️","Cybersecurity":"🛡️","Management":"👔","Accounts":"💵"}

            st.markdown(f'<div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.1em; color:#64748b; font-weight:700; margin-bottom:10px;">📋 Ticket Queue — {total_shown} records</div>', unsafe_allow_html=True)

            for idx, t in enumerate(tickets_list):
                prio = t.get("priority","Medium")
                stat = t.get("status","Pending")
                cat_icon = cat_icons.get(t.get("category",""),"🎫")
                emp  = t.get("employee_name") or "Voice Intake User"
                dept = t.get("assigned_department") or "—"
                wrkr = t.get("assigned_worker") or "Unassigned"
                tn   = t.get("ticket_number","")
                try:
                    from datetime import datetime
                    dt = datetime.strptime(t.get("created_at",""), "%Y-%m-%d %H:%M:%S")
                    date_fmt = dt.strftime("%b %d, %H:%M")
                except:
                    date_fmt = (t.get("created_at","") or "")[:10]

                bc = prio_border.get(prio,"#64748b")
                pb = prio_badge.get(prio,"background:rgba(100,116,139,0.12);color:#94a3b8;border:1px solid rgba(100,116,139,0.25);")
                sb = stat_badge.get(stat,"background:rgba(100,116,139,0.12);color:#94a3b8;border:1px solid rgba(100,116,139,0.25);")
                delay = min(0.6, idx * 0.08)

                st.markdown(f"""
                <div style="background:rgba(15,23,42,0.45); border:1px solid rgba(255,255,255,0.05); border-left:4px solid {bc}; border-radius:12px; padding:13px 16px; margin-bottom:8px; opacity:0; transform:translateY(10px); animation:fadeInUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) {delay}s forwards;">
                    <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
                        <span style="font-family:monospace; font-size:0.76rem; font-weight:700; color:#64748b; background:rgba(0,0,0,0.25); padding:3px 8px; border-radius:6px;">{tn}</span>
                        <span style="font-size:1rem;">{cat_icon}</span>
                        <span style="font-size:0.92rem; font-weight:700; color:#f1f5f9; flex:1; min-width:100px;">{t.get("title","")}</span>
                        <span style="font-size:0.7rem; font-weight:700; padding:2px 9px; border-radius:20px; {pb}">{prio}</span>
                        <span style="font-size:0.7rem; font-weight:700; padding:2px 9px; border-radius:20px; {sb}">{stat}</span>
                    </div>
                    <div style="display:flex; gap:16px; margin-top:8px; flex-wrap:wrap;">
                        <span style="font-size:0.75rem; color:#64748b;">👤 <strong style="color:#94a3b8;">{emp}</strong></span>
                        <span style="font-size:0.75rem; color:#64748b;">🏢 <span style="color:#94a3b8;">{dept}</span></span>
                        <span style="font-size:0.75rem; color:#64748b;">🔧 <span style="color:#94a3b8;">{wrkr}</span></span>
                        <span style="font-size:0.72rem; color:#475569; margin-left:auto;">{date_fmt}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"  ↳ Details · {tn}"):
                    ex1, ex2 = st.columns(2)
                    with ex1:
                        st.markdown(f"**🎫 Ticket:** `{tn}`")
                        st.markdown(f"**👤 Name:** {t.get('employee_name') or 'Voice Intake User'}")
                        st.markdown(f"**🪪 Emp ID:** {t.get('employee_id') or '—'}")
                        st.markdown(f"**📱 Mobile:** {t.get('mobile_number') or '—'}")
                        st.markdown(f"**📧 Email:** {t.get('email') or '—'}")
                    with ex2:
                        st.markdown(f"**📁 Category:** {cat_icon} {t.get('category','—')}")
                        st.markdown(f"**🔥 Priority:** {prio}")
                        st.markdown(f"**📶 Status:** {stat}")
                        st.markdown(f"**💬 Sentiment:** {t.get('sentiment','—')}")
                        st.markdown(f"**⏱️ ETA:** {t.get('resolution_time') or '—'}")
                    st.markdown("**📋 AI Summary:**")
                    st.info(t.get("ticket_summary") or "No summary available.")
                    if t.get("suggested_resolution"):
                        st.markdown("**🔧 Suggested Resolution:**")
                        st.write(t.get("suggested_resolution"))
                    if t.get("transcript"):
                        with st.expander("📝 Raw Transcript"):
                            st.markdown(f'<div style="font-size:0.84rem; color:#94a3b8; line-height:1.7; background:rgba(0,0,0,0.2); padding:14px; border-radius:8px;">{t.get("transcript","")}</div>', unsafe_allow_html=True)

    # ── RIGHT: Manager Panel + Admin ────────────────────────────────────────────
    with col_mgr:

        # ── Manager update panel ────────────────────────────────────────────────
        st.markdown('<div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.1em; color:#64748b; font-weight:700; margin-bottom:10px;">🛠️ Manager Operations Panel</div>', unsafe_allow_html=True)

        if tickets_list:
            ticket_options = [f"{t['ticket_number']} — {(t.get('title') or '')[:38]}" for t in tickets_list]
            sel_label = st.selectbox("Select ticket", ticket_options, label_visibility="collapsed")
            sel_num = sel_label.split(" — ")[0].strip()
            t_details = next((t for t in tickets_list if t["ticket_number"] == sel_num), None)

            if t_details:
                st.markdown(f"""
                <div style="background:rgba(15,23,42,0.5); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:12px 14px; margin-bottom:12px;">
                    <div style="font-size:0.68rem; text-transform:uppercase; letter-spacing:0.1em; color:#64748b; font-weight:700; margin-bottom:6px;">Selected</div>
                    <div style="font-size:0.88rem; font-weight:700; color:#f1f5f9; margin-bottom:4px;">{t_details.get('title','')}</div>
                    <div style="font-size:0.72rem; color:#64748b;">{t_details.get('category','—')} &nbsp;|&nbsp; Sentiment: {t_details.get('sentiment','—')}</div>
                </div>
                """, unsafe_allow_html=True)

                new_worker   = st.text_input("👷 Assign Engineer", value=t_details.get("assigned_worker") or "", placeholder="Engineer name")
                new_status   = st.selectbox("📶 Update Status", ["Pending","Work In Progress","Resolved"],
                    index=["Pending","Work In Progress","Resolved"].index(t_details.get("status") or "Pending"))
                new_res_time = st.text_input("⏱️ Resolution ETA", value=t_details.get("resolution_time") or "", placeholder="e.g. 2 hours")
                new_notes    = st.text_area("📝 Notes", value=t_details.get("resolution_notes") or "", height=90, placeholder="Resolution notes...")

                if st.button("💾 Apply Update", use_container_width=True, type="primary"):
                    database.assign_worker(sel_num, new_worker)
                    database.update_ticket_status(sel_num, new_status)
                    database.update_resolution_time(sel_num, new_res_time)
                    database.add_resolution_notes(sel_num, new_notes)
                    if new_status == "Resolved":
                        database.mark_resolved(sel_num, new_notes)
                    st.success(f"✅ {sel_num} updated!")
                    time.sleep(0.7)
                    st.rerun()

                if st.button("🗑️ Delete Ticket", use_container_width=True):
                    database.delete_ticket(sel_num)
                    st.warning(f"Ticket {sel_num} deleted.")
                    time.sleep(0.7)
                    st.rerun()
        else:
            st.info("No tickets to manage. Clear filters to see tickets.")

        st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

        # ── CSV Export
        st.markdown('<div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.1em; color:#64748b; font-weight:700; margin-bottom:10px;">📥 Export & Backup</div>', unsafe_allow_html=True)
        all_raw = database.get_all_tickets()
        if all_raw:
            df_exp = pd.DataFrame(all_raw)
            df_exp["employee_name"] = df_exp["employee_name"].fillna("Voice Intake User")
            csv_bytes = df_exp.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download All Tickets (CSV)", data=csv_bytes, file_name="smartdesk_backup.csv", mime="text/csv", use_container_width=True)

        st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

        # ── Admin Controls
        st.markdown('<div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.1em; color:#ef4444; font-weight:700; margin-bottom:8px;">⚠️ Admin Controls</div>', unsafe_allow_html=True)
        st.markdown('<div style="background:rgba(239,68,68,0.05); border:1px solid rgba(239,68,68,0.15); border-radius:10px; padding:11px 14px; margin-bottom:10px; font-size:0.78rem; color:#94a3b8;">Wipes all tickets and reseeds with 8 sample enterprise records.</div>', unsafe_allow_html=True)
        if st.button("🚨 Reset & Re-Seed Database", use_container_width=True):
            database.create_database()
            with database.sqlite3.connect(database.DB_PATH) as conn:
                conn.execute("DELETE FROM tickets")
                database.seed_tickets(conn)
                conn.commit()
            st.success("Database reset and reseeded!")
            time.sleep(1.0)
            st.rerun()

        st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

        # ── Team Alert Routing
        st.markdown('<div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.1em; color:#64748b; font-weight:700; margin-bottom:10px;">📧 Team Alert Routing</div>', unsafe_allow_html=True)
        configs = database.get_email_configs()
        if configs:
            for team, email in configs.items():
                st.markdown(f"""
                <div style="background:rgba(15,23,42,0.45); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:8px 12px; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap;">
                    <span style="font-size:0.77rem; font-weight:600; color:#94a3b8;">{team}</span>
                    <span style="font-size:0.71rem; color:#3b82f6; font-family:monospace;">{email}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No alert emails configured.")
