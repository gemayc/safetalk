"""
Bot de Telegram que detecta bullying en mensajes.

Se conecta a la API de SafeTalk (desplegada en Hugging Face Spaces)
y analiza cada mensaje que recibe.

Comportamiento:
- En grupos: borra mensajes ofensivos y avisa citando el contenido
- En chats privados: analiza y responde con el resultado (no borra)
"""

import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatType, ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Cargar variables de entorno (.env)
load_dotenv()


# ============================================================
# 🔧 CONFIGURACIÓN DEL BOT
# (modifica estos valores según necesites)
# ============================================================

# Umbral de confianza para BORRAR un mensaje (en grupos)
# Si la confianza es MAYOR o IGUAL a este valor, el mensaje se borra
# Rango: 0.0 a 1.0  (ej: 0.90 = 90%)
UMBRAL_CONFIANZA = 0.90

# ¿Avisar en el grupo cuando se borra un mensaje?
# True  = avisa citando el contenido borrado (transparente)
# False = borra silenciosamente
AVISAR_AL_BORRAR = True

# ¿El bot funciona también en chats privados (1 a 1)?
# True  = sí, analiza mensajes en privados (sin borrar)
# False = solo funciona en grupos
FUNCIONAR_EN_PRIVADO = True

# URL de la API SafeTalk. Se puede sobrescribir con la variable de entorno
# SAFETALK_API_URL (útil para apuntar a un Space de pruebas sin tocar el código).
API_URL = os.getenv("SAFETALK_API_URL", "https://Gemita284-safetalk-api.hf.space")

# ============================================================


# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cargar token del .env
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN no está en el archivo .env"
    )


# ============================================================
# COMANDOS DEL BOT
# ============================================================

async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Se ejecuta cuando alguien envía /start"""
    usuario = update.effective_user.first_name

    mensaje = (
        f"👋 ¡Hola, {usuario}!\n\n"
        f"Soy *SafeTalk Bot* 🛡️\n\n"
        f"Mi misión es detectar mensajes ofensivos o de bullying.\n\n"
        f"📍 *En chats privados:*\n"
        f"Envíame cualquier mensaje y te diré si es ofensivo.\n\n"
        f"📍 *En grupos:*\n"
        f"Analizo automáticamente todos los mensajes y borro los "
        f"ofensivos (necesito ser admin).\n\n"
        f"*Comandos:*\n"
        f"/start - Mostrar este mensaje\n"
        f"/help - Ayuda\n"
        f"/info - Información del modelo"
    )

    await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)


async def comando_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Se ejecuta cuando alguien envía /help"""
    mensaje = (
        "📖 *Cómo usar el bot:*\n\n"
        "*Modo Chat Privado:*\n"
        "1️⃣ Envíame un mensaje\n"
        "2️⃣ Te respondo si es ofensivo o no\n"
        "3️⃣ Te muestro el porcentaje de confianza\n\n"
        "*Modo Grupo:*\n"
        "1️⃣ Añádeme al grupo\n"
        "2️⃣ Hazme admin con permiso de borrar mensajes\n"
        f"3️⃣ Borraré automáticamente los mensajes ofensivos\n"
        f"   (confianza ≥ {UMBRAL_CONFIANZA*100:.0f}%)\n\n"
        "🤖 Uso el modelo BETO (BERT español) fine-tuned."
    )

    await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)


async def comando_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra información del modelo consultando la API"""
    try:
        respuesta = requests.get(f"{API_URL}/model/info", timeout=10)
        respuesta.raise_for_status()
        info = respuesta.json()

        mensaje = (
            "🤖 *Información del Modelo*\n\n"
            f"📊 *Modelo:* {info.get('nombre', 'N/A')}\n"
            f"🔢 *Versión:* {info.get('version', 'N/A')}\n\n"
            f"📈 *Métricas en TEST:*\n"
            f"• F1-Score: {info.get('f1_score', 0)*100:.2f}%\n"
            f"• Accuracy: {info.get('accuracy', 0)*100:.2f}%\n"
            f"• Precision: {info.get('precision', 0)*100:.2f}%\n"
            f"• Recall: {info.get('recall', 0)*100:.2f}%\n\n"
            f"⚙️ *Configuración del bot:*\n"
            f"• Umbral para borrar: {UMBRAL_CONFIANZA*100:.0f}%"
        )

    except Exception as e:
        logger.error(f"Error obteniendo info del modelo: {e}")
        mensaje = "❌ No pude conectar con la API. Intenta más tarde."

    await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)


# ============================================================
# FUNCIÓN AUXILIAR: LLAMAR A LA API
# ============================================================

def predecir_con_api(texto: str) -> dict | None:
    """
    Llama a la API SafeTalk para predecir si un texto es ofensivo.

    Args:
        texto: El texto a analizar

    Returns:
        dict con la predicción, o None si hubo error
    """
    try:
        respuesta = requests.post(
            f"{API_URL}/predict",
            json={"texto": texto},
            timeout=30
        )
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.exceptions.Timeout:
        logger.error("Timeout al llamar a la API")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al llamar a la API: {e}")
        return None


# ============================================================
# MANEJADORES DE MENSAJES
# ============================================================

async def manejar_mensaje_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Se ejecuta cuando llega un mensaje en un GRUPO.
    Comportamiento: borra mensajes ofensivos y avisa citando el contenido.
    """
    mensaje = update.message
    if not mensaje or not mensaje.text:
        return

    texto = mensaje.text
    usuario = mensaje.from_user

    logger.info(f"[GRUPO] Mensaje de {usuario.username or usuario.first_name}: {texto[:50]}")

    # Llamar a la API
    resultado = predecir_con_api(texto)
    if not resultado:
        return  # Error: no hacer nada, no spamear el grupo

    prediccion = resultado["prediccion"]
    confianza = resultado["confianza"]

    # Si NO es ofensivo o la confianza es baja → no hacer nada
    if prediccion != "ofensivo" or confianza < UMBRAL_CONFIANZA:
        return

    # ----------------------------------------
    # ES OFENSIVO → BORRAR + AVISAR
    # ----------------------------------------

    logger.info(
        f"[GRUPO] Mensaje OFENSIVO detectado ({confianza*100:.1f}%). "
        f"Borrando..."
    )

    # 1. BORRAR el mensaje
    try:
        await mensaje.delete()
        logger.info("[GRUPO] Mensaje borrado correctamente")
    except Exception as e:
        logger.error(f"[GRUPO] Error al borrar mensaje: {e}")
        # Probablemente el bot no es admin con permisos de borrar
        await mensaje.reply_text(
            "⚠️ He detectado un mensaje ofensivo pero no puedo borrarlo.\n"
            "Por favor, hazme administrador del grupo con permiso de "
            "borrar mensajes."
        )
        return

    # 2. AVISAR en el grupo (si está activado)
    if AVISAR_AL_BORRAR:
        # Mención del usuario (con @ si tiene username, sino con nombre)
        if usuario.username:
            mencion_usuario = f"@{usuario.username}"
        else:
            mencion_usuario = usuario.first_name

        # Escapar el texto para que markdown no rompa
        texto_seguro = texto.replace("*", "").replace("_", "").replace("`", "").replace("[", "").replace("]", "")
        if len(texto_seguro) > 200:
            texto_seguro = texto_seguro[:200] + "..."

        aviso = (
            f"🛡️ He eliminado un mensaje ofensivo\n\n"
            f"👤 Usuario: {mencion_usuario}\n"
            f"📝 Contenido: \"{texto_seguro}\"\n"
            f"📊 Confianza de detección: {confianza*100:.1f}%"
        )

        try:
            await context.bot.send_message(
                chat_id=mensaje.chat_id,
                text=aviso
            )
        except Exception as e:
            logger.error(f"[GRUPO] Error al enviar aviso: {e}")


async def manejar_mensaje_privado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Se ejecuta cuando llega un mensaje en CHAT PRIVADO.
    Comportamiento: analiza y responde con el resultado (no borra).
    """
    mensaje = update.message
    if not mensaje or not mensaje.text:
        return

    texto = mensaje.text
    usuario = mensaje.from_user

    logger.info(f"[PRIVADO] Mensaje de {usuario.first_name}: {texto[:50]}")

    # Avisar que estamos analizando
    msg_procesando = await mensaje.reply_text("🔍 Analizando...")

    # Llamar a la API
    resultado = predecir_con_api(texto)
    if not resultado:
        await msg_procesando.edit_text(
            "❌ Error al conectar con la API. Intenta más tarde."
        )
        return

    prediccion = resultado["prediccion"]
    confianza = resultado["confianza"]

    # Construir respuesta
    if prediccion == "ofensivo":
        emoji = "⚠️"
        estado = "*OFENSIVO*"
    else:
        emoji = "✅"
        estado = "*NO ofensivo*"

    respuesta = (
        f"{emoji} El mensaje es {estado}\n\n"
        f"📊 Confianza: {confianza*100:.2f}%"
    )

    await msg_procesando.edit_text(respuesta, parse_mode=ParseMode.MARKDOWN)


async def enrutar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Decide qué función ejecutar según el tipo de chat:
    - Grupo/Supergrupo → borrar ofensivos
    - Privado → solo analizar (si está activado)
    """
    if not update.message:
        return

    chat_type = update.message.chat.type

    # GRUPOS
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await manejar_mensaje_grupo(update, context)

    # CHATS PRIVADOS
    elif chat_type == ChatType.PRIVATE:
        if FUNCIONAR_EN_PRIVADO:
            await manejar_mensaje_privado(update, context)


# ============================================================
# ARRANCAR EL BOT
# ============================================================

def main():
    """Función principal: arranca el bot"""

    logger.info("=" * 60)
    logger.info("Iniciando SafeTalk Bot")
    logger.info("=" * 60)
    logger.info(f"API: {API_URL}")
    logger.info(f"Umbral confianza: {UMBRAL_CONFIANZA*100:.0f}%")
    logger.info(f"Avisar al borrar: {AVISAR_AL_BORRAR}")
    logger.info(f"Funcionar en privado: {FUNCIONAR_EN_PRIVADO}")
    logger.info("=" * 60)

    # Crear aplicación
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", comando_start))
    app.add_handler(CommandHandler("help", comando_help))
    app.add_handler(CommandHandler("info", comando_info))

    # Mensajes de texto (no comandos)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, enrutar_mensaje)
    )

    logger.info("Bot listo. Esperando mensajes...")
    logger.info("Pulsa Ctrl+C para detener")

    # Arrancar (modo polling)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()