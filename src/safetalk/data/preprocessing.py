"""
Preprocesamiento de texto para modelos de detección.
"""

import re
from typing import List


class TextPreprocessor:
    """
    Preprocesador de texto con técnicas específicas para español
    y contextos de mensajería juvenil.
    """
    
    def __init__(
        self,
        lowercase: bool = True,
        remove_urls: bool = True,
        remove_mentions: bool = False,
        remove_hashtags: bool = False,
        remove_emojis: bool = False
    ):
        """
        Inicializa el preprocesador.
        
        Args:
            lowercase: Convertir a minúsculas
            remove_urls: Eliminar URLs
            remove_mentions: Eliminar menciones (@usuario)
            remove_hashtags: Eliminar hashtags
            remove_emojis: Eliminar emojis
        """
        self.lowercase = lowercase
        self.remove_urls = remove_urls
        self.remove_mentions = remove_mentions
        self.remove_hashtags = remove_hashtags
        self.remove_emojis = remove_emojis
        
    def clean_text(self, text: str) -> str:
        """
        Limpia un texto aplicando todas las transformaciones configuradas.
        
        Args:
            text: Texto a limpiar
            
        Returns:
            Texto limpio
        """
        if not isinstance(text, str):
            return ""
            
        # Eliminar URLs
        if self.remove_urls:
            text = re.sub(r'http\S+|www\.\S+', '', text)
            
        # Eliminar menciones
        if self.remove_mentions:
            text = re.sub(r'@\w+', '', text)
            
        # Eliminar hashtags
        if self.remove_hashtags:
            text = re.sub(r'#\w+', '', text)
            
        # Eliminar emojis (simplificado)
        if self.remove_emojis:
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F300-\U0001F5FF"  # símbolos & pictogramas
                "\U0001F680-\U0001F6FF"  # transporte & símbolos de mapa
                "\U0001F1E0-\U0001F1FF"  # banderas
                "]+",
                flags=re.UNICODE
            )
            text = emoji_pattern.sub(r'', text)
            
        # Eliminar espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        
        # Lowercase
        if self.lowercase:
            text = text.lower()
            
        return text.strip()
    
    def clean_batch(self, texts: List[str]) -> List[str]:
        """
        Limpia múltiples textos.
        
        Args:
            texts: Lista de textos a limpiar
            
        Returns:
            Lista de textos limpios
        """
        return [self.clean_text(text) for text in texts]
