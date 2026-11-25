from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.crud.evento import crud_evento
from app.database import getSession
from app.models.evento import Evento
from app.schemas.evento import EventoCreate, EventoPublic, EventoUpdate
from app.schemas.paginacao import PaginaEventos
from app.utils import conflito_409, metadados, ou_404

router = APIRouter(prefix="/eventos", tags=["Eventos"])
NAO_ENCONTRADO = "Evento não encontrado"
DUPLICADO = "Evento com este nome já existe"


@router.post("/", response_model=EventoPublic, status_code=201)
def criar_evento(dados: EventoCreate, session: Session = Depends(getSession)):
    with conflito_409(DUPLICADO):
        return crud_evento.criar(session, Evento.model_validate(dados))


@router.get("/", response_model=PaginaEventos)
def listar_eventos(
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(10, ge=1, le=100),
    nome: str | None = Query(default=None),
    ativo: bool | None = Query(default=None),
    session: Session = Depends(getSession),
):
    filtros = []
    if nome:
        filtros.append(Evento.nome.ilike(f"%{nome}%"))
    if ativo is not None:
        filtros.append(Evento.ativo == ativo)
    itens, total = crud_evento.listar(
        session, filtros=filtros, pagina=pagina, tamanho_pagina=tamanho_pagina
    )
    return PaginaEventos(
        dados=itens, paginacao=metadados(total, pagina, tamanho_pagina)
    )


@router.get("/{evento_id}", response_model=EventoPublic)
def buscar_evento(evento_id: int, session: Session = Depends(getSession)):
    return ou_404(crud_evento.buscar(session, evento_id), NAO_ENCONTRADO)


@router.patch("/{evento_id}", response_model=EventoPublic)
def atualizar_evento(
    evento_id: int,
    dados: EventoUpdate,
    session: Session = Depends(getSession),
):
    evento = ou_404(crud_evento.buscar(session, evento_id), NAO_ENCONTRADO)
    with conflito_409(DUPLICADO):
        return crud_evento.atualizar(
            session, evento, dados.model_dump(exclude_unset=True)
        )


@router.delete("/{evento_id}", status_code=204)
def excluir_evento(evento_id: int, session: Session = Depends(getSession)):
    evento = ou_404(crud_evento.buscar(session, evento_id), NAO_ENCONTRADO)
    with conflito_409(
        "Evento possui atividades associadas e não pode ser removido"
    ):
        crud_evento.excluir(session, evento)
