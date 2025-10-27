# stt.py
import torch
import whisper
import os
import sounddevice as sd
import tempfile
from scipy.io.wavfile import write
from pydub import AudioSegment  # helps convert from webm/mp3 to wav

_whisper_model = None

def load_whisper_model():
    """Load Whisper model once and cache it."""
    global _whisper_model
    if _whisper_model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🧠 Loading Whisper model on {device}...")
        _whisper_model = whisper.load_model("medium", device=device)
    return _whisper_model


def transcribe_file(audio_path: str):
    """Transcribe an uploaded audio file (any format)."""
    model = load_whisper_model()

    # Convert to wav if needed
    if not audio_path.lower().endswith(".wav"):
        sound = AudioSegment.from_file(audio_path)
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        sound.export(temp_wav.name, format="wav")
        audio_path = temp_wav.name

    print("🧠 Transcribing uploaded audio with Whisper...")
    result = model.transcribe(audio_path, fp16=False)
    return result["text"]


def record_and_transcribe(duration=5, fs=16000):
    """Record from mic (fallback mode)."""
    print("🎙️ Recording audio...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(temp_file.name, fs, audio)

    print("🧠 Transcribing live mic input with Whisper...")
    model = load_whisper_model()
    result = model.transcribe(temp_file.name, fp16=False)

    os.remove(temp_file.name)
    return result["text"]
