from datetime import datetime

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

class AtividadePalestrante(SQLModel, table=True):
 atividade_id: int | None = Field(
 default=None,
 foreign_key="atividade.id",
 primary_key=True,
 )
 palestrante_id: int | None = Field(
 default=None,
 foreign_key="palestrante.id",
 primary_key=True,
 )

class AtividadeBase(SQLModel):
 evento_id: int = Field(foreign_key="evento.id", index=True)
 local_id: int = Field(foreign_key="local.id", index=True)
 titulo: str = Field(min_length=3, max_length=300, index=True)
 descricao: str | None = Field(default=None, max_length=1000)
 data_hora_inicio: datetime = Field(index=True)
 data_hora_fim: datetime = Field(index=True)
 capacidade_maxima: int = Field(gt=0)
 cancelada: bool = Field(default=False, index=True)

class Atividade(AtividadeBase, table=True):
 __table_args__ = (
 CheckConstraint("capacidade_maxima > 0", name="ck_atividade_capacidade"),
 UniqueConstraint("evento_id", "titulo", name="uq_atividade_evento_titulo"),
 )

 id: int | None = Field(default=None, primary_key=True)

 evento: "Evento" = Relationship(back_populates="atividades")
 local: "Local" = Relationship(back_populates="atividades")
 palestrantes: list["Palestrante"] = Relationship(
 back_populates="atividades",
 link_model=AtividadePalestrante,
 )
 inscricoes: list["Inscricao"] = Relationship(back_populates="atividade")