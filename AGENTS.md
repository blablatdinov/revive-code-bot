# AGENTS.md

## Commands

- **Run tests:** `poetry run pytest src -m 'not integration' -vv` (or `task tests`)
- **Run a single test:** `cd src && poetry run pytest <path>` (or `task test -- <path>`)
- **Coverage:** CI runs `pytest -m 'not integration' --doctest-modules --cov --cov-report xml`
- **Lint:** `poetry run ruff check src --output-format=concise && poetry run flake8 src && poetry run mypy src` (or `task lint`)
- **Type check:** `poetry run mypy src` (or `task type-check`)
  - Local mypy with in-memory DB: `DATABASE_URL=sqlite:///:memory: poetry run mypy src/ --show-traceback`
- **Format:** `poetry run ruff check src --fix --fix-only` (or `task fmt`)
- **Syntax check:** `poetry run ruff check src --select=F --ignore=F401,F841` (or `task syntax-check`)
- **Migrations:** `poetry run python src/manage.py makemigrations && poetry run python src/manage.py migrate` (or `task migrate`)
- **Django shell:** `poetry run python src/manage.py shell_plus` (or `task shell`)
- **Docker (dev):** `task compose-setup` -> `task compose-run` -> `task compose-tests` / `task compose-lint`
- **Commits:** Use the `git-authoring` skill for commit messages, PR titles/descriptions, branch naming, and all git operations (rebasing, cherry-picking, squashing, etc.)

## Conventions

- Python 3.14, Django 6.1, PostgreSQL (psycopg), Poetry package manager
- Line length: 120
- Quote style: single quotes for inline strings, double for docstrings/multiline
- Ruff rules: `ALL` with specific ignores (see `pyproject.toml`)
- External linter: wemake-python-styleguide (WPS rules via flake8, `setup.cfg`)
- Refurb linter (ignore rule 184)
- mypy with django-stubs plugin, settings module: `config.settings`, `mypy_path = "src"`
- **No f-strings** — use `.format()` instead (enforced via `FLY002`, `UP032` ignores)
- **No `noqa` comments** — fix the underlying linter issue instead. If a rule is genuinely a false positive, flag it to the user rather than suppressing
- SPDX license headers (`SPDX-FileCopyrightText` + `SPDX-License-Identifier: MIT`) at the top of every source file — enforced by flake8 `copyright-check`
- Every Python file begins with a module docstring
- `@final` decorator on Django model classes
- All imports at the top of the file — never inside functions
- No comments in code unless explicitly requested
- Migrations excluded from linting (`D100`, `CPY001`, `D101`, `RUF012` ignored)
- `max-args = 6` (ruff pylint + flake8)
- `USE_I18N = True`, `TIME_ZONE = 'UTC'`, `LANGUAGE_CODE = 'en-us'`

## Testing

- pytest + pytest-django, pytest-cov, pytest-randomly, time-machine, requests-mock, model-bakery, django-test-migrations
- Django settings module: `config.settings`
- Tests in `src/tests/`, mirroring `src/main/` structure
- Integration tests marked with `@pytest.mark.integration` — excluded from default runs
- Fixtures in `src/tests/conftest.py`: `anon` (Django test Client), `baker` (model-bakery), `mock_http` (requests_mock)
- GitHub webhook/API fixtures in `src/tests/fixtures/` (JSON files)
- Test factories use `model_bakery.baker.make(...)` (via `baker` fixture)
- Tests use `pytestmark = [pytest.mark.django_db]`
- Test files ignore: `S101`, `INP001`, `D`, `ANN`, `PLR2004`, `PLR0913`
- Fake ("Fk") implementations of GitHub-dependent classes (`FkClonedRepo`, `FkNewIssue`, `FkReviveConfig`, etc.) enable DB-less, network-less unit tests — always prefer fakes over mocking real GitHub API calls

## Architecture

- Single Django app `main` holds all domain logic (models, algorithms, services, views, management commands)
- **Protocol-based config layering** (`main/services/revive_config/`): `ReviveConfig` Protocol with implementations `DefaultReviveConfig`, `DiskReviveConfig`, `GhReviveConfig`, `PgReviveConfig`, `MergedConfig` — each with an `Fk` counterpart for tests
- **GitHub object abstractions** (`main/services/github_objs/`): `ClonedRepo`, `NewIssue`, `RepoInstallation`, `github_client` — real (`Gh*`) and fake (`Fk*`) implementations
- **Algorithms** (`main/algorithms.py`): git-based file-stagnation scoring (commit dates, blame, coverage XML parsing)
- **Background worker** (`main/management/commands/worker.py`): long-polling loop over `ProcessTask` rows (`pending` -> `in_process` -> `success`/`failed`)
- **Webhook handler** (`main/views/gh_webhook.py`): handles `installation_added`, `push`, `issue_edited` GitHub events
- Per-repo config via `.revive-code-bot.yml` in target repos (`cron`, `glob`, `limit`)

## CI

- **PR check** (`.github/workflows/pr-check.yml`): Python 3.14 + Poetry, PostgreSQL service, `pytest -m 'not integration' --doctest-modules --cov --cov-report xml`, ruff + mypy
- **Master** (`.github/workflows/master.yml`): same checks on push to `master`
- **Deploy** (`.github/workflows/deploy.yml`): on tag push — checks -> Docker build/push -> migrate -> SSH deploy

## 0pdd — Puzzle-Driven Development

- Keep task scope small: do exactly what was asked, nothing more
- When you encounter a problem that is out of scope of the current task, do NOT fix it immediately
- Instead, leave a puzzle comment in the code using the standard 0pdd format:
  ```
  @todo #<issue-number>:<time-estimate> <description>
  ```
- Puzzles are auto-parsed by 0pdd.com and turned into GitHub issues
- When closing a puzzle (issue resolved), remove the puzzle comment from code
- Never expand scope "while you're at it" — log it as a puzzle and move on
- Focus: one task = one change, committed cleanly

Example puzzle in code:

```python
# @todo #42:30min Extract validation logic into a separate service class.
#  Currently duplicated across three views.
```
