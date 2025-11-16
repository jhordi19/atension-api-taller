FROM python:3.11-slim

WORKDIR /app

# **CORRECCIÓN:** Cambiamos 'libatlas-base-dev' por 'libopenblas-dev'
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libopenblas-dev \
    gfortran \
    # Limpieza final
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt /app/requirements.txt

# El pip install ahora debería poder compilar las librerías Python
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app/ /app/app/

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]