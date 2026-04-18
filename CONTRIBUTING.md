# Guía de Contribución - SafeTalk

¡Gracias por tu interés en contribuir a SafeTalk! Este documento proporciona directrices para colaborar efectivamente en el proyecto.

## 🌟 Cómo Contribuir

### 1. Fork y Clone

```bash
# Fork el repositorio en GitHub, luego:
git clone git@github.com:[TU-USUARIO]/safetalk.git
cd safetalk
```

### 2. Configurar el Entorno de Desarrollo

```bash
# Instalar uv si no lo tienes
curl -LsSf https://astral.sh/uv/install.sh | sh

# Crear entorno virtual e instalar dependencias
uv venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
uv pip install -e ".[all]"

# Configurar pre-commit hooks
pre-commit install
```

### 3. Crear una Rama

```bash
# Actualizar main
git checkout main
git pull origin main

# Crear rama descriptiva
git checkout -b tipo/descripcion-corta

# Ejemplos:
# git checkout -b feat/beto-optimization
# git checkout -b fix/beto-tokenization-bug
# git checkout -b docs/update-readme
```

### 4. Hacer Cambios

#### Estándares de Código

- **Formateo**: Usamos `black` con línea de 100 caracteres
  ```bash
  black src/ tests/
  ```

- **Linting**: Usamos `ruff` para análisis estático
  ```bash
  ruff check src/ tests/ --fix
  ```

- **Type hints**: Añade type hints cuando sea posible
  ```python
  def predict(self, text: str) -> Dict[str, float]:
      ...
  ```

- **Docstrings**: Usa formato Google/NumPy
  ```python
  def train(self, X_train, y_train):
      """
      Entrena el modelo con los datos proporcionados.
      
      Args:
          X_train: Datos de entrenamiento
          y_train: Etiquetas de entrenamiento
      """
      ...
  ```

#### Tests

- **Siempre añade tests** para código nuevo
- Ejecuta tests antes de hacer commit:
  ```bash
  pytest tests/
  ```

- Mantén coverage alto:
  ```bash
  pytest --cov=src/safetalk --cov-report=term
  ```

### 5. Commits

Usa [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Formato
tipo(scope): descripción breve

# Tipos principales:
feat:     Nueva funcionalidad
fix:      Corrección de bug
docs:     Cambios en documentación
test:     Añadir o modificar tests
refactor: Refactorización sin cambiar funcionalidad
style:    Formateo, punto y coma faltantes, etc.
perf:     Mejoras de rendimiento
chore:    Tareas de mantenimiento, actualizar dependencias

# Ejemplos buenos:
git commit -m "feat(beto): add batch prediction support"
git commit -m "fix(preprocessing): handle empty text correctly"
git commit -m "docs: update installation instructions"
git commit -m "test(preprocessing): add URL removal tests"
```

### 6. Push y Pull Request

```bash
# Push a tu fork
git push origin tipo/descripcion-corta

# Crear Pull Request en GitHub con:
# - Título descriptivo
# - Descripción de cambios
# - Referencias a issues si aplica
# - Screenshots si hay cambios visuales
```

## 📋 Checklist de Pull Request

Antes de enviar tu PR, verifica:

- [ ] El código pasa todos los tests (`pytest`)
- [ ] El código está formateado (`black`, `ruff`)
- [ ] Añadiste tests para código nuevo
- [ ] Actualizaste la documentación si es necesario
- [ ] Los commits siguen Conventional Commits
- [ ] La descripción del PR es clara y completa
- [ ] No hay conflictos con `main`

## 🎯 Áreas de Contribución

### Prioridades Actuales

1. **Recolección y etiquetado de datos**
   - Buscar datasets públicos de bullying en español
   - Crear pipeline de etiquetado

2. **Mejora de modelos**
   - Experimentar con diferentes arquitecturas
   - Optimizar hiperparámetros
   - Implementar data augmentation

3. **Testing y documentación**
   - Aumentar coverage de tests
   - Añadir ejemplos de uso
   - Crear notebooks tutoriales

4. **API y deployment**
   - Implementar API REST con FastAPI
   - Containerización con Docker
   - CI/CD pipeline

### Bugs y Mejoras

Revisa los [Issues](https://github.com/[TU-USUARIO]/safetalk/issues) para encontrar tareas pendientes.

## 🤔 ¿Tienes una Idea?

Si tienes una idea pero no estás seguro de cómo implementarla:

1. Abre un **Issue** describiendo tu propuesta
2. Espera feedback del equipo
3. Una vez aprobado, crea tu PR

## 💬 Comunicación

- **Issues**: Para bugs, features, preguntas técnicas
- **Pull Requests**: Para proponer cambios de código
- **Discussions**: Para ideas generales, preguntas abiertas

## ⚖️ Código de Conducta

### Nuestros Compromisos

- Crear un ambiente respetuoso e inclusivo
- Aceptar críticas constructivas
- Enfocarse en el bien del proyecto
- Mostrar empatía hacia otros colaboradores

### Comportamiento Inaceptable

- Lenguaje o imágenes sexualizadas
- Trolling, insultos o comentarios despectivos
- Acoso público o privado
- Publicar información privada sin permiso

## 🙏 Reconocimientos

Todos los contribuidores serán reconocidos en el proyecto. ¡Gracias por tu tiempo y esfuerzo!

---

**¿Preguntas?** No dudes en abrir un Issue o contactar al equipo.
