#!/usr/bin/env python
"""
Diagnostic script to check database status and admin setup.
"""
import pymysql
from backend import create_app
from backend.models import User, db

DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "smartgearai"
DB_PORT = 3306

print("=" * 60)
print("DATABASE & ADMIN SETUP CHECK")
print("=" * 60)

# 1. Check database connection
print("\n1. Checking database connection...")
try:
    conn = pymysql.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME, port=DB_PORT
    )
    print("   ✓ Connected to database")
    cur = conn.cursor()
except Exception as e:
    print(f"   ✗ Failed to connect: {e}")
    exit(1)

# 2. Check if columns exist
print("\n2. Checking users table schema...")
try:
    cur.execute("DESC users")
    cols = cur.fetchall()
    col_names = [col[0] for col in cols]
    
    has_role = "role" in col_names
    has_approved = "is_approved" in col_names
    
    print(f"   - role column: {'✓' if has_role else '✗'}")
    print(f"   - is_approved column: {'✓' if has_approved else '✗'}")
    
    if not (has_role and has_approved):
        print("\n   ⚠️ Missing columns! Run: python fix_schema.py")
        conn.close()
        exit(1)
except Exception as e:
    print(f"   ✗ Error checking schema: {e}")
    conn.close()
    exit(1)

# 3. Check admin user exists
print("\n3. Checking admin user...")
try:
    cur.execute("SELECT id, username, email, role, is_approved FROM users WHERE email='admin@gmail.com'")
    admin = cur.fetchone()
    if admin:
        admin_id, username, email, role, is_approved = admin
        print(f"   ✓ Admin exists:")
        print(f"     - ID: {admin_id}")
        print(f"     - Username: {username}")
        print(f"     - Email: {email}")
        role_status = "✓" if role == "admin" else "✗ (should be admin)"
        approved_status = "✓" if is_approved else "✗ (should be 1)"
        print(f"     - Role: {role} {role_status}")
        print(f"     - Is Approved: {is_approved} {approved_status}")
    else:
        print("   ✗ Admin user not found!")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 4. Check pending users
print("\n4. Checking pending signup requests...")
try:
    cur.execute("SELECT id, username, email, role, is_approved FROM users WHERE is_approved=0 OR is_approved=FALSE")
    pending = cur.fetchall()
    if pending:
        print(f"   ✓ Found {len(pending)} pending requests:")
        for uid, uname, uemail, urole, uapproved in pending:
            print(f"     - {uemail} ({urole}) - ID: {uid}")
    else:
        print("   ℹ️ No pending requests (this is OK if you haven't signed up any heads yet)")
except Exception as e:
    print(f"   ✗ Error: {e}")

conn.close()

# 5. Test Flask app and JWT
print("\n5. Testing Flask app...")
try:
    app = create_app()
    with app.app_context():
        admin_user = User.query.filter_by(email="admin@gmail.com").first()
        if admin_user:
            print(f"   ✓ Flask can query admin user")
            print(f"     - Role in app: {admin_user.role}")
            print(f"     - Approved in app: {admin_user.is_approved}")
        else:
            print("   ✗ Flask cannot find admin user")
except Exception as e:
    print(f"   ✗ Error loading Flask app: {e}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("""
If all checks pass:
1. Run backend: python backend\\app.py
2. Run Streamlit: streamlit run app\\main.py
3. Login as: admin@gmail.com / admin

If checks fail:
1. Run: python fix_schema.py
2. Then retry this script
""")
