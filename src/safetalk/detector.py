"""
Módulo principal para la detección de bullying y discurso de odio.
"""

from typing import Dict, Optional
from pathlib import Path


class BullyingDetector:
    """
    Detector principal para identificar bullying y discurso de odio en texto.
    
    Combina modelos baseline (TF-IDF + SVM) y modelos fine-tuned (BETO)
    para clasificar mensajes como potencialmente dañinos.
    """
    
    def __init__(
        self,
        model_type: str = "beto",
        model_path: Optional[Path] = None,
        threshold: float = 0.7
    ):
        """
        Inicializa el detector.
        
        Args:
            model_type: Tipo de modelo a usar ('baseline' o 'beto')
            model_path: Ruta al modelo pre-entrenado
            threshold: Umbral de confianza para clasificación positiva
        """
        self.model_type = model_type
        self.model_path = model_path
        self.threshold = threshold
        self.model = None
        
    def load_model(self):
        """Carga el modelo especificado."""
        raise NotImplementedError("Método a implementar")
        
    def predict(self, text: str) -> Dict[str, float]:
        """
        Predice si un texto contiene bullying o discurso de odio.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Diccionario con scores de clasificación
        """
        raise NotImplementedError("Método a implementar")
        
    def predict_batch(self, texts: list[str]) -> list[Dict[str, float]]:
        """
        Predice para múltiples textos.
        
        Args:
            texts: Lista de textos a analizar
            
        Returns:
            Lista de diccionarios con scores de clasificación
        """
        raise NotImplementedError("Método a implementar")
