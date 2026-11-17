# Testes de Integracao

Testes ponta a ponta da camada de apresentacao e persistencia real:

- [`api/`](api/): testes da API REST FastAPI com `TestClient`, SQLite temporario, middleware de correlacao `X-Request-ID` e mapeamento de excecoes de dominio.
