import os
from dotenv import load_dotenv

# Load environment variables from .env file (if exists)
load_dotenv()


class Config:
    DEBUG = False
    TESTING = False

    # ==============================
    # Database Configuration (XAMPP)
    # ==============================

    DB_USER = os.getenv("MYSQL_USER", "root")
    DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")  # Default EMPTY for XAMPP
    DB_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    DB_PORT = os.getenv("MYSQL_PORT", "3306")
    DB_NAME = os.getenv("MYSQL_DATABASE", "smartgearai")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ==============================
    # JWT Configuration
    # ==============================

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-this-32-characters")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    # Admin credentials (used to seed admin user if missing)
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@gmail.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

