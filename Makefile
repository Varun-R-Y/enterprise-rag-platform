backend:
	cd backend && uv run uvicorn main:app --reload

test:
	cd backend && uv run pytest

lint:
	cd backend && uv run ruff check .

format:
	cd backend && uv run ruff format .
