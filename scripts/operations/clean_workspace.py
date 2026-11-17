"""Orquestrador unico bidirecional por tecnologia (Pre-Commit, Makefile e CI/CD)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

IGNORED_DIRS = {".git", ".venv", ".venv-wsl", "node_modules", ".next", "__pycache__", ".pytest_cache"}
_SENSITIVE_KEY_RE = re.compile(r"(password|secret|token|api_key|private_key)\s*[:=]\s*['\"][^'\"]+['\"]", re.I)


def resolve_backend_python() -> str:
    """Resolve Python executable preferring the matching OS backend venv interpreter."""
    if sys.platform == "win32":
        candidates = [BACKEND_DIR / ".venv" / "Scripts" / "python.exe"]
    else:
        candidates = [
            BACKEND_DIR / ".venv-wsl" / "bin" / "python",
            BACKEND_DIR / ".venv" / "bin" / "python",
        ]
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


def _node_bin(name: str) -> str:
    return f"{name}.cmd" if sys.platform == "win32" else name


def run_python(stage: str, coverage_fail_under: int) -> int:
    py = resolve_backend_python()
    if stage == "lint":
        if shutil.which("ruff"):
            rc = run_cmd(["ruff", "check", "src", "tests"], BACKEND_DIR)
            return rc or run_cmd(["ruff", "format", "--check", "src", "tests"], BACKEND_DIR)
        return run_cmd([py, "-m", "compileall", "-q", "src", "tests"], BACKEND_DIR)

    if stage == "validate":
        return run_cmd([py, "-m", "compileall", "-q", "src", "tests"], BACKEND_DIR)

    if stage == "security":
        if shutil.which("gitleaks"):
            cmd = ["gitleaks", "detect", "--source", ".", "--config", ".gitleaks.toml"]
            if not (ROOT_DIR / ".git").exists():
                cmd.append("--no-git")
            rc = run_cmd(cmd, ROOT_DIR)
            if rc != 0:
                return rc
        if shutil.which("bandit"):
            return run_cmd(["bandit", "-r", "src", "-ll"], BACKEND_DIR)
        return 0

    if stage == "test":
        cmd = [py, "-m", "pytest", "--cov=src", "--cov-report=term-missing"]
        if coverage_fail_under > 0:
            cmd.append(f"--cov-fail-under={coverage_fail_under}")
        return run_cmd(cmd, BACKEND_DIR)

    if stage == "build":
        return run_cmd([py, "-c", "from src.presentation.main import app; assert app is not None"], BACKEND_DIR)

    if stage == "clean":
        for folder in (".pytest_cache", ".ruff_cache", ".mypy_cache", "htmlcov"):
            target = BACKEND_DIR / folder
            if target.exists():
                shutil.rmtree(target, ignore_errors=True)
        return 0

    raise ValueError(f"Unsupported stage for python: {stage}")


def run_typescript(stage: str) -> int:
    npx = _node_bin("npx")
    if stage == "lint":
        return run_cmd([npx, "eslint", "src/types", "src/services"], FRONTEND_DIR)
    if stage == "validate":
        rc = run_cmd([npx, "next", "typegen"], FRONTEND_DIR)
        return rc or run_cmd([npx, "tsc", "--noEmit"], FRONTEND_DIR)
    if stage == "security":
        tsconfig = json.loads((FRONTEND_DIR / "tsconfig.json").read_text(encoding="utf-8"))
        if not tsconfig.get("compilerOptions", {}).get("strict"):
            print("[clean_workspace] TypeScript strict mode deve estar habilitado em tsconfig.json.")
            return 1
        return 0
    if stage == "test":
        return run_cmd([npx, "tsc", "--noEmit", "--noUnusedLocals"], FRONTEND_DIR)
    if stage == "build":
        rc = run_cmd([npx, "next", "typegen"], FRONTEND_DIR)
        return rc or run_cmd([npx, "tsc", "--noEmit", "--incremental", "false"], FRONTEND_DIR)
    return 0


def run_react(stage: str) -> int:
    npx = _node_bin("npx")
    components = sorted((FRONTEND_DIR / "src" / "components").glob("*.tsx"))
    if stage == "lint":
        return run_cmd([npx, "eslint", "src/components", "src/app"], FRONTEND_DIR)
    if stage == "validate":
        for comp in components:
            if '"use client"' not in comp.read_text(encoding="utf-8"):
                print(f"[clean_workspace] Diretiva 'use client' ausente em {comp.name}.")
                return 1
        return 0
    if stage == "security":
        for comp in components:
            if "dangerouslySetInnerHTML" in comp.read_text(encoding="utf-8"):
                print(f"[clean_workspace] Uso inseguro de dangerouslySetInnerHTML em {comp.name}.")
                return 1
        return 0
    if stage == "test":
        for comp in components:
            text = comp.read_text(encoding="utf-8")
            if "export function " not in text:
                print(f"[clean_workspace] Componente sem export nomeado: {comp.name}")
                return 1
        return 0
    if stage == "build":
        return run_cmd([npx, "tsc", "--noEmit"], FRONTEND_DIR)
    return 0


def run_nextjs(stage: str) -> int:
    npm = _node_bin("npm")
    npx = _node_bin("npx")
    if stage == "lint":
        return run_cmd([npm, "run", "lint"], FRONTEND_DIR)
    if stage == "validate":
        next_cfg = (FRONTEND_DIR / "next.config.ts").read_text(encoding="utf-8")
        if 'output: "standalone"' not in next_cfg:
            print("[clean_workspace] next.config.ts deve conter output: 'standalone'.")
            return 1
        return 0
    if stage == "security":
        return run_cmd([npm, "audit", "--omit=dev", "--audit-level=high"], FRONTEND_DIR)
    if stage == "test":
        return run_cmd([npx, "next", "typegen"], FRONTEND_DIR)
    if stage == "build":
        return run_cmd([npm, "run", "build"], FRONTEND_DIR)
    if stage == "clean":
        next_dir = FRONTEND_DIR / ".next"
        if next_dir.exists():
            shutil.rmtree(next_dir, ignore_errors=True)
        return 0
    return 0


def run_tailwind(stage: str) -> int:
    globals_css = FRONTEND_DIR / "src" / "app" / "globals.css"
    next_config = FRONTEND_DIR / "next.config.ts"
    if stage == "lint":
        if not globals_css.exists():
            return 1
        if '@import "tailwindcss"' not in globals_css.read_text(encoding="utf-8"):
            print("[clean_workspace] @import 'tailwindcss' ausente em globals.css.")
            return 1
        return 0
    if stage == "validate":
        if "@tailwindcss/turbopack" not in next_config.read_text(encoding="utf-8"):
            print("[clean_workspace] Loader @tailwindcss/turbopack ausente em next.config.ts.")
            return 1
        return 0
    if stage == "security":
        if "http://" in globals_css.read_text(encoding="utf-8"):
            print("[clean_workspace] URL HTTP insegura detectada em globals.css.")
            return 1
        return 0
    if stage == "test":
        tsx_files = list((FRONTEND_DIR / "src").rglob("*.tsx"))
        if not any("className=" in f.read_text(encoding="utf-8") for f in tsx_files):
            print("[clean_workspace] Nenhuma classe utilitaria Tailwind encontrada em src/*.tsx.")
            return 1
        return 0
    if stage == "build":
        css_dir = FRONTEND_DIR / ".next" / "static"
        if not css_dir.exists():
            return run_cmd([_node_bin("npm"), "run", "build"], FRONTEND_DIR)
        return 0
    return 0


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
                return 1
        return 0
    if stage == "validate":
        if shutil.which("docker"):
            return run_cmd(["docker", "compose", "config", "--quiet"], ROOT_DIR)
        return 0
    if stage == "security":
        if shutil.which("trivy"):
            return run_cmd(["trivy", "config", "--severity", "HIGH,CRITICAL", "."], ROOT_DIR)
        for df in dockerfiles:
            content = df.read_text(encoding="utf-8")
            if _SENSITIVE_KEY_RE.search(content):
                print(f"[clean_workspace] Possivel segredo hardcoded em {df}.")
                return 1
        return 0
    if stage == "test":
        for df in dockerfiles:
            content = df.read_text(encoding="utf-8")
            if "tini" not in content or "USER " not in content or "HEALTHCHECK " not in content:
                print(f"[clean_workspace] Requisitos seniores ausentes em {df}.")
                return 1
        return 0
    if stage == "build":
        if shutil.which("docker"):
            return run_cmd(["docker", "compose", "build"], ROOT_DIR)
        return 0
    return 0


def run_shell(stage: str) -> int:
    scripts = iter_project_files(".sh")
    rel_scripts = [s.relative_to(ROOT_DIR).as_posix() for s in scripts]
    if not rel_scripts:
        return 0
    if stage == "lint":
        if shutil.which("shellcheck"):
            return run_cmd(["shellcheck", *rel_scripts], ROOT_DIR)
        if shutil.which("bash"):
            for s in rel_scripts:
                rc = run_cmd(["bash", "-n", s], ROOT_DIR)
                if rc != 0:
                    return rc
        return 0
    if stage == "validate":
        for s in scripts:
            if "set -euo pipefail" not in s.read_text(encoding="utf-8"):
                print(f"[clean_workspace] 'set -euo pipefail' ausente em {s.name}.")
                return 1
        return 0
    if stage == "security":
        for s in scripts:
            if _SENSITIVE_KEY_RE.search(s.read_text(encoding="utf-8")):
                print(f"[clean_workspace] Possivel segredo em {s.name}.")
                return 1
        return 0
    if stage in {"test", "build"}:
        if shutil.which("bash"):
            for s in rel_scripts:
                rc = run_cmd(["bash", "-n", s], ROOT_DIR)
                if rc != 0:
                    return rc
        return 0
    return 0


def run_json(stage: str) -> int:
    files = [f for f in iter_project_files(".json") if f.name != "tsconfig.json"]
    if stage in {"lint", "validate", "build"}:
        for f in files:
            try:
                json.loads(f.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                print(f"[clean_workspace] JSON invalido em {f}: {exc}")
                return 1
        return 0
    if stage == "security":
        for f in files:
            if _SENSITIVE_KEY_RE.search(f.read_text(encoding="utf-8")):
                print(f"[clean_workspace] Possivel segredo em {f}.")
                return 1
        return 0
    if stage == "test":
        pkg = json.loads((FRONTEND_DIR / "package.json").read_text(encoding="utf-8"))
        if "build" not in pkg.get("scripts", {}) or "lint" not in pkg.get("scripts", {}):
            print("[clean_workspace] Scripts obrigatorios ausentes em frontend/package.json.")
            return 1
        return 0
    return 0


def run_yaml(stage: str) -> int:
    files = iter_project_files(".yml", ".yaml")
    rel_files = [f.relative_to(ROOT_DIR).as_posix() for f in files]
    py = resolve_backend_python()
    if stage == "lint":
        if shutil.which("yamllint"):
            return run_cmd(["yamllint", "-c", ".yamllint.yaml", *rel_files], ROOT_DIR)
        stage = "validate"
    if stage in {"validate", "build"}:
        for rel_path in rel_files:
            rc = run_cmd(
                [py, "-c", "import sys, yaml; yaml.safe_load(open(sys.argv[1], encoding='utf-8'))", rel_path],
                ROOT_DIR,
            )
            if rc != 0:
                return rc
        return 0
    if stage == "security":
        for f in files:
            if _SENSITIVE_KEY_RE.search(f.read_text(encoding="utf-8")):
                print(f"[clean_workspace] Possivel segredo em {f}.")
                return 1
        return 0
    if stage == "test":
        ci_text = (ROOT_DIR / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        if "jobs:" not in ci_text:
            return 1
        return 0
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Bidirectional Clean Workspace & CI/CD Runner")
    parser.add_argument(
        "--area",
        required=True,
        choices=[
            "python",
            "typescript",
            "react",
            "nextjs",
            "tailwind",
            "docker",
            "shell",
            "json",
            "yaml",
            "all",
        ],
    )
    parser.add_argument(
        "--stage",
        required=True,
        choices=["lint", "validate", "security", "test", "build", "clean"],
    )
    parser.add_argument("--coverage-fail-under", type=int, default=100)
    args = parser.parse_args()

    dispatch = {
        "python": lambda: run_python(args.stage, args.coverage_fail_under),
        "typescript": lambda: run_typescript(args.stage),
        "react": lambda: run_react(args.stage),
        "nextjs": lambda: run_nextjs(args.stage),
        "tailwind": lambda: run_tailwind(args.stage),
        "docker": lambda: run_docker(args.stage),
        "shell": lambda: run_shell(args.stage),
        "json": lambda: run_json(args.stage),
        "yaml": lambda: run_yaml(args.stage),
    }

    if args.area == "all" and args.stage == "clean":
        return run_python("clean", args.coverage_fail_under) or run_nextjs("clean")

    return dispatch[args.area]()


if __name__ == "__main__":
    raise SystemExit(main())
