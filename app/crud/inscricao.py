from sqlalchemy import func
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.inscricao import Inscricao, StatusInscricao


class CRUDInscricao(CRUDBase[Inscricao]):
    def cancelar(self, session: Session, inscricao: Inscricao) -> Inscricao:
        """Soft delete: mantém o histórico e libera a vaga."""
        return self.atualizar(
            session, inscricao, {"status": StatusInscricao.CANCELADA}
        )

    def contar_confirmadas(
        self,
        session: Session,
        atividade_id: int,
        ignorar_inscricao_id: int | None = None,
    ) -> int:
        consulta = select(func.count()).select_from(Inscricao).where(
            Inscricao.atividade_id == atividade_id,
            Inscricao.status == StatusInscricao.CONFIRMADA,
        )
        if ignorar_inscricao_id is not None:
            consulta = consulta.where(Inscricao.id != ignorar_inscricao_id)
        return session.exec(consulta).one()


crud_inscricao = CRUDInscricao(Inscricao, Inscricao.data_criacao.desc())
