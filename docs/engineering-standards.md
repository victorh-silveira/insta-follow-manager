# Padroes de Engenharia, TDD, Pre-Commit e CI/CD

## Paridade Bidirecional (Local <-> GitHub Actions)

Todas as etapas de qualidade passam pelo runner unico `scripts/operations/ci_runner.py`, garantindo identicos resultados no `Makefile`, `.pre-commit-config.yaml` e `.github/workflows/ci.yml`:

| Stack | Etapa | Nome Padrao |
|---|---|---|
| Commitlint | Conventional Commits | `Commitlint \| Conventional Commits` |
| Python | Lint | `Python \| Lint` |
| Python | Validate | `Python \| Validate` |
| Python | Seguranca | `Python \| Seguranca` |
| Python | Testes | `Python \| Testes` |
| Python | Build | `Python \| Build` |
| Frontend | Lint | `Frontend \| Lint` |
| Frontend | Validate | `Frontend \| Validate` |
| Frontend | Seguranca | `Frontend \| Seguranca` |
| Frontend | Build | `Frontend \| Build` |
| Docker | Lint | `Docker \| Lint` |
| Docker | Validate | `Docker \| Validate` |

## Contrato de Commits (PT-BR)

Configurado em `linters/commitlint.config.mjs`:
- Formato: `tipo(escopo): assunto em portugues`
- Verbos em ingles no assunto sao bloqueados automaticamente.
