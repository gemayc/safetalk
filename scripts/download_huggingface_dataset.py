"""
Script para descargar datasets desde Hugging Face Hub.

Este script facilita la descarga de datasets de hate speech en español
directamente desde Hugging Face, sin necesidad de registros complicados.

Uso:
    # Ver datasets disponibles
    python scripts/download_huggingface_dataset.py --list

    # Descargar dataset específico
    python scripts/download_huggingface_dataset.py --dataset hate_speech_offensive
    
    # Descargar y convertir al formato SafeTalk
    python scripts/download_huggingface_dataset.py --dataset hate_speech_offensive --convert
"""

import argparse
from pathlib import Path
import pandas as pd


def list_recommended_datasets():
    """Lista datasets recomendados de Hugging Face."""
    datasets_info = [
        {
            "name": "hate_speech_offensive",
            "description": "Tweets clasificados como odio/ofensivo/neutro",
            "size": "~25k tweets",
            "labels": "hate_speech, offensive, neither"
        },
        {
            "name": "Paul/hatecheck-spanish",
            "description": "Dataset de evaluación para hate speech en español",
            "size": "~500 casos de prueba",
            "labels": "hateful, non-hateful"
        },
    ]
    
    print("\n🎯 Datasets Recomendados en Hugging Face:\n")
    for i, ds in enumerate(datasets_info, 1):
        print(f"{i}. {ds['name']}")
        print(f"   📝 {ds['description']}")
        print(f"   📊 Tamaño: {ds['size']}")
        print(f"   🏷️  Etiquetas: {ds['labels']}")
        print()
    
    print("💡 Buscar más: https://huggingface.co/datasets?language=language:es&search=hate")
    print()


def download_dataset(dataset_name: str, output_dir: Path):
    """
    Descarga un dataset desde Hugging Face.
    
    Args:
        dataset_name: Nombre del dataset en Hugging Face
        output_dir: Directorio donde guardar los archivos
    """
    try:
        from datasets import load_dataset
    except ImportError:
        print("❌ Error: La librería 'datasets' no está instalada.")
        print("Instálala con: uv pip install datasets")
        return None
    
    print(f"📥 Descargando dataset '{dataset_name}' desde Hugging Face...")
    
    try:
        dataset = load_dataset(dataset_name)
        print(f"✅ Dataset descargado exitosamente!")
        
        # Crear directorio de salida
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar cada split como CSV
        for split_name, split_data in dataset.items():
            output_file = output_dir / f"{split_name}.csv"
            df = pd.DataFrame(split_data)
            df.to_csv(output_file, index=False)
            print(f"   💾 Guardado: {output_file} ({len(df)} filas)")
        
        # Mostrar información del dataset
        print(f"\n📊 Información del dataset:")
        first_split = list(dataset.keys())[0]
        df_sample = pd.DataFrame(dataset[first_split])
        print(f"   Columnas: {df_sample.columns.tolist()}")
        print(f"\n   Primeras filas:")
        print(df_sample.head(3))
        
        return dataset
    
    except Exception as e:
        print(f"❌ Error al descargar dataset: {e}")
        print("\n💡 Verifica que el nombre del dataset sea correcto.")
        print("   Busca en: https://huggingface.co/datasets")
        return None


def convert_to_safetalk_format(input_file: Path, output_file: Path, text_col: str, label_col: str):
    """
    Convierte dataset descargado al formato SafeTalk.
    
    Args:
        input_file: Archivo CSV de entrada
        output_file: Archivo CSV de salida
        text_col: Nombre de la columna de texto
        label_col: Nombre de la columna de etiquetas
    """
    print(f"\n🔄 Convirtiendo al formato SafeTalk...")
    
    df = pd.read_csv(input_file)
    
    if text_col not in df.columns:
        print(f"❌ Error: Columna '{text_col}' no encontrada.")
        print(f"   Columnas disponibles: {df.columns.tolist()}")
        return
    
    if label_col not in df.columns:
        print(f"❌ Error: Columna '{label_col}' no encontrada.")
        print(f"   Columnas disponibles: {df.columns.tolist()}")
        return
    
    # Convertir etiquetas a binario (0/1)
    # Esto depende del dataset específico - puede requerir ajuste
    label_mapping = {
        'neither': 0, 'offensive': 1, 'hate_speech': 1,  # para hate_speech_offensive
        'non-hateful': 0, 'hateful': 1,  # para hatecheck
        0: 0, 1: 1,  # ya binario
    }
    
    result_df = pd.DataFrame({
        'text': df[text_col],
        'label': df[label_col].map(lambda x: label_mapping.get(x, x))
    })
    
    # Verificar que labels sean 0/1
    unique_labels = result_df['label'].unique()
    if not all(label in [0, 1] for label in unique_labels):
        print(f"\n⚠️  Advertencia: Las etiquetas no son binarias (0/1): {unique_labels}")
        print("   Puede que necesites ajustar el label_mapping en el script")
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_file, index=False)
    
    print(f"✅ Dataset convertido: {output_file}")
    print(f"   Total de muestras: {len(result_df)}")
    print(f"   Distribución de clases:")
    print(result_df['label'].value_counts())


def main():
    parser = argparse.ArgumentParser(description="Descargar datasets desde Hugging Face")
    parser.add_argument("--list", action="store_true", help="Listar datasets recomendados")
    parser.add_argument("--dataset", type=str, help="Nombre del dataset a descargar")
    parser.add_argument("--output", type=str, default="data/raw", 
                       help="Directorio de salida (default: data/raw)")
    parser.add_argument("--convert", action="store_true", 
                       help="Convertir automáticamente al formato SafeTalk")
    parser.add_argument("--text-col", type=str, default="text", 
                       help="Nombre de la columna de texto")
    parser.add_argument("--label-col", type=str, default="label",
                       help="Nombre de la columna de etiquetas")
    
    args = parser.parse_args()
    
    if args.list:
        list_recommended_datasets()
        return
    
    if not args.dataset:
        print("❌ Error: Debes especificar --dataset o usar --list")
        print("\nUso:")
        print("  python scripts/download_huggingface_dataset.py --list")
        print("  python scripts/download_huggingface_dataset.py --dataset hate_speech_offensive")
        return
    
    # Descargar dataset
    output_dir = Path(args.output)
    dataset = download_dataset(args.dataset, output_dir)
    
    if dataset is None:
        return
    
    # Convertir si se solicitó
    if args.convert:
        # Usar el split de entrenamiento por defecto
        train_split = 'train' if 'train' in dataset else list(dataset.keys())[0]
        input_file = output_dir / f"{train_split}.csv"
        output_file = Path("data/processed") / "train_converted.csv"
        
        convert_to_safetalk_format(input_file, output_file, args.text_col, args.label_col)
    
    print("\n🎉 ¡Listo! Ahora puedes usar tu dataset para entrenar.")
    print(f"\n📋 Próximos pasos:")
    print(f"   1. Explorar datos: jupyter lab notebooks/01_exploratory_analysis.ipynb")
    print(f"   2. Entrenar baseline: python scripts/train_baseline.py --data data/processed/train_converted.csv")


if __name__ == "__main__":
    main()
