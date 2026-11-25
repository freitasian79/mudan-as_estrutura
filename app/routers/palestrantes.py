from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.crud.palestrante import crud_palestrante
from app.database import getSession
from app.models.palestrante import Palestrante
from app.schemas.paginacao import PaginaPalestrantes
from app.schemas.palestrante import (
    PalestranteCreate,
    PalestrantePublic,
    PalestranteUpdate,
)
from app.utils import conflito_409, metadados, ou_404

router = APIRouter(prefix="/palestrantes", tags=["Palestrantes"])
NAO_ENCONTRADO = "Palestrante não encontrado"
DUPLICADO = "Palestrante com este email já existe"


@router.post("/", response_model=PalestrantePublic, status_code=201)
def criar_palestrante(
    dados: PalestranteCreate, session: Session = Depends(getSession)
):
    with conflito_409(DUPLICADO):
        return crud_palestrante.criar(
            session, Palestrante.model_validate(dados)
        )


@router.get("/", response_model=PaginaPalestrantes)
def listar_palestrantes(
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(10, ge=1, le=100),
    nome: str | None = Query(default=None),
    session: Session = Depends(getSession),
):
    filtros = [Palestrante.nome.ilike(f"%{nome}%")] if nome else []
    itens, total = crud_palestrante.listar(
        session, filtros=filtros, pagina=pagina, tamanho_pagina=tamanho_pagina
    )
    return PaginaPalestrantes(
        dados=itens, paginacao=metadados(total, pagina, tamanho_pagina)
    )


@router.get("/{palestrante_id}", response_model=PalestrantePublic)
def buscar_palestrante(
    palestrante_id: int, session: Session = Depends(getSession)
):
    return ou_404(
        crud_palestrante.buscar(session, palestrante_id), NAO_ENCONTRADO
    )


@router.patch("/{palestrante_id}", response_model=PalestrantePublic)
def atualizar_palestrante(
    palestrante_id: int,
    dados: PalestranteUpdate,
    session: Session = Depends(getSession),
):
    palestrante = ou_404(
        crud_palestrante.buscar(session, palestrante_id), NAO_ENCONTRADO
    )
    with conflito_409(DUPLICADO):
        return crud_palestrante.atualizar(
            session, palestrante, dados.model_dump(exclude_unset=True)
        )


@router.delete("/{palestrante_id}", status_code=204)
def excluir_palestrante(
    palestrante_id: int, session: Session = Depends(getSession)
):
    palestrante = ou_404(
        crud_palestrante.buscar(session, palestrante_id), NAO_ENCONTRADO
    )
    with conflito_409(
        "Palestrante possui atividades associadas e não pode ser removido"
    ):
        crud_palestrante.excluir(session, palestrante)
