import streamlit as st
import pandas as pd
import joblib
import os
import sys
import tempfile
from PIL import Image
import torch
from src.pdf_generator.gearbox_report_pdf import generate_gearbox_pdf
import matplotlib.pyplot as plt
from reportlab.platypus import Image as RLImage

if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Home"
st.set_page_config(page_title="SmartGear AI", page_icon="⚙️")

project_root = r"C:\Projects\SGMAS"
sys.path.append(project_root)
# including app folder to allow direct import when running as script
sys.path.append(os.path.join(project_root, "app"))




from src.quality_defect.predict_quality import (
    load_quality_model,
    predict_quality,
    QUALITY_CLASSES
)
from src.gear_box_defect.predict import predict_fault_and_severity
from maintenance_dashboard import display_gearbox_diagnosis
from src.pdf_generator.create_pdf import generate_estimate_pdf
from src.utils.config import load_config, save_config

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="SGMAS – Smart Gear Management System",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# --- Authentication gate: show login/signup when not authenticated ---
from login import login_page

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
    st.stop()

# Provide a simple logout control in the sidebar when authenticated
def _safe_rerun():
    if hasattr(st, "experimental_rerun"):
        try:
            st.experimental_rerun()
            return
        except Exception:
            pass
    st.stop()


def display_workload_analyzer():
    st.markdown("## ⚙️ Workload Analyzer (Production Head)")
    st.write("Use the ML model to predict lead time, machine requirements, and status.")

    col1, col2, col3 = st.columns(3)
    with col1:
        gear_type = st.selectbox("Gear Type", ["Spur", "Helical", "Bevel"], index=0)
    with col2:
        teeth = st.number_input("Teeth", value=80, min_value=1)
    with col3:
        diameter = st.number_input("Diameter", value=180, min_value=1)

    process_steps = st.number_input("Process Steps", value=4, min_value=1)
    machine_count = st.number_input("Current Machine Count", value=3, min_value=1)
    current_jobs = st.number_input("Current Jobs", value=5, min_value=0)
    machine_capacity = st.number_input("Machine Capacity", value=6, min_value=1)
    progress = st.slider("Progress (%)", min_value=0, max_value=100, value=60)

    st.markdown("### ⚙️ Risk Inputs")
    air_temp = st.number_input("Air Temperature (K)", value=300.0)
    process_temp = st.number_input("Process Temperature (K)", value=308.0)
    rotational_speed = st.number_input("Rotational Speed (rpm)", value=1500.0)
    torque = st.number_input("Torque (Nm)", value=50.0)
    tool_wear = st.number_input("Tool Wear (min)", value=5.0)

    if st.button("Analyze Workload"):
        if not st.session_state.get("token"):
            st.error("Authentication token missing. Please log in again.")
            return

        import requests
        headers = {"Authorization": f"Bearer {st.session_state.token}", "Content-Type": "application/json"}
        payload = {
            "gear_type": gear_type,
            "teeth": teeth,
            "diameter": diameter,
            "process_steps": process_steps,
            "machine_count": machine_count,
            "current_jobs": current_jobs,
            "machine_capacity": machine_capacity,
            "progress": progress,
            "air_temperature": air_temp,
            "process_temperature": process_temp,
            "rotational_speed": rotational_speed,
            "torque": torque,
            "tool_wear": tool_wear,
        }
        try:
            resp = requests.post("http://127.0.0.1:5000/api/production/workload-analyzer", json=payload, headers=headers, timeout=20)
            if resp.status_code != 200:
                st.error(f"Workload API error {resp.status_code}: {resp.text}")
            else:
                data = resp.json()
                st.success("✅ Workload prediction succeeded")
                msg = data.get("messages", {})
                st.markdown("### 🔎 Prediction Summary")
                st.write(msg.get("lead_time_text", "Lead time unavailable"))
                st.write(msg.get("machine_requirement_text", "Machine requirement unavailable"))
                status = msg.get("workload_status", "unknown")
                status_badge = {
                    "overloaded": "🔴 Overloaded",
                    "normal": "🟢 Normal",
                    "underutilized": "🟡 Underutilized",
                }.get(status, "⚪ Unknown")
                st.write(f"### Workload Status: {status_badge}")
                st.write(msg.get("remaining_time_text", "Remaining time unavailable"))

                st.markdown("### 📊 Numeric Output")
                st.metric("Lead Time (hrs)", f"{data.get('lead_time', 0):.2f}")
                st.metric("Remaining Time (hrs)", f"{data.get('remaining_time', 0):.2f}")
                st.metric("Machine Needed", data.get("machine_needed", 1))
                st.metric("Machine Risk", data.get("machine_risk", "normal"))
        except Exception as exc:
            st.error(f"Error calling backend API: {exc}")


with st.sidebar:
    # Modern SGMAS Header
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%);
            padding: 20px;
            border-radius: 14px;
            text-align: center;
            border-top: 4px solid #D97706;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
            border: 1px solid rgba(217, 119, 6, 0.2);
        ">
            <h2 style="
                margin: 0;
                color: white;
                font-size: 1.6em;
                font-weight: 800;
                letter-spacing: -0.5px;
            ">⚙️ SGMAS</h2>
            <p style="
                margin: 6px 0 0 0;
                color: rgba(255, 255, 255, 0.9);
                font-size: 0.85em;
                font-weight: 500;
                letter-spacing: 0.3px;
            ">Smart Gear Management System</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # User Profile Section
    if "username" in st.session_state and st.session_state.username:
        st.markdown(f"""
            <div style="
                padding: 18px 20px;
                background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%);
                border-radius: 14px;
                color: white;
                text-align: center;
                border-top: 3px solid #D97706;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
                border: 1px solid rgba(217, 119, 6, 0.2);
                margin: 15px 0;
            ">
                <div style="margin-bottom: 12px;">
                    <b style="font-size: 1.1em; letter-spacing: 0.3px; display: block;">👤 {st.session_state.username}</b>
                    <small style="color: rgba(255, 255, 255, 0.85); font-size: 0.9em; letter-spacing: 0.2px; display: block; margin-top: 4px;">{st.session_state.get('role', 'User').replace('_', ' ').title()}</small>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.current_tab = "Home"
            _safe_rerun()
    else:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.token = None
            st.session_state.current_tab = "Home"
            _safe_rerun()

# ==================== CUSTOM CSS ====================


st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;300;400;500;600;700;800&family=Roboto+Mono:wght@400;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    :root {
        --primary-dark: #1E3A5F;
        --primary-steel: #2C5282;
        --accent-orange: #D97706;
        --accent-amber: #B8860B;
        --success-green: #059669;
        --danger-red: #DC2626;
        --background: #F5F7FA;
        --card-bg: #FFFFFF;
        --text-primary: #111827;
        --text-secondary: #6B7280;
        --border-light: #E5E7EB;
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 12px 24px rgba(0, 0, 0, 0.12);
        --shadow-xl: 0 20px 40px rgba(0, 0, 0, 0.15);
    }
    
    html, body {
        background-color: var(--background) !important;
        scroll-behavior: smooth;
    }
    
    .main {
        background-color: var(--background);
        padding: 20px;
    }
    
    /* HERO HEADER - ADVANCED */
    .hero-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 50%, #2C5282 100%);
        color: white;
        padding: 60px 50px;
        border-radius: 16px;
        margin-bottom: 35px;
        box-shadow: 
            var(--shadow-xl),
            0 0 60px rgba(217, 119, 6, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        text-align: center;
        border-top: 5px solid var(--accent-orange);
        position: relative;
        overflow: hidden;
        animation: fadeInDown 0.6s ease-out;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .hero-header::before {
        content: '⚙️';
        position: absolute;
        top: -30px;
        right: -30px;
        font-size: 150px;
        opacity: 0.08;
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(20px); }
    }
    
    .hero-header h1 {
        margin: 0;
        font-size: 3.2em;
        font-weight: 800;
        letter-spacing: -0.8px;
        background: linear-gradient(135deg, #FFFFFF 0%, #FFE5CC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .hero-header p {
        margin: 16px 0 0 0;
        font-size: 1.15em;
        opacity: 0.95;
        font-weight: 400;
        letter-spacing: 0.3px;
    }
    
    /* ADVANCED CARD STYLING */
    .industrial-card {
        background: var(--card-bg);
        border-radius: 14px;
        padding: 28px;
        margin: 20px 0;
        box-shadow: var(--shadow-md);
        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
        border-left: 5px solid var(--accent-orange);
        position: relative;
        border: 1px solid rgba(217, 119, 6, 0.2);
    }
    
    .industrial-card::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: linear-gradient(135deg, rgba(217, 119, 6, 0.05) 0%, transparent 70%);
        border-radius: 0 14px 0 0;
    }
    
    .industrial-card:hover {
        transform: translateY(-6px);
        box-shadow: var(--shadow-xl);
        border-left-color: #F59E0B;
    }
    
    .industrial-card h3 {
        color: var(--primary-dark);
        margin: 0 0 14px 0;
        font-size: 1.4em;
        font-weight: 700;
        letter-spacing: -0.3px;
        position: relative;
        z-index: 1;
    }
    
    /* PREMIUM METRIC CARDS */
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);
        color: var(--text-primary);
        padding: 28px;
        border-radius: 14px;
        text-align: center;
        box-shadow: var(--shadow-md);
        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
        border-top: 4px solid var(--accent-orange);
        border: 1px solid rgba(229, 231, 235, 0.8);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, var(--accent-orange) 0%, transparent 100%);
        opacity: 0;
        animation: slideRight 0.6s ease-out;
    }
    
    @keyframes slideRight {
        to { opacity: 1; }
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: var(--shadow-xl);
        background: linear-gradient(135deg, #FFFFFF 0%, #F3F4F6 100%);
    }
    
    .metric-card h4 {
        margin: 0 0 10px 0;
        font-size: 0.8em;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.7px;
        font-weight: 700;
    }
    
    .metric-card .value {
        font-size: 2.6em;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent-orange) 0%, #F59E0B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        font-family: 'Roboto Mono', monospace;
        letter-spacing: -1px;
    }
    
    /* SUCCESS CARD - PREMIUM */
    .success-card {
        background: linear-gradient(135deg, var(--success-green) 0%, #047857 100%);
        color: white;
        padding: 32px;
        border-radius: 14px;
        margin: 25px 0;
        box-shadow: var(--shadow-xl);
        text-align: center;
        border-left: 5px solid #10B981;
        position: relative;
        overflow: hidden;
        animation: scaleIn 0.5s ease-out;
    }
    
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    .success-card::before {
        content: '✓';
        position: absolute;
        top: -20px;
        right: -20px;
        font-size: 100px;
        opacity: 0.08;
    }
    
    .success-card h3 {
        margin: 0 0 14px 0;
        font-size: 1.3em;
        font-weight: 700;
        position: relative;
        z-index: 1;
    }
    
    .success-card .price {
        font-size: 3.5em;
        font-weight: 800;
        margin: 10px 0;
        font-family: 'Roboto Mono', monospace;
        letter-spacing: -1px;
        position: relative;
        z-index: 1;
    }
    
    /* ADVANCED INPUT SECTION */
    .input-section {
        background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);
        padding: 32px;
        border-radius: 14px;
        margin: 25px 0;
        box-shadow: var(--shadow-md);
        border-top: 4px solid var(--primary-dark);
        border: 1px solid rgba(229, 231, 235, 0.8);
        transition: all 0.3s ease;
    }
    
    .input-section:hover {
        box-shadow: var(--shadow-lg);
    }
    
    .input-section h3 {
        color: var(--primary-dark);
        margin-top: 0;
        font-weight: 700;
        font-size: 1.25em;
    }
    
    /* RESULT CARD - PREMIUM */
    .result-card {
        background: var(--card-bg);
        border-radius: 14px;
        overflow: hidden;
        box-shadow: var(--shadow-md);
        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
        border: 1px solid rgba(229, 231, 235, 0.8);
        animation: fadeInUp 0.5s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .result-card:hover {
        transform: translateY(-6px);
        box-shadow: var(--shadow-xl);
    }
    
    .result-status {
        padding: 18px;
        text-align: center;
        font-weight: 700;
        font-size: 1.1em;
        letter-spacing: 0.5px;
    }
    
    .result-good {
        background: linear-gradient(135deg, var(--success-green) 0%, #047857 100%);
        color: white;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }
    
    .result-defect {
        background: linear-gradient(135deg, var(--danger-red) 0%, #991B1B 100%);
        color: white;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    /* ADVANCED TABLE */
    .breakdown-table {
        background: var(--card-bg);
        padding: 28px;
        border-radius: 14px;
        box-shadow: var(--shadow-md);
        margin: 25px 0;
        border: 1px solid rgba(229, 231, 235, 0.8);
        overflow: hidden;
    }
    
    .breakdown-table h3 {
        color: var(--primary-dark);
        margin-top: 0;
        font-weight: 700;
        font-size: 1.25em;
    }
    
    .breakdown-table table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .breakdown-table th {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-steel) 100%);
        color: white;
        padding: 14px;
        text-align: left;
        font-weight: 700;
        border-bottom: 2px solid var(--accent-orange);
        letter-spacing: 0.3px;
        font-size: 0.95em;
    }
    
    .breakdown-table td {
        padding: 14px;
        border-bottom: 1px solid rgba(229, 231, 235, 0.6);
        font-size: 0.95em;
    }
    
    .breakdown-table tr:hover {
        background-color: rgba(217, 119, 6, 0.03);
    }
    
    .breakdown-table tr:last-child td {
        border-bottom: 2px solid var(--primary-dark);
        font-weight: 700;
        color: var(--accent-orange);
        background: rgba(217, 119, 6, 0.05);
    }
    
    /* PREMIUM BUTTONS */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-orange) 0%, #F59E0B 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 32px !important;
        font-weight: 700 !important;
        font-size: 0.95em !important;
        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        box-shadow: 
            0 10px 25px rgba(217, 119, 6, 0.25),
            0 0 1px rgba(255, 255, 255, 0.3) inset !important;
        letter-spacing: 0.3px !important;
        overflow: hidden !important;
        position: relative !important;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) !important;
        box-shadow: 
            0 15px 35px rgba(217, 119, 6, 0.35),
            0 0 1px rgba(255, 255, 255, 0.5) inset !important;
        background: linear-gradient(135deg, #B45309 0%, #D97706 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* ADVANCED TAB STYLING */
    .stTabs {
        margin-bottom: 30px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 2px solid rgba(217, 119, 6, 0.2);
        padding-bottom: 8px;
        background: linear-gradient(90deg, transparent 0%, rgba(217, 119, 6, 0.02) 100%);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-bottom: 3px solid transparent !important;
        color: var(--text-secondary) !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        padding: 12px 16px !important;
        font-size: 0.95em !important;
        letter-spacing: 0.3px !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--accent-orange) !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        border-bottom-color: var(--accent-orange) !important;
        color: var(--accent-orange) !important;
        font-weight: 800 !important;
    }
    
    /* DIVIDER */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, var(--border-light) 50%, transparent 100%);
        margin: 28px 0;
    }
    
    /* SIDEBAR STYLING */
    .sidebar-header {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-steel) 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
        border-top: 4px solid var(--accent-orange);
        box-shadow: var(--shadow-lg);
    }
    
    .sidebar-header h2 {
        margin: 0;
        font-size: 1.6em;
        font-weight: 800;
        letter-spacing: -0.3px;
    }
    
    .info-box {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-steel) 100%);
        color: white;
        padding: 18px;
        border-radius: 10px;
        margin: 14px 0;
        border-left: 5px solid var(--accent-orange);
        font-weight: 500;
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
    }
    
    .info-box:hover {
        transform: translateX(4px);
        box-shadow: var(--shadow-lg);
    }
    
    .info-box strong {
        color: var(--accent-orange);
        font-weight: 700;
    }
    
    /* MESSAGE STYLING */
    .stSuccess {
        background: rgba(5, 150, 105, 0.1) !important;
        border: 1.5px solid #059669 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        animation: slideInDown 0.3s ease-out;
    }
    
    .stError {
        background: rgba(220, 38, 38, 0.1) !important;
        border: 1.5px solid #DC2626 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        animation: slideInDown 0.3s ease-out;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        border: 1.5px solid #F59E0B !important;
        border-radius: 12px !important;
        padding: 16px !important;
        animation: slideInDown 0.3s ease-out;
    }
    
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* FOOTER */
    .footer {
        text-align: center;
        padding: 40px;
        color: var(--text-secondary);
        font-size: 0.9em;
        border-top: 2px solid var(--border-light);
        margin-top: 60px;
        background: linear-gradient(135deg, var(--card-bg) 0%, #F9FAFB 100%);
        border-radius: 12px;
        letter-spacing: 0.2px;
    }
    
    /* MODERN INPUTS */
    input, select, textarea {
        border-radius: 10px !important;
        border: 1.5px solid rgba(217, 119, 6, 0.3) !important;
        padding: 12px 14px !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
    }
    
    input:focus, select:focus, textarea:focus {
        border-color: var(--accent-orange) !important;
        box-shadow: 
            0 0 0 3px rgba(217, 119, 6, 0.1),
            inset 0 0 0 1px rgba(217, 119, 6, 0.2) !important;
        outline: none !important;
    }
    
    label {
        font-weight: 700 !important;
        color: var(--primary-dark) !important;
        font-size: 0.9em !important;
        letter-spacing: 0.2px !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'Home'

# ==================== HELPER FUNCTIONS ====================

def display_home_features():
    """Display home page with features"""
    st.markdown("""
        <div class="hero-header">
            <h1>⚙️ SGMAS</h1>
            <p>Smart Gear Management & Analysis System</p>
            <p style="font-size: 1em; margin-top: 20px;">Intelligent Solutions for Gear Quality Detection, Price Prediction & Gearbox Diagnosis</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

def display_quality_detection():
    """Display gear quality detection module"""
    st.markdown("""
        <div class="hero-header" style="padding: 40px; margin-bottom: 30px;">
            <h1>🖼️ Gear Quality Detection</h1>
            <p>AI-Powered Image Analysis for Defect Detection</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="info-box">
            <h4>📋 How to Use</h4>
            <p>Upload one or multiple gear images. Our AI will analyze each image to detect quality defects and classify gears as GOOD or DEFECT.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load quality model
    @st.cache_resource
    def load_quality_model_cached():
        return load_quality_model("data/models/quality_model_weights.pth")
    
    try:
        model = load_quality_model_cached()
    except FileNotFoundError:
        st.error("❌ Quality model not found. Please train the model first.")
        return
    
    # File uploader
    st.markdown("<div class='input-section'>", unsafe_allow_html=True)
    st.markdown("### 📤 Upload Gear Images")
    uploaded_files = st.file_uploader(
        "Select one or multiple gear images",
        type=["jpg", "jpeg", "png", "bmp"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    if uploaded_files:
        results = []
        st.markdown("---")
        st.markdown("### 🔍 Detection Results")
        
        # Create columns for image display
        cols = st.columns(3)
        col_index = 0
        
        for file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(file.getbuffer())
                temp_path = tmp.name
            
            try:
                prediction = predict_quality(temp_path, model)
                
                with cols[col_index]:
                    st.markdown(f"""
                        <div class="result-card">
                            <img src='file://{os.path.abspath(file.name)}' style='display:none;'>
                    """, unsafe_allow_html=True)
                    
                    img = Image.open(file)
                    # Resize image to 200x200 pixels
                    img_resized = img.resize((200, 200), Image.Resampling.LANCZOS)
                    st.image(img_resized)
                    
                    if prediction == "GOOD":
                        st.markdown("""
                            <div class="result-status result-good">
                                ✅ GOOD QUALITY
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                            <div class="result-status result-defect">
                                ⚠️ DEFECT DETECTED
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"<p style='text-align: center; color: #7f8c8d;'>{file.name}</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                results.append({
                    "Image Name": file.name,
                    "Status": prediction,
                    "Quality": "✅ Good" if prediction == "GOOD" else "⚠️ Defect"
                })
                
                col_index = (col_index + 1) % 3
            finally:
                os.remove(temp_path)
        
        # Summary Statistics
        st.markdown("---")
        st.markdown("### 📊 Summary Statistics")
        
        df = pd.DataFrame(results)
        
        col1, col2, col3 = st.columns(3)
        good_count = (df["Status"] == "GOOD").sum()
        defect_count = (df["Status"] == "DEFECT").sum()
        
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>Total Images</h4>
                    <p class="value">{len(df)}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>✅ Good Quality</h4>
                    <p class="value" style="color: #06A77D;">{good_count}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>⚠️ Defects</h4>
                    <p class="value" style="color: #FF6B6B;">{defect_count}</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Results table
        st.markdown("### 📋 Detailed Results")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    else:
        st.markdown("""
            <div class="info-box" style="text-align: center; padding: 40px;">
                <h3>⬆️ Upload Gear Images to Begin Detection</h3>
                <p>Drag and drop or click to select gear images for quality analysis</p>
            </div>
        """, unsafe_allow_html=True)

def display_price_prediction():
    """Display gear price prediction module"""
    st.markdown("""
        <div class="hero-header" style="padding: 40px; margin-bottom: 30px;">
            <h1>💰 Gear Price Predictor</h1>
            <p>Intelligent Pricing for Precision Gears</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="info-box">
            <h4>💡 Smart Pricing Engine</h4>
            <p>Enter gear specifications below and our advanced ML model will calculate an accurate price estimate including material costs, labor, and special treatments.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load config
    config = load_config()
    
    # Check if model exists
    model_path = os.path.join(project_root, 'data', 'models', 'gear_price_model.pkl')
    if not os.path.exists(model_path):
        st.error(f"❌ Trained model not found. Please train the price prediction model first.")
        return
    
    model = joblib.load(model_path)
    
    # Input Section
    st.markdown("<div class='input-section'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Enter Gear Specifications")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        gear_type = st.selectbox("🔧 Gear Type", ["Spur", "Helical", "Bevel"], key="gear_type")
        diameter = st.slider("📏 Diameter (mm)", 50, 300, 100, key="diameter")
        thickness = st.slider("📐 Thickness (mm)", int(diameter*0.05), int(diameter*0.2), int(diameter*0.1), key="thickness")
    
    with col2:
        material = st.selectbox("🛠️ Material", ["Steel", "Alloy Steel", "Carbon Steel"], key="material")
        teeth = st.slider("🦷 Teeth Count", int(diameter*0.3), int(diameter*0.6), int(diameter*0.5), key="teeth")
        quantity = st.slider("📦 Quantity", 1, 500, 50, key="quantity")
    
    with col3:
        special_req = st.selectbox("✨ Special Treatment", ["None", "Hardening", "Coating"], key="special_req")
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
        predict_btn = st.button("💰 Calculate Price", use_container_width=True, key="predict_btn")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if predict_btn:
        # Calculate weight
        outer_radius = diameter / 2
        inner_radius = outer_radius * 0.3
        volume_cm3 = 3.1416 * (outer_radius**2 - inner_radius**2) * thickness * 0.1
        material_density = {'Steel': 7.85, 'Alloy Steel': 7.8, 'Carbon Steel': 7.7}
        weight_kg = volume_cm3 * material_density[material] / 1000
        
        # Prepare input for model
        input_df = pd.DataFrame([{
            'Gear_Type': gear_type,
            'Material': material,
            'Diameter_mm': diameter,
            'Teeth_Count': teeth,
            'Thickness_mm': thickness,
            'Quantity': quantity,
            'Special_Requirement': special_req,
            'Weight_kg': round(weight_kg, 2)
        }])
        
        base_price = model.predict(input_df)[0]
        
        # Cost calculations
        material_cost = weight_kg * config["material_rate_per_kg"].get(material, 100)
        treatment_cost = config["surface_treatment_charge"].get(special_req, 0) * quantity
        labor_hours_per_gear = 0.5 + 0.01*teeth
        machine_hours_per_gear = 0.5 + 0.005*diameter
        labor_cost = labor_hours_per_gear * config["labor_rate_per_hour"] * quantity
        machine_cost = machine_hours_per_gear * config["machine_hourly_cost"] * quantity
        urgency_multiplier = 1 + config["urgency_percentage"]/100
        
        predicted_price = (base_price + material_cost + treatment_cost + labor_cost + machine_cost) * urgency_multiplier
        
        # Display price
        st.markdown(f"""
            <div class="success-card">
                <h3>Estimated Total Price</h3>
                <p class="price">₹ {predicted_price:,.2f}</p>
                <p>Quantity: {quantity} units | Weight: {weight_kg:.2f} kg</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Cost breakdown
        cost_breakdown = {
            "Base ML Price": base_price,
            "Material Cost": material_cost,
            "Labor Cost": labor_cost,
            "Machine Cost": machine_cost,
            "Surface Treatment": treatment_cost,
            "Urgency Adjustment": predicted_price - (base_price + material_cost + treatment_cost + labor_cost + machine_cost)
        }
        
        customer_input = {
            "Gear Type": gear_type,
            "Material": material,
            "Diameter (mm)": diameter,
            "Teeth Count": teeth,
            "Thickness (mm)": thickness,
            "Quantity": quantity,
            "Special Requirement": special_req,
            "Weight (kg)": round(weight_kg, 2)
        }
        
        # Cost breakdown table
        st.markdown("<div class='breakdown-table'>", unsafe_allow_html=True)
        st.markdown("### 📊 Cost Breakdown")
        
        breakdown_df = pd.DataFrame(list(cost_breakdown.items()), columns=['Component', 'Amount (₹)'])
        breakdown_df['Amount (₹)'] = breakdown_df['Amount (₹)'].apply(lambda x: f"₹ {x:,.2f}")
        
        st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Specifications summary
        st.markdown("### 📋 Specifications Summary")
        spec_df = pd.DataFrame(list(customer_input.items()), columns=['Parameter', 'Value'])
        st.dataframe(spec_df, use_container_width=True, hide_index=True)
        
        # PDF Download
        st.markdown("---")
        pdf_path = generate_estimate_pdf(customer_input, predicted_price, cost_breakdown)
        
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Estimate PDF",
                data=f,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf",
                use_container_width=True
            )


def display_market_sales_forecast():
    st.markdown("""
        <div class='hero-header' style='padding: 30px; margin-bottom: 24px;'>
            <h1>📈 Market Sales Forecasting</h1>
            <p>Train and predict monthly sales with historical gear sales data.</p>
        </div>
    """, unsafe_allow_html=True)

    from pathlib import Path
    from datetime import datetime
    import pandas as pd

    csv_path = Path("data/raw/gear_sales_data.csv")
    df = None
    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                if "Quantity_Sold" not in df.columns and "Quantity Sold" in df.columns:
                    df["Quantity_Sold"] = df["Quantity Sold"]
                if "Quantity_Sold" in df.columns:
                    df = df.dropna(subset=["Date", "Quantity_Sold"])
                    df["Month"] = df["Date"].dt.month
                    df["Year"] = df["Date"].dt.year
                    df["MonthYear"] = df["Date"].dt.to_period("M").astype(str)
            else:
                st.warning("Date column missing in CSV. Forecast graphs are disabled until dataset is fixed.")
        except Exception:
            st.warning("Could not parse sales CSV. Forecast graphs may be unavailable.")
    else:
        st.warning("Sales dataset not found at data/raw/gear_sales_data.csv")

    # Training and predict controls
    st.markdown("### 🔧 Forecast Controls")
    col_train, col_predict = st.columns([1, 2])
    with col_train:
        if st.button("Train Forecast Model"):
            try:
                import requests
                r = requests.get("http://127.0.0.1:5000/api/forecast/train", timeout=35)
                if r.ok:
                    data = r.json()
                    st.success("✅ Model trained successfully")
                    st.write(data)
                else:
                    st.error(f"Training failed: {r.status_code} {r.text}")
            except Exception as exc:
                st.error(f"Training API error: {exc}")

    with col_predict:
        pm, py = st.columns(2)
        month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        month_name = pm.selectbox("Month", month_names, index=datetime.now().month - 1)
        year = py.number_input("Year", min_value=2000, max_value=2100, value=datetime.now().year)
        gear_type = st.selectbox("Gear Type", ["Spur", "Helical", "Bevel"], index=0)
        region = st.selectbox("Region", ["North", "South", "East", "West"], index=0)

        if st.button("Predict Sales"):
            try:
                import requests
                month_num = month_names.index(month_name) + 1
                r = requests.post(
                    "http://127.0.0.1:5000/api/forecast/predict",
                    json={"month": month_num, "year": int(year), "gear_type": gear_type, "region": region, "customer_type": "Retail"},
                    timeout=20,
                )
                if r.ok:
                    pred = r.json()
                    st.session_state.sales_forecast_prediction = pred
                    st.success("✅ Prediction successful")
                    st.metric("Predicted Sales", f"{pred.get('predicted_sales', 0):,.2f}")
                    st.write(f"**Insight:** {pred.get('insight', 'N/A')}")
                    st.write(f"Average Historical Sales: {pred.get('average_sales', 'N/A')}")
                    rec = pred.get("recommendation", "N/A")
                    st.info(f"Inventory Recommendation: {rec}")

                    # Next month forecast
                    next_month = month_num + 1
                    next_year = year
                    if next_month == 13:
                        next_month = 1
                        next_year += 1
                    r2 = requests.post(
                        "http://127.0.0.1:5000/api/forecast/predict",
                        json={"month": next_month, "year": next_year, "gear_type": gear_type, "region": region, "customer_type": "Retail"},
                        timeout=20,
                    )
                    if r2.ok:
                        next_pred = r2.json().get("predicted_sales", None)
                        if next_pred is not None:
                            st.success(f"Next month forecast ({month_names[next_month-1]} {next_year}): {next_pred:,.2f}")
                    else:
                        st.warning("Could not compute next-month forecast")
                else:
                    st.error(f"Prediction failed: {r.status_code} {r.text}")
            except Exception as exc:
                st.error(f"Prediction API error: {exc}")

    with st.expander("🔍 Advanced AI Insights: Price Optimization & Demand Segmentation", expanded=False):
        colA, colB = st.columns(2)
        with colA:
            try:
                rpo = requests.get("http://127.0.0.1:5000/api/forecast/price-optimization", timeout=20)
                if rpo.ok:
                    p = rpo.json()
                    if "error" not in p:
                        st.markdown("**Price Optimization**")
                        st.write(f"Price coeff: {p.get('price_coefficient')}, intercept: {p.get('intercept')}")
                        st.write(p.get('message'))
                        st.write(f"Optimal price estimate: {p.get('optimal_price_revenue')}")
                        st.write(f"Expected demand at optimal price: {p.get('optimal_quantity_at_optimal_price')}")
                    else:
                        st.warning(p.get('error'))
                else:
                    st.warning("Price optimization service unavailable")
            except Exception:
                st.warning("Price optimization request failed")

        with colB:
            try:
                rseg = requests.get("http://127.0.0.1:5000/api/forecast/demand-segmentation", timeout=20)
                if rseg.ok:
                    seg = rseg.json()
                    if "error" not in seg:
                        st.markdown("**Demand Segmentation**")
                        for msg in seg.get("customer_behavior", []):
                            st.write(f"- {msg}")
                        for msg in seg.get("segment_summary", []):
                            st.write(f"- {msg}")
                    else:
                        st.warning(seg.get('error'))
                else:
                    st.warning("Demand segmentation service unavailable")
            except Exception:
                st.warning("Demand segmentation request failed")

    st.markdown("---")
    if df is not None and not df.empty and "MonthYear" in df.columns and "Quantity_Sold" in df.columns:
        st.markdown("### 📊 Forecast Insights & Charts")

        # Metric cards
        with st.container():
            total = int(df["Quantity_Sold"].sum())
            avg = float(df["Quantity_Sold"].mean())
            max_month = df.groupby("MonthYear")["Quantity_Sold"].sum().idxmax()
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Historical Sold", f"{total:,}")
            col2.metric("Average Monthly", f"{avg:,.2f}")
            col3.metric("Top Month", max_month)

        # Chart 1: Historical monthly trend
        monthly = (
            df.groupby("MonthYear")["Quantity_Sold"].sum().reset_index().sort_values("MonthYear")
        )
        monthly["MonthYear"] = pd.to_datetime(monthly["MonthYear"])
        monthly = monthly.set_index("MonthYear")

        st.write("#### 1) Historical Monthly Sales Trend")
        st.line_chart(monthly["Quantity_Sold"])

        # Chart 2: Seasonality by month
        month_avg = df.groupby("Month")["Quantity_Sold"].mean().reindex(range(1, 13), fill_value=0)
        st.write("#### 2) Average Sales by Month (Seasonality)")
        st.bar_chart(month_avg)

        # Chart 3: Predicted vs Historical (basic)
        st.write("#### 3) Historical Yearly Sales")
        agg = df.groupby("Year")["Quantity_Sold"].sum().reset_index()
        if not agg.empty:
            st.area_chart(agg.rename(columns={"Year": "index"}).set_index("index"))
        else:
            st.write("Not enough historical data for year-level chart.")

        if st.session_state.get("sales_forecast_prediction"):
            pred = st.session_state.sales_forecast_prediction
            st.markdown("#### 4) Last Prediction Summary")
            st.metric("Predicted Sales", f"{pred.get('predicted_sales', 0):,.2f}")
            st.write(f"Insight: {pred.get('insight', 'N/A')}")
            st.write(f"Average Sales: {pred.get('average_sales', 'N/A')}")

    else:
        st.info("Add a valid 'Date' and 'Quantity_Sold' column to 'data/raw/gear_sales_data.csv' for charts.")

    st.markdown("---")
    st.markdown("#### Connect to React Dashboard")
    st.markdown("Use /api/forecast/train and /api/forecast/predict from your React UI. Build a line chart with monthly historical totals and predicted next month values for a unified dashboard.")


# def generate_signal_plots(csv_path, rms, energy, rms_th, energy_th):
#     img_dir = "data/reports/plots"
#     os.makedirs(img_dir, exist_ok=True)

#     df = pd.read_csv(csv_path)

#     # Time-domain plot
#     plt.figure(figsize=(6, 3))
#     plt.plot(df.iloc[:, 0], linewidth=0.8)
#     plt.title("Vibration Signal (Time Domain)")
#     plt.xlabel("Samples")
#     plt.ylabel("Amplitude")
#     time_plot = os.path.join(img_dir, "time_signal.png")
#     plt.tight_layout()
#     plt.savefig(time_plot)
#     plt.close()

#     # RMS bar chart
#     plt.figure(figsize=(4, 3))
#     plt.bar(["RMS", "Threshold"], [rms, rms_th])
#     plt.title("RMS vs Threshold")
#     rms_plot = os.path.join(img_dir, "rms_plot.png")
#     plt.tight_layout()
#     plt.savefig(rms_plot)
#     plt.close()

#     # Energy bar chart
#     plt.figure(figsize=(4, 3))
#     plt.bar(["Energy", "Threshold"], [energy, energy_th])
#     plt.title("Energy vs Threshold")
#     energy_plot = os.path.join(img_dir, "energy_plot.png")
#     plt.tight_layout()
#     plt.savefig(energy_plot)
#     plt.close()

#     return time_plot, rms_plot, energy_plot


def display_admin_login():
    """Display admin login form"""
    st.markdown("""
        <style>
        .admin-login-container {
            max-width: 600px;
            margin: 60px auto;
            background: white;
            border-radius: 20px;
            padding: 50px 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }
        
        .admin-header-hero {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .admin-header-hero h1 {
            background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5em;
            font-weight: 700;
            margin: 0 0 10px 0;
        }
        
        .admin-header-hero p {
            color: #7f8c8d;
            font-size: 0.95em;
            margin: 0;
        }
        </style>
        <div class="admin-login-container">
            <div class="admin-header-hero">
                <h1>🔐 Admin Access</h1>
                <p>Secure Configuration Panel</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        username = st.text_input("👤 Username", value="", placeholder="Enter admin username", key="admin_user")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter admin password", key="admin_pass")
        
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        if st.button("🔓 Login", use_container_width=True, key="admin_login_btn"):
            if username == "admin" and password == "admin":
                st.session_state.admin_authenticated = True
                st.success("✅ Authentication successful! Redirecting...")
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please try again.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_admin_panel():
    """Display admin configuration panel"""
    st.markdown("""
        <div class="hero-header" style="padding: 40px; margin-bottom: 30px;">
            <h1>⚙️ Admin Control Panel</h1>
            <p>Manage Pricing, Labor Rates, and Cost Factors</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check admin status via backend login
    role = st.session_state.get('role', 'guest')
    if role != 'admin':
        st.error('Admin access required. Please log in with an admin account.')
        return
    # Logout and Admin Status
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    with col1:
        st.markdown(f"""
            <div style="padding: 12px; background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%); 
                        border-radius: 10px; color: white; text-align: center;">
                <b>👨‍💼 Admin Panel</b><br>
                <small>Configuration Mode</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True, key="logout_admin_btn"):
            st.session_state.logged_in = False
            st.session_state.token = None
            st.session_state.role = 'guest'
            st.session_state.admin_authenticated = False
            st.session_state.current_tab = "Home"
            st.experimental_rerun()
    
    st.markdown("---")
    
    config = load_config()
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💰 Material Rates",
        "🏭 Labor & Machine",
        "✨ Treatments",
        "⚡ Urgency",
        "📊 Configuration View"
    ])
    
    # Tab 1: Material Rates
    with tab1:
        st.markdown("""
            <div class="feature-card">
                <h3>💰 Material Rates Per Kilogram</h3>
                <p>Configure the cost per kilogram for different materials</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        materials = list(config["material_rate_per_kg"].keys())
        
        for idx, material in enumerate(materials):
            col = [col1, col2, col3][idx % 3]
            with col:
                st.markdown(f"""
                    <div class="metric-card" style="background: white; color: #2c3e50; text-align: left; padding: 20px;">
                        <h4 style="color: #FF6B6B; margin: 0 0 10px 0;">{material}</h4>
                """, unsafe_allow_html=True)
                
                config["material_rate_per_kg"][material] = st.number_input(
                    f"Rate (₹/kg)",
                    value=float(config["material_rate_per_kg"][material]),
                    step=10.0,
                    key=f"material_{material}",
                    label_visibility="collapsed"
                )
                
                st.markdown(f"""
                        <p style="margin: 10px 0 0 0; color: #7f8c8d; font-size: 0.9em;">Current: ₹{config['material_rate_per_kg'][material]:.2f}/kg</p>
                    </div>
                """, unsafe_allow_html=True)
    
    # Tab 2: Labor & Machine Costs
    with tab2:
        st.markdown("""
            <div class="feature-card">
                <h3>🏭 Labor & Machine Cost Configuration</h3>
                <p>Set hourly rates for labor and machine operations</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; color: white; border-radius: 15px;">
                    <h3 style="margin: 0 0 20px 0;">👷 Labor Rate</h3>
            """, unsafe_allow_html=True)
            
            config["labor_rate_per_hour"] = st.number_input(
                "Labor Rate (₹/hour)",
                value=float(config["labor_rate_per_hour"]),
                step=50.0,
                key="labor_rate",
                label_visibility="collapsed"
            )
            
            st.markdown(f"""
                    <p style="margin: 15px 0 0 0; opacity: 0.9;">Current: ₹{config['labor_rate_per_hour']:.2f}/hour</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="metric-card" style="background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%); padding: 20px; color: white; border-radius: 15px;">
                    <h3 style="margin: 0 0 20px 0;">🤖 Machine Cost</h3>
            """, unsafe_allow_html=True)
            
            config["machine_hourly_cost"] = st.number_input(
                "Machine Cost (₹/hour)",
                value=float(config["machine_hourly_cost"]),
                step=50.0,
                key="machine_cost",
                label_visibility="collapsed"
            )
            
            st.markdown(f"""
                    <p style="margin: 15px 0 0 0; opacity: 0.9;">Current: ₹{config['machine_hourly_cost']:.2f}/hour</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Tab 3: Surface Treatment Charges
    with tab3:
        st.markdown("""
            <div class="feature-card">
                <h3>✨ Surface Treatment Charges Per Unit</h3>
                <p>Set charges for different surface treatment options</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        treatments = list(config["surface_treatment_charge"].keys())
        
        for idx, treatment in enumerate(treatments):
            col = [col1, col2, col3][idx % 3]
            with col:
                st.markdown(f"""
                    <div class="metric-card" style="background: white; color: #2c3e50; text-align: left; padding: 20px;">
                        <h4 style="color: #4ECDC4; margin: 0 0 10px 0;">{treatment}</h4>
                """, unsafe_allow_html=True)
                
                config["surface_treatment_charge"][treatment] = st.number_input(
                    f"Charge (₹)",
                    value=float(config["surface_treatment_charge"][treatment]),
                    step=50.0,
                    key=f"treatment_{treatment}",
                    label_visibility="collapsed"
                )
                
                st.markdown(f"""
                        <p style="margin: 10px 0 0 0; color: #7f8c8d; font-size: 0.9em;">Current: ₹{config['surface_treatment_charge'][treatment]:.2f}</p>
                    </div>
                """, unsafe_allow_html=True)
    
    # Tab 4: Urgency Adjustment
    with tab4:
        st.markdown("""
            <div class="feature-card">
                <h3>⚡ Urgency Multiplier Configuration</h3>
                <p>Set percentage markup for urgent orders</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="info-box">
                <p><strong>📌 How it works:</strong> This percentage is added as a multiplier to the final price for urgent orders. 
                For example, 20% means prices will be multiplied by 1.20x for urgent requests.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            config["urgency_percentage"] = st.slider(
                "Urgency Percentage (%)",
                min_value=0,
                max_value=100,
                value=int(config["urgency_percentage"]),
                step=5,
                key="urgency"
            )
            
            st.markdown(f"""
                <div class="feature-card">
                    <h4>Price Multiplier Impact</h4>
                    <p>With {int(config['urgency_percentage'])}% urgency adjustment:</p>
                    <p style="font-size: 1.3em; color: #FF6B6B; font-weight: 600;">Base Price × {1 + config['urgency_percentage']/100:.2f}x</p>
                    <p style="color: #7f8c8d; font-size: 0.9em;">Example: ₹100,000 would become ₹{100000 * (1 + config['urgency_percentage']/100):,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>Multiplier</h4>
                    <p class="value" style="font-size: 2em; margin: 10px 0;">{1 + config['urgency_percentage']/100:.2f}x</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Tab 5: Configuration View
    with tab5:
        st.markdown("""
            <div class="feature-card">
                <h3>📊 Current Configuration Overview</h3>
                <p>View all active system configuration settings</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Material Rates Summary
        st.markdown("### 💰 Material Rates (per kg)")
        material_df = pd.DataFrame(
            list(config["material_rate_per_kg"].items()),
            columns=["Material", "Rate (₹/kg)"]
        )
        material_df["Rate (₹/kg)"] = material_df["Rate (₹/kg)"].apply(lambda x: f"₹{x:.2f}")
        st.dataframe(material_df, use_container_width=True, hide_index=True)
        
        # Labor & Machine Summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👷 Labor Rate")
            st.markdown(f"""
                <div class="metric-card">
                    <p class="value">₹{config['labor_rate_per_hour']:.2f}</p>
                    <p>per hour</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🤖 Machine Cost")
            st.markdown(f"""
                <div class="metric-card">
                    <p class="value">₹{config['machine_hourly_cost']:.2f}</p>
                    <p>per hour</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Treatment Charges Summary
        st.markdown("### ✨ Treatment Charges")
        treatment_df = pd.DataFrame(
            list(config["surface_treatment_charge"].items()),
            columns=["Treatment", "Charge (₹)"]
        )
        treatment_df["Charge (₹)"] = treatment_df["Charge (₹)"].apply(lambda x: f"₹{x:.2f}")
        st.dataframe(treatment_df, use_container_width=True, hide_index=True)
        
        # Urgency Summary
        st.markdown("### ⚡ Urgency Configuration")
        st.markdown(f"""
            <div class="success-card" style="text-align: left;">
                <h4>Current Urgency Multiplier: <strong>{1 + config['urgency_percentage']/100:.2f}x</strong></h4>
                <p>Markup: <strong>{int(config['urgency_percentage'])}%</strong></p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Save button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 Save All Changes", use_container_width=True, key="save_btn"):
            save_config(config)
            st.success("✅ Configuration saved successfully!")
            st.balloons()

# ==================== MAIN APP ====================

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
        <div class="sidebar-header">
            <h2>⚙️ SGMAS</h2>
            <p>Smart Gear Management System</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### �️ Navigation")

    role = st.session_state.get('role', 'guest')
    nav_items = [
        ("🏠 Home", "Home"),
    ]
    if role != 'guest':
        nav_items.append(("🔔 Notifications", "Notifications"))

    # Role-based navigation
    if role == 'user':
        nav_items.extend([
            ("💰 Price Prediction", "Price Prediction"),
            ("💵 Price Estimation", "Price Estimation"),
        ])
    elif role == 'inventory_head':
        nav_items.extend([
            ("🖼️ Quality Detection", "Quality Detection"),
            ("📋 Inventory", "Inventory"),
            ("✓ Approve Requests", "Approve Requests"),
        ])
    elif role == 'maintenance_head':
        nav_items.append(("⚙️ Gearbox Diagnosis", "Gearbox Diagnosis"))
    elif role == 'production_head':
        # production heads get workload analyzer, material requests and forecasting
        nav_items.extend([
            ("⚙️ Workload Analyzer", "Workload Analyzer"),
            ("📝 Material Request", "Material Request"),
            ("📈 Market Sales Forecasting", "Market Sales Forecasting"),
        ])
    elif role == 'admin':
        nav_items.extend([
            ("🔧 Admin Panel", "Admin Panel"),
            ("🧾 Pending Signups", "Admin Requests"),
            ("👥 Manage Heads", "Manage Heads"),
            ("📈 Market Sales Forecasting", "Market Sales Forecasting"),
        ])
    elif role == 'scm_head':
        nav_items.extend([
            ("🛒 SCM Dashboard", "SCM Dashboard"),
            ("📋 Inventory", "Inventory"),
        ])
    elif role == 'scm_planner':
        # planner can view dashboard to see material requests and create PRs
        nav_items.extend([
            ("🛒 SCM Dashboard", "SCM Dashboard"),
            ("📝 Purchase Requests", "Purchase Requests"),
        ])
    elif role == 'scm_purchaser':
        # purchaser needs access to both PR list (to see what to order) and POs
        nav_items.extend([
            ("📝 Purchase Requests", "Purchase Requests"),
            ("📦 Purchase Orders", "Purchase Orders"),
        ])
    else:
        # guest or unknown: show Home only
        pass

    for label, key in nav_items:
        if st.button(label, use_container_width=True):
            st.session_state.current_tab = key
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 System Info")
    st.metric("Modules", 5)

    st.markdown("---")
    st.markdown("""
        **SGMAS**  
        AI-powered Gear Quality, Pricing & Diagnostics System
    """)

# ==================== MAIN CONTENT ====================

# ==================== MAIN CONTENT ====================

current = st.session_state.current_tab

if current == "Home":
    display_home_features()

elif current == "Quality Detection":
    display_quality_detection()

elif current == "Price Prediction":
    display_price_prediction()

elif current == "Price Estimation":
    from price_estimation_ui import main as price_estimation_main
    # Check role access
    if st.session_state.get('role') != 'user':
        st.error("❌ Access Denied: Only users can access the Price Estimation module.")
        st.stop()
    # Pass token and role through session state for API calls
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = st.session_state.get('role')
    price_estimation_main()

elif current == "Gearbox Diagnosis":
    display_gearbox_diagnosis()

elif current == "Admin Panel":
    display_admin_panel()

elif current == "Admin Requests":
    from admin_requests import display_pending_requests
    display_pending_requests()

elif current == "Manage Heads":
    from manage_heads import display_manage_heads
    display_manage_heads()

elif current == "SCM Dashboard":
    # inventory head / scm_head sees overall workflow
    from scm_chain import display_scm_dashboard
    display_scm_dashboard()

elif current == "Inventory":
    from scm_chain import display_inventory_management
    display_inventory_management()

elif current == "Material Request":
    from scm_chain import display_production_requests
    display_production_requests()

elif current == "Workload Analyzer":
    display_workload_analyzer()

elif current == "Market Sales Forecasting":
    display_market_sales_forecast()

elif current == "Notifications":
    from scm_chain import display_notifications
    display_notifications()

elif current == "Purchase Requests":
    from scm_chain import display_purchase_requests
    display_purchase_requests()

elif current == "Purchase Orders":
    from scm_chain import display_purchase_orders
    display_purchase_orders()

elif current == "Approve Requests":
    from inventory_manager import display_approve_requests
    display_approve_requests()
    
# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
    <div class="footer">
        <p>⚙️ <strong>SGMAS</strong> – Smart Gear Management & Analysis System</p>
        <p>Advanced AI Solutions for Precision Gear Manufacturing, Quality Control & Gearbox Diagnostics</p>
        <p style="font-size: 0.85em; opacity: 0.7;">© 2026 | Intelligent Gear Solutions | Powered by Machine Learning</p>
    </div>
""", unsafe_allow_html=True)