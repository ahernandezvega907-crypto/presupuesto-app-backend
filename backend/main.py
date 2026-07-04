from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.database import engine, Base
from backend.routers import usuarios, transacciones, categorias, presupuestos
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Presupuesto Personal API",
    description="API para manejo de presupuesto personal",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(usuarios.router)
app.include_router(transacciones.router)
app.include_router(categorias.router)
app.include_router(presupuestos.router)

@app.get("/favicon.ico")
def favicon():
    return FileResponse(os.path.join(STATIC_DIR, "favicon.ico"))

@app.get("/")
def inicio():
    return {
        "app": "Presupuesto Personal",
        "version": "1.0.0",
        "estado": "activo"
    }

@app.get("/health")
def health():
    return {"estado": "OK"}