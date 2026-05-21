"""
Esquemas de datos para la API REST.

Define la estructura de las peticiones (input) y respuestas (output)
usando Pydantic, que valida los datos automáticamente.
"""

from pydantic import BaseModel, Field
from typing import List, Dict


class TextoInput(BaseModel):
    """
    Estructura de entrada: un solo texto a clasificar.

    Ejemplo de lo que el usuario envía:
        { "texto": "eres un gilipollas" }
    """
    texto: str = Field(
        ...,                                    # ... significa "obligatorio"
        min_length=1,                           # Mínimo 1 carácter
        max_length=500,                         # Máximo 500 caracteres
        description="Texto a clasificar"
    )

    class Config:
        # Ejemplo que aparecerá en la documentación automática
        json_schema_extra = {
            "example": {
                "texto": "eres un gilipollas"
            }
        }


class TextosInput(BaseModel):
    """
    Estructura de entrada: varios textos a la vez.

    Ejemplo:
        { "textos": ["hola", "eres tonto", "buenos días"] }
    """
    textos: List[str] = Field(
        ...,
        min_items=1,                            # Al menos 1 texto
        max_items=100,                          # Máximo 100 textos
        description="Lista de textos a clasificar"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "textos": [
                    "eres un gilipollas",
                    "hola qué tal",
                    "vete a la mierda"
                ]
            }
        }


class Prediccion(BaseModel):
    """
    Estructura de salida: el resultado de una predicción.

    Esto es lo que la API devuelve al usuario.
    """
    texto: str
    prediccion: str = Field(
        ...,
        description="Resultado: 'ofensivo' o 'no_ofensivo'"
    )
    confianza: float = Field(
        ...,
        ge=0.0,                                 # ge = greater or equal (>= 0)
        le=1.0,                                 # le = less or equal (<= 1)
        description="Confianza de la predicción (entre 0 y 1)"
    )
    probabilidades: Dict[str, float]
    modelo_usado: str

    class Config:
        json_schema_extra = {
            "example": {
                "texto": "eres un gilipollas",
                "prediccion": "ofensivo",
                "confianza": 0.996,
                "probabilidades": {
                    "no_ofensivo": 0.004,
                    "ofensivo": 0.996
                },
                "modelo_usado": "BETO (local)"
            }
        }


class PrediccionBatch(BaseModel):
    """
    Estructura de salida: resultado de varias predicciones.
    """
    predicciones: List[Prediccion]
    total: int
    modelo_usado: str


class ModeloInfo(BaseModel):
    """
    Información sobre el modelo cargado y sus métricas.
    """
    nombre: str
    version: str = "1.0.0"
    f1_score: float = 0.8860
    accuracy: float = 0.8881
    precision: float = 0.8961
    recall: float = 0.8762