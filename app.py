from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import requests, base64
from pydub import AudioSegment

import os
AudioSegment.converter = r"C:\Users\rohan\Downloads\ffmpeg-8.0.1-essentials_build\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"

# Example placeholder for your detection function
def analyze_voice(file_path):
    # For demo purposes, always return HUMAN with 0.95 confidence
    return "HUMAN", 0.95

API_KEY = "8084b8d9671466b57cf0c197f8d8c81f297fc80c8af697db59b9d591c56f992d"

app = FastAPI(title="AI Voice Detector", version="1.0")

class VoiceRequest(BaseModel):
    audio_url: str | None = None
    audio_base64: str | None = None
    message: str | None = None
    language: str | None = None

def verify_api_key(auth: str | None, x_key: str | None):
    if auth and API_KEY in auth:
        return
    if x_key and API_KEY == x_key:
        return
    raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/detect-voice")
def detect_voice(
    data: VoiceRequest,
    authorization: str = Header(None),
    x_api_key: str = Header(None)
):
    # 🔐 Check API key
    verify_api_key(authorization, x_api_key)

    try:
        # Handle audio input
        if data.audio_url:
            r = requests.get(data.audio_url)
            r.raise_for_status()
            with open("input.mp3", "wb") as f:
                f.write(r.content)
        elif data.audio_base64:
            audio_bytes = base64.b64decode(data.audio_base64)
            with open("input.mp3", "wb") as f:
                f.write(audio_bytes)
        else:
            raise HTTPException(status_code=400, detail="Audio input missing")

        # Convert MP3 → WAV
        audio = AudioSegment.from_mp3("input.mp3")
        audio.export("input.wav", format="wav")

        # Analyze
        result, confidence = analyze_voice("input.wav")

    except Exception as e:
        return {"error": str(e)}

    finally:
        # Cleanup
        if os.path.exists("input.mp3"):
            os.remove("input.mp3")
        if os.path.exists("input.wav"):
            os.remove("input.wav")

    return {"result": result, "confidence": confidence}
