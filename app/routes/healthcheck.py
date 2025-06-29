from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.head("/ping")
@router.get("/ping", response_class=PlainTextResponse)
async def ping():
    return "pong"