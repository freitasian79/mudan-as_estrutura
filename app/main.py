from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

import app.models  # noqa: F401  (registra as tabelas)
from app.database import engine

from app.routers import (
    atividades,
    estatisticas,
    eventos,
    inscricoes,
    locais,
    palestrantes,
    participantes,
    presencas,
)

@asynccontextmanager
async def lifespan(_):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Sistema de Gestão de Eventos",
    version="1.0.0",
    description="Trabalho Prático 2 — QXD0099",
)

app.include_router(eventos.router)
app.include_router(locais.router)
app.include_router(palestrantes.router)
app.include_router(atividades.router)
app.include_router(participantes.router)
app.include_router(inscricoes.router)
app.include_router(presencas.router)
app.include_router(estatisticas.router)
