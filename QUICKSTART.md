# 🚀 Quick Start Guide - SafeTalk

Esta guía te llevará de 0 a un entorno completamente funcional en **menos de 10 minutos**.

## ⚡ Setup Rápido

### 1. Instalar uv (1 minuto)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Recargar shell
source ~/.zshrc  # o ~/.bashrc
```

### 2. Setup del Proyecto (2 minutos)

```bash
# Ya clonaste el repo, así que:
cd safetalk

# Crear entorno virtual e instalar todo
uv venv
source .venv/bin/activate
uv pip install -e ".[all]"
```

### 3. Verificar Instalación (1 minuto)

```bash
# Ejecutar tests básicos
pytest tests/ -v

# Debería ver:
# ✓ test_detector_initialization PASSED
# ✓ test_lowercase PASSED
# etc.
```

## 🎯 Primeros Pasos con el Código

### Opción 1: Notebook Exploratorio (Recomendado)

```bash
# Iniciar Jupyter Lab
jupyter lab

# Abrir: notebooks/01_exploratory_analysis.ipynb
```

### Opción 2: Script Python

Crea `test_setup.py`:

```python
from safetalk.data.preprocessing import TextPreprocessor

# Probar preprocesador
preprocessor = TextPreprocessor(lowercase=True, remove_urls=True)
text = "Hola @usuario! Mira https://example.com"
clean = preprocessor.clean_text(text)

print(f"Original: {text}")
print(f"Limpio:   {clean}")
```

Ejecutar:
```bash
python test_setup.py
```

## 📊 Siguientes Pasos

### 1. Conseguir Datos (Forma Más Fácil)

**Opción A: Descargar desde Hugging Face (Recomendado)**

```bash
# Ver datasets disponibles
python scripts/download_huggingface_dataset.py --list

# Descargar y convertir automáticamente
python scripts/download_huggingface_dataset.py \
  --dataset hate_speech_offensive \
  --convert

# ¡Listo! Archivo en: data/processed/train_converted.csv
```

**Opción B: Usar datos de ejemplo**

Crea `data/raw/example.csv`:

```csv
text,label
"Este es un mensaje normal",0
"Mensaje con contenido dañino",1
"Otro mensaje sin problemas",0
"Comentario ofensivo",1
```

### 2. Entrenar Modelo Baseline

```bash
python scripts/train_baseline.py \
  --data data/processed/train_converted.csv \
  --output models/baseline.pkl
```

### 3. Experimentar con BETO

```bash
# Requiere más datos y GPU (opcional)
python scripts/train_beto.py \
  --data data/processed/train_converted.csv \
  --epochs 3
```

## 🔧 Comandos Útiles (con Makefile)

```bash
make help           # Ver todos los comandos disponibles
make test           # Ejecutar tests
make format         # Formatear código
make lint           # Verificar código
make quality        # Todos los checks de calidad
make clean          # Limpiar archivos temporales
```

## 📝 Flujo de Trabajo Típico

```bash
# 1. Crear rama para tu trabajo
git checkout -b feat/nueva-funcionalidad

# 2. Hacer cambios en el código
# ... editar archivos ...

# 3. Formatear y verificar
make format
make lint

# 4. Ejecutar tests
make test

# 5. Commit y push
git add .
git commit -m "feat: descripción del cambio"
git push origin feat/nueva-funcionalidad

# 6. Crear Pull Request en GitHub
```

## ⚠️ Troubleshooting

### Error: "ModuleNotFoundError: No module named 'safetalk'"

```bash
# Asegúrate de haber instalado en modo editable:
uv pip install -e .

# Y que el entorno virtual está activado:
source .venv/bin/activate
```

### Error al instalar dependencias con GPU

Si no tienes GPU NVIDIA:

```bash
# Instalar PyTorch solo CPU
uv pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## 🎓 Recursos de Aprendizaje

1. **Hugging Face Transformers**: https://huggingface.co/docs/transformers/
2. **BETO Model**: https://huggingface.co/dccuchile/bert-base-spanish-wwm-cased
3. **uv Documentation**: https://docs.astral.sh/uv/

## 💡 Tips

- **Usa notebooks** para experimentación rápida
- **Escribe tests** para código nuevo
- **Documenta** decisiones importantes en NOTES.md
- **Pregunta** si algo no está claro - usa Issues en GitHub

## ✅ Checklist de Setup Completo

- [ ] uv instalado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas
- [ ] Tests ejecutados exitosamente
- [ ] Jupyter funcionando
- [ ] Git configurado
- [ ] Pre-commit hooks instalados (opcional)

---

**¿Listo?** ¡Ahora estás preparado para empezar a trabajar en SafeTalk! 🚀
