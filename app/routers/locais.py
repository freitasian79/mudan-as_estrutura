from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.crud.local import crud_local
from app.database import getSession
from app.models.local import Local
from app.schemas.local import LocalCreate, LocalPublic, LocalUpdate
from app.schemas.paginacao import PaginaLocais
from app.utils import conflito_409, metadados, ou_404

router = APIRouter(prefix="/locais", tags=["Locais"])
NAO_ENCONTRADO = "Local não encontrado"
DUPLICADO = "Local com este nome já existe"


@router.post("/", response_model=LocalPublic, status_code=201)
def criar_local(dados: LocalCreate, session: Session = Depends(getSession)):
    with conflito_409(DUPLICADO):
        return crud_local.criar(session, Local.model_validate(dados))


@router.get("/", response_model=PaginaLocais)
def listar_locais(
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(10, ge=1, le=100),
    nome: str | None = Query(default=None),
    session: Session = Depends(getSession),
):
    filtros = [Local.nome.ilike(f"%{nome}%")] if nome else []
    itens, total = crud_local.listar(
        session, filtros=filtros, pagina=pagina, tamanho_pagina=tamanho_pagina
    )
    return PaginaLocais(
        dados=itens, paginacao=metadados(total, pagina, tamanho_pagina)
    )


@router.get("/{local_id}", response_model=LocalPublic)
def buscar_local(local_id: int, session: Session = Depends(getSession)):
    return ou_404(crud_local.buscar(session, local_id), NAO_ENCONTRADO)


@router.patch("/{local_id}", response_model=LocalPublic)
def atualizar_local(
    local_id: int,
    dados: LocalUpdate,
    session: Session = Depends(getSession),
):
    local = ou_404(crud_local.buscar(session, local_id), NAO_ENCONTRADO)
    with conflito_409(DUPLICADO):
        return crud_local.atualizar(
            session, local, dados.model_dump(exclude_unset=True)
        )


@router.delete("/{local_id}", status_code=204)
def excluir_local(local_id: int, session: Session = Depends(getSession)):
    local = ou_404(crud_local.buscar(session, local_id), NAO_ENCONTRADO)
    with conflito_409(
        "Local possui atividades associadas e não pode ser removido"
    ):
        crud_local.excluir(session, local)
