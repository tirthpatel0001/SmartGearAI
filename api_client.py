import requests

# Point API to backend service created in this project
API_URL = "http://127.0.0.1:5000/api"


def login_user(username, password):
    payload = {"username": username, "password": password}
    return requests.post(f"{API_URL}/auth/login", json=payload)


def signup_user(username, email, password):
    payload = {"username": username, "email": email, "password": password}
    return requests.post(f"{API_URL}/auth/signup", json=payload)


def signup_user_with_role(username, email, password, role="user"):
    payload = {"username": username, "email": email, "password": password, "role": role}
    return requests.post(f"{API_URL}/auth/signup", json=payload)


def admin_get_pending(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{API_URL}/admin/pending", headers=headers)


def admin_approve(token: str, user_id: int):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(f"{API_URL}/admin/approve/{user_id}", headers=headers)


def admin_reject(token: str, user_id: int):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(f"{API_URL}/admin/reject/{user_id}", headers=headers)


def admin_get_heads(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{API_URL}/admin/heads", headers=headers)


# SCM / inventory helpers

def get_inventory_items(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{API_URL}/inventory/items", headers=headers)


def create_inventory_item(token: str, data: dict):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(f"{API_URL}/inventory/items", json=data, headers=headers)


def get_material_requests(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{API_URL}/material_requests", headers=headers)


def create_material_request(token: str, data: dict):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(f"{API_URL}/material_requests", json=data, headers=headers)


def get_purchase_requests(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{API_URL}/purchase_requests", headers=headers)


def create_purchase_request(token: str, data: dict):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(f"{API_URL}/purchase_requests", json=data, headers=headers)


def get_purchase_orders(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{API_URL}/purchase_orders", headers=headers)


def create_purchase_order(token: str, data: dict):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(f"{API_URL}/purchase_orders", json=data, headers=headers)


def get_scrap_records(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{API_URL}/scrap_records", headers=headers)


def create_scrap_record(token: str, data: dict):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(f"{API_URL}/scrap_records", json=data, headers=headers)
