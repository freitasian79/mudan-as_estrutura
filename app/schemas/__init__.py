from app.schemas.evento import EventoCreate, EventoPublic, EventoUpdate
from app.schemas.local import LocalCreate, LocalPublic, LocalUpdate
from app.schemas.palestrante import PalestranteCreate, PalestrantePublic, PalestranteUpdate
from app.schemas.atividade import (
 AtividadeCreate,
 AtividadePublic,
 AtividadePublicDetalhada,
 AtividadeUpdate,
)
from app.schemas.participante import ParticipanteCreate, ParticipantePublic, ParticipanteUpdate
from app.schemas.inscricao import (
 InscricaoCreate,
 InscricaoPublic,
 InscricaoPublicDetalhada,
 InscricaoUpdate,
)
from app.schemas.presenca import PresencaCreate, PresencaPublic
from app.schemas.paginacao import (
 PaginaAtividades,
 PaginaEventos,
 PaginaInscricoes,
 PaginaLocais,
 PaginaPalestrantes,
 PaginaParticipantes,
)