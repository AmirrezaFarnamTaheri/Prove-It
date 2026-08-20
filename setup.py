from __future__ import annotations

import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py


ROOT = Path(__file__).resolve().parent


class build_py(_build_py):
    """Build the wheel from canonical repository resources without committed mirrors."""

    def run(self) -> None:
        super().run()
        destination = Path(self.build_lib) / "prove_it" / "resources"
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True)
        (destination / "__init__.py").write_text(
            '"""Packaged Prove It protocol resources."""\n', encoding="utf-8"
        )

        shutil.copy2(ROOT / "manifest.json", destination / "manifest.json")
        shutil.copytree(ROOT / "adapters", destination / "adapters")
        shutil.copytree(ROOT / "skills" / "prove-it", destination / "skills" / "prove-it")
        shutil.copytree(ROOT / "evals" / "cases", destination / "evals" / "cases")


setup(cmdclass={"build_py": build_py})
