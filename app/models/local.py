from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship, SQLModel

class LocalBase(SQLModel):
 nome: str = Field(min_length=3, max_length=200, unique=True, index=True)
 capacidade_geral: int = Field(gt=0)
 descricao: str | None = Field(default=None, max_length=500)

class Local(LocalBase, table=True):
 __table_args__ = (
 CheckConstraint("capacidade_geral > 0", name="ck_local_capacidade"),
 )

 id: int | None = Field(default=None, primary_key=True)

 atividades: list["Atividade"] = Relationship(back_populates="local")