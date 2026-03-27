import pyaudio
import wave
from datetime import datetime
from pathlib import Path
import threading
import sys

# Allow running this file directly (`python controller\get_audio.py`).
# Without this, `config.py` in the project root may not be on `sys.path`.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import get_assets_dir

audio = pyaudio.PyAudio()

is_recording = False
stream = None
frames = []
lock = threading.Lock()


def _record():
    global frames, stream, is_recording

    while is_recording:
        try:
            data = stream.read(1024, exception_on_overflow=False)
            with lock:
                frames.append(data)
        except Exception as e:
            print(f"❌ Recording error: {e}")
            break

recording_thread = None


def toggle_audio():
    global is_recording, stream, frames, recording_thread

    ASSETS_DIR = get_assets_dir()
    Path(ASSETS_DIR).mkdir(parents=True, exist_ok=True)

    if not is_recording:
        # START RECORDING
        frames = []
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )

        if not is_recording:
            is_recording = True
            recording_thread = threading.Thread(target=_record, daemon=True)
            recording_thread.start()

        print("🎤 Recording started... (press again to stop)")
        return None

    else:
        # STOP RECORDING
        is_recording = False
        recording_thread.join()

        stream.stop_stream()
        stream.close()

        filename = f"audio_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.wav"
        destination_path = Path(ASSETS_DIR) / filename

        with wave.open(str(destination_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b"".join(frames))

        print(f"💾 Audio saved: {filename}")

        return {
            "type": "audio",
            "filename": filename
        }

def is_audio_recording():
    return is_recording

def cleanup():
    audio.terminate()