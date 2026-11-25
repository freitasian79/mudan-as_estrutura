from sqlmodel import Field, Relationship, SQLModel

class ParticipanteBase(SQLModel):
 nome: str = Field(min_length=3, max_length=200, index=True)
 email: str = Field(unique=True, max_length=200, index=True)
 cpf: str | None = Field(default=None, unique=True, max_length=14, index=True)
 instituicao: str | None = Field(default=None, max_length=200)

class Participante(ParticipanteBase, table=True):
 id: int | None = Field(default=None, primary_key=True)

 inscricoes: list["Inscricao"] = Relationship(back_populates="participante")