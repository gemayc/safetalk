"""
Bot de Discord que detecta bullying en mensajes.

Se conecta a la API de SafeTalk (desplegada en Hugging Face Spaces)
y analiza cada mensaje que recibe en los canales del servidor.

Comportamiento:
- En canales de servidor: borra mensajes ofensivos (si tiene Manage Messages)
  y publica un embed transparente avisando del contenido borrado.
- En mensajes directos (DM): solo analiza y responde con el resultado, no borra.
"""

import logging
import os

import discord
import requests
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# CONFIGURACIÓN DEL BOT
# ============================================================

# Umbral de confianza para BORRAR un mensaje en un servidor.
# Si la confianza es MAYOR o IGUAL a este valor, el mensaje se borra.
# Alineado con el bot de Telegram tras la migración a BETO V2 (que devuelve
# confianzas más bajas que V1 al estar mejor calibrado).
UMBRAL_CONFIANZA = 0.65

# ¿Avisar en el canal cuando se borra un mensaje?
AVISAR_AL_BORRAR = True

# ¿El bot funciona también en mensajes directos (DM)?
FUNCIONAR_EN_DM = True

# URL de la API SafeTalk. Configurable por SAFETALK_API_URL.
API_URL = os.getenv("SAFETALK_API_URL", "https://Gemita284-safetalk-api.hf.space")

# Timeout de las llamadas a la API (segundos)
API_TIMEOUT = 15

# ============================================================


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# Discord exige declarar los "intents" que el bot va a usar.
# message_content es imprescindible para leer el texto de los mensajes.
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def analizar_texto(texto: str) -> dict | None:
    """Llama al endpoint /predict y devuelve el resultado, o None si falla."""
    try:
        respuesta = requests.post(
            f"{API_URL}/predict",
            json={"texto": texto},
            timeout=API_TIMEOUT,
        )
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.RequestException as e:
        logger.error(f"Error consultando la API: {e}")
        return None


def embed_aviso(autor: str, contenido: str, confianza: float) -> discord.Embed:
    """Construye el embed que se publica tras borrar un mensaje ofensivo."""
    embed = discord.Embed(
        title="Mensaje eliminado",
        description="He detectado contenido potencialmente ofensivo y lo he borrado.",
        color=discord.Color.red(),
    )
    embed.add_field(name="Usuario", value=autor, inline=True)
    embed.add_field(name="Confianza", value=f"{confianza * 100:.1f}%", inline=True)
    embed.add_field(name="Contenido", value=f"`{contenido}`", inline=False)
    embed.set_footer(text="SafeTalk · Bot de moderación")
    return embed


def embed_analisis(texto: str, resultado: dict) -> discord.Embed:
    """Construye el embed de respuesta en DM (solo análisis, sin acción)."""
    es_ofensivo = resultado["prediccion"] == "ofensivo"
    color = discord.Color.red() if es_ofensivo else discord.Color.green()
    embed = discord.Embed(
        title="Resultado del análisis",
        description=f"`{texto}`",
        color=color,
    )
    embed.add_field(name="Predicción", value=resultado["prediccion"], inline=True)
    embed.add_field(
        name="Confianza", value=f"{resultado['confianza'] * 100:.1f}%", inline=True
    )
    embed.set_footer(text="SafeTalk · Solo análisis (los DMs no se borran)")
    return embed


@client.event
async def on_ready():
    logger.info("=" * 60)
    logger.info("SafeTalk Discord Bot conectado")
    logger.info("=" * 60)
    logger.info(f"Usuario: {client.user}")
    logger.info(f"API: {API_URL}")
    logger.info(f"Umbral confianza: {UMBRAL_CONFIANZA * 100:.0f}%")
    logger.info(f"Servidores: {len(client.guilds)}")
    for guild in client.guilds:
        logger.info(f"  - {guild.name} ({guild.id})")
    logger.info("=" * 60)


@client.event
async def on_message(message: discord.Message):
    # Ignorar mensajes del propio bot (evita bucles)
    if message.author == client.user:
        return

    # Ignorar comandos vacíos
    texto = message.content.strip()
    if not texto:
        return

    es_dm = message.guild is None

    if es_dm and not FUNCIONAR_EN_DM:
        return

    contexto = "DM" if es_dm else f"{message.guild.name}#{message.channel.name}"
    logger.info(f"[{contexto}] Mensaje de {message.author}: {texto}")

    resultado = analizar_texto(texto)
    if resultado is None:
        return  # error de red, ya logueado

    prediccion = resultado["prediccion"]
    confianza = resultado["confianza"]

    # ---- En DM: solo respondemos con el análisis, nunca borramos ----
    if es_dm:
        await message.channel.send(embed=embed_analisis(texto, resultado))
        return

    # ---- En canal de servidor: aplicamos política de moderación ----
    if prediccion != "ofensivo" or confianza < UMBRAL_CONFIANZA:
        return  # no actuar en zona gris ni en mensajes inocentes

    logger.info(f"[{contexto}] OFENSIVO ({confianza * 100:.1f}%). Borrando...")

    try:
        await message.delete()
    except discord.Forbidden:
        logger.error(
            f"[{contexto}] Sin permisos para borrar. "
            "Asegúrate de tener 'Manage Messages' en este canal."
        )
        return
    except discord.HTTPException as e:
        logger.error(f"[{contexto}] Error al borrar: {e}")
        return

    if AVISAR_AL_BORRAR:
        await message.channel.send(
            embed=embed_aviso(message.author.display_name, texto, confianza)
        )


def main():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise SystemExit(
            "Falta DISCORD_BOT_TOKEN en el entorno (.env). "
            "Sácalo del Discord Developer Portal."
        )
    client.run(token)


if __name__ == "__main__":
    main()
