import shutil
from config import SCREENSHOT_DIR, IMAGE_DIR
from pathlib import Path

Path(IMAGE_DIR).mkdir(parents=True, exist_ok=True)

def get_latest_screenshot():

    try:
        if not SCREENSHOT_DIR.exists():
            print(f"⚠️ Screenshot folder not found: {SCREENSHOT_DIR}")
            return None

        image_files = [f for f in SCREENSHOT_DIR.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg")]
        if not image_files:
            print("⚠️ No screenshots found")
            return None

        latest_file = max(image_files, key=lambda f: f.stat().st_ctime)
        filename = latest_file.name.replace(" ", "_")
        destination_path = Path(IMAGE_DIR) / filename

        if not destination_path.exists():
            shutil.copy(latest_file, destination_path)

        return {
            "type": "image",
            "path": destination_path
        }

    except Exception as e:
        print(f"❌ from get_image.py Error: {e}")
        return None

