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

    # ensure new tables exist (inventory, requests, etc.)
    print("\nEnsuring new SCM/inventory tables exist...")
    from backend.models import db as _db
    _db.create_all()
    print("  ✓ Tables created or already present")

    # check inventory_items for item_code column and add if missing
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )
    cur = conn.cursor()
    # if inventory_items table doesn't exist yet we can't even select from it
    try:
        cur.execute("SELECT item_code FROM inventory_items LIMIT 1")
        print("  ✓ inventory_items.item_code column already exists")
    except Exception as e:
        msg = str(e)
        # use double quotes for strings containing apostrophes
        if "Unknown column" in msg or "doesn't exist" in msg or "does not exist" in msg:
            if "doesn't exist" in msg and "inventory_items" in msg:
                print("  ✗ inventory_items table missing, will be created by SQLAlchemy later")
            # add column when table does exist; ignore if table missing
            if "inventory_items" in msg and "doesn't exist" not in msg:
                print("  ✗ item_code column missing, adding...")
                # add as nullable first so existing rows can be updated
                cur.execute("ALTER TABLE inventory_items ADD COLUMN item_code VARCHAR(50)")
                # populate existing rows with a simple code based on id
                print("    populating existing rows with default codes")
                cur.execute("SELECT id, name FROM inventory_items")
                rows = cur.fetchall()
                for rid, rname in rows:
                    code = f"IT{rid:04d}"
                    cur.execute("UPDATE inventory_items SET item_code=%s WHERE id=%s", (code, rid))
                # now alter to enforce not null and unique
                try:
                    cur.execute("ALTER TABLE inventory_items MODIFY item_code VARCHAR(50) NOT NULL")
                    cur.execute("ALTER TABLE inventory_items ADD UNIQUE (item_code)")
                except Exception:
                    pass
                print("  ✓ Added item_code column")
        else:
            print(f"  Error checking item_code column: {e}")
    conn.commit()
    # seed predefined gearbox manufacturing items (use raw SQL to avoid ORM caching issues)
    print("\nSeeding predefined inventory items...")
    predefined = [
        {"item_code": "RS", "name": "Replacement gear set", "category": "component"},
        {"item_code": "LUB", "name": "Lubricant", "category": "consumable"},
        {"item_code": "STG", "name": "Surface-treated gears", "category": "component"},
        {"item_code": "INS", "name": "Inspection kit", "category": "tool"},
        {"item_code": "CGA", "name": "Complete gearbox assembly", "category": "assembly"},
        {"item_code": "FST", "name": "Fasteners", "category": "hardware"},
        {"item_code": "HSG", "name": "High-strength gears", "category": "component"},
        {"item_code": "SPB", "name": "Support bearings", "category": "component"},
        {"item_code": "RFG", "name": "Reinforced gear", "category": "component"},
        {"item_code": "CMS", "name": "Crack monitoring sensor", "category": "sensor"},
        {"item_code": "INT", "name": "Inspection tools", "category": "tool"},
        {"item_code": "FGK", "name": "Full gearbox kit", "category": "assembly"},
    ]
    for item in predefined:
        # check existence via cursor
        try:
            cur.execute(
                "SELECT COUNT(*) FROM inventory_items WHERE item_code=%s", (item['item_code'],)
            )
            cnt = cur.fetchone()[0]
            if cnt == 0:
                cur.execute(
                    "INSERT INTO inventory_items (item_code,name,category,quantity) VALUES (%s,%s,%s,0)",
                    (item['item_code'], item['name'], item['category']),
                )
                conn.commit()
                print(f"    added {item['item_code']} - {item['name']}")
            else:
                print(f"    already present {item['item_code']}")
        except Exception as se:
            print(f"    could not add {item['item_code']}: {se}")
    conn.close()

print("\n✅ Schema and seeding complete!")
