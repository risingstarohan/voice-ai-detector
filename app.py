from detector import detect_ai_voice
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
import base64
import uuid
import os

app = FastAPI(title="AI Generated Voice Detection API")

API_KEY = "8084b8d9671466b57cf0c197f8d8c81f297fc80c8af697db59b9d591c56f992d"

UPLOAD_DIR = "temp_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class AudioRequest(BaseModel):
    language: str
    audio_format: str = Field(..., alias="audioFormat")
    audio_base64: str = Field(..., alias="audioBase64")

    class Config:
        allow_population_by_field_name = True


# ------------------- AI Voice Detection Endpoint -------------------
@app.post("/detect")
def detect_voice(
    data: AudioRequest,
    x_api_key: str = Header(None)
):
    # 🔐 API KEY CHECK
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    try:
        # Decode base64 audio
        audio_bytes = base64.b64decode(data.audio_base64)

        filename = f"{uuid.uuid4()}.{data.audio_format}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        # Run detection logic
        result, confidence = detect_ai_voice(file_path)

        # Cleanup
        os.remove(file_path)

        return {
            "status": "success",
            "language": data.language,
            "result": result,
            "confidence": confidence
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ------------------- Honeypot Endpoint -------------------
@app.get("/honeypot")
def honeypot_check(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return {
        "status": "active",
        "service": "agentic-honeypot",
        "message": "Honeypot endpoint reachable",
        "honeypot": True
    }

