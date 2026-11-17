# Prompt-modelo de engenharia

Contrato reutilizavel derivado deste repositorio (**Insta Follow Manager**). Use este arquivo para orientar um agente a gerar ou adaptar qualquer projeto (Python, Fullstack ou outra linguagem) com o mesmo padrao de engenharia: **DDD, Clean Architecture, SOLID, TDD, Logging Semantico, Docker Senior, DX e documentacao**.

Dominios de negocio especificos (como triagem de seguidores do Instagram) sao apenas exemplos de aplicacao do padrao — **nao** regra obrigatoria do novo projeto.

## 1. Papel e objetivo

Voce e um engenheiro senior. Ao receber um novo dominio de negocio e (opcionalmente) uma linguagem, deve:

1. Projetar e implementar a solucao no padrao deste contrato.
2. Adaptar ferramentas e pastas a linguagem escolhida sem abandonar os invariantes.
3. Manter `docs/`, `Makefile`, hooks, CI/CD bidirecional e gates alinhados ao codigo.
4. Preferir TDD: testes primeiro nas camadas de dominio e application; integracao nos adapters de IO e API.

Objetivo final: o novo repositorio deve "parecer" este projeto em arquitetura, qualidade, observabilidade e operacao — nao copiar o dominio especifico de triagem do Instagram.

## 2. Contrato invariavel (language-agnostic)

### Camadas (Clean Architecture / DDD / Ports & Adapters)

| Camada | Conteudo | Pode depender de |
|---|---|---|
| `domain` | Entidades, value objects, domain services, excecoes e ports | Ninguem de fora do dominio |
| `application` | Use cases + DTOs + helper leve de eventos | `domain` |
| `infrastructure` | Adapters (Gateways HTTP/APIs, SQLite/DB), config (`settings.py`), logging formatter | `application`, `domain` |
| `presentation` | API REST (FastAPI) / middlewares / schemas + composition root (`dependencies.py`) | `application`, `domain`, `infrastructure` |

Regras:

- `domain` nao importa `fastapi`, `sqlite3`, `instagrapi`, `pydantic` nem `infrastructure`/`presentation`.
- `application` nao importa `infrastructure` nem `presentation`.
- Ports sao contratos (`ABC` / `Protocol` / interface). Adapters concretos residem em `infrastructure/`.
- Validacao de entidades e regras de negocio ficam no `domain`.
- Formatacao de payload de resposta HTTP fica na `presentation` (`schemas.py`); regras de classificacao/ordenacao ficam no `domain`/`application`.
- Composition root (`dependencies.py` ligando `Settings` -> adapters -> use cases) fica na `presentation`.
- Neste repo: Backend **Python 3.13 (`venv`) + FastAPI + SQLite** e Frontend **React + Next.js (App Router, TypeScript) + Tailwind CSS** (`output: "standalone"`).

### Qualidade e estilo

- Codigo autodescritivo com docstrings claras; evitar comentarios soltos explicando o obvio.
- Documentacao tecnica, respostas e mensagens de commit em **PT-BR**; **zero emojis** em codigo, logs ou documentacao.
- Conventional Commits com assunto em **PT-BR** (`linters/commitlint.config.mjs`).
- Segredos nunca no Git: `.env` ignorado + `.env.example` versionado; configuracao via `pydantic-settings`.
- Cobertura alta nas camadas de app (gate minimo `>= 80%` no `ci_runner.py`, visando **100%** em `domain/` e `use_cases/`).
- Limite de tamanho por arquivo de codigo (~**300** linhas); extrair quando passar.
- Type checking estrito (`tsc --noEmit` no frontend; tipagem completa no backend Python).

### Testes (TDD)

- Unitarios por camada: `backend/tests/unit/{domain,application,infrastructure}`.
- Integracao para adapters de IO e endpoints HTTP: `backend/tests/integration/api/`.
- Application: usar fakes/test doubles em memoria dos ports (`InMemoryProfileRepository`, `FakeInstagramGateway`).
- Isolar testes de bancos e sessoes reais usando `tmp_path` e `dependency_overrides`.

## 3. Arquitetura de pastas (template)

```text
.
├── backend/
│   ├── .venv/
│   ├── src/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   ├── value_objects/
│   │   │   ├── repositories/
│   │   │   ├── gateways/
│   │   │   └── exceptions.py
│   │   ├── application/
│   │   │   ├── dto/
│   │   │   ├── use_cases/
│   │   │   └── event_logger.py
│   │   ├── infrastructure/
│   │   │   ├── config/
│   │   │   ├── logging/
│   │   │   ├── persistence/
│   │   │   └── gateways/
│   │   └── presentation/
│   │       ├── api/
│   │       │   ├── middleware/
│   │       │   ├── routes/
│   │       │   ├── dependencies.py
│   │       │   └── schemas.py
│   │       └── main.py
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .env.example
│   ├── pyproject.toml
│   ├── pytest.ini
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── services/
│   │   └── types/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── next.config.ts
│   └── package.json
├── scripts/
│   └── operations/
│       └── clean_workspace.py    # Orquestrador unico bidirecional (Pre-Commit <-> Makefile <-> CI)
├── docs/
│   ├── README.md
│   ├── arquitetura.md
│   ├── engineering-standards.md
│   ├── infra-docker.md
│   └── CHANGELOG.md
├── linters/
│   ├── commitlint.config.mjs
│   ├── git-hooks/
│   └── README.md
├── .agents/
│   ├── agents/
│   ├── rules/
│   └── skills/
├── .github/
│   ├── workflows/ci.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── .gitattributes
├── .gitignore
├── .gitleaks.toml
├── .pre-commit-config.yaml
├── .yamllint.yaml
├── AGENTS.md
├── docker-compose.yml
├── Makefile
├── prompt-model.md
└── README.md
```

## 4. Qualidade, DX e Paridade Bidirecional

### Gates conceituais (nomenclatura `<Stack> | <Etapa>`)

| Gate | Ferramentas neste projeto |
|---|---|
| `Commitlint \| Conventional Commits` | `@commitlint/cli` + `linters/commitlint.config.mjs` (PT-BR) |
| `Python \| Lint` | `ruff check` + `ruff format --check` |
| `Python \| Validate` | `python -m compileall -q src tests` |
| `Python \| Seguranca` | `gitleaks` (`.gitleaks.toml`) + `bandit` |
| `Python \| Testes` | `pytest --cov=src --cov-fail-under=100` |
| `Python \| Build` | Importacao e validacao da app FastAPI |
| `Frontend \| Lint` | `npm run lint` (`eslint`) |
| `Frontend \| Validate` | `npx tsc --noEmit` |
| `Frontend \| Seguranca` | `npm audit --audit-level=high` |
| `Frontend \| Build` | `npm run build` (Next.js `standalone`) |
| `Docker \| Lint` | `hadolint` / verificacao `USER` non-root + `HEALTHCHECK` |
| `Docker \| Validate` | `docker compose config --quiet` |

Orquestrador central unico: `scripts/operations/ci_runner.py`, chamado identicamente por `.pre-commit-config.yaml`, `Makefile` e `.github/workflows/ci.yml`.

## 5. Logging semantico

Principios aplicados neste repositorio:

- Saida exclusiva em `stdout` (`SemanticJsonFormatter` via `LOG_FORMAT=json` ou `SemanticConsoleFormatter` via `LOG_FORMAT=console`).
- Eventos nomeados no padrao `dominio.acao.resultado` (ex.: `relationships.sync.started`, `relationships.sync.completed`, `relationships.unfollow.succeeded`, `http.request.completed`).
- Correlacao ponta a ponta via `contextvars` (`request_id` gerado/propagado por `RequestLoggingMiddleware` no header `X-Request-ID`).
- Zero emojis; zero dump de payload ou credenciais (`_redact_fields` mascara `password`, `token`, `secret`, `cookie`, `session`).
- Silenciar loggers ruidosos (`uvicorn.access` desabilitado em favor do middleware semantico).

## 6. Documentacao obrigatoria

| Doc | Papel |
|---|---|
| `docs/README.md` | Indice da documentacao |
| `docs/arquitetura.md` | Camadas DDD, Clean Architecture, ports e fluxo |
| `docs/engineering-standards.md` | Matriz bidirecional Pre-Commit/CI, TDD e CommitLint |
| `docs/infra-docker.md` | Dockerfiles multi-stage, non-root, tini, Compose e Makefile |
| `docs/CHANGELOG.md` | Historico de versoes |
| `AGENTS.md` | Ponto de entrada unico para agentes |
| `prompt-model.md` | Este contrato (raiz) |

## 7. Superficie universal de agentes (`.agents/`)

- Rules: `.agents/rules/*.mdc` (`alwaysApply: true`)
- Skills: `.agents/skills/*/SKILL.md` (`precommit-ci-sync`, `tdd-workflow`)
- Subagentes: `.agents/agents/*.md` (`architect.md`, `qa-tester.md`, `devops.md`)
- Indice: `AGENTS.md`

## 8. Protocolo de adaptacao (checklist do agente)

1. Ler o dominio/requisitos do novo projeto e a stack alvo.
2. Mapear entidades, value objects, use cases, ports e adapters necessarios.
3. Criar a arvore de pastas e impor regras de dependencia (`domain` puro).
4. Configurar `.env.example`, `Makefile`, `scripts/operations/ci_runner.py`, `.pre-commit-config.yaml` e `.github/workflows/ci.yml`.
5. Instalar hooks (`linters/git-hooks/install.sh` + `commitlint.config.mjs` em PT-BR).
6. Implementar em TDD: `domain` -> `application` (fakes) -> `infrastructure` -> `presentation` -> `frontend`.
7. Containerizar com `Dockerfile` multi-stage (`non-root`, `tini`, `CMD` exec, `HEALTHCHECK`) e `docker-compose.yml` (`condition: service_healthy`, bind `127.0.0.1`, named volumes, limits).
8. Atualizar `docs/` e `AGENTS.md`.
9. Rodar `ci_runner.py` (ou `make app-lint`, `make app-validate`, `make app-test`, `make app-build`) ate ficar 100% verde.

## 9. Anti-padroes

- Imports de framework web, SQL ou SDK externo dentro de `domain/` ou `application/`.
- Emojis em codigo, logs ou documentacao.
- Segredos commitados no Git ou em camadas Docker (`ENV`/`ARG`/`COPY`).
- Containers rodando como `root`, sem `tini` ou com `CMD` em forma shell.
- Divergencia entre checks do Pre-Commit, `Makefile` e GitHub Actions CI.
- Commits fora de Conventional Commits em PT-BR.
- Docs ou `.agents/` desatualizados apos mudancas estruturais.

## 10. PROMPT PARA COLAR

Copie o bloco abaixo integralmente em um novo chat/projeto. Substitua apenas as linhas marcadas com `<<< >>>`.

```text
Voce e um engenheiro senior. Adapte ou crie o repositorio abaixo para ficar equivalente ao contrato de engenharia do projeto de referencia (DDD + Clean Architecture + SOLID + TDD + Logging Semantico + Docker Senior + CI/CD Bidirecional). Contrato: prompt-model.md do repositorio Insta Follow Manager.

NOVO PROJETO
- Nome: <<<NOME>>>
- Dominio / objetivo: <<<DESCRICAO DO NEGOCIO>>>
- Stack Backend: <<<python/fastapi|go|node|outro>>>
- Stack Frontend: <<<nextjs+tailwind|nenhum|outro>>>
- Integracoes externas: <<<listar ou "nenhuma ainda">>>
- Infra Docker necessaria: <<<sim/nao; se sim, servicos minimos>>>

INVARIANTES (obrigatorios)
1. Camadas: domain (100% puro), application (use_cases + dto), infrastructure (adapters/config/logging), presentation (API/CLI + composition root).
2. Ports como contratos; adapters na infrastructure.
3. Validacao no dominio; regras de negocio nunca vazam para controllers/UI.
4. Logging semantico em stdout (JSON/console, request_id via contextvars, eventos dominio.acao.resultado, redacao de segredos, zero emojis).
5. Idioma PT-BR em respostas, docs e commits; zero emojis; Conventional Commits validados por linters/commitlint.config.mjs.
6. Config via .env + .env.example; nunca commitar segredos.
7. Testes TDD: unit por camada + integracao nos adapters de IO/API; fakes nos ports.
8. Paridade bidirecional Pre-Commit <-> Makefile <-> GitHub Actions via scripts/operations/ci_runner.py com nomes `<Stack> | <Etapa>`.
9. Dockerfiles multi-stage, tag fixa, usuario non-root, tini (PID 1), CMD exec, HEALTHCHECK, docker-compose.yml com condition: service_healthy e bind 127.0.0.1.

PASTAS ALVO
backend/src/{domain,application,infrastructure,presentation}
backend/tests/{unit,integration}
frontend/src/{app,components,services,types} (se houver UI)
scripts/operations/ci_runner.py
docs/{README,arquitetura,engineering-standards,infra-docker,CHANGELOG}.md
linters/{commitlint.config.mjs,git-hooks/,README.md}
.agents/{agents,rules,skills}
.github/workflows/ci.yml
.pre-commit-config.yaml, .gitattributes, .gitignore, .gitleaks.toml, .yamllint.yaml, Makefile, AGENTS.md, prompt-model.md, docker-compose.yml, README.md

PROTOCOLO
1) Mapear entidades, value objects, use cases, ports e adapters do dominio informado.
2) Criar estrutura, gates bidirecionais e hooks.
3) Implementar em TDD (domain -> application -> infrastructure -> presentation -> frontend).
4) Aplicar Docker Senior + Logging Semantico.
5) Atualizar docs/, AGENTS.md e .agents/.
6) Rodar ci_runner.py ate tudo ficar verde.

Entregue: estrutura, codigo, testes, Docker, CI/CD, Makefile, docs e AGENTS.md coerentes com este contrato.
```

## Referencia deste repositorio

- [`AGENTS.md`](AGENTS.md)
- [`docs/arquitetura.md`](docs/arquitetura.md)
- [`docs/engineering-standards.md`](docs/engineering-standards.md)
- [`docs/infra-docker.md`](docs/infra-docker.md)
- [`Makefile`](Makefile)
- [`scripts/operations/ci_runner.py`](scripts/operations/ci_runner.py)
- [`linters/commitlint.config.mjs`](linters/commitlint.config.mjs)
- [`.pre-commit-config.yaml`](.pre-commit-config.yaml)
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
