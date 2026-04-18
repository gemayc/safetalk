"""
Clase Dataset para cargar y gestionar datos de entrenamiento.
"""

from typing import Optional
from pathlib import Path
import pandas as pd
from torch.utils.data import Dataset
from datasets import Dataset as HFDataset


class BullyingDataset:
    """
    Gestor de datasets para detección de bullying.
    
    Carga y prepara datos desde archivos CSV/JSON para entrenamiento
    y evaluación de modelos.
    """
    
    def __init__(self, data_path: Path, text_column: str = "text", label_column: str = "label"):
        """
        Inicializa el dataset.
        
        Args:
            data_path: Ruta al archivo de datos (CSV o JSON)
            text_column: Nombre de la columna con texto
            label_column: Nombre de la columna con etiquetas
        """
        self.data_path = Path(data_path)
        self.text_column = text_column
        self.label_column = label_column
        self.df = None
        
    def load(self) -> pd.DataFrame:
        """Carga los datos desde el archivo."""
        if self.data_path.suffix == '.csv':
            self.df = pd.read_csv(self.data_path)
        elif self.data_path.suffix == '.json':
            self.df = pd.read_json(self.data_path)
        else:
            raise ValueError(f"Formato no soportado: {self.data_path.suffix}")
            
        return self.df
    
    def get_texts(self) -> list:
        """Retorna la lista de textos."""
        if self.df is None:
            self.load()
        return self.df[self.text_column].tolist()
    
    def get_labels(self) -> list:
        """Retorna la lista de etiquetas."""
        if self.df is None:
            self.load()
        return self.df[self.label_column].tolist()
    
    def to_huggingface_dataset(self) -> HFDataset:
        """Convierte a formato HuggingFace Dataset."""
        if self.df is None:
            self.load()
        return HFDataset.from_pandas(self.df)
    
    def split(self, test_size: float = 0.2, random_state: int = 42):
        """
        Divide el dataset en train/test.
        
        Args:
            test_size: Proporción del conjunto de test
            random_state: Semilla aleatoria
            
        Returns:
            Tupla (train_dataset, test_dataset)
        """
        from sklearn.model_selection import train_test_split
        
        if self.df is None:
            self.load()
            
        train_df, test_df = train_test_split(
            self.df,
            test_size=test_size,
            random_state=random_state,
            stratify=self.df[self.label_column]
        )
        
        train_dataset = BullyingDataset.__new__(BullyingDataset)
        train_dataset.df = train_df
        train_dataset.text_column = self.text_column
        train_dataset.label_column = self.label_column
        
        test_dataset = BullyingDataset.__new__(BullyingDataset)
        test_dataset.df = test_df
        test_dataset.text_column = self.text_column
        test_dataset.label_column = self.label_column
        
        return train_dataset, test_dataset
