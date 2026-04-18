# SafeTalk - Notas del Proyecto

## Próximos Pasos

### 1. Recolección de Datos
- [ ] **Opción A (Recomendado)**: Descargar desde Hugging Face
  - [ ] https://huggingface.co/datasets/hate_speech_offensive
  - [ ] Buscar otros: https://huggingface.co/datasets?language=language:es&search=hate
- [ ] **Opción B**: Desde GitHub
  - [ ] MeOffendEs: https://github.com/msang/meoffendes
  - [ ] HaterNet: https://github.com/gsi-upm/haterNet
- [ ] **Opción C**: Intentar CodaLab (puede requerir cuenta en https://codalab.lisn.upsaclay.fr/)
  - [ ] HatEval 2019 si está disponible
- [ ] Convertir datasets con `scripts/convert_dataset.py`
- [ ] Definir si usar clasificación binaria o multiclase

### 2. Experimentación Inicial
- [ ] Crear notebook exploratorio en `notebooks/01_exploratory_analysis.ipynb`
- [ ] Análisis de balance de clases
- [ ] Análisis de longitud de textos
- [ ] Palabras más frecuentes por clase

### 3. Baseline
- [ ] Implementar y entrenar modelo TF-IDF + SVM
- [ ] Calcular métricas: accuracy, precision, recall, F1
- [ ] Análisis de errores

### 4. BETO Fine-tuning
- [ ] Fine-tune BETO con datos de entrenamiento
- [ ] Comparar con baseline
- [ ] Optimización de hiperparámetros

### 5. API y Deployment (Opcional)
- [ ] Crear API REST con FastAPI
- [ ] Dockerizar aplicación
- [ ] Deploy en servicio cloud

## Recursos Útiles

### Datasets Disponibles (Ordenados por Facilidad de Acceso)

**🏆 Hugging Face (Más Fácil)**
- **hate_speech_offensive**: https://huggingface.co/datasets/hate_speech_offensive
  - Descarga directa con Python
- **Búsqueda general**: https://huggingface.co/datasets?language=language:es&search=hate
  - Múltiples datasets en español

**📦 GitHub (Fácil)**
- **MeOffendEs**: https://github.com/msang/meoffendes
  - ~4,000 tweets ofensivos en español, descarga directa
- **HaterNet**: https://github.com/gsi-upm/haterNet
  - Tweets con discurso de odio, múltiples categorías

**⚠️ CodaLab (Complicado - Migración de Plataforma)**
- **Nota**: CodaLab migró a https://codalab.lisn.upsaclay.fr/
- Algunos datasets antiguos pueden no estar accesibles
- **HatEval 2019**: https://competitions.codalab.org/competitions/19935 (verificar disponibilidad)
- **DETOXIS 2021**: Puede no estar disponible en la plataforma antigua

### Papers de Referencia
- BETO: A Spanish BERT Model
- Multilingual Toxic Comment Classification
- Automated Bullying Detection

## Notas de Reuniones

### [Fecha] - Reunión Inicial
- Decidido usar BETO como modelo principal
- Enfoque exclusivo en mensajes de texto (sin audio)
- uv como gestor de dependencias

---

Mantén este archivo actualizado con decisiones importantes y progreso.
