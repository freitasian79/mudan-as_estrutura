from app.crud.base import CRUDBase
from app.models.local import Local

crud_local = CRUDBase(Local, Local.nome)
