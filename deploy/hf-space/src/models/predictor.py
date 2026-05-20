"""
Predictor unificado para detección de bullying.

Este módulo decide de dónde cargar el modelo:
1. Si está en el PC local, lo usa directamente.
2. Si NO está, lo descarga automáticamente desde Hugging Face Hub.
"""

from pathlib import Path
from typing import Dict, List
import logging

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from .beto_classifier import BETOClassifier

logger = logging.getLogger(__name__)

# Nombre de tu modelo en Hugging Face Hub
HF_REPO = "Gemita284/safetalk-beto"


class BullyingPredictor:
    """
    Predictor que carga BETO desde local o desde Hugging Face.
    """

    def __init__(self, models_dir: str = "models"):
        """
        Inicializa el predictor.

        Args:
            models_dir: Carpeta donde buscar/guardar el modelo local
        """
        self.models_dir = Path(models_dir)
        self.model = None
        self.model_name = None

        # Al crear el predictor, carga el modelo
        self._load_model()

    def _load_model(self):
        """
        Carga el modelo: primero intenta local, si no, descarga de HF.
        """
        # Rutas donde debería estar el modelo en local
        beto_model_path = self.models_dir / "beto" / "modelo"
        beto_tokenizer_path = self.models_dir / "beto" / "tokenizer"

        # OPCIÓN 1: ¿Está el modelo en el PC local?
        if beto_model_path.exists() and beto_tokenizer_path.exists():
            logger.info("Modelo BETO encontrado en local. Cargando...")
            self.model = BETOClassifier(
                str(beto_model_path),
                str(beto_tokenizer_path)
            )
            self.model_name = "BETO (local)"
            logger.info("Modelo BETO local cargado correctamente")
            return

        # OPCIÓN 2: No está local -> descargar de Hugging Face
        logger.info("Modelo BETO no encontrado en local")
        logger.info(f"Descargando desde Hugging Face: {HF_REPO}")
        logger.info("(La primera vez tarda unos minutos, ~440 MB)")

        try:
            # Descargar tokenizer (está en la subcarpeta 'tokenizer')
            tokenizer = AutoTokenizer.from_pretrained(
                HF_REPO,
                subfolder="tokenizer"
            )

            # Descargar modelo (está en la subcarpeta 'modelo')
            model = AutoModelForSequenceClassification.from_pretrained(
                HF_REPO,
                subfolder="modelo"
            )

            # Crear las carpetas locales para guardar el modelo
            beto_model_path.mkdir(parents=True, exist_ok=True)
            beto_tokenizer_path.mkdir(parents=True, exist_ok=True)

            # Guardar en local para no tener que descargarlo otra vez
            tokenizer.save_pretrained(str(beto_tokenizer_path))
            model.save_pretrained(str(beto_model_path))

            logger.info("Modelo descargado y guardado en local")

            # Ahora cargarlo con nuestra clase
            self.model = BETOClassifier(
                str(beto_model_path),
                str(beto_tokenizer_path)
            )
            self.model_name = "BETO (descargado de Hugging Face)"
            logger.info("Modelo BETO cargado correctamente")
            return

        except Exception as e:
            logger.error(f"Error al descargar el modelo: {e}")
            raise RuntimeError(
                f"No se pudo cargar el modelo ni local ni desde Hugging Face. "
                f"Error: {e}"
            )

    def predict(self, text: str) -> Dict[str, any]:
        """
        Predice si un texto es ofensivo.

        Args:
            text: Texto a clasificar

        Returns:
            Diccionario con la predicción
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
        """Devuelve información del modelo cargado."""
        return {
            "nombre": self.model_name,
            "repositorio_hf": HF_REPO,
            "disponible": self.model is not None
        }