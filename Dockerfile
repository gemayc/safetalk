# Usamos una imagen oficial, ligera y segura
FROM python:3.12-slim

# Evita que Python escriba archivos .pyc y asegura que los logs salgan en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalamos uv para gestionar dependencias a máxima velocidad
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Configuramos nuestro directorio de trabajo en el contenedor
WORKDIR /app

# Copiamos primero las dependencias (optimiza la caché de Docker)
COPY pyproject.toml .
# COPY uv.lock . # (Descomenta esta línea si usas uv.lock)

# Instalamos las librerías a nivel de sistema
RUN uv pip install --system -r pyproject.toml

# Copiamos todo el código fuente y el script de arranque
COPY src/ ./src/
COPY start.sh .

# Damos permisos de ejecución al script de bash
RUN chmod +x start.sh

# Punto de entrada
CMD ["./start.sh"]