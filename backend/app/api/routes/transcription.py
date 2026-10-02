from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

router = APIRouter()


class TranscriptionResponse(BaseModel):
    text: str
    confidence: float


@router.post("/transcription", response_model=TranscriptionResponse)
async def transcribe_audio(audio: UploadFile = File(...)):
    if not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be audio")

    # TODO: Integrate with AI ASR module
    return {"text": "", "confidence": 0.0}