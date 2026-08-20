.PHONY: test eval dist check wheel clean

PYTHON ?= python3


test:
	PYTHONPATH=src $(PYTHON) -m pytest -q


eval:
	PYTHONPATH=src $(PYTHON) -m prove_it --root . eval


dist:
	PYTHONPATH=src $(PYTHON) scripts/build_dist.py


check: test eval dist
	PYTHONPATH=src $(PYTHON) -m prove_it validate --prompt build/generated/PROVE_IT_MASTER_PROMPT.md --allow-placeholders


wheel: clean
	mkdir -p wheelhouse
	$(PYTHON) -c "from setuptools import build_meta; print(build_meta.build_wheel('wheelhouse'))"


clean:
	rm -rf build dist wheelhouse .pytest_cache src/*.egg-info src/*/*.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name '*.py[co]' -delete
