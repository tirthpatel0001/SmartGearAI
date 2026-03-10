import streamlit as st
from api_client import login_user, signup_user


def _safe_rerun():
    """Call Streamlit rerun safely."""
    try:
        st.experimental_rerun()
    except Exception:
        st.stop()


def apply_login_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        * { font-family: 'Poppins', sans-serif; }
        </style>
    """, unsafe_allow_html=True)


def login_page():

    # ⚠️ IMPORTANT: set_page_config MUST be first Streamlit command
    st.set_page_config(
        page_title="SmartGear AI - Login",
        page_icon="⚙️",
        layout="centered"
    )

    apply_login_css()

    # If already logged in → immediate rerun
    if st.session_state.get("logged_in"):
        _safe_rerun()

    st.markdown("""
        <div style="text-align:center;">
            <h1>⚙️ SmartGear AI</h1>
            <p>Intelligent Gearbox Management & Maintenance System</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    # ================= LOGIN =================
    with tab1:

        with st.form("login_form"):
            username = st.text_input("Username or Email", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")

            submitted = st.form_submit_button("🚀 Login", use_container_width=True)

            if submitted:

                if not username or not password:
                    st.error("❌ Please fill in all fields")
                    st.stop()

                with st.spinner("🔄 Verifying credentials..."):
                    response = login_user(username, password)

                if response.status_code == 200:
                    data = response.json()

                    st.session_state.logged_in = True
                    st.session_state.token = data.get("access_token")
                    st.session_state.username = data.get("user", {}).get("username")
                    st.session_state.email = data.get("user", {}).get("email")
                    st.session_state.role = data.get("user", {}).get("role", "user")
                    st.session_state.user_id = data.get("user", {}).get("id")
                    st.session_state.current_tab = "Home"

                    # 🚀 Immediate rerun WITHOUT rendering UI
                    _safe_rerun()

                else:
                    try:
                        error_msg = response.json().get('error', 'Invalid credentials')
                    except Exception:
                        error_msg = f'Login failed ({response.status_code})'
                    if response.status_code == 403:
                        # pending approval or similar
                        st.warning(f"⏳ {error_msg}")
                    else:
                        st.error(f"❌ {error_msg}")

    # ================= SIGNUP =================
    with tab2:
        st.subheader("📝 Create New Account")
        
        with st.form("signup_form"):
            new_username = st.text_input("Username", key="signup_username")
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")

            # Role selection INSIDE form - all roles including SCM sub-roles
            role_options = {
                "user": "General User",
                "inventory_head": "Inventory Head",
                "maintenance_head": "Maintenance Head",
                "production_head": "Production Head",
                "scm_head": "SCM Head",
                "scm_planner": "SCM Planner",
                "scm_purchaser": "SCM Purchaser"
            }
            
            role = st.selectbox(
                "Role",
                list(role_options.keys()),
                format_func=lambda x: role_options.get(x, x),
                key="signup_role",
                help="Choose a role. If you select a special role, admin approval is required."
            )
            
            st.caption("⚠️ Users requesting any non-user role will require admin approval before login")

            submitted2 = st.form_submit_button("✨ Create Account", use_container_width=True)

        if submitted2:

            if not all([new_username, new_email, new_password, confirm_password]):
                st.error("❌ Please fill in all fields")
                st.stop()

            if new_password != confirm_password:
                st.error("❌ Passwords do not match")
                st.stop()

            with st.spinner("📝 Creating account..."):
                # all non-user roles use the role-aware endpoint
                if role == "user":
                    resp = signup_user(new_username, new_email, new_password)
                else:
                    from api_client import signup_user_with_role
                    resp = signup_user_with_role(new_username, new_email, new_password, role)

            if resp.status_code in (200, 201):
                data = resp.json()
                # backend returns msg 'signup_pending' when approval is needed
                if data.get("msg") == "signup_pending":
                    st.success("✅ Account created! Your request is pending admin approval. You will be able to log in once approved.")
                else:
                    st.success("✅ Account created successfully! You can now log in.")
            else:
                try:
                    err = resp.json().get("error")
                except Exception:
                    err = resp.text
                st.error(f"❌ Error: {err}")