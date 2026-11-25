from sqlmodel import Session

from app.crud.base import CRUDBase
from app.models.presenca import Presenca


class CRUDPresenca(CRUDBase[Presenca]):
    """A chave primária de Presenca é a própria inscricao_id,
    então `buscar`, `criar` e `excluir` da base já resolvem."""

    def registrar(self, session: Session, inscricao_id: int) -> Presenca:
        return self.criar(session, Presenca(inscricao_id=inscricao_id))


crud_presenca = CRUDPresenca(Presenca, Presenca.data_checkin)
