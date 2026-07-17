# Contributing to InsightAI

## Workflow
1. Fork and branch from `main` using `feature/<name>` or `fix/<name>`.
2. Write tests for all new code (unit + integration where applicable).
3. Run `scripts/lint_all.sh` and `scripts/run_tests.sh` before opening a PR.
4. Fill out the PR template completely, including test evidence.
5. At least one approving review is required before merge.

## Commit Convention
Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.

## Code Style
- Backend: black, isort, flake8, mypy (strict).
- Frontend: eslint + prettier, TypeScript strict mode.
- ML: black, isort, docstrings required on public functions.
