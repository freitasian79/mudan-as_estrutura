from sqlmodel import SQLModel

from app.models.paginacao import MetadadosPaginacao
from app.schemas.atividade import AtividadePublic
from app.schemas.evento import EventoPublic
from app.schemas.inscricao import InscricaoPublic
from app.schemas.local import LocalPublic
from app.schemas.palestrante import PalestrantePublic
from app.schemas.participante import ParticipantePublic

class PaginaEventos(SQLModel):
    dados: list[EventoPublic]
    paginacao: MetadadosPaginacao

class PaginaLocais(SQLModel):
    dados: list[LocalPublic]
    paginacao: MetadadosPaginacao

class PaginaPalestrantes(SQLModel):
    dados: list[PalestrantePublic]
    paginacao: MetadadosPaginacao

class PaginaAtividades(SQLModel):
    dados: list[AtividadePublic]
    paginacao: MetadadosPaginacao

class PaginaParticipantes(SQLModel):
    dados: list[ParticipantePublic]
    paginacao: MetadadosPaginacao

class PaginaInscricoes(SQLModel):
    dados: list[InscricaoPublic]
    paginacao: MetadadosPaginacao