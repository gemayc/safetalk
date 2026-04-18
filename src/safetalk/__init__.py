"""
SafeTalk - Sistema de detección automática de bullying y discurso de odio en español.

Este paquete proporciona modelos y herramientas para detectar contenido dañino
en mensajes de texto en plataformas digitales donde interactúan jóvenes.
"""

__version__ = "0.1.0"
__author__ = "SafeTalk Team"

from safetalk.detector import BullyingDetector

__all__ = ["BullyingDetector"]
