# Imagen base: Python 3.11 versión "slim" (ligera)
FROM python:3.11-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Variables de entorno para optimizar Python en Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Carpeta de caché para Hugging Face (donde se descargará BETO)
# Hugging Face Spaces requiere que sea escribible por el usuario no-root
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface

# Instalar dependencias del sistema (mínimas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para aprovechar caché de Docker)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar el código de la API
COPY src/ ./src/

# Crear carpeta de caché y dar permisos (necesario para HF Spaces)
RUN mkdir -p /app/.cache/huggingface && \
    chmod -R 777 /app/.cache

# Exponer el puerto que usa Hugging Face Spaces
EXPOSE 7860

# Comando para arrancar la API
# IMPORTANTE: puerto 7860 (no 8000 como en local)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "7860"]