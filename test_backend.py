#!/usr/bin/env python
"""
Test script to verify backend admin endpoints are working.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

print("=" * 60)
print("BACKEND API TEST")
print("=" * 60)

# 1. Test health endpoint
print("\n1. Testing health endpoint...")
try:
    resp = requests.get(f"{BASE_URL}/")
    if resp.status_code == 200:
        print(f"   ✓ Backend is alive: {resp.json()}")
    else:
        print(f"   ✗ Unexpected status: {resp.status_code}")
except Exception as e:
    print(f"   ✗ Backend not running! Error: {e}")
    print("   → Run: python backend\\app.py")
    exit(1)

# 2. Test admin login
print("\n2. Testing admin login...")
resp = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin@gmail.com",
    "password": "admin"
})
if resp.status_code == 200:
    data = resp.json()
    token = data.get("access_token")
    user = data.get("user", {})
    print(f"   ✓ Login successful")
    print(f"     - Token: {token[:50]}...")
    print(f"     - User role: {user.get('role')}")
    print(f"     - User is_approved: {user.get('is_approved')}")
else:
    print(f"   ✗ Login failed: {resp.status_code}")
    print(f"     Response: {resp.json()}")
    exit(1)

# 3. Test pending requests endpoint
print("\n3. Testing /admin/pending endpoint...")
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get(f"{BASE_URL}/admin/pending", headers=headers)
if resp.status_code == 200:
    pending = resp.json()
    print(f"   ✓ Got pending requests: {len(pending)} found")
    for u in pending:
        print(f"     - {u.get('email')} ({u.get('role')}) - ID: {u.get('id')}")
else:
    print(f"   ✗ Failed: {resp.status_code}")
    print(f"     Response: {resp.json()}")

# 4. Quick smoke for new SCM endpoints (admin token should be allowed but subject to role restrictions)
print("\n4. Smoke test SCM endpoints with admin token (admin has access to everything)")
for path in ["inventory/items", "material_requests", "purchase_requests", "purchase_orders", "scrap_records"]:
    r = requests.get(f"{BASE_URL}/{path}", headers=headers)
    print(f"   GET /{path} -> {r.status_code}")
    if r.status_code == 200:
        items = r.json()
        print(f"     returned {len(items)} entries")
        if path == "inventory/items":
            for it in items[:10]:
                print(f"       - {it.get('item_code')} {it.get('name')} qty={it.get('quantity')}")
    else:
        print(f"     error: {r.text}")

# 5. Create a dummy inventory item, make a material request and process it
print("\n5. Workflow test: inventory -> material request -> process")
# create an inventory_head user to add inventory items
print("\n   creating an inventory_head user for testing...")
signup_inv = requests.post(f"{BASE_URL}/auth/signup", json={
    "username": "invhead@example.com",
    "email": "invhead@example.com",
    "password": "secret",
    "role": "inventory_head"
}, headers=headers)
print(f"   signup inv response: {signup_inv.status_code} -> {signup_inv.text}")
inv_token = None
if signup_inv.status_code == 201:
    iid = signup_inv.json().get('user', {}).get('id')
    appr_inv = requests.post(f"{BASE_URL}/admin/approve/{iid}", headers=headers)
    print(f"   approve inv user: {appr_inv.status_code}")
    resp_inv_login = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "invhead@example.com",
        "password": "secret"
    })
    if resp_inv_login.status_code == 200:
        inv_token = resp_inv_login.json().get('access_token')
inv_headers = {"Authorization": f"Bearer {inv_token}"} if inv_token else headers

# create inventory item (provide an item_code) using inventory head
resp_inv = requests.post(
    f"{BASE_URL}/inventory/items",
    json={"item_code": "TW01", "name": "test_widget", "quantity": 5, "category": "raw"},
    headers=inv_headers
)
print(f"   create inventory item: {resp_inv.status_code} -> {resp_inv.text}")

# create a production_head user so we can test MR creation with proper role
print("\n   creating a production_head user for testing...")
signup = requests.post(f"{BASE_URL}/auth/signup", json={
    "username": "prodhead@example.com",
    "email": "prodhead@example.com",
    "password": "secret",
    "role": "production_head"
}, headers=headers)
print(f"   signup response: {signup.status_code} -> {signup.text}")
prod_token = None
if signup.status_code == 201:
    user_info = signup.json().get('user', {})
    pid = user_info.get('id')
    # approve the new user
    appr = requests.post(f"{BASE_URL}/admin/approve/{pid}", headers=headers)
    print(f"   approve user: {appr.status_code}")
    resp_prod = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "prodhead@example.com",
        "password": "secret"
    })
    if resp_prod.status_code == 200:
        prod_token = resp_prod.json().get('access_token')
elif signup.status_code == 409:
    print("   production_head already exists; attempting login")
    resp_prod = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "prodhead@example.com",
        "password": "secret"
    })
    if resp_prod.status_code == 200:
        prod_token = resp_prod.json().get('access_token')
    else:
        print(f"   login failed after conflict: {resp_prod.status_code} {resp_prod.text}")
else:
    print("   unexpected signup response")

# create an scm_planner user so we can verify they can see material requests
print("\n   creating an scm_planner user for testing...")
signup_pl = requests.post(f"{BASE_URL}/auth/signup", json={
    "username": "planner@example.com",
    "email": "planner@example.com",
    "password": "secret",
    "role": "scm_planner"
}, headers=headers)
print(f"   signup planner response: {signup_pl.status_code} -> {signup_pl.text}")
planner_token = None
if signup_pl.status_code == 201:
    pid2 = signup_pl.json().get('user', {}).get('id')
    appr_pl = requests.post(f"{BASE_URL}/admin/approve/{pid2}", headers=headers)
    print(f"   approve planner user: {appr_pl.status_code}")
    resp_pl = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "planner@example.com",
        "password": "secret"
    })
    if resp_pl.status_code == 200:
        planner_token = resp_pl.json().get('access_token')
elif signup_pl.status_code == 409:
    resp_pl = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "planner@example.com",
        "password": "secret"
    })
    if resp_pl.status_code == 200:
        planner_token = resp_pl.json().get('access_token')

# create an scm_purchaser user so we can verify they receive submitted PRs
print("\n   creating an scm_purchaser user for testing...")
signup_pc = requests.post(f"{BASE_URL}/auth/signup", json={
    "username": "purchaser@example.com",
    "email": "purchaser@example.com",
    "password": "secret",
    "role": "scm_purchaser"
}, headers=headers)
print(f"   signup purchaser response: {signup_pc.status_code} -> {signup_pc.text}")
purchaser_token = None
if signup_pc.status_code == 201:
    pid3 = signup_pc.json().get('user', {}).get('id')
    appr_pc = requests.post(f"{BASE_URL}/admin/approve/{pid3}", headers=headers)
    print(f"   approve purchaser user: {appr_pc.status_code}")
    resp_pc = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "purchaser@example.com",
        "password": "secret"
    })
    if resp_pc.status_code == 200:
        purchaser_token = resp_pc.json().get('access_token')
elif signup_pc.status_code == 409:
    resp_pc = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "purchaser@example.com",
        "password": "secret"
    })
    if resp_pc.status_code == 200:
        purchaser_token = resp_pc.json().get('access_token')

if prod_token:
    prod_headers = {"Authorization": f"Bearer {prod_token}"}
    prod_user_id = None
    try:
        prod_user_id = resp_prod.json().get('user', {}).get('id')
    except Exception:
        pass
    # create material request (simulate production head)
    resp_mr = requests.post(
        f"{BASE_URL}/material_requests",
        json={
            "department": "production",
            "requested_by": prod_user_id or 1,
            "items": [{"item_id": resp_inv.json().get('id'), "quantity": 7}],
        },
        headers=prod_headers,
    )
    print(f"   create MR: {resp_mr.status_code} -> {resp_mr.text}")
    if resp_mr.status_code == 201:
        data = resp_mr.json()
        mr = data.get('material_request') or {}
        result = data.get('result') or {}
        mrid = mr.get('id')
        print("   evaluation result", result)
        # inventory should NOT yet be reduced until processed
        resp_after = requests.get(f"{BASE_URL}/inventory/items", headers=headers)
        if resp_after.status_code == 200:
            inv_after = resp_after.json()
            remaining = next((i for i in inv_after if i.get('item_code') == 'TW01'), None)
            if remaining:
                print(f"   inventory after MR (before processing): {remaining.get('quantity')} (should be 5.0)")
        # notification for inventory head should exist
        if inv_token:
            inv_notes = requests.get(f"{BASE_URL}/notifications", headers=inv_headers)
            print(f"   inventory head notifications -> {inv_notes.status_code}, {len(inv_notes.json()) if inv_notes.status_code==200 else inv_notes.text}")
        # inventory head processes the request
        if inv_token:
            proc = requests.post(f"{BASE_URL}/material_requests/{mrid}/process", headers=inv_headers)
            print(f"   inventory head processed MR -> {proc.status_code} {proc.text}")
            # after processing, inventory should have dropped by 5
            resp_after2 = requests.get(f"{BASE_URL}/inventory/items", headers=headers)
            if resp_after2.status_code == 200:
                inv_after2 = resp_after2.json()
                remaining2 = next((i for i in inv_after2 if i.get('item_code') == 'TW01'), None)
                if remaining2:
                    print(f"   inventory after processing: {remaining2.get('quantity')} (should be 0.0)")
            # production head should receive a notification
            prod_notes = requests.get(f"{BASE_URL}/notifications", headers=prod_headers)
            print(f"   production head notifications -> {prod_notes.status_code}, {len(prod_notes.json()) if prod_notes.status_code==200 else prod_notes.text}")
        # there should be no automatic purchase request yet (planner will create one later)
        resp_prs = requests.get(f"{BASE_URL}/purchase_requests", headers=headers)
        print(f"   GET purchase_requests -> {resp_prs.status_code}, {len(resp_prs.json()) if resp_prs.status_code==200 else resp_prs.text}")

        # planner should be able to view material requests
        if planner_token:
            planner_headers = {"Authorization": f"Bearer {planner_token}"}
            resp_mrs = requests.get(f"{BASE_URL}/material_requests", headers=planner_headers)
            print(f"   planner GET material_requests -> {resp_mrs.status_code}, {len(resp_mrs.json()) if resp_mrs.status_code==200 else resp_mrs.text}")
            # planner can send purchase request to purchaser
            if resp_mrs.status_code == 200 and resp_mrs.json():
                first_mr = resp_mrs.json()[0]
                to_order = []
                for it in first_mr.get('items', []):
                    inv_qty = 0
                    try:
                        inv_after = requests.get(f"{BASE_URL}/inventory/items", headers=headers).json()
                        inv_item = next((i for i in inv_after if i.get('id') == it.get('item_id')), None)
                        inv_qty = inv_item.get('quantity', 0) if inv_item else 0
                    except Exception:
                        pass
                    if it.get('quantity', 0) > inv_qty:
                        to_order.append({'item_name': it.get('item_name'), 'quantity': it.get('quantity') - inv_qty})
                if to_order:
                    resp_send = requests.post(
                        f"{BASE_URL}/purchase_requests",
                        json={
                            'material_request_id': first_mr.get('id'),
                            'created_by': prod_user_id or 1,
                            'items': to_order,
                            'status': 'submitted',
                            'purchaser_email': 'purchaser@example.com',
                        },
                        headers=planner_headers,
                    )
                    print(f"   planner sent PR -> {resp_send.status_code} {resp_send.text}")
                    # purchaser should see the submitted PR
                    if purchaser_token:
                        pur_headers = {"Authorization": f"Bearer {purchaser_token}"}
                        resp_prs2 = requests.get(f"{BASE_URL}/purchase_requests", headers=pur_headers)
                        print(f"   purchaser GET purchase_requests -> {resp_prs2.status_code}, {len(resp_prs2.json()) if resp_prs2.status_code==200 else resp_prs2.text}")
                        if resp_prs2.status_code == 200 and resp_prs2.json():
                            last = resp_prs2.json()[-1]
                            print(f"     last PR purchaser_email={last.get('purchaser_email')}")

        # if a purchase request exists create a PO and then mark it received
        if resp_prs.status_code == 200 and resp_prs.json():
            pr_id = resp_prs.json()[-1].get('id')
            resp_po = requests.post(
                f"{BASE_URL}/purchase_orders",
                json={
                    "purchase_request_id": pr_id,
                    "created_by": prod_user_id or 1,
                    "vendor": "Acme Supplies",
                    "items": [{"item_name": "test_widget", "quantity": 2}],
                },
                headers=headers,
            )
            print(f"   create PO: {resp_po.status_code} -> {resp_po.text}")
            if resp_po.status_code == 201:
                po = resp_po.json()
                po_id = po.get('id')
                # simulate receipt of goods
                resp_recv = requests.post(f"{BASE_URL}/purchase_orders/{po_id}/receive", headers=headers)
                print(f"   receive PO: {resp_recv.status_code} -> {resp_recv.text}")
                if resp_recv.status_code == 200:
                    # inventory should now show 2 units returned
                    resp_inv2 = requests.get(f"{BASE_URL}/inventory/items", headers=headers)
                    if resp_inv2.status_code == 200:
                        inv2 = resp_inv2.json()
                        rem2 = next((i for i in inv2 if i.get('item_code') == 'TW01'), None)
                        if rem2:
                            print(f"   inventory after receiving PO: {rem2.get('quantity')} (should be 2.0)")
                else:
                    print("   ✗ PO receive failed")
    else:
        print("   ✗ MR creation failed")
else:
    print("   ✗ could not obtain production head token")

print("\n" + "=" * 60)
print("If test 3 passed, the issue is in Streamlit.")
print("If test 1 or 2 failed, restart the backend:")
print("  python backend\\app.py")
print("=" * 60)
