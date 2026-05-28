# Modelo BETO Fine-tuned para Detección de Bullying

## Información del Modelo

- **Modelo base:** dccuchile/bert-base-spanish-wwm-cased (BETO)
- **Tarea:** Clasificación binaria (ofensivo/no ofensivo)
- **F1-Score en TEST:** 88.60%
- **Precisión:** 89.61%
- **Recall:** 87.62%

## Resultados

### Comparación con Baselines

| Modelo | F1-Score | Mejora vs SVM | FN (Bullying perdido) | FP (Censura) |
|--------|----------|---------------|----------------------|--------------|
| SVM | 84.36% | - | 104 (16.5%) | 91 (14.2%) |
| LightGBM | 84.86% | +0.50% | 103 (16.3%) | 82 (12.8%) |
| **BETO** | **88.60%** | **+4.24%** | **78 (12.4%)** | **64 (10.0%)** |

### Reducción de Errores

- **25 casos MÁS** de bullying detectados vs LightGBM (-24.3%)
- **18 casos MENOS** de censura injusta vs LightGBM (-22.0%)
- **43 errores MENOS** en total vs LightGBM (-23.2%)

## Uso del Modelo

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Cargar modelo y tokenizer
tokenizer = AutoTokenizer.from_pretrained('./tokenizer')
model = AutoModelForSequenceClassification.from_pretrained('./modelo')

# Predecir
def predecir_texto(texto):
    inputs = tokenizer(texto, return_tensors="pt", padding=True, truncation=True, max_length=128)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    probs = torch.softmax(outputs.logits, dim=1)
    prediccion = torch.argmax(probs, dim=1).item()
    confianza = probs[0][prediccion].item()
    
    etiqueta = "Ofensivo" if prediccion == 1 else "No ofensivo"
    
    return {
        "texto": texto,
        "prediccion": etiqueta,
        "confianza": confianza
    }

# Ejemplo
resultado = predecir_texto("eres un gilipollas")
print(resultado)
# {'texto': 'eres un gilipollas', 'prediccion': 'Ofensivo', 'confianza': 0.95}
```

## Archivos

- `modelo/` - Modelo BETO fine-tuned
- `tokenizer/` - Tokenizer de BETO
- `metricas_beto.json` - Métricas completas del modelo
- `README.md` - Este archivo

## Configuración de Entrenamiento

- Learning rate: 2e-5
- Batch size: 16
- Epochs: 3
- Max sequence length: 128 tokens
- Hardware: Google Colab Tesla T4 GPU
- Tiempo de entrenamiento: ~20 minutos

## Dataset

- Train: 5,919 ejemplos
- Validation: 1,269 ejemplos
- Test: 1,269 ejemplos
- Balance: ~50% ofensivo, ~50% no ofensivo

## Fecha

Entrenado: 2026-05-10
