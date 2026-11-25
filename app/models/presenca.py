from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

class Presenca(SQLModel, table=True):
 inscricao_id: int = Field(
 foreign_key="inscricao.id",
 primary_key=True,
 unique=True,
 )
 data_checkin: datetime = Field(default_factory=datetime.now)

 inscricao: "Inscricao" = Relationship(back_populates="presenca")