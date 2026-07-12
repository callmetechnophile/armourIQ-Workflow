"""
speech.py
---------
FastAPI router for Text-to-Speech (TTS) capabilities.
"""
from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io

from backend.services.speech_service import text_to_speech
from backend.services.stt_service import speech_to_text
from backend.armoriq.delegation import capture_plan, delegate, invoke_tool

router = APIRouter(prefix="/api/speech", tags=["Speech"])


class TTSRequest(BaseModel):
    text: str


@router.post("/tts")
def text_to_speech_endpoint(payload: TTSRequest):
    """
    Generate speech audio from text.
    Uses Sarvam AI as primary and Groq as secondary.
    Governed under ArmorIQ enforcers.
    """
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text to synthesize cannot be empty.")

    try:
        # Wrap read in ArmorIQ receipt enforcer
        root_receipt = capture_plan(f"Synthesize speech for text: {payload.text[:30]}...")
        speech_receipt = delegate(
            agent_name="ExportAgent",  # We can delegate audio export/synthesis to the ExportAgent
            requested_scope=["export.media"],
            parent_receipt=root_receipt.model_dump()
        )
        invoke_tool(
            agent_name="ExportAgent",
            tool_name="export.media",
            args={"type": "audio", "text_length": len(payload.text)},
            receipt_dict=speech_receipt.model_dump()
        )

        audio_bytes, content_type = text_to_speech(payload.text)
        return StreamingResponse(io.BytesIO(audio_bytes), media_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text-to-speech synthesis failed: {str(e)}")


@router.post("/stt")
async def speech_to_text_endpoint(file: UploadFile = File(...)):
    """
    Transcribe audio file into text.
    Uses Sarvam AI as primary and Groq as secondary.
    Governed under ArmorIQ enforcers.
    """
    try:
        # Read file bytes
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Audio file is empty.")

        # Wrap read in ArmorIQ receipt enforcer
        root_receipt = capture_plan(f"Transcribe audio file: {file.filename}")
        speech_receipt = delegate(
            agent_name="ExtractionAgent",
            requested_scope=["extraction.media"],
            parent_receipt=root_receipt.model_dump()
        )
        invoke_tool(
            agent_name="ExtractionAgent",
            tool_name="extraction.media",
            args={"type": "audio", "filename": file.filename},
            receipt_dict=speech_receipt.model_dump()
        )

        transcription = speech_to_text(content, file.filename)
        return {"text": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech-to-text transcription failed: {str(e)}")
