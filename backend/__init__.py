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
            # Ensure the core tables exist before we attempt schema tweaks.  This
            # plays nicely on a fresh database where migrations haven't been run
            # yet (development/devops convenience).  It is harmless when tables
            # already exist.
            db.create_all()

            # make sure schema additions are present (non-destructive)
            from sqlalchemy import inspect

            def _add_column_if_missing(table, column_sql):
                insp_local = inspect(db.engine)  # fresh inspector each time
                cols = [c['name'] for c in insp_local.get_columns(table)]
                name = column_sql.split()[0]
                if name not in cols:
                    print(f"adding column {name} to {table}")
                    db.engine.execute(f"ALTER TABLE {table} ADD COLUMN {column_sql}")

            insp = inspect(db.engine)
            if 'material_requests' in insp.get_table_names():
                _add_column_if_missing('material_requests', 'processed_by INT NULL')
                _add_column_if_missing('material_requests', 'processed_at DATETIME NULL')
            if 'material_request_items' in insp.get_table_names():
                _add_column_if_missing('material_request_items', 'quantity_allocated FLOAT DEFAULT 0.0')
                _add_column_if_missing('material_request_items', 'quantity_to_order FLOAT DEFAULT 0.0')
                _add_column_if_missing('material_request_items', "status VARCHAR(50) DEFAULT 'pending'")
            if 'purchase_requests' in insp.get_table_names():
                _add_column_if_missing('purchase_requests', 'purchaser_email VARCHAR(120) NULL')

            admin_email = app.config.get('ADMIN_EMAIL')
            admin_password = app.config.get('ADMIN_PASSWORD')
            admin = User.query.filter_by(email=admin_email).first()
            if not admin:
                u = User(username=admin_email, email=admin_email, role='admin', is_approved=True)
                u.set_password(admin_password)
                db.session.add(u)
                db.session.commit()
            # also seed default inventory items if not present
            from .models import InventoryItem
            default_items = [
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
            for item in default_items:
                exists = InventoryItem.query.filter_by(item_code=item['item_code']).first()
                if not exists:
                    try:
                        inv = InventoryItem(**item, quantity=0.0)
                        db.session.add(inv)
                        db.session.commit()
                    except Exception:
                        # ignore if table not ready or constraint
                        pass
    except Exception:
        # Ignore failures (e.g., missing DB connection)
        pass

    return app
