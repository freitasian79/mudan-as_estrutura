from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.crud.atividade import crud_atividade
from app.crud.evento import crud_evento
from app.crud.local import crud_local
from app.crud.palestrante import crud_palestrante
from app.database import getSession
from app.models.atividade import Atividade
from app.schemas.atividade import (
    AtividadeCreate,
    AtividadePublicDetalhada,
    AtividadeUpdate,
)
from app.schemas.paginacao import PaginaAtividades
from app.utils import conflito_409, metadados, ou_404

router = APIRouter(prefix="/atividades", tags=["Atividades"])
NAO_ENCONTRADA = "Atividade não encontrada"
DUPLICADA = "Já existe atividade com este título neste evento"


def obter_palestrantes(ids: list[int], session: Session):
    return [
        ou_404(
            crud_palestrante.buscar(session, pid),
            f"Palestrante {pid} não encontrado",
        )
        for pid in dict.fromkeys(ids)  # remove duplicados mantendo a ordem
    ]


def validar_referencias(
    session: Session, evento_id: int | None, local_id: int | None
):
    if evento_id is not None:
        ou_404(crud_evento.buscar(session, evento_id), "Evento não encontrado")
    if local_id is not None:
        ou_404(crud_local.buscar(session, local_id), "Local não encontrado")


@router.post("/", response_model=AtividadePublicDetalhada, status_code=201)
def criar_atividade(
    dados: AtividadeCreate, session: Session = Depends(getSession)
):
    validar_referencias(session, dados.evento_id, dados.local_id)
    palestrantes = obter_palestrantes(dados.palestrante_ids, session)
    with conflito_409(DUPLICADA):
        return crud_atividade.criar_com_palestrantes(
            session,
            dados.model_dump(exclude={"palestrante_ids"}),
            palestrantes,
        )


@router.get("/", response_model=PaginaAtividades)
def listar_atividades(
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(10, ge=1, le=100),
    titulo: str | None = Query(default=None),
    evento_id: int | None = Query(default=None),
    cancelada: bool | None = Query(default=None),
    session: Session = Depends(getSession),
):
    filtros = []
    if titulo:
        filtros.append(Atividade.titulo.ilike(f"%{titulo}%"))
    if evento_id is not None:
        filtros.append(Atividade.evento_id == evento_id)
    if cancelada is not None:
        filtros.append(Atividade.cancelada == cancelada)
    itens, total = crud_atividade.listar(
        session, filtros=filtros, pagina=pagina, tamanho_pagina=tamanho_pagina
    )
    return PaginaAtividades(
        dados=itens, paginacao=metadados(total, pagina, tamanho_pagina)
    )


@router.get("/{atividade_id}", response_model=AtividadePublicDetalhada)
def buscar_atividade(
    atividade_id: int, session: Session = Depends(getSession)
):
    return ou_404(crud_atividade.buscar(session, atividade_id), NAO_ENCONTRADA)


@router.patch("/{atividade_id}", response_model=AtividadePublicDetalhada)
def atualizar_atividade(
    atividade_id: int,
    dados: AtividadeUpdate,
    session: Session = Depends(getSession),
):
    atividade = ou_404(
        crud_atividade.buscar(session, atividade_id), NAO_ENCONTRADA
    )
    valores = dados.model_dump(exclude_unset=True)
    palestrante_ids = valores.pop("palestrante_ids", None)

    validar_referencias(
        session, valores.get("evento_id"), valores.get("local_id")
    )
    palestrantes = (
        obter_palestrantes(palestrante_ids, session)
        if palestrante_ids is not None
        else None
    )
    with conflito_409(DUPLICADA):
        return crud_atividade.atualizar_com_palestrantes(
            session, atividade, valores, palestrantes
        )


@router.delete("/{atividade_id}", status_code=204)
def excluir_atividade(
    atividade_id: int, session: Session = Depends(getSession)
):
    atividade = ou_404(
        crud_atividade.buscar(session, atividade_id), NAO_ENCONTRADA
    )
    with conflito_409(
        "Atividade possui inscrições associadas e não pode ser removida"
    ):
        crud_atividade.excluir(session, atividade)
