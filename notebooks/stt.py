import whisper
import os
import sounddevice as sd
from scipy.io.wavfile import write
from io import BytesIO
import numpy as np

def record_and_transcribe(duration=5, fs=16000):
    print("🎙️ Recording audio...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()

    # Save to temp file (Whisper works best with file paths)
    temp_file = "temp_audio.wav"
    write(temp_file, fs, audio)

    print("🧠 Transcribing with Whisper...")
    model = whisper.load_model("medium")  # use "small" or "medium" for better accuracy
    result = model.transcribe(temp_file, fp16=False)

    os.remove(temp_file)  # clean up after transcription
    return result["text"]

def transcribe_audio():
    
    file_path = '/workspace/file_store/referece.wav'

    # Load model (use "turbo" for speed, "small"/"medium"/"large" for better accuracy)
    model = whisper.load_model("medium")
    
    # Perform transcription
    result = model.transcribe(file_path, fp16=False)
    
    print("\n🧠 Transcription complete!\n")
    return result["text"]



print(transcribe_audio())

# print(record_and_transcribe())
