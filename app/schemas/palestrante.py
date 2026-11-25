from sqlmodel import SQLModel

class PalestranteCreate(SQLModel):
    nome: str
    email: str
    biografia: str | None = None
    instituicao: str | None = None

class PalestrantePublic(SQLModel):
    id: int
    nome: str
    email: str
    biografia: str | None
    instituicao: str | None

class PalestranteUpdate(SQLModel):
    nome: str | None = None
    email: str | None = None
    biografia: str | None = None
    instituicao: str | None = None