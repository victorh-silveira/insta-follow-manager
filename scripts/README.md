# Scripts Operacionais

Scripts de automacao, qualidade e manutencao do workspace:

- [`operations/clean_workspace.py`](operations/clean_workspace.py): orquestrador unico bidirecional executado pelo `Makefile`, `.pre-commit-config.yaml` e `.github/workflows/ci.yml` (`Lint`, `Validate`, `Seguranca`, `Testes`, `Build` e `Clean`).
