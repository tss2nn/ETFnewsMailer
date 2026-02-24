# Development Standards

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) for all Python code
- Use type hints on all function signatures (e.g. `def foo(x: str) -> list[str]:`)
- Keep functions single-purpose; each function in `main.py` handles exactly one stage of the pipeline
- Use f-strings for string formatting
- Constants in `UPPER_SNAKE_CASE` at module level; local variables in `lower_snake_case`
- Format with `black` and lint with `flake8` before committing:
  ```bash
  pip install black flake8
  black main.py
  flake8 main.py
  ```

## Version Control

- Branch naming: `feature/short-description`, `fix/short-description`
- Commit messages: imperative mood, present tense ("Add ticker validation" not "Added ticker validation")
- One logical change per commit — don't bundle unrelated changes
- Never commit `.env`, credentials, or secrets; verify `.gitignore` covers them before staging

## Testing

- Use `pytest` for all tests:
  ```bash
  pip install pytest
  pytest
  ```
- Unit test each pipeline function in isolation using mocks for external calls (`feedparser.parse`, `smtplib.SMTP_SSL`)
- At minimum, test: valid/invalid ticker parsing, empty `tickers.txt`, missing env vars, malformed RSS feed responses
- Tests live in `tests/test_main.py`

## Documentation

- Keep `README.md` accurate — update it any time the CLI interface, configuration, or scheduling instructions change
- `CLAUDE.md` documents architecture for AI-assisted development; update it when the pipeline stages change
- Inline comments only where logic is non-obvious; avoid restating what the code already says clearly

## Code Review

- All changes go through a pull request — no direct commits to `main`
- PR description must state: what changed, why, and how to test it
- Reviewer checks: correctness, no secrets in code, type hints present, README/CLAUDE.md updated if needed
- Squash-merge PRs to keep `main` history clean

## CI/CD

- Run `black --check` and `flake8` in CI on every PR
- Run `pytest` in CI; PRs cannot merge with failing tests
- Cron scheduling is managed locally via `crontab` — there is no deployment pipeline
- Suggested GitHub Actions workflow triggers: `push` to any branch, `pull_request` to `main`

## Security

- Credentials (`GMAIL_APP_PASS`) are stored only in `.env`, which is gitignored
- Use Gmail App Passwords only — never store the account password
- Rotate the App Password immediately if it is ever exposed
- Do not log or print credential values anywhere in the code
- `tickers.txt` input is validated against `^[A-Z]{1,5}$` before use — maintain this validation for any new input sources
