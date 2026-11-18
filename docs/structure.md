# Estrutura Canônica do Repositório

```text
insta-follow-manager/
├── .python-version              # SSOT da versao Python (3.13.9)
├── .node-version                # SSOT da versao Node.js (22.14.0)
├── .dockerignore                # Exclusoes para builds Docker com contexto raiz
├── Makefile                     # Automacao local (qualidade, testes e Docker)
├── .github/
│   ├── actions/ci/              # Composite actions (setup-python, setup-node, release, etc.)
│   └── workflows/ci.yml         # Pipeline CI/CD por tecnologia
├── infra/
│   └── docker/
│       ├── docker-compose.yml   # Orquestracao backend + frontend + log-viewer
│       ├── backend.Dockerfile   # Imagem FastAPI multi-stage non-root
│       ├── frontend.Dockerfile  # Imagem Next.js standalone multi-stage non-root
│       ├── .dockerignore        # Espelho de exclusoes para infra/docker
│       ├── .env.example         # Variaveis de build/runtime do Compose
│       └── README.md            # Guia operacional Docker
├── backend/                     # API FastAPI (DDD: domain, application, infrastructure, presentation)
├── frontend/                    # Aplicacao Next.js (App Router + TypeScript + Tailwind CSS)
├── linters/                     # Commitlint PT-BR, semantic-release e git hooks
├── scripts/operations/          # Gates por tecnologia (clean_workspace.py)
└── docs/                        # Documentacao tecnica e CHANGELOG
```
