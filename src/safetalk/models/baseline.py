"""
Modelo baseline usando TF-IDF + SVM para detección de bullying.
"""

from typing import Optional
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline


class BaselineModel:
    """
    Modelo baseline que combina TF-IDF para extracción de features
    y SVM para clasificación binaria.
    """
    
    def __init__(self, max_features: int = 5000, C: float = 1.0):
        """
        Inicializa el modelo baseline.
        
        Args:
            max_features: Número máximo de features TF-IDF
            C: Parámetro de regularización de SVM
        """
        self.max_features = max_features
        self.C = C
        self.pipeline = self._build_pipeline()
        
    def _build_pipeline(self) -> Pipeline:
        """Construye el pipeline de TF-IDF + SVM."""
        return Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=self.max_features,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95
            )),
            ('clf', SVC(
                C=self.C,
                kernel='linear',
                probability=True,
                random_state=42
            ))
        ])
    
    def train(self, X_train, y_train):
        """Entrena el modelo con los datos proporcionados."""
        self.pipeline.fit(X_train, y_train)
        
    def predict(self, X):
        """Realiza predicciones."""
        return self.pipeline.predict(X)
        
    def predict_proba(self, X):
        """Retorna probabilidades de clasificación."""
        return self.pipeline.predict_proba(X)
    
    def save(self, path: Path):
        """Guarda el modelo entrenado."""
        joblib.dump(self.pipeline, path)
        
    def load(self, path: Path):
        """Carga un modelo previamente entrenado."""
        self.pipeline = joblib.load(path)
