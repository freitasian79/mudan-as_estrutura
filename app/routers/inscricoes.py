from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.crud.atividade import crud_atividade
from app.crud.consultas import inscritos_por_atividade
from app.crud.inscricao import crud_inscricao
from app.crud.participante import crud_participante
from app.database import getSession
from app.models.inscricao import Inscricao, StatusInscricao
from app.schemas.inscricao import (
    InscricaoCreate,
    InscricaoPublic,
    InscricaoPublicDetalhada,
    InscricaoUpdate,
)
from app.schemas.paginacao import PaginaInscricoes
from app.schemas.participante import ParticipantePublic
from app.services.inscricao_service import validar_inscricao
from app.utils import conflito_409, metadados, ou_404

router = APIRouter(prefix="/inscricoes", tags=["Inscrições"])
NAO_ENCONTRADA = "Inscrição não encontrada"


@router.post("/", response_model=InscricaoPublic, status_code=201)
def criar_inscricao(
    dados: InscricaoCreate, session: Session = Depends(getSession)
):
    ou_404(
        crud_participante.buscar(session, dados.participante_id),
        "Participante não encontrado",
    )
    validar_inscricao(session, dados.participante_id, dados.atividade_id)
    with conflito_409("Erro ao criar inscrição"):
        return crud_inscricao.criar(session, Inscricao.model_validate(dados))


@router.get("/", response_model=PaginaInscricoes)
def listar_inscricoes(
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(10, ge=1, le=100),
    status: StatusInscricao | None = Query(default=None),
    atividade_id: int | None = Query(default=None),
    session: Session = Depends(getSession),
):
    filtros = []
    if status is not None:
        filtros.append(Inscricao.status == status)
    if atividade_id is not None:
        filtros.append(Inscricao.atividade_id == atividade_id)
    itens, total = crud_inscricao.listar(
        session, filtros=filtros, pagina=pagina, tamanho_pagina=tamanho_pagina
    )
    return PaginaInscricoes(
        dados=itens, paginacao=metadados(total, pagina, tamanho_pagina)
    )


# Rota fixa antes de "/{inscricao_id}" para não haver ambiguidade.
@router.get(
    "/atividade/{atividade_id}/inscritos",
    response_model=list[ParticipantePublic],
)
def listar_inscritos_atividade(
    atividade_id: int, session: Session = Depends(getSession)
):
    """F10b: inscritos por atividade."""
    ou_404(
        crud_atividade.buscar(session, atividade_id), "Atividade não encontrada"
    )
    return inscritos_por_atividade(session, atividade_id)


@router.get("/{inscricao_id}", response_model=InscricaoPublicDetalhada)
def buscar_inscricao(
    inscricao_id: int, session: Session = Depends(getSession)
):
    return ou_404(crud_inscricao.buscar(session, inscricao_id), NAO_ENCONTRADA)


@router.patch("/{inscricao_id}", response_model=InscricaoPublic)
def atualizar_inscricao(
    inscricao_id: int,
    dados: InscricaoUpdate,
    session: Session = Depends(getSession),
):
    inscricao = ou_404(
        crud_inscricao.buscar(session, inscricao_id), NAO_ENCONTRADA
    )
    valores = dados.model_dump(exclude_unset=True)

    if valores.get("status") == StatusInscricao.CONFIRMADA:
        validar_inscricao(
            session,
            valores.get("participante_id", inscricao.participante_id),
            valores.get("atividade_id", inscricao.atividade_id),
            ignorar_inscricao_id=inscricao.id,
        )
    with conflito_409("Erro ao atualizar inscrição"):
        return crud_inscricao.atualizar(session, inscricao, valores)


@router.delete("/{inscricao_id}", status_code=204)
def cancelar_inscricao(
    inscricao_id: int, session: Session = Depends(getSession)
):
    inscricao = ou_404(
        crud_inscricao.buscar(session, inscricao_id), NAO_ENCONTRADA
    )
    crud_inscricao.cancelar(session, inscricao)
