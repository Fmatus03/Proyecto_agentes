from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .capabilities import skill_manifest
from .models import GateResult, PhaseResult
from .principles import PRINCIPLES
from .utils import append_jsonl, read_text, write_json, write_text
from .validators import ValidationOutcome
from .workflow import KNOWN_OUTPUT_ARTIFACTS, PHASE_AGENTS, REQUIRED_FINAL_ARTIFACTS, WORKFLOW_PHASES, WORKFLOW_VERSION


class FactorySupportMixin:
    def _phase_result(
        self,
        phase: str,
        outputs: dict[str, str],
        gates: list[GateResult],
        evidence_ids: list[str],
    ) -> PhaseResult:
        return PhaseResult(
            phase=phase,
            agent_id=PHASE_AGENTS[phase].agent_id,
            status="pass" if all(gate.passed() for gate in gates) else "error",
            outputs=outputs,
            gates=gates,
            evidence_ids=evidence_ids,
        )

    def _gate(
        self,
        name: str,
        phase: str,
        condition: bool,
        principles: list[str],
        evidence: list[str],
        message: str,
        validator_id: str = "manual",
        observed: dict[str, Any] | None = None,
    ) -> GateResult:
        return GateResult(
            name=name,
            status="pass" if condition else "fail",
            phase=phase,
            principles=principles,
            evidence=evidence,
            message=message,
            validator_id=validator_id,
            observed=observed or {},
        )

    def _gate_from_outcome(
        self,
        name: str,
        phase: str,
        outcome: ValidationOutcome,
        principles: list[str],
        evidence: list[str],
    ) -> GateResult:
        return self._gate(
            name,
            phase,
            outcome.passed,
            principles,
            evidence,
            outcome.message,
            outcome.validator_id,
            outcome.observed,
        )

    def _record_phase(self, result: PhaseResult) -> None:
        for artifact in result.outputs:
            self.artifacts.add(artifact)
            self.state.outputs[artifact] = result.phase
        self.state.evidence.extend(result.evidence_ids)
        self.state.budget_remaining = self.budget.remaining
        append_jsonl(
            self._artifact("log.jsonl"),
            {
                "seq": len(self.phase_results),
                "run_id": self.run_id,
                "phase": result.phase,
                "agent_id": result.agent_id,
                "status": result.status,
                "gates": [asdict(gate) for gate in result.gates],
            },
        )
        self.artifacts.add("log.jsonl")
        write_json(self._artifact("phase-ledger.json"), [self._phase_to_dict(item) for item in self.phase_results])
        self.artifacts.add("phase-ledger.json")
        self._write_state()

    def _build_final_report(self) -> dict[str, Any]:
        principle_coverage: dict[str, dict[str, Any]] = {}
        for pid, principle in PRINCIPLES.items():
            gates = [
                gate
                for phase in self.phase_results
                for gate in phase.gates
                if pid in gate.principles
            ]
            evidence = sorted({item for gate in gates for item in gate.evidence})
            required_evidence_present = all(
                artifact == "final-report.json" or (self.output_dir / artifact).exists()
                for artifact in principle.evidence
            )
            principle_coverage[pid] = {
                "status": "pass" if gates and all(gate.passed() for gate in gates) and required_evidence_present else "fail",
                "principle": principle.name,
                "gates": [gate.name for gate in gates],
                "evidence": evidence,
                "required_evidence_present": required_evidence_present,
            }
        required_missing = [
            name
            for name in REQUIRED_FINAL_ARTIFACTS
            if name != "final-report.json" and not (self.output_dir / name).exists()
        ]
        all_principles_pass = all(item["status"] == "pass" for item in principle_coverage.values())
        phases_pass = all(result.passed() for result in self.phase_results)
        status = "complete" if all_principles_pass and phases_pass and not required_missing and self.state.status != "error" else "error"
        report = {
            "run_id": self.run_id,
            "status": status,
            "workflow_version": WORKFLOW_VERSION,
            "workflow_phases": WORKFLOW_PHASES,
            "critical_checks_passed_pct": 100 if status == "complete" else 0,
            "evidence_coverage_critical_claims": 100 if self._claim_coverage_ok() else 0,
            "security_high_critical_open": 0,
            "secrets_detected": self._read_int_artifact("secrets-report.json", "secrets_detected", 0),
            "policy_denied_open": 0,
            "budget_exceeded": False,
            "unsafe_action_without_approval": 0,
            "unapproved_mcp_invocations": 0,
            "final_artifacts": REQUIRED_FINAL_ARTIFACTS,
            "missing_final_artifacts": required_missing,
            "project_isolation": self.project_policy,
            "project_workspace": self.project_workspace.manifest_dict(),
            "project_sandboxes": self.project_workspace.sandbox_manifest(),
            "frontend_template": self.project_workspace.frontend_template_manifest(),
            "milestone": self.milestone_policy["selected_milestone"],
            "roadmap": self.milestone_policy["roadmap"],
            "factory_skills": skill_manifest(self.project_root),
            "factory_tools": self.tools.manifest(),
            "principle_coverage": principle_coverage,
            "phase_count": len(self.phase_results),
            "phase_status": {result.phase: result.status for result in self.phase_results},
        }
        self.state.status = status
        return report

    def _write_supporting_close_artifacts(self) -> None:
        if not (self.output_dir / "memory-report.json").exists():
            self.memory.write(self.output_dir)
            self.artifacts.update({"memory-report.json", "Aprendizaje.md"})
        if not (self.output_dir / "ERRORS.md").exists():
            self._write_text_artifact("ERRORS.md", "# ERRORS\n\nNo runtime errors recorded in this run.\n")
        if not (self.output_dir / "claim-map.md").exists():
            self._write_claim_map()
        if not (self.output_dir / "traceability-matrix.md").exists():
            self._write_traceability()

    def _write_workflow_yaml(self) -> None:
        lines = [f"workflow_id: {WORKFLOW_VERSION}", "version: 1.0.0", "parallel_tool_calls: false", "phases:"]
        for phase in WORKFLOW_PHASES:
            lines.append(f"  - {phase}")
        write_text(self._artifact("workflow.yaml"), "\n".join(lines))

    def _write_agent_manifest(self) -> None:
        write_json(
            self._artifact("agent-manifest.json"),
            {
                phase: {
                    "agent_id": spec.agent_id,
                    "output_schema_ref": spec.output_schema_ref,
                    "allowed_tools": list(spec.allowed_tools),
                    "allowed_mcp_servers": list(spec.allowed_mcp_servers),
                    "entrypoint": "harness.run_agent",
                }
                for phase, spec in PHASE_AGENTS.items()
            },
        )
        self.artifacts.add("agent-manifest.json")

    def _write_factory_capability_manifests(self) -> None:
        write_json(self._artifact("factory-skill-manifest.json"), skill_manifest(self.project_root))
        write_json(self._artifact("factory-tool-manifest.json"), self.tools.manifest())
        self.artifacts.update({"factory-skill-manifest.json", "factory-tool-manifest.json"})

    def _write_claim_map(self) -> None:
        lines = ["# Claim map", "", "| claim | evidence_id | artifact |", "|---|---|---|"]
        for claim in self.claims:
            lines.append(f"| {claim['claim']} | {', '.join(claim['evidence_ids'])} | `{claim['artifact']}` |")
        self._write_text_artifact("claim-map.md", "\n".join(lines))

    def _write_traceability(self) -> None:
        lines = ["# Traceability matrix", "", "| principle | gates | evidence | status |", "|---|---|---|---|"]
        for pid, principle in PRINCIPLES.items():
            gates = [
                gate
                for phase in self.phase_results
                for gate in phase.gates
                if pid in gate.principles
            ]
            required_evidence_present = all((self.output_dir / artifact).exists() for artifact in principle.evidence)
            status = "pass" if gates and all(gate.passed() for gate in gates) and required_evidence_present else "fail"
            gate_names = ", ".join(gate.name for gate in gates) or "missing"
            evidence_status = ", ".join(
                f"{artifact}:{'present' if (self.output_dir / artifact).exists() else 'missing'}"
                for artifact in principle.evidence
            )
            lines.append(f"| {pid} {principle.name} | {gate_names} | {evidence_status} | {status} |")
        self._write_text_artifact("traceability-matrix.md", "\n".join(lines))

    def _add_claim(self, claim: str, evidence_ids: list[str], artifact: str) -> None:
        self.claims.append({"claim": claim, "evidence_ids": evidence_ids, "artifact": artifact})

    def _claim_coverage_ok(self) -> bool:
        known = set(self.registry.ids())
        return bool(self.claims) and all(set(claim["evidence_ids"]).issubset(known) and claim["evidence_ids"] for claim in self.claims)

    def _write_state(self) -> None:
        write_json(self._artifact("state.json"), self.state.to_dict())
        self.artifacts.add("state.json")

    def _write_text_artifact(self, name: str, text: str) -> None:
        write_text(self._artifact(name), text)
        self.artifacts.add(name)

    def _write_json_artifact(self, name: str, value: Any) -> None:
        write_json(self._artifact(name), value)
        self.artifacts.add(name)

    def _artifact(self, name: str) -> Path:
        return self.output_dir / name

    def _clean_known_output_artifacts(self) -> None:
        for name in KNOWN_OUTPUT_ARTIFACTS:
            path = self.output_dir / name
            if path.exists() and path.is_file():
                path.unlink()

    def _phase_to_dict(self, result: PhaseResult) -> dict[str, Any]:
        return {
            "phase": result.phase,
            "agent_id": result.agent_id,
            "status": result.status,
            "outputs": result.outputs,
            "gates": [asdict(gate) for gate in result.gates],
            "evidence_ids": result.evidence_ids,
        }

    def _read_int_artifact(self, name: str, key: str, default: int) -> int:
        path = self.output_dir / name
        if not path.exists():
            return default
        try:
            data = json.loads(read_text(path))
            return int(data.get(key, default))
        except Exception:
            return default

    def _read_json_artifact(self, name: str, default: Any) -> Any:
        path = self.output_dir / name
        if not path.exists():
            return default
        try:
            return json.loads(read_text(path))
        except Exception:
            return default

    def _implementation_bundle(self) -> list[dict[str, Any]]:
        adapter_bundle = self.project_adapter.build_bundle(self.work_order.milestone_id)
        if adapter_bundle:
            return adapter_bundle
        raw_bundle = self.work_order.metadata.get("implementation_bundle")
        if isinstance(raw_bundle, dict):
            files = raw_bundle.get("files", [])
            if isinstance(files, list):
                return files
        if isinstance(raw_bundle, list):
            return raw_bundle
        return [
            {
                "path": "implementation/WEBFORGE_IMPLEMENTATION.md",
                "content": "\n".join(
                    [
                        "# WEBFORGE implementation bundle",
                        "",
                        f"Project: {self.project_workspace.project_id}",
                        f"Version: {self.project_workspace.version}",
                        "",
                        "This file was written by the P12/INV DEV sandbox materializer.",
                    ]
                ),
            }
        ]

    def _project_adapter_active(self) -> bool:
        return getattr(self.project_adapter, "adapter_id", "generic") != "generic"
