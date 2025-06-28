from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://club_deportivo_blanca_cristiana_user:cB5MseIHzi8AshEsfljbYM6lPywFA3zO@dpg-d1dkcjripnbc73dcmccg-a/club_deportivo_blanca_cristiana"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()