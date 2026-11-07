"""Command-line interface for envkeycheck."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import compare_key_sets, parse_env_keys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envkeycheck",
        description="Compare variable names in dotenv-style files without displaying values.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="two or more dotenv-style files; the first file is the reference",
    )
    return parser


def _read_keys(path: Path) -> set[str] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"envkeycheck: {path}: {exc}", file=sys.stderr)
        return None

    keys, invalid_lines = parse_env_keys(text)
    if invalid_lines:
        for line_number in invalid_lines:
            print(f"{path}:{line_number}: invalid assignment line", file=sys.stderr)
        return None
    return keys


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if len(args.files) < 2:
        build_parser().error("provide at least two files to compare")

    paths = [Path(name) for name in args.files]
    key_sets: list[set[str]] = []
    for path in paths:
        keys = _read_keys(path)
        if keys is None:
            return 2
        key_sets.append(keys)

    reference_path = paths[0]
    reference_keys = key_sets[0]
    has_mismatch = False
    for path, candidate_keys in zip(paths[1:], key_sets[1:]):
        missing, extra = compare_key_sets(reference_keys, candidate_keys)
        if not missing and not extra:
            print(f"{path}: keys match {reference_path}")
            continue

        has_mismatch = True
        details = []
        if missing:
            details.append("missing: " + ", ".join(sorted(missing)))
        if extra:
            details.append("extra: " + ", ".join(sorted(extra)))
        print(f"{path}: " + "; ".join(details))

    return 1 if has_mismatch else 0
