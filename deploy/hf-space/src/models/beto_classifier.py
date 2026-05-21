"""
Clasificador BETO para detección de bullying.

Este módulo contiene la clase que carga el modelo BETO fine-tuned
y realiza predicciones sobre si un texto es ofensivo o no.
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, List
import logging

# Configurar logger para ver mensajes informativos
logger = logging.getLogger(__name__)


class BETOClassifier:
    """
    Clasificador basado en BETO fine-tuned para detectar bullying.

    Esta clase carga el modelo y el tokenizer, y proporciona métodos
    para predecir si un texto (o varios) son ofensivos.
    """

    def __init__(self, model_path: str, tokenizer_path: str):
        """
        Inicializa el clasificador cargando modelo y tokenizer.

        Args:
            model_path: Ruta a la carpeta del modelo
            tokenizer_path: Ruta a la carpeta del tokenizer
        """
        logger.info(f"Cargando modelo desde: {model_path}")

        # Detectar si hay GPU disponible, si no usar CPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Usando dispositivo: {self.device}")

        # Cargar el tokenizer (convierte texto en números)
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

        # Cargar el modelo BETO entrenado
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)

        # Mover el modelo a GPU o CPU
        self.model.to(self.device)

        # Poner el modelo en modo evaluación (no entrenamiento)
        self.model.eval() #Pone BETO en "modo predicción". Sin esto, el modelo se comportaría como si estuviera entrenando.

        # Diccionario para convertir el número de predicción en texto
        self.id2label = {0: "no_ofensivo", 1: "ofensivo"}

        logger.info("Modelo BETO cargado correctamente")

    def predict(self, text: str) -> Dict[str, any]:
        """
        Predice si un texto es ofensivo.

        Args:
            text: El texto a clasificar

        Returns:
            Diccionario con la predicción, confianza y probabilidades
        """
        # Paso 1: Convertir el texto en números (tokens)
        inputs = self.tokenizer(
            text,
            return_tensors="pt",      # Formato PyTorch
            padding=True,             # Rellenar si es corto
            truncation=True,          # Cortar si es muy largo
            max_length=128            # Máximo 128 tokens
        )

        # Paso 2: Mover los datos a GPU/CPU
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Paso 3: Hacer la predicción (sin calcular gradientes, más rápido)
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Paso 4: Convertir las salidas en probabilidades (0 a 1)
        probs = torch.softmax(outputs.logits, dim=1)

        # Paso 5: Obtener la clase con mayor probabilidad
        prediccion_id = torch.argmax(probs, dim=1).item()

        # Paso 6: Obtener el valor de confianza de esa predicción
        confianza = probs[0][prediccion_id].item()

        # Paso 7: Devolver el resultado completo
        return {
            "texto": text,
            "prediccion": self.id2label[prediccion_id],
            "confianza": float(confianza),
            "probabilidades": {
                "no_ofensivo": float(probs[0][0]),
                "ofensivo": float(probs[0][1])
            }
        }

    def predict_batch(self, texts: List[str], batch_size: int = 16) -> List[Dict[str, any]]:
        """
        Predice varios textos a la vez (más eficiente).

        Args:
            texts: Lista de textos a clasificar
            batch_size: Cuántos procesar a la vez

        Returns:
            Lista de diccionarios con las predicciones
        """
        resultados = []

        # Procesar los textos en grupos (batches)
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            # Tokenizar el grupo completo
            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=128
            )

            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Predecir todo el grupo
            with torch.no_grad():
                outputs = self.model(**inputs)

            probs = torch.softmax(outputs.logits, dim=1)
            predicciones = torch.argmax(probs, dim=1)

            # Procesar cada resultado del grupo
            for j, texto in enumerate(batch):
                pred_id = predicciones[j].item()
                conf = probs[j][pred_id].item()

                resultados.append({
                    "texto": texto,
                    "prediccion": self.id2label[pred_id],
                    "confianza": float(conf),
                    "probabilidades": {
                        "no_ofensivo": float(probs[j][0]),
                        "ofensivo": float(probs[j][1])
                    }
                })

        return resultados