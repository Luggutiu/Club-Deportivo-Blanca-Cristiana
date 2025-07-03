# ========================================
# Proyecto desarrollado exclusivamente para:
# Club Deportivo Blanca Cristiana
# Desarrollador: Luis Gutierrez
# Sitio: https://club-deportivo-blanca-cristiana.onrender.com
# Email: clubdeportivoblancacristiana@gmail.com
# Año: 2025
# Todos los derechos reservados
# ========================================

from fastapi import Form, File, UploadFile, Request, Depends, APIRouter
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os, shutil

from app.database import get_db
from app.models import Suscriptor
from app.utils.email_utils import notificar_admin_suscripcion, enviar_correo_bienvenida

router = APIRouter()

    
    
