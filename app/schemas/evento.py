from datetime import date

from sqlmodel import SQLModel

class EventoCreate(SQLModel):
    nome: str
    descricao: str | None = None
    data_inicio: date
    data_fim: date
    ativo: bool = True

class EventoPublic(SQLModel):
    id: int
    nome: str
    descricao: str | None
    data_inicio: date
    data_fim: date
    ativo: bool

class EventoUpdate(SQLModel):
    nome: str | None = None
    descricao: str | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    ativo: bool | None = None