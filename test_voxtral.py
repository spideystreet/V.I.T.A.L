"""Quick Voxtral transcription test — records 5s from mic then transcribes."""
import os
import tempfile
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
from mistralai.client import Mistral

API_KEY = os.getenv("MISTRAL_API_KEY", "DltcFjizvwkGnGteLv0DEKtd7it1tRMY")
DURATION = 5
SAMPLERATE = 16000

print(f"🎙  Recording {DURATION}s — speak now...")
audio = sd.rec(int(DURATION * SAMPLERATE), samplerate=SAMPLERATE, channels=1, dtype="int16")
sd.wait()
print("✅ Done recording, sending to Voxtral...")

with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
    wav.write(f.name, SAMPLERATE, audio)
    tmp = f.name

client = Mistral(api_key=API_KEY)
with open(tmp, "rb") as f:
    result = client.audio.transcriptions.complete(
        model="voxtral-mini-latest",
        file={"file_name": "recording.wav", "content": f, "content_type": "audio/wav"},
        language="fr",
    )

print(f"\n📝 Transcription:\n{result.text}")
