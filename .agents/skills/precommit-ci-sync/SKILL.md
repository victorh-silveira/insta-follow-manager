---
name: precommit-ci-sync
description: Garante paridade bidirecional entre pre-commit, Makefile e GitHub Actions CI.
---

# Pre-Commit & CI Bidirectional Sync

1. Toda verificacao deve ser implementada em `scripts/operations/ci_runner.py`.
2. Nomear hooks e steps sempre no formato `<Stack> | <Etapa>` (ex.: `Python | Lint`, `Python | Seguranca`, `Frontend | Build`, `Docker | Lint`).
3. Validar localmente executando `python scripts/operations/ci_runner.py --area <area> --stage <stage>`.
