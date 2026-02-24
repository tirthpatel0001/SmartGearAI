import streamlit as st
import requests
from api_client import (
    API_URL,
    get_inventory_items,
    create_inventory_item,
    get_material_requests,
    create_material_request,
    get_purchase_requests,
    get_assigned_purchase_requests,
    create_purchase_request,
    delete_purchase_request,
    delete_all_purchase_requests,
    update_purchase_request_status,
    get_purchase_orders,
    create_purchase_order,
    get_scrap_records,
    create_scrap_record,
    get_notifications,
    mark_notification_read,
)

# helper utilities

def _safe_rerun():
    # some Streamlit versions removed experimental_rerun
    if hasattr(st, "experimental_rerun"):
        try:
            st.experimental_rerun()
            return
        except Exception:
            pass
    st.stop()


def display_inventory_management():
    st.markdown('<div class="scm-header"><h2>📋 Inventory Management</h2></div>', unsafe_allow_html=True)
    role = st.session_state.get('role', 'guest')
    if role not in ['inventory_head', 'scm_head']:
        st.error('🔒 Only inventory heads or SCM heads can manage inventory here')
        return

    st.info('Add or update items in the central inventory')
    # fetch existing items to populate dropdown
    items = []
    try:
        resp_items = get_inventory_items(st.session_state.get('token'))
        if resp_items.status_code == 200:
            items = resp_items.json()
    except Exception:
        pass

    # helper to send update / create payload
    def save_item(payload):
        resp_inv = create_inventory_item(st.session_state.get('token'), payload)
        if resp_inv.status_code in (200, 201):
            st.success('Inventory item saved')
            _safe_rerun()
        else:
            st.error(f'Error: {resp_inv.text}')

    with st.expander('🛠 Update existing item'):
        if items:
            sel = st.selectbox('Select item', options=items, format_func=lambda i: f"{i.get('item_code')} - {i.get('name')}")
            if sel:
                name = sel.get('name')
                code = sel.get('item_code')
                category = sel.get('category') or ''
                qty = st.number_input('Quantity', min_value=0.0, step=0.1, value=sel.get('quantity', 0.0))
                if st.button('Save changes', key='update_item'):
                    payload = {'item_code': code, 'name': name, 'quantity': qty, 'category': category}
                    save_item(payload)
        else:
            st.info('No inventory items yet.')

    with st.expander('➕ Add new item'):
        new_code = st.text_input('Item Code')
        new_name = st.text_input('Item Name')
        new_category = st.text_input('Category (e.g. raw material, component)')
        new_qty = st.number_input('Starting Quantity', min_value=0.0, step=0.1, value=0.0)
        if st.button('Add item', key='add_item'):
            if not new_code or not new_name:
                st.error('Code and name required')
            else:
                payload = {'item_code': new_code, 'name': new_name, 'quantity': new_qty, 'category': new_category}
                save_item(payload)

    # show current inventory
    items = []
    try:
        resp = get_inventory_items(st.session_state.get('token'))
        if resp.status_code == 200:
            items = resp.json()
    except Exception:
        pass

    if items:
        st.subheader('📦 Current Inventory')
        st.table(items)
    else:
        st.info('No inventory items to display')

    # debug counts also available
    with st.expander('🔍 Inventory counts (debug)'):
        try:
            inv = get_inventory_items(st.session_state.get('token')).json()
            st.write(f"Inventory items: {len(inv)}")
        except Exception as e:
            st.write(f"Error retrieving inventory: {e}")




def display_scm_dashboard():
    st.markdown('<div class="scm-header"><h2>🛒 SCM / Inventory Dashboard</h2></div>', unsafe_allow_html=True)
    role = st.session_state.get('role', 'guest')
    username = st.session_state.get('username', 'guest')

    # inventory head, scm head, or planner can access this dashboard
    if role not in ['inventory_head', 'scm_head', 'scm_planner']:
        st.error('🔒 SCM dashboard is available only to inventory head, SCM head or SCM planner')
        return

    st.info('Overview of inventory levels and scrap records')

    # show inventory items
    items = []
    try:
        resp = get_inventory_items(st.session_state.get('token'))
        if resp.status_code == 200:
            items = resp.json()
    except Exception:
        pass

    if items:
        st.subheader('📦 Current Inventory')
        st.table(items)
    else:
        st.info('No inventory items to display')

    # show scrap records
    try:
        resp = get_scrap_records(st.session_state.get('token'))
        if resp.status_code == 200:
            recs = resp.json()
            if recs:
                st.subheader('🗑 Scrap Records')
                st.table(recs)
    except Exception:
        pass

    # debug: show counts of SCM tables
    with st.expander('🔍 View table counts (debug)'):
        try:
            inv = get_inventory_items(st.session_state.get('token')).json()
            mr = get_material_requests(st.session_state.get('token')).json()
            pr = get_purchase_requests(st.session_state.get('token')).json()
            po = get_purchase_orders(st.session_state.get('token')).json()
            sc = get_scrap_records(st.session_state.get('token')).json()
            st.write(f"Inventory items: {len(inv)}")
            st.write(f"Material requests: {len(mr)}")
            st.write(f"Purchase requests: {len(pr)}")
            st.write(f"Purchase orders: {len(po)}")
            st.write(f"Scrap records: {len(sc)}")
        except Exception as e:
            st.write(f"Error retrieving counts: {e}")

    st.markdown('---')
    st.write('Use the other modules from the sidebar to raise requests or orders.')


def display_notifications():
    st.markdown('<div class="scm-header"><h2>🔔 Notifications</h2></div>', unsafe_allow_html=True)
    role = st.session_state.get('role', 'guest')
    token = st.session_state.get('token')
    if not token:
        st.error('🔒 Please login to view notifications')
        return
    try:
        resp = get_notifications(token)
        if resp.status_code == 200:
            notes = resp.json()
            if notes:
                for n in notes:
                    status = '✅' if n.get('seen') else '🔴'
                    st.write(f"{status} {n.get('message')} (related {n.get('related_type')} {n.get('related_id')})")
                    if not n.get('seen'):
                        if st.button(f"Mark read #{n.get('id')}", key=f"note_{n.get('id')}"):
                            mark_notification_read(token, n.get('id'))
                            _safe_rerun()
            else:
                st.info('No notifications')
        else:
            st.error(f"Error fetching notifications: {resp.text}")
    except Exception as e:
        st.error(f"Exception retrieving notifications: {e}")

    # scrap record entry
    if role in ['inventory_head', 'production_head', 'scm_head']:
        st.markdown('---')
        st.subheader('🗑 Report Scrap Item')
        with st.form('scrap_form'):
            dept = st.text_input('Department', value=role.replace('_', ' ').title())
            desc = st.text_area('Description of scrap')
            qty = st.number_input('Quantity', min_value=0.0, step=0.1)
            submitted2 = st.form_submit_button('Submit Scrap Report')
            if submitted2:
                payload = {
                    'department': dept,
                    'description': desc,
                    'quantity': qty,
                    'created_by': st.session_state.get('user_id'),
                }
                resp = create_scrap_record(st.session_state.get('token'), payload)
                if resp.status_code in (200, 201):
                    st.success('Scrap record submitted')
                else:
                    st.error(f'Error: {resp.text}')



def display_production_requests():
    st.markdown('<div class="scm-header"><h2>📝 Material Requests (Production)</h2></div>', unsafe_allow_html=True)
    role = st.session_state.get('role', 'guest')
    if role != 'production_head':
        st.error('🔒 Only production head can create material requests')
        return

    token = st.session_state.get('token')
    
    # Create tabs: New Request, My Requests, Approved Requests
    tab1, tab2, tab3 = st.tabs(['Create Request', 'My Requests', 'Approved Requests'])
    
    with tab1:
        # fetch inventory items for dropdown
        inv_items = []
        try:
            resp = get_inventory_items(token)
            if resp.status_code == 200:
                inv_items = resp.json()
        except Exception:
            pass

        # session state list of lines
        if 'mr_lines' not in st.session_state:
            st.session_state.mr_lines = []

        st.subheader('Current Request Lines')
        if st.session_state.mr_lines:
            # display as table for a bill-like appearance
            import pandas as _pd
            df = _pd.DataFrame([
                {'Item': l['name'], 'Quantity': l['qty']} for l in st.session_state.mr_lines
            ])
            st.table(df)
        else:
            st.info('Add items below')

        st.markdown('---')
        st.subheader('Add Item to Request')
        cols = st.columns([2, 1, 1])
        with cols[0]:
            item_choice = st.selectbox(
                'Item',
                options=inv_items,
                format_func=lambda i: f"{i.get('item_code')} - {i.get('name')}",
                key='mr_item_choice'
            )
        with cols[1]:
            qty_choice = st.number_input('Qty', min_value=0.0, key='mr_qty_choice')
        with cols[2]:
            if st.button('➕ Add', key='mr_add_btn'):
                if item_choice and qty_choice > 0:
                    selected = item_choice
                    st.session_state.mr_lines.append({'id': selected['id'], 'name': selected['name'], 'qty': qty_choice})
                    _safe_rerun()

        # submit full request when ready
        if st.button('✅ Submit Request', key='mr_submit_btn'):
            if st.session_state.mr_lines:
                payload = {
                    'department': 'production',
                    'requested_by': st.session_state.get('user_id'),
                    'items': [{'item_id': l['id'], 'quantity': l['qty']} for l in st.session_state.mr_lines]
                }
                resp = create_material_request(token, payload)
                if resp.status_code in (200, 201):
                    st.success('Material request submitted')
                    data = resp.json()
                    result = data.get('result', {})
                    if result:
                        st.subheader('Material Request Result')
                        # Show available items
                        if result.get('available'):
                            st.success('The following items are available in inventory and will be sent to you once inventory head approves:')
                            st.table(result['available'])
                        # Show unavailable items
                        if result.get('to_order'):
                            st.warning('The following items are not available in inventory and have been sent to SCM planner for purchase:')
                            st.table(result['to_order'])
                    st.session_state.mr_lines = []
                    _safe_rerun()
                else:
                    st.error(f'Error: {resp.text}')
    
    with tab2:
        # Show past material requests by this user
        try:
            resp_mys = get_material_requests(token)
            if resp_mys.status_code == 200:
                all_mrs = resp_mys.json()
                mymrs = [r for r in all_mrs if r.get('requested_by') == st.session_state.get('user_id')]
                if not mymrs:
                    st.info('No material requests created yet.')
                else:
                    st.subheader(f'Your Material Requests ({len(mymrs)})')
                    for mr in mymrs:
                        with st.expander(f"MR #{mr['id']} - Status: {mr.get('status')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Requested At:** {mr.get('requested_at')}")
                            with col2:
                                st.write(f"**Status:** {mr.get('status')}")
                            
                            st.markdown('**Items:**')
                            for it in mr.get('items', []):
                                line = f"- {it.get('item_name')} qty {it.get('quantity')}"
                                alloc = it.get('quantity_allocated')
                                toord = it.get('quantity_to_order')
                                if alloc is not None and alloc > 0:
                                    line += f" (allocated {alloc})"
                                if toord is not None and toord > 0:
                                    line += f" (to order {toord})"
                                st.write(line)
        except Exception as e:
            st.error(f'Error fetching requests: {str(e)}')
    
    with tab3:
        # Show approved requests
        try:
            resp_all = get_material_requests(token)
            if resp_all.status_code == 200:
                all_mrs = resp_all.json()
                mymrs = [r for r in all_mrs if r.get('requested_by') == st.session_state.get('user_id') and r.get('status') == 'inventory_approved']
                
                if not mymrs:
                    st.info('No approved requests yet.')
                else:
                    st.subheader(f'Approved Requests ({len(mymrs)})')
                    for mr in mymrs:
                        with st.expander(f"MR #{mr['id']} - APPROVED ✓"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write(f"**Requested At:** {mr.get('requested_at')}")
                            with col2:
                                st.write(f"**Approved At:** {mr.get('processed_at', 'N/A')}")
                            with col3:
                                st.write(f"**Status:** ✓ Approved")
                            
                            st.markdown('**Items Approved for Dispatch:**')
                            for it in mr.get('items', []):
                                alloc = it.get('quantity_allocated') or 0
                                if alloc > 0:
                                    st.write(f"✓ {it.get('item_name')} - {alloc} units ready for dispatch")
                            
                            if any((item.get('quantity_to_order') or 0) > 0 for item in (mr.get('items') or [])):
                                st.markdown('**Items Being Ordered:**')
                                for it in mr.get('items', []):
                                    toord = it.get('quantity_to_order') or 0
                                    if toord > 0:
                                        st.write(f"⏳ {it.get('item_name')} - {toord} units (on order via SCM)")
        except Exception as e:
            st.error(f'Error: {str(e)}')


# For backward compatibility with main menu option

def display_purchase_requests():
    """Show a purchase request interface appropriate for the current role.

    - production_head: identical to production/material request view (with both
      MR and PR sections).
    - scm_planner or scm_head: only the purchase request list/form.
    """
    role = st.session_state.get('role', 'guest')
    if role == 'production_head':
        display_production_requests()
        return
    if role in ('scm_planner', 'scm_head'):
        st.markdown('<div class="scm-header"><h2>PR Assignment to Purchasers</h2></div>', unsafe_allow_html=True)
        token = st.session_state.get('token')
        
        try:
            resp = get_purchase_requests(token)
            if resp.status_code == 200:
                prs = resp.json()
                pending_prs = [pr for pr in prs if not pr.get('purchaser_email')]
                assigned_prs = [pr for pr in prs if pr.get('purchaser_email') and pr.get('status') != 'po_uploaded']
                
                if not pending_prs and not assigned_prs:
                    st.info('No purchase requests.')
                else:
                    if pending_prs:
                        st.subheader('Pending PRs - Assign to Purchaser')
                        col1, col2 = st.columns([5, 1])
                        with col2:
                            if st.button('Delete All Pending', key='del_pending'):
                                for pr in pending_prs:
                                    delete_purchase_request(token, pr.get('id'))
                                st.success('Deleted all pending PRs')
                                _safe_rerun()
                        
                        for pr in pending_prs:
                            with st.expander(f"PR #{pr.get('id')} - MR #{pr.get('material_request_id')}"):
                                st.write(f"**Created:** {pr.get('created_at')}")
                                st.markdown('**Items:**')
                                for item in pr.get('items', []):
                                    st.write(f"  - {item.get('item_name')} x {item.get('quantity')}")
                                
                                st.markdown('---')
                                col1, col2, col3 = st.columns([2, 1, 1])
                                with col1:
                                    email = st.text_input('Purchaser Email', key=f'email_{pr.get("id")}', placeholder='purchaser@company.com')
                                with col2:
                                    if st.button('Assign', key=f'assign_{pr.get("id")}'):
                                        if email:
                                            update_resp = update_purchase_request_status(token, pr.get('id'), 'assigned', purchaser_email=email)
                                            if update_resp.status_code == 200:
                                                st.success(f'Assigned to {email}')
                                                _safe_rerun()
                                            else:
                                                st.error('Failed to assign')
                                        else:
                                            st.error('Enter email')
                                with col3:
                                    if st.button('Delete', key=f'del_{pr.get("id")}'):
                                        delete_purchase_request(token, pr.get('id'))
                                        st.success('Deleted')
                                        _safe_rerun()
                    
                    if assigned_prs:
                        st.markdown('---')
                        st.subheader('Assigned PRs')
                        col1, col2 = st.columns([5, 1])
                        with col2:
                            if st.button('Delete All Assigned', key='del_assigned'):
                                for pr in assigned_prs:
                                    delete_purchase_request(token, pr.get('id'))
                                st.success('Deleted all assigned')
                                _safe_rerun()
                        
                        for pr in assigned_prs:
                            with st.expander(f"PR #{pr.get('id')} - {pr.get('purchaser_email')}"):
                                st.write(f"**Status:** {pr.get('status')}")
                                st.write(f"**Created:** {pr.get('created_at')}")
                                st.markdown('**Items:**')
                                for item in pr.get('items', []):
                                    st.write(f"  - {item.get('item_name')} x {item.get('quantity')}")
                                st.markdown('---')
                                if st.button('Delete', key=f'del_asgn_{pr.get("id")}'):
                                    delete_purchase_request(token, pr.get('id'))
                                    st.success('Deleted')
                                    _safe_rerun()
        except Exception as e:
            st.error(f'Error: {str(e)}')
        
        return
    if role == 'scm_purchaser':
        st.markdown('<div class="scm-header"><h2>� Purchase Requests Assigned to You</h2></div>', unsafe_allow_html=True)
        token = st.session_state.get('token')
        purchaser_email = st.session_state.get('email')
        
        try:
            resp = get_assigned_purchase_requests(token)
            if resp.status_code == 200:
                prs = resp.json()
                
                # Split into pending and uploaded POs
                pending_prs = [pr for pr in prs if pr.get('status') != 'po_uploaded']
                uploaded_prs = [pr for pr in prs if pr.get('status') == 'po_uploaded']
                
                if not pending_prs and not uploaded_prs:
                    st.info('✅ No purchase requests assigned to you yet.')
                else:
                    # Show pending PRs
                    if pending_prs:
                        st.subheader('📥 Pending Purchase Requests')
                        col1, col2 = st.columns([5, 1])
                        with col2:
                            if st.button('🗑️ Delete All Pending', key='delete_all_pending_prs'):
                                for pr in pending_prs:
                                    delete_purchase_request(token, pr.get('id'))
                                st.success('All pending PRs deleted')
                                _safe_rerun()
                        st.markdown('---')
                    
                    # Show uploaded POs
                    if uploaded_prs:
                        st.subheader('📦 Uploaded Purchase Orders')
                        col1, col2 = st.columns([5, 1])
                        with col2:
                            if st.button('🗑️ Delete All Orders', key='delete_all_orders'):
                                for pr in uploaded_prs:
                                    delete_purchase_request(token, pr.get('id'))
                                st.success('All orders deleted')
                                _safe_rerun()
                    
                    # Display pending PRs
                    for pr in pending_prs:
                        with st.expander(f"PR #{pr.get('id')} - MR #{pr.get('material_request_id', 'N/A')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Created By:** {pr.get('created_by')}")
                                st.write(f"**Created At:** {pr.get('created_at')}")
                            with col2:
                                st.write(f"**Status:** {pr.get('status', 'draft')}")
                            
                            st.markdown('**Items to Purchase:**')
                            for item in pr.get('items', []):
                                st.write(f"- {item.get('item_name')} × {item.get('quantity')}")
                            
                            st.markdown('---')
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                st.write('**Upload Purchase Order (PO):**')
                                uploaded_file = st.file_uploader(
                                    f"Upload PO for PR #{pr.get('id')}",
                                    type=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'],
                                    key=f"upload_po_{pr.get('id')}"
                                )
                                if uploaded_file:
                                    # Update PR status to po_uploaded
                                    update_resp = update_purchase_request_status(token, pr.get('id'), 'po_uploaded')
                                    if update_resp.status_code == 200:
                                        st.success(f"✅ PO uploaded: {uploaded_file.name}")
                                        _safe_rerun()
                                    else:
                                        st.error(f'Error updating status: {update_resp.text}')
                            with col2:
                                st.write('')
                            with col3:
                                if st.button(f'🗑️ Delete', key=f'delete_pr_{pr.get("id")}'):
                                    del_resp = delete_purchase_request(token, pr.get('id'))
                                    if del_resp.status_code in (200, 204):
                                        st.success('PR deleted')
                                        _safe_rerun()
                                    else:
                                        st.error(f'Failed to delete: {del_resp.text}')
                    
                    # Display uploaded POs
                    for pr in uploaded_prs:
                        with st.expander(f"PO #{pr.get('id')} - MR #{pr.get('material_request_id', 'N/A')} ✅"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Created By:** {pr.get('created_by')}")
                                st.write(f"**Created At:** {pr.get('created_at')}")
                            with col2:
                                st.write(f"**Status:** PO Uploaded ✅")
                            
                            st.markdown('**Items:**')
                            for item in pr.get('items', []):
                                st.write(f"- {item.get('item_name')} × {item.get('quantity')}")
                            
                            st.markdown('---')
                            if st.button(f'🗑️ Delete', key=f'delete_order_{pr.get("id")}'):
                                del_resp = delete_purchase_request(token, pr.get('id'))
                                if del_resp.status_code in (200, 204):
                                    st.success('Order deleted')
                                    _safe_rerun()
                                else:
                                    st.error(f'Failed to delete: {del_resp.text}')
            else:
                st.error(f'Error fetching assigned PRs: {resp.text}')
        except Exception as e:
            st.error(f'Error: {str(e)}')
        return
    # other roles cannot access this view
    st.error('🔒 Only production head, SCM planner, SCM head or SCM purchaser can view purchase requests')


def display_purchase_orders():
    role = st.session_state.get('role', 'guest')
    # SCM Purchaser view moved to display_assigned_prs()
    def display_assigned_prs():
        role = st.session_state.get('role', 'guest')
        if role == 'scm_purchaser':
            st.markdown('<div class="scm-header"><h2>📝 Purchase Requests Assigned to You</h2></div>', unsafe_allow_html=True)
            token = st.session_state.get('token')
            prs = []
            resp = get_purchase_requests(token)
            if resp.status_code == 200:
                prs = resp.json()
            submitted_prs = [pr for pr in prs if pr.get('status') == 'submitted']
            if submitted_prs:
                for pr in submitted_prs:
                    st.markdown(f"### PR #{pr.get('id')} (Material Request ID: {pr.get('material_request_id')})")
                    st.write(f"**Requested By:** {pr.get('created_by')}")
                    st.write(f"**Status:** {pr.get('status')}")
                    # Show items in a nice table
                    import pandas as pd
                    items = pr.get('items', [])
                    if items:
                        item_df = pd.DataFrame([
                            {'Item Name': it.get('item_name'), 'Quantity': it.get('quantity')} for it in items
                        ])
                        st.table(item_df)
                    # Upload PO option
                    st.write('**Upload Purchase Order (PO):**')
                    uploaded_file = st.file_uploader(f"Upload PO for PR #{pr.get('id')}", type=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'], key=f"upload_po_{pr.get('id')}")
                    if uploaded_file:
                        st.success(f"PO uploaded for PR #{pr.get('id')}: {uploaded_file.name}")
                    st.markdown('---')
            else:
                st.info('No purchase requests assigned to you.')
            return
    # Optionally, keep the old view for SCM Head or others
    if role == 'scm_head':
        st.markdown('<div class="scm-header"><h2>📦 Purchase Order Module</h2></div>', unsafe_allow_html=True)
        token = st.session_state.get('token')
        pos = []
        resp = get_purchase_orders(token)
        if resp.status_code == 200:
            pos = resp.json()
        if pos:
            st.subheader('Existing Purchase Orders')
            for po in pos:
                st.markdown(f"**PO {po['id']}** (status: {po.get('status','open')})")
                for it in po.get('items', []):
                    st.write(f"- {it.get('item_name')} (qty {it.get('quantity')})")
                if po.get('status') == 'open':
                    if st.button(f"Receive order {po['id']}", key=f"recv_{po['id']}"):
                        resp = requests.post(
                            f"{API_URL}/purchase_orders/{po['id']}/receive",
                            headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
                        )
                        if resp.status_code == 200:
                            st.success('Order marked received; inventory updated')
                            _safe_rerun()
                        else:
                            st.error(f"Error receiving order: {resp.text}")
                st.markdown('---')
        else:
            st.info('No purchase orders')
