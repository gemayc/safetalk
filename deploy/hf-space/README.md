---
title: SafeTalk API
emoji: 🛡️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 🛡️ SafeTalk API

API REST para detección de bullying y contenido ofensivo en español.

## 🚀 Endpoints

- `GET /` - Información de la API
- `GET /health` - Estado de la API
- `POST /predict` - Clasificar un texto
- `POST /predict/batch` - Clasificar varios textos
- `GET /model/info` - Métricas del modelo
- `GET /docs` - Documentación interactiva (Swagger UI)

## 📊 Modelo

Usa **BETO** (BERT en español) fine-tuned para detectar bullying.

- **Modelo:** [Gemita284/safetalk-beto](https://huggingface.co/Gemita284/safetalk-beto)
- **F1-Score:** 88.60%
- **Accuracy:** 88.81%
- **Precision:** 89.61%
- **Recall:** 87.62%

## 💡 Ejemplo de uso

```python
import requests

response = requests.post(
    "https://Gemita284-safetalk-api.hf.space/predict",
    json={"texto": "eres un gilipollas"}
)
print(response.json())
```

## 🏗️ Tecnologías

- FastAPI
- PyTorch
- Transformers (Hugging Face)
- BETO (BERT en español)