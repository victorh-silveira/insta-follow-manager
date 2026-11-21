# ==============================================================================
#                  INSTA FOLLOW MANAGER - CORE MAKEFILE
# ==============================================================================

SHELL := /bin/bash
PYTHON ?= python
DOCKER_DIR := infra/docker
DOCKER_COMPOSE := docker compose -f $(DOCKER_DIR)/docker-compose.yml
DOCKER_LOGS_TAIL ?= 200
DOCKER_SERVICE ?=
F ?= 1

GREEN  := \033[1;32m
YELLOW := \033[1;33m
BLUE   := \033[1;34m
CYAN   := \033[1;36m
RED    := \033[1;31m
RESET  := \033[0m

.DEFAULT_GOAL := help

.PHONY: help app-install app-lint app-validate app-security app-test app-build \
	app-clean app-pre-commit app-pre-commit-run docker-up docker-down \
	docker-restart docker-build docker-rebuild docker-reset docker-clean \
	docker-ps docker-logs docker-stats docker-smoke docker-shell \
	docker-debug-up docker-debug-down

help:
	@echo -e "$(BLUE)========================================================================$(RESET)"
	@echo -e "$(GREEN)                 INSTA FOLLOW MANAGER - MENU DE AJUDA                   $(RESET)"
	@echo -e "$(BLUE)========================================================================$(RESET)"
	@echo -e "Uso: $(CYAN)make <comando>$(RESET)"
	@echo -e ""
	@echo -e "$(YELLOW)Qualidade e CI Local (100% por Tecnologia):$(RESET)"
	@echo -e "  $(GREEN)app-install$(RESET)        - Cria backend/.venv e instala dependencias Python/Node"
	@echo -e "  $(GREEN)app-lint$(RESET)           - Lint de Python, TypeScript, React, Next.js, Tailwind, Docker, Shell, JSON, YAML"
	@echo -e "  $(GREEN)app-validate$(RESET)       - Validate de todas as 9 tecnologias da stack"
	@echo -e "  $(GREEN)app-security$(RESET)       - Seguranca de todas as 9 tecnologias da stack"
	@echo -e "  $(GREEN)app-test$(RESET)           - Testes de todas as 9 tecnologias da stack"
	@echo -e "  $(GREEN)app-build$(RESET)          - Build de todas as 9 tecnologias da stack"
	@echo -e "  $(GREEN)app-clean$(RESET)          - Limpa caches locais"
	@echo -e "  $(GREEN)app-pre-commit$(RESET)     - Instala githooks pre-commit e commit-msg"
	@echo -e "  $(GREEN)app-pre-commit-run$(RESET) - Roda todos os hooks por tecnologia"
	@echo -e ""
	@echo -e "$(YELLOW)Docker:$(RESET)"
	@echo -e "  $(GREEN)docker-up$(RESET)          - Sobe backend e frontend em containers (build + detach)"
	@echo -e "  $(GREEN)docker-down$(RESET)        - Para os containers preservando o volume SQLite"
	@echo -e "  $(GREEN)docker-restart$(RESET)     - Reinicia os containers preservando dados"
	@echo -e "  $(GREEN)docker-build$(RESET)       - Builda as imagens multi-stage (DOCKER_SERVICE=...)"
	@echo -e "  $(GREEN)docker-rebuild$(RESET)     - Rebuild sem cache e recria containers"
	@echo -e "  $(GREEN)docker-reset$(RESET)       - $(RED)DESTRUTIVO$(RESET): remove volumes, rebuilda e sobe do zero"
	@echo -e "  $(GREEN)docker-clean$(RESET)       - $(RED)DESTRUTIVO$(RESET): remove containers, redes, volumes e imagens"
	@echo -e "  $(GREEN)docker-ps$(RESET)          - Exibe status e healthcheck dos containers"
	@echo -e "  $(GREEN)docker-logs$(RESET)        - Exibe logs (DOCKER_SERVICE=... DOCKER_LOGS_TAIL=200 F=1)"
	@echo -e "  $(GREEN)docker-stats$(RESET)       - Exibe consumo de CPU e memoria dos containers"
	@echo -e "  $(GREEN)docker-smoke$(RESET)       - Verifica healthcheck HTTP de backend e frontend"
	@echo -e "  $(GREEN)docker-shell$(RESET)       - Abre shell no container (DOCKER_SERVICE=backend)"
	@echo -e "  $(GREEN)docker-debug-up$(RESET)    - Sobe stack com profile debug (Dozzle em :8888)"
	@echo -e "  $(GREEN)docker-debug-down$(RESET)  - Para stack incluindo profile debug"
	@echo -e "$(BLUE)========================================================================$(RESET)"

app-install:
	cd backend && $(PYTHON) -m venv .venv && ./.venv/bin/pip install -r requirements.txt -r requirements-dev.txt
	cd frontend && npm ci

app-lint:
	@for area in python typescript react nextjs tailwind docker shell json yaml; do \
		$(PYTHON) scripts/operations/clean_workspace.py --area $$area --stage lint || exit 1; \
	done

app-validate:
	@for area in python typescript react nextjs tailwind docker shell json yaml; do \
		$(PYTHON) scripts/operations/clean_workspace.py --area $$area --stage validate || exit 1; \
	done

app-security:
	@for area in python typescript react nextjs tailwind docker shell json yaml; do \
		$(PYTHON) scripts/operations/clean_workspace.py --area $$area --stage security || exit 1; \
	done

app-test:
	@for area in python typescript react nextjs tailwind docker shell json yaml; do \
		$(PYTHON) scripts/operations/clean_workspace.py --area $$area --stage test --coverage-fail-under 100 || exit 1; \
	done

app-build:
	@for area in python typescript react nextjs tailwind docker shell json yaml; do \
		$(PYTHON) scripts/operations/clean_workspace.py --area $$area --stage build || exit 1; \
	done

app-clean:
	$(PYTHON) scripts/operations/clean_workspace.py --area all --stage clean

app-pre-commit:
	bash linters/git-hooks/install.sh

app-pre-commit-run:
	pre-commit run --all-files

# ---- ALVOS DOCKER ----

docker-up:
	$(DOCKER_COMPOSE) up -d --build

docker-down:
	$(DOCKER_COMPOSE) down

docker-restart:
	$(DOCKER_COMPOSE) restart $(DOCKER_SERVICE)

docker-build:
	$(DOCKER_COMPOSE) build $(DOCKER_SERVICE)

docker-rebuild:
	$(DOCKER_COMPOSE) build --no-cache $(DOCKER_SERVICE)
	$(DOCKER_COMPOSE) up -d --force-recreate $(DOCKER_SERVICE)

docker-reset:
	$(DOCKER_COMPOSE) down -v --remove-orphans
	$(DOCKER_COMPOSE) up -d --build --force-recreate

docker-clean:
	$(DOCKER_COMPOSE) down -v --rmi local --remove-orphans

docker-ps:
	$(DOCKER_COMPOSE) ps -a

docker-logs:
	$(DOCKER_COMPOSE) logs $(if $(filter 1,$(F)),-f,) --tail=$(DOCKER_LOGS_TAIL) $(DOCKER_SERVICE)

docker-stats:
	docker stats --no-stream insta-manager-backend insta-manager-frontend

docker-smoke:
	@echo -e "$(CYAN)Verificando saude dos containers...$(RESET)"
	@curl -fsS http://127.0.0.1:8000/api/health && echo ""
	@curl -fsS -o /dev/null -w "Frontend HTTP %{http_code}\n" http://127.0.0.1:3000

docker-shell:
	$(DOCKER_COMPOSE) exec $(or $(DOCKER_SERVICE),backend) /bin/sh

docker-debug-up:
	$(DOCKER_COMPOSE) --profile debug up -d --build

docker-debug-down:
	$(DOCKER_COMPOSE) --profile debug down
