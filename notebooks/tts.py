

import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
# print(TTS().list_models())

# Init TTS
tts = TTS("tts_models/en/ljspeech/fast_pitch").to(device)

# Run TTS
# ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
# Text to speech list of amplitude values as output
# wav = tts.tts(text="Hello world!", speaker_wav="file_store/referece.wav", language="en")
# Text to speech to a file
tts.tts_to_file(text="Hello world! this is cloned voice", speaker_wav="/workspace/file_store/referece.wav", file_path="/workspace/outputs/audio.wav") #language="en", 

