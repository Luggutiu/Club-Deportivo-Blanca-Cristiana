# ⚠️ Ruta solo para uso temporal de desarrollo
from fastapi import APIRouter
from app.database import engine, Base

router = APIRouter()

@router.get("/crear-tablas")
def crear_tablas():
    """
    Crea todas las tablas definidas en los modelos SQLAlchemy.
    ⚠️ Solo debe usarse en desarrollo o pruebas locales.
    """
    Base.metadata.create_all(bind=engine)
    return {"mensaje": "¡Tablas creadas exitosamente!"}