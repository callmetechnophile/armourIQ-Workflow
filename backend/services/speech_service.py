"""
speech_service.py
-----------------
Converts text into audio speech (TTS) using Sarvam AI as the primary provider
and Groq as the secondary (fallback) provider. Includes a silent WAV fallback
for sandboxed or offline environments.
"""
import os
import httpx
import base64
import struct
import logging

logger = logging.getLogger("SpeechService")


def get_silent_wav() -> bytes:
    """Generate a minimal 1-second silent WAV file (8000Hz, 8-bit mono)."""
    num_samples = 8000
    data_size = num_samples
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + data_size,
        b'WAVE',
        b'fmt ',
        16,          # Subchunk1Size
        1,           # AudioFormat (PCM)
        1,           # NumChannels
        8000,        # SampleRate
        8000,        # ByteRate
        1,           # BlockAlign
        8,           # BitsPerSample
        b'data',
        data_size
    )
    data = b'\x80' * data_size
    return header + data


def text_to_speech(text: str) -> tuple[bytes, str]:
    """
    Synthesize text into speech.
    Returns:
        (audio_bytes, content_type)
    """
    # 1. Try Sarvam AI (Primary)
    sarvam_key = os.environ.get("SARVAM_API_KEY")
    if sarvam_key and not sarvam_key.startswith("sarvam_placeholder"):
        try:
            logger.info("Attempting Sarvam AI TTS (Primary)")
            url = "https://api.sarvam.ai/text-to-speech"
            headers = {
                "api-subscription-key": sarvam_key,
                "Content-Type": "application/json"
            }
            payload = {
                "text": text,
                "speaker": "anushka",
                "target_language_code": "en-IN",
                "model": "bulbul:v3"
            }
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    audios = data.get("audios", [])
                    if audios and len(audios) > 0:
                        audio_data = audios[0]
                        return base64.b64decode(audio_data), "audio/wav"
                    else:
                        logger.warning("Sarvam AI returned empty audios array.")
                else:
                    logger.warning(f"Sarvam AI TTS API error {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Sarvam AI TTS failed: {e}")

    # 2. Try Groq (Secondary)
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key and not groq_key.startswith("gsk_placeholder"):
        try:
            logger.info("Attempting Groq TTS (Secondary)")
            url = "https://api.groq.com/openai/v1/audio/speech"
            headers = {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            }
            # Orpheus is the default fast TTS model on Groq
            payload = {
                "model": "canopylabs/orpheus-v1-english",
                "input": text[:200],  # Orpheus limits input to 200 chars
                "voice": "troy",
                "response_format": "wav"
            }
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    return res.content, "audio/wav"
                else:
                    logger.warning(f"Groq TTS API error {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Groq TTS failed: {e}")

    # 3. Fallback to silent wav if both fail
    logger.info("Falling back to silent WAV generation.")
    return get_silent_wav(), "audio/wav"
