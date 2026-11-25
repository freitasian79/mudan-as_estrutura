from sqlalchemy import Float, case, cast, func
from sqlmodel import Session, select

from app.models.atividade import Atividade
from app.models.inscricao import Inscricao, StatusInscricao
from app.models.participante import Participante


def programacao_participante(session: Session, participante_id: int):

    return session.exec(
        select(Atividade)
        .join(Inscricao, Inscricao.atividade_id == Atividade.id)
        .where(
            Inscricao.participante_id == participante_id,
            Inscricao.status != StatusInscricao.CANCELADA,
        )
        .order_by(Atividade.data_hora_inicio)
    ).all()


def inscritos_por_atividade(session: Session, atividade_id: int):

    return session.exec(
        select(Participante)
        .join(Inscricao, Inscricao.participante_id == Participante.id)
        .where(
            Inscricao.atividade_id == atividade_id,
            Inscricao.status != StatusInscricao.CANCELADA,
        )
    ).all()


def atividades_com_vagas(session: Session, evento_id: int | None = None):

    consulta = (
        select(
            Atividade,
            func.count(Inscricao.id).label("inscritos"),
        )
        .outerjoin(
            Inscricao,
            (Inscricao.atividade_id == Atividade.id)
            & (Inscricao.status == StatusInscricao.CONFIRMADA),
        )
        .group_by(Atividade.id)
        .having(func.count(Inscricao.id) < Atividade.capacidade_maxima)
    )
    if evento_id is not None:
        consulta = consulta.where(Atividade.evento_id == evento_id)
    return session.exec(consulta).all()


def taxa_ocupacao_por_atividade(session: Session, evento_id: int | None = None):

    consulta = (
        select(
            Atividade.id,
            Atividade.titulo,
            Atividade.capacidade_maxima,
            func.count(Inscricao.id).label("confirmadas"),
            (
                cast(func.count(Inscricao.id), Float)
                / Atividade.capacidade_maxima
            ).label("taxa"),
        )
        .outerjoin(
            Inscricao,
            (Inscricao.atividade_id == Atividade.id)
            & (Inscricao.status == StatusInscricao.CONFIRMADA),
        )
        .group_by(Atividade.id)
        .order_by(
            (
                cast(func.count(Inscricao.id), Float)
                / Atividade.capacidade_maxima
            ).desc()
        )
    )
    if evento_id is not None:
        consulta = consulta.where(Atividade.evento_id == evento_id)
    return session.exec(consulta).all()


def conflitos_horario_participante(session: Session, participante_id: int):

    i1 = Inscricao.__table__.alias("i1")
    i2 = Inscricao.__table__.alias("i2")
    a1 = Atividade.__table__.alias("a1")
    a2 = Atividade.__table__.alias("a2")

    stmt = (
        select(
            a1.c.id.label("atividade_1_id"),
            a1.c.titulo.label("atividade_1_titulo"),
            a1.c.data_hora_inicio.label("inicio_1"),
            a1.c.data_hora_fim.label("fim_1"),
            a2.c.id.label("atividade_2_id"),
            a2.c.titulo.label("atividade_2_titulo"),
            a2.c.data_hora_inicio.label("inicio_2"),
            a2.c.data_hora_fim.label("fim_2"),
        )
        .select_from(i1)
        .join(i2, i1.c.participante_id == i2.c.participante_id)
        .join(a1, i1.c.atividade_id == a1.c.id)
        .join(a2, i2.c.atividade_id == a2.c.id)
        .where(
            i1.c.participante_id == participante_id,
            i1.c.status != StatusInscricao.CANCELADA,
            i2.c.status != StatusInscricao.CANCELADA,
            i1.c.id < i2.c.id,
            a1.c.data_hora_inicio < a2.c.data_hora_fim,
            a2.c.data_hora_inicio < a1.c.data_hora_fim,
        )
    )
    return session.exec(stmt).all()


def estatisticas_evento(session: Session, evento_id: int):

    return session.exec(
        select(
            func.count(Inscricao.id).label("total_inscricoes"),
            func.coalesce(
                func.sum(
                    case((Inscricao.status == StatusInscricao.CONFIRMADA, 1), else_=0)
                ),
                0,
            ).label("confirmadas"),
            func.coalesce(
                func.sum(
                    case((Inscricao.status == StatusInscricao.CANCELADA, 1), else_=0)
                ),
                0,
            ).label("canceladas"),
            func.min(Inscricao.data_criacao).label("primeira_inscricao"),
            func.max(Inscricao.data_criacao).label("ultima_inscricao"),
        )
        .join(Atividade, Inscricao.atividade_id == Atividade.id)
        .where(Atividade.evento_id == evento_id)
    ).one()


def ocupacao_media_por_evento(session: Session):

    subq = (
        select(
            Atividade.evento_id,
            Atividade.id.label("atividade_id"),
            Atividade.capacidade_maxima,
            func.count(Inscricao.id).label("confirmadas"),
        )
        .outerjoin(
            Inscricao,
            (Inscricao.atividade_id == Atividade.id)
            & (Inscricao.status == StatusInscricao.CONFIRMADA),
        )
        .group_by(Atividade.evento_id, Atividade.id)
    ).subquery()

    return session.exec(
        select(
            subq.c.evento_id,
            func.avg(
                cast(subq.c.confirmadas, Float) / subq.c.capacidade_maxima
            ).label("ocupacao_media"),
        )
        .group_by(subq.c.evento_id)
    ).all()