from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.crud.consultas import programacao_participante
from app.crud.participante import crud_participante
from app.database import getSession
from app.models.participante import Participante
from app.schemas.atividade import AtividadePublic
from app.schemas.paginacao import PaginaParticipantes
from app.schemas.participante import (
    ParticipanteCreate,
    ParticipantePublic,
    ParticipanteUpdate,
)
from app.utils import conflito_409, metadados, ou_404

router = APIRouter(prefix="/participantes", tags=["Participantes"])
NAO_ENCONTRADO = "Participante não encontrado"
DUPLICADO = "Email ou CPF já cadastrado"


@router.post("/", response_model=ParticipantePublic, status_code=201)
def criar_participante(
    dados: ParticipanteCreate, session: Session = Depends(getSession)
):
    with conflito_409(DUPLICADO):
        return crud_participante.criar(
            session, Participante.model_validate(dados)
        )


@router.get("/", response_model=PaginaParticipantes)
def listar_participantes(
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(10, ge=1, le=100),
    nome: str | None = Query(default=None),
    session: Session = Depends(getSession),
):
    filtros = [Participante.nome.ilike(f"%{nome}%")] if nome else []
    itens, total = crud_participante.listar(
        session, filtros=filtros, pagina=pagina, tamanho_pagina=tamanho_pagina
    )
    return PaginaParticipantes(
        dados=itens, paginacao=metadados(total, pagina, tamanho_pagina)
    )


@router.get("/{participante_id}", response_model=ParticipantePublic)
def buscar_participante(
    participante_id: int, session: Session = Depends(getSession)
):
    return ou_404(
        crud_participante.buscar(session, participante_id), NAO_ENCONTRADO
    )


@router.get(
    "/{participante_id}/programacao", response_model=list[AtividadePublic]
)
def ver_programacao(
    participante_id: int, session: Session = Depends(getSession)
):
    """F17: visualização da programação do participante."""
    ou_404(crud_participante.buscar(session, participante_id), NAO_ENCONTRADO)
    return programacao_participante(session, participante_id)


@router.patch("/{participante_id}", response_model=ParticipantePublic)
def atualizar_participante(
    participante_id: int,
    dados: ParticipanteUpdate,
    session: Session = Depends(getSession),
):
    participante = ou_404(
        crud_participante.buscar(session, participante_id), NAO_ENCONTRADO
    )
    with conflito_409(DUPLICADO):
        return crud_participante.atualizar(
            session, participante, dados.model_dump(exclude_unset=True)
        )


@router.delete("/{participante_id}", status_code=204)
def excluir_participante(
    participante_id: int, session: Session = Depends(getSession)
):
    participante = ou_404(
        crud_participante.buscar(session, participante_id), NAO_ENCONTRADO
    )
    with conflito_409(
        "Participante possui inscrições associadas e não pode ser removido"
    ):
        crud_participante.excluir(session, participante)
