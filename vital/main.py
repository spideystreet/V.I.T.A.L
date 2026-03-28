"""V.I.T.A.L — Voice-Integrated Tracker & Adaptive Listener.

Main conversation loop orchestrating audio, LLM, and health data.
"""

import argparse
import sys

from mistralai.client import Mistral
from rich.console import Console
from rich.live import Live
from rich.text import Text

from vital.config import MISTRAL_API_KEY, ORANGE, REFRESH_FPS
from vital.health_store import get_summary, init_db
from vital.viz import SpeakingWaveform, render_health_banner

console = Console()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="V.I.T.A.L health assistant")
    parser.add_argument("--text", action="store_true", help="Text-only mode (no microphone)")
    parser.add_argument("--no-speak", action="store_true", help="Disable TTS playback")
    return parser.parse_args()


def _get_query(text_mode: bool) -> str | None:
    """Get user input via voice or text."""
    if text_mode:
        try:
            return console.input(f"[{ORANGE}]you >[/] ").strip()
        except (EOFError, KeyboardInterrupt):
            return None

    # Voice mode
    from vital.audio import record
    from vital.voxtral import transcribe

    console.print(f"[{ORANGE}]Listening...[/]")
    try:
        audio_data = record()
        if not audio_data:
            console.print("[dim]No speech detected.[/dim]")
            return ""
        client = Mistral(api_key=MISTRAL_API_KEY)
        text = transcribe(client, audio_data)
        console.print(f"[dim]> {text}[/dim]")
        return text
    except Exception as e:
        console.print(f"[red]Audio error: {e}. Falling back to text.[/red]")
        return console.input(f"[{ORANGE}]you >[/] ").strip()


def _render_response(text: str, streaming: str = "", speaking: bool = False) -> Text | object:
    """Render the assistant response with optional waveform."""
    from rich.console import Group

    parts = []
    content = streaming or text
    msg = Text()
    msg.append("vital > ", style=f"bold {ORANGE}")
    msg.append(content)
    parts.append(msg)

    if speaking:
        parts.append(SpeakingWaveform())

    return Group(*parts) if len(parts) > 1 else parts[0]


def main():
    args = _parse_args()

    if not MISTRAL_API_KEY:
        console.print("[red]MISTRAL_API_KEY is not set.[/red]")
        sys.exit(1)

    init_db()
    client = Mistral(api_key=MISTRAL_API_KEY)

    # Show health banner if data exists
    summary = get_summary(24)
    if summary:
        console.print(render_health_banner(summary))

    console.print(f"\n[bold {ORANGE}]  ╔═══════════════════════════════════════╗[/]")
    console.print(f"[bold {ORANGE}]  ║   V.I.T.A.L — Health Assistant        ║[/]")
    console.print(f"[bold {ORANGE}]  ╚═══════════════════════════════════════╝[/]")
    console.print(f"[dim]  Mode: {'text' if args.text else 'voice'} | Type 'quit' to exit[/dim]\n")

    from vital.brain import build_system_message, stream_response

    messages = [build_system_message()]
    speak_mode = not args.text and not args.no_speak

    while True:
        query = _get_query(args.text)
        if query is None or query.lower() in ("quit", "exit", "q"):
            console.print(f"\n[{ORANGE}]Take care! 🧡[/]")
            break
        if not query:
            continue

        messages.append({"role": "user", "content": query})

        # Refresh health context every turn
        messages[0] = build_system_message()

        token_stream = stream_response(client, messages)
        full_text = ""

        if speak_mode:
            from vital.voxtral import speak_streaming

            with Live(
                _render_response("", speaking=True),
                refresh_per_second=REFRESH_FPS,
                vertical_overflow="visible",
            ) as live:
                for token in speak_streaming(client, token_stream):
                    full_text += token
                    live.update(_render_response("", streaming=full_text, speaking=True))
                live.update(_render_response(full_text))
        else:
            with Live(
                _render_response(""),
                refresh_per_second=REFRESH_FPS,
                vertical_overflow="visible",
            ) as live:
                for token in token_stream:
                    full_text += token
                    live.update(_render_response("", streaming=full_text))
                live.update(_render_response(full_text))

        messages.append({"role": "assistant", "content": full_text})


if __name__ == "__main__":
    main()
