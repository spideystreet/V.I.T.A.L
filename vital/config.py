"""Configuration and constants for V.I.T.A.L."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "")

# --- Models ---
STT_MODEL = "voxtral-mini-transcribe-2507"
LLM_MODEL = "mistral-small-latest"
TTS_MODEL = "voxtral-mini-tts-2603"

# --- Audio ---
SAMPLE_RATE = 16_000  # Voxtral STT requirement
TTS_SAMPLE_RATE = 24_000  # Voxtral TTS output
SILENCE_THRESHOLD = 500
SILENCE_DURATION = 1.5  # seconds
MAX_RECORD_SECONDS = 30
AUDIO_OUTPUT_DEVICE = os.environ.get("AUDIO_OUTPUT_DEVICE")
TTS_VOICE_ID = os.environ.get("TTS_VOICE_ID", "")

# --- Health Server ---
HEALTH_SERVER_HOST = os.environ.get("VITAL_HOST", "0.0.0.0")
HEALTH_SERVER_PORT = int(os.environ.get("VITAL_PORT", "8420"))

# --- Storage ---
DATA_DIR = Path(os.environ.get("VITAL_DATA_DIR", Path.home() / ".vital"))
DB_PATH = DATA_DIR / "health.db"

# --- UI ---
ORANGE = "#ff7000"
ORANGE_DIM = "#cc5500"
ORANGE_DARK = "#884400"
REFRESH_FPS = 15
