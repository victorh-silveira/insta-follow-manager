## [1.1.1](https://github.com/victorh-silveira/insta-follow-manager/compare/v1.1.0...v1.1.1) (2026-11-17)

### Correcoes de Bug

* **all:** eliminar warnings de tini, starlette e actions node20 ([7695003](https://github.com/victorh-silveira/insta-follow-manager/commit/7695003af34583958bc7e39e4f34057306b6a811))

## [1.1.0](https://github.com/victorh-silveira/insta-follow-manager/compare/v1.0.0...v1.1.0) (2026-11-17)

### Funcionalidades

* **all:** integra autenticacao e sincronizacao real com API do Instagram ([60ff7d9](https://github.com/victorh-silveira/insta-follow-manager/commit/60ff7d99dd376b0474028f5ce68c6f89ab1b5b4e))

## 1.0.0 (2026-11-17)

### Funcionalidades

* **all:** estrutura inicial do gerenciador de seguidores com DDD, Docker e CI ([36e5207](https://github.com/victorh-silveira/insta-follow-manager/commit/36e52076527ec6dddc1ee579e553cfb748bb5d71))

### Correcoes de Bug

* **ci:** audita apenas dependencias de producao no Next.js Seguranca ([42647a3](https://github.com/victorh-silveira/insta-follow-manager/commit/42647a3e402d55990707b308a534e0a52efdc0e1))
* **ci:** corrige escopo do gitleaks e elimina interpolacao SQL no repositorio ([d360094](https://github.com/victorh-silveira/insta-follow-manager/commit/d36009429101f295bd2d03c8c01a5a7fe33b67d0))
* **ci:** corrige TypeScript Validate e Hadolint nos Dockerfiles ([33b8539](https://github.com/victorh-silveira/insta-follow-manager/commit/33b8539dd840692cf78438eb74031f0873e1d0cc))
* **scripts:** adiciona suporte a venv isolada no WSL ([3724bfd](https://github.com/victorh-silveira/insta-follow-manager/commit/3724bfd4934e90ea47c7629781caabc2b58a06d6))
* **scripts:** resolve python por SO e usa caminhos relativos no YAML lint ([b0064b6](https://github.com/victorh-silveira/insta-follow-manager/commit/b0064b6bbdb84869aae15d622b834ca439054b87))

### Refatoracoes Tecnicas

* **ci:** desdobra gates por tecnologia em clean_workspace, pre-commit e CI ([6e559ae](https://github.com/victorh-silveira/insta-follow-manager/commit/6e559ae50193dfb766ef58ce955ccd2a3152ff81))

### Documentacao

* **repo:** adiciona badges seniores e aprimora arquivos markdown ([eccbfc4](https://github.com/victorh-silveira/insta-follow-manager/commit/eccbfc40ee12d5361c89323c887acab6de3e2654))
* **repo:** corrige visualizacao de pastas colapsadas no GitHub ([a3244fc](https://github.com/victorh-silveira/insta-follow-manager/commit/a3244fc3f7dfa3266c91c3458f51f1422988837b))

## 1.0.0 (2026-11-17)

### Funcionalidades

* **all:** estrutura inicial do gerenciador de seguidores com DDD, Docker e CI ([36e5207](https://github.com/victorh-silveira/insta-follow-manager/commit/36e52076527ec6dddc1ee579e553cfb748bb5d71))

### Correcoes de Bug

* **ci:** audita apenas dependencias de producao no Next.js Seguranca ([42647a3](https://github.com/victorh-silveira/insta-follow-manager/commit/42647a3e402d55990707b308a534e0a52efdc0e1))
* **ci:** corrige escopo do gitleaks e elimina interpolacao SQL no repositorio ([d360094](https://github.com/victorh-silveira/insta-follow-manager/commit/d36009429101f295bd2d03c8c01a5a7fe33b67d0))
* **ci:** corrige TypeScript Validate e Hadolint nos Dockerfiles ([33b8539](https://github.com/victorh-silveira/insta-follow-manager/commit/33b8539dd840692cf78438eb74031f0873e1d0cc))
* **scripts:** adiciona suporte a venv isolada no WSL ([3724bfd](https://github.com/victorh-silveira/insta-follow-manager/commit/3724bfd4934e90ea47c7629781caabc2b58a06d6))
* **scripts:** resolve python por SO e usa caminhos relativos no YAML lint ([b0064b6](https://github.com/victorh-silveira/insta-follow-manager/commit/b0064b6bbdb84869aae15d622b834ca439054b87))

### Refatoracoes Tecnicas

* **ci:** desdobra gates por tecnologia em clean_workspace, pre-commit e CI ([6e559ae](https://github.com/victorh-silveira/insta-follow-manager/commit/6e559ae50193dfb766ef58ce955ccd2a3152ff81))

### Documentacao

* **repo:** adiciona badges seniores e aprimora arquivos markdown ([eccbfc4](https://github.com/victorh-silveira/insta-follow-manager/commit/eccbfc40ee12d5361c89323c887acab6de3e2654))
* **repo:** corrige visualizacao de pastas colapsadas no GitHub ([a3244fc](https://github.com/victorh-silveira/insta-follow-manager/commit/a3244fc3f7dfa3266c91c3458f51f1422988837b))

# Changelog

## [1.0.0] - 2026-11-17

### Adicionado
- Backend Python (`venv`) com FastAPI, SQLite e arquitetura DDD / Clean Architecture / SOLID / TDD.
- Frontend React + Next.js + Tailwind CSS com selecao alfabetica (`A-Z`, `0-9`, `Caracteres Especiais`) por nome de exibicao e botao Unfollow.
- Dockerfiles multi-stage (`non-root`, `tini`, `standalone`) e `docker-compose.yml` com healthchecks e volumes nomeados.
- Padronizacao completa de repositorio: `AGENTS.md`, `.agents/`, `linters/commitlint.config.mjs`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `Makefile` e `docs/`.
