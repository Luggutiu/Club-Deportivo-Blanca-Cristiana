from sqlalchemy import create_engine
from app.database import Base  # Asegúrate que este importa bien tu Base
from app.models import Post    # Importa el modelo Post

# Usa la misma URL de conexión que usas en tu entorno local
DATABASE_URL = "postgresql://usuario:contraseña@localhost:5432/tu_base_de_datos"

engine = create_engine(DATABASE_URL)

# 🔥 Borrar la tabla (cuidado: se borra TODO su contenido)
Base.metadata.drop_all(bind=engine, tables=[Post.__table__])

# ✅ Volver a crearla con las columnas correctas
Base.metadata.create_all(bind=engine, tables=[Post.__table__])

print("La tabla 'posts' fue borrada y recreada exitosamente.")