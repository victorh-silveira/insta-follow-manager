# Padroes de Engenharia, TDD, Logging Semantico e CI/CD

## Paridade Bidirecional 100% por Tecnologia (Local <-> GitHub Actions)

Cada tecnologia possui um job dedicado no GitHub Actions (`CI - <Tecnologia>`) e o ciclo completo de 5 etapas (`Lint`, `Validate`, `Seguranca`, `Testes`, `Build`) no `.pre-commit-config.yaml`, `Makefile` e `scripts/operations/clean_workspace.py`:

| Job CI | Area (`clean_workspace.py`) | Etapas |
|---|---|---|
| `CI - Commitlint` | — | `Commitlint (Conventional Commits)` |
| `CI - Python` | `python` | `Python \| Lint`, `Validate`, `Seguranca`, `Testes`, `Build` |
| `CI - TypeScript` | `typescript` | `TypeScript \| Lint`, `Validate`, `Seguranca`, `Testes`, `Build` |
| `CI - React` | `react` | `React \| Lint`, `Validate`, `Seguranca`, `Testes`, `Build` |
| `CI - Next.js` | `nextjs` | `Next.js \| Lint`, `Validate`, `Seguranca`, `Testes`, `Build` |
| `CI - Tailwind CSS` | `tailwind` | `Tailwind CSS \| Lint`, `Validate`, `Seguranca`, `Testes`, `Build` |
| `CI - Docker` | `docker` | `Docker \| Lint`, `Validate`, `Seguranca`, `Testes`, `Build` |
| `CI - Shell` | `shell` | `Shell \| Lint`, `Validate`, `Seguranca`, `Testes`, `Build` |
| `CI - JSON` | `json` | `JSON \| Lint`, `Validate`, `Seguranca`, `Testes`, `Build` |
| `CI - YAML` | `yaml` | `YAML \| Lint`, `Validate`, `Seguranca`, `Testes`, `Build` |

## Logging Semantico Estruturado

- Saida exclusivamente em `stdout` (`LOG_FORMAT=json|console`, `LOG_LEVEL=INFO`).
- Correlacao via `X-Request-ID` propagada por `RequestLoggingMiddleware` + `contextvars`.
- Eventos no padrao `dominio.acao.resultado` (`relationships.sync.started`, `relationships.sync.completed`, `relationships.unfollow.succeeded`, `http.request.completed`).
- Zero emojis e mascaramento automatico (`***REDACTED***`) para chaves contendo `password`, `token`, `secret`, `cookie`, `session` ou `authorization`.

## Contrato de Commits (PT-BR)

Configurado em `linters/commitlint.config.mjs`:
- Formato: `tipo(escopo): assunto em portugues` (linha de corpo com no maximo 100 caracteres).
- Verbos em ingles no assunto sao bloqueados automaticamente.
