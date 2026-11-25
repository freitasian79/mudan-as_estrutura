from sqlmodel import SQLModel

class LocalCreate(SQLModel):
    nome: str
    capacidade_geral: int
    descricao: str | None = None

class LocalPublic(SQLModel):
    id: int
    nome: str
    capacidade_geral: int
    descricao: str | None

class LocalUpdate(SQLModel):
    nome: str | None = None
    capacidade_geral: int | None = None
    descricao: str | None = None