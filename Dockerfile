# USAR ESTA VERSIÓN
FROM python:3.11

WORKDIR /app

# MANTENEMOS ESTOS PASOS POR TUS OTRAS LIBRERÍAS (numpy, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libopenblas-dev \
    gfortran \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Asegúrate de que tu requirements.txt ahora tiene google-cloud-sql-connector-python
COPY app/requirements.txt /app/requirements.txt

# El pip install debería funcionar
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app/ /app/app/

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]