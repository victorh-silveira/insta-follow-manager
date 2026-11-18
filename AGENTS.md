# AGENTS.md — Insta Follow Manager

Ponto de entrada unico e canonico para agentes autonomos de IA e desenvolvedores no repositorio **Insta Follow Manager**.

---

## 1. Identidade e Diretrizes Gerais

- **Idioma oficial:** Todas as respostas, documentacoes tecnicas e mensagens de commit devem ser escritas em **PT-BR**.
- **Arquitetura:** **DDD (Domain-Driven Design), Clean Architecture, SOLID e TDD**.
  - `backend/src/domain/` deve permanecer 100% puro, sem imports de `fastapi`, `sqlite3`, `instagrapi` ou `pydantic`.
  - Comunicacao com servicos externos ocorre exclusivamente via Ports (`InstagramGateway`, `ProfileRepository`) e Adapters na camada `infrastructure/`.
- **Frontend:** React + Next.js (App Router, TypeScript) + Tailwind CSS com build `standalone`.
- **Integridade de Codigo:** Funcoes pequenas, responsabilidade unica, zero duplicacao de logica e docstrings claras.
- **Proibicao de Comentarios em Codigo:** E **100% proibido** escrever comentarios (`#`, `//`, `/* */`) em codigo-fonte e testes (`backend/src/`, `backend/tests/`, `frontend/src/`, `scripts/`). O codigo deve ser autoexplicativo por nomes claros e docstrings concisas; apenas diretivas tecnicas obrigatorias de ferramentas (`# type: ignore[...]`, `eslint-disable-next-line`, shebangs) sao toleradas quando inevitaveis.
- **Contrato de Commits:** Seguir rigorosamente Conventional Commits em **PT-BR** validados por `linters/commitlint.config.mjs`.

---

## 2. Harness de Agentes (`.agents/`)

As instrucoes operacionais estao centralizadas na pasta agnostica `.agents/`:
- **Regras (`.agents/rules/`):** aplicadas continuamente durante alteracoes de codigo e infra.
- **Perfis (`.agents/agents/`):** `architect.md`, `qa-tester.md` e `devops.md`.
- **Habilidades (`.agents/skills/`):** `precommit-ci-sync` e `tdd-workflow`.

---

## 3. Matriz de Leitura Rapida

| Tarefa | Documento Principal | Regra Obrigatoria |
|---|---|---|
| Arquitetura DDD / Clean / SOLID | `docs/arquitetura.md` | `.agents/rules/architecture-senior.mdc` |
| Padroes de Engenharia, TDD e CI | `docs/engineering-standards.md` | `.agents/rules/engineering.mdc` |
| Testes Automatizados (pytest) | `docs/engineering-standards.md` | `.agents/rules/testing.mdc` |
| Commits PT-BR e Pre-Commit | `linters/README.md` | `.agents/rules/git-commit.mdc` |
| Dockerfiles e Compose Senior | `docs/infra-docker.md` | `.agents/rules/infra-docker.mdc` |
