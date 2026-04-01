import streamlit as st
from api_client import admin_get_heads, admin_delete_head


def _safe_rerun():
    """Safe Streamlit rerun."""
    if hasattr(st, "experimental_rerun"):
        try:
            st.experimental_rerun()
            return
        except Exception:
            pass
    st.stop()


def display_manage_heads():
    """Display and manage allocated department heads."""
    st.markdown('<div class="admin-header"><h2>👥 Manage Department Heads</h2></div>', unsafe_allow_html=True)
    st.markdown("View and manage all allocated department heads (Inventory, Maintenance, Production)")

    token = st.session_state.get('token')
    role = st.session_state.get('role', 'guest')
    username = st.session_state.get('username', 'guest')

    if not token or role != 'admin':
        st.error('🔒 Admin Access Required')
        st.write(f"You are logged in as: **{username}** (Role: {role})")
        st.stop()

    # Fetch heads
    resp = admin_get_heads(token)
    if resp.status_code != 200:
        st.error(f'Failed to load allocated heads: {resp.text}')
        return

    heads = resp.json()

    if not heads:
        st.info('ℹ️ No department heads allocated yet.')
    else:
        st.subheader(f"📊 Total Allocated Heads: {len(heads)}")
        st.markdown("---")
        
        # Show by role
        roles_dict = {
            'inventory_head': {'label': '📦 Inventory Heads', 'icon': '📦', 'count': 0},
            'maintenance_head': {'label': '🔧 Maintenance Heads', 'icon': '🔧', 'count': 0},
            'production_head': {'label': '⚙️ Production Heads', 'icon': '⚙️', 'count': 0},
            'scm_head': {'label': '🗂 SCM Heads', 'icon': '🗂', 'count': 0},
            'scm_planner': {'label': '📝 SCM Planners', 'icon': '📝', 'count': 0},
            'scm_purchaser': {'label': '📦 SCM Purchasers', 'icon': '📦', 'count': 0},
            'scm': {'label': '🗂 SCM (legacy)', 'icon': '🗂', 'count': 0},
        }
        
        for head in heads:
            if head['role'] in roles_dict:
                roles_dict[head['role']]['count'] += 1
        
        # Summary metrics
        # display first row of three
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Inventory", roles_dict['inventory_head']['count'])
        with col2:
            st.metric("🔧 Maintenance", roles_dict['maintenance_head']['count'])
        with col3:
            st.metric("⚙️ Production", roles_dict['production_head']['count'])
        # second row for SCM roles
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🗂 SCM Heads", roles_dict['scm_head']['count'])
        with col2:
            st.metric("📝 SCM Planners", roles_dict['scm_planner']['count'])
        with col3:
            st.metric("📦 SCM Purchasers", roles_dict['scm_purchaser']['count'])
        
        st.markdown("---")
        
        # Display heads by role
        for role_key, role_info in roles_dict.items():
            role_heads = [h for h in heads if h['role'] == role_key]
            if role_heads:
                st.subheader(f"{role_info['icon']} {role_info['label']}")
                for head in role_heads:
                    col1, col2, col3 = st.columns([3, 0.8, 0.6])
                    with col1:
                        status_badge = "✅ Approved" if head['is_approved'] else "⏳ Pending"
                        st.markdown(f"""
                        **{head['email']}** | {status_badge}
                        - Username: {head['username']}
                        - Joined: {head['created_at'][:10]}
                        """)
                    with col2:
                        st.text(f"ID: {head['id']}")
                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_head_{head['id']}", help="Remove this department head"):
                            if st.session_state.get(f"confirm_delete_{head['id']}", False):
                                # Confirmed - delete the head
                                resp = admin_delete_head(token, head['id'])
                                if resp.status_code == 200:
                                    st.success(f"✅ Department head {head['email']} removed successfully")
                                    st.session_state[f"confirm_delete_{head['id']}"] = False
                                    _safe_rerun()
                                else:
                                    st.error(f"❌ Failed to delete head: {resp.text}")
                                    st.session_state[f"confirm_delete_{head['id']}"] = False
                            else:
                                # First click - show confirmation
                                st.session_state[f"confirm_delete_{head['id']}"] = True
                                st.warning(f"⚠️ Click 'Delete' again to confirm removal of {head['email']}")
                                _safe_rerun()
                st.divider()
