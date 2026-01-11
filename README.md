Setup python environment:

using uv (https://docs.astral.sh/uv/):
```
uv sync
```

Without:
```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install [dependencies that are in the pyproject.toml]
```
