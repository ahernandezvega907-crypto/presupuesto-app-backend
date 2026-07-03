from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routers import usuarios, transacciones, categorias, presupuestos

# Crear todas las tablas en la base de datos
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

app.include_router(usuarios.router)
app.include_router(transacciones.router)
app.include_router(categorias.router)
app.include_router(presupuestos.router)

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