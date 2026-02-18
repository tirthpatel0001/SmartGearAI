import streamlit as st
from login import login_page
from dashboard2 import dashboard_page

st.set_page_config(page_title="SmartGear AI", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    dashboard_page()
else:
    login_page()
