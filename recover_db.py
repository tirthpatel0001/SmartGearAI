import os
import logging
import subprocess
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='recovery_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Database configuration
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_NAME = "smartgearai"

DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# SQLAlchemy setup
Base = declarative_base()

# Define models (copied from backend/models.py)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=True)
    role = Column(String(50), nullable=False, default="user")
    is_approved = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String(500), nullable=False)
    related_type = Column(String(50), nullable=True)
    related_id = Column(Integer, nullable=True)
    seen = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(Integer, primary_key=True)
    item_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)
    quantity = Column(Float, default=0.0)
    reorder_level = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class MaterialRequest(Base):
    __tablename__ = "material_requests"
    id = Column(Integer, primary_key=True)
    department = Column(String(100), nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="pending")
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class MaterialRequestItem(Base):
    __tablename__ = "material_request_items"
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("material_requests.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity_requested = Column(Float, nullable=False)
    quantity_allocated = Column(Float, default=0.0)
    quantity_to_order = Column(Float, default=0.0)
    status = Column(String(50), default="pending")

class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"
    id = Column(Integer, primary_key=True)
    department = Column(String(100), nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="pending")
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    processed_at = Column(DateTime, nullable=True)
    purchaser_email = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PurchaseRequestItem(Base):
    __tablename__ = "purchase_request_items"
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("purchase_requests.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity_requested = Column(Float, nullable=False)
    quantity_allocated = Column(Float, default=0.0)
    quantity_to_order = Column(Float, default=0.0)
    status = Column(String(50), default="pending")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True)
    purchase_request_id = Column(Integer, ForeignKey("purchase_requests.id"), nullable=False)
    supplier = Column(String(200), nullable=False)
    status = Column(String(50), default="pending")
    ordered_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    id = Column(Integer, primary_key=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity_ordered = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

class ScrapRecord(Base):
    __tablename__ = "scrap_records"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)
    scrapped_at = Column(DateTime, default=datetime.utcnow)

class WorkloadLog(Base):
    __tablename__ = "workload_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

def get_all_tables():
    return [
        "users", "notifications", "inventory_items", "material_requests",
        "material_request_items", "purchase_requests", "purchase_request_items",
        "purchase_orders", "purchase_order_items", "scrap_records", "workload_logs"
    ]

def phase1_discard_tablespaces():
    logging.info("Starting Phase 1: Discard Tablespaces")
    try:
        # Connect without database first
        temp_uri = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/?charset=utf8mb4"
        engine = create_engine(temp_uri)
        with engine.connect() as conn:
            # Drop and recreate database
            conn.execute(text("DROP DATABASE IF EXISTS smartgearai"))
            conn.execute(text("CREATE DATABASE smartgearai"))
            logging.info("Database dropped and recreated")

        # Reconnect to the database
        engine = create_engine(DATABASE_URI)
        Base.metadata.create_all(engine)
        logging.info("Tables created")

        # Discard tablespaces
        with engine.connect() as conn:
            tables = get_all_tables()
            for table in tables:
                try:
                    conn.execute(text(f"ALTER TABLE {table} DISCARD TABLESPACE"))
                    logging.info(f"Discarded tablespace for {table}")
                except Exception as e:
                    logging.error(f"Failed to discard tablespace for {table}: {e}")
    except Exception as e:
        logging.error(f"Phase 1 failed: {e}")
        sys.exit(1)

def phase2_import_tablespaces():
    logging.info("Starting Phase 2: Import Tablespaces")
    try:
        engine = create_engine(DATABASE_URI)
        with engine.connect() as conn:
            tables = get_all_tables()
            for table in tables:
                ibd_file = f"C:\\xampp\\mysql\\data\\smartgearai\\{table}.ibd"
                if os.path.exists(ibd_file):
                    try:
                        conn.execute(text(f"ALTER TABLE {table} IMPORT TABLESPACE"))
                        logging.info(f"Imported tablespace for {table}")
                    except Exception as e:
                        logging.error(f"Failed to import tablespace for {table}: {e}")
                else:
                    logging.warning(f"IBD file not found for {table}: {ibd_file}")
    except Exception as e:
        logging.error(f"Phase 2 failed: {e}")
        sys.exit(1)

def run_batch_script():
    logging.info("Running batch script for file operations")
    try:
        result = subprocess.run(["recover_files.bat"], capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            logging.info("Batch script executed successfully")
        else:
            logging.error(f"Batch script failed: {result.stderr}")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to run batch script: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python recover_db.py <phase>")
        print("Phases: 1 (discard), 2 (import)")
        sys.exit(1)

    phase = sys.argv[1]

    if phase == "1":
        phase1_discard_tablespaces()
    elif phase == "2":
        run_batch_script()
        phase2_import_tablespaces()
    else:
        print("Invalid phase. Use 1 or 2")
        sys.exit(1)

if __name__ == "__main__":
    main()