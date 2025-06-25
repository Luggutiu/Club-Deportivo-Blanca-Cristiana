from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_posts():
    return {"message": "Listado de publicaciones"}
