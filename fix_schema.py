#!/usr/bin/env python
"""
Quick script to add missing role and is_approved columns to users table  
and seed the admin user if needed.
"""
import pymysql
from backend.models import User
from backend import create_app

# Database connection (adjust as needed from your .env)
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = ""  # XAMPP default
DB_NAME = "smartgearai"
DB_PORT = 3306

print("Connecting to database...")
conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=DB_PORT
)
cur = conn.cursor()

# Check if columns exist before adding
try:
    print("Checking if role column exists...")
    cur.execute("SELECT role FROM users LIMIT 1")
    print("  ✓ role column already exists")
except Exception as e:
    if "Unknown column" in str(e):
        print("  ✗ role column missing, adding...")
        cur.execute("ALTER TABLE users ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'user'")
        print("  ✓ Added role column")
    else:
        print(f"  Error: {e}")

try:
    print("Checking if is_approved column exists...")
    cur.execute("SELECT is_approved FROM users LIMIT 1")
    print("  ✓ is_approved column already exists")
except Exception as e:
    if "Unknown column" in str(e):
        print("  ✗ is_approved column missing, adding...")
        cur.execute("ALTER TABLE users ADD COLUMN is_approved TINYINT(1) NOT NULL DEFAULT 1")
        print("  ✓ Added is_approved column")
    else:
        print(f"  Error: {e}")

conn.commit()
cur.close()
conn.close()

# Now seed admin user via Flask app
print("\nSeeding admin user via Flask...")
app = create_app()
with app.app_context():
    admin = User.query.filter_by(email="admin@gmail.com").first()
    if admin:
        print("  ✓ Admin user already exists")
    else:
        print("  ✗ Admin user missing, creating...")
        from backend.models import db
        u = User(username="admin@gmail.com", email="admin@gmail.com", role="admin", is_approved=True)
        u.set_password("admin")
        db.session.add(u)
        db.session.commit()
        print("  ✓ Admin user created (email: admin@gmail.com, password: admin)")

print("\n✅ Schema and seeding complete!")
