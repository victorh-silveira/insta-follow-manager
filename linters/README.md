# Linters e Git Hooks

Este diretorio centraliza a governanca de commits e hooks locais do repositorio:

- `commitlint.config.mjs`: valida Conventional Commits em **PT-BR** com escopos padronizados.
- `git-hooks/install.sh`: instala os hooks `pre-commit` e `commit-msg` via `pre-commit`.
- `git-hooks/bin/commitlint-early.sh`: valida a mensagem de commit ja na primeira linha de `make app-pre-commit-run`.

## Instalacao e Execucao

```bash
make app-pre-commit
make app-pre-commit-run
```
