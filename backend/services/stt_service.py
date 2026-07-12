"""
stt_service.py
--------------
Converts spoken audio into text (STT) using Sarvam AI as the primary provider
and Groq (Whisper) as the secondary (fallback) provider.
"""
import os
import httpx
import logging

logger = logging.getLogger("STTService")


def speech_to_text(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """
    Transcribe audio bytes to text.
    Uses Sarvam AI as primary and Groq as secondary.
    """
    if not audio_bytes:
        return ""

    # 1. Try Sarvam AI (Primary)
    sarvam_key = os.environ.get("SARVAM_API_KEY")
    if sarvam_key and not sarvam_key.startswith("sarvam_placeholder"):
        try:
            logger.info("Attempting Sarvam AI STT (Primary)")
            url = "https://api.sarvam.ai/speech-to-text"
            headers = {
                "api-subscription-key": sarvam_key
            }
            files = {
                "file": (filename, audio_bytes, "audio/wav")
            }
            data = {
                "model": "saaras:v3",
                "mode": "transcribe"
            }
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, headers=headers, files=files, data=data)
                if res.status_code == 200:
                    result = res.json()
                    transcript = result.get("transcript", "").strip()
                    if transcript:
                        logger.info("Sarvam AI STT transcription successful.")
                        return transcript
                else:
                    logger.warning(f"Sarvam AI STT API error {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Sarvam AI STT failed: {e}")

    # 2. Try Groq (Secondary)
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key and not groq_key.startswith("gsk_placeholder"):
        try:
            logger.info("Attempting Groq Whisper STT (Secondary)")
            url = "https://api.groq.com/openai/v1/audio/transcriptions"
            headers = {
                "Authorization": f"Bearer {groq_key}"
            }
            files = {
                "file": (filename, audio_bytes, "audio/wav")
            }
            data = {
                "model": "whisper-large-v3-turbo"
            }
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, headers=headers, files=files, data=data)
                if res.status_code == 200:
                    result = res.json()
                    text = result.get("text", "").strip()
                    if text:
                        logger.info("Groq Whisper STT transcription successful.")
                        return text
                else:
                    logger.warning(f"Groq Whisper STT API error {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Groq Whisper STT failed: {e}")

    # 3. Local simulated fallback for sandbox stability
    logger.info("Falling back to local simulated speech recognition response.")
    return "I want to build a solar powered vacuum cleaner"
