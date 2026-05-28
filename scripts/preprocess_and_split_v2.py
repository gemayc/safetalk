"""
Aplica el preprocesado y genera el split para BETO V2.

Reproduce el mismo split del notebook 06 (random_state=42)
aplicando el TextPreprocessor nuevo (anti-ofuscación).

Uso (desde la raíz del proyecto):
    python scripts/preprocess_and_split_v2.py

Entrada:
    data/processed/dataset_safetalk_final.csv

Salidas:
    data/processed/train_v2.csv
    data/processed/val_v2.csv
    data/processed/test_v2.csv
"""

import sys
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.preprocessing import TextPreprocessor


# ========================================
# CONFIGURACIÓN (idéntica al notebook 06)
# ========================================

INPUT_FILE  = "data/processed/dataset_safetalk_final.csv"
OUTPUT_TRAIN = "data/processed/train_v2.csv"
OUTPUT_VAL   = "data/processed/val_v2.csv"
OUTPUT_TEST  = "data/processed/test_v2.csv"

RANDOM_STATE         = 42
TEST_SIZE_FIRST      = 0.15      # 15% test
TEST_SIZE_SECOND     = 0.1765    # 15% val del 85% restante

PREPROCESSOR = TextPreprocessor(
    lowercase=True,
    remove_urls=True,
    remove_mentions=True,
    remove_hashtags=True,
    remove_rt=True,
    remove_emojis=True,
    normalize_unicode=True,
    normalize_leetspeak=True,
    collapse_repeated=True,
    remove_letter_separators=False,
)


def main():
    print("=" * 80)
    print("PREPROCESADO + SPLIT PARA BETO V2")
    print("=" * 80)

    # ----------------------------------------
    # PASO 1: Cargar dataset
    # ----------------------------------------
    print(f"\n📂 PASO 1: Cargando {INPUT_FILE}...")

    if not Path(INPUT_FILE).exists():
        print(f"❌ ERROR: No se encuentra {INPUT_FILE}")
        sys.exit(1)

    df = pd.read_csv(INPUT_FILE)
    print(f"  ✅ {len(df)} ejemplos cargados")

    # Quedarse solo con texto y label
    if "fuente" in df.columns:
        df = df[["texto", "label"]]
        print(f"  ℹ️  Columna 'fuente' eliminada")

    print(f"\n  Distribución de clases:")
    print(f"    Clase 0 (no ofensivo): {(df['label']==0).sum()} ({(df['label']==0).mean()*100:.1f}%)")
    print(f"    Clase 1 (ofensivo):    {(df['label']==1).sum()} ({(df['label']==1).mean()*100:.1f}%)")

    # ----------------------------------------
    # PASO 2: Aplicar preprocesado
    # ----------------------------------------
    print(f"\n🔧 PASO 2: Aplicando TextPreprocessor...")

    textos_originales = df["texto"].copy()
    df["texto"] = PREPROCESSOR.clean_batch(df["texto"].tolist())

    # Eliminar vacíos (por seguridad)
    filas_antes = len(df)
    df = df[df["texto"].str.strip() != ""]
    eliminadas = filas_antes - len(df)

    cambios = (textos_originales.loc[df.index] != df["texto"]).sum()

    print(f"  ✅ Preprocesado completado")
    print(f"  📝 Textos modificados: {cambios} ({cambios/len(df)*100:.1f}%)")

    if eliminadas > 0:
        print(f"  ⚠️  Filas eliminadas (vacías): {eliminadas}")
    else:
        print(f"  ✅ Sin filas vacías")

    # ----------------------------------------
    # PASO 3: Split (igual que notebook 06)
    # ----------------------------------------
    print(f"\n✂️  PASO 3: Haciendo split (random_state={RANDOM_STATE})...")

    X = df["texto"]
    y = df["label"]

    # Split 1: train+val vs test
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE_FIRST,
        random_state=RANDOM_STATE,
        stratify=y
    )

    # Split 2: train vs val
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=TEST_SIZE_SECOND,
        random_state=RANDOM_STATE,
        stratify=y_train_val
    )

    # ----------------------------------------
    # PASO 4: Guardar
    # ----------------------------------------
    print(f"\n💾 PASO 4: Guardando archivos...")

    df_train = pd.DataFrame({"texto": X_train.values, "label": y_train.values})
    df_val   = pd.DataFrame({"texto": X_val.values,   "label": y_val.values})
    df_test  = pd.DataFrame({"texto": X_test.values,  "label": y_test.values})

    df_train.to_csv(OUTPUT_TRAIN, index=False, encoding="utf-8")
    df_val.to_csv(OUTPUT_VAL,     index=False, encoding="utf-8")
    df_test.to_csv(OUTPUT_TEST,   index=False, encoding="utf-8")

    print(f"  ✅ {OUTPUT_TRAIN}")
    print(f"  ✅ {OUTPUT_VAL}")
    print(f"  ✅ {OUTPUT_TEST}")

    # ----------------------------------------
    # RESUMEN FINAL
    # ----------------------------------------
    print(f"\n{'='*80}")
    print("✅ COMPLETADO")
    print("=" * 80)

    total = len(df_train) + len(df_val) + len(df_test)

    print(f"\n  {'Split':<8} {'Ejemplos':>10} {'Porcentaje':>12} {'Ofensivos':>12}")
    print(f"  {'-'*8} {'-'*10} {'-'*12} {'-'*12}")
    print(f"  {'Train':<8} {len(df_train):>10} {len(df_train)/total*100:>11.1f}% {df_train['label'].mean()*100:>11.1f}%")
    print(f"  {'Val':<8} {len(df_val):>10} {len(df_val)/total*100:>11.1f}% {df_val['label'].mean()*100:>11.1f}%")
    print(f"  {'Test':<8} {len(df_test):>10} {len(df_test)/total*100:>11.1f}% {df_test['label'].mean()*100:>11.1f}%")
    print(f"  {'-'*8} {'-'*10} {'-'*12} {'-'*12}")
    print(f"  {'TOTAL':<8} {total:>10}")

    # Comparar con V1
    train_v1 = "data/processed/train.csv"
    if Path(train_v1).exists():
        df_v1 = pd.read_csv(train_v1)
        print(f"\n  🔍 Comparación con V1:")
        print(f"     Train V1: {len(df_v1)} | Train V2: {len(df_train)}")

        if len(df_v1) == len(df_train):
            print(f"     ✅ Mismo tamaño → comparación V1 vs V2 PERFECTAMENTE JUSTA")
        else:
            print(f"     ⚠️  Tamaños diferentes (filas eliminadas en preprocesado)")

    print(f"\n🚀 Siguiente paso: subir estos 3 archivos a Colab para entrenar V2")
    print("=" * 80)


if __name__ == "__main__":
    main()