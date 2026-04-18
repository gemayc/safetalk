"""
Modelo basado en BETO (BERT en español) fine-tuned para detección de bullying.
"""

from typing import Optional
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import Trainer, TrainingArguments


class BETOModel:
    """
    Modelo fine-tuned sobre BETO para clasificación de texto dañino.
    
    BETO es el modelo BERT pre-entrenado en español por el
    Barcelona Supercomputing Center.
    """
    
    def __init__(
        self,
        model_name: str = "dccuchile/bert-base-spanish-wwm-cased",
        num_labels: int = 2,
        max_length: int = 128
    ):
        """
        Inicializa el modelo BETO.
        
        Args:
            model_name: Nombre del modelo BETO en HuggingFace
            num_labels: Número de clases (2 para clasificación binaria)
            max_length: Longitud máxima de secuencia
        """
        self.model_name = model_name
        self.num_labels = num_labels
        self.max_length = max_length
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.tokenizer = None
        self.model = None
        
    def load_model(self):
        """Carga el modelo y tokenizer desde HuggingFace."""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=self.num_labels
        )
        self.model.to(self.device)
        
    def train(
        self,
        train_dataset,
        eval_dataset=None,
        output_dir: Path = Path("./models/beto-finetuned"),
        num_epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5
    ):
        """
        Fine-tune del modelo BETO.
        
        Args:
            train_dataset: Dataset de entrenamiento (HuggingFace Dataset)
            eval_dataset: Dataset de evaluación opcional
            output_dir: Directorio para guardar el modelo
            num_epochs: Número de épocas de entrenamiento
            batch_size: Tamaño de batch
            learning_rate: Tasa de aprendizaje
        """
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=str(output_dir / "logs"),
            logging_steps=100,
            evaluation_strategy="epoch" if eval_dataset else "no",
            save_strategy="epoch",
            load_best_model_at_end=True if eval_dataset else False,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
        )
        
        trainer.train()
        
    def predict(self, text: str):
        """Predice la clase de un texto."""
        if self.model is None or self.tokenizer is None:
            raise ValueError("Modelo no cargado. Llama a load_model() primero.")
            
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            max_length=self.max_length,
            truncation=True,
            padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
        return {
            "label": int(torch.argmax(probs)),
            "probabilities": probs.cpu().numpy()[0].tolist()
        }
    
    def save(self, path: Path):
        """Guarda el modelo fine-tuned."""
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        
    def load_finetuned(self, path: Path):
        """Carga un modelo previamente fine-tuned."""
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.model = AutoModelForSequenceClassification.from_pretrained(path)
        self.model.to(self.device)
