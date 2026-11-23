import tempfile
import unittest
from pathlib import Path

from limpyo import organizer
from limpyo.categories import category_for
from limpyo.cli import main


def make(folder: Path, *names: str) -> None:
    for name in names:
        (folder / name).write_text(name, encoding="utf-8")


class CategoryTests(unittest.TestCase):
    def test_known_extension(self):
        self.assertEqual(category_for(Path("photo.JPG")), "Images")

    def test_unknown_extension_falls_back(self):
        self.assertEqual(category_for(Path("data.xyz")), "Others")
        self.assertEqual(category_for(Path("README")), "Others")


class OrganizerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_plan_does_not_touch_disk(self):
        make(self.folder, "a.png", "b.pdf")
        moves = organizer.plan(self.folder)
        self.assertEqual(len(moves), 2)
        self.assertTrue((self.folder / "a.png").exists())
        self.assertFalse((self.folder / "Images").exists())

    def test_apply_moves_files(self):
        make(self.folder, "a.png", "b.pdf", "c.zip")
        organizer.apply(self.folder, organizer.plan(self.folder))
        self.assertTrue((self.folder / "Images" / "a.png").exists())
        self.assertTrue((self.folder / "Documents" / "b.pdf").exists())
        self.assertTrue((self.folder / "Archives" / "c.zip").exists())

    def test_hidden_files_and_folders_are_skipped(self):
        make(self.folder, ".secret.txt", "ok.txt")
        (self.folder / "subdir").mkdir()
        moves = organizer.plan(self.folder)
        self.assertEqual([m.src for m in moves], ["ok.txt"])

    def test_name_collision_never_overwrites(self):
        (self.folder / "Images").mkdir()
        make(self.folder / "Images", "a.png")
        make(self.folder, "a.png")
        organizer.apply(self.folder, organizer.plan(self.folder))
        self.assertTrue((self.folder / "Images" / "a.png").exists())
        self.assertTrue((self.folder / "Images" / "a (1).png").exists())

    def test_undo_restores_and_cleans_up(self):
        make(self.folder, "a.png", "b.pdf")
        organizer.apply(self.folder, organizer.plan(self.folder))
        restored, warnings = organizer.undo(self.folder)
        self.assertEqual(restored, 2)
        self.assertEqual(warnings, [])
        self.assertTrue((self.folder / "a.png").exists())
        self.assertFalse((self.folder / "Images").exists())
        self.assertFalse((self.folder / organizer.HISTORY_FILE).exists())

    def test_undo_with_no_history(self):
        restored, warnings = organizer.undo(self.folder)
        self.assertEqual(restored, 0)
        self.assertTrue(warnings)

    def test_plan_rejects_missing_folder(self):
        with self.assertRaises(NotADirectoryError):
            organizer.plan(self.folder / "nope")


class CliTests(unittest.TestCase):
    def test_dry_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            make(folder, "a.png")
            self.assertEqual(main(["organize", "--dry-run", str(folder)]), 0)
            self.assertTrue((folder / "a.png").exists())

    def test_organize_then_undo(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            make(folder, "a.mp3")
            self.assertEqual(main(["organize", str(folder)]), 0)
            self.assertTrue((folder / "Audio" / "a.mp3").exists())
            self.assertEqual(main(["undo", str(folder)]), 0)
            self.assertTrue((folder / "a.mp3").exists())

    def test_bad_folder_returns_error(self):
        self.assertEqual(main(["scan", "/definitely/not/here"]), 1)


if __name__ == "__main__":
    unittest.main()
