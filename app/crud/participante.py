from app.crud.base import CRUDBase
from app.models.participante import Participante

crud_participante = CRUDBase(Participante, Participante.nome)
