from config import NOTES_DIR
from pathlib import Path
from get_text import get_text_note
from get_image import get_latest_screenshot
from get_audio import toggle_audio

current_session = None


def start_session(name):
    global current_session

    if not name:
        print("❌ Provide session name")
        return

    Path(NOTES_DIR).mkdir(parents=True, exist_ok=True)

    path = Path(NOTES_DIR) / f"{name}.md"

    if path.exists():
        print(f"❌ Session already exists: {name}")
        return

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"## {name}\n\n")

    current_session = path
    print(f"🚀 Started session: {name}")


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
        return  # ✅ prevent crash

    path = current_session

    if note["type"] == "text":
        with open(path, "a", encoding="utf-8") as f:
            f.write("```\n")
            f.write(note["text"])
            f.write("\n```")
            f.write("\n\n")

    elif note["type"] == "image":   
        with open(path, "a", encoding="utf-8") as f:
            f.write(f'![Screenshot](..\{note["path"]})\n\n')

    elif note["type"] == "audio":
        with open(path, "a", encoding="utf-8") as f:
            f.write(f'<audio controls src="..\{note["path"]}"></audio>\n\n')

    print(f"✅ Saved note: {note['type']}")


def handle_text():
    save_note(get_text_note())


def handle_image():
    save_note(get_latest_screenshot())


def handle_audio():
    note = toggle_audio()

    # Only save when recording stops
    if note:
        save_note(note)