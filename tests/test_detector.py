"""
Tests básicos para el detector de bullying.
"""

import pytest
from safetalk.detector import BullyingDetector


def test_detector_initialization():
    """Test de inicialización del detector."""
    detector = BullyingDetector(model_type="beto")
    assert detector.model_type == "beto"
    assert detector.threshold == 0.7


def test_detector_baseline_initialization():
    """Test de inicialización con modelo baseline."""
    detector = BullyingDetector(model_type="baseline", threshold=0.8)
    assert detector.model_type == "baseline"
    assert detector.threshold == 0.8


# TODO: Añadir más tests cuando los modelos estén implementados
