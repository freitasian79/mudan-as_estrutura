from fastapi import HTTPException
from sqlmodel import Session, select

from app.crud.inscricao import crud_inscricao
from app.models.atividade import Atividade
from app.models.inscricao import Inscricao, StatusInscricao


def validar_inscricao(
    session: Session,
    participante_id: int,
    atividade_id: int,
    ignorar_inscricao_id: int | None = None,
) -> None:
    """Regras para criar/confirmar uma inscrição.

    404 atividade inexistente | 400 atividade cancelada
    409 duplicada, sem vagas ou conflito de horário.
    `ignorar_inscricao_id` evita que a própria inscrição conte contra si
    mesma ao ser confirmada via PATCH.
    """
    atividade = session.get(Atividade, atividade_id)
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    if atividade.cancelada:
        raise HTTPException(status_code=400, detail="Atividade cancelada")

    ativas = session.exec(
        select(Inscricao).where(
            Inscricao.participante_id == participante_id,
            Inscricao.status != StatusInscricao.CANCELADA,
        )
    ).all()
    ativas = [i for i in ativas if i.id != ignorar_inscricao_id]

    if any(i.atividade_id == atividade_id for i in ativas):
        raise HTTPException(
            status_code=409, detail="Inscrição duplicada para esta atividade"
        )

    confirmadas = crud_inscricao.contar_confirmadas(
        session, atividade_id, ignorar_inscricao_id
    )
    if confirmadas >= atividade.capacidade_maxima:
        raise HTTPException(status_code=409, detail="Atividade sem vagas")

    for i in ativas:
        outra = i.atividade
        if (
            atividade.data_hora_inicio < outra.data_hora_fim
            and outra.data_hora_inicio < atividade.data_hora_fim
        ):
            raise HTTPException(
                status_code=409,
                detail=f"Conflito de horário com a atividade '{outra.titulo}'",
            )
