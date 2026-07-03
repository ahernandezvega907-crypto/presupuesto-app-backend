from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from backend.database import get_db
from backend.models.models import Usuario
from backend.auth import crear_token

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UsuarioRegistro(BaseModel):
    nombre: str
    email: str
    password: str

class UsuarioLogin(BaseModel):
    email: str
    password: str

@router.post("/registro")
def registrar(usuario: UsuarioRegistro, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    existe = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    # Encriptar contraseña
    password_hash = pwd_context.hash(usuario.password)

    # Crear usuario
    nuevo = Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        password=password_hash
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"mensaje": "Usuario registrado exitosamente", "id": nuevo.id, "nombre": nuevo.nombre}

@router.post("/login")
def login(datos: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if not usuario or not pwd_context.verify(datos.password, usuario.password):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = crear_token({"usuario_id": usuario.id, "email": usuario.email})

    return {
        "mensaje": "Login exitoso",
        "id": usuario.id,
        "nombre": usuario.nombre,
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/{id}")
def obtener_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"id": usuario.id, "nombre": usuario.nombre, "email": usuario.email}