from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import requests
import base64
import os
from pydub import AudioSegment
import imageio_ffmpeg

# Make pydub use imageio-ffmpeg as converter
AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()

from detector import analyze_voice

API_KEY = "8084b8d9671466b57cf0c197f8d8c81f297fc80c8af697db59b9d591c56f992d"

app = FastAPI(
    title="AI Generated Voice Detection API",
    description="Detects whether a voice sample is AI-generated or human",
    version="1.0"
)

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
    # 🔐 Authentication
    verify_api_key(authorization, x_api_key)

    # 🎧 Input handling
    if data.audio_url:
        r = requests.get(data.audio_url)
        if r.status_code != 200:
            raise HTTPException(status_code=400, detail="Unable to download audio")
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

    # 🧠 Detection
    result, confidence = analyze_voice("input.wav")

    # Cleanup
    os.remove("input.mp3")
    os.remove("input.wav")

    return {
        "result": result,
        "confidence": confidence
    }
