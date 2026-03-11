import os
import requests
from fastapi import FastAPI, Request, Response, HTTPException

app = FastAPI()

SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY", "")
SARVAM_API_URL = "https://api.sarvam.ai/text-to-speech/stream"

@app.get("/")
def health():
    return {"ok": True}

@app.post("/tts")
async def tts(req: Request):
    if not SARVAM_API_KEY:
        raise HTTPException(status_code=500, detail="Missing SARVAM_API_KEY")

    body = await req.json()
    text = body.get("text") or body.get("input") or body.get("message")
    if not text:
        raise HTTPException(status_code=400, detail="Missing text")

    payload = {
        "text": text,
        "target_language_code": body.get("target_language_code", "hi-IN"),
        "speaker": body.get("speaker", "shubh"),
        "model": body.get("model", "bulbul:v3"),
        "pace": body.get("pace", 1.1),
        "speech_sample_rate": 22050,
        "output_audio_codec": "mp3",
        "enable_preprocessing": True
    }

    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        with requests.post(SARVAM_API_URL, headers=headers, json=payload, stream=True, timeout=60) as r:
            if not r.ok:
                raise HTTPException(status_code=502, detail=f"Sarvam error: {r.text}")
            audio_bytes = r.content

        return Response(content=audio_bytes, media_type="audio/mpeg")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Network error calling Sarvam: {str(e)}")
