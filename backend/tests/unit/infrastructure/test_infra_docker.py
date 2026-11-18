"""Testes de contrato para padronizacao de versoes e stack infra/docker."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[4]
INFRA_DOCKER_DIR = ROOT_DIR / "infra" / "docker"


def test_version_files_exist_and_match_stack() -> None:
    python_version = (ROOT_DIR / ".python-version").read_text(encoding="utf-8").strip()
    node_version = (ROOT_DIR / ".node-version").read_text(encoding="utf-8").strip()

    assert python_version == "3.13" or python_version.startswith("3.13.")
    assert node_version.startswith("22.14")


def test_infra_docker_files_and_hardening() -> None:
    compose = (INFRA_DOCKER_DIR / "docker-compose.yml").read_text(encoding="utf-8")
    backend_df = (INFRA_DOCKER_DIR / "backend.Dockerfile").read_text(encoding="utf-8")
    frontend_df = (INFRA_DOCKER_DIR / "frontend.Dockerfile").read_text(encoding="utf-8")

    assert (INFRA_DOCKER_DIR / ".dockerignore").is_file()
    assert (INFRA_DOCKER_DIR / ".env.example").is_file()
    assert (INFRA_DOCKER_DIR / "README.md").is_file()

    assert "x-logging:" in compose
    assert "no-new-privileges:true" in compose
    assert "cap_drop:" in compose
    assert "infra/docker/backend.Dockerfile" in compose
    assert "infra/docker/frontend.Dockerfile" in compose

    for df in (backend_df, frontend_df):
        assert "org.opencontainers.image." in df
        assert "tini" in df
        assert "HEALTHCHECK" in df
        assert "USER " in df
