"""
Compara predicciones del modelo BETO CON y SIN normalización.

Primera ejecución: descarga el modelo desde HuggingFace (~440 MB).
Ejecuciones siguientes: usa el modelo cacheado en models/beto/.

Uso:
    uv run python scripts/probar_normalizacion.py
"""

import sys
from pathlib import Path

# Permitir imports desde la raíz del repo
sys.path.insert(0, str(Path(__file__).parent.parent))

from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src.data.preprocessing import TextPreprocessor
from src.models.beto_classifier import BETOClassifier

HF_REPO = "Gemita284/safetalk-beto"
LOCAL_MODEL = Path("models/beto/modelo")
LOCAL_TOKENIZER = Path("models/beto/tokenizer")


# Preprocesador "passthrough": todo desactivado, simula el comportamiento previo
PASSTHROUGH = TextPreprocessor(
    lowercase=False,
    remove_urls=False,
    remove_mentions=False,
    remove_hashtags=False,
    remove_rt=False,
    remove_emojis=False,
    normalize_unicode=False,
    normalize_leetspeak=False,
    collapse_repeated=False,
)


# Pares (original, variantes ofuscadas)
CASOS = [
    ("eres un gilipollas", ["eres un gillip0llas", "eres un g1l1p0ll4s"]),
    ("eres un cabrón", ["eres un c4brón", "eres un c4br0n"]),
    ("eres una puta", ["eres una put@", "eres una puuuuuta"]),
    ("eres un idiota", ["eres un 1d10t4"]),
    ("eres un maricón", ["eres un m4ricón", "eres un m4r1c0n"]),
    # Caso negativo: NO debe marcarse como ofensivo
    ("hola, ¿cómo estás hoy?", []),
]


def imprimir_prediccion(etiqueta: str, texto: str, resultado: dict) -> None:
    pred = resultado["prediccion"]
    conf = resultado["confianza"]
    icono = "🟥" if pred == "ofensivo" else "🟩"
    print(f"  {icono} [{etiqueta:8}] {texto!r:45} → {pred:12} ({conf:.2%})")


def asegurar_modelo_local() -> None:
    """Descarga el modelo desde HuggingFace si los pesos no están presentes."""
    pesos = LOCAL_MODEL / "model.safetensors"
    if pesos.exists():
        print(f"Modelo ya presente en {LOCAL_MODEL}")
        return

    print(f"Descargando modelo desde {HF_REPO} (~440 MB)...")
    tokenizer = AutoTokenizer.from_pretrained(HF_REPO, subfolder="tokenizer")
    model = AutoModelForSequenceClassification.from_pretrained(HF_REPO, subfolder="modelo")
    assert tokenizer is not None and model is not None, "Fallo descargando desde HF"

    LOCAL_TOKENIZER.mkdir(parents=True, exist_ok=True)
    LOCAL_MODEL.mkdir(parents=True, exist_ok=True)
    tokenizer.save_pretrained(str(LOCAL_TOKENIZER))
    model.save_pretrained(str(LOCAL_MODEL))
    print("Descarga completa.")


def main() -> None:
    print("=" * 80)
    print("Cargando modelo BETO...")
    print("=" * 80)

    asegurar_modelo_local()

    classifier_con_norm = BETOClassifier(str(LOCAL_MODEL), str(LOCAL_TOKENIZER))
    classifier_sin_norm = BETOClassifier(
        str(LOCAL_MODEL),
        str(LOCAL_TOKENIZER),
        preprocessor=PASSTHROUGH,
    )

    print(f"\nModelo cargado desde: {LOCAL_MODEL}\n")

    aciertos_con_norm = 0
    aciertos_sin_norm = 0
    total_ofuscados = 0

    for original, variantes in CASOS:
        print("-" * 80)
        print(f"FRASE ORIGINAL: {original!r}")

        res_orig = classifier_con_norm.predict(original)
        imprimir_prediccion("baseline", original, res_orig)

        for variante in variantes:
            total_ofuscados += 1
            res_sin = classifier_sin_norm.predict(variante)
            res_con = classifier_con_norm.predict(variante)
            imprimir_prediccion("SIN norm", variante, res_sin)
            imprimir_prediccion("CON norm", variante, res_con)

            esperado = res_orig["prediccion"]
            if res_sin["prediccion"] == esperado:
                aciertos_sin_norm += 1
            if res_con["prediccion"] == esperado:
                aciertos_con_norm += 1
        print()

    print("=" * 80)
    print("RESUMEN sobre variantes ofuscadas:")
    print(f"  SIN normalización: {aciertos_sin_norm}/{total_ofuscados} aciertos")
    print(f"  CON normalización: {aciertos_con_norm}/{total_ofuscados} aciertos")
    print(f"  Mejora: +{aciertos_con_norm - aciertos_sin_norm} casos recuperados")
    print("=" * 80)


if __name__ == "__main__":
    main()
