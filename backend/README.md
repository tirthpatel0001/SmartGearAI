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

```powershell
set MYSQL_USER=root
set MYSQL_PASSWORD=your_password
set MYSQL_DATABASE=sgmas_db
docker-compose up --build
```

The backend will be available at `http://localhost:5000` and MySQL on port `3306`.
