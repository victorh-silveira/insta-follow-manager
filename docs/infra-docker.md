# Infraestrutura Docker e Docker Compose

## Praticas Seniores Aplicadas

- **Multi-stage builds**:
  - `infra/docker/backend.Dockerfile`: `python:3.13.9-slim-bookworm` (`builder` -> `runtime`), copiando apenas `/opt/venv` e `backend/src/`.
  - `infra/docker/frontend.Dockerfile`: `node:22.14-alpine` (`deps` -> `builder` -> `runner`) com Next.js `output: "standalone"`.
- **Menor Privilegio (`USER`)**:
  - Containers executam como usuarios sem privilegios e sem shell de login (`appuser` e `nextjs`, UID `10001`).
- **PID 1 e Graceful Shutdown**:
  - `tini` + `init: true` + `CMD` em forma exec para repasse correto de `SIGTERM`.
- **Redes, Portas e Volumes (`infra/docker/docker-compose.yml`)**:
  - Rede isolada `insta_net` (`bridge`).
  - Portas vinculadas exclusivamente em `127.0.0.1` (`127.0.0.1:8000:8000` e `127.0.0.1:3000:3000`).
  - `depends_on` com `condition: service_healthy` e `healthcheck` real em ambos os servicos.
  - Volume nomeado `insta_db_data:/app/data` para persistencia do SQLite e sessao.
  - Profile opcional `debug` (`make docker-debug-up` / `docker compose --profile debug up -d`) para logs via Dozzle.

## Comandos Docker no Makefile

- `make docker-up` / `make docker-down` / `make docker-restart`
- `make docker-build` / `make docker-rebuild` (`DOCKER_SERVICE=backend|frontend`)
- `make docker-reset` / `make docker-clean` (destrutivos)
- `make docker-ps` / `make docker-logs` / `make docker-stats`
- `make docker-smoke` / `make docker-shell` / `make docker-debug-up`
