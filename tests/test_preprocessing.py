"""
Tests para el preprocesamiento de texto.
"""

import pytest

from src.data.preprocessing import TextPreprocessor


# ---------- Tests heredados (limpieza tipo notebook 03) ----------

def test_lowercase():
    preprocessor = TextPreprocessor(lowercase=True)
    assert preprocessor.clean_text("HOLA Mundo") == "hola mundo"


def test_remove_urls():
    preprocessor = TextPreprocessor(remove_urls=True)
    text = "Mira esto https://example.com es interesante"
    assert "https://example.com" not in preprocessor.clean_text(text)


def test_remove_mentions():
    preprocessor = TextPreprocessor(remove_mentions=True)
    assert "@usuario" not in preprocessor.clean_text("Hola @usuario que tal")


def test_batch_processing():
    preprocessor = TextPreprocessor(lowercase=True)
    assert preprocessor.clean_batch(["HOLA", "MUNDO", "Python"]) == ["hola", "mundo", "python"]


# ---------- Normalización contra ofuscación (la razón de esta tarea) ----------

@pytest.mark.parametrize(
    "ofuscado,esperado",
    [
        ("gillip0llas", "gillipollas"),  # 0 → o
        ("g1l1p0ll4s", "gilipollas"),    # leetspeak completo
        ("c4br0n", "cabron"),
        ("put@", "puta"),                # @ → a
        ("1d10t4", "idiota"),
        ("m4r1c0n", "maricon"),
    ],
)
def test_leetspeak_normalization(ofuscado, esperado):
    preprocessor = TextPreprocessor()
    assert preprocessor.clean_text(ofuscado) == esperado


def test_collapse_repeated_chars():
    preprocessor = TextPreprocessor()
    # Deja máximo 2 repeticiones consecutivas para preservar "perro", "cuello", etc.
    assert preprocessor.clean_text("puuuuuta") == "puuta"
    assert preprocessor.clean_text("tontoooooo") == "tontoo"
    assert preprocessor.clean_text("perro") == "perro"  # no rompe palabras válidas


def test_letter_separators_optin():
    # Off por defecto (puede romper siglas)
    default = TextPreprocessor()
    assert default.clean_text("g.i.l.i.p.o.l.l.a.s") != "gilipollas"

    # On explícito: junta letras separadas y luego normaliza
    aggressive = TextPreprocessor(remove_letter_separators=True)
    assert aggressive.clean_text("g.i.l.i.p.o.l.l.a.s") == "gilipollas"
    assert aggressive.clean_text("g i l i p o l l a s") == "gilipollas"


# ---------- Tests negativos: no romper texto inocente ----------

def test_does_not_break_innocent_text():
    preprocessor = TextPreprocessor()
    # Una frase normal en español, con acentos, debe quedar intacta (salvo lowercase)
    assert preprocessor.clean_text("Hola, ¿cómo estás?") == "hola, ¿cómo estás?"


def test_preserves_accented_chars():
    preprocessor = TextPreprocessor()
    out = preprocessor.clean_text("Camión, niño, año")
    for char in "áéíóúñ":
        # Verifica que el pipeline no destruye acentos castellanos
        pass
    assert "camión" in out
    assert "niño" in out
    assert "año" in out


def test_letter_separators_preserves_short_acronyms():
    # "U.S.A" tiene 3 letras → debajo del umbral (≥4), no se toca
    preprocessor = TextPreprocessor(remove_letter_separators=True)
    out = preprocessor.clean_text("Vive en U.S.A actualmente")
    assert "u.s.a" in out  # acrónimo preservado
