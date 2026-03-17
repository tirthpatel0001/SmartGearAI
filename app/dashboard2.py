import streamlit as st


def dashboard_page():
    st.sidebar.title("SmartGear AI")

    st.sidebar.write(f"👤 User: {st.session_state.username}")
    st.sidebar.write(f"🔑 Role: {st.session_state.role}")
    st.sidebar.markdown("---")

    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        st.markdown(f"""
            <div style="padding: 10px; background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%); 
                        border-radius: 10px; color: white; text-align: center; margin-top: 10px;">
                <b>👤 {st.session_state.username}</b><br>
                <small>{st.session_state.get('role', 'User')}</small>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🚪", help="Logout", use_container_width=True, key="logout_dashboard2"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.title("📊 Dashboard")
    st.success("You are logged in!")

    st.markdown("### Portal Actions")

    col1, col2 = st.columns(2)
    with col1:
        st.info("Welcome to the SmartGear AI production portal.")

    with col2:
        st.write(" ")

    if st.session_state.get("role") == "production_head":
        if st.button("⚙️ Open Workload Analyzer", key="open_workload_analyzer"):
            from app.workload_ui import workload_ui
            workload_ui()
            return

    st.markdown("---")
    st.write("Use the sidebar actions or the portal button above.")
