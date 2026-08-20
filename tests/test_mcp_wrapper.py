from __future__ import annotations

import sys
import types

from prove_it import mcp_server


class FakeServer:
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.kwargs = kwargs
        self.tools = {}
        self.resources = {}
        self.ran = False

    def tool(self, *, name=None, **kwargs):
        def decorator(fn):
            self.tools[name or fn.__name__] = fn
            return fn
        return decorator

    def resource(self, uri: str, **kwargs):
        def decorator(fn):
            self.resources[uri] = fn
            return fn
        return decorator

    def run(self):
        self.ran = True


def test_mcp_server_registers_only_proof_surface(monkeypatch):
    server_module = types.ModuleType("mcp.server")
    server_module.MCPServer = FakeServer
    mcp_module = types.ModuleType("mcp")
    mcp_module.server = server_module
    monkeypatch.setitem(sys.modules, "mcp", mcp_module)
    monkeypatch.setitem(sys.modules, "mcp.server", server_module)

    server = mcp_server._server()
    assert set(server.tools) == {
        "proveit.start",
        "proveit.add_criterion",
        "proveit.record_source",
        "proveit.record_evidence",
        "proveit.run_check",
        "proveit.set_criterion_state",
        "proveit.status",
        "proveit.report",
    }
    assert set(server.resources) == {
        "proveit://proof/current",
        "proveit://proof/report",
    }
    assert not any(name.endswith("read_file") or name.endswith("run_shell") for name in server.tools)
