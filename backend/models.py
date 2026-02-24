from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    role = db.Column(db.String(50), nullable=False, default="user")
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def as_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email}

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        from werkzeug.security import generate_password_hash

        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        from werkzeug.security import check_password_hash

        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)


# ---- additional table for simple notifications ----

class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    related_type = db.Column(db.String(50), nullable=True)
    related_id = db.Column(db.Integer, nullable=True)
    seen = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="notifications")

    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message": self.message,
            "related_type": self.related_type,
            "related_id": self.related_id,
            "seen": self.seen,
            "created_at": str(self.created_at),
        }

# -------------------- SCM & Inventory Models --------------------


class InventoryItem(db.Model):
    __tablename__ = "inventory_items"
    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(50), unique=True, nullable=False)  # unique code used to identify the item
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=True)  # e.g. raw material, component, etc.
    quantity = db.Column(db.Float, default=0.0)
    reorder_level = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def as_dict(self):
        return {
            "id": self.id,
            "item_code": self.item_code,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "reorder_level": self.reorder_level,
            "created_at": str(self.created_at),
        }


class MaterialRequest(db.Model):
    __tablename__ = "material_requests"
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(100), nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(50), default="pending")  # pending, inventory_approved, ordered, fulfilled
    processed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    processed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("MaterialRequestItem", backref="request", cascade="all, delete-orphan")

    def as_dict(self):
        return {
            "id": self.id,
            "department": self.department,
            "requested_by": self.requested_by,
            "status": self.status,
            "processed_by": self.processed_by,
            "processed_at": str(self.processed_at) if self.processed_at else None,
            "created_at": str(self.created_at),
            "items": [i.as_dict() for i in self.items],
        }


class MaterialRequestItem(db.Model):
    __tablename__ = "material_request_items"
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("material_requests.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)  # snapshot of name at time of request
    quantity = db.Column(db.Float, nullable=False)

    # these additional fields capture allocation results and workflow status
    quantity_allocated = db.Column(db.Float, default=0.0)
    quantity_to_order = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default="pending")  # pending, allocated, to_order, sent, received

    item = db.relationship("InventoryItem", backref="requested_in")

    def as_dict(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "quantity_allocated": self.quantity_allocated,
            "quantity_to_order": self.quantity_to_order,
            "status": self.status,
        }


class PurchaseRequest(db.Model):
    __tablename__ = "purchase_requests"
    id = db.Column(db.Integer, primary_key=True)
    material_request_id = db.Column(db.Integer, db.ForeignKey("material_requests.id"))
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    purchaser_email = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(50), default="draft")  # draft, submitted, approved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("PurchaseRequestItem", backref="purchase_request", cascade="all, delete-orphan")

    def as_dict(self):
        return {
            "id": self.id,
            "material_request_id": self.material_request_id,
            "created_by": self.created_by,
            "purchaser_email": self.purchaser_email,
            "status": self.status,
            "created_at": str(self.created_at),
            "items": [i.as_dict() for i in self.items],
        }


class PurchaseRequestItem(db.Model):
    __tablename__ = "purchase_request_items"
    id = db.Column(db.Integer, primary_key=True)
    purchase_request_id = db.Column(db.Integer, db.ForeignKey("purchase_requests.id"), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    def as_dict(self):
        return {"id": self.id, "purchase_request_id": self.purchase_request_id, "item_name": self.item_name, "quantity": self.quantity}


class PurchaseOrder(db.Model):
    __tablename__ = "purchase_orders"
    id = db.Column(db.Integer, primary_key=True)
    purchase_request_id = db.Column(db.Integer, db.ForeignKey("purchase_requests.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    vendor = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(50), default="open")  # open, received, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("PurchaseOrderItem", backref="purchase_order", cascade="all, delete-orphan")

    def as_dict(self):
        return {
            "id": self.id,
            "purchase_request_id": self.purchase_request_id,
            "created_by": self.created_by,
            "vendor": self.vendor,
            "status": self.status,
            "created_at": str(self.created_at),
            "items": [i.as_dict() for i in self.items],
        }


class PurchaseOrderItem(db.Model):
    __tablename__ = "purchase_order_items"
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey("purchase_orders.id"), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    def as_dict(self):
        return {"id": self.id, "purchase_order_id": self.purchase_order_id, "item_name": self.item_name, "quantity": self.quantity}


class ScrapRecord(db.Model):
    __tablename__ = "scrap_records"
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(50), default="reported")  # reported, approved, processed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def as_dict(self):
        return {
            "id": self.id,
            "department": self.department,
            "description": self.description,
            "quantity": self.quantity,
            "created_by": self.created_by,
            "status": self.status,
            "created_at": str(self.created_at),
        }
