from app.crud.base import CRUDBase
from app.models.palestrante import Palestrante

crud_palestrante = CRUDBase(Palestrante, Palestrante.nome)
