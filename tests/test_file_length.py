"""
test_file_length.py
===================
Enforce a 500-line hard cap on every tracked source file in the project.

Rationale: files longer than ~500 lines are a forcing function for poor
separation of concerns — components become monoliths, modules accumulate
unrelated logic, and AI-assisted navigation degrades. Fail fast here so
the issue is caught at commit time, not during code review.

Scope
-----
- Python  : backend/**/*.py, tests/**/*.py, main.py
- Vue SFC : frontend/src/**/*.vue
- TypeScript: frontend/src/**/*.ts  (excluding generated .d.ts)

Exclusions (legitimate long files)
-----------------------------------
- uv.lock, pnpm-lock.yaml  — generated, not authored
- frontend/dist/**          — build output
- .venv/**                  — dependencies
- node_modules/**           — dependencies
- .agents/**                — third-party skill data files
"""

from __future__ import annotations

import pathlib
from typing import Iterator

import pytest

# ── Constants ─────────────────────────────────────────────────────────────
REPO_ROOT = pathlib.Path(__file__).parent.parent
MAX_LINES = 500

# Glob patterns relative to REPO_ROOT that define which files are checked
SOURCE_GLOBS: list[str] = [
    "main.py",
    "backend/**/*.py",
    "tests/**/*.py",
    "frontend/src/**/*.vue",
    "frontend/src/**/*.ts",
]

# Sub-paths to skip (checked against the relative path string)
SKIP_PREFIXES: tuple[str, ...] = (
    ".venv",
    "node_modules",
    "frontend/dist",
    ".agents",
)
SKIP_SUFFIXES: tuple[str, ...] = (
    ".d.ts",  # TypeScript declaration files are generated
)


# ── Helpers ───────────────────────────────────────────────────────────────

def _iter_source_files() -> Iterator[pathlib.Path]:
    """Yield every source file matched by SOURCE_GLOBS, minus exclusions."""
    seen: set[pathlib.Path] = set()
    for pattern in SOURCE_GLOBS:
        for path in REPO_ROOT.glob(pattern):
            if not path.is_file():
                continue
            rel = path.relative_to(REPO_ROOT)
            rel_str = rel.as_posix()
            if any(rel_str.startswith(p) for p in SKIP_PREFIXES):
                continue
            if any(rel_str.endswith(s) for s in SKIP_SUFFIXES):
                continue
            if path not in seen:
                seen.add(path)
                yield path


def _count_lines(path: pathlib.Path) -> int:
    """Return the number of lines in *path* (empty file = 0)."""
    try:
        return sum(1 for _ in path.open(encoding="utf-8", errors="replace"))
    except OSError:
        return 0


# ── Parametrised test ─────────────────────────────────────────────────────

def _source_file_ids() -> list[pathlib.Path]:
    return sorted(_iter_source_files())


@pytest.mark.parametrize("source_file", _source_file_ids(), ids=lambda p: p.relative_to(REPO_ROOT).as_posix())
def test_file_does_not_exceed_max_lines(source_file: pathlib.Path) -> None:
    """Each source file must be ≤ 500 lines.

    If this test fails, split the file into smaller, single-responsibility
    modules / components before merging.
    """
    line_count = _count_lines(source_file)
    rel = source_file.relative_to(REPO_ROOT).as_posix()
    assert line_count <= MAX_LINES, (
        f"\n\n  ❌  {rel}  has  {line_count}  lines  (limit: {MAX_LINES})\n"
        f"  Split this file into smaller modules before committing.\n"
    )
