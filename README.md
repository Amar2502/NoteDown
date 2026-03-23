# Note Down

A tiny Windows hotkey-based CLI that saves your clipboard text, latest screenshot, and microphone recording into timestamped “sessions”.

## Features
- `Ctrl+T`: save clipboard text as Markdown (preserves formatting)
- `Ctrl+I`: save the latest screenshot from your OneDrive Screenshots folder
- `Ctrl+A`: start/stop audio recording (saves a `.wav` on stop)

## Setup
1. Create/activate a virtual environment (optional).
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage
Run:
```powershell
python cli_runner.py
```

Then use:
- `start <session_name>`: creates `notes/<session_name>.md`
- `end`: stops the current session
- `exit`: quits

## Where files go
- Notes: `notes/`
- Images: `assets/images/`
- Audio: `assets/audio/`
- Screenshots source (used by `Ctrl+I`): `~/OneDrive/Pictures/Screenshots`

