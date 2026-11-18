# Infraestrutura Docker (`infra/docker/`)

Toda a orquestração e empacotamento em containers do **Insta Follow Manager** fica centralizada nesta pasta:

- `docker-compose.yml`: definição dos serviços `backend`, `frontend` e `log-viewer` (profile `debug`).
- `backend.Dockerfile`: build multi-stage Python (`3.13.9-slim-bookworm`), usuário não-root (`10001:10001`), `tini` como PID 1 e labels OCI.
- `frontend.Dockerfile`: build multi-stage Node.js (`22.14-alpine`) com Next.js `standalone`, usuário não-root (`10001:10001`), `tini` como PID 1 e labels OCI.
- `.dockerignore`: espelho do `.dockerignore` da raiz para builds com contexto `../..`.
- `.env.example`: variáveis opcionais de build e runtime.

## Comandos recomendados (via `Makefile` na raiz)

```bash
make docker-up         # Builda e sobe backend + frontend
make docker-smoke      # Valida /api/health e HTTP 200 no frontend
make docker-logs       # Acompanha os logs dos containers
make docker-down       # Para os containers preservando o volume SQLite
```
