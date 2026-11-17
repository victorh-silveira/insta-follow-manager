# Arquitetura — DDD, Clean Architecture e SOLID

## Camadas do Backend (`backend/src/`)

1. **Domain (`domain/`)**:
   - `InstagramProfile`: entidade central com `pk`, `username`, `full_name`, `is_following`, `is_follower`, `is_verified` e `mark_unfollowed()`.
   - `NameBucket`: Value Object que normaliza acentos via Unicode NFKD e classifica o **nome de exibicao** (`full_name`) em `A-Z`, `0-9` ou `SPECIAL`.
   - `ProfileRepository` e `InstagramGateway`: interfaces (Ports) sem dependencias externas.
2. **Application (`application/`)**:
   - `SyncRelationshipsUseCase`: sincroniza Seguindo e Seguidores e persiste o snapshot.
   - `ListProfilesByBucketUseCase`: filtra por lista (`following`, `followers`, `non_followers`), bucket (`A-Z`, `0-9`, `SPECIAL`) e busca, ordenando alfabeticamente pelo nome de exibicao.
   - `UnfollowProfileUseCase`: envia unfollow para o gateway e atualiza o repositorio apenas em caso de sucesso.
3. **Infrastructure (`infrastructure/`)**:
   - `SQLiteProfileRepository` + `SQLiteDatabase`: cache local para filtragem instantanea.
   - `MockInstagramGateway` (desenvolvimento/TDD) e `InstagrapiGateway` (API privada do Instagram).
4. **Presentation (`presentation/`)**:
   - FastAPI REST API (`/api/health`, `/api/relationships/sync`, `/api/relationships`, `/api/relationships/{pk}/unfollow`).
