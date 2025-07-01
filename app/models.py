from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from datetime import datetime

Base = declarative_base()

# ---------------------------
# Modelo: Publicación (Post)
# ---------------------------
from sqlalchemy import Boolean  # asegúrate de tenerlo importado

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=True)
    texto = Column(Text, nullable=True)
    imagen_url = Column(String, nullable=True)
    imagen_archivo = Column(String, nullable=True)
    url = Column(String, nullable=True)
    embed_url = Column(String, nullable=True)
    video_embed = Column(Text, nullable=True)
    plataforma = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    likes = Column(Integer, default=0)  # Nuevo campo

    publicado = Column(Boolean, default=True) 
# ---------------------------
# Modelo: Sección Informativa
# ---------------------------
class SeccionInformativa(Base):
    __tablename__ = "secciones"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)  # Nuevo campo
    contenido = Column(Text, nullable=False)
    imagen_url = Column(String, nullable=True)

# ---------------------------
# Modelo: Horario de actividad
# ---------------------------
class Horario(Base):
    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, index=True)
    dia = Column(String, nullable=False)
    hora_inicio = Column(String, nullable=False)
    hora_fin = Column(String, nullable=False)
    actividad = Column(String, nullable=False)
    publicado = Column(Boolean, default=False, nullable=False)
    
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
from sqlalchemy import Column, Integer, String
from app.database import Base

class Suscriptor(Base):
    __tablename__ = "suscriptores"

    id = Column(Integer, primary_key=True, index=True)
    tipo_documento = Column(String, nullable=False)
    numero_documento = Column(String, unique=True, nullable=False)
    nombre_completo = Column(String, nullable=False)
    celular = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)