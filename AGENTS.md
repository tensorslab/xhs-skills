# Agent Guidelines

## Architecture Requirements

* **一个文件做一件事**：遵循单一职责原则，确保代码清晰。
* **模块化**：通过模块化设计提高代码的可重用性和可维护性。

## Code Formatting

在修改代码或实现功能之后，必须进行代码格式化。

### TypeScript / JavaScript

Prettier: single quotes, no semicolons, print width 100.

```bash
pnpm run format
pnpm run format:check
```

### Python

Black (line-length 100) + Ruff lint.

```bash
pnpm run format:py
pnpm run lint:py
```

Or directly:

```bash
black --line-length 100 skills/xhs-note-creator/scripts/
ruff check skills/xhs-note-creator/scripts/
```

### Lint All

```bash
pnpm run check
```
