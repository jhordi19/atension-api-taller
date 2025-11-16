# Usar imagen oficial de Python 3.13 slim
FROM python:3.13-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements.txt primero
COPY app/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ /app/

# Exponer el puerto (documentación)
EXPOSE 8080

# Comando para ejecutar la aplicación
# Cloud Run inyecta PORT=8080 por defecto
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}