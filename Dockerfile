# Usar imagen oficial de Python 3.13 slim
FROM python:3.13-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements.txt primero
COPY app/requirements.txt .

# Instalar dependencias de Python (ya no se necesita gcc)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ /app/

# Comando para ejecutar la aplicación
# Este CMD es más flexible: lee el puerto $PORT
# que Cloud Run le da automáticamente.
CMD uvicorn main:app --host 0.0.0.0 --port $PORT