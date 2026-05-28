#!/bin/bash

# 1. Le decimos a Python que la carpeta raíz de nuestro código es 'src'
# Esto evita el temido error "ModuleNotFoundError"
export PYTHONPATH=/app/src:$PYTHONPATH

echo "Iniciando despliegue de SafeTalk Bots..."

# 2. Arrancamos el bot de Telegram en segundo plano (ajusta la ruta si se llama distinto)
python src/telegram/bot.py &
TELEGRAM_PID=$!

# 3. Arrancamos el bot de Discord en segundo plano
python src/discord_bot/bot.py &
DISCORD_PID=$!

echo "Bots lanzados. Discord PID: $DISCORD_PID, Telegram PID: $TELEGRAM_PID"

# 4. Esperamos a que cualquier proceso termine o falle.
# Si uno de los bots hace 'crash', el contenedor se reiniciará automáticamente.
wait -n

# Salimos devolviendo el código de error correspondiente
exit $?