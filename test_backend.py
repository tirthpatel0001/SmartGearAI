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

print("\n" + "=" * 60)
print("If test 3 passed, the issue is in Streamlit.")
print("If test 1 or 2 failed, restart the backend:")
print("  python backend\\app.py")
print("=" * 60)
