FROM python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel

# COPIA requirements desde backend/app/
COPY backend/app/requirements.txt ./requirements.txt

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# COPIAR TODO EL CÓDIGO DE backend/app/ → /app
COPY backend/app /app

ENV PYTHONPATH=/app

EXPOSE 8080

# IMPORTANTE: app.main:app porque el archivo está dentro de /app/app/main.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
