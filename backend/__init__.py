from flask import Flask
from flask_migrate import Migrate
from .config import Config
from .models import db
from .models import User


def create_app(config_object: object = None):
    app = Flask(__name__)

    # Load configuration from object or default Config
    if config_object is None:
        app.config.from_object(Config)
    else:
        app.config.from_object(config_object)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    # Register blueprints
    from .routes import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    # Try to ensure an admin user exists (best-effort; requires DB/tables exist)
    try:
        with app.app_context():
            admin_email = app.config.get('ADMIN_EMAIL')
            admin_password = app.config.get('ADMIN_PASSWORD')
            admin = User.query.filter_by(email=admin_email).first()
            if not admin:
                u = User(username=admin_email, email=admin_email, role='admin', is_approved=True)
                u.set_password(admin_password)
                db.session.add(u)
                db.session.commit()
    except Exception:
        # Ignore failures (e.g., tables not created yet)
        pass

    return app
