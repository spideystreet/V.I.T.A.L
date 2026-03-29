"""MCP server that wraps Mistral Vibe CLI in headless mode.

Exposes vibe as a native tool for Claude Code, enabling multi-agent
orchestration where Claude plans/reviews and Vibe executes.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from mcp.server.fastmcp import Context, FastMCP

VIBE_BIN = os.environ.get("VIBE_BIN", "vibe")
DEFAULT_MAX_TURNS = 10
DEFAULT_MAX_PRICE = 0.5
DEFAULT_TIMEOUT = 300

mcp = FastMCP(name="vibe")


def _build_command(
    prompt: str,
    *,
    max_turns: int,
    max_price: float,
    output_format: str,
    workdir: str | None,
    enabled_tools: list[str] | None,
    agent: str | None,
) -> list[str]:
    """Build the vibe CLI command."""
    cmd = [
        VIBE_BIN,
        "-p",
        prompt,
        "--max-turns",
        str(max_turns),
        "--max-price",
        str(max_price),
        "--output",
        output_format,
    ]
    if workdir:
        cmd.extend(["--workdir", workdir])
    if agent:
        cmd.extend(["--agent", agent])
    if enabled_tools:
        for tool in enabled_tools:
            cmd.extend(["--enabled-tools", tool])
    return cmd


async def _run_vibe(cmd: list[str], timeout: int) -> dict[str, Any]:
    """Execute vibe subprocess and return parsed result."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        return {"ok": False, "error": f"Vibe timed out after {timeout}s"}

    if proc.returncode != 0:
        return {
            "ok": False,
            "exit_code": proc.returncode,
            "error": stderr.decode().strip(),
        }

    try:
        messages = json.loads(stdout.decode())
    except json.JSONDecodeError:
        return {
            "ok": False,
            "error": "Failed to parse vibe JSON output",
            "raw_stdout": stdout.decode()[:2000],
        }

    # Extract the last assistant message as the main result
    assistant_msgs = [m for m in messages if m.get("role") == "assistant"]
    last_response = assistant_msgs[-1]["content"] if assistant_msgs else None

    # Extract cost info from the last message that has it
    cost = None
    for m in reversed(messages):
        if "total_cost_usd" in m:
            cost = m["total_cost_usd"]
            break

    return {
        "ok": True,
        "response": last_response,
        "cost_usd": cost,
        "turn_count": len(assistant_msgs),
        "messages": messages,
    }


@mcp.tool()
async def vibe_run(
    prompt: str,
    max_turns: int = DEFAULT_MAX_TURNS,
    max_price: float = DEFAULT_MAX_PRICE,
    workdir: str | None = None,
    enabled_tools: list[str] | None = None,
    agent: str | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    ctx: Context = None,
) -> dict[str, Any]:
    """Run Mistral Vibe in headless mode with a given prompt.

    Args:
        prompt: The task for Vibe to execute.
        max_turns: Maximum assistant turns (default 10).
        max_price: Cost ceiling in USD (default 0.50).
        workdir: Working directory for Vibe (defaults to project root).
        enabled_tools: Restrict Vibe to specific tools (e.g. ["read_file", "grep"] for read-only).
        agent: Vibe agent name (builtin: default, plan, auto-approve, or custom).
        timeout: Max execution time in seconds (default 300).
    """
    cmd = _build_command(
        prompt,
        max_turns=max_turns,
        max_price=max_price,
        output_format="json",
        workdir=workdir,
        enabled_tools=enabled_tools,
        agent=agent,
    )

    if ctx:
        await ctx.info(f"Launching vibe: {prompt[:100]}...")

    result = await _run_vibe(cmd, timeout)

    if ctx:
        if result["ok"]:
            await ctx.info(
                f"Vibe completed — {result['turn_count']} turns, ${result.get('cost_usd', '?')}"
            )
        else:
            await ctx.info(f"Vibe failed: {result.get('error', 'unknown')}")

    return result


@mcp.tool()
async def vibe_review(
    target: str,
    workdir: str | None = None,
    ctx: Context = None,
) -> dict[str, Any]:
    """Run Vibe in read-only mode to review/audit code.

    Args:
        target: What to review (e.g. "review tests/test_health_store.py for quality").
        workdir: Working directory for Vibe.
    """
    return await vibe_run(
        prompt=target,
        max_turns=5,
        max_price=0.2,
        workdir=workdir,
        enabled_tools=["read_file", "grep"],
        ctx=ctx,
    )


if __name__ == "__main__":
    mcp.run()
