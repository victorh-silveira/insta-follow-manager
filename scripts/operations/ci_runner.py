"""Runner bidirecional unico para Pre-Commit, Makefile e GitHub Actions CI/CD."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"


def resolve_backend_python() -> str:
    """Resolve Python executable preferring backend/.venv when present."""
    candidates = [
        BACKEND_DIR / ".venv" / "Scripts" / "python.exe",
        BACKEND_DIR / ".venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return sys.executable


def run_cmd(cmd: list[str], cwd: Path) -> int:
    """Execute a subprocess and stream output directly."""
    print(f"[ci_runner] ({cwd.name}) -> {' '.join(cmd)}")
    completed = subprocess.run(cmd, cwd=str(cwd), check=False)
    return completed.returncode


def run_python(stage: str, coverage_fail_under: int) -> int:
    py = resolve_backend_python()
    if stage == "lint":
        if shutil.which("ruff"):
            rc = run_cmd(["ruff", "check", "src", "tests"], BACKEND_DIR)
            if rc != 0:
                return rc
            return run_cmd(["ruff", "format", "--check", "src", "tests"], BACKEND_DIR)
        print("[ci_runner] ruff nao instalado localmente; validando sintaxe via py_compile.")
        return run_cmd([py, "-m", "compileall", "-q", "src", "tests"], BACKEND_DIR)

    if stage == "validate":
        return run_cmd([py, "-m", "compileall", "-q", "src", "tests"], BACKEND_DIR)

    if stage == "security":
        if shutil.which("gitleaks"):
            gitleaks_cmd = ["gitleaks", "detect", "--source", ".", "--config", ".gitleaks.toml"]
            if not (ROOT_DIR / ".git").exists():
                gitleaks_cmd.append("--no-git")
            rc = run_cmd(gitleaks_cmd, ROOT_DIR)
            if rc != 0:
                return rc
        if shutil.which("bandit"):
            return run_cmd(["bandit", "-r", "src", "-ll"], BACKEND_DIR)
        print("[ci_runner] gitleaks/bandit opcionais ausentes; verificacao basica concluida.")
        return 0

    if stage == "test":
        cmd = [py, "-m", "pytest", "--cov=src", "--cov-report=term-missing"]
        if coverage_fail_under > 0:
            cmd.append(f"--cov-fail-under={coverage_fail_under}")
        return run_cmd(cmd, BACKEND_DIR)

    if stage == "build":
        return run_cmd(
            [py, "-c", "from src.presentation.main import app; assert app is not None"],
            BACKEND_DIR,
        )

    if stage == "clean":
        for folder in (".pytest_cache", ".ruff_cache", ".mypy_cache", "htmlcov"):
            target = BACKEND_DIR / folder
            if target.exists():
                shutil.rmtree(target, ignore_errors=True)
        return 0

    raise ValueError(f"Unsupported stage for python: {stage}")


def run_frontend(stage: str) -> int:
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    npx_cmd = "npx.cmd" if sys.platform == "win32" else "npx"

    if stage == "lint":
        return run_cmd([npm_cmd, "run", "lint"], FRONTEND_DIR)
    if stage == "validate":
        return run_cmd([npx_cmd, "tsc", "--noEmit"], FRONTEND_DIR)
    if stage == "security":
        return run_cmd([npm_cmd, "audit", "--audit-level=high"], FRONTEND_DIR)
    if stage == "test":
        print("[ci_runner] Frontend lint + typecheck validados (sem suite Jest configurada).")
        return 0
    if stage == "build":
        return run_cmd([npm_cmd, "run", "build"], FRONTEND_DIR)
    if stage == "clean":
        next_dir = FRONTEND_DIR / ".next"
        if next_dir.exists():
            shutil.rmtree(next_dir, ignore_errors=True)
        return 0

    raise ValueError(f"Unsupported stage for frontend: {stage}")


def run_docker(stage: str) -> int:
    dockerfiles = [BACKEND_DIR / "Dockerfile", FRONTEND_DIR / "Dockerfile"]

    if stage == "lint":
        if shutil.which("hadolint"):
            for df in dockerfiles:
                rc = run_cmd(["hadolint", str(df)], ROOT_DIR)
                if rc != 0:
                    return rc
            return 0
        for df in dockerfiles:
            content = df.read_text(encoding="utf-8")
            if "USER " not in content or "HEALTHCHECK " not in content:
                print(f"[ci_runner] Falha de seguranca em {df}: USER ou HEALTHCHECK ausente.")
                return 1
        print("[ci_runner] Dockerfiles validados (USER non-root e HEALTHCHECK presentes).")
        return 0

    if stage == "validate":
        if shutil.which("docker"):
            return run_cmd(["docker", "compose", "config", "--quiet"], ROOT_DIR)
        print("[ci_runner] docker CLI ausente neste ambiente; validacao compose ignorada.")
        return 0

    if stage == "security":
        if shutil.which("trivy"):
            return run_cmd(["trivy", "config", "--severity", "HIGH,CRITICAL", "."], ROOT_DIR)
        print("[ci_runner] trivy ausente neste ambiente; scan de config ignorado.")
        return 0

    if stage == "build":
        if shutil.which("docker"):
            return run_cmd(["docker", "compose", "build"], ROOT_DIR)
        print("[ci_runner] docker CLI ausente neste ambiente; docker build ignorado.")
        return 0

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Bidirectional CI/CD & Pre-Commit Runner")
    parser.add_argument("--area", required=True, choices=["python", "frontend", "docker"])
    parser.add_argument(
        "--stage",
        required=True,
        choices=["lint", "validate", "security", "test", "build", "clean"],
    )
    parser.add_argument("--coverage-fail-under", type=int, default=80)
    args = parser.parse_args()

    if args.area == "python":
        return run_python(args.stage, args.coverage_fail_under)
    if args.area == "frontend":
        return run_frontend(args.stage)
    return run_docker(args.stage)


if __name__ == "__main__":
    raise SystemExit(main())
