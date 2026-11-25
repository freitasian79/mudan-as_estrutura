from app.crud.base import CRUDBase
from app.models.evento import Evento

crud_evento = CRUDBase(Evento, Evento.nome)
