# Insta Follow Manager

Aplicação para triagem e organização de listas de **Seguindo** e **Seguidores** do Instagram em ordem alfabética (**A–Z**, **0–9** e **Caracteres Especiais**) pelo **nome de exibição** (`full_name`), com botão de **Unfollow** direto.

## Arquitetura

- **Backend (`backend/`)**: Python + `venv` + FastAPI + SQLite seguindo **DDD, Clean Architecture, SOLID e TDD** (`pytest`).
  - `domain/`: Entidade `InstagramProfile`, Value Object `NameBucket` (A–Z com normalização de acentos, `0-9`, `SPECIAL`), e Ports (`ProfileRepository`, `InstagramGateway`).
  - `application/`: Casos de uso `SyncRelationshipsUseCase`, `ListProfilesByBucketUseCase` e `UnfollowProfileUseCase`.
  - `infrastructure/`: `SQLiteProfileRepository`, `MockInstagramGateway` (padrão seguro para desenvolvimento) e `InstagrapiGateway` (API privada do Instagram).
  - `presentation/`: API REST FastAPI.
- **Frontend (`frontend/`)**: React + Next.js (App Router + TypeScript) + Tailwind CSS.

## Como executar

### 1. Backend (Python + venv)

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
copy .env.example .env
uvicorn src.presentation.main:app --reload
```

Rodar testes automatizados (TDD):

```powershell
cd backend
.\.venv\Scripts\pytest.exe --cov=src
```

### 2. Frontend (Next.js + Tailwind CSS)

```powershell
cd frontend
npm run dev
```

Acesse `http://localhost:3000`, clique em **Sincronizar Instagram** e navegue pelas abas **A–Z**, **0–9** e **Caracteres Especiais**.
