import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import app.models  # noqa
from app.database import getSession
from app.main import app


@pytest.fixture
def c():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(eng)

    def sess():
        with Session(eng) as s:
            yield s

    app.dependency_overrides[getSession] = sess
    with TestClient(app) as cl:
        yield cl
    app.dependency_overrides.clear()


def mk(c):
    ev = c.post("/eventos/", json={"nome": "Evento X", "data_inicio": "2026-12-01", "data_fim": "2026-12-03"}).json()
    lo = c.post("/locais/", json={"nome": "Sala 1", "capacidade_geral": 50}).json()
    pa = c.post("/palestrantes/", json={"nome": "Ana Lima", "email": "a@x.com"}).json()
    return ev, lo, pa


def ativ(c, ev, lo, pids, titulo="Palestra A", ini="2026-12-01T09:00:00", fim="2026-12-01T10:00:00", cap=1):
    return c.post("/atividades/", json={"evento_id": ev["id"], "local_id": lo["id"], "titulo": titulo,
        "data_hora_inicio": ini, "data_hora_fim": fim, "capacidade_maxima": cap, "palestrante_ids": pids})


def test_crud_basico_e_409(c):
    r = c.post("/locais/", json={"nome": "Sala 1", "capacidade_geral": 5}); assert r.status_code == 201
    assert c.post("/locais/", json={"nome": "Sala 1", "capacidade_geral": 5}).status_code == 409
    assert c.get("/locais/999").status_code == 404
    r = c.get("/locais/?pagina=1&tamanho_pagina=10&nome=sala").json()
    assert r["paginacao"]["total_registros"] == 1
    assert c.patch(f"/locais/{r['dados'][0]['id']}", json={"descricao": "x"}).json()["descricao"] == "x"
    assert c.delete(f"/locais/{r['dados'][0]['id']}").status_code == 204


def test_atividade_palestrantes(c):
    ev, lo, pa = mk(c)
    r = ativ(c, ev, lo, [pa["id"], pa["id"]]); assert r.status_code == 201, r.text
    a = r.json(); assert len(a["palestrantes"]) == 1
    pa2 = c.post("/palestrantes/", json={"nome": "Bia Souza", "email": "b@x.com"}).json()
    r = c.patch(f"/atividades/{a['id']}", json={"palestrante_ids": [pa2["id"]]}); assert r.status_code == 200, r.text
    assert [p["id"] for p in r.json()["palestrantes"]] == [pa2["id"]]
    assert ativ(c, ev, lo, [pa["id"]]).status_code == 409
    assert ativ(c, ev, lo, [999], titulo="Outra").status_code == 404
    assert c.delete(f"/atividades/{a['id']}").status_code == 204


def test_inscricoes_regras_e_stats(c):
    ev, lo, pa = mk(c)
    a1 = ativ(c, ev, lo, [pa["id"]]).json()
    a2 = ativ(c, ev, lo, [], titulo="Sobreposta", ini="2026-12-01T09:30:00", fim="2026-12-01T10:30:00", cap=5).json()
    p1 = c.post("/participantes/", json={"nome": "Carlos", "email": "c@x.com", "cpf": "1"}).json()
    p2 = c.post("/participantes/", json={"nome": "Diana", "email": "d@x.com", "cpf": "2"}).json()

    i1 = c.post("/inscricoes/", json={"participante_id": p1["id"], "atividade_id": a1["id"], "status": "confirmada"})
    assert i1.status_code == 201, i1.text
    assert c.post("/inscricoes/", json={"participante_id": p1["id"], "atividade_id": a1["id"]}).status_code == 409  # duplicada
    assert c.post("/inscricoes/", json={"participante_id": p2["id"], "atividade_id": a1["id"]}).status_code == 409  # lotada
    r = c.post("/inscricoes/", json={"participante_id": p1["id"], "atividade_id": a2["id"]})
    assert r.status_code == 409 and "Conflito" in r.json()["detail"]

    # check-in
    assert c.post("/presencas/", json={"inscricao_id": i1.json()["id"]}).status_code == 201
    assert c.post("/presencas/", json={"inscricao_id": i1.json()["id"]}).status_code == 409
    assert c.get(f"/presencas/{i1.json()['id']}").status_code == 200

    # confirmar a própria inscrição via PATCH não pode barrar por duplicidade/capacidade
    assert c.patch(f"/inscricoes/{i1.json()['id']}", json={"status": "confirmada"}).status_code == 200

    assert c.get(f"/participantes/{p1['id']}/programacao").json()[0]["id"] == a1["id"]
    assert len(c.get(f"/inscricoes/atividade/{a1['id']}/inscritos").json()) == 1

    s = c.get(f"/estatisticas/evento/{ev['id']}").json(); assert s["confirmadas"] == 1 and s["canceladas"] == 0
    t = c.get("/estatisticas/taxa-ocupacao").json(); assert t[0]["taxa"] == 1.0
    assert len(c.get("/estatisticas/ocupacao-media").json()) == 1
    assert [x["atividade_id"] for x in c.get("/estatisticas/atividades-com-vagas").json()] == [a2["id"]]
    assert c.get(f"/estatisticas/conflitos/{p1['id']}").status_code == 200

    # cancelar libera vaga; evento sem inscrições devolve 0 (não None)
    assert c.delete(f"/inscricoes/{i1.json()['id']}").status_code == 204
    assert c.post("/inscricoes/", json={"participante_id": p2["id"], "atividade_id": a1["id"]}).status_code == 201
    ev2 = c.post("/eventos/", json={"nome": "Vazio", "data_inicio": "2026-12-01", "data_fim": "2026-12-02"}).json()
    s = c.get(f"/estatisticas/evento/{ev2['id']}").json(); assert s["confirmadas"] == 0 and s["canceladas"] == 0
