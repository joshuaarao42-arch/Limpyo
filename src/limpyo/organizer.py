"""Core logic: plan moves, apply them, and undo them."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from limpyo.categories import category_for

HISTORY_FILE = ".limpyo_history.json"


@dataclass(frozen=True)
class Move:
    """A single planned file move. Paths are relative to the organized folder."""

    src: str
    dst: str


def unique_path(path: Path) -> Path:
    """Return `path`, or 'name (1).ext', 'name (2).ext'... if it already exists."""
    if not path.exists():
        return path
    n = 1
    while True:
        candidate = path.with_name(f"{path.stem} ({n}){path.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def plan(folder: Path) -> list[Move]:
    """Plan moves for the top-level files in `folder`.

    Hidden files, subfolders, symlinks and Limpyo's own history file are left alone.
    Nothing is touched on disk.
    """
    folder = Path(folder)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")

    moves: list[Move] = []
    taken: set[Path] = set()
    for item in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
        if item.name.startswith(".") or item.name == HISTORY_FILE:
            continue
        if item.is_symlink() or not item.is_file():
            continue
        target_dir = folder / category_for(item)
        target = unique_path(target_dir / item.name)
        while target in taken:
            target = target.with_name(f"{target.stem} (x){target.suffix}")
            target = unique_path(target)
        taken.add(target)
        moves.append(Move(item.name, str(target.relative_to(folder))))
    return moves


def apply(folder: Path, moves: list[Move]) -> int:
    """Perform moves transactionally and record them for undo.

    If a move fails, already-moved files are restored before the error is re-raised.
    """
    folder = Path(folder)
    done: list[Move] = []
    try:
        for move in moves:
            src, dst = folder / move.src, folder / move.dst
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            done.append(move)
    except Exception:
        # Do not leave a half-organized folder without a matching undo record.
        for move in reversed(done):
            src, dst = folder / move.src, folder / move.dst
            if dst.exists():
                src.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dst), str(src))
            try:
                dst.parent.rmdir()
            except OSError:
                pass
        raise
    if done:
        _append_history(folder, done)
    return len(done)


def undo(folder: Path) -> tuple[int, list[str]]:
    """Reverse the most recent run. Returns (restored_count, warnings)."""
    folder = Path(folder)
    runs = _read_history(folder)
    if not runs:
        return 0, ["Nothing to undo."]

    run = runs.pop()
    restored, warnings = 0, []
    for entry in reversed(run["moves"]):
        src, dst = folder / entry["src"], folder / entry["dst"]
        if not dst.exists():
            warnings.append(f"Missing, skipped: {entry['dst']}")
            continue
        target = unique_path(src)
        shutil.move(str(dst), str(target))
        restored += 1
        try:
            dst.parent.rmdir()
        except OSError:
            pass
    _write_history(folder, runs)
    return restored, warnings


def summarize(moves: list[Move]) -> dict[str, int]:
    """Count planned moves per category folder."""
    counts: dict[str, int] = {}
    for move in moves:
        category = Path(move.dst).parent.name
        counts[category] = counts.get(category, 0) + 1
    return dict(sorted(counts.items()))


def _read_history(folder: Path) -> list[dict]:
    path = folder / HISTORY_FILE
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _write_history(folder: Path, runs: list[dict]) -> None:
    path = folder / HISTORY_FILE
    if runs:
        path.write_text(json.dumps(runs, indent=2), encoding="utf-8")
    elif path.exists():
        path.unlink()


def _append_history(folder: Path, moves: list[Move]) -> None:
    runs = _read_history(folder)
    runs.append(
        {
            "time": datetime.now().isoformat(timespec="seconds"),
            "moves": [{"src": m.src, "dst": m.dst} for m in moves],
        }
    )
    _write_history(folder, runs)
