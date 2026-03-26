from config import NOTES_DIR
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
    if folder:
        folder_path = Path(NOTES_DIR) / folder
    else:
        folder_path = Path(NOTES_DIR)

    folder_path.mkdir(parents=True, exist_ok=True)

    # 🔥 File path
    path = folder_path / f"{safe_name}.md"

    # 🔥 Avoid overwrite
    counter = 1
    original_path = path
    while path.exists():
        path = original_path.with_name(f"{safe_name}-{counter}.md")
        counter += 1

    # 🔥 Create frontmatter
    today = datetime.now().strftime("%Y-%m-%d")

    content = f"""---
title: {name}
date: {today}
tags: []
---

"""

    path.write_text(content, encoding="utf-8")

    current_session = path
    print(f"🚀 Started session: {path}")


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

    with open(path, "a", encoding="utf-8") as f:

        # ---- TEXT ----
        if note["type"] == "text":
            f.write("```\n")
            f.write(note["text"])
            f.write("\n```\n\n")

        # ---- IMAGE ----
        elif note["type"] == "image":
            f.write(f'![Screenshot]({note["filename"]})\n\n')

        # ---- AUDIO ----
        elif note["type"] == "audio":
            f.write(f'<audio controls src="{note["filename"]}"></audio>\n\n')

    print(f"✅ Saved note: {note['type']}")


def handle_text():
    save_note(get_text_note())


def handle_image():
    save_note(get_latest_screenshot())


def handle_audio():
    note = toggle_audio()

    if note:
        save_note(note)