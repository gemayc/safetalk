import os

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

# 1. Conexión a Supabase
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Mapeo de la Tabla 1 (mensajes_moderacion)
class MensajeModeracion(Base):
    __tablename__ = "mensajes_moderacion"

    id = Column(Integer, primary_key=True, autoincrement=True) # int8 en BD
    mensaje = Column(Text)                                     # text en BD
    prediccion = Column(String)                                # varchar en BD
    confianza = Column(Float)                                  # float8 en BD
    plataforma = Column(String, default="telegram")            # varchar en BD
    revisado = Column(Boolean, default=False)                  # bool en BD
    label_correcta = Column(String, nullable=True)             # varchar en BD
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# 3. Mapeo de la Tabla 2 (feedback_modelo)
class FeedbackModelo(Base):
    __tablename__ = "feedback_modelo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mensaje_id = Column(Integer, ForeignKey("mensajes_moderacion.id")) 
    mensaje = Column(Text)
    prediccion_modelo = Column(String)
    label_real = Column(String)
    comentario = Column(Text, nullable=True)
    revisado_por_humano = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Como ya creaste las tablas en la web de Supabase, esta línea 
# solo conectará los modelos de Python con tus tablas existentes.
Base.metadata.create_all(bind=engine)