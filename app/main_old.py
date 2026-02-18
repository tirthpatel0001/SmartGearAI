import sys
import os
import streamlit as st
import hashlib

# ------------------------------------------------------------------
# FIX PYTHON PATH (VERY IMPORTANT)
# ------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="SGMAS – Smart Gear AI",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------
# CUSTOM STYLING
# ------------------------------------------------------------------
st.markdown("""
    <style>
        /* Admin login styling */
        .admin-login-box {
            background: linear-gradient(135deg, #FF6B6B 0%, #FF5252 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin: 15px 0;
        }
        
        .admin-badge {
            display: inline-block;
            background: #FF6B6B;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-right: 10px;
        }
        
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .main-title {
            font-size: 2.8em;
            font-weight: 900;
            margin: 0;
        }
        
        .main-subtitle {
            font-size: 1.2em;
            opacity: 0.95;
            margin: 10px 0 0 0;
        }
        
        .module-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }
        
        .module-card:hover {
            transform: translateY(-5px);
        }
        
        .module-icon {
            font-size: 3.5em;
            margin-bottom: 15px;
        }
        
        .module-name {
            font-size: 1.5em;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        .module-desc {
            font-size: 0.95em;
            opacity: 0.9;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# AUTHENTICATION SYSTEM (FOR ADMIN ONLY)
# ------------------------------------------------------------------
def check_admin_credentials(username, password):
    valid_username = "tirth0001"
    valid_password = "0001"
    return username == valid_username and password == valid_password

# Initialize session state
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False
if 'admin_username' not in st.session_state:
    st.session_state.admin_username = ""

# ------------------------------------------------------------------
# MAIN HEADER
# ------------------------------------------------------------------
st.markdown("""
    <div class="main-header">
        <div class="main-title">⚙️ SGMAS</div>
        <div class="main-subtitle">Smart Gear AI System</div>
    </div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------------------------
st.sidebar.title("⚙️ SGMAS Navigation")

menu = st.sidebar.radio(
    "📋 Select Module",
    [
        "🏠 Home",
        "🖼️ Gear Quality Detection",
        "💰 Gear Price Predictor"
    ]
)

# Admin section in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔐 Admin Panel")

if st.session_state.admin_authenticated:
    st.sidebar.success(f"✅ Admin: {st.session_state.admin_username}")
    if st.sidebar.button("🚪 Admin Logout"):
        st.session_state.admin_authenticated = False
        st.session_state.admin_username = ""
        st.rerun()
else:
    with st.sidebar.expander("🔓 Admin Login"):
        admin_user = st.text_input("Username", placeholder="tirth0001", key="admin_user")
        admin_pass = st.text_input("Password", type="password", placeholder="****", key="admin_pass")
        
        if st.button("Login to Admin", use_container_width=True):
            if check_admin_credentials(admin_user, admin_pass):
                st.session_state.admin_authenticated = True
                st.session_state.admin_username = admin_user
                st.success("✅ Admin authenticated!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

# ------------------------------------------------------------------
# HOME PAGE
# ------------------------------------------------------------------
if menu == "🏠 Home":
    st.markdown("""
        <div style="text-align: center; margin: 40px 0;">
            <h1 style="font-size: 2.5em; margin-bottom: 10px;">Welcome to SGMAS</h1>
            <p style="font-size: 1.1em; color: #666;">Select a module from the sidebar to get started</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Display available modules
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="module-card">
                <div class="module-icon">🖼️</div>
                <div class="module-name">Gear Quality Detection</div>
                <div class="module-desc">AI-powered image analysis to detect gear defects and quality assessment</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="module-card">
                <div class="module-icon">💰</div>
                <div class="module-name">Gear Price Predictor</div>
                <div class="module-desc">Intelligent pricing system with cost breakdown and PDF estimate generation</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick stats
    st.markdown("### 📊 System Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔧 Active Modules", "2", "+2")
    with col2:
        st.metric("🤖 AI Models", "2", "+2")
    with col3:
        admin_status = "✅ Logged In" if st.session_state.admin_authenticated else "🔒 Locked"
        st.metric("🔐 Admin Access", admin_status)
    with col4:
        st.metric("📈 Status", "Operational")

# ------------------------------------------------------------------
# GEAR QUALITY DETECTION MODULE
# ------------------------------------------------------------------
elif menu == "🖼️ Gear Quality Detection":
    from app.gear_detection import *  # Import all from gear_detection module

# ------------------------------------------------------------------
# GEAR PRICE PREDICTOR MODULE
# ------------------------------------------------------------------
elif menu == "💰 Gear Price Predictor":
    from app.dashboard import *  # Import all from dashboard module
