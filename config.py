from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional, TypedDict


PROJECT_ROOT = Path(__file__).resolve().parent


class NoteDownPaths(TypedDict):
    vault_path: Path
    assets_path: Path
    screenshot_path: Path


def _config_dir() -> Path:
    appdata = os.environ.get("APPDATA") or str(Path.home())
    return Path(appdata) / "NoteDown"


def config_path() -> Path:
    return _config_dir() / "config.json"


def _default_paths() -> NoteDownPaths:
    # Safe-ish defaults; user should normally run setup to set these.
    vault = Path.home() / "Documents" / "Obsidian"
    return {
        "vault_path": vault,
        "assets_path": vault / "Assets",
        "screenshot_path": Path.home() / "Pictures" / "Screenshots",
    }


@lru_cache(maxsize=1)
def load_paths() -> NoteDownPaths:
    """
    Load NoteDown paths from `%APPDATA%/NoteDown/config.json`.
    Falls back to defaults if config is missing/invalid.
    """
    cfg = config_path()
    if not cfg.exists():
        return _default_paths()

    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
        vault = Path(data["vault_path"])
        assets = Path(data["assets_path"])
        screenshot = Path(data["screenshot_path"])
        return {
            "vault_path": vault,
            "assets_path": assets,
            "screenshot_path": screenshot,
        }
    except Exception:
        return _default_paths()


def reload_paths() -> NoteDownPaths:
    load_paths.cache_clear()
    return load_paths()


def get_obsidian_dir() -> Path:
    return load_paths()["vault_path"]


def get_notes_dir() -> Path:
    return load_paths()["vault_path"]


def get_assets_dir() -> Path:
    return load_paths()["assets_path"]


def get_screenshot_dir() -> Path:
    return load_paths()["screenshot_path"]