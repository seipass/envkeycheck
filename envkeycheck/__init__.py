"""Compare environment-variable names without exposing their values."""

from __future__ import annotations

import re

__all__ = ["compare_key_sets", "parse_env_keys"]

_ASSIGNMENT = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=.*$")


def parse_env_keys(text: str) -> tuple[set[str], list[int]]:
    """Return variable names and line numbers that are not comments or assignments.

    Values are deliberately ignored and are never returned. This accepts simple
    KEY=value and export KEY=value lines; it does not evaluate shell syntax.
    """
    keys: set[str] = set()
    invalid_lines: list[int] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _ASSIGNMENT.fullmatch(line)
        if match:
            keys.add(match.group(1))
        else:
            invalid_lines.append(line_number)
    return keys, invalid_lines


def compare_key_sets(reference: set[str], candidate: set[str]) -> tuple[set[str], set[str]]:
    """Return (missing_from_candidate, extra_in_candidate)."""
    return reference - candidate, candidate - reference
