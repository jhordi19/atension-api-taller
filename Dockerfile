FROM python:3.11-slim

WORKDIR /app

# **Paso crucial:** Instalar herramientas de compilación y librerías científicas necesarias.
# build-essential y libffi-dev son para la mayoría de paquetes (cffi, cryptography).
# libatlas-base-dev y gfortran son necesarios para numpy, scipy y scikit-learn.
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libatlas-base-dev \
    gfortran \
    # Limpieza final
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt /app/requirements.txt

# El pip install debería funcionar ahora sin errores de compilación
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app/ /app/app/

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]