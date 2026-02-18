#!/usr/bin/env python
"""
Debug script to test admin token and pending requests.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

print("=" * 60)
print("ADMIN TOKEN & REQUESTS DEBUG")
print("=" * 60)

# 1. Login and get token
print("\n1. Logging in as admin...")
resp = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin@gmail.com",
    "password": "admin"
})
if resp.status_code != 200:
    print(f"   ✗ Login failed: {resp.status_code}")
    print(f"   Response: {resp.json()}")
    exit(1)

data = resp.json()
token = data.get("access_token")
user = data.get("user", {})

print(f"   ✓ Login successful")
print(f"   - Token length: {len(token)}")
print(f"   - Token preview: {token[:50]}...")
print(f"   - User: {user.get('username')}")
print(f"   - Role: {user.get('role')}")

# 2. Decode token to check payload
import jwt
try:
    from backend.config import Config
    decoded = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
    print(f"\n2. Token Payload:")
    print(f"   - ID (sub): {decoded.get('sub')}")
    print(f"   - Username: {decoded.get('username')}")
    print(f"   - Role: {decoded.get('role')}")
except Exception as e:
    print(f"\n2. ✗ Could not decode token: {e}")

# 3. Test pending endpoint WITH header
print(f"\n3. Testing /admin/pending with Authorization header...")
headers = {"Authorization": f"Bearer {token}"}
print(f"   Headers: {headers}")
resp = requests.get(f"{BASE_URL}/admin/pending", headers=headers)
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.json()}")

# 4. Test pending endpoint WITHOUT header (should fail)
print(f"\n4. Testing /admin/pending WITHOUT Authorization header...")
resp = requests.get(f"{BASE_URL}/admin/pending", headers={})
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.json()}")

print("\n" + "=" * 60)
