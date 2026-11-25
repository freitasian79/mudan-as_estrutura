from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.crud.consultas import (
    atividades_com_vagas,
    conflitos_horario_participante,
    estatisticas_evento,
    ocupacao_media_por_evento,
    taxa_ocupacao_por_atividade,
)
from app.database import getSession
from app.models.evento import Evento

router = APIRouter(prefix="/estatisticas", tags=["Estatísticas"])


@router.get("/evento/{evento_id}")
def stats_evento(evento_id: int, session: Session = Depends(getSession)):
    """F12: estatísticas gerais de um evento."""
    if not session.get(Evento, evento_id):
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    resultado = estatisticas_evento(session, evento_id)
    return {
        "evento_id": evento_id,
        "total_inscricoes": resultado.total_inscricoes,
        "confirmadas": resultado.confirmadas,
        "canceladas": resultado.canceladas,
        "primeira_inscricao": resultado.primeira_inscricao,
        "ultima_inscricao": resultado.ultima_inscricao,
    }


@router.get("/ocupacao-media")
def stats_ocupacao_media(session: Session = Depends(getSession)):
    """F12 domínio: ocupação média por evento."""
    resultados = ocupacao_media_por_evento(session)
    return [
        {
            "evento_id": r.evento_id,
            "ocupacao_media": round(r.ocupacao_media, 4),
        }
        for r in resultados
    ]


@router.get("/taxa-ocupacao")
def stats_taxa_ocupacao(
    evento_id: int | None = None, session: Session = Depends(getSession)
):
    """F11a: taxa de ocupação por atividade."""
    resultados = taxa_ocupacao_por_atividade(session, evento_id)
    return [
        {
            "atividade_id": r.id,
            "titulo": r.titulo,
            "capacidade_maxima": r.capacidade_maxima,
            "confirmadas": r.confirmadas,
            "taxa": round(r.taxa, 4),
        }
        for r in resultados
    ]


@router.get("/atividades-com-vagas")
def stats_atividades_vagas(
    evento_id: int | None = None, session: Session = Depends(getSession)
):
    """F10c: atividades com vagas disponíveis."""
    resultados = atividades_com_vagas(session, evento_id)
    return [
        {
            "atividade_id": r[0].id,
            "titulo": r[0].titulo,
            "capacidade_maxima": r[0].capacidade_maxima,
            "inscritos_confirmados": r[1],
            "vagas_disponiveis": r[0].capacidade_maxima - r[1],
        }
        for r in resultados
    ]


@router.get("/conflitos/{participante_id}")
def stats_conflitos(
    participante_id: int, session: Session = Depends(getSession)
):
    """F11b: conflitos de horário de um participante."""
    from app.models.participante import Participante

    if not session.get(Participante, participante_id):
        raise HTTPException(
            status_code=404, detail="Participante não encontrado"
        )

    resultados = conflitos_horario_participante(session, participante_id)
    return [
        {
            "atividade_1": {
                "id": r.atividade_1_id,
                "titulo": r.atividade_1_titulo,
                "inicio": r.inicio_1,
                "fim": r.fim_1,
            },
            "atividade_2": {
                "id": r.atividade_2_id,
                "titulo": r.atividade_2_titulo,
                "inicio": r.inicio_2,
                "fim": r.fim_2,
            },
        }
        for r in resultados
    ]