# Usar imagen oficial de Python 3.13 slim
FROM python:3.13-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero (para aprovechar caché de Docker)
COPY app/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ /app/

# Exponer el puerto que Cloud Run espera (8080)
EXPOSE 8080

# Variables de entorno para producción
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Comando para ejecutar la aplicación con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]