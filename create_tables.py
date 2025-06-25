# create_tables.py
from app.database import engine, Base
from app import models  # Importante: esto registra los modelos para que se creen las tablas

print("Creando tablas en la base de datos...")
Base.metadata.create_all(bind=engine)
print("¡Tablas creadas exitosamente!")