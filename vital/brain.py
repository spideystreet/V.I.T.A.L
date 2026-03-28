"""LLM reasoning with health context injection."""

from collections.abc import Iterator

from mistralai.client import Mistral

from vital.config import LLM_MODEL
from vital.health_store import get_summary

SYSTEM_TEMPLATE = """\
You are V.I.T.A.L (Voice-Integrated Tracker & Adaptive Listener), a health \
monitoring assistant. You have access to the user's real Apple Watch health data \
provided below.

Your role:
- Analyze health trends and patterns from the data
- Cross-reference user-reported symptoms with objective health metrics
- Provide actionable wellness suggestions (hydration, rest, exercise adjustments)
- Flag concerning patterns that deserve professional attention

CRITICAL RULES:
- NEVER diagnose medical conditions. You are NOT a doctor.
- ALWAYS recommend consulting a healthcare professional for medical concerns.
- Use short, conversational spoken French sentences. No markdown, no bullet points.
- Be warm, supportive, and factual.
- When data is missing or insufficient, say so honestly.

--- HEALTH DATA (last {hours}h) ---
{health_context}
"""


def build_system_message(hours: int = 24) -> dict:
    """Build the system message with current health context."""
    summary = get_summary(hours)

    if not summary:
        health_context = "No health data available yet. Ask the user to sync their Apple Watch data."
    else:
        lines = []
        for metric, stats in summary.items():
            unit = stats.get("unit") or ""
            lines.append(
                f"- {metric}: avg={stats['avg']} {unit}, "
                f"min={stats['min']}, max={stats['max']}, "
                f"latest={stats['latest']} ({stats['count']} readings)"
            )
        health_context = "\n".join(lines)

    return {
        "role": "system",
        "content": SYSTEM_TEMPLATE.format(hours=hours, health_context=health_context),
    }


def stream_response(client: Mistral, messages: list[dict]) -> Iterator[str]:
    """Stream LLM response token by token."""
    for chunk in client.chat.stream(model=LLM_MODEL, messages=messages):
        delta = chunk.data.choices[0].delta.content
        if delta:
            yield delta
