from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Usa la URL de conexión externa que Render te dio
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://club_deportivo_blanca_cristiana_user:cB5MseIHzi8AshEsfljbYM6lPywFA3zO@dpg-d1dkcjripnbc73dcmccg-a/club_deportivo_blanca_cristiana")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

from app.database import SessionLocal
from sqlalchemy.orm import Session
from typing import Generator

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()