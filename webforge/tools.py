from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from .policy import BudgetManager, PolicyDecision
from .utils import append_jsonl, find_secret_hits, read_text, stable_json, write_json


@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    purpose: str
    gate: str
    writes: bool
    timeout_seconds: int


@dataclass
class ToolResult:
    tool_id: str
    status: str
    output: dict[str, Any]
    gate: str


class ToolRegistry:
    version = "toolreg.webforge.v1"

    def __init__(self, output_dir: Path, budget: BudgetManager) -> None:
        self.output_dir = output_dir
        self.budget = budget
        self.agent_scope: dict[str, Any] | None = None
        self.specs: dict[str, ToolSpec] = {
            "tool.sandbox.dev_materialize": ToolSpec(
                "tool.sandbox.dev_materialize",
                "DEV sandbox bundle materialization through P12/INV isolation API",
                "sandbox",
                True,
                30,
            ),
            "tool.security.secrets": ToolSpec("tool.security.secrets", "Secret scan", "secrets", True, 30),
            "tool.security.deps": ToolSpec("tool.security.deps", "Dependency manifest scan", "dependency", True, 30),
            "tool.sbom.generate": ToolSpec("tool.sbom.generate", "SBOM generation", "sbom", True, 30),
            "tool.policy.static": ToolSpec("tool.policy.static", "Static policy scan", "policy", True, 30),
            "tool.validation.artifacts": ToolSpec("tool.validation.artifacts", "Artifact completeness", "final_format", True, 30),
        }

    def manifest(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "default": "deny_unregistered_tools",
            "tools": [asdict(spec) for spec in self.specs.values()],
        }

    def write_manifest(self) -> None:
        write_json(self.output_dir / "tool-registry.json", self.manifest())

    def begin_agent_scope(self, agent_id: str, phase: str, allowed_tools: tuple[str, ...]) -> None:
        self.agent_scope = {"agent_id": agent_id, "phase": phase, "allowed_tools": set(allowed_tools)}

    def end_agent_scope(self) -> None:
        self.agent_scope = None

    def run(self, tool_id: str, func: Callable[[], dict[str, Any]]) -> ToolResult:
        self._log_event(tool_id, "pre", "pending", self.specs.get(tool_id, ToolSpec(tool_id, "unknown", "policy", False, 0)).gate, {})
        if self.agent_scope is not None and tool_id not in self.agent_scope["allowed_tools"]:
            result = ToolResult(
                tool_id,
                "error",
                {
                    "reason": "tool not allowed for current agent",
                    "agent_id": self.agent_scope["agent_id"],
                    "phase": self.agent_scope["phase"],
                    "allowed_tools": sorted(self.agent_scope["allowed_tools"]),
                    "blocking_findings": 1,
                },
                "tool_permission",
            )
            self._log(result)
            return result
        if tool_id not in self.specs:
            result = ToolResult(tool_id, "error", {"reason": "tool not allowlisted"}, "policy")
            self._log(result)
            return result
        budget_decision = self.budget.assert_tool_available(tool_id)
        if not budget_decision.allowed:
            result = ToolResult(tool_id, "error", {"reason": budget_decision.reason}, budget_decision.gate)
            self._log(result)
            return result
        try:
            output = func()
            status = "pass" if not output.get("blocking_findings") else "error"
            result = ToolResult(tool_id, status, output, self.specs[tool_id].gate)
        except Exception as exc:  # pragma: no cover - defensive safe fail
            result = ToolResult(tool_id, "error", {"reason": repr(exc)}, self.specs[tool_id].gate)
        self.budget.record_tool_call(tool_id, result.status)
        self._log(result)
        return result

    def _log(self, result: ToolResult) -> None:
        self._log_event(result.tool_id, "post", result.status, result.gate, result.output)

    def _log_event(self, tool_id: str, stage: str, status: str, gate: str, output: dict[str, Any]) -> None:
        scope = self.agent_scope or {}
        append_jsonl(
            self.output_dir / "tool-logs.jsonl",
            {
                "tool_id": tool_id,
                "stage": stage,
                "status": status,
                "gate": gate,
                "agent_id": scope.get("agent_id", ""),
                "phase": scope.get("phase", ""),
                "allowed_tools": sorted(scope.get("allowed_tools", [])),
                "output_hash": stable_json(output),
            },
        )


def secret_scan(paths: list[Path]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists() or path.is_dir():
            continue
        if path.suffix.lower() not in {".md", ".json", ".yaml", ".yml", ".toml", ".py", ".txt"}:
            continue
        hits = find_secret_hits(read_text(path))
        for hit in hits:
            findings.append({"path": path.name, "match": hit})
    return {"findings": findings, "blocking_findings": len(findings), "secrets_detected": len(findings)}


def dependency_scan(root: Path) -> dict[str, Any]:
    manifests = []
    for name in ["pyproject.toml", "requirements.txt", "package.json", "package-lock.json", "poetry.lock"]:
        if (root / name).exists():
            manifests.append(name)
    return {
        "manifests": manifests,
        "scanner": "local_manifest_policy_scan",
        "high_critical_open": 0,
        "blocking_findings": 0,
        "note": "No external CVE database was called; runtime has no third-party dependencies.",
    }


def generate_sbom(root: Path) -> dict[str, Any]:
    components = [{"name": "python-stdlib", "type": "runtime", "version": "system"}]
    if (root / "pyproject.toml").exists():
        components.append({"name": "webforge-factory", "type": "application", "version": "0.1.0"})
    return {"sbom_format": "webforge.local.v1", "components": components, "blocking_findings": 0}


def static_policy_scan(root: Path) -> dict[str, Any]:
    disallowed_markers = ["direct_" + "model_call(", "invoke_mcp_" + "unchecked(", "external_write_" + "unapproved("]
    findings: list[dict[str, Any]] = []
    for path in (root / "webforge").glob("*.py"):
        text = read_text(path)
        for marker in disallowed_markers:
            if marker in text:
                findings.append({"path": str(path), "marker": marker})
    return {"findings": findings, "blocking_findings": len(findings)}


def artifact_check(output_dir: Path, required: list[str]) -> dict[str, Any]:
    missing = [name for name in required if not (output_dir / name).exists()]
    return {"required": required, "missing": missing, "blocking_findings": len(missing)}
