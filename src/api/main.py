"""
API REST para detección de bullying con FastAPI.

Esta API recibe textos y devuelve si son ofensivos o no,
usando el modelo BETO entrenado.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import logging

# Importar los esquemas de datos
from .schemas import (
    TextoInput,
    TextosInput,
    Prediccion,
    PrediccionBatch,
    ModeloInfo
)

# Importar el predictor
from ..models.predictor import BullyingPredictor

# Configurar logging para ver mensajes informativos
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variable global que contendrá el modelo cargado
predictor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Se ejecuta al arrancar y al cerrar la API.

    Al arrancar: carga el modelo (una sola vez).
    Al cerrar: libera recursos.
    """
    # --- ARRANQUE ---
    global predictor
    logger.info("Iniciando API y cargando modelo...")

    try:
        # Buscar la carpeta 'models' del proyecto
        models_dir = Path(__file__).parent.parent.parent / "models"
        predictor = BullyingPredictor(str(models_dir))
        logger.info(f"Modelo cargado: {predictor.model_name}")
    except Exception as e:
        logger.error(f"Error cargando el modelo: {e}")
        raise

    yield  # Aquí la API está funcionando

    # --- CIERRE ---
    logger.info("Cerrando API...")


# Crear la aplicación FastAPI
app = FastAPI(
    title="SafeTalk API",
    description="API para detectar bullying y contenido ofensivo en español",
    version="1.0.0",
    lifespan=lifespan
)

# Permitir que la API sea llamada desde otros sitios (necesario para Telegram)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Permitir cualquier origen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Endpoint raíz. Muestra información básica de la API.
    Se accede en: http://localhost:8000/
    """
    return {
        "mensaje": "SafeTalk API - Detección de Bullying",
        "version": "1.0.0",
        "endpoints": {
            "predecir_uno": "/predict",
            "predecir_varios": "/predict/batch",
            "estado": "/health",
            "info_modelo": "/model/info",
            "documentacion": "/docs"
        }
    }


@app.get("/health")
async def health():
    """
    Comprueba que la API y el modelo están funcionando.
    Se accede en: http://localhost:8000/health
    """
    return {
        "status": "healthy",
        "modelo_cargado": predictor is not None,
        "modelo": predictor.model_name if predictor else None
    }


@app.post("/predict", response_model=Prediccion)
async def predecir_texto(input: TextoInput):
    """
    Predice si UN texto es ofensivo.

    Recibe: { "texto": "eres tonto" }
    Devuelve: { "prediccion": "ofensivo", "confianza": 0.95, ... }
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")

    try:
        resultado = predictor.predict(input.texto)
        return resultado
    except Exception as e:
        logger.error(f"Error en predicción: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch", response_model=PrediccionBatch)
async def predecir_varios(input: TextosInput):
    """
    Predice VARIOS textos a la vez.

    Recibe: { "textos": ["hola", "eres tonto"] }
    Devuelve: lista de predicciones
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")

    try:
        resultados = predictor.predict_batch(input.textos)
        return {
            "predicciones": resultados,
            "total": len(resultados),
            "modelo_usado": predictor.model_name
        }
    except Exception as e:
        logger.error(f"Error en predicción batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model/info", response_model=ModeloInfo)
async def info_modelo():
    """
    Devuelve información y métricas del modelo.
    Se accede en: http://localhost:8000/model/info
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")

    return ModeloInfo(
        nombre=predictor.model_name,
        version="1.0.0",
        f1_score=0.8860,
        accuracy=0.8881,
        precision=0.8961,
        recall=0.8762
    )