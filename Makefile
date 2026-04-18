# SafeTalk Makefile
# Comandos útiles para desarrollo

.PHONY: help install test lint format clean run-baseline run-beto

help:  ## Mostrar esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Instalar dependencias
	uv pip install -e ".[all]"
	pre-commit install

install-dev:  ## Instalar solo dependencias de desarrollo
	uv pip install -e ".[dev]"

test:  ## Ejecutar tests
	pytest tests/ -v

test-cov:  ## Ejecutar tests con coverage
	pytest tests/ --cov=src/safetalk --cov-report=html --cov-report=term

lint:  ## Verificar código con ruff
	ruff check src/ tests/

lint-fix:  ## Corregir problemas de linting automáticamente
	ruff check src/ tests/ --fix

format:  ## Formatear código con black
	black src/ tests/ scripts/

format-check:  ## Verificar formateo sin modificar
	black src/ tests/ scripts/ --check

typecheck:  ## Verificar tipos con mypy
	mypy src/

quality:  ## Ejecutar todos los checks de calidad
	@echo "Running ruff..."
	ruff check src/ tests/
	@echo "\nRunning black..."
	black src/ tests/ scripts/ --check
	@echo "\nRunning mypy..."
	mypy src/
	@echo "\nRunning tests..."
	pytest tests/ -v

clean:  ## Limpiar archivos temporales
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/ .ruff_cache/

download-dataset:  ## Listar datasets disponibles de Hugging Face
	python scripts/download_huggingface_dataset.py --list

convert-dataset:  ## Convertir dataset al formato SafeTalk (ejemplo)
	@echo "Uso: python scripts/convert_dataset.py --input data/raw/original.csv --output data/processed/converted.csv"
	@echo "Ver README.md sección 'Preparación de Datos' para más detalles"

run-baseline:  ## Ejecutar entrenamiento del modelo baseline
	python scripts/train_baseline.py --data data/processed/train.csv

run-beto:  ## Ejecutar fine-tuning de BETO
	python scripts/train_beto.py --data data/processed/train.csv

notebook:  ## Iniciar Jupyter Lab
	jupyter lab

docs:  ## Generar documentación (futuro)
	@echo "Documentación por implementar"

.DEFAULT_GOAL := help
