"""Terminal waveform visualizations — Mistral pixel aesthetic."""

import math
import time

from rich.text import Text

from vital.config import ORANGE, ORANGE_DARK, ORANGE_DIM

BLOCK_CHARS = " ▁▂▃▄▅▆▇█"


def render_listening(level: float) -> Text:
    """Render an animated waveform reactive to microphone input level."""
    t = time.monotonic()
    intensity = min(level / 300, 1.0)
    half = 15

    bars: list[float] = []
    for i in range(half):
        wave = (
            math.sin(t * 6 + i * 0.7) * 0.35
            + math.sin(t * 9 + i * 0.4) * 0.25
            + 0.25
        )
        envelope = 1.0 - (i / half) * 0.5
        height = wave * envelope * (0.2 + intensity * 0.8)
        bars.append(max(0.05, min(height, 1.0)))

    bars = list(reversed(bars)) + bars

    text = Text()
    text.append("  🎙  ", style="bold")
    for b in bars:
        idx = int(b * (len(BLOCK_CHARS) - 1))
        char = BLOCK_CHARS[idx]
        if b > 0.6:
            style = f"bold {ORANGE}"
        elif b > 0.3:
            style = ORANGE_DIM
        else:
            style = ORANGE_DARK
        text.append(char, style=style)
    text.append("  ", style="bold")
    return text


class SpeakingWaveform:
    """Rich renderable for animated speaking waveform."""

    def __rich_console__(self, console, options):
        t = time.monotonic()
        half = 15
        bars: list[float] = []

        for i in range(half):
            wave = (
                math.sin(t * 5 + i * 0.6) * 0.4
                + math.sin(t * 8 + i * 0.3) * 0.3
                + 0.3
            )
            envelope = 1.0 - (i / half) * 0.4
            height = wave * envelope
            bars.append(max(0.05, min(height, 1.0)))

        bars = list(reversed(bars)) + bars

        text = Text()
        text.append("  🔊  ", style="bold")
        for b in bars:
            idx = int(b * (len(BLOCK_CHARS) - 1))
            char = BLOCK_CHARS[idx]
            if b > 0.6:
                style = f"bold {ORANGE}"
            elif b > 0.3:
                style = ORANGE_DIM
            else:
                style = ORANGE_DARK
            text.append(char, style=style)
        text.append("  ", style="bold")
        yield text


def render_health_banner(summary: dict) -> Text:
    """Render a compact health data banner for the terminal."""
    text = Text()
    text.append("\n  ── VITAL SIGNS ──\n", style=f"bold {ORANGE}")

    icons = {
        "heart_rate": "♥",
        "spo2": "🫁",
        "steps": "👟",
        "calories": "🔥",
        "sleep": "😴",
        "hrv": "📈",
    }

    for metric, stats in summary.items():
        icon = icons.get(metric, "•")
        unit = stats.get("unit") or ""
        text.append(f"  {icon} {metric}: ", style=f"bold {ORANGE}")
        text.append(f"{stats['latest']} {unit}", style="white")
        text.append(f"  (avg: {stats['avg']}, range: {stats['min']}–{stats['max']})\n", style="dim")

    return text
