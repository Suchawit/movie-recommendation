.PHONY: install run test lint

install:
	uv sync

run:
	PYTHONPATH=src uv run uvicorn recommender.main:app --host 0.0.0.0 --port 8088

test:
	PYTHONPATH=src uv run python -m unittest discover -s tests -p "test_*.py"
