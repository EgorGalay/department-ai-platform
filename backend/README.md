# Backend

FastAPI application built for Python 3.12. See the repository README for setup and run commands.

`requirements.txt` is generated from `pyproject.toml` and `uv.lock`; do not edit it by hand. To refresh it after changing dependencies in `pyproject.toml`, run from this directory:

```powershell
uv lock
uv export --frozen --no-dev --format requirements.txt --no-hashes --no-cache --output-file requirements.txt
```

For a pip-based runtime install from this directory, use `pip install -r requirements.txt`.

After applying migrations, create the first administrator with `uv run python -m department_ai.modules.identity.bootstrap_admin`. The command asks for the password interactively. Public self-registration is not enabled.
