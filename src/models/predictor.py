"""
Predictor unificado para detección de bullying.

Carga automáticamente BETO V2_FINAL desde local o desde
Hugging Face Hub si no está disponible localmente.

V2_FINAL mejoras sobre V1:
   - Preprocesado anti-ofuscación (leetspeak, unicode, etc.)
   - Layer Freezing (capas 0-7 congeladas)
   - Early Stopping
   - Overfitting reducido: 9% → 2.16%
   - Precision mejorada: 89.61% → 92.73%
"""

from pathlib import Path
from typing import Dict, List
import logging

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)
from .beto_classifier import BETOClassifier

logger = logging.getLogger(__name__)

# ========================================
# CONFIGURACIÓN
# ========================================

# Nombre del modelo en Hugging Face Hub
HF_REPO = "Gemita284/safetalk-beto-v2"

# Rutas locales (dentro de models/)
LOCAL_MODEL_SUBDIR     = "beto_v2_final/modelo"
LOCAL_TOKENIZER_SUBDIR = "beto_v2_final/tokenizer"


class BullyingPredictor:
    """
    Predictor que carga BETO V2_FINAL desde local
    o lo descarga automáticamente de Hugging Face Hub.
    """

    def __init__(self, models_dir: str = "models"):
        """
        Inicializa el predictor.

        Args:
            models_dir: Carpeta raíz donde buscar el modelo local
        """
        self.models_dir   = Path(models_dir)
        self.model        = None
        self.model_name   = None

        self._load_model()

    def _load_model(self):
        """
        Carga el modelo:
        1. Intenta cargar desde local (models/beto_v2_final/)
        2. Si no está, lo descarga de Hugging Face Hub
        """
        beto_model_path     = self.models_dir / LOCAL_MODEL_SUBDIR
        beto_tokenizer_path = self.models_dir / LOCAL_TOKENIZER_SUBDIR

        # ── OPCIÓN 1: Modelo local ──────────────────────────────
        if beto_model_path.exists() and beto_tokenizer_path.exists():
            logger.info("Modelo BETO V2_FINAL encontrado en local. Cargando...")

            self.model = BETOClassifier(
                str(beto_model_path),
                str(beto_tokenizer_path)
            )
            self.model_name = "BETO V2_FINAL (local)"
            logger.info("✅ Modelo BETO V2_FINAL local cargado")
            return

        # ── OPCIÓN 2: Descargar de Hugging Face ─────────────────
        logger.info(f"Modelo no encontrado en local.")
        logger.info(f"Descargando desde Hugging Face: {HF_REPO}")
        logger.info("(Primera vez: tarda unos minutos, ~440 MB)")

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                HF_REPO,
                subfolder="tokenizer"
            )
            model = AutoModelForSequenceClassification.from_pretrained(
                HF_REPO,
                subfolder="modelo"
            )

            # Guardar en local para próximas veces
            beto_model_path.mkdir(parents=True, exist_ok=True)
            beto_tokenizer_path.mkdir(parents=True, exist_ok=True)

            tokenizer.save_pretrained(str(beto_tokenizer_path))
            model.save_pretrained(str(beto_model_path))

            logger.info(f"✅ Modelo descargado y guardado en local")

            self.model = BETOClassifier(
                str(beto_model_path),
                str(beto_tokenizer_path)
            )
            self.model_name = "BETO V2_FINAL (descargado de HF)"
            return

        except Exception as e:
            logger.error(f"Error al descargar el modelo: {e}")
            raise RuntimeError(
                f"No se pudo cargar el modelo ni local ni desde HF. "
                f"Repo: {HF_REPO}. Error: {e}"
            )

    def predict(self, text: str) -> Dict[str, any]:
        """
        Predice si un texto es ofensivo.

        Args:
            text: Texto a clasificar

        Returns:
            Dict con prediccion, confianza, probabilidades
        """
        resultado = self.model.predict(text)
        resultado["modelo_usado"] = self.model_name
        return resultado

    def predict_batch(self, texts: List[str]) -> List[Dict[str, any]]:
        """
        Predice varios textos a la vez.

        Args:
            texts: Lista de textos

        Returns:
            Lista de predicciones
        """
        resultados = self.model.predict_batch(texts)
        for r in resultados:
            r["modelo_usado"] = self.model_name
        return resultados

    def get_model_info(self) -> Dict[str, any]:
        """Información del modelo cargado"""
        return {
            "nombre": self.model_name,
            "repositorio_hf": HF_REPO,
            "disponible": self.model is not None
        }