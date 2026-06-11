from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, presets, projects
from app.core.config import get_settings
from app.db.models import Base
from app.db.session import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
allowed_origins = sorted(
    {settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"}
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    same_site="lax",
    https_only=settings.session_cookie_secure,
)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(presets.router, prefix=settings.api_prefix)
app.include_router(projects.router, prefix=settings.api_prefix)
app.mount("/", StaticFiles(directory="./public", html=True), name="public")


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """API は JSON、それ以外は SPA の index.html を返す。"""
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

    try:
        with open("./public/index.html") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="ファイルが見つかりません", status_code=404)
