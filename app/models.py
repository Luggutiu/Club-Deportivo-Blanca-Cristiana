from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    embed_url = Column(String, nullable=False)
    plataforma = Column(String, nullable=True)

class SeccionInformativa(Base):
    __tablename__ = "secciones"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, unique=True, index=True)
    contenido = Column(Text)