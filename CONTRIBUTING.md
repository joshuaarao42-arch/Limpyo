# Contributing to Limpyo

Salamat for wanting to help! Bug reports, ideas, docs fixes, and code are all welcome.

## Ways to contribute

- **Report a bug:** open an issue with your OS, Python version, the command you ran,
  and what you expected vs. what happened.
- **Suggest a feature:** open an issue describing the problem first, before writing code.
- **Add a file type:** extend the map in `src/limpyo/categories.py` (and a test if it
  is a new category).
- **Improve the docs:** typo fixes and clearer examples are always appreciated.

## Development setup

```bash
git clone https://github.com/joshuaarao42-arch/limpyo.git
cd limpyo
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

Limpyo has no runtime dependencies, so please keep it that way unless there is a very
good reason.

## Running the tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

All tests must pass before you open a pull request.

## Pull request workflow

1. Fork the repo and create a branch: `git checkout -b feature/short-description`.
2. Make your change, with tests for new behavior or bug fixes.
3. Run the test suite.
4. Commit using a clear message in the imperative mood, such as
   `Add .heif to Images category`.
5. Push your branch and open a pull request describing **what** changed and **why**.

## Code guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/) and use type hints on new functions.
- Keep functions small and focused. Planning, moving, and the CLI stay separate.
- **Safety first:** Limpyo moves people's files. Anything that touches the filesystem
  must never overwrite or delete user data, and should be undoable.
- Test with temporary folders (`tempfile.TemporaryDirectory`), never real user folders.

## Be kind

Be respectful and constructive in issues and reviews. Everyone is learning.
