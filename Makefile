run:
	# poetry run uvicorn src.app.main:app --reload --log-level=debug
	poetry run litestar --app src.app.main:app run -d

lint:
	poetry run isort src tests
	poetry run flake8 src tests

test:
	poetry run pytest
