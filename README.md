# NoteDown

<p align="center">
  <b>⚡ Lightweight, always-on-top quick capture for Obsidian</b>
</p>

---


A lightweight, always-on-top **quick note** app for Windows built with **PyQt6**.  
It includes a first-run setup flow and stores your paths in `%APPDATA%\NoteDown\config.json`.

### Requirements

- Python 3.10+ (3.11/3.12 also fine)
- Windows 10/11

### Install

```bash
pip install -r requirements.txt
```

### Start

```bash
python start.py
```

## Build Windows `.exe` (PyInstaller)

### One command build (PowerShell)

Run this from the project root (the folder that contains `start.py` and `NoteDown.ico`):

```powershell
pyinstaller --noconfirm --clean --windowed --onefile --name "NoteDown" --icon "NoteDown.ico" "start.py" --add-data "ui_utils;ui_utils" --hidden-import "PyQt6.QtMultimedia" --hidden-import "PyQt6.QtMultimediaWidgets"
```

Your output will be in:

- `dist\NoteDown.exe`

## Project layout

- `start.py`: app launcher + first-run setup flow
- `ui.py`: main UI
- `config.py`: loads paths from `%APPDATA%\NoteDown\config.json`
- `ui_utils/`: SVG icons + setup video assets bundled into the app

## Where settings are stored

NoteDown reads/writes configuration here:

- `%APPDATA%\NoteDown\config.json`

1. Build the app to get `dist\NoteDown.exe`
2. On GitHub: **Releases → Draft a new release**
3. Attach `NoteDown.exe` as a **release asset**
4. Copy the “latest release” link into the **Download** section above

Licensed under the MIT License. See the LICENSE file for details.

