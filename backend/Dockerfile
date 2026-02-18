FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "backend.wsgi:app", "-b", "0.0.0.0:5000", "--workers", "2"]
