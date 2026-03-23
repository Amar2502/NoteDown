import core
import keyboard

NEON_BLUE = "\033[94m"
RESET_ALL = "\033[0m"


def register_hotkeys():
    actions = {
        "ctrl+t": core.handle_text,
        "ctrl+i": core.handle_image,
        "ctrl+a": core.handle_audio,
    }

    for hotkey, func in actions.items():
        keyboard.add_hotkey(hotkey, func, suppress=True)


def handle_command(command: str):
    parts = command.strip().split()

    if not parts:
        return

    cmd = parts[0].lower()

    if cmd == "start":
        if len(parts) < 2:
            print("❌ Usage: start <session_name>")
            return
        core.start_session(parts[1])

    elif cmd == "end":
        core.end_session()

    elif cmd == "exit":
        print("👋 Exiting...")
        exit()

    else:
        print("❌ Unknown command")


def main():
    print(f"{NEON_BLUE}Note Down CLI Runner{RESET_ALL}")

    print("\nCommands:")
    print("  start <session_name>")
    print("  end")
    print("  exit\n")

    print("Hotkeys:")
    print("  Ctrl+T → Save clipboard text (Markdown preserved)")
    print("  Ctrl+I → Save latest screenshot")
    print("  Ctrl+A → Toggle audio recording (start/stop)")
    print("  ESC → Exit\n")

    register_hotkeys()

    keyboard.add_hotkey("esc", lambda: exit(), suppress=True)

    while True:
        try:
            command = input(">> ")
            handle_command(command)
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break


if __name__ == "__main__":
    main()