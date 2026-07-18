# Tapo Event Bridge

Experimental Home Assistant custom integration focused on reliable, normalized
Tapo camera events.

> Current status: foundation only. This version creates a config entry and
> exposes safe diagnostics. It does not connect to cameras yet.

## Principles

- **Confirmed** — backed by documentation, protocol evidence, or reproducible tests.
- **Observed** — reproduced on the project camera lab.
- **Hypothesis** — plausible, but not yet proven.

## Development checks

```bash
uv sync --dev
uv run ruff check .
uv run pytest
```

## Test camera lab

C211, C220, C425, C520WS ×2, and C660.
