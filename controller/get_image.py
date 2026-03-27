import shutil
from pathlib import Path
import sys

# Allow running this file directly (`python controller\get_image.py`).
# Without this, `config.py` in the project root may not be on `sys.path`.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import get_screenshot_dir, get_assets_dir

Path(get_assets_dir()).mkdir(parents=True, exist_ok=True)

def get_latest_screenshot():

    try:
        SCREENSHOT_DIR = get_screenshot_dir()
        ASSETS_DIR = get_assets_dir()
        if not SCREENSHOT_DIR.exists():
            print(f"⚠️ Screenshot folder not found: {SCREENSHOT_DIR}")
            return None

        image_files = [f for f in SCREENSHOT_DIR.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg")]
        if not image_files:
            print("⚠️ No screenshots found")
            return None

        latest_file = max(image_files, key=lambda f: f.stat().st_ctime)
        filename = latest_file.name.replace(" ", "_")
        destination_path = Path(ASSETS_DIR) / filename

        if not destination_path.exists():
            shutil.copy(latest_file, destination_path)

        return {
            "type": "image",
            "filename": filename
        }

    except Exception as e:
        print(f"❌ from get_image.py Error: {e}")
        return None

