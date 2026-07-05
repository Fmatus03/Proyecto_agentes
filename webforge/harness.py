from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .context import ContextManager, MemoryGate
from .models import GateResult, PhaseResult
from .policy import BudgetManager, MCPGateway, PolicyEngine


@dataclass(frozen=True)
class AgentSpec:
    agent_id: str
    phase: str
    output_schema_ref: str
    allowed_tools: tuple[str, ...] = ()
    allowed_mcp_servers: tuple[str, ...] = ()


class HarnessRunner:
    def __init__(
        self,
        policy: PolicyEngine,
        budget: BudgetManager,
        context: ContextManager,
        memory: MemoryGate,
        mcp: MCPGateway,
        tool_registry: Any | None = None,
    ) -> None:
        self.policy = policy
        self.budget = budget
        self.context = context
        self.memory = memory
        self.mcp = mcp
        self.tool_registry = tool_registry
        self.invocations: list[dict[str, str]] = []

    def run_agent(
        self,
        spec: AgentSpec,
        state: dict[str, Any],
        handler: Callable[[dict[str, Any]], PhaseResult],
    ) -> PhaseResult:
        decision = self.policy.check_agent(spec.agent_id)
        if not decision.allowed:
            return PhaseResult(
                phase=spec.phase,
                agent_id=spec.agent_id,
                status="error",
                outputs={},
                gates=[
                    GateResult(
                        name=decision.gate,
                        status="fail",
                        phase=spec.phase,
                        principles=["P05"],
                        evidence=[],
                        message=decision.reason,
                    )
                ],
                evidence_ids=[],
            )
        prompt_input = {
            "task_id": state["task_id"],
            "phase": spec.phase,
            "context_pack": state.get("context_pack", {}),
            "memory_pack": self.memory.read_filtered(spec.agent_id, spec.phase),
            "previous_outputs": state.get("outputs", {}),
            "rules": {
                "no_inventar": True,
                "usar_solo_evidencia": True,
                "salida_schema": spec.output_schema_ref,
                "mcp_requires_pre_and_post_gate": True,
                "persistent_memory": "project_scoped_propose_only",
                "memory_isolation": "project_only_no_factory_memory",
            },
        }
        for server_id in spec.allowed_mcp_servers:
            mcp_decision = self.mcp.invoke(server_id, f"{spec.agent_id}:{spec.phase}")
            if not mcp_decision.allowed:
                return PhaseResult(
                    phase=spec.phase,
                    agent_id=spec.agent_id,
                    status="error",
                    outputs={},
                    gates=[
                        GateResult(
                            name=mcp_decision.gate,
                            status="fail",
                            phase=spec.phase,
                            principles=["P11"],
                            evidence=["mcp-invocations.jsonl"],
                            message=mcp_decision.reason,
                        )
                    ],
                    evidence_ids=[],
                )
        if self.tool_registry is not None:
            self.tool_registry.begin_agent_scope(spec.agent_id, spec.phase, spec.allowed_tools)
        try:
            result = handler(prompt_input)
        finally:
            if self.tool_registry is not None:
                self.tool_registry.end_agent_scope()
        self.invocations.append({"agent_id": spec.agent_id, "phase": spec.phase, "status": result.status})
        return result
