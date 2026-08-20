from __future__ import annotations

import asyncio

import pytest

mcp = pytest.importorskip("mcp", reason="optional MCP SDK is not installed")

from mcp import Client

from prove_it.mcp_server import _server


def test_official_mcp_sdk_lists_and_calls_proof_tools(tmp_path, monkeypatch):
    monkeypatch.setenv("PROVE_IT_WORKSPACE", str(tmp_path))

    async def exercise() -> None:
        server = _server()
        async with Client(server) as client:
            tools = await client.list_tools()
            names = {tool.name for tool in tools.tools}
            assert {
                "proveit.start",
                "proveit.record_source",
                "proveit.run_check",
                "proveit.status",
                "proveit.report",
            }.issubset(names)

            start = await client.call_tool(
                "proveit.start",
                {
                    "task": "MCP integration smoke",
                    "acceptance_criteria": ["proof session exists"],
                    "overwrite": True,
                },
            )
            assert not start.is_error

            status = await client.call_tool("proveit.status", {})
            assert not status.is_error

    asyncio.run(exercise())
