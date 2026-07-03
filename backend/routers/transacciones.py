from backend.auth import obtener_usuario_actual
from backend.models.models import Usuario
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from backend.database import get_db
from backend.models.models import Transaccion, Categoria

router = APIRouter(prefix="/transacciones", tags=["Transacciones"])

class TransaccionCrear(BaseModel):
    monto: float
    descripcion: Optional[str] = None
    tipo: str  # "ingreso" o "gasto"
    usuario_id: int
    categoria_id: int

@router.post("/")
def crear_transaccion(
    t: TransaccionCrear, 
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    if usuario_actual.id != t.usuario_id:
        raise HTTPException(status_code=403, detail="No puedes crear transacciones para otro usuario")
    if t.tipo not in ["ingreso", "gasto"]:
        raise HTTPException(status_code=400, detail="Tipo debe ser 'ingreso' o 'gasto'")
    if t.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser positivo")

    nueva = Transaccion(
        monto=t.monto, descripcion=t.descripcion, tipo=t.tipo,
        usuario_id=t.usuario_id, categoria_id=t.categoria_id
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return {"mensaje": "Transacción registrada", "id": nueva.id}

@router.get("/usuario/{usuario_id}")
def listar_transacciones(
    usuario_id: int, 
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    if usuario_actual.id != usuario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver estas transacciones")

    transacciones = db.query(Transaccion).filter(
        Transaccion.usuario_id == usuario_id
    ).order_by(Transaccion.fecha.desc()).all()

    return [{
        "id": t.id, "monto": t.monto, "descripcion": t.descripcion,
        "tipo": t.tipo, "fecha": t.fecha.strftime("%d/%m/%Y %H:%M"),
        "categoria_id": t.categoria_id
    } for t in transacciones]

@router.delete("/{id}")
def eliminar_transaccion(
    id: int, 
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    t = db.query(Transaccion).filter(Transaccion.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    if t.usuario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No puedes eliminar transacciones de otro usuario")
    db.delete(t)
    db.commit()
    return {"mensaje": "Transacción eliminada"}

class TransaccionActualizar(BaseModel):
    monto: Optional[float] = None
    descripcion: Optional[str] = None
    tipo: Optional[str] = None
    categoria_id: Optional[int] = None

@router.put("/{id}")
def actualizar_transaccion(
    id: int,
    cambios: TransaccionActualizar,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    t = db.query(Transaccion).filter(Transaccion.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    if t.usuario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No puedes editar transacciones de otro usuario")

    if cambios.monto is not None:
        if cambios.monto <= 0:
            raise HTTPException(status_code=400, detail="El monto debe ser positivo")
        t.monto = cambios.monto
    if cambios.descripcion is not None:
        t.descripcion = cambios.descripcion
    if cambios.tipo is not None:
        if cambios.tipo not in ["ingreso", "gasto"]:
            raise HTTPException(status_code=400, detail="Tipo debe ser 'ingreso' o 'gasto'")
        t.tipo = cambios.tipo
    if cambios.categoria_id is not None:
        t.categoria_id = cambios.categoria_id

    db.commit()
    db.refresh(t)
    return {
        "mensaje": "Transacción actualizada",
        "id": t.id,
        "monto": t.monto,
        "descripcion": t.descripcion,
        "tipo": t.tipo
    }

from sqlalchemy import func

@router.get("/resumen/{usuario_id}")
def resumen_presupuesto(
    usuario_id: int, 
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    if usuario_actual.id != usuario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este resumen")

    ingresos = db.query(func.sum(Transaccion.monto)).filter(
        Transaccion.usuario_id == usuario_id, Transaccion.tipo == "ingreso"
    ).scalar() or 0
    gastos = db.query(func.sum(Transaccion.monto)).filter(
        Transaccion.usuario_id == usuario_id, Transaccion.tipo == "gasto"
    ).scalar() or 0
    balance = ingresos - gastos
    total = db.query(Transaccion).filter(Transaccion.usuario_id == usuario_id).count()
    return {
        "usuario_id": usuario_id,
        "total_ingresos": round(ingresos, 2),
        "total_gastos": round(gastos, 2),
        "balance": round(balance, 2),
        "total_transacciones": total,
        "estado": "positivo" if balance >= 0 else "negativo"
    }

@router.get("/resumen/{usuario_id}/por-categoria")
def gastos_por_categoria(
    usuario_id: int, 
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    if usuario_actual.id != usuario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta información")

    resultado = db.query(
        Transaccion.categoria_id,
        func.sum(Transaccion.monto).label("total")
    ).filter(
        Transaccion.usuario_id == usuario_id,
        Transaccion.tipo == "gasto"
    ).group_by(Transaccion.categoria_id).all()

    return [{"categoria_id": r.categoria_id, "total": round(r.total, 2)} for r in resultado]