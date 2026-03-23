import pyaudio
import wave
from datetime import datetime
from config import AUDIO_DIR
from pathlib import Path
import threading

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


def toggle_audio():
    global is_recording, stream, frames

    Path(AUDIO_DIR).mkdir(parents=True, exist_ok=True)

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

        is_recording = True
        threading.Thread(target=_record, daemon=True).start()

        print("🎤 Recording started... (press again to stop)")
        return None

    else:
        # STOP RECORDING
        is_recording = False

        stream.stop_stream()
        stream.close()

        filename = Path(AUDIO_DIR) / f"audio_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.wav"

        with wave.open(str(filename), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b"".join(frames))

        print(f"💾 Audio saved: {filename}")

        return {
            "type": "audio",
            "path": filename
        }