"""
Preprocesamiento y normalización de texto para SafeTalk.

Centraliza la limpieza usada en entrenamiento (notebook 03) y añade
normalización adicional contra ofuscación adversarial (leetspeak,
repeticiones, separadores entre letras, homoglyphs unicode).

La misma instancia debe usarse en entrenamiento e inferencia para
evitar train/inference skew.
"""

from __future__ import annotations

import re
import unicodedata
from typing import List

# Mapa de leetspeak: dígitos y símbolos comunes → letra equivalente.
# Conservador a propósito: solo sustituciones de alta confianza.
LEETSPEAK_MAP = str.maketrans(
    {
        "0": "o",
        "1": "i",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
        "@": "a",
        "$": "s",
    }
)

# Caracteres permitidos tras eliminar emojis/símbolos raros.
# Coincide con la regex del notebook 03 para reproducir el dataset de entrenamiento.
_ALLOWED_CHARS_RE = re.compile(r"[^\w\s,.!?¿¡;:\-()áéíóúñÁÉÍÓÚÑüÜ]")

_URL_RE = re.compile(r"http\S+|www\.\S+")
_MENTION_RE = re.compile(r"@\w+")
_MENTION_SPACE_RE = re.compile(r"@\s+")
_MENTION_SYMBOL_RE = re.compile(r"@[^\w\s]+")
_HASHTAG_RE = re.compile(r"#(\w+)")
_RT_RE = re.compile(r"\bRT\b", flags=re.IGNORECASE)
_WHITESPACE_RE = re.compile(r"\s+")
_TRAILING_DOTS_RE = re.compile(r"\.\.\.+$")
_REPEATED_CHAR_RE = re.compile(r"(.)\1{2,}")

# Detecta secuencias del tipo "g.i.l.i.p" o "g i l i p" (≥4 letras sueltas
# unidas por un único separador) AISLADAS (no rodeadas por más letras).
# El lookbehind/lookahead evita que "en U.S.A" enganche la "n" de "en".
# Acrónimos de 3 letras como "U.S.A" siguen preservados por el umbral.
_LETTER_CLASS = r"A-Za-zÁÉÍÓÚÑÜáéíóúñü"
_LETTER_SEP_RE = re.compile(
    rf"(?<![{_LETTER_CLASS}])(?:[{_LETTER_CLASS}][\s.\-_*]){{3,}}[{_LETTER_CLASS}](?![{_LETTER_CLASS}])"
)


class TextPreprocessor:
    """Pipeline de normalización de texto.

    Por defecto activa todas las limpiezas seguras. `remove_letter_separators`
    queda opt-in porque puede afectar siglas y abreviaturas legítimas.
    """

    def __init__(
        self,
        lowercase: bool = True,
        remove_urls: bool = True,
        remove_mentions: bool = True,
        remove_hashtags: bool = True,
        remove_rt: bool = True,
        remove_emojis: bool = True,
        normalize_unicode: bool = True,
        normalize_leetspeak: bool = True,
        collapse_repeated: bool = True,
        remove_letter_separators: bool = False,
    ) -> None:
        self.lowercase = lowercase
        self.remove_urls = remove_urls
        self.remove_mentions = remove_mentions
        self.remove_hashtags = remove_hashtags
        self.remove_rt = remove_rt
        self.remove_emojis = remove_emojis
        self.normalize_unicode = normalize_unicode
        self.normalize_leetspeak = normalize_leetspeak
        self.collapse_repeated = collapse_repeated
        self.remove_letter_separators = remove_letter_separators

    def clean_text(self, text: str) -> str:
        # Normalizar unicode primero para neutralizar homoglyphs antes del resto
        # de regex (NFKC es preferible a NFKD: combina caracteres y mantiene
        # forma compatible, sin romper acentos legítimos).
        if self.normalize_unicode:
            text = unicodedata.normalize("NFKC", text)

        if self.remove_urls:
            text = _URL_RE.sub("", text)

        if self.remove_mentions:
            text = _MENTION_RE.sub("", text)
            text = _MENTION_SPACE_RE.sub("", text)
            text = _MENTION_SYMBOL_RE.sub("", text)

        if self.remove_hashtags:
            text = _HASHTAG_RE.sub(r"\1", text)

        if self.remove_rt:
            text = _RT_RE.sub("", text)

        # Juntar letras separadas ANTES de leetspeak para que "g.1.l.1.p"
        # primero se vuelva "g1l1p" y luego "gilip".
        if self.remove_letter_separators:
            text = _LETTER_SEP_RE.sub(
                lambda m: re.sub(r"[\s.\-_*]", "", m.group()), text
            )

        if self.normalize_leetspeak:
            text = text.translate(LEETSPEAK_MAP)

        # Lowercase después de leetspeak porque el mapa solo tiene minúsculas;
        # si bajamos antes, "@" → "a" igual funciona pero queda más claro así.
        if self.lowercase:
            text = text.lower()

        if self.remove_emojis:
            text = _ALLOWED_CHARS_RE.sub("", text)

        if self.collapse_repeated:
            # "puuuuta" → "puuta" (deja máximo 2 repeticiones consecutivas)
            text = _REPEATED_CHAR_RE.sub(r"\1\1", text)

        # Limpieza final de whitespace (siempre)
        text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        text = _WHITESPACE_RE.sub(" ", text).strip()
        text = _TRAILING_DOTS_RE.sub("", text)

        return text

    def clean_batch(self, texts: List[str]) -> List[str]:
        return [self.clean_text(t) for t in texts]
