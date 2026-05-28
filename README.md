# 🛡️ SafeTalk

> Sistema de detección automática de bullying y discurso de odio en español, integrado en Telegram y Discord.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Model](https://img.shields.io/badge/Model-BETO%20V2__FINAL-teal)](https://huggingface.co/Gemita284/safetalk-beto-v2)
[![API](https://img.shields.io/badge/API-HuggingFace%20Spaces-orange)](https://huggingface.co/spaces/Gemita284/safetalk-api)
[![Bots](https://img.shields.io/badge/Bots-AWS%20EC2%20%C2%B7%2024%2F7-yellow)](https://aws.amazon.com/ec2/)

---

## ¿Qué es SafeTalk?

SafeTalk es un prototipo de sistema de inteligencia artificial que detecta mensajes de bullying y discurso de odio en español en tiempo real. Cuando alguien manda un mensaje ofensivo en un grupo, el bot lo detecta, lo elimina y avisa al grupo automáticamente.

**Lo que hace diferente a SafeTalk:**

- Detecta técnicas de ofuscación reales: `gilip0llas`, `g1l1p0ll4s`, `puuuuuta`
- Entiende el contexto: `"no eres tonto"` ≠ `"eres tonto"`
- Funciona en Telegram y Discord simultáneamente
- API REST pública desplegada en Hugging Face Spaces

---

## Arquitectura

```
Usuario en Telegram/Discord
         ↓
   Bot (Telegram / Discord)
   [AWS EC2 · Docker · 24/7]
         ↓  HTTP POST /predict
   API REST (FastAPI · HF Spaces)
         ↓
   TextPreprocessor (anti-ofuscación)
         ↓
   BETO V2_FINAL (Hugging Face Hub)
         ↓
   Predicción: ofensivo / no ofensivo + confianza
```

---

## Estructura del proyecto

```
safetalk/
├── configs/
│   └── training_config.yaml           # Configuración del entrenamiento BETO
├── data/
│   └── processed/                     # Datasets procesados (train/val/test)
├── deploy/                            # Configuración de despliegue (HF Space)
├── models/                            # Modelos locales (en .gitignore)
│   └── beto_v2_final/
│       ├── modelo/
│       └── tokenizer/
├── notebooks/                         # Jupyter notebooks del proyecto
│   ├── 01_analisis_dataset_zenodo.ipynb          # Análisis exploratorio dataset Zenodo
│   ├── 01_exploracion_dataset_safetalk_completo.ipynb  # Exploración dataset completo
│   ├── 02_limpieza_clase_0.ipynb                 # Limpieza de la clase no ofensiva
│   ├── 03_limpieza_textos.ipynb                  # Limpieza y normalización de textos
│   ├── 04_generar_sinteticos_chatgpt.ipynb       # Generación de datos sintéticos con GPT
│   ├── 05_combinar_dataset_final.ipynb           # Combinación del dataset final
│   ├── 06_dividir_train_val_test.ipynb           # Split train/val/test
│   ├── 07_baseline_tfidf_svm.ipynb               # Baseline SVM + TF-IDF
│   ├── 08_baseline_lightgbm_optuna.ipynb         # Baseline LightGBM + Optuna
│   ├── 09_beto_finetuning.ipynb                  # Fine-tuning BETO V1
│   ├── 10_test_beto_local.ipynb                  # Test del modelo BETO en local
│   ├── 11_Beto_V2_preprocesado.ipynb             # Entrenamiento BETO V2
│   └── 12_Beto_V2_final.ipynb                    # Entrenamiento BETO V2_FINAL
├── results/                           # Métricas y gráficas guardadas
├── scripts/
│   ├── preprocess_and_split_v2.py     # Preprocesa dataset y genera splits V2
│   ├── verify_preprocessing.py        # Verifica impacto del preprocesado
│   └── sync_hf_space.sh               # Sincroniza código con HF Space
├── src/
│   ├── api/
│   │   ├── main.py                    # API FastAPI
│   │   └── schemas.py                 # Schemas Pydantic
│   ├── data/
│   │   └── preprocessing.py           # TextPreprocessor (anti-ofuscación)
│   ├── discord_bot/
│   │   └── bot.py                     # Bot de Discord
│   ├── models/
│   │   ├── beto_classifier.py         # Clasificador BETO
│   │   └── predictor.py               # Predictor unificado
│   └── telegram/
│       └── bot.py                     # Bot de Telegram
├── tests/
│   └── test_preprocessing.py          # Tests del preprocesador
├── .env.example                       # Variables de entorno de ejemplo
├── .gitignore
├── CONTRIBUTING.md                    # Guía de contribución
├── Dockerfile                         # Orquesta ambos bots en producción
├── LICENSE                            # Licencia MIT
├── Makefile                           # Comandos útiles de desarrollo
├── NOTES.md                           # Notas internas del proyecto
├── pyproject.toml                     # Dependencias del proyecto
├── QUICKSTART.md                      # Guía rápida de inicio
├── README.md
├── run_api.py                         # Lanza la API en local
├── start.sh                           # Arranca Telegram + Discord + servidor fantasma
└── uv.lock                            # Lockfile de dependencias
```

---

## Requisitos previos

- Python 3.10 o superior
- [uv](https://github.com/astral-sh/uv) (gestor de paquetes ultrarrápido)
- Cuenta en [Hugging Face](https://huggingface.co)
- Token de bot de Telegram (via [@BotFather](https://t.me/BotFather))
- Token de bot de Discord (via [Discord Developer Portal](https://discord.com/developers/applications))

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Gemita284/safetalk.git
cd safetalk
```

### 2. Crear entorno virtual e instalar dependencias

```bash
uv venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows

uv pip install -r pyproject.toml
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```env
# ── Telegram ──────────────────────────────────────
TELEGRAM_BOT_TOKEN=tu_token_de_telegram

# ── Discord ───────────────────────────────────────
DISCORD_BOT_TOKEN=tu_token_de_discord

# ── SafeTalk API ──────────────────────────────────
API_URL=https://Gemita284-safetalk-api.hf.space

# ── Detección ─────────────────────────────────────
UMBRAL_CONFIANZA=0.70       # Umbral para borrar mensajes (0.0 - 1.0)

# ── Hugging Face ──────────────────────────────────
HF_TOKEN=tu_token_de_huggingface

# ── OpenAI (opcional, para generación de datos) ───
OPENAI_API_KEY=tu_api_key_de_openai
```

---

## Uso en local

### Lanzar solo la API

```bash
python run_api.py
```

La API estará disponible en `http://localhost:8000`. Puedes probarla en:

```
http://localhost:8000/docs
```

Ejemplo de llamada:

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"texto": "eres un gilipollas"}'
```

Respuesta:

```json
{
  "prediccion": "ofensivo",
  "confianza": 0.9876,
  "probabilidades": {
    "no_ofensivo": 0.0124,
    "ofensivo": 0.9876
  }
}
```

### Lanzar el bot de Telegram

```bash
python src/telegram/bot.py
```

### Lanzar el bot de Discord

```bash
python src/discord_bot/bot.py
```

### Lanzar ambos bots a la vez

```bash
bash start.sh
```

---

## Despliegue con Docker

El `Dockerfile` orquesta ambos bots (Telegram y Discord) en un único contenedor. Incluye un servidor HTTP fantasma para mantener el servicio activo en plataformas gratuitas como Render.

### Build de la imagen

```bash
docker build -t safetalk .
```

### Ejecutar el contenedor

```bash
docker run --env-file .env safetalk
```

### Variables de entorno en Docker

Asegúrate de pasar todas las variables del `.env` al contenedor. Si usas Render u otra plataforma, configúralas en el panel de la plataforma.

---

## Despliegue en AWS EC2 (producción)

Los bots de Telegram y Discord están desplegados en una instancia de **AWS EC2** mediante Docker, funcionando **24/7**.

### Requisitos de la instancia

- Tipo recomendado: `t2.micro` (free tier) o superior
- SO: Ubuntu 22.04 LTS
- Docker instalado

### Pasos de despliegue

**1. Conectar a la instancia EC2**

```bash
ssh -i tu-clave.pem ubuntu@tu-ip-ec2
```

**2. Instalar Docker en la instancia**

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
```

**3. Clonar el repositorio**

```bash
git clone https://github.com/Gemita284/safetalk.git
cd safetalk
```

**4. Crear el archivo `.env`**

```bash
cp .env.example .env
nano .env   # Añade tus tokens y variables
```

**5. Build de la imagen**

```bash
docker build -t safetalk .
```

**6. Lanzar el contenedor en segundo plano**

```bash
docker run -d \
  --name safetalk-bots \
  --restart always \
  --env-file .env \
  safetalk
```

El flag `--restart always` garantiza que los bots se reinicien automáticamente si la instancia se reinicia o si el contenedor falla.

**7. Verificar que está corriendo**

```bash
docker ps
docker logs safetalk-bots
```

### Actualizar a una nueva versión

Cuando haya cambios en el código:

```bash
cd safetalk
git pull
docker stop safetalk-bots
docker rm safetalk-bots
docker build -t safetalk .
docker run -d \
  --name safetalk-bots \
  --restart always \
  --env-file .env \
  safetalk
```

### Arquitectura de despliegue

```
┌─────────────────────────────────────────┐
│           AWS EC2 (Ubuntu)              │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │       Docker Container           │   │
│  │                                  │   │
│  │  start.sh                        │   │
│  │    ├── src/telegram/bot.py  &    │   │
│  │    └── src/discord_bot/bot.py &  │   │
│  │                                  │   │
│  └──────────────────────────────────┘   │
│                                         │
│  Uptime: 24/7 · --restart always        │
└─────────────────────────────────────────┘
         │                    │
         ▼                    ▼
   Telegram API         Discord API
```

## Despliegue en Render (alternativa gratuita)

Si no tienes acceso a AWS EC2, puedes usar Render como alternativa gratuita:

1. Conecta tu repositorio de GitHub a [Render](https://render.com)
2. Crea un nuevo **Web Service**
3. Selecciona **Docker** como entorno
4. Añade las variables de entorno del `.env` en el panel de Render
5. Render detectará el `Dockerfile` y desplegará automáticamente

> El `start.sh` levanta un servidor HTTP en el puerto `$PORT` (por defecto 10000) para que Render no duerma el servicio en el plan gratuito.

---

## Cómo funciona el bot en un grupo

### Telegram

1. Añade el bot al grupo
2. Hazlo administrador con permiso de **"Eliminar mensajes"**
3. Desactiva el Privacy Mode en [@BotFather](https://t.me/BotFather) con `/setprivacy`
4. El bot analizará cada mensaje y actuará si supera el umbral de confianza

### Discord

1. Invita el bot al servidor con los permisos `Manage Messages` y `Read Message History`
2. El bot monitorizará los canales donde tenga acceso

### ¿Qué hace cuando detecta un mensaje ofensivo?

```
1. Borra el mensaje del grupo
2. Envía un aviso citando el contenido eliminado:

   🛡️ He eliminado un mensaje ofensivo

   👤 Usuario: @usuario
   📝 "eres un gilip0llas"
   📊 Confianza de detección: 87.6%
```

---

## Modelo de IA

### BETO V2_FINAL

El modelo está basado en [BETO](https://huggingface.co/dccuchile/bert-base-spanish-wwm-cased), un BERT preentrenado en español por la Universidad de Chile.

**Repositorio del modelo:** [Gemita284/safetalk-beto-v2](https://huggingface.co/Gemita284/safetalk-beto-v2)

El modelo se descarga automáticamente en el primer arranque si no está disponible en local.

### Métricas (test set independiente)

| Métrica | Valor |
|---------|-------|
| Accuracy | 88.34% |
| Precision | 92.73% |
| Recall | 83.02% |
| F1-Score | 87.60% |
| ROC-AUC | 94.36% |
| PR-AUC | 95.55% |
| Overfitting (Train-Test gap) | 2.16% |

### Técnicas aplicadas para reducir el overfitting

- **Layer Freezing:** capas 0-7 y embeddings congelados (110M → ~25M parámetros entrenables)
- **Early Stopping:** parada automática cuando la validation loss empeora (patience=1)
- **Weight Decay:** regularización aumentada de 0.01 a 0.1

### Evolución de modelos

| Modelo | F1-Score | Overfitting |
|--------|----------|-------------|
| SVM + TF-IDF | 84.36% | 13.00% |
| LightGBM + Optuna | 84.86% | 1.97% |
| BETO V1 | 88.60% | 9.00% |
| **BETO V2_FINAL** | **87.60%** | **2.16%** |

---

## Preprocesado anti-ofuscación

El `TextPreprocessor` detecta y normaliza técnicas de evasión reales:

| Técnica | Entrada | Salida |
|---------|---------|--------|
| Leetspeak básico | `gilip0llas` | `gilipollas` |
| Leetspeak completo | `g1l1p0ll4s` | `gilipollas` |
| Letras repetidas | `puuuuuta` | `puuta` |
| Separadores | `g.i.l.i.p.o.l.l.a.s` | `gilipollas` |
| Símbolo arroba | `put@` | `puta` |
| Unicode homoglyphs | `саbrón` (с cirílico) | `cabrón` |

El preprocesador también preserva el español correcto: acentos (á, é, í, ó, ú), la ñ, y acrónimos.

---

## API REST

La API está desplegada en Hugging Face Spaces:

```
https://Gemita284-safetalk-api.hf.space
```

### Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Estado de la API |
| `GET` | `/health` | Health check |
| `POST` | `/predict` | Predice si un texto es ofensivo |
| `POST` | `/predict/batch` | Predice múltiples textos |

### Ejemplo `/predict`

```bash
curl -X POST "https://Gemita284-safetalk-api.hf.space/predict" \
  -H "Content-Type: application/json" \
  -d '{"texto": "hola buenos días"}'
```

---

## Flujo de notebooks

Los notebooks están numerados en orden de ejecución y documentan todo el proceso:

| Notebook | Descripción |
|----------|-------------|
| `01_analisis_dataset_zenodo` | Análisis exploratorio del dataset original de Zenodo |
| `01_exploracion_dataset_safetalk_completo` | Exploración del dataset completo combinado |
| `02_limpieza_clase_0` | Limpieza de mensajes no ofensivos |
| `03_limpieza_textos` | Normalización y limpieza general de textos |
| `04_generar_sinteticos_chatgpt` | Generación de datos sintéticos con ChatGPT para balancear clases |
| `05_combinar_dataset_final` | Combinación del dataset Zenodo + sintéticos |
| `06_dividir_train_val_test` | Split estratificado 70/15/15 (random_state=42) |
| `07_baseline_tfidf_svm` | Baseline con SVM + TF-IDF (F1: 84.36%) |
| `08_baseline_lightgbm_optuna` | Baseline con LightGBM + Optuna (F1: 84.86%) |
| `09_beto_finetuning` | Fine-tuning BETO V1 en Google Colab (F1: 88.60%) |
| `10_test_beto_local` | Pruebas del modelo BETO V1 en local |
| `11_Beto_V2_preprocesado` | Entrenamiento BETO V2 con layer freezing + early stopping |
| `12_Beto_V2_final` | Entrenamiento BETO V2_FINAL con dataset completo |

---

## Tests

```bash
pytest tests/ -v
```

Los tests cubren el `TextPreprocessor`:

- Normalización de leetspeak
- Preservación de textos inocentes
- Preservación de acentos y ñ
- Procesamiento en batch

---

## Scripts de utilidad

### Verificar el preprocesado antes de entrenar

```bash
python scripts/verify_preprocessing.py
```

Comprueba que el preprocesado no rompe el dataset (textos vacíos, palabras clave preservadas).

### Generar splits V2 del dataset

```bash
python scripts/preprocess_and_split_v2.py
```

Aplica el `TextPreprocessor` al dataset completo y genera `train_v2.csv`, `val_v2.csv`, `test_v2.csv` con el mismo split que V1 (random_state=42).

### Sincronizar con Hugging Face Space

```bash
bash scripts/sync_hf_space.sh
```

---

## Configuración del bot de Telegram

Para que el bot funcione en grupos:

1. Habla con [@BotFather](https://t.me/BotFather)
2. Ejecuta `/setprivacy` → selecciona tu bot → **DISABLE**
3. Añade el bot al grupo
4. Hazlo **administrador** con permiso de eliminar mensajes

El Privacy Mode debe estar **desactivado** para que el bot pueda leer mensajes de grupo.

---

## Variables de entorno (referencia completa)

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram | ✅ |
| `DISCORD_BOT_TOKEN` | Token del bot de Discord | ✅ |
| `API_URL` | URL de la API de SafeTalk | ✅ |
| `UMBRAL_CONFIANZA` | Umbral de confianza para borrar (0.0-1.0) | ✅ (default: 0.70) |
| `HF_TOKEN` | Token de Hugging Face (para subir modelos) | Solo para desarrollo |
| `OPENAI_API_KEY` | API key de OpenAI (para generar datos) | Solo para desarrollo |

---

## Limitaciones conocidas

- El modelo no detecta el 17% del bullying real (recall 83%)
- Los emojis ofensivos (🖕🤡💀) no son analizados como señal
- El sarcasmo sutil es difícil de detectar
- Los datos de entrenamiento son parcialmente sintéticos

---

## Roadmap

- [ ] Guardar logs de predicciones en Supabase para reentrenamiento continuo
- [ ] Pipeline de reentrenamiento automático con datos reales
- [ ] Dashboard de monitorización
- [ ] Soporte de emojis (modelo multimodal)

---

## Contribuir

1. Haz fork del repositorio
2. Crea una rama: `git checkout -b feat/mi-mejora`
3. Haz commit de tus cambios: `git commit -m 'feat: descripción'`
4. Push a la rama: `git push origin feat/mi-mejora`
5. Abre un Pull Request

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

---

## Tecnologías

| Categoría | Tecnología |
|-----------|-----------|
| Modelo IA | BETO (dccuchile/bert-base-spanish-wwm-cased) |
| Framework ML | PyTorch + Hugging Face Transformers |
| Optimización | Optuna (LightGBM baseline) |
| API | FastAPI + Uvicorn |
| Despliegue API | Hugging Face Spaces (Docker) |
| Bot Telegram | python-telegram-bot |
| Bot Discord | discord.py |
| Despliegue bots | AWS EC2 (Docker · 24/7) |
| Modelo Hub | Hugging Face Hub |
| Entrenamiento | Google Colab (Tesla T4 GPU) |
| Contenedor | Docker + uv |
| Control versiones | GitHub |
| Lenguaje | Python 3.12 |

---

## Licencia

MIT License — consulta el archivo [LICENSE](LICENSE) para más detalles.


-----

## 👥 Equipo

Este proyecto fue desarrollado por el **Equipo-Saturdays**:

| Nombre |  
| :--- |
| **Gema Yébenes** | 
| **Camila Arenas** | 
| **Alex Méndez** | 
| **María Hetro** | 
| **Elena Martínez** | 

-----

## Crédito

Desarrollado como proyecto del programa **[Saturdays AI](https://www.saturdays.ai)**, una iniciativa que hace la inteligencia artificial más accesible (#ai4all) mediante proyectos para el bien social (#ai4good).

---

*Modelo alojado en: [Gemita284/safetalk-beto-v2](https://huggingface.co/Gemita284/safetalk-beto-v2)*
*API desplegada en: [Gemita284/safetalk-api](https://huggingface.co/spaces/Gemita284/safetalk-api)*
