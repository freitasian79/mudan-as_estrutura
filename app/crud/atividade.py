from sqlmodel import Session

from app.crud.base import CRUDBase
from app.models.atividade import Atividade
from app.models.palestrante import Palestrante


class CRUDAtividade(CRUDBase[Atividade]):
    def criar_com_palestrantes(
        self,
        session: Session,
        valores: dict,
        palestrantes: list[Palestrante],
    ) -> Atividade:
        atividade = Atividade(**valores, palestrantes=palestrantes)
        return self.criar(session, atividade)

    def atualizar_com_palestrantes(
        self,
        session: Session,
        atividade: Atividade,
        valores: dict,
        palestrantes: list[Palestrante] | None = None,
    ) -> Atividade:
        # O relationship gerencia a tabela associativa; basta atribuir.
        if palestrantes is not None:
            atividade.palestrantes = palestrantes
        return self.atualizar(session, atividade, valores)


crud_atividade = CRUDAtividade(Atividade, Atividade.data_hora_inicio)
