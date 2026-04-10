"""HTTP server to receive health data from Apple Shortcuts."""

import asyncio
import base64
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket
from fastapi.responses import Response, StreamingResponse
from mistralai.client import Mistral
from pydantic import BaseModel
from uvicorn import run as uvicorn_run

from backend.berries import init_berries
from backend.brain import build_system_message, stream_response
from backend.config import (
    DEMO_ASSISTANT_VOICE,
    HEALTH_SERVER_HOST,
    HEALTH_SERVER_PORT,
    MISTRAL_API_KEY,
)
from backend.health_store import get_summary, init_db, insert_metrics
from backend.voice_ws import handle_voice_ws
from backend.voxtral import (
    prewarm_tts,
    stream_voice_events,
    synthesize_wav_from_stream,
    transcribe,
)

logger = logging.getLogger("backend.server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_berries()
    logger.info("Health database initialized")
    yield


app = FastAPI(title="V.I.T.A.L Health Receiver", version="0.1.0", lifespan=lifespan)


class HealthPayload(BaseModel):
    """Payload sent by the Apple Shortcut."""

    metrics: list[dict]


@app.post("/health")
async def receive_health_data(payload: HealthPayload):
    """Receive health metrics from Apple Shortcuts."""
    if not payload.metrics:
        raise HTTPException(status_code=400, detail="No metrics provided")

    loop = asyncio.get_running_loop()
    count = await loop.run_in_executor(None, insert_metrics, payload.metrics)
    return {"status": "ok", "inserted": count}


@app.get("/health/summary")
async def health_summary(hours: int = 24):
    """Get aggregated health summary."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_summary, hours)


@app.get("/health/ping")
async def ping():
    return {"status": "alive"}


_mistral_client: Mistral | None = None


def _get_mistral() -> Mistral:
    global _mistral_client  # noqa: PLW0603
    if _mistral_client is None:
        _mistral_client = Mistral(api_key=MISTRAL_API_KEY)
    return _mistral_client


@app.post("/voice")
async def voice_loop(audio: UploadFile = File(...)):
    """Non-streaming voice loop (kept for compat/testing). Returns WAV bytes."""
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio")

    loop = asyncio.get_running_loop()
    client = _get_mistral()
    try:
        user_text = transcribe(client, audio_bytes)
    except Exception as exc:
        logger.exception("STT failed")
        raise HTTPException(status_code=500, detail=f"STT failed: {exc}") from exc

    logger.info("User said: %s", user_text)
    if not user_text:
        user_text = "(silence)"

    system_msg = await loop.run_in_executor(None, build_system_message)
    messages = [system_msg, {"role": "user", "content": user_text}]

    token_stream = stream_response(client, messages)
    wav_bytes, reply = synthesize_wav_from_stream(
        token_stream, voice_id=DEMO_ASSISTANT_VOICE
    )
    logger.info("VITAL replied: %s", reply)

    return Response(
        content=wav_bytes,
        media_type="audio/wav",
        headers={
            "X-Transcript-B64": base64.b64encode(user_text.encode("utf-8")).decode("ascii"),
            "X-Reply-B64": base64.b64encode(reply.encode("utf-8")).decode("ascii"),
        },
    )


@app.post("/voice/stream")
async def voice_loop_stream(audio: UploadFile = File(...)):
    """Streaming voice loop: raw float32 PCM @ 24kHz mono, chunks sent as TTS produces them.

    iPhone should play progressively via AVAudioEngine. The transcript is returned
    as an X-Transcript-B64 header before the body starts.
    """
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio")

    # Pre-warm TTS TLS socket while STT is running — saves ~80-150ms per turn
    asyncio.get_running_loop().run_in_executor(None, prewarm_tts)

    loop = asyncio.get_running_loop()
    client = _get_mistral()
    try:
        user_text = transcribe(client, audio_bytes)
    except Exception as exc:
        logger.exception("STT failed")
        raise HTTPException(status_code=500, detail=f"STT failed: {exc}") from exc

    logger.info("User said: %s", user_text)
    if not user_text:
        user_text = "(silence)"

    system_msg = await loop.run_in_executor(None, build_system_message)
    messages = [system_msg, {"role": "user", "content": user_text}]

    def _frame_generator():
        # Frame format: 1-byte type + 4-byte big-endian length + payload
        # type 0x01 = text token (utf-8), 0x02 = audio pcm float32 le
        token_stream = stream_response(client, messages)
        for kind, payload in stream_voice_events(
            token_stream, voice_id=DEMO_ASSISTANT_VOICE
        ):
            if kind == "text":
                data = payload.encode("utf-8")
                yield b"\x01" + len(data).to_bytes(4, "big") + data
            elif kind == "audio":
                yield b"\x02" + len(payload).to_bytes(4, "big") + payload

    return StreamingResponse(
        _frame_generator(),
        media_type="application/octet-stream",
        headers={
            "X-Transcript-B64": base64.b64encode(user_text.encode("utf-8")).decode("ascii"),
            "X-Sample-Rate": "24000",
            "X-Format": "vital-frames-v1",
        },
    )


@app.websocket("/voice/ws")
async def voice_ws(ws: WebSocket):
    """Realtime voice loop — bidirectional WebSocket.
    Client sends PCM16@16k binary; server sends transcript/token JSON text + PCM audio binary.
    """
    await handle_voice_ws(ws)


def main():
    """Entry point for vital-server."""
    init_db()
    uvicorn_run(
        "backend.health_server:app",
        host=HEALTH_SERVER_HOST,
        port=HEALTH_SERVER_PORT,
        log_level="info",
    )


if __name__ == "__main__":
    main()
