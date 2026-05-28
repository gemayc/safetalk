"""
Script para arrancar la API de SafeTalk fácilmente.

Uso:
    python run_api.py
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",       # Ruta a la app FastAPI
        host="127.0.0.1",          # Solo accesible desde tu PC (desarrollo)
        port=8000,                 # Puerto
        reload=True                # Reinicio automático al cambiar código
    )