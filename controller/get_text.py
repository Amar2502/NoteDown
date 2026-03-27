import pyperclip


def clean_text(text: str) -> str:

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip("\n")


def get_text_note():
    text = pyperclip.paste()

    if not text or not text.strip():
        print("⚠️ No text found in clipboard")
        return None

    text = clean_text(text)

    return {
        "type": "text",
        "text": text
    }