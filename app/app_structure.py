"""
ELECON Manufacturing System - Multi-page Streamlit App Structure
This file helps organize the app with proper page routing
"""

import streamlit as st

# Page configuration
pages = {
    "🏠 Home": "app/main.py",
    "💰 Dashboard": "app/dashboard.py", 
    "🔍 Quality Inspector": "app/quality_defect_ui.py",
    "⚙️ Workload Analyzer": "app/workload_ui.py",
    "🔐 Admin Panel": "app/admin_panel.py",
}

# Sidebar navigation
st.sidebar.title("🏭 ELECON System")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    list(pages.keys()),
    index=0,
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
    ### 📱 About
    
    **ELECON Manufacturing System**
    
    An AI-powered platform for:
    - 💰 Intelligent pricing
    - 🔍 Quality detection
    - ⚙️ Production tracking
    - 🔐 Cost management
    
    **Version:** 1.0
    **Status:** Active ✅
""")

st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style="text-align: center; color: #999; font-size: 0.8em;">
        <p>© 2026 ELECON Manufacturing</p>
        <p>Powered by AI & Machine Learning</p>
    </div>
""", unsafe_allow_html=True)
