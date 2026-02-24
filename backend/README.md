# SGMA S Backend (Flask + MySQL)

Quick scaffold for a Flask backend using SQLAlchemy + MySQL.

Setup (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
copy backend\.env.example backend\.env
# Edit backend\.env with your MySQL credentials
```

Run (dev):

```powershell
python backend\app.py
```

Database migrations (optional):

```powershell
pip install Flask-Migrate
set FLASK_APP=backend.app
flask db init
flask db migrate -m "initial"
flask db upgrade
```

Docker development (MySQL + backend):

## Schema changes (2026 Feb)

The material request workflow was extended to support allocation and
notifications.

* `material_requests` now has `status`, `processed_by`, `processed_at`.
* `material_request_items` include `quantity_allocated`, `quantity_to_order`,
  and `status` per-line.
* new `notifications` table stores simple user alerts.
* `purchase_requests` now stores an optional `purchaser_email`.

If you already have a database you will need to add these columns or run a
migration (see Flask-Migrate commands above).

**Troubleshooting runtime errors**

When the application is started against an older schema it now performs a
best-effort update automatically.  If you see an exception like:

```
OperationalError: (1054, "Unknown column 'processed_by' in 'field list'")
```

it means the `material_requests` table does not yet include the new
`processed_by`/`processed_at` fields.  Restart the backend so the startup
logic can add the missing columns.  You will see console output such as:

```
adding column processed_by to material_requests
```

If you cannot restart the server, apply the alterations manually:

```sql
ALTER TABLE material_requests ADD COLUMN processed_by INT NULL;
ALTER TABLE material_requests ADD COLUMN processed_at DATETIME NULL;
ALTER TABLE material_request_items ADD COLUMN quantity_allocated FLOAT DEFAULT 0.0;
ALTER TABLE material_request_items ADD COLUMN quantity_to_order FLOAT DEFAULT 0.0;
ALTER TABLE material_request_items ADD COLUMN status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE purchase_requests ADD COLUMN purchaser_email VARCHAR(120) NULL;
```

Once the schema is up-to-date, retry your operation.

Docker development (MySQL + backend):

```powershell
set MYSQL_USER=root
set MYSQL_PASSWORD=your_password
set MYSQL_DATABASE=sgmas_db
docker-compose up --build
```

The backend will be available at `http://localhost:5000` and MySQL on port `3306`.
