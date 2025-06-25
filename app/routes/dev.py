# ⚠️ Ruta solo para uso temporal de desarrollo
from fastapi import APIRouter
from app.database import engine, Base

router = APIRouter()

@router.get("/crear-tablas")
def crear_tablas():
    Base.metadata.create_all(bind=engine)
    return {"mensaje": "¡Tablas creadas exitosamente!"}