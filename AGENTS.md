# Agent Guidelines

## Code Formatting

All code changes must be formatted before committing.

### TypeScript / JavaScript

Prettier: single quotes, no semicolons, print width 100.

```bash
pnpm run format          # format all JS files
pnpm run format:check    # check without writing
```

### Python

Black (line-length 100) + Ruff lint.

```bash
pnpm run format:py       # format with black
pnpm run lint:py         # lint with ruff
```

Or directly:

```bash
black --line-length 100 skills/xhs-note-creator/scripts/
ruff check skills/xhs-note-creator/scripts/
```

### Lint All

```bash
pnpm run check           # runs format:check + lint + lint:py
```
