from typing import Generic, Sequence, TypeVar

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, select

ModelT = TypeVar("ModelT", bound=SQLModel)


class CRUDBase(Generic[ModelT]):
    """CRUD genérico. Não conhece HTTP: em caso de violação de restrição
    faz rollback e propaga IntegrityError para o chamador traduzir."""

    def __init__(self, model: type[ModelT], ordenar_por):
        self.model = model
        self.ordenar_por = ordenar_por

    def buscar(self, session: Session, id: int) -> ModelT | None:
        return session.get(self.model, id)

    def listar(
        self,
        session: Session,
        *,
        filtros: Sequence = (),
        pagina: int = 1,
        tamanho_pagina: int = 10,
    ) -> tuple[list[ModelT], int]:
        total = session.exec(
            select(func.count()).select_from(self.model).where(*filtros)
        ).one()
        itens = session.exec(
            select(self.model)
            .where(*filtros)
            .order_by(self.ordenar_por)
            .offset((pagina - 1) * tamanho_pagina)
            .limit(tamanho_pagina)
        ).all()
        return list(itens), total

    def _commit(self, session: Session) -> None:
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise

    def criar(self, session: Session, obj: ModelT) -> ModelT:
        session.add(obj)
        self._commit(session)
        session.refresh(obj)
        return obj

    def atualizar(self, session: Session, obj: ModelT, valores: dict) -> ModelT:
        obj.sqlmodel_update(valores)
        session.add(obj)
        self._commit(session)
        session.refresh(obj)
        return obj

    def excluir(self, session: Session, obj: ModelT) -> None:
        session.delete(obj)
        self._commit(session)
