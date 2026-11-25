from datetime import date

from sqlmodel import Field, Relationship, SQLModel

class EventoBase(SQLModel):
 nome: str = Field(min_length=3, max_length=200, unique=True, index=True)
 descricao: str | None = Field(default=None, max_length=1000)
 data_inicio: date = Field(index=True)
 data_fim: date = Field(index=True)
 ativo: bool = Field(default=True, index=True)

class Evento(EventoBase, table=True):
 id: int | None = Field(default=None, primary_key=True)

 atividades: list["Atividade"] = Relationship(back_populates="evento")