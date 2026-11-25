from datetime import datetime

from sqlmodel import SQLModel

from app.models.inscricao import StatusInscricao
from app.schemas.atividade import AtividadePublic
from app.schemas.participante import ParticipantePublic

class InscricaoCreate(SQLModel):
    participante_id: int
    atividade_id: int
    status: StatusInscricao = StatusInscricao.PENDENTE

class InscricaoPublic(SQLModel):
    id: int
    participante_id: int
    atividade_id: int
    status: StatusInscricao
    data_criacao: datetime

class InscricaoPublicDetalhada(InscricaoPublic):
    participante: ParticipantePublic | None = None
    atividade: AtividadePublic | None = None

class InscricaoUpdate(SQLModel):
    participante_id: int | None = None
    atividade_id: int | None = None
    status: StatusInscricao | None = None