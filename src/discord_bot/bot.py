"""
Bot de Discord que detecta bullying en mensajes.

Se conecta a la API de SafeTalk (desplegada en Hugging Face Spaces)
y analiza cada mensaje que recibe en los canales del servidor.
Incluye un filtro local avanzado (Regex) para detectar insultos directos y ofuscados.
"""

import logging
import os
import re

import discord
import requests
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# CONFIGURACIÓN DEL BOT
# ============================================================

UMBRAL_CONFIANZA = 0.65
AVISAR_AL_BORRAR = True
FUNCIONAR_EN_DM = True
API_URL = os.getenv("SAFETALK_API_URL")
API_TIMEOUT = 15

# ============================================================
# 🛡️ SISTEMA ANTI-OFUSCACIÓN (Lista Negra Avanzada)
# ============================================================

BLACKLIST_BASE = list(set([
    "gilipollas", "subnormal", "idiota", "puta", "puto", "putas", "putos",
    "retrasado", "maricon", "imbecil", "zorra", "estupido", "estupidos", 
    "tonto", "tarado", "cretino", "pendejo", "pendeja", "cabrón", "maldito", 
    "bastardo", "gordo", "fea", "feo", "lameculos", "cerdo", "zopenco", 
    "capullo", "hijo de puta", "chinga tu madre", "puta madre"
]))

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


# ============================================================
# INICIALIZACIÓN
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# ============================================================
# FUNCIONES DE EVALUACIÓN
# ============================================================

def analizar_texto_api(texto: str) -> dict | None:
    """Llama al endpoint /predict de Hugging Face."""
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

def evaluar_mensaje(texto: str) -> dict | None:
    """
    Evalúa el mensaje usando primero la Blacklist local y luego la API.
    """
    # 1. Normalización Anti-Ofuscación (Traductor Leetspeak)
    traductor = str.maketrans('0@4135', 'oaaies')
    texto_norm = texto.translate(traductor).lower()
    texto_norm = re.sub(r'[^\w\s]', '', texto_norm).strip()

    # 2. Búsqueda de insultos locales
    for patron in BLACKLIST_REGEX:
        if patron.search(texto_norm):
            logger.info(f"[FILTRO LOCAL] Insulto ofuscado detectado: {patron.pattern}")
            return {
                "prediccion": "ofensivo",
                "confianza": 1.0,
                "origen": "filtro_avanzado"
            }
    
    # 3. Si pasa el filtro, se lo enviamos a BETO
    resultado = analizar_texto_api(texto)
    if resultado:
        resultado["origen"] = "modelo_hf"
    return resultado


# ============================================================
# EMBEDS DE DISCORD
# ============================================================

def embed_aviso(autor: str, contenido: str, confianza: float, origen: str) -> discord.Embed:
    embed = discord.Embed(
        title="Mensaje eliminado",
        description="He detectado contenido potencialmente ofensivo y lo he borrado.",
        color=discord.Color.red(),
    )
    fuente_aviso = "Filtro de reglas" if origen == "filtro_avanzado" else f"{confianza * 100:.1f}%"
    
    embed.add_field(name="Usuario", value=autor, inline=True)
    embed.add_field(name="Confianza", value=fuente_aviso, inline=True)
    embed.add_field(name="Contenido", value=f"`{contenido}`", inline=False)
    embed.set_footer(text="SafeTalk · Bot de moderación")
    return embed


def embed_analisis(texto: str, resultado: dict) -> discord.Embed:
    es_ofensivo = resultado["prediccion"] == "ofensivo"
    color = discord.Color.red() if es_ofensivo else discord.Color.green()
    origen_texto = "Filtro estricto" if resultado.get("origen") == "filtro_avanzado" else "IA (BETO)"
    
    embed = discord.Embed(
        title="Resultado del análisis",
        description=f"`{texto}`",
        color=color,
    )
    embed.add_field(name="Predicción", value=resultado["prediccion"], inline=True)
    embed.add_field(
        name="Confianza", value=f"{resultado['confianza'] * 100:.1f}%", inline=True
    )
    embed.add_field(name="Motor", value=origen_texto, inline=False)
    embed.set_footer(text="SafeTalk · Solo análisis (los DMs no se borran)")
    return embed


# ============================================================
# EVENTOS DEL BOT
# ============================================================

@client.event
async def on_ready():
    logger.info("=" * 60)
    logger.info("SafeTalk Discord Bot conectado")
    logger.info("=" * 60)
    logger.info(f"Usuario: {client.user}")
    logger.info(f"API: {API_URL}")
    logger.info(f"Umbral confianza: {UMBRAL_CONFIANZA * 100:.0f}%")
    logger.info(f"Filtros Regex cargados: {len(BLACKLIST_REGEX)}")
    logger.info(f"Servidores: {len(client.guilds)}")
    logger.info("=" * 60)


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    texto = message.content.strip()
    if not texto:
        return

    es_dm = message.guild is None

    if es_dm and not FUNCIONAR_EN_DM:
        return

    contexto = "DM" if es_dm else f"{message.guild.name}#{message.channel.name}"
    
    # Evaluar mensaje (Regex + API)
    resultado = evaluar_mensaje(texto)
    if resultado is None:
        return  

    prediccion = resultado["prediccion"]
    confianza = resultado["confianza"]
    origen = resultado.get("origen", "desconocido")

    # ---- En DM: solo respondemos con el análisis ----
    if es_dm:
        logger.info(f"[{contexto}] Analizado por {origen}")
        await message.channel.send(embed=embed_analisis(texto, resultado))
        return

    # ---- En canal de servidor: aplicamos política de moderación ----
    if prediccion != "ofensivo" or confianza < UMBRAL_CONFIANZA:
        return 

    logger.info(f"[{contexto}] OFENSIVO ({confianza * 100:.1f}% vía {origen}). Borrando...")

    try:
        await message.delete()
    except discord.Forbidden:
        logger.error(f"[{contexto}] Sin permisos para borrar (Falta 'Manage Messages').")
        return
    except discord.HTTPException as e:
        logger.error(f"[{contexto}] Error al borrar: {e}")
        return

    if AVISAR_AL_BORRAR:
        await message.channel.send(
            embed=embed_aviso(message.author.display_name, texto, confianza, origen)
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