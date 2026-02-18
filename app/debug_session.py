import streamlit as st

st.set_page_config(page_title="Debug Session State", layout="wide")

st.title("🔍 Debug: Session State")
st.markdown("---")

st.subheader("Current Session State:")
st.json(st.session_state)

st.markdown("---")

st.subheader("Key Values:")
cols = st.columns(4)
with cols[0]:
    logged_in = st.session_state.get('logged_in', False)
    st.metric("Logged In", "✓ Yes" if logged_in else "✗ No")
with cols[1]:
    token = st.session_state.get('token')
    token_len = len(token) if token else 0
    st.metric("Token Length", token_len)
with cols[2]:
    role = st.session_state.get('role', 'guest')
    st.metric("Role", role)
with cols[3]:
    username = st.session_state.get('username', 'guest')
    st.metric("Username", username)

st.markdown("---")

if st.session_state.get('token'):
    st.subheader("🔐 Token Details:")
    st.code(st.session_state.get('token')[:100] + "...", language="text")
    
    st.write("To verify token is correct, run in PowerShell:")
    st.code("""python debug_token.py""")
