"""Microphone recording with silence detection and visual feedback."""

import io
import wave

import numpy as np
import sounddevice as sd
from rich.live import Live

from backend.config import MAX_RECORD_SECONDS, SAMPLE_RATE, SILENCE_DURATION, SILENCE_THRESHOLD
from backend.viz import render_listening


def record() -> bytes:
    """Record audio from microphone until silence is detected. Returns WAV bytes."""
    chunk_size = int(SAMPLE_RATE * 0.1)  # 100ms chunks
    max_chunks = int(MAX_RECORD_SECONDS / 0.1)
    silence_chunks = int(SILENCE_DURATION / 0.1)

    chunks: list[np.ndarray] = []
    has_speech = False
    silent_count = 0

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16") as stream:
        with Live(render_listening(0.0), refresh_per_second=15) as live:
            for _ in range(max_chunks):
                data, _ = stream.read(chunk_size)
                chunks.append(data.copy())

                level = float(np.abs(data).mean())
                live.update(render_listening(level))

                if level > SILENCE_THRESHOLD:
                    has_speech = True
                    silent_count = 0
                else:
                    silent_count += 1

                if has_speech and silent_count >= silence_chunks:
                    break

    if not has_speech:
        return b""

    audio = np.concatenate(chunks)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())
    return buf.getvalue()
