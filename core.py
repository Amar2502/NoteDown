from config import get_notes_dir
from pathlib import Path
from datetime import datetime

from controller.get_text import get_text_note
from controller.get_image import get_latest_screenshot
from controller.get_audio import toggle_audio

current_session = None


# 🔹 Helper
def sanitize_filename(name: str) -> str:
    return name.strip().replace(" ", "-").lower()


def start_session(name, folder=""):
    global current_session

    if not name:
        print("❌ Provide session name")
        return

    safe_name = sanitize_filename(name)

    # 🔥 Folder handling
    notes_dir = get_notes_dir()
    folder_path = Path(notes_dir) / folder if folder else Path(notes_dir)
    folder_path.mkdir(parents=True, exist_ok=True)

    # 🔥 File path
    path = folder_path / f"{safe_name}.md"

    # 🔥 If file exists → continue session
    if path.exists():
        print(f"🔁 Continuing existing session: {path}")
        current_session = path
        return

    # 🔥 Create new file
    today = datetime.now().strftime("%Y-%m-%d")

    content = f"""---
title: {name}
date: {today}
tags: []
---

"""

    path.write_text(content, encoding="utf-8")

    current_session = path
    print(f"🚀 Started new session: {path}")

def end_session():
    global current_session

    if not current_session:
        print("❌ No session to end")
        return

    print(f"🏁 Ended session: {current_session.name}")
    current_session = None

def save_note(note):
    global current_session

    if not current_session:
        print("❌ No session to save note")
        return

    if not note:
        return

    path = current_session

    content = ""
    if path.exists():
        content = path.read_text(encoding="utf-8")

    with open(path, "a", encoding="utf-8") as f:

        # Add main heading if missing
        if "# Session Notes" not in content:
            f.write("\n# Session Notes\n")

        # ---- TEXT ----
        if note["type"] == "text":
            if "## 📝 Notes" not in content:
                if content.strip():
                    f.write("\n***\n")
                    f.write("```")
            f.write(f"- {note['text'].strip()}\n")
            f.write("```")

        # ---- IMAGE ----
        elif note["type"] == "image":
            if "## 📸 Screenshots" not in content:
                if content.strip():
                    f.write("\n***\n")
            f.write(f"![[{note['filename']}]]")

        # ---- AUDIO ----
        elif note["type"] == "audio":
            if "## 🎤 Audio" not in content:
                if content.strip():
                    f.write("\n***\n")
            f.write(f"![[{note['filename']}]]")

        f.write("\n")

    print(f"✅ Saved note: {note['type']}")


def handle_text():
    save_note(get_text_note())


def handle_image():
    save_note(get_latest_screenshot())


def handle_audio():
    note = toggle_audio()

    if note:
        save_note(note)