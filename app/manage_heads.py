import streamlit as st
from api_client import admin_get_heads


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
        }
        
        for head in heads:
            if head['role'] in roles_dict:
                roles_dict[head['role']]['count'] += 1
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Inventory", roles_dict['inventory_head']['count'])
        with col2:
            st.metric("🔧 Maintenance", roles_dict['maintenance_head']['count'])
        with col3:
            st.metric("⚙️ Production", roles_dict['production_head']['count'])
        
        st.markdown("---")
        
        # Display heads by role
        for role_key, role_info in roles_dict.items():
            role_heads = [h for h in heads if h['role'] == role_key]
            if role_heads:
                st.subheader(f"{role_info['icon']} {role_info['label']}")
                for head in role_heads:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        status_badge = "✅ Approved" if head['is_approved'] else "⏳ Pending"
                        st.markdown(f"""
                        **{head['email']}** | {status_badge}
                        - Username: {head['username']}
                        - Joined: {head['created_at'][:10]}
                        """)
                    with col2:
                        st.text(f"ID: {head['id']}")
                st.divider()
