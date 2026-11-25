from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.crud.inscricao import crud_inscricao
from app.crud.presenca import crud_presenca
from app.database import getSession
from app.models.inscricao import StatusInscricao
from app.schemas.presenca import PresencaCreate, PresencaPublic
from app.utils import conflito_409, ou_404

router = APIRouter(prefix="/presencas", tags=["Presenças"])
NAO_ENCONTRADA = "Presença não encontrada"


@router.post("/", response_model=PresencaPublic, status_code=201)
def registrar_presenca(
    dados: PresencaCreate, session: Session = Depends(getSession)
):
    inscricao = ou_404(
        crud_inscricao.buscar(session, dados.inscricao_id),
        "Inscrição não encontrada",
    )
    if inscricao.status != StatusInscricao.CONFIRMADA:
        raise HTTPException(
            status_code=400,
            detail="Check-in permitido apenas para inscrições confirmadas",
        )
    if crud_presenca.buscar(session, dados.inscricao_id):
        raise HTTPException(
            status_code=409,
            detail="Presença já registrada para esta inscrição",
        )
    with conflito_409("Erro ao registrar presença"):
        return crud_presenca.registrar(session, dados.inscricao_id)


@router.get("/{inscricao_id}", response_model=PresencaPublic)
def buscar_presenca(inscricao_id: int, session: Session = Depends(getSession)):
    return ou_404(crud_presenca.buscar(session, inscricao_id), NAO_ENCONTRADA)


@router.delete("/{inscricao_id}", status_code=204)
def remover_presenca(
    inscricao_id: int, session: Session = Depends(getSession)
):
    presenca = ou_404(
        crud_presenca.buscar(session, inscricao_id), NAO_ENCONTRADA
    )
    crud_presenca.excluir(session, presenca)
