---
name: precommit-ci-sync
description: Garante paridade bidirecional entre pre-commit, Makefile e GitHub Actions CI.
---

# Pre-Commit & CI Bidirectional Sync

1. Toda verificacao deve ser implementada em `scripts/operations/clean_workspace.py`.
2. Nomear hooks e steps sempre por tecnologia especifica no formato `<Tecnologia> | <Etapa>` (ex.: `Python | Lint`, `TypeScript | Validate`, `React (ESLint) | Lint`, `Tailwind CSS | Validate`, `Next.js | Build`, `Docker | Lint`, `Shell | Lint`).
3. Validar localmente executando `python scripts/operations/clean_workspace.py --area <area> --stage <stage>`.
