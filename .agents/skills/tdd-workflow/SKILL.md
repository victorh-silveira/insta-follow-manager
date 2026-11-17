---
name: tdd-workflow
description: Fluxo padrao de desenvolvimento orientado a testes para o backend e frontend.
---

# TDD Workflow

1. Escrever ou atualizar testes unitarios em `backend/tests/unit/` antes de implementar regras novas.
2. Utilizar test doubles (`InMemoryProfileRepository`, `FakeInstagramGateway`) sem tocar rede ou banco real nos unitarios.
3. Validar integracao FastAPI + SQLite em `backend/tests/integration/`.
4. Rodar `python scripts/operations/ci_runner.py --area python --stage test`.
