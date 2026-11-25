from datetime import datetime
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel

class StatusInscricao(str, Enum):
 PENDENTE = "pendente"
 CONFIRMADA = "confirmada"
 CANCELADA = "cancelada"

class InscricaoBase(SQLModel):
 participante_id: int = Field(foreign_key="participante.id", index=True)
 atividade_id: int = Field(foreign_key="atividade.id", index=True)
 status: StatusInscricao = Field(default=StatusInscricao.PENDENTE, index=True)

class Inscricao(InscricaoBase, table=True):
 __table_args__ = (
 {"sqlite_autoincrement": False},
 )

 id: int | None = Field(default=None, primary_key=True)
 data_criacao: datetime = Field(default_factory=datetime.now)

 participante: "Participante" = Relationship(back_populates="inscricoes")
 atividade: "Atividade" = Relationship(back_populates="inscricoes")
 presenca: "Presenca" = Relationship(back_populates="inscricao")