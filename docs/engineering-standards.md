# Padroes de Engenharia, TDD, Pre-Commit e CI/CD

## Paridade Bidirecional por Tecnologia (Local <-> GitHub Actions)

Todas as etapas de qualidade passam pelo orquestrador unico `scripts/operations/clean_workspace.py`, garantindo identicos resultados no `Makefile`, `.pre-commit-config.yaml` e `.github/workflows/ci.yml`:

| Tecnologia | Etapa | Nome Padrao |
|---|---|---|
| Commitlint | Conventional Commits | `Commitlint \| Conventional Commits` |
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

## Contrato de Commits (PT-BR)

Configurado em `linters/commitlint.config.mjs`:
- Formato: `tipo(escopo): assunto em portugues`
- Verbos em ingles no assunto sao bloqueados automaticamente.
