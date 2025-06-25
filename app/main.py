from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_302_FOUND

from app.routes import posts, auth, admin, dev

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def root():
    return RedirectResponse(url="/posts", status_code=HTTP_302_FOUND)

app.include_router(posts.router, prefix="/posts")
app.include_router(auth.router, prefix="/admin")
app.include_router(admin.router)
app.include_router(dev.router)