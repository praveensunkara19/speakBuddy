import os
import uuid
from pathlib import Path
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
import torch

# ✅ Local imports
import llm
import stt
import tts
from ui import home_ui

# --- FastAPI Setup ---
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="🎧 Talking Agent (Static Image + Voice Clone)")
app.mount("/file_store", StaticFiles(directory="file_store"), name="file_store")

# --- Paths ---
FILE_STORE = Path("/workspace/file_store")
IMAGE_PATH = FILE_STORE / "alice.jpg"
REF_AUDIO_PATH = FILE_STORE / "reference.wav"
OUTPUTS = Path("outputs")
OUTPUTS.mkdir(exist_ok=True)

# --- ROUTES ---
@app.get("/", response_class=HTMLResponse)
def serve_ui():
    """Serve the main web UI."""
    return HTMLResponse(content=home_ui("/file_store/alice.jpg"))



@app.post("/talking_agent/")
async def talking_agent(
    user_text: str = Form(None),
    user_audio: UploadFile = File(None),
):
    """Handle user input: (text or audio) → LLM → TTS → return audio."""
    try:
        print("🎙️ Request received...")
        if user_audio:
            # Save uploaded audio
            temp_audio_path = FILE_STORE / f"{uuid.uuid4()}_{user_audio.filename}"
            with open(temp_audio_path, "wb") as f:
                f.write(await user_audio.read())

            print(f"🎧 User audio saved: {temp_audio_path}")

            # Transcribe to text
            user_text = stt.transcribe_file(str(temp_audio_path))
            print(f"🗣️ Transcribed text: {user_text}")

        elif not user_text or not user_text.strip():
            user_text = "Hi Hello, welcome to agentSpeak!?"

        print(f"🧠 Final user text: {user_text}")

        # 🧩 Get LLM response
        llm_text = llm.get_llm_response(user_text)
        print(f"💬 LLM replied: {llm_text}")

        # 🗣️ Convert LLM response to speech
        tts_path = tts.tts_to_temp(llm_text, str(REF_AUDIO_PATH))
        print(f"🎧 Generated TTS: {tts_path}")

        return FileResponse(tts_path, media_type="audio/wav")

    except Exception as e:
        print("❌ Error in /talking_agent/:", e)
        return JSONResponse({"error": str(e)}, status_code=500)


@app.on_event("startup")
def preload_models():
    """Load all models into memory for faster response."""
    print("⚙️ Preloading models...")

    if torch.cuda.is_available():
        print(f"🧠 GPU: {torch.cuda.get_device_name(0)}")
        print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

    try:
        _ = llm.get_llm_response("Hello!")  # warm up
        _ = stt.load_whisper_model()
        _ = tts.load_tts_model()
        print("✅ All models loaded successfully.")
    except Exception as e:
        print("⚠️ Model preload error:", e)
