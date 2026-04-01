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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;300;400;500;600;700;800&display=swap');
        
        * { 
            font-family: 'Inter', sans-serif;
        }
        
        html, body {
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
        }
        
        body {
            background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 50%, #2C5282 100%);
            background-attachment: fixed;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .main {
            background: transparent !important;
            padding: 0 !important;
        }
        
        .stApp {
            background: transparent;
        }
        
        /* MODERN GLASSMORPHISM CONTAINER */
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(30px);
            -webkit-backdrop-filter: blur(30px);
            border-radius: 20px;
            padding: 50px;
            box-shadow: 
                0 30px 60px rgba(0, 0, 0, 0.25),
                0 0 1px rgba(255, 255, 255, 0.5) inset,
                0 0 60px rgba(217, 119, 6, 0.1);
            max-width: 450px;
            margin: 0 auto;
            border: 1px solid rgba(255, 255, 255, 0.3);
            animation: fadeInUp 0.6s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .login-header {
            color: #1E3A5F;
            font-weight: 800;
            font-size: 2.2em;
            text-align: center;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #1E3A5F 0%, #D97706 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .login-subtitle {
            color: #6B7280;
            font-size: 1em;
            text-align: center;
            margin-bottom: 35px;
            font-weight: 400;
            letter-spacing: 0.3px;
        }
        
        /* MODERN INPUT FIELDS */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        input[type="text"],
        input[type="password"],
        input[type="email"],
        select {
            background: rgba(255, 255, 255, 0.6) !important;
            border: 1.5px solid rgba(217, 119, 6, 0.3) !important;
            border-radius: 12px !important;
            padding: 14px 16px !important;
            font-size: 0.95em !important;
            color: #1E3A5F !important;
            transition: all 0.3s ease !important;
            backdrop-filter: blur(10px) !important;
        }
        
        input[type="text"]:focus,
        input[type="password"]:focus,
        input[type="email"]:focus,
        select:focus {
            background: rgba(255, 255, 255, 0.95) !important;
            border-color: #D97706 !important;
            box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.1), 
                        inset 0 0 0 1px rgba(217, 119, 6, 0.2) !important;
            outline: none !important;
        }
        
        input::placeholder {
            color: rgba(107, 114, 128, 0.6) !important;
        }
        
        /* MODERN BUTTON */
        .stButton > button {
            background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 14px 32px !important;
            font-weight: 700 !important;
            font-size: 1em !important;
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
            box-shadow: 
                0 10px 25px rgba(217, 119, 6, 0.25),
                0 0 1px rgba(255, 255, 255, 0.5) inset !important;
            letter-spacing: 0.3px !important;
            width: 100% !important;
            cursor: pointer !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 
                0 15px 35px rgba(217, 119, 6, 0.35),
                0 0 1px rgba(255, 255, 255, 0.8) inset !important;
            background: linear-gradient(135deg, #B45309 0%, #D97706 100%) !important;
        }
        
        .stButton > button:active {
            transform: translateY(-1px) !important;
        }
        
        /* TAB STYLING */
        .stTabs {
            margin-bottom: 25px;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background: transparent !important;
            border-bottom: 2px solid rgba(217, 119, 6, 0.2) !important;
            gap: 16px !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: transparent !important;
            border-bottom: 3px solid transparent !important;
            color: #6B7280 !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            padding: 12px 8px !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: #D97706 !important;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            border-bottom-color: #D97706 !important;
            color: #D97706 !important;
            font-weight: 700 !important;
        }
        
        /* FORM LABELS */
        label {
            color: #374151 !important;
            font-weight: 600 !important;
            font-size: 0.9em !important;
            margin-bottom: 8px !important;
        }
        
        /* SUCCESS/ERROR MESSAGES */
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
        
        /* SPINNER */
        .stSpinner {
            text-align: center;
            color: #D97706 !important;
        }
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
        <div style="text-align:center; margin-bottom: 30px; animation: fadeInDown 0.6s ease-out;">
            <div style="
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
                backdrop-filter: blur(10px);
                padding: 30px;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                margin-bottom: 20px;
            ">
                <h1 style="
                    margin: 0;
                    font-size: 3.2em;
                    background: linear-gradient(135deg, #FFFFFF 0%, #FFE5CC 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    font-weight: 800;
                    letter-spacing: -0.8px;
                ">⚙️ SmartGear AI</h1>
                <p style="
                    margin: 12px 0 0 0;
                    color: rgba(255, 255, 255, 0.95);
                    font-size: 1.05em;
                    font-weight: 400;
                    letter-spacing: 0.3px;
                ">Intelligent Gearbox Management & Maintenance System</p>
                <p style="
                    margin: 8px 0 0 0;
                    color: rgba(217, 119, 6, 0.9);
                    font-size: 0.9em;
                    font-weight: 600;
                ">🚀 Enterprise-Grade Predictive Maintenance</p>
            </div>
        </div>
        
        <style>
            @keyframes fadeInDown {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    # ================= LOGIN =================
    with tab1:
        st.markdown("""
            <p style="text-align: center; color: #6B7280; font-size: 0.95em; margin-bottom: 20px;">
                🔒 Sign in with your credentials to access the system
            </p>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("**👤 Username or Email**")
            username = st.text_input("", placeholder="Enter your username or email address", key="login_username", label_visibility="collapsed")
            
            st.markdown("**🔐 Password**")
            password = st.text_input("", placeholder="Enter your password", type="password", key="login_password", label_visibility="collapsed")

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
        st.markdown("""
            <p style="text-align: center; color: #6B7280; font-size: 0.95em; margin-bottom: 20px;">
                ✨ Create a new account to get started
            </p>
        """, unsafe_allow_html=True)
        
        with st.form("signup_form"):
            st.markdown("**👤 Username**")
            new_username = st.text_input("", placeholder="Choose a unique username", key="signup_username", label_visibility="collapsed")
            
            st.markdown("**📧 Email Address**")
            new_email = st.text_input("", placeholder="your@email.com", key="signup_email", label_visibility="collapsed")
            
            st.markdown("**🔐 Password**")
            new_password = st.text_input("", placeholder="Create a strong password", type="password", key="signup_password", label_visibility="collapsed")
            
            st.markdown("**✔️ Confirm Password**")
            confirm_password = st.text_input("", placeholder="Re-enter your password", type="password", key="signup_confirm_password", label_visibility="collapsed")

            st.markdown("**👑 Select Your Role**")
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
                "",
                list(role_options.keys()),
                format_func=lambda x: role_options.get(x, x),
                key="signup_role",
                label_visibility="collapsed",
                help="Choose a role. If you select a special role, admin approval is required."
            )
            
            st.info("⚠️ **Note:** Users requesting any non-user role will require admin approval before login")

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