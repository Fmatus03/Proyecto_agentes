from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .utils import append_jsonl, write_json, write_text


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str
    gate: str


class PolicyEngine:
    version = "policy.webforge.v1"

    def __init__(self, allowed_agents: set[str]) -> None:
        self.allowed_agents = allowed_agents

    def check_agent(self, agent_id: str) -> PolicyDecision:
        if agent_id in self.allowed_agents:
            return PolicyDecision(True, "agent allowlisted", "policy")
        return PolicyDecision(False, "agent is not allowlisted", "policy")

    def check_action(self, action: str, permissions: dict[str, Any]) -> PolicyDecision:
        if action == "external_write" and not permissions.get("external_write", False):
            return PolicyDecision(False, "external writes require approval", "human_approval")
        if action == "deploy" and not permissions.get("deploy", False):
            return PolicyDecision(False, "deploy requires approval and rollback", "human_approval")
        if action == "production_data" and not permissions.get("production_data", False):
            return PolicyDecision(False, "production data denied by default", "security")
        return PolicyDecision(True, "allowed by current permissions", "policy")


class BudgetManager:
    version = "budget.webforge.v1"

    def __init__(self, budget: dict[str, int | float] | None = None) -> None:
        budget = budget or {}
        self.remaining: dict[str, int | float] = {
            "tokens": budget.get("tokens", 0),
            "tool_calls": budget.get("tool_calls", 200),
            "mcp_calls": budget.get("mcp_calls", 0),
            "cost_usd": budget.get("cost_usd", 0),
            "latency_ms": budget.get("latency_ms", 0),
        }
        self.initial = dict(self.remaining)
        self.usage: list[dict[str, Any]] = []

    def assert_tool_available(self, tool_id: str) -> PolicyDecision:
        if self.remaining["tool_calls"] <= 0:
            return PolicyDecision(False, f"budget exhausted before {tool_id}", "budget")
        return PolicyDecision(True, "tool budget available", "budget")

    def record_tool_call(self, tool_id: str, status: str) -> None:
        self.remaining["tool_calls"] = max(0, int(self.remaining["tool_calls"]) - 1)
        self.usage.append({"tool_id": tool_id, "status": status, "cost_usd": 0, "tokens": 0})

    def write(self, output_dir: Path) -> None:
        consumed_tool_calls = max(0, int(self.initial.get("tool_calls", 0)) - int(self.remaining.get("tool_calls", 0)))
        write_json(
            output_dir / "billing-ledger.json",
            {
                "version": self.version,
                "estimated_consumption": {
                    "basis": "deterministic local WEBFORGE run; no LLM, MCP or external billing is invoked by the harness",
                    "tool_calls": consumed_tool_calls or len(self.usage),
                    "mcp_calls": 0,
                    "tokens": 0,
                    "cost_usd": 0,
                },
                "remaining": self.remaining,
                "usage": self.usage,
                "budget_exceeded": False,
            },
        )


class MCPGateway:
    version = "mcpreg.webforge.v1"

    def __init__(self, output_dir: Path, allowlist: set[str] | None = None) -> None:
        self.output_dir = output_dir
        self.allowlist = allowlist or set()

    def invoke(self, server_id: str, action: str) -> PolicyDecision:
        allowed = server_id in self.allowlist
        decision = PolicyDecision(
            allowed=allowed,
            reason="server allowlisted" if allowed else "MCP server denied by default",
            gate="mcp_policy",
        )
        append_jsonl(
            self.output_dir / "mcp-invocations.jsonl",
            {"server_id": server_id, "action": action, "allowed": allowed, "reason": decision.reason},
        )
        return decision

    def write_policy(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "mcp-invocations.jsonl").touch()
        write_text(
            self.output_dir / "mcp-policy.yaml",
            "\n".join(
                [
                    "mcp_gateway:",
                    "  default: deny",
                    "  discovery_allowed: false",
                    "  invocation_allowed: false",
                    "  allowlist: []",
                    "  write_requires_human_approval: true",
                    "  pre_gate: mcp_policy",
                    "  post_gate: tool-output",
                ]
            ),
        )
        write_json(
            self.output_dir / "mcp-policy.json",
            {"default": "deny", "allowlist": sorted(self.allowlist), "version": self.version},
        )


def write_approval_matrix(output_dir: Path) -> None:
    write_text(
        output_dir / "approval-matrix.md",
        "\n".join(
            [
                "# Approval matrix",
                "",
                "| action | default | approval required |",
                "|---|---|---|",
                "| external_write | denied | yes |",
                "| deploy | denied | yes + rollback |",
                "| production_data | denied | yes + data policy |",
                "| persistent_memory_activation | denied | yes + evals + rollback |",
                "| new_dependency | denied | yes + license + CVE scan |",
            ]
        ),
    )
