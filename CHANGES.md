# Alterações

## Arquivos do zip que estavam errados (corrigidos)
- `services/inscricao_service.py` continha o **router de eventos** → movido para `routers/eventos.py`; o serviço foi escrito (`validar_inscricao` não existia).
- `routers/eventos.py` era cópia de `locais.py` (prefixo `/locais`).
- `schemas/ativiade.py` (typo) → `schemas/atividade.py` (o `__init__` importava o nome correto, que não existia).
- `models/ativiade.py` vazio → removido.

## Arquitetura
- `crud/base.py`: `CRUDBase` genérico (buscar/listar paginado/criar/atualizar/excluir).
- `crud/*.py`: instâncias de `CRUDBase`; `CRUDAtividade` (palestrantes via relationship), `CRUDInscricao` (cancelar, contar_confirmadas), `CRUDPresenca`.
- `utils.py`: `metadados`, `ou_404`, `conflito_409`.
- Routers só fazem HTTP; nenhum usa `session.add/commit/delete` direto.

## Bugs corrigidos
- `func.cast(x, float)` quebrava na compilação → `cast(x, Float)`.
- `estatisticas_evento` devolvia `None` sem inscrições → `coalesce` + `case`.
- PATCH de atividade: removido o delete manual de `AtividadePalestrante`.
- `Palestrante.link_model="AtividadePalestrante"` (string) quebrava o import dos models.
- PATCH de atividade agora valida evento/local informados.
- Inscrição: não existia unique no banco, então o 409 "duplicada" nunca disparava; agora a checagem está no serviço (e permite reinscrever após cancelamento).
- `main.py` cria as tabelas no startup.

Testes: `pytest tests` (3 testes, fluxo completo). Rodado com sqlmodel 0.0.22 / SQLAlchemy 2.0.
