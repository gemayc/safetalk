"""
Script de fine-tuning para el modelo BETO.

Uso:
    python scripts/train_beto.py --data data/processed/train.csv --output models/beto-finetuned
"""

import argparse
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

from safetalk.models.beto_model import BETOModel
from safetalk.data.preprocessing import TextPreprocessor
from datasets import Dataset


def main():
    parser = argparse.ArgumentParser(description="Fine-tune BETO para detección de bullying")
    parser.add_argument("--data", type=str, required=True, help="Ruta al archivo de datos CSV")
    parser.add_argument("--output", type=str, default="models/beto-finetuned", help="Directorio de salida")
    parser.add_argument("--epochs", type=int, default=3, help="Número de épocas")
    parser.add_argument("--batch-size", type=int, default=16, help="Tamaño de batch")
    parser.add_argument("--learning-rate", type=float, default=2e-5, help="Learning rate")
    parser.add_argument("--test-size", type=float, default=0.2, help="Proporción de test")
    
    args = parser.parse_args()
    
    # Cargar datos
    print(f"Cargando datos desde {args.data}...")
    df = pd.read_csv(args.data)
    
    # Preprocesar (mínimo para BETO)
    print("Preprocesando textos...")
    preprocessor = TextPreprocessor(lowercase=False, remove_urls=True)
    df['clean_text'] = preprocessor.clean_batch(df['text'].tolist())
    
    # Split train/validation
    train_df, val_df = train_test_split(
        df,
        test_size=args.test_size,
        random_state=42,
        stratify=df['label']
    )
    
    # Convertir a HuggingFace Dataset
    train_dataset = Dataset.from_pandas(train_df[['clean_text', 'label']].rename(columns={'clean_text': 'text'}))
    val_dataset = Dataset.from_pandas(val_df[['clean_text', 'label']].rename(columns={'clean_text': 'text'}))
    
    # Inicializar y cargar modelo
    print("Cargando modelo BETO...")
    model = BETOModel()
    model.load_model()
    
    # Tokenizar datasets
    def tokenize_function(examples):
        return model.tokenizer(
            examples['text'],
            padding='max_length',
            truncation=True,
            max_length=model.max_length
        )
    
    train_dataset = train_dataset.map(tokenize_function, batched=True)
    val_dataset = val_dataset.map(tokenize_function, batched=True)
    
    # Entrenar
    print(f"\nIniciando fine-tuning por {args.epochs} épocas...")
    output_dir = Path(args.output)
    model.train(
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        output_dir=output_dir,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate
    )
    
    # Guardar modelo final
    model.save(output_dir / "final")
    print(f"\nModelo guardado en: {output_dir / 'final'}")


if __name__ == "__main__":
    main()
