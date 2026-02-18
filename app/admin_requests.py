import streamlit as st
from api_client import admin_get_pending, admin_approve, admin_reject


def _safe_rerun():
    """Safe rerun helper."""
    if hasattr(st, "experimental_rerun"):
        try:
            st.experimental_rerun()
            return
        except Exception:
            pass
    st.stop()


def display_pending_requests():
    """Display pending signup requests for admin."""
    st.markdown('<div class="admin-header"><h2>🧾 Pending Signup Requests</h2></div>', unsafe_allow_html=True)

    token = st.session_state.get('token')
    role = st.session_state.get('role', 'guest')
    username = st.session_state.get('username', 'guest')

    if not token or role != 'admin':
        st.error('🔒 Admin Access Required')
        st.write(f"You are logged in as: **{username}** (Role: {role})")
        st.write("To access this page, please log in with an **admin account**.")
        st.stop()

    resp = admin_get_pending(token)
    if resp.status_code != 200:
        st.error('Failed to load pending requests: ' + resp.text)
        return

    pending = resp.json()
    if not pending:
        st.info('ℹ️ No pending signup requests.')
    else:
        st.subheader(f"📋 {len(pending)} Pending Request(s)")
        st.markdown("---")
        for u in pending:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                with col1:
                    st.write(f"**{u['email']}**")
                with col2:
                    role_badge = f"<span style='background: #667eea; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.9em;'>{u['role']}</span>"
                    st.markdown(role_badge, unsafe_allow_html=True)
                with col3:
                    if st.button('✅ Approve', key=f"approve_{u['id']}", use_container_width=True):
                        r = admin_approve(token, u['id'])
                        if r.status_code == 200:
                            st.success(f"Approved {u['email']}")
                            _safe_rerun()
                        else:
                            st.error('Failed to approve: ' + r.text)
                with col4:
                    if st.button('❌ Reject', key=f"reject_{u['id']}", use_container_width=True):
                        r = admin_reject(token, u['id'])
                        if r.status_code == 200:
                            st.success(f"Rejected {u['email']}")
                            _safe_rerun()
                        else:
                            st.error('Failed to reject: ' + r.text)
            st.divider()
