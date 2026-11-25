from sqlmodel import SQLModel

class ParticipanteCreate(SQLModel):
    nome: str
    email: str
    cpf: str | None = None
    instituicao: str | None = None

class ParticipantePublic(SQLModel):
    id: int
    nome: str
    email: str
    cpf: str | None
    instituicao: str | None

class ParticipanteUpdate(SQLModel):
    nome: str | None = None
    email: str | None = None
    cpf: str | None = None
    instituicao: str | None = None