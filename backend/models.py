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
