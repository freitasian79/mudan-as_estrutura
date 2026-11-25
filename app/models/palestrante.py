from sqlmodel import Field, Relationship, SQLModel

from app.models.atividade import AtividadePalestrante

class PalestranteBase(SQLModel):
 nome: str = Field(min_length=3, max_length=200, index=True)
 email: str = Field(unique=True, max_length=200, index=True)
 biografia: str | None = Field(default=None, max_length=1000)
 instituicao: str | None = Field(default=None, max_length=200)

class Palestrante(PalestranteBase, table=True):
 id: int | None = Field(default=None, primary_key=True)

 atividades: list["Atividade"] = Relationship(
 back_populates="palestrantes",
 link_model=AtividadePalestrante,
 )