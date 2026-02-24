"""Inventory Head Portal - Approve and process material requests with available inventory."""

import streamlit as st
from api_client import (
    get_material_requests,
    process_material_request,
    get_notifications,
    mark_notification_read
)


def _safe_rerun():
    """Safe rerun helper."""
    if hasattr(st, "experimental_rerun"):
        try:
            st.experimental_rerun()
            return
        except Exception:
            pass
    st.stop()


def display_approve_requests():
    """Display material requests that need inventory approval."""
    st.markdown('<div class="scm-header"><h2>Approve Inventory Requests</h2></div>', unsafe_allow_html=True)
    
    role = st.session_state.get('role', 'guest')
    token = st.session_state.get('token')
    
    if role != 'inventory_head':
        st.error('Access Denied: Only Inventory Head can approve requests')
        return
    
    try:
        # Fetch all material requests
        resp = get_material_requests(token)
        if resp.status_code != 200:
            st.error(f'Error fetching requests: {resp.text}')
            return
        
        all_mrs = resp.json()
        
        # Filter for requests that:
        # 1. Have items with quantity_allocated > 0 (items available in inventory)
        # 2. NOT already processed (status != 'inventory_approved')
        pending_mrs = []
        for mr in all_mrs:
            if mr.get('status') == 'inventory_approved':
                continue
            
            has_allocated_items = False
            for item in (mr.get('items') or []):
                if (item.get('quantity_allocated') or 0) > 0:
                    has_allocated_items = True
                    break
            
            if has_allocated_items:
                pending_mrs.append(mr)
        
        # Display tabs: Pending Approvals, Approved Requests
        tab1, tab2 = st.tabs(['Pending Approvals', 'Approved Requests'])
        
        with tab1:
            if not pending_mrs:
                st.info('No requests pending approval.')
            else:
                st.subheader(f'Pending Approvals ({len(pending_mrs)})')
                
                # Delete all button
                col1, col2 = st.columns([5, 1])
                with col2:
                    if st.button('Mark All Approved', key='mark_all_approved', use_container_width=True):
                        for mr in pending_mrs:
                            approve_resp = process_material_request(token, mr.get('id'))
                            if approve_resp.status_code not in (200, 201):
                                st.error(f"Failed to approve MR #{mr.get('id')}: {approve_resp.text}")
                        st.success(f'Approved all {len(pending_mrs)} requests')
                        _safe_rerun()
                
                st.markdown('---')
                
                for mr in pending_mrs:
                    with st.expander(f"MR #{mr.get('id')} - {mr.get('department')} - Requested by {mr.get('requested_by')}"):
                        # Show request details
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Request ID:** {mr.get('id')}")
                            st.write(f"**Department:** {mr.get('department')}")
                        with col2:
                            st.write(f"**Requested By:** {mr.get('requested_by')}")
                            st.write(f"**Requested At:** {mr.get('requested_at')}")
                        with col3:
                            st.write(f"**Status:** {mr.get('status', 'pending')}")
                        
                        st.markdown('**Items with Available Inventory:**')
                        
                        # Show only allocated items
                        allocated_items = []
                        for item in (mr.get('items') or []):
                            qty_allocated = item.get('quantity_allocated') or 0
                            if qty_allocated > 0:
                                allocated_items.append(item)
                                st.write(f"  ✓ {item.get('item_name')} - {qty_allocated} units (from inventory)")
                        
                        # Show any items that need to be ordered
                        to_order_items = []
                        for item in (mr.get('items') or []):
                            qty_to_order = item.get('quantity_to_order') or 0
                            if qty_to_order > 0:
                                to_order_items.append(item)
                                st.write(f"  ⏳ {item.get('item_name')} - {qty_to_order} units (on order via SCM)")
                        
                        st.markdown('---')
                        
                        # Approval button
                        col1, col2 = st.columns([3, 1])
                        with col2:
                            if st.button('✓ Approve', key=f'approve_{mr.get("id")}', use_container_width=True):
                                approve_resp = process_material_request(token, mr.get('id'))
                                if approve_resp.status_code in (200, 201):
                                    st.success('Request approved! Items will be deducted from inventory.')
                                    _safe_rerun()
                                else:
                                    st.error(f'Error: {approve_resp.text}')
        
        with tab2:
            # Show approved requests
            approved_mrs = [mr for mr in all_mrs if mr.get('status') == 'inventory_approved']
            
            if not approved_mrs:
                st.info('No approved requests yet.')
            else:
                st.subheader(f'Approved Requests ({len(approved_mrs)})')
                
                for mr in approved_mrs:
                    with st.expander(f"MR #{mr.get('id')} - {mr.get('department')} ✓"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Request ID:** {mr.get('id')}")
                            st.write(f"**Department:** {mr.get('department')}")
                        with col2:
                            st.write(f"**Requested By:** {mr.get('requested_by')}")
                            st.write(f"**Requested At:** {mr.get('requested_at')}")
                        with col3:
                            st.write(f"**Processed At:** {mr.get('processed_at', 'N/A')}")
                            st.write(f"**Status:** ✓ Approved")
                        
                        st.markdown('**Items Allocated:**')
                        for item in (mr.get('items') or []):
                            if (item.get('quantity_allocated') or 0) > 0:
                                st.write(f"  - {item.get('item_name')} - {item.get('quantity_allocated')} units")
                        
                        if any((item.get('quantity_to_order') or 0) > 0 for item in (mr.get('items') or [])):
                            st.markdown('**Items on Order:**')
                            for item in (mr.get('items') or []):
                                if (item.get('quantity_to_order') or 0) > 0:
                                    st.write(f"  - {item.get('item_name')} - {item.get('quantity_to_order')} units")
    
    except Exception as e:
        st.error(f'Error: {str(e)}')
