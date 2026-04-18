"""
Tests para el preprocesamiento de texto.
"""

import pytest
from safetalk.data.preprocessing import TextPreprocessor


def test_lowercase():
    """Test de conversión a minúsculas."""
    preprocessor = TextPreprocessor(lowercase=True)
    result = preprocessor.clean_text("HOLA Mundo")
    assert result == "hola mundo"


def test_remove_urls():
    """Test de eliminación de URLs."""
    preprocessor = TextPreprocessor(remove_urls=True)
    text = "Mira esto https://example.com es interesante"
    result = preprocessor.clean_text(text)
    assert "https://example.com" not in result


def test_remove_mentions():
    """Test de eliminación de menciones."""
    preprocessor = TextPreprocessor(remove_mentions=True)
    text = "Hola @usuario que tal"
    result = preprocessor.clean_text(text)
    assert "@usuario" not in result


def test_batch_processing():
    """Test de procesamiento en lote."""
    preprocessor = TextPreprocessor(lowercase=True)
    texts = ["HOLA", "MUNDO", "Python"]
    results = preprocessor.clean_batch(texts)
    assert results == ["hola", "mundo", "python"]
