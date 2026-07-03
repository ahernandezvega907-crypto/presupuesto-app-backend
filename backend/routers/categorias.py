from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.models.models import Categoria, Usuario
from backend.auth import obtener_usuario_actual

router = APIRouter(prefix="/categorias", tags=["Categorías"])

class CategoriaCrear(BaseModel):
    nombre: str
    tipo: str
    icono: str = "💰"
    usuario_id: int

@router.post("/")
def crear_categoria(
    c: CategoriaCrear, 
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    if usuario_actual.id != c.usuario_id:
        raise HTTPException(status_code=403, detail="No puedes crear categorías para otro usuario")
    nueva = Categoria(**c.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return {"mensaje": "Categoría creada", "id": nueva.id}

@router.get("/usuario/{usuario_id}")
def listar_categorias(
    usuario_id: int, 
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    if usuario_actual.id != usuario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver estas categorías")
    categorias = db.query(Categoria).filter(Categoria.usuario_id == usuario_id).all()
    return [{"id": c.id, "nombre": c.nombre, "tipo": c.tipo, "icono": c.icono} for c in categorias]