from app.database import engine, SessionLocal
from app import models

print("Creando tablas...")
models.Base.metadata.create_all(bind=engine)
print("¡Tablas creadas correctamente!")

print("Agregando post de prueba...")
db = SessionLocal()

nuevo_post = models.Post(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    embed_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
    plataforma="YouTube"
)

db.add(nuevo_post)
db.commit()
db.close()
print("¡Post agregado exitosamente!")