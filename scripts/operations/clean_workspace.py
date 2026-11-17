"""Orquestrador unico bidirecional para Clean Workspace, Pre-Commit, Makefile e CI/CD."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

IGNORED_DIRS = {".git", ".venv", "node_modules", ".next", "__pycache__", ".pytest_cache"}


def resolve_backend_python() -> str:
    """Resolve Python executable preferring the matching OS backend/.venv interpreter."""
    if sys.platform == "win32":
        candidates = [BACKEND_DIR / ".venv" / "Scripts" / "python.exe"]
    else:
        candidates = [BACKEND_DIR / ".venv" / "bin" / "python"]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return sys.executable


def run_cmd(cmd: list[str], cwd: Path) -> int:
    """Execute a subprocess and stream output directly."""
    print(f"[clean_workspace] ({cwd.name}) -> {' '.join(cmd)}")
    completed = subprocess.run(cmd, cwd=str(cwd), check=False)
    return completed.returncode


def iter_project_files(*extensions: str) -> list[Path]:
    """Collect project files matching extensions while skipping vendor/cache dirs."""
    matched: list[Path] = []
    for path in ROOT_DIR.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in extensions:
            matched.append(path)
    return sorted(matched)


def run_python(stage: str, coverage_fail_under: int) -> int:
    py = resolve_backend_python()
    if stage == "lint":
        if shutil.which("ruff"):
            rc = run_cmd(["ruff", "check", "src", "tests"], BACKEND_DIR)
            if rc != 0:
                return rc
            return run_cmd(["ruff", "format", "--check", "src", "tests"], BACKEND_DIR)
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
        print("[clean_workspace] gitleaks/bandit opcionais ausentes; verificacao basica concluida.")
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


def run_json(stage: str) -> int:
    if stage != "validate":
        return 0
    files = iter_project_files(".json")
    for file_path in files:
        # tsconfig.json permits comments in some setups; parse standard JSON files strictly
        if file_path.name == "tsconfig.json":
            continue
        try:
            json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"[clean_workspace] JSON invalido em {file_path}: {exc}")
            return 1
    print(f"[clean_workspace] {len(files)} arquivos JSON validados.")
    return 0


def run_yaml(stage: str) -> int:
    if stage != "lint":
        return 0
    files = iter_project_files(".yml", ".yaml")
    rel_files = [f.relative_to(ROOT_DIR).as_posix() for f in files]
    if shutil.which("yamllint"):
        return run_cmd(["yamllint", "-c", ".yamllint.yaml", *rel_files], ROOT_DIR)
    py = resolve_backend_python()
    for rel_path in rel_files:
        rc = run_cmd(
            [
                py,
                "-c",
                "import sys, yaml; yaml.safe_load(open(sys.argv[1], encoding='utf-8'))",
                rel_path,
            ],
            ROOT_DIR,
        )
        if rc != 0:
            return rc
    print(f"[clean_workspace] {len(rel_files)} arquivos YAML validados.")
    return 0


def run_typescript(stage: str) -> int:
    if stage != "validate":
        return 0
    npx_cmd = "npx.cmd" if sys.platform == "win32" else "npx"
    return run_cmd([npx_cmd, "tsc", "--noEmit"], FRONTEND_DIR)


def run_react(stage: str) -> int:
    if stage != "lint":
        return 0
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    return run_cmd([npm_cmd, "run", "lint"], FRONTEND_DIR)


def run_tailwind(stage: str) -> int:
    if stage != "validate":
        return 0
    globals_css = FRONTEND_DIR / "src" / "app" / "globals.css"
    next_config = FRONTEND_DIR / "next.config.ts"
    if not globals_css.exists():
        print("[clean_workspace] globals.css nao encontrado.")
        return 1
    css_text = globals_css.read_text(encoding="utf-8")
    if "tailwindcss" not in css_text:
        print("[clean_workspace] Diretiva tailwindcss ausente em globals.css.")
        return 1
    if "@tailwindcss/turbopack" not in next_config.read_text(encoding="utf-8"):
        print("[clean_workspace] Loader @tailwindcss/turbopack ausente em next.config.ts.")
        return 1
    print("[clean_workspace] Configuracao Tailwind CSS validada.")
    return 0


def run_nextjs(stage: str) -> int:
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    if stage == "build":
        return run_cmd([npm_cmd, "run", "build"], FRONTEND_DIR)
    if stage == "clean":
        next_dir = FRONTEND_DIR / ".next"
        if next_dir.exists():
            shutil.rmtree(next_dir, ignore_errors=True)
        return 0
    return 0


def run_node(stage: str) -> int:
    if stage != "security":
        return 0
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    return run_cmd([npm_cmd, "audit", "--audit-level=high"], FRONTEND_DIR)


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
                print(f"[clean_workspace] Falha de seguranca em {df}: USER ou HEALTHCHECK ausente.")
                return 1
        print("[clean_workspace] Dockerfiles validados (USER non-root e HEALTHCHECK presentes).")
        return 0

    if stage == "validate":
        if shutil.which("docker"):
            return run_cmd(["docker", "compose", "config", "--quiet"], ROOT_DIR)
        print("[clean_workspace] docker CLI ausente neste ambiente; validacao compose ignorada.")
        return 0

    if stage == "security":
        if shutil.which("trivy"):
            return run_cmd(["trivy", "config", "--severity", "HIGH,CRITICAL", "."], ROOT_DIR)
        print("[clean_workspace] trivy ausente neste ambiente; scan de config ignorado.")
        return 0

    if stage == "build":
        if shutil.which("docker"):
            return run_cmd(["docker", "compose", "build"], ROOT_DIR)
        print("[clean_workspace] docker CLI ausente neste ambiente; docker build ignorado.")
        return 0

    return 0


def run_shell(stage: str) -> int:
    if stage != "lint":
        return 0
    scripts = iter_project_files(".sh")
    if not scripts:
        return 0
    rel_scripts = [s.relative_to(ROOT_DIR).as_posix() for s in scripts]
    if shutil.which("shellcheck"):
        return run_cmd(["shellcheck", *rel_scripts], ROOT_DIR)
    if shutil.which("bash"):
        for script in rel_scripts:
            rc = run_cmd(["bash", "-n", script], ROOT_DIR)
            if rc != 0:
                return rc
        return 0
    print("[clean_workspace] shellcheck/bash ausentes; validacao shell ignorada.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Bidirectional Clean Workspace & CI/CD Runner")
    parser.add_argument(
        "--area",
        required=True,
        choices=[
            "python",
            "json",
            "yaml",
            "typescript",
            "react",
            "tailwind",
            "nextjs",
            "node",
            "docker",
            "shell",
            "all",
        ],
    )
    parser.add_argument(
        "--stage",
        required=True,
        choices=["lint", "validate", "security", "test", "build", "clean"],
    )
    parser.add_argument("--coverage-fail-under", type=int, default=80)
    args = parser.parse_args()

    dispatch = {
        "python": lambda: run_python(args.stage, args.coverage_fail_under),
        "json": lambda: run_json(args.stage),
        "yaml": lambda: run_yaml(args.stage),
        "typescript": lambda: run_typescript(args.stage),
        "react": lambda: run_react(args.stage),
        "tailwind": lambda: run_tailwind(args.stage),
        "nextjs": lambda: run_nextjs(args.stage),
        "node": lambda: run_node(args.stage),
        "docker": lambda: run_docker(args.stage),
        "shell": lambda: run_shell(args.stage),
    }

    if args.area == "all" and args.stage == "clean":
        rc1 = run_python("clean", args.coverage_fail_under)
        rc2 = run_nextjs("clean")
        return rc1 or rc2

    return dispatch[args.area]()


if __name__ == "__main__":
    raise SystemExit(main())
