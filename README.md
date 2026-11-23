# Limpyo

> *Limpyo* is Cebuano for **"clean."**

Limpyo is a small command-line tool that tidies a messy folder (your Downloads, a
flash drive dump, a desktop full of screenshots) by sorting files into folders by
type. It previews before it moves anything, never overwrites a file, and can undo its
last run.

No dependencies. Just Python 3.9+.

## Features

- **Sorts by type** into `Images`, `Documents`, `Spreadsheets`, `Presentations`,
  `Videos`, `Audio`, `Archives`, `Code`, `Installers`, and `Others`.
- **Dry run** to see exactly what will happen first.
- **Undo** reverses the most recent run, and removes category folders it emptied.
- **Safe by default:** never overwrites (clashes become `name (1).ext`), and skips
  hidden files, subfolders, and symlinks.

## Install

```bash
git clone https://github.com/joshuaarao42-arch/limpyo.git
cd limpyo
pip install .
```

Or run it without installing:

```bash
PYTHONPATH=src python -m limpyo --help
```

## Usage

```bash
# Preview what would move (changes nothing)
limpyo scan ~/Downloads
limpyo organize --dry-run ~/Downloads

# Do it
limpyo organize ~/Downloads

# Changed your mind?
limpyo undo ~/Downloads
```

Example:

```text
$ limpyo organize ~/Downloads
Limpyo na! 6 file(s) organized:
  Archives       1
  Documents      2
  Images         3
Changed your mind? Run: limpyo undo /home/josh/Downloads
```

Each run is recorded in a hidden `.limpyo_history.json` inside the folder you
organized. That file is what powers `undo`.

## Project layout

```text
src/limpyo/
  categories.py   # extension -> category map
  organizer.py    # plan / apply / undo logic
  cli.py          # argparse command-line interface
tests/            # unittest suite
```

## Running the tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## License

[MIT](LICENSE) © 2026 Joshua C. Arao
