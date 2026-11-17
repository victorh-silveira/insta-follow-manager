# Changelog

## [1.0.0] - 2026-11-17

### Adicionado
- Backend Python (`venv`) com FastAPI, SQLite e arquitetura DDD / Clean Architecture / SOLID / TDD.
- Frontend React + Next.js + Tailwind CSS com selecao alfabetica (`A-Z`, `0-9`, `Caracteres Especiais`) por nome de exibicao e botao Unfollow.
- Dockerfiles multi-stage (`non-root`, `tini`, `standalone`) e `docker-compose.yml` com healthchecks e volumes nomeados.
- Padronizacao completa de repositorio: `AGENTS.md`, `.agents/`, `linters/commitlint.config.mjs`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `Makefile` e `docs/`.
