#!/bin/bash
# Sincroniza el código src/ al espacio de despliegue de Hugging Face
#
# Uso (desde la raíz del proyecto):
#     bash scripts/sync_hf_space.sh

set -e  # Para el script si hay un error

# Colores para los mensajes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'  # Sin color

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Sincronizando código → Hugging Face Space${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"

# Rutas
SOURCE_DIR="src"
TARGET_DIR="deploy/hf-space/src"

# Verificar que existe la carpeta fuente
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${YELLOW}❌ Error: no se encuentra la carpeta $SOURCE_DIR${NC}"
    echo "¿Estás ejecutando el script desde la raíz del proyecto?"
    exit 1
fi

# Verificar que existe la carpeta destino
if [ ! -d "deploy/hf-space" ]; then
    echo -e "${YELLOW}❌ Error: no se encuentra deploy/hf-space${NC}"
    echo "Crea primero la carpeta con: mkdir -p deploy/hf-space"
    exit 1
fi

# Borrar la carpeta destino si ya existe (para empezar limpio)
if [ -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}🗑️  Eliminando copia anterior: $TARGET_DIR${NC}"
    rm -rf "$TARGET_DIR"
fi

# Copiar src/ al destino
echo -e "${GREEN}📂 Copiando $SOURCE_DIR/ → $TARGET_DIR/${NC}"
cp -r "$SOURCE_DIR" "$TARGET_DIR"

# Eliminar __pycache__ si se copiaron (basura de Python)
find "$TARGET_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Mostrar resultado
echo -e "${GREEN}✅ Sincronización completada${NC}"
echo ""
echo -e "${BLUE}Archivos sincronizados:${NC}"
ls -R "$TARGET_DIR"

echo ""
echo -e "${GREEN}🎉 Listo. Ya puedes hacer commit y push al Space.${NC}"