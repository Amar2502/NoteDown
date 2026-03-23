import pyperclip


def clean_text(text: str) -> str:
    """
    Preserve original formatting as much as possible.
    Only clean problematic whitespace.
    """

    # Normalize Windows/Mac line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove trailing spaces from each line
    lines = [line.rstrip() for line in text.split("\n")]

    # Rejoin exactly as-is
    text = "\n".join(lines)

    # Remove leading/trailing empty lines (but keep internal spacing)
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