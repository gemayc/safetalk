# """
# Bot de Telegram que detecta bullying en mensajes.

# Se conecta a la API de SafeTalk (desplegada en Hugging Face Spaces)
# y analiza cada mensaje que recibe. Integra un sistema híbrido:
# lista negra local para insultos evidentes y modelo de IA para contexto.
# """
# import sys
# import os
# import re
# import logging
# import requests
# from dotenv import load_dotenv
# from telegram import Update
# from telegram.constants import ChatType, ParseMode
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     filters,
#     ContextTypes
# )


# # Esto le dice a Python que mire en la carpeta superior (src) para buscar archivos
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # Ahora ya puedes importar tu base de datos y tus tablas sin que dé error
# from database import SessionLocal, MensajeModeracion, FeedbackModelo

# # Cargar variables de entorno (.env)
# load_dotenv()


# # ============================================================
# # 🔧 CONFIGURACIÓN DEL BOT
# # ============================================================

# # Umbral de confianza para BORRAR un mensaje (en grupos)
# UMBRAL_CONFIANZA = 0.65  # Ajustado al 65%

# # ¿Avisar en el grupo cuando se borra un mensaje?
# AVISAR_AL_BORRAR = True

# # ¿El bot funciona también en chats privados (1 a 1)?
# FUNCIONAR_EN_PRIVADO = True

# # Lista negra de palabras inaceptables sin importar el contexto.
# # Si el bot detecta alguna de estas, no gasta recursos llamando a la API.
# import re

# # ============================================================
# # 🛡️ SISTEMA ANTI-OFUSCACIÓN (Lista Negra Avanzada)
# # ============================================================

# BLACKLIST_BASE = [
#     "gilipollas", "subnormal", "idiota", "puta", 
#     "retrasado", "maricon", "imbecil","zorra", "estupido","estupidos", "tonto", "tarado", "cretino", "pendejo", "cabrón", "hijo de puta", "maldito", "bastardo", "gordo", "fea", "feo", "lameculos", "cerdo", "zopenco", "capullo", "chinga tu madre", "pendeja", "pendejo", "puto", "putos","puta madre", 
# ]

# # Aquí ocurre la magia: convertimos las palabras en patrones Regex flexibles.
# # "puta" se convierte en el patrón \bp+u+t+a+\b (detecta "puta", "puuuutaaa", "ptaaaa")
# import re

# # ============================================================
# # 🛡️ SISTEMA ANTI-OFUSCACIÓN (Lista Negra Ampliada, Plurales y Acentos)
# # ============================================================

# BLACKLIST_BASE = [
#     "gilipollas", "subnormal", "idiota", "puta", "puto", "putas", "putos",
#     "retrasado", "maricon", "imbecil", "zorra", "estupido", "estupidos", 
#     "tonto", "tarado", "cretino", "pendejo", "pendeja", "cabrón", "maldito", 
#     "bastardo", "gordo", "fea", "feo", "lameculos", "cerdo", "zopenco", 
#     "capullo", "hijo de puta", "chinga tu madre", "puta madre"
# ]

# # Eliminamos duplicados exactos automáticamente para optimizar memoria
# BLACKLIST_BASE = list(set(BLACKLIST_BASE))

# # Diccionario para que el patrón acepte letras con o sin tilde de forma flexible
# MAPA_ACENTOS = {
#     'a': '[aá]', 'e': '[eé]', 'i': '[ií]', 'o': '[oó]', 'u': '[uú]',
#     'á': '[aá]', 'é': '[eé]', 'í': '[ií]', 'ó': '[oó]', 'ú': '[uú]'
# }

# BLACKLIST_REGEX = []
# for palabra in BLACKLIST_BASE:
#     # 1. Simplificamos letras repetidas consecutivas (ej: 'putaaaa' -> 'puta')
#     # Conservamos los espacios intactos para las frases compuestas
#     palabra_simplificada = re.sub(r'(.)\1+', r'\1', palabra)
    
#     # 2. Construimos el patrón letra a letra
#     componentes = []
#     for c in palabra_simplificada:
#         if c == ' ':
#             componentes.append(r' +')  # Soporta múltiples espacios intermedios
#         elif c in MAPA_ACENTOS:
#             componentes.append(f"{MAPA_ACENTOS[c]}+")  # Soporta tildes y repetición (ej: óóóó)
#         else:
#             componentes.append(f"{c}+")  # Soporta repetición de consonantes (ej: pppp)
            
#     patron_base = r''.join(componentes)
    
#     # 3. 🪄 MAGIA PARA PLURALES GENERALES:
#     # Permite que cualquier palabra o frase termine opcionalmente en 'e', 's' o 'es' repetidas
#     patron_con_plural = f"{patron_base}(?:e+)?(?:s+)?"
    
#     # 4. Compilamos el patrón con límites de palabra (\b) e ignorando mayúsculas
#     BLACKLIST_REGEX.append(re.compile(fr'\b{patron_con_plural}\b', re.IGNORECASE))

   
# # URL de la API SafeTalk
# API_URL = os.getenv("SAFETALK_API_URL")

# # ============================================================

# # Configurar logging
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)

# TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# if not TELEGRAM_TOKEN:
#     raise ValueError("TELEGRAM_BOT_TOKEN no está en el archivo .env")


# # ============================================================
# # COMANDOS DEL BOT
# # ============================================================

# async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     usuario = update.effective_user.first_name
#     mensaje = (
#         f"👋 ¡Hola, {usuario}!\n\n"
#         f"Soy *SafeTalk Bot* 🛡️\n\n"
#         f"Mi misión es detectar mensajes ofensivos o de bullying.\n\n"
#         f"📍 *En chats privados:*\n"
#         f"Envíame cualquier mensaje y te diré si es ofensivo.\n\n"
#         f"📍 *En grupos:*\n"
#         f"Analizo automáticamente todos los mensajes y borro los "
#         f"ofensivos (necesito ser admin).\n\n"
#         f"*Comandos:*\n"
#         f"/start - Mostrar este mensaje\n"
#         f"/help - Ayuda\n"
#         f"/info - Información del modelo"
#     )
#     await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)

# async def comando_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     mensaje = (
#         "📖 *Cómo usar el bot:*\n\n"
#         "*Modo Chat Privado:*\n"
#         "1️⃣ Envíame un mensaje\n"
#         "2️⃣ Te respondo si es ofensivo o no\n"
#         "3️⃣ Te muestro el porcentaje de confianza\n\n"
#         "*Modo Grupo:*\n"
#         "1️⃣ Añádeme al grupo\n"
#         "2️⃣ Hazme admin con permiso de borrar mensajes\n"
#         f"3️⃣ Borraré automáticamente los mensajes ofensivos\n"
#         f"   (confianza ≥ {UMBRAL_CONFIANZA*100:.0f}%)\n\n"
#         "🤖 Uso el modelo BETO (BERT español) fine-tuned + Reglas."
#     )
#     await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)

# async def comando_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         respuesta = requests.get(f"{API_URL}/model/info", timeout=10)
#         respuesta.raise_for_status()
#         info = respuesta.json()

#         mensaje = (
#             "🤖 *Información del Modelo*\n\n"
#             f"📊 *Modelo:* {info.get('nombre', 'N/A')}\n"
#             f"🔢 *Versión:* {info.get('version', 'N/A')}\n\n"
#             f"📈 *Métricas en TEST:*\n"
#             f"• F1-Score: {info.get('f1_score', 0)*100:.2f}%\n"
#             f"• Accuracy: {info.get('accuracy', 0)*100:.2f}%\n"
#             f"• Precision: {info.get('precision', 0)*100:.2f}%\n"
#             f"• Recall: {info.get('recall', 0)*100:.2f}%\n\n"
#             f"⚙️ *Configuración del bot:*\n"
#             f"• Umbral para borrar: {UMBRAL_CONFIANZA*100:.0f}%"
#         )
#     except Exception as e:
#         logger.error(f"Error obteniendo info del modelo: {e}")
#         mensaje = "❌ No pude conectar con la API. Intenta más tarde."

#     await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)


# # ============================================================
# # FUNCIONES DE ANÁLISIS E INFERENCIA
# # ============================================================

# def predecir_con_api(texto: str) -> dict | None:
#     try:
#         respuesta = requests.post(
#             f"{API_URL}/predict",
#             json={"texto": texto},
#             timeout=30
#         )
#         respuesta.raise_for_status()
#         return respuesta.json()
#     except requests.exceptions.Timeout:
#         logger.error("Timeout al llamar a la API")
#         return None
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Error al llamar a la API: {e}")
#         return None

# def evaluar_mensaje(texto: str) -> dict | None:
#     """
#     Evalúa el mensaje combinando reglas avanzadas (anti-leetspeak) y la API.
#     """
#     # 1. Normalización Anti-Ofuscación (Traductor Leetspeak)
#     # Cambiamos números y símbolos típicos por las letras que intentan imitar
#     # 0 -> o, @ -> a, 4 -> a, 1 -> i, 3 -> e, 5 -> s
#     traductor = str.maketrans('0@4135', 'oaaies')
#     texto_norm = texto.translate(traductor).lower()
    
#     # Quitamos puntuación molesta que separe las letras (ej: p.u.t.a)
#     texto_norm = re.sub(r'[^\w\s]', '', texto_norm).strip()

#     # 2. Búsqueda de insultos con letras repetidas ("putaaaa")
#     for patron in BLACKLIST_REGEX:
#         if patron.search(texto_norm):
#             logger.info(f"[FILTRO LOCAL] Insulto ofuscado detectado: {patron.pattern}")
#             return {
#                 "prediccion": "ofensivo",
#                 "confianza": 1.0,  # 100% de confianza por regla explícita
#                 "origen": "filtro_avanzado"
#             }
    
#     # 3. Si pasa el filtro local, se lo enviamos a la IA para buscar contexto.
#     # IMPORTANTE: Enviamos el `texto` ORIGINAL, no el normalizado, porque 
#     # la IA de Hugging Face se alimenta del tono real (mayúsculas, exclamaciones).
#     resultado = predecir_con_api(texto)
#     if resultado:
#         resultado["origen"] = "modelo_hf"
#     return resultado


# # ============================================================
# # MANEJADORES DE MENSAJES
# # ============================================================

# async def manejar_mensaje_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     mensaje = update.message
#     if not mensaje or not mensaje.text:
#         return

#     texto = mensaje.text
#     usuario = mensaje.from_user

#     logger.info(f"[GRUPO] Mensaje de {usuario.username or usuario.first_name}: {texto[:50]}")

#     # Llamar a la función evaluadora (Blacklist + API)
#     resultado = evaluar_mensaje(texto)
#     if not resultado:
#         return  

#     prediccion = resultado["prediccion"]
#     confianza = resultado["confianza"]
#     origen = resultado.get("origen", "desconocido")

#     if prediccion != "ofensivo" or confianza < UMBRAL_CONFIANZA:
#         return

#     # ES OFENSIVO → BORRAR + AVISAR
#     logger.info(f"[GRUPO] Mensaje OFENSIVO detectado ({confianza*100:.1f}% vía {origen}). Borrando...")

#     try:
#         await mensaje.delete()
#         logger.info("[GRUPO] Mensaje borrado correctamente")
#     except Exception as e:
#         logger.error(f"[GRUPO] Error al borrar mensaje: {e}")
#         await mensaje.reply_text(
#             "⚠️ He detectado un mensaje ofensivo pero no puedo borrarlo.\n"
#             "Por favor, hazme administrador del grupo con permiso de borrar mensajes."
#         )
#         return

#     if AVISAR_AL_BORRAR:
#         mencion_usuario = f"@{usuario.username}" if usuario.username else usuario.first_name
#         texto_seguro = texto.replace("*", "").replace("_", "").replace("`", "").replace("[", "").replace("]", "")
#         if len(texto_seguro) > 200:
#             texto_seguro = texto_seguro[:200] + "..."

#         # Si viene de la blacklist, le damos un aviso 100% seguro.
#         fuente_aviso = "Filtro de reglas" if origen == "blacklist" else f"{confianza*100:.1f}%"
        
#         aviso = (
#             f"🛡️ He eliminado un mensaje ofensivo\n\n"
#             f"👤 Usuario: {mencion_usuario}\n"
#             f"📝 Contenido: \"{texto_seguro}\"\n"
#             f"📊 Confianza: {fuente_aviso}"
#         )

#         try:
#             await context.bot.send_message(chat_id=mensaje.chat_id, text=aviso)
#         except Exception as e:
#             logger.error(f"[GRUPO] Error al enviar aviso: {e}")


# async def manejar_mensaje_privado(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     mensaje = update.message
#     if not mensaje or not mensaje.text:
#         return

#     texto = mensaje.text
#     usuario = mensaje.from_user

#     logger.info(f"[PRIVADO] Mensaje de {usuario.first_name}: {texto[:50]}")
#     msg_procesando = await mensaje.reply_text("🔍 Analizando...")

#     resultado = evaluar_mensaje(texto)
#     if not resultado:
#         await msg_procesando.edit_text("❌ Error al conectar con la API. Intenta más tarde.")
#         return

#     prediccion = resultado["prediccion"]
#     confianza = resultado["confianza"]
#     origen = resultado.get("origen", "desconocido")

#     if prediccion == "ofensivo":
#         emoji = "⚠️"
#         estado = "*OFENSIVO*"
#     else:
#         emoji = "✅"
#         estado = "*NO ofensivo*"

#     fuente_texto = "Filtro estricto (Palabra prohibida)" if origen == "blacklist" else "IA"
    
#     respuesta = (
#         f"{emoji} El mensaje es {estado}\n\n"
#         f"📊 Confianza: {confianza*100:.2f}%\n"
#         f"⚙️ Origen de decisión: {fuente_texto}"
#     )

#     await msg_procesando.edit_text(respuesta, parse_mode=ParseMode.MARKDOWN)


# async def enrutar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not update.message:
#         return

#     chat_type = update.message.chat.type

#     if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
#         await manejar_mensaje_grupo(update, context)
#     elif chat_type == ChatType.PRIVATE:
#         if FUNCIONAR_EN_PRIVADO:
#             await manejar_mensaje_privado(update, context)


# # ============================================================
# # ARRANCAR EL BOT
# # ============================================================

# def main():
#     logger.info("=" * 60)
#     logger.info("Iniciando SafeTalk Bot")
#     logger.info("=" * 60)
#     logger.info(f"API: {API_URL}")
#     logger.info(f"Umbral confianza: {UMBRAL_CONFIANZA*100:.0f}%")
#     logger.info(f"Avisar al borrar: {AVISAR_AL_BORRAR}")
#     logger.info(f"Funcionar en privado: {FUNCIONAR_EN_PRIVADO}")
#     logger.info("=" * 60)

#     app = Application.builder().token(TELEGRAM_TOKEN).build()

#     app.add_handler(CommandHandler("start", comando_start))
#     app.add_handler(CommandHandler("help", comando_help))
#     app.add_handler(CommandHandler("info", comando_info))
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, enrutar_mensaje))

#     logger.info("Bot listo. Esperando mensajes...")
#     app.run_polling(allowed_updates=Update.ALL_TYPES)

# if __name__ == "__main__":
#     main()


"""
Bot de Telegram que detecta bullying en mensajes.

Se conecta a la API de SafeTalk (desplegada en Hugging Face Spaces)
y analiza cada mensaje que recibe. Integra un sistema híbrido:
lista negra local para insultos evidentes y modelo de IA para contexto.
"""
import sys
import os
import re
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

# Esto le dice a Python que mire en la carpeta superior (src) para buscar archivos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importamos la base de datos y las tablas
from database import SessionLocal, MensajeModeracion, FeedbackModelo

# Cargar variables de entorno (.env)
load_dotenv()


# ============================================================
#  CONFIGURACIÓN DEL BOT
# ============================================================

UMBRAL_CONFIANZA = 0.65  # Ajustado al 65%
AVISAR_AL_BORRAR = True
FUNCIONAR_EN_PRIVADO = True


MI_TELEGRAM_ID = int(os.getenv("MI_TELEGRAM_ID"))

# ============================================================
#  SISTEMA ANTI-OFUSCACIÓN (Lista Negra Ampliada, Plurales y Acentos)
# ============================================================

BLACKLIST_BASE = [
    "gilipollas", "subnormal", "idiota", "puta", "puto", "putas", "putos",
    "retrasado", "maricon", "imbecil", "zorra", "estupido", "estupidos", 
    "tonto", "tarado", "cretino", "pendejo", "pendeja", "cabrón", "maldito", 
    "bastardo", "gordo", "fea", "feo", "lameculos", "cerdo", "zopenco", 
    "capullo", "hijo de puta", "chinga tu madre", "puta madre"
]

# Eliminamos duplicados exactos automáticamente para optimizar memoria
BLACKLIST_BASE = list(set(BLACKLIST_BASE))

# Diccionario para que el patrón acepte letras con o sin tilde de forma flexible
MAPA_ACENTOS = {
    'a': '[aá]', 'e': '[eé]', 'i': '[ií]', 'o': '[oó]', 'u': '[uú]',
    'á': '[aá]', 'é': '[eé]', 'í': '[ií]', 'ó': '[oó]', 'ú': '[uú]'
}

BLACKLIST_REGEX = []
for palabra in BLACKLIST_BASE:
    palabra_simplificada = re.sub(r'(.)\1+', r'\1', palabra)
    componentes = []
    for c in palabra_simplificada:
        if c == ' ':
            componentes.append(r' +')
        elif c in MAPA_ACENTOS:
            componentes.append(f"{MAPA_ACENTOS[c]}+")
        else:
            componentes.append(f"{c}+")
            
    patron_base = r''.join(componentes)
    patron_con_plural = f"{patron_base}(?:e+)?(?:s+)?"
    BLACKLIST_REGEX.append(re.compile(fr'\b{patron_con_plural}\b', re.IGNORECASE))

   
# URL de la API SafeTalk
API_URL = os.getenv("SAFETALK_API_URL")

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN no está en el archivo .env")


# ============================================================
# COMANDOS DEL BOT
# ============================================================

async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        "🤖 Uso el modelo DistilBERT fine-tuned + Reglas."
    )
    await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)

async def comando_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        respuesta = requests.get(f"{API_URL}/model/info", timeout=10)
        respuesta.raise_for_status()
        info = respuesta.json()

        mensaje = (
            " *Información del Modelo*\n\n"
            f" *Modelo:* {info.get('nombre', 'N/A')}\n"
            f" *Versión:* {info.get('version', 'N/A')}\n\n"
            f" *Configuración del bot:*\n"
            f"• Umbral para borrar: {UMBRAL_CONFIANZA*100:.0f}%"
        )
    except Exception as e:
        logger.error(f"Error obteniendo info del modelo: {e}")
        mensaje = "❌ No pude conectar con la API. Intenta más tarde."

    await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)

# ============================================================
# COMANDO OCULTO: /corregir (Manejo de Feedback)
# ============================================================
async def comando_corregir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario_id = str(update.message.from_user.id)
    print(f"🚨 EL ID QUE ESTÁ LEYENDO ES: {usuario_id}")
    # AÑADE ESTAS DOS LÍNEAS AQUÍ MISMO:
    print(f"DEBUG - ID QUE LLEGA DE TELEGRAM: {usuario_id} (Tipo: {type(usuario_id)})")
    print(f"DEBUG - ID GUARDADO EN AWS (.env): {MI_TELEGRAM_ID} (Tipo: {type(MI_TELEGRAM_ID)})")
    # SEGURIDAD: Solo tú puedes ejecutar este comando
    if str(usuario_id) != str(MI_TELEGRAM_ID):
        return

    try:
        # Extraemos los datos del comando: /corregir <ID> <label> <comentario>
        argumentos = context.args
        if len(argumentos) < 2:
            raise ValueError("Faltan argumentos")
            
        id_mensaje = int(argumentos[0])
        label_real = argumentos[1].lower() # "ofensivo" o "no_ofensivo"
        comentario = " ".join(argumentos[2:]) if len(argumentos) > 2 else ""

        db = SessionLocal()
        
        # 1. Buscamos el mensaje original
        mensaje_original = db.query(MensajeModeracion).filter(MensajeModeracion.id == id_mensaje).first()
        
        if not mensaje_original:
            await update.message.reply_text("❌ Error: Ese ID de mensaje no existe en la BD.")
            db.close()
            return

        # 2. Actualizamos la Tabla 1
        mensaje_original.revisado = True
        mensaje_original.label_correcta = label_real

        # 3. Guardamos en la Tabla 2
        nuevo_feedback = FeedbackModelo(
            mensaje_id=mensaje_original.id,
            mensaje=mensaje_original.mensaje,
            prediccion_modelo=mensaje_original.prediccion,
            label_real=label_real,
            comentario=comentario,
            revisado_por_humano=True
        )
        db.add(nuevo_feedback)
        db.commit()
        db.close()

        await update.message.reply_text(f" ¡Feedback guardado con éxito!\nID Mensaje: {id_mensaje} -> Etiqueta: {label_real}")

    except Exception as e:
        logger.error(f"Error en /corregir: {e}")
        await update.message.reply_text("⚠️ Formato incorrecto.\nUso: `/corregir <ID> <ofensivo/no_ofensivo> <comentario opcional>`", parse_mode=ParseMode.MARKDOWN)


# ============================================================
# FUNCIONES DE ANÁLISIS E INFERENCIA
# ============================================================

def predecir_con_api(texto: str) -> dict | None:
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

def evaluar_mensaje(texto: str) -> dict | None:
    traductor = str.maketrans('0@4135', 'oaaies')
    texto_norm = texto.translate(traductor).lower()
    texto_norm = re.sub(r'[^\w\s]', '', texto_norm).strip()

    for patron in BLACKLIST_REGEX:
        if patron.search(texto_norm):
            return {
                "prediccion": "ofensivo",
                "confianza": 1.0,
                "origen": "blacklist"
            }
    
    resultado = predecir_con_api(texto)
    if resultado:
        resultado["origen"] = "modelo_hf"
    return resultado


# ============================================================
# FUNCIONES AUXILIARES: GUARDAR EN BASE DE DATOS
# ============================================================
def guardar_mensaje_bd(texto: str, prediccion: str, confianza: float, plataforma: str) -> int | None:
    db = SessionLocal()
    try:
        nuevo_mensaje = MensajeModeracion(
            mensaje=texto,
            prediccion=prediccion,
            confianza=confianza,
            plataforma=plataforma,
            revisado=False
        )
        db.add(nuevo_mensaje)
        db.commit()
        msg_id = nuevo_mensaje.id
        return msg_id
    except Exception as e:
        logger.error(f"Error guardando en BD: {e}")
        db.rollback()
        return None
    finally:
        db.close()


# ============================================================
# MANEJADORES DE MENSAJES
# ============================================================

async def manejar_mensaje_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message
    if not mensaje or not mensaje.text:
        return

    texto = mensaje.text
    usuario = mensaje.from_user

    resultado = evaluar_mensaje(texto)
    if not resultado:
        return  

    prediccion = resultado["prediccion"]
    confianza = resultado["confianza"]
    origen = resultado.get("origen", "desconocido")

    #  GUARDAR EN BASE DE DATOS
    msg_id = guardar_mensaje_bd(texto, prediccion, confianza, "telegram_grupo")
    id_texto = f"#{msg_id}" if msg_id else "N/A"

    if prediccion != "ofensivo" or confianza < UMBRAL_CONFIANZA:
        return

    logger.info(f"[GRUPO] Mensaje OFENSIVO detectado. Borrando...")

    try:
        await mensaje.delete()
    except Exception as e:
        logger.error(f"[GRUPO] Error al borrar mensaje: {e}")
        return

    if AVISAR_AL_BORRAR:
        mencion_usuario = f"@{usuario.username}" if usuario.username else usuario.first_name
        texto_seguro = texto.replace("*", "").replace("_", "").replace("`", "").replace("[", "").replace("]", "")
        if len(texto_seguro) > 200:
            texto_seguro = texto_seguro[:200] + "..."

        fuente_aviso = "Filtro de reglas" if origen == "blacklist" else f"{confianza*100:.1f}%"
        
        aviso = (
            f" He eliminado un mensaje ofensivo\n\n"
            f" Usuario: {mencion_usuario}\n"
            f" Contenido: \"{texto_seguro}\"\n"
            f" Confianza: {fuente_aviso}\n"
            f" ID en BD: {id_texto}"
        )

        try:
            await context.bot.send_message(chat_id=mensaje.chat_id, text=aviso)
        except Exception as e:
            logger.error(f"[GRUPO] Error al enviar aviso: {e}")


async def manejar_mensaje_privado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message
    if not mensaje or not mensaje.text:
        return

    texto = mensaje.text

    msg_procesando = await mensaje.reply_text("🔍 Analizando...")

    resultado = evaluar_mensaje(texto)
    if not resultado:
        await msg_procesando.edit_text("❌ Error al conectar con la API. Intenta más tarde.")
        return

    prediccion = resultado["prediccion"]
    confianza = resultado["confianza"]
    origen = resultado.get("origen", "desconocido")

    #  GUARDAR EN BASE DE DATOS
    msg_id = guardar_mensaje_bd(texto, prediccion, confianza, "telegram_privado")
    id_texto = f"#{msg_id}" if msg_id else "N/A"

    if prediccion == "ofensivo":
        emoji = "⚠️"
        estado = "*OFENSIVO*"
    else:
        emoji = "✅"
        estado = "*NO ofensivo*"

    fuente_texto = "Filtro estricto (Palabra prohibida)" if origen == "blacklist" else "IA"
    
    respuesta = (
        f"{emoji} El mensaje es {estado}\n\n"
        f"📊 Confianza: {confianza*100:.2f}%\n"
        f"⚙️ Origen de decisión: {fuente_texto}\n"
        f"🆔 ID en BD: {id_texto}"
    )

    await msg_procesando.edit_text(respuesta, parse_mode=ParseMode.MARKDOWN)


async def enrutar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat_type = update.message.chat.type

    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await manejar_mensaje_grupo(update, context)
    elif chat_type == ChatType.PRIVATE:
        if FUNCIONAR_EN_PRIVADO:
            await manejar_mensaje_privado(update, context)


# ============================================================
# ARRANCAR EL BOT
# ============================================================

def main():
    logger.info("=" * 60)
    logger.info("Iniciando SafeTalk Bot")
    logger.info("=" * 60)
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", comando_start))
    app.add_handler(CommandHandler("help", comando_help))
    app.add_handler(CommandHandler("info", comando_info))
    
    # Registramos nuestro nuevo comando secreto
    app.add_handler(CommandHandler("corregir", comando_corregir))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, enrutar_mensaje))

    logger.info("Bot listo. Esperando mensajes...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()