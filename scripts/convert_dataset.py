"""
Script para convertir datasets de diferentes formatos al formato SafeTalk.

El formato esperado de SafeTalk es:
    text,label
    "mensaje de texto",0
    "otro mensaje",1

Uso:
    python scripts/convert_dataset.py --input data/raw/train.csv --output data/processed/train_safetalk.csv
"""

import argparse
import pandas as pd
from pathlib import Path


def convert_hateval_format(input_path: Path, output_path: Path):
    """
    Convierte formato HatEval/CodaLab a formato SafeTalk.
    
    HatEval suele tener columnas como: 'text', 'HS' (hate speech)
    """
    df = pd.read_csv(input_path)
    
    print(f"Columnas encontradas: {df.columns.tolist()}")
    print(f"Primeras filas:")
    print(df.head())
    
    # Detectar columna de texto (puede variar)
    text_col = None
    for col in ['text', 'tweet', 'comment', 'message', 'content']:
        if col in df.columns:
            text_col = col
            break
    
    if text_col is None:
        raise ValueError(f"No se encontró columna de texto. Columnas: {df.columns.tolist()}")
    
    # Detectar columna de etiqueta
    label_col = None
    for col in ['HS', 'label', 'hate_speech', 'toxic', 'offensive']:
        if col in df.columns:
            label_col = col
            break
    
    if label_col is None:
        raise ValueError(f"No se encontró columna de etiqueta. Columnas: {df.columns.tolist()}")
    
    # Crear DataFrame en formato SafeTalk
    result_df = pd.DataFrame({
        'text': df[text_col],
        'label': df[label_col].astype(int)
    })
    
    # Guardar
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_path, index=False)
    
    # Estadísticas
    print(f"\n✅ Dataset convertido exitosamente!")
    print(f"📊 Total de muestras: {len(result_df)}")
    print(f"📊 Distribución de clases:")
    print(result_df['label'].value_counts())
    print(f"📁 Guardado en: {output_path}")


def convert_generic_format(input_path: Path, output_path: Path, text_col: str, label_col: str):
    """
    Convierte formato genérico especificando las columnas.
    """
    df = pd.read_csv(input_path)
    
    if text_col not in df.columns:
        raise ValueError(f"Columna '{text_col}' no encontrada. Columnas disponibles: {df.columns.tolist()}")
    
    if label_col not in df.columns:
        raise ValueError(f"Columna '{label_col}' no encontrada. Columnas disponibles: {df.columns.tolist()}")
    
    # Crear DataFrame en formato SafeTalk
    result_df = pd.DataFrame({
        'text': df[text_col],
        'label': df[label_col].astype(int)
    })
    
    # Guardar
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_path, index=False)
    
    print(f"\n✅ Dataset convertido exitosamente!")
    print(f"📊 Total de muestras: {len(result_df)}")
    print(f"📊 Distribución de clases:")
    print(result_df['label'].value_counts())
    print(f"📁 Guardado en: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Convertir dataset al formato SafeTalk")
    parser.add_argument("--input", type=str, required=True, help="Archivo CSV de entrada")
    parser.add_argument("--output", type=str, required=True, help="Archivo CSV de salida")
    parser.add_argument("--text-col", type=str, help="Nombre de la columna de texto (opcional)")
    parser.add_argument("--label-col", type=str, help="Nombre de la columna de etiquetas (opcional)")
    parser.add_argument("--mode", type=str, default="auto", 
                       choices=["auto", "manual"],
                       help="Modo: 'auto' detecta columnas automáticamente, 'manual' usa text-col y label-col")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"❌ Error: El archivo {input_path} no existe")
        return
    
    try:
        if args.mode == "auto":
            convert_hateval_format(input_path, output_path)
        else:
            if not args.text_col or not args.label_col:
                print("❌ Error: En modo 'manual' debes especificar --text-col y --label-col")
                return
            convert_generic_format(input_path, output_path, args.text_col, args.label_col)
    
    except Exception as e:
        print(f"❌ Error al convertir dataset: {e}")
        print("\n💡 Intenta con modo 'manual' especificando las columnas:")
        print("   python scripts/convert_dataset.py --input ... --output ... --mode manual --text-col NOMBRE --label-col NOMBRE")


if __name__ == "__main__":
    main()
