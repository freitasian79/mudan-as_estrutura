from datetime import datetime

from sqlmodel import SQLModel

class PresencaCreate(SQLModel):
    inscricao_id: int

class PresencaPublic(SQLModel):
    inscricao_id: int
    data_checkin: datetime