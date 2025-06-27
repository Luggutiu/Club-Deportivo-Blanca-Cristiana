from sqlalchemy import Column, Integer, String, Text, Boolean
from .database import Base

# Modelo para publicaciones de video
from sqlalchemy import Text, DateTime
from datetime import datetime


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=True)
    texto = Column(Text, nullable=True)
    imagen_url = Column(String, nullable=True)
    imagen_archivo = Column(String, nullable=True)
    url = Column(String, nullable=True)
    embed_url = Column(String, nullable=True)
    video_embed = Column(Text, nullable=True)  # solo si generas HTML embed
    plataforma = Column(String, nullable=True)

# Modelo para secciones informativas (misión, visión, etc.)
class SeccionInformativa(Base):
    __tablename__ = "secciones"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, unique=True, index=True)
    contenido = Column(Text)

# Modelo para horarios de actividades
class Horario(Base):
    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, index=True)
    dia = Column(String, nullable=False)
    hora_inicio = Column(String, nullable=False)
    hora_fin = Column(String, nullable=False)
    actividad = Column(String, nullable=False)
    publicado = Column(Boolean, default=False)