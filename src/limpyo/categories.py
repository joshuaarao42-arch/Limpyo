"""File-type categories used to decide where each file goes."""

from pathlib import Path

CATEGORIES: dict[str, set[str]] = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".heic", ".tiff"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt", ".epub"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".ods", ".tsv"},
    "Presentations": {".ppt", ".pptx", ".odp", ".key"},
    "Videos": {".mp4", ".mkv", ".mov", ".avi", ".wmv", ".webm", ".flv"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp", ".json", ".sql", ".sh"},
    "Installers": {".exe", ".msi", ".dmg", ".pkg", ".deb", ".apk"},
}

FALLBACK = "Others"

_EXT_TO_CATEGORY = {ext: name for name, exts in CATEGORIES.items() for ext in exts}


def category_for(path: Path) -> str:
    """Return the category folder name for a file, based on its extension."""
    return _EXT_TO_CATEGORY.get(path.suffix.lower(), FALLBACK)
