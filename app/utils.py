from contextlib import contextmanager

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.models.paginacao import MetadadosPaginacao


def metadados(total: int, pagina: int, tamanho: int) -> MetadadosPaginacao:
    return MetadadosPaginacao(
        total_registros=total,
        total_paginas=(total + tamanho - 1) // tamanho,
        pagina_atual=pagina,
        tamanho_pagina=tamanho,
    )


def ou_404(obj, mensagem: str):
    if obj is None:
        raise HTTPException(status_code=404, detail=mensagem)
    return obj


@contextmanager
def conflito_409(mensagem: str):
    """Traduz IntegrityError (já com rollback feito no CRUD) em HTTP 409."""
    try:
        yield
    except IntegrityError:
        raise HTTPException(status_code=409, detail=mensagem)
