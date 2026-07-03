from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id       = Column(Integer, primary_key=True, index=True)
    nombre   = Column(String, nullable=False)
    email    = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    creado   = Column(DateTime, default=datetime.now)

    transacciones = relationship("Transaccion", back_populates="usuario")
    categorias    = relationship("Categoria", back_populates="usuario")

class Categoria(Base):
    __tablename__ = "categorias"

    id       = Column(Integer, primary_key=True, index=True)
    nombre   = Column(String, nullable=False)
    tipo     = Column(String, nullable=False)  # "ingreso" o "gasto"
    icono    = Column(String, default="💰")
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))

    usuario      = relationship("Usuario", back_populates="categorias")
    transacciones = relationship("Transaccion", back_populates="categoria")

class Transaccion(Base):
    __tablename__ = "transacciones"

    id           = Column(Integer, primary_key=True, index=True)
    monto        = Column(Float, nullable=False)
    descripcion  = Column(String)
    fecha        = Column(DateTime, default=datetime.now)
    tipo         = Column(String, nullable=False)  # "ingreso" o "gasto"
    usuario_id   = Column(Integer, ForeignKey("usuarios.id"))
    categoria_id = Column(Integer, ForeignKey("categorias.id"))

    usuario   = relationship("Usuario", back_populates="transacciones")
    categoria = relationship("Categoria", back_populates="transacciones")

class PresupuestoMensual(Base):
    __tablename__ = "presupuestos_mensuales"

    id           = Column(Integer, primary_key=True, index=True)
    limite       = Column(Float, nullable=False)
    mes          = Column(Integer, nullable=False)
    año          = Column(Integer, nullable=False)
    usuario_id   = Column(Integer, ForeignKey("usuarios.id"))
    categoria_id = Column(Integer, ForeignKey("categorias.id"))

    usuario   = relationship("Usuario")
    categoria = relationship("Categoria")