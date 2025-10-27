import torch
import tempfile
import os
from TTS.api import TTS

# 🧩 Fix for PyTorch 2.6+ weights_only restriction
import torch.serialization
try:
    from TTS.tts.configs.xtts_config import XttsConfig
    torch.serialization.add_safe_globals([XttsConfig])
except Exception as e:
    print("⚠️ Safe globals registration failed:", e)

_tts_model = None


def load_tts_model():
    """Load the TTS model once into GPU memory."""
    global _tts_model
    if _tts_model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🎤 Loading XTTS model on {device}...")

        # ⚙️ Force torch.load to allow full pickle (safe for trusted model)
        torch.serialization._legacy_load = torch.load
        def unsafe_load(*args, **kwargs):
            kwargs["weights_only"] = False
            return torch.serialization._legacy_load(*args, **kwargs)
        torch.load = unsafe_load

        # Now load the XTTS model
        _tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        print("✅ XTTS model ready.")

    return _tts_model


def tts_to_temp(text: str, speaker_wav: str) -> str:
    """Generate speech audio as a temporary WAV file and return its path."""
    model = load_tts_model()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    model.tts_to_file(
        text=text,
        speaker_wav=speaker_wav,
        language="en",
        file_path=temp_file.name
    )
    print(f"🎧 Temporary TTS file created: {temp_file.name}")
    return temp_file.name
