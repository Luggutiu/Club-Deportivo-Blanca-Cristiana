from pydantic import BaseModel, Field, validator

class HorarioCreate(BaseModel):
    dia: str
    hora_inicio: str
    hora_fin: str
    actividad: str

    @validator("hora_fin")
    def check_horario_valido(cls, v, values):
        if "hora_inicio" in values:
            if v < values["hora_inicio"]:
                raise ValueError("La hora de fin debe ser mayor que la de inicio")
        return v