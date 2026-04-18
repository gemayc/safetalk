"""
Script de entrenamiento para el modelo baseline (TF-IDF + SVM).

Uso:
    python scripts/train_baseline.py --data data/processed/train.csv --output models/baseline.pkl
"""

import argparse
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

from safetalk.models.baseline import BaselineModel
from safetalk.data.preprocessing import TextPreprocessor


def main():
    parser = argparse.ArgumentParser(description="Entrenar modelo baseline")
    parser.add_argument("--data", type=str, required=True, help="Ruta al archivo de datos CSV")
    parser.add_argument("--output", type=str, default="models/baseline.pkl", help="Ruta de salida del modelo")
    parser.add_argument("--test-size", type=float, default=0.2, help="Proporción de test")
    parser.add_argument("--max-features", type=int, default=5000, help="Máximo de features TF-IDF")
    
    args = parser.parse_args()
    
    # Cargar datos
    print(f"Cargando datos desde {args.data}...")
    df = pd.read_csv(args.data)
    
    # Preprocesar
    print("Preprocesando textos...")
    preprocessor = TextPreprocessor(lowercase=True, remove_urls=True)
    df['clean_text'] = preprocessor.clean_batch(df['text'].tolist())
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        df['clean_text'],
        df['label'],
        test_size=args.test_size,
        random_state=42,
        stratify=df['label']
    )
    
    # Entrenar modelo
    print("Entrenando modelo baseline...")
    model = BaselineModel(max_features=args.max_features)
    model.train(X_train, y_train)
    
    # Evaluar
    print("\nEvaluando modelo...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nAccuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Guardar modelo
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(output_path)
    print(f"\nModelo guardado en: {output_path}")


if __name__ == "__main__":
    main()
