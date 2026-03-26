from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import NOTES_DIR

def get_folders():
    all_folders = []

    for folder in NOTES_DIR.rglob("*"):
        if not folder.is_dir():
            continue

        if (
            folder.name == "Assets"
            or any(part.startswith(".obsidian") for part in folder.parts)
        ):
            continue

        all_folders.append(str(folder.relative_to(NOTES_DIR)))

    return sorted(all_folders)