import streamlit as st
from api_client import login_user, signup_user


def _safe_rerun():
    """Call Streamlit rerun if available, otherwise stop execution as a fallback."""
    if hasattr(st, "experimental_rerun"):
        try:
            st.experimental_rerun()
            return
        except Exception:
            pass
    # Fallback
    st.stop()


def apply_login_css():
    """Apply custom CSS styling to match main UI design"""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        
        * {
            font-family: 'Poppins', sans-serif;
        }
        
        :root {
            --primary-color: #FF6B6B;
            --secondary-color: #4ECDC4;
            --accent-color: #FFE66D;
            --dark-bg: #1a1a1a;
            --light-bg: #f8f9fa;
            --card-bg: #ffffff;
            --text-dark: #2c3e50;
            --text-light: #7f8c8d;
        }
        
        /* Main Background */
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        
        /* Login Container */
        .login-container {
            max-width: 500px;
            margin: 60px auto 0;
            background: white;
            border-radius: 20px;
            padding: 50px 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            backdrop-filter: blur(10px);
        }
        
        /* Hero Header */
        .hero-header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .hero-header h1 {
            background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 50%, #FFE66D 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.8em;
            font-weight: 700;
            margin: 0 0 10px 0;
        }
        
        .hero-header p {
            color: #7f8c8d;
            font-size: 0.95em;
            margin: 0;
            font-weight: 300;
        }
        
        /* Tab Container */
        .tab-container {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        /* Input Section */
        .input-section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            border-left: 4px solid #FF6B6B;
        }
        
        /* Form Input Styling */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {
            border: 2px solid #e0e0e0 !important;
            border-radius: 10px !important;
            padding: 12px 15px !important;
            font-size: 0.95em !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border: 2px solid #FF6B6B !important;
            box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.1) !important;
        }
        
        /* Button Styling */
        .stButton > button {
            width: 100%;
            padding: 12px 24px !important;
            font-size: 1em !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            border: none !important;
            background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%) !important;
            color: white !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3) !important;
            margin-top: 10px;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 25px rgba(255, 107, 107, 0.4) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
        }
        
        /* Alert Messages */
        .stSuccess {
            background-color: #d4edda;
            border-radius: 10px;
            border-left: 4px solid #28a745;
        }
        
        .stError {
            background-color: #f8d7da;
            border-radius: 10px;
            border-left: 4px solid #dc3545;
        }
        
        .stInfo {
            background-color: #d1ecf1;
            border-radius: 10px;
            border-left: 4px solid #17a2b8;
        }
        
        /* Form Labels */
        .stTextInput > label,
        .stSelectbox > label {
            color: #2c3e50 !important;
            font-weight: 600 !important;
            font-size: 0.95em !important;
        }
        
        /* Divider */
        hr {
            margin: 20px 0;
            border: none;
            border-top: 1px solid #e0e0e0;
        }
        
        /* Security Badge */
        .security-badge {
            text-align: center;
            margin-top: 20px;
            color: #7f8c8d;
            font-size: 0.85em;
        }
        </style>
    """, unsafe_allow_html=True)


def login_page():
    """Main login page with improved UI"""
    apply_login_css()
    st.set_page_config(
        page_title="SmartGear AI - Login",
        page_icon="⚙️",
        layout="centered"
    )
    
    # Header
    st.markdown("""
        <div class="hero-header">
            <h1>⚙️ SmartGear AI</h1>
            <p>Intelligent Gearbox Management & Maintenance System</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Tab selection
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    # ==================== LOGIN TAB ====================
    with tab1:
        st.markdown("### Welcome Back!")
        st.markdown("Enter your credentials to access SmartGear AI")
        
        username = st.text_input(
            "Username or Email",
            placeholder="enter your username or email",
            key="login_username"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="enter your password",
            key="login_password"
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🚀 Login", use_container_width=True, key="login_btn"):
                if not username or not password:
                    st.error("❌ Please fill in all fields")
                else:
                    with st.spinner("🔄 Verifying credentials..."):
                        response = login_user(username, password)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.logged_in = True
                        st.session_state.token = data.get("access_token")
                        st.session_state.username = data.get("user", {}).get("username")
                        st.session_state.role = data.get("user", {}).get("role", "user")
                        st.success("✅ Login successful! Redirecting...")
                        _safe_rerun()
                    else:
                        try:
                            error_msg = response.json().get('error', 'Invalid credentials')
                        except Exception:
                            error_msg = f'Login failed (Status: {response.status_code}) - Invalid credentials'
                        st.error(f"❌ {error_msg}")
        
        with col2:
            st.markdown("&nbsp;")
            st.markdown("&nbsp;")
            st.write("")
        
        # Security badge
        st.markdown("""
            <div class="security-badge">
                🔒 Your credentials are encrypted and secure
            </div>
        """, unsafe_allow_html=True)
    
    # ==================== SIGNUP TAB ====================
    with tab2:
        st.markdown("### Create New Account")
        st.markdown("Join SmartGear AI and start managing your gearbox efficiently")
        
        new_username = st.text_input(
            "Username",
            placeholder="choose a username",
            key="signup_username"
        )
        new_email = st.text_input(
            "Email Address",
            placeholder="enter your email",
            key="signup_email"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            role = st.selectbox(
                "Role",
                ["user", "inventory_head", "maintenance_head", "production_head"],
                index=0,
                key="signup_role"
            )
        
        with col2:
            st.write("")
            st.write("")
        
        new_password = st.text_input(
            "Password",
            type="password",
            placeholder="create a strong password",
            key="signup_password"
        )
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="repeat your password",
            key="signup_confirm_password"
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("✨ Create Account", use_container_width=True, key="signup_btn"):
                # Validate inputs
                if not all([new_username, new_email, new_password, confirm_password]):
                    st.error("❌ Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    with st.spinner("📝 Creating account..."):
                        # use role-aware signup
                        if role == "user":
                            resp = signup_user(new_username, new_email, new_password)
                        else:
                            from api_client import signup_user_with_role
                            resp = signup_user_with_role(new_username, new_email, new_password, role=role)
                        
                        if resp.status_code in (200, 201):
                            data = resp.json()
                            if data.get("msg") == "signup_pending":
                                st.info("⏳ Signup submitted — pending admin approval.")
                            else:
                                st.success("✅ Account created successfully! You can now log in.")
                        else:
                            try:
                                err = resp.json().get("error")
                            except Exception:
                                err = resp.text
                            st.error(f"❌ Error: {err}")
        
        st.markdown("""
            <div class="security-badge">
                🔒 Account data is encrypted and never shared
            </div>
        """, unsafe_allow_html=True)
