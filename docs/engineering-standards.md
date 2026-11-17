# Padroes de Engenharia, TDD, Logging Semantico e CI/CD

## Paridade Bidirecional por Tecnologia (Local <-> GitHub Actions)

Todas as etapas passam pelo orquestrador unico `scripts/operations/clean_workspace.py`, garantindo resultados identicos entre `.pre-commit-config.yaml`, `Makefile` e `.github/workflows/ci.yml`:

| Tecnologia | Etapa | Nome Padrao |
|---|---|---|
| Commitlint | Conventional Commits | `Commitlint (Conventional Commits)` |
| Python (FastAPI / SQLite) | Lint | `Python \| Lint` |
| Python (FastAPI / SQLite) | Validate | `Python \| Validate` |
| Python (FastAPI / SQLite) | Seguranca | `Python \| Seguranca` |
| Python (FastAPI / SQLite) | Testes | `Python \| Testes` |
| Python (FastAPI / SQLite) | Build | `Python \| Build` |
| JSON | Validate | `JSON \| Validate` |
| YAML | Lint | `YAML \| Lint` |
| TypeScript | Validate | `TypeScript \| Validate` |
| React (ESLint) | Lint | `React (ESLint) \| Lint` |
| Tailwind CSS | Validate | `Tailwind CSS \| Validate` |
| Next.js | Build | `Next.js \| Build` |
| Node (npm) | Seguranca | `Node (npm) \| Seguranca` |
| Docker | Lint | `Docker \| Lint` |
| Docker | Validate | `Docker \| Validate` |
| Docker | Seguranca | `Docker \| Seguranca` |
| Docker | Build | `Docker \| Build` |
| Shell (Bash) | Lint | `Shell \| Lint` |

## Logging Semantico Estruturado

- Saida exclusivamente em `stdout` (`LOG_FORMAT=json|console`, `LOG_LEVEL=INFO`).
- Correlacao via `X-Request-ID` propagada por `RequestLoggingMiddleware` + `contextvars`.
- Eventos no padrao `dominio.acao.resultado` (`relationships.sync.started`, `relationships.sync.completed`, `relationships.unfollow.succeeded`, `http.request.completed`).
- Zero emojis e mascaramento automatico (`***REDACTED***`) para chaves contendo `password`, `token`, `secret`, `cookie`, `session` ou `authorization`.

## Contrato de Commits (PT-BR)

Configurado em `linters/commitlint.config.mjs`:
- Formato: `tipo(escopo): assunto em portugues` (linha de corpo com no maximo 100 caracteres).
- Verbos em ingles no assunto sao bloqueados automaticamente.
