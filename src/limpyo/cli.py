"""Command-line interface for Limpyo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from limpyo import __version__, organizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="limpyo",
        description="Limpyo (Cebuano for 'clean'): sort a messy folder by file type, with undo.",
    )
    parser.add_argument("--version", action="version", version=f"limpyo {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="show what would be moved, without touching anything")
    scan.add_argument("folder", type=Path)

    org = sub.add_parser("organize", help="move files into category folders")
    org.add_argument("folder", type=Path)
    org.add_argument("-n", "--dry-run", action="store_true", help="preview only")

    und = sub.add_parser("undo", help="reverse the most recent organize run")
    und.add_argument("folder", type=Path)
    return parser


def _print_summary(moves: list[organizer.Move]) -> None:
    for category, count in organizer.summarize(moves).items():
        print(f"  {category:<14} {count}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        if args.command == "undo":
            restored, warnings = organizer.undo(args.folder)
            for warning in warnings:
                print(f"! {warning}")
            if restored:
                print(f"Gibalik: {restored} file(s) restored.")
            return 0

        moves = organizer.plan(args.folder)
        if not moves:
            print("Limpyo na! Nothing to organize.")
            return 0

        if args.command == "scan" or args.dry_run:
            print(f"{len(moves)} file(s) would be moved:")
            _print_summary(moves)
            for move in moves:
                print(f"  {move.src}  ->  {move.dst}")
            return 0

        count = organizer.apply(args.folder, moves)
        print(f"Limpyo na! {count} file(s) organized:")
        _print_summary(moves)
        print("Changed your mind? Run: limpyo undo", args.folder)
        return 0
    except (NotADirectoryError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
