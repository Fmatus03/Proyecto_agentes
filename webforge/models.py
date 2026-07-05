from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .utils import sha256_file


CLOSED_STATES = {"complete", "needs_user_input", "not_answerable", "error"}


@dataclass
class EvidenceSource:
    evidence_id: str
    path: str
    summary: str
    sha256: str

    @classmethod
    def from_path(cls, evidence_id: str, path: Path, summary: str, root: Path | None = None) -> "EvidenceSource":
        source_path = path
        if root is not None:
            try:
                source_path = path.resolve().relative_to(root.resolve())
            except ValueError:
                source_path = path.resolve()
        return cls(evidence_id=evidence_id, path=source_path.as_posix(), summary=summary, sha256=sha256_file(path))


@dataclass
class WorkOrder:
    objective: str
    project_id: str = ""
    project_version: str = "v0001"
    milestone_id: str = ""
    type: str = "factory_runtime"
    scope: str = "local_artifacts_only"
    side_effects: str = "no_external_writes_no_deploy"
    acceptance_criteria: list[str] = field(default_factory=list)
    authorized_sources: list[str] = field(default_factory=list)
    approvals: dict[str, bool] = field(default_factory=dict)
    budget: dict[str, int | float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkOrder":
        return cls(
            objective=str(data.get("objective", "")).strip(),
            project_id=str(data.get("project_id", data.get("metadata", {}).get("project_id", ""))).strip(),
            project_version=str(data.get("project_version", data.get("metadata", {}).get("project_version", "v0001"))).strip()
            or "v0001",
            milestone_id=str(
                data.get("milestone_id", data.get("milestone", data.get("metadata", {}).get("milestone_id", "")))
            ).strip(),
            type=str(data.get("type", "factory_runtime")).strip() or "factory_runtime",
            scope=str(data.get("scope", "local_artifacts_only")).strip() or "local_artifacts_only",
            side_effects=str(data.get("side_effects", "no_external_writes_no_deploy")).strip()
            or "no_external_writes_no_deploy",
            acceptance_criteria=list(data.get("acceptance_criteria", [])),
            authorized_sources=list(data.get("authorized_sources", [])),
            approvals=dict(data.get("approvals", {})),
            budget=dict(data.get("budget", {})),
            metadata=dict(data.get("metadata", {})),
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.objective:
            errors.append("objective is required")
        if self.project_id and ".." in self.project_id:
            errors.append("project_id cannot contain parent traversal")
        if self.milestone_id and ".." in self.milestone_id:
            errors.append("milestone_id cannot contain parent traversal")
        if self.side_effects not in {"no_external_writes_no_deploy", "approved_external_writes", "approved_deploy"}:
            errors.append("side_effects must be a closed value")
        if not self.acceptance_criteria:
            errors.append("acceptance_criteria must contain at least one measurable item")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GateResult:
    name: str
    status: str
    phase: str
    principles: list[str]
    evidence: list[str]
    message: str
    validator_id: str = "manual"
    observed: dict[str, Any] = field(default_factory=dict)

    def passed(self) -> bool:
        return self.status == "pass"


@dataclass
class PhaseResult:
    phase: str
    agent_id: str
    status: str
    outputs: dict[str, str]
    gates: list[GateResult]
    evidence_ids: list[str]

    def passed(self) -> bool:
        return self.status == "pass" and all(gate.passed() for gate in self.gates)


@dataclass
class CycleState:
    run_id: str
    cycle_id: str
    workflow_version: str
    status: str
    phase: str
    task_id: str
    agent_id: str
    input_hash: str
    spec_hash: str
    plan_hash: str
    tasks_hash: str
    context_pack_id: str
    context_pack_hash: str
    repo_commit: str
    policy_version: str
    tool_registry_version: str
    mcp_registry_version: str
    memory_version: str
    budget_remaining: dict[str, int | float]
    permissions: dict[str, Any]
    outputs: dict[str, str] = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)
    open_risks: list[str] = field(default_factory=list)
    blocked_items: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
