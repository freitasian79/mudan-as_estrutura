from datetime import datetime

from sqlmodel import SQLModel

from app.schemas.palestrante import PalestrantePublic

class AtividadeCreate(SQLModel):
    evento_id: int
    local_id: int
    titulo: str
    descricao: str | None = None
    data_hora_inicio: datetime
    data_hora_fim: datetime
    capacidade_maxima: int
    palestrante_ids: list[int] = []

class AtividadePublic(SQLModel):
    id: int
    evento_id: int
    local_id: int
    titulo: str
    descricao: str | None
    data_hora_inicio: datetime
    data_hora_fim: datetime
    capacidade_maxima: int
    cancelada: bool

class AtividadePublicDetalhada(AtividadePublic):
    palestrantes: list[PalestrantePublic] = []

class AtividadeUpdate(SQLModel):
    evento_id: int | None = None
    local_id: int | None = None
    titulo: str | None = None
    descricao: str | None = None
    data_hora_inicio: datetime | None = None
    data_hora_fim: datetime | None = None
    capacidade_maxima: int | None = None
    cancelada: bool | None = None
    palestrante_ids: list[int] | None = None