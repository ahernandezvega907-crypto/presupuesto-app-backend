from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import datetime
from backend.database import get_db
from backend.models.models import PresupuestoMensual, Transaccion, Usuario
from backend.auth import obtener_usuario_actual

router = APIRouter(prefix="/presupuestos", tags=["Presupuestos Mensuales"])

class PresupuestoCrear(BaseModel):
    limite: float
    mes: int
    year: int
    usuario_id: int
    categoria_id: int

@router.post("/")
def crear_presupuesto(
    p: PresupuestoCrear,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    if usuario_actual.id != p.usuario_id:
        raise HTTPException(status_code=403, detail="No puedes crear presupuestos para otro usuario")
    if p.mes < 1 or p.mes > 12:
        raise HTTPException(status_code=400, detail="El mes debe estar entre 1 y 12")

    nuevo = PresupuestoMensual(
        limite=p.limite, mes=p.mes, año=p.year,
        usuario_id=p.usuario_id, categoria_id=p.categoria_id
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"mensaje": "Presupuesto creado", "id": nuevo.id}

@router.get("/usuario/{usuario_id}/estado")
def estado_presupuestos(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Compara cada presupuesto con lo gastado realmente en esa categoría/mes."""
    if usuario_actual.id != usuario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta información")

    presupuestos = db.query(PresupuestoMensual).filter(
        PresupuestoMensual.usuario_id == usuario_id
    ).all()

    resultado = []
    for p in presupuestos:
        gastado = db.query(func.sum(Transaccion.monto)).filter(
            Transaccion.usuario_id == usuario_id,
            Transaccion.categoria_id == p.categoria_id,
            Transaccion.tipo == "gasto",
            func.strftime("%m", Transaccion.fecha) == f"{p.mes:02d}",
            func.strftime("%Y", Transaccion.fecha) == str(p.año)
        ).scalar() or 0

        porcentaje = (gastado / p.limite * 100) if p.limite > 0 else 0
        resultado.append({
            "categoria_id": p.categoria_id,
            "mes": p.mes,
            "año": p.año,
            "limite": p.limite,
            "gastado": round(gastado, 2),
            "disponible": round(p.limite - gastado, 2),
            "porcentaje_usado": round(porcentaje, 1),
            "alerta": "⚠️ Límite superado" if gastado > p.limite else "✓ Dentro del presupuesto"
        })

    return resultado