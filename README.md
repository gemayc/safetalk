# 🛡️ SafeTalk

**Sistema de detección automática de bullying y discurso de odio en español**

SafeTalk es un proyecto de Machine Learning y Deep Learning diseñado para detectar automáticamente contenido potencialmente dañino en entornos digitales donde interactúan jóvenes, como Discord, Twitter y plataformas educativas institucionales.

## 📋 Descripción del Proyecto

El sistema analiza **mensajes de texto** en español, identificando en tiempo real contenido de bullying y discurso de odio, alertando a moderadores para intervenir oportunamente.

> **⚠️ Nota importante**: Este proyecto está enfocado **exclusivamente en el análisis de mensajes de texto**. No incluye procesamiento de audio o voz.

### Características Técnicas

- **Modelo Baseline**: TF-IDF + SVM como referencia de rendimiento
- **Modelo Avanzado**: Fine-tuning sobre BETO (BERT en español del Barcelona Supercomputing Center)
- **Enfoque**: Análisis exclusivo de mensajes de texto en español

## 🚀 Guía de Configuración - Paso a Paso

### Prerequisitos

Antes de empezar, asegúrate de tener instalado:
- **Python 3.10+** (recomendado 3.11 o 3.12)
- **Git**
- **uv** (gestor de dependencias Python ultrarrápido)

### Paso 1: Instalar uv

Si aún no tienes `uv` instalado:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Con pip:**
```bash
pip install uv
```

### Paso 2: Clonar el Repositorio

```bash
git clone git@github.com:[TU-USUARIO]/safetalk.git
cd safetalk
```

### Paso 3: Crear Entorno Virtual con uv

```bash
# Crear entorno virtual
uv venv

# Activar el entorno virtual
# En macOS/Linux:
source .venv/bin/activate

# En Windows:
.venv\Scripts\activate
```

### Paso 4: Instalar Dependencias

```bash
# Instalar dependencias del proyecto
uv pip install -e .

# Instalar dependencias de desarrollo
uv pip install -e ".[dev]"

# Instalar dependencias para notebooks
uv pip install -e ".[notebooks]"

# O instalar todo junto
uv pip install -e ".[all]"
```

### Paso 5: Descargar Modelos Adicionales (Opcional)

```bash
# Descargar modelo de lenguaje español para spaCy
python -m spacy download es_core_news_sm

# Descargar recursos de NLTK
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
```

### Paso 6: Verificar Instalación

```bash
# Ejecutar tests
pytest tests/

# O con coverage
pytest tests/ --cov=src/safetalk --cov-report=html
```

### Paso 7: Configurar Pre-commit (Opcional pero Recomendado)

```bash
# Instalar pre-commit hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

## 📁 Estructura del Proyecto

```
safetalk/
├── src/safetalk/          # Código fuente principal
│   ├── models/            # Modelos ML/DL (baseline, BETO)
│   ├── data/              # Preprocesamiento y gestión de datos
│   └── detector.py        # Detector principal
├── notebooks/             # Jupyter notebooks para experimentación
├── scripts/               # Scripts de entrenamiento y evaluación
│   ├── train_baseline.py  # Entrenar modelo TF-IDF+SVM
│   └── train_beto.py      # Fine-tune BETO
├── tests/                 # Tests unitarios
├── data/                  # Datos del proyecto
│   ├── raw/               # Datos sin procesar
│   └── processed/         # Datos procesados
├── models/                # Modelos entrenados guardados
├── configs/               # Archivos de configuración
├── pyproject.toml         # Configuración del proyecto y dependencias
└── README.md             # Este archivo
```

## 🎯 Uso Básico

### Entrenar Modelo Baseline

```bash
python scripts/train_baseline.py \
  --data data/processed/train.csv \
  --output models/baseline.pkl \
  --max-features 5000
```

### Fine-tune BETO

```bash
python scripts/train_beto.py \
  --data data/processed/train.csv \
  --output models/beto-finetuned \
  --epochs 3 \
  --batch-size 16
```

### Uso Programático

```python
from safetalk.detector import BullyingDetector

# Inicializar detector
detector = BullyingDetector(model_type="beto")
detector.load_model()

# Predecir en un texto
result = detector.predict("Este es un mensaje de ejemplo")
print(result)
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=src/safetalk --cov-report=html

# Ver reporte de coverage en el navegador
open htmlcov/index.html
```

## 📊 Preparación de Datos

### Formato Esperado

SafeTalk espera datos en formato CSV:

```csv
text,label
"Mensaje de ejemplo 1",0
"Mensaje con contenido dañino",1
```

Donde:
- `label = 0`: Mensaje no dañino
- `label = 1`: Bullying o discurso de odio

### Datasets Públicos Recomendados

Para entrenar tus modelos, puedes usar estos datasets en español:

**🏆 Recomendado: Hugging Face Datasets** (Más Fácil de Usar)

**hate_speech_offensive (Español)**
- 🔗 https://huggingface.co/datasets/hate_speech_offensive
- 🇪🇸 Tweets clasificados como odio/ofensivo/neutro
- ✅ Descarga directa, sin registro complicado

**HateCheck Spanish**
- 🔗 https://huggingface.co/datasets/Paul/hatecheck-spanish
- 🇪🇸 Dataset de evaluación para hate speech
- ✅ Disponible en Hugging Face

**Spanish Hate Speech Dataset**
- 🔗 Buscar en: https://huggingface.co/datasets?language=language:es&search=hate
- 🇪🇸 Varios datasets disponibles

**Desde GitHub (Acceso Directo)**

**MeOffendEs**
- 🔗 https://github.com/msang/meoffendes
- 🇪🇸 ~4,000 tweets ofensivos
- ✅ Descarga directa desde GitHub

**HaterNet**
- 🔗 https://github.com/gsi-upm/haterNet
- 🇪🇸 Tweets con discurso de odio
- ✅ Descarga directa desde GitHub

**⚠️ Datasets en CodaLab (Requieren Registro)**

> **Nota**: CodaLab migró a https://codalab.lisn.upsaclay.fr/. Algunos datasets antiguos pueden requerir cuenta en la nueva plataforma o no estar disponibles.

**HatEval 2019 (SemEval)** - Si está disponible
- 🔗 https://competitions.codalab.org/competitions/19935
- 🇪🇸 ~5,000 tweets en español sobre odio

### Cómo Descargar Datasets

**Opción 1: Desde Hugging Face (Recomendado) 🏆**

La forma más fácil usando nuestro script:

```bash
# Ver datasets disponibles
python scripts/download_huggingface_dataset.py --list

# Descargar dataset y convertir automáticamente
python scripts/download_huggingface_dataset.py \
  --dataset hate_speech_offensive \
  --convert

# Los archivos quedarán en data/processed/train_converted.csv
```

O manualmente con Python:

```python
from datasets import load_dataset
import pandas as pd

# Descargar dataset
dataset = load_dataset("hate_speech_offensive")

# Guardar como CSV
train_df = pd.DataFrame(dataset['train'])
train_df.to_csv('data/raw/huggingface_train.csv', index=False)
```

**Opción 2: Desde GitHub**

```bash
# Clonar repositorio con dataset
git clone https://github.com/msang/meoffendes.git

# Copiar datos a tu proyecto
cp meoffendes/data/*.csv data/raw/

# Convertir al formato SafeTalk
python scripts/convert_dataset.py \
  --input data/raw/[archivo].csv \
  --output data/processed/train.csv
```

**Opción 3: Desde CodaLab (Si está disponible)**

> ⚠️ **Problema Conocido**: CodaLab migró a https://codalab.lisn.upsaclay.fr/. 
> Los datasets antiguos pueden requerir cuenta en la nueva plataforma o no estar disponibles.
> **Recomendamos usar Hugging Face (Opción 1)** que es más directo.

### Convertir Dataset al Formato SafeTalk

Si descargaste desde GitHub u otra fuente:

```bash
# Conversión automática (detecta columnas)
python scripts/convert_dataset.py \
  --input data/raw/original_train.csv \
  --output data/processed/train.csv

# Conversión manual (especificando columnas)
python scripts/convert_dataset.py \
  --input data/raw/original_train.csv \
  --output data/processed/train.csv \
  --mode manual \
  --text-col "text" \
  --label-col "HS"
```

## 🤝 Colaboración en Equipo

### Flujo de Trabajo Git

1. **Crear una rama para tu feature:**
   ```bash
   git checkout -b feature/nombre-feature
   ```

2. **Hacer commits descriptivos:**
   ```bash
   git add .
   git commit -m "feat: descripción clara del cambio"
   ```

3. **Sincronizar con el repositorio remoto:**
   ```bash
   git pull origin main
   git push origin feature/nombre-feature
   ```

4. **Crear Pull Request** en GitHub para revisión

### Convenciones de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `test:` Añadir o modificar tests
- `refactor:` Refactorización de código
- `style:` Formateo, estilo de código
- `chore:` Tareas de mantenimiento

## 🛠️ Herramientas de Desarrollo

- **Formateo**: `black` y `ruff`
  ```bash
  black src/ tests/
  ruff check src/ tests/
  ```

- **Type checking**: `mypy`
  ```bash
  mypy src/
  ```

## 📚 Recursos

- [BETO - BERT en español](https://github.com/dccuchile/beto)
- [uv - Documentación](https://docs.astral.sh/uv/)
- [Transformers - Hugging Face](https://huggingface.co/docs/transformers/)

## 📝 Licencia

MIT License

## 👥 Equipo

SafeTalk Team - AI Saturdays Project

---

**¡Importante!** Este proyecto aborda un problema social real. Asegúrate de:
- Manejar los datos con responsabilidad y ética
- Proteger la privacidad de los usuarios
- Considerar sesgos en los modelos
- Usar el sistema como herramienta de apoyo, no como juez único
