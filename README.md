# Insta Follow Manager

[![CI/CD](https://github.com/victorh-silveira/insta-follow-manager/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/victorh-silveira/insta-follow-manager/actions/workflows/ci.yml)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](backend/requirements.txt)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688?logo=fastapi&logoColor=white)](backend/src/presentation/main.py)
[![Next.js](https://img.shields.io/badge/Next.js-standalone-000000?logo=nextdotjs&logoColor=white)](frontend/next.config.ts)
[![React](https://img.shields.io/badge/React-TypeScript-61DAFB?logo=react&logoColor=black)](frontend/package.json)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-UI-06B6D4?logo=tailwindcss&logoColor=white)](frontend/src/app/globals.css)
[![Architecture](https://img.shields.io/badge/Architecture-DDD%20%7C%20Clean%20%7C%20SOLID-0A66C2)](docs/arquitetura.md)
[![Ruff](https://img.shields.io/badge/Ruff-lint%20%7C%20format-D7FF64?logo=ruff&logoColor=black)](backend/pyproject.toml)
[![Tests](https://img.shields.io/badge/pytest-58%20passed%20%7C%20100%25%20cov-0F9D58?logo=pytest&logoColor=white)](backend/tests)
[![Security](https://img.shields.io/badge/security-bandit%20%7C%20gitleaks-C0392B)](.gitleaks.toml)
[![Pre-commit](https://img.shields.io/badge/pre--commit-16%20gates%20ativos-FAB040?logo=pre-commit&logoColor=white)](.pre-commit-config.yaml)
[![Commits](https://img.shields.io/badge/commits-Conventional%20Commits%20PT--BR-FE5196?logo=conventionalcommits&logoColor=white)](linters/commitlint.config.mjs)
[![Docker Compose](https://img.shields.io/badge/infra-Docker%20Compose-2496ED?logo=docker&logoColor=white)](infra/docker/docker-compose.yml)

Aplicacao full-stack para sincronizacao, triagem alfabetica e gerenciamento de listas de **Seguindo** (*Following*) e **Seguidores** (*Followers*) do Instagram pelo **nome de exibicao** (`full_name`), com filtro instantaneo (**A–Z**, **0–9** e **Caracteres Especiais**) e acao direta de **Unfollow**.

---

## Destaques de Arquitetura e Engenharia

- **DDD + Clean Architecture + SOLID:** Camada `backend/src/domain/` 100% pura (zero imports de `fastapi`, `sqlite3`, `instagrapi` ou `pydantic`), comunicando-se exclusivamente via Ports (`InstagramGateway`, `ProfileRepository`).
- **Adapter Pattern Plugavel:** `MockInstagramGateway` (padrao seguro para desenvolvimento e TDD) e `InstagrapiGateway` (integracao real com sessao persistida e tratamento de desafios/rate-limit).
- **Cache Local Indexado (SQLite):** Navegacao instantanea entre letras sem estourar rate limits da API do Instagram.
- **Logging Semantico Estruturado:** Saida em `stdout` (`LOG_FORMAT=json|console`), correlacao ponta a ponta via `X-Request-ID` (`contextvars`) e redacao automatica de credenciais.
- **Dockerfiles Seniores + Compose:** Multi-stage builds (`python:3.13.9-slim-bookworm` e `node:22.14-alpine` com Next.js `standalone`), usuarios `non-root` (`UID 10001`), `tini` (PID 1), `healthcheck` real e bind exclusivo em `127.0.0.1`.
- **CI/CD Bidirecional:** Paridade 1:1 por tecnologia entre `scripts/operations/clean_workspace.py`, `Makefile`, `.pre-commit-config.yaml` e `.github/workflows/ci.yml`.
- **Harness Universal de Agentes (`.agents/`):** Regras (`.agents/rules/`), personas (`.agents/agents/`) e skills (`.agents/skills/`) alinhadas em [AGENTS.md](AGENTS.md) e [prompt-model.md](prompt-model.md).

---

## Triagem Alfabetica pelo Nome de Exibicao (`NameBucket`)

- **`A–Z`:** Normalizacao Unicode NFKD (ex.: `Ágata` -> `A`, `Érika` -> `E`, `Ícaro` -> `I`).
- **`0–9`:** Nomes iniciados por digitos numericos (ex.: `007 Tech News`, `3D Studio Brasil`).
- **`Caracteres Especiais` (`SPECIAL`):** Emojis, simbolos (`.`, `_`, `@`) ou perfis sem `full_name` preenchido.

---

## Execucao Rapida

### 1. Modo Local (`venv` + Next.js)

```powershell
# Backend (Windows PowerShell)
cd backend
.\.venv\Scripts\Activate.ps1
copy .env.example .env
uvicorn src.presentation.main:app --reload
```

```powershell
# Frontend (em outro terminal)
cd frontend
npm run dev
```

Acesse `http://localhost:3000`, clique em **Sincronizar Instagram** e navegue pelas abas **Seguindo**, **Seguidores** e **Nao me seguem de volta**.

### 2. Modo Container (Docker Compose)

```bash
make docker-up
make docker-ps
make docker-smoke
```

---

## Operacao via Makefile & Quality Gates

```bash
make help                # Menu interativo completo
make app-lint            # Lint Python, YAML, React (ESLint), Docker e Shell
make app-validate        # Validate Python, JSON, TypeScript, Tailwind CSS e Docker
make app-security        # Seguranca Python (gitleaks + bandit), Node (npm) e Docker
make app-test            # Testes automatizados pytest + cobertura
make app-build           # Build Python (FastAPI) e Next.js standalone
make app-pre-commit      # Instala githooks pre-commit e commit-msg
make app-pre-commit-run  # Executa os 16 hooks por tecnologia em todos os arquivos
```

---

## Documentacao Tecnica Completa

- [Indice da Documentacao](docs/README.md)
- [Arquitetura Tecnica (DDD + Clean Architecture)](docs/arquitetura.md)
- [Padroes de Engenharia, Logging e CI/CD Bidirecional](docs/engineering-standards.md)
- [Infraestrutura Docker e Docker Compose](docs/infra-docker.md)
- [Harness de Agentes (`AGENTS.md`)](AGENTS.md)
- [Contrato Reutilizavel (`prompt-model.md`)](prompt-model.md)
- [Historico de Mudancas (`CHANGELOG.md`)](docs/CHANGELOG.md)
