from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path


def _rm_tree(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    dist_dir = repo_root / "dist"
    _rm_tree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)

    # Build a minimal app directory for packaging.
    with tempfile.TemporaryDirectory() as td:
        tmp_root = Path(td)
        app_dir = tmp_root / "app"
        app_dir.mkdir(parents=True, exist_ok=True)

        # Copy game sources.
        def _ignore(_dir: str, names: list[str]) -> set[str]:
            skip = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "save"}
            return {n for n in names if n in skip or n.endswith(".pyc")}

        shutil.copytree(repo_root / "game", app_dir / "game", dirs_exist_ok=True, ignore=_ignore)

        # Shared config for web build.
        cfg = repo_root / "config.toml"
        if cfg.exists():
            shutil.copy2(cfg, app_dir / "config.toml")

        # Startup script required by `pyxel package` must be under `app_dir`.
        startup = app_dir / "main.py"
        startup.write_text(
            "from game.app import run\n\n"
            "if __name__ == '__main__':\n"
            "    run()\n",
            encoding="utf-8",
        )

        # Create `.pyxapp` and then HTML via Pyxel's CLI functions.
        import pyxel.cli  # local import (Pyxel is optional for non-web usage)

        cwd = os.getcwd()
        try:
            os.chdir(tmp_root)
            pyxel.cli.package_pyxel_app(str(app_dir), str(startup))
        finally:
            os.chdir(cwd)

        pyxapp_path = tmp_root / "app.pyxapp"

        # Generate HTML (written to current working directory).
        cwd = os.getcwd()
        try:
            os.chdir(dist_dir)
            shutil.copy2(pyxapp_path, dist_dir / pyxapp_path.name)
            pyxel.cli.create_html_from_pyxel_app(pyxapp_path.name)
            html_path = dist_dir / "app.html"
            (dist_dir / "index.html").write_bytes(html_path.read_bytes())
            html_path.unlink()
            (dist_dir / pyxapp_path.name).unlink(missing_ok=True)
            (dist_dir / ".nojekyll").write_text("", encoding="utf-8")
        finally:
            os.chdir(cwd)


if __name__ == "__main__":
    main()
