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
st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%); color: white; padding: 16px; border-radius: 8px; margin-bottom: 20px; border-top: 3px solid #D97706;">
        <h2 style="margin: 0; font-size: 1.4em; font-weight: 700;">⚙️ SmartGear AI</h2>
        <p style="margin: 6px 0 0 0; opacity: 0.9; font-size: 0.9em;">Manufacturing Intelligence System</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    list(pages.keys()),
    index=0,
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style="background: #FFFFFF; padding: 16px; border-radius: 8px; border-left: 3px solid #D97706;">
        <h3 style="margin: 0 0 12px 0; color: #1E3A5F; font-size: 1em; font-weight: 600;">Platform Features</h3>
        <ul style="margin: 0; padding-left: 20px; color: #6B7280; font-size: 0.9em;">
            <li>💰 Intelligent price estimation</li>
            <li>🔍 Quality & defect detection</li>
            <li>⚙️ Production management</li>
            <li>📊 Predictive maintenance</li>
            <li>📈 Workload analysis</li>
        </ul>
    </div>
""")

st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.85em; padding: 12px;">
        <p style="margin: 0 0 6px 0;"><strong>SmartGear AI v1.0</strong></p>
        <p style="margin: 0;">© 2026 Gear Manufacturing</p>
        <p style="margin: 6px 0 0 0; opacity: 0.7;">Powered by ML & AI</p>
    </div>
""", unsafe_allow_html=True)
