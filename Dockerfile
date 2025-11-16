FROM python:3.11-slim

WORKDIR /app

# 1. Instalar dependencias del sistema operativo para la compilación
# Esto es necesario para librerías Python que usan código C (como google-cloud-sql-connector y cryptography)
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    # Limpieza para reducir el tamaño de la imagen final
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt /app/requirements.txt

# 2. Ejecutar la instalación de paquetes Python
RUN pip install --no-cache-dir -r /app/requirements.txt

# 3. Copiar el resto del código
# Nota: La instrucción 'COPY app/ /app/app/' implica que tu código Python 
# (incluyendo main.py) está en el directorio 'app' dentro de tu contexto de compilación.
COPY app/ /app/app/

# 4. Exponer el puerto
EXPOSE 8080

# 5. Comando de inicio
# Asegúrate de que 'app.main:app' sea la ruta correcta a tu objeto FastAPI/Uvicorn.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]