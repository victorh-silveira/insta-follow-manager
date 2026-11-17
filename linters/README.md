# Linters e Git Hooks

Este diretorio centraliza a governanca de commits e hooks locais do repositorio:

- `commitlint.config.mjs`: valida Conventional Commits em **PT-BR** com escopos padronizados.
- `git-hooks/install.sh`: instala os hooks `pre-commit` e `commit-msg` via `pre-commit`.

## Instalacao

```bash
bash linters/git-hooks/install.sh
```
