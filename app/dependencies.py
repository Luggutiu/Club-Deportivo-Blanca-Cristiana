from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# 👇 Usa tu string de conexión real aquí
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # O la URL que tú uses en Render
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()