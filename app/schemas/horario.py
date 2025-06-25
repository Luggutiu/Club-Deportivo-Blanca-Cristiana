from pydantic import BaseModel

class HorarioCreate(BaseModel):
    dia: str
    hora_inicio: str
    hora_fin: str
    actividad: str