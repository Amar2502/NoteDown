from pathlib import Path
from datetime import datetime

SCREENSHOT_DIR = Path.home() / "OneDrive" / "Pictures" / "Screenshots"

IMAGE_DIR = "assets/images"
AUDIO_DIR = "assets/audio"
NOTES_DIR = "notes"

filename = Path(AUDIO_DIR) / f"audio_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.wav"

print(filename)