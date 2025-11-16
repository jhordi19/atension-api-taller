FROM python:3.11

WORKDIR /app

# Actualizar pip y wheel
RUN pip install --upgrade pip setuptools wheel

# Copiar requirements
COPY app/requirements.txt .

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar librerías Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY app/ /app/

EXPOSE 8080

# CORRECCIÓN DE CMD: Busca el módulo 'main' en la raíz (/app) y el objeto 'app'.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]