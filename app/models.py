from sqlalchemy import Column, Integer, String, Text, Boolean
from .database import Base

# Modelo para publicaciones de video
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    embed_url = Column(String, nullable=False)
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
    publicado = Column(Boolean, default=True)