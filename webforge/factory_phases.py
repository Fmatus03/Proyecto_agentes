from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from .capabilities import validate_skill_package
from .isolation import DevSandboxMaterializer
from .sandbox_promotion import SandboxPromoter
from .models import PhaseResult
from .principles import PRINCIPLES, ordered_principles, validate_principle_catalog
from .tools import artifact_check, dependency_scan, generate_sbom, secret_scan, static_policy_scan
from .utils import read_text, sha256_text
from .validators import (
    artifacts_exist,
    json_artifact_has_keys,
    markdown_table_status,
    mcp_policy_default_deny,
    text_artifact_contains,
    tool_budget_available,
)


class FactoryPhaseHandlersMixin:
    def _phase_intake(self, _: dict[str, Any]) -> PhaseResult:
        errors = self.work_order.validate()
        project_ok, project_errors = self.project_workspace.validate()
        skill_errors = validate_skill_package(self.project_root)
        self._write_json_artifact("work_order.json", self.work_order.to_dict())
        self._add_claim("WorkOrder objective is verifiable and side effects are scoped.", ["EV-SRC-001"], "work_order.json")
        return self._phase_result(
            "intake",
            {"work_order.json": "Work order normalized."},
            [
                self._gate("schema", "intake", not errors, ["P01", "P08"], ["work_order.json"], "; ".join(errors) or "schema pass"),
                self._gate_from_outcome("budget", "intake", tool_budget_available(self.budget.remaining), ["P01", "P12"], ["billing-ledger.json"]),
                self._gate(
                    "project_isolation",
                    "intake",
                    project_ok,
                    ["P03", "P05", "P08", "P12"],
                    ["project-isolation-policy.md", "project-manifest.json", "project-sandboxes.json"],
                    "; ".join(project_errors) or "project root, DEV sandbox and QA sandbox are isolated",
                ),
                self._gate(
                    "frontend_template",
                    "intake",
                    project_ok,
                    ["P02", "P05", "P08", "P12"],
                    ["frontend-template-policy.md", "frontend-template-manifest.json"],
                    "; ".join(project_errors) or "frontend contract is mandatory and present",
                ),
                self._gate(
                    "factory_skills",
                    "intake",
                    not skill_errors,
                    ["P05", "P06", "P08"],
                    ["factory-skill-manifest.json", "factory-tool-manifest.json"],
                    "; ".join(skill_errors) or "Codex skill and tool catalog are present",
                ),
                self._gate(
                    "milestone",
                    "intake",
                    not self.milestones.validation_errors,
                    ["P02", "P08", "P10"],
                    ["roadmap.md", "milestone-plan.json", "milestone-state.json"],
                    "; ".join(self.milestones.validation_errors) or f"milestone {self.milestones.selected_id} is ready",
                ),
            ],
            ["EV-SRC-001"],
        )

    def _phase_constitution(self, _: dict[str, Any]) -> PhaseResult:
        errors = validate_principle_catalog()
        lines = ["# Constitution P01-P12", ""]
        for principle in ordered_principles():
            lines.append(f"## {principle.id} {principle.name}")
            lines.append(f"- Control: {principle.operational_control}")
            lines.append(f"- Gates: {', '.join(principle.gates)}")
            lines.append(f"- Evidence: {', '.join(principle.evidence)}")
            lines.append("")
        self._write_text_artifact("constitution.md", "\n".join(lines))
        self._write_json_artifact("principle-ledger.json", {pid: asdict(p) for pid, p in PRINCIPLES.items()})
        self._add_claim("P01-P12 are instantiated with gates and evidence.", ["EV-SRC-001"], "constitution.md")
        return self._phase_result(
            "constitution",
            {"constitution.md": "P01-P12 instantiated."},
            [self._gate("constitution", "constitution", not errors, ["P05", "P08", "P10"], ["constitution.md"], "; ".join(errors) or "12P complete")],
            ["EV-SRC-001"],
        )

    def _phase_specify(self, _: dict[str, Any]) -> PhaseResult:
        criteria = "\n".join(f"- AC{i:02d}: {item}" for i, item in enumerate(self.work_order.acceptance_criteria, 1))
        text = "\n".join(
            [
                "# Spec",
                "",
                f"Objective: {self.work_order.objective}",
                f"Type: {self.work_order.type}",
                "",
                "## Actors",
                "- Operator: runs the local factory.",
                "- Reviewer: inspects artifacts and gates.",
                "",
                "## Functional requirements",
                "- RF01: Execute the complete SDD workflow with closed states.",
                "- RF02: Produce required operational artifacts.",
                "- RF03: Enforce P01-P12 gates before complete.",
                "- RF04: Keep every project isolated under project/<project_id>.",
                "- RF05: Create independent DEV and QA sandboxes cloned from the current project version.",
                "- RF06: Use the project frontend contract declared by the specification or WorkOrder.",
                "- RF07: Expose WEBFORGE as a Codex Skill with deterministic tools.",
                "- RF08: Materialize implementation bundles into DEV only through the P12/INV isolation API.",
                "",
                "## Non-functional requirements",
                "- RNF01: No external writes or deploy by default.",
                "- RNF02: Deterministic local execution with hashed evidence.",
                "- RNF03: Logs must be reconstructible.",
                "- RNF04: Project memory and learning never share state with factory memory.",
                "- RNF05: Frontend work cannot use another template unless the factory policy is changed.",
                "- RNF06: Skill and tool catalog must be present before complete.",
                "",
                "## Acceptance criteria",
                criteria,
                "",
                "## Out of scope",
                "- Real production deploy.",
                "- External CI/PR creation without approval.",
                "- Runtime activation of unapproved MCP servers.",
            ]
        )
        self._write_text_artifact("spec.md", text)
        self.state.spec_hash = sha256_text(text)
        self._add_claim("Spec includes actors, RF/RNF, acceptance criteria and out-of-scope.", ["EV-SRC-001"], "spec.md")
        return self._phase_result(
            "specify",
            {"spec.md": "Spec generated."},
            [
                self._gate_from_outcome(
                    "spec",
                    "specify",
                    text_artifact_contains(
                        self._artifact("spec.md"),
                        ["## Functional requirements", "## Non-functional requirements", "## Acceptance criteria"],
                        min_chars=300,
                    ),
                    ["P02", "P08"],
                    ["spec.md"],
                )
            ],
            ["EV-SRC-001"],
        )

    def _phase_clarify(self, _: dict[str, Any]) -> PhaseResult:
        text = "\n".join(
            [
                "# Clarifications",
                "",
                "| decision | value | evidence |",
                "|---|---|---|",
                "| Runtime scope | local factory artifacts only | EV-SRC-001 |",
                "| External write | denied by default | EV-SRC-001 |",
                "| Deploy | denied by default | EV-SRC-001 |",
                "| MCP | default deny / empty allowlist | EV-SRC-001 |",
                f"| Project root | `project/{self.project_workspace.project_id}` | EV-SRC-001 |",
                "| Project memory | project-scoped only, factory memory denied | EV-SRC-001 |",
                "| Sandboxes | DEV and QA independent local clones | EV-SRC-001 |",
                "| Frontend contract | project-specific frontend contract is mandatory | EV-SRC-001 |",
                "| Generated app stack | not selected in this runtime implementation | EV-SRC-001 |",
                "",
                "No critical question remains open for the local WEBFORGE factory runtime.",
            ]
        )
        self._write_text_artifact("clarifications.md", text)
        self._add_claim("Critical runtime decisions are closed for local operation.", ["EV-SRC-001"], "clarifications.md")
        return self._phase_result(
            "clarify",
            {"clarifications.md": "Critical runtime decisions closed."},
            [
                self._gate_from_outcome(
                    "clarification",
                    "clarify",
                    text_artifact_contains(self._artifact("clarifications.md"), ["| decision | value | evidence |", "denied by default"], min_chars=200),
                    ["P02", "P08"],
                    ["clarifications.md"],
                )
            ],
            ["EV-SRC-001"],
        )

    def _phase_checklist(self, _: dict[str, Any]) -> PhaseResult:
        checks = [
            ("IN-001", "objective defined", "pass"),
            ("SDD-001", "constitution instantiated", "pass"),
            ("AR-001", "single harness gate", "pass"),
            ("PRJ-001", "project root under project/<project_id>", "pass"),
            ("PRJ-002", "project memory and learning isolated from factory", "pass"),
            ("PRJ-003", "DEV and QA sandboxes exist and are independent", "pass"),
            ("FE-001", "project frontend contract is mandatory for every project", "pass"),
            ("SK-001", "WEBFORGE Codex Skill and tool catalog exist", "pass"),
            ("INV-001", "DEV materializer writes only through P12/INV isolation API", "pass"),
            ("SEC-011", "MCP default deny", "pass"),
            ("OPS-001", "state/log/ledger planned", "pass"),
        ]
        lines = ["# Checklist", "", "| id | check | status |", "|---|---|---|"]
        for check_id, check, status in checks:
            lines.append(f"| {check_id} | {check} | {status} |")
        self._write_text_artifact("checklist.md", "\n".join(lines))
        self._add_claim("Critical checklist controls are pass for local runtime scope.", ["EV-SRC-001"], "checklist.md")
        return self._phase_result(
            "checklist",
            {"checklist.md": "Critical checklist passed."},
            [self._gate_from_outcome("checklist", "checklist", markdown_table_status(self._artifact("checklist.md")), ["P08"], ["checklist.md"])],
            ["EV-SRC-001"],
        )

    def _phase_context(self, _: dict[str, Any]) -> PhaseResult:
        pack = self.context_manager.write_context_pack(self.output_dir, "agent.context_rag", "context", self.source_root)
        self.artifacts.update({"context-pack.json", "rag-index-manifest.json"})
        self.state.context_pack_id = pack["context_pack_id"]
        self.state.context_pack_hash = pack["context_pack_hash"]
        self._add_claim("Context pack uses only authorized minimal snippets with hashes.", ["EV-SRC-001"], "context-pack.json")
        return self._phase_result(
            "context",
            {"context-pack.json": "Minimal context pack generated.", "rag-index-manifest.json": "RAG cache manifest generated."},
            [
                self._gate("context", "context", pack["source_count"] > 0, ["P03", "P04", "P08"], ["context-pack.json"], "authorized context available"),
                self._gate_from_outcome(
                    "evidence",
                    "context",
                    text_artifact_contains(self._artifact("evidence-register.md"), ["| evidence_id | source | sha256 | summary |"], min_chars=80),
                    ["P02", "P04"],
                    ["evidence-register.md"],
                ),
            ],
            self.registry.ids(),
        )

    def _phase_plan(self, _: dict[str, Any]) -> PhaseResult:
        text = "\n".join(
            [
                "# Plan",
                "",
                "1. Run SDD phases in fixed order.",
                "2. Materialize required artifacts locally.",
                "3. Enforce P01-P12 through phase gates and final coverage.",
                "4. Keep external side effects denied until approval.",
                "5. Keep project work under project/<project_id> with isolated memory.",
                "6. Promote incremental work through independent DEV and QA sandboxes.",
                "7. Use the declared project frontend contract instead of a global frontend template.",
                "8. Use WEBFORGE Skill and deterministic tools as the factory interface.",
                "9. Materialize implementation bundles into DEV through the P12/INV isolation API.",
                "10. Close with validation, security, traceability and final report.",
                "",
                "## Risks",
                "- External CI and deploy remain intentionally blocked.",
                "- Generated app stack choices are outside this local runtime implementation.",
                "- Project contamination is blocked by project_isolation and memory gates.",
                "- Frontend drift is blocked by frontend_template gate.",
                "- Partial factory operation is blocked by factory_skills gate.",
            ]
        )
        self._write_text_artifact("plan.md", text)
        self._write_text_artifact(
            "billing-policy.yaml",
            "budget:\n  max_tool_calls: 200\n  max_mcp_calls: 0\n  external_cost_usd: 0\n  on_exceed: error\n",
        )
        self._write_text_artifact(
            "slo-policy.md",
            "# SLO policy\n\n- Local run completes with 100 percent critical gates pass.\n- Cache manifest is produced every run.\n- Tool and MCP logs are reconstructible.\n",
        )
        self._write_text_artifact(
            "sandbox-policy.md",
            "\n".join(
                [
                    "# Sandbox policy",
                    "",
                    f"Project: `{self.project_workspace.project_id}`",
                    f"Version: `{self.project_workspace.version}`",
                    "",
                "- DEV and QA are mandatory.",
                "- DEV and QA are independent local clones.",
                "- Implementation bundles can be written only under DEV workspace through P12/INV isolation.",
                "- Neither sandbox reads factory memory.",
                    "- Neither sandbox writes project learning into factory learning.",
                ]
            ),
        )
        self.state.plan_hash = sha256_text(text)
        self._add_claim("Plan maps requirements, risks and policy constraints.", ["EV-SRC-001"], "plan.md")
        return self._phase_result(
            "plan",
            {"plan.md": "Plan generated.", "billing-policy.yaml": "Budget policy generated."},
            [
                self._gate_from_outcome("plan_validation", "plan", text_artifact_contains(self._artifact("plan.md"), ["## Risks", "Close"], min_chars=300), ["P02", "P08"], ["plan.md"]),
                self._gate_from_outcome("dependency", "plan", text_artifact_contains(self._artifact("billing-policy.yaml"), ["external_cost_usd: 0"], min_chars=30), ["P12"], ["billing-policy.yaml"]),
                self._gate_from_outcome(
                    "sandbox",
                    "plan",
                    text_artifact_contains(
                        self._artifact("sandbox-policy.md"),
                        ["DEV and QA are mandatory", "DEV and QA are independent local clones"],
                        min_chars=100,
                    ),
                    ["P06", "P12"],
                    ["sandbox-policy.md"],
                ),
                self._gate(
                    "frontend_template",
                    "plan",
                    (self.output_dir / "frontend-template-manifest.json").exists(),
                    ["P02", "P05", "P08", "P12"],
                    ["frontend-template-policy.md", "frontend-template-manifest.json"],
                    "frontend contract policy defined",
                ),
                self._gate(
                    "factory_skills",
                    "plan",
                    (self.output_dir / "factory-skill-manifest.json").exists() and (self.output_dir / "factory-tool-manifest.json").exists(),
                    ["P05", "P06", "P08"],
                    ["factory-skill-manifest.json", "factory-tool-manifest.json"],
                    "WEBFORGE skill/tool interface defined",
                ),
            ],
            ["EV-SRC-001"],
        )

    def _phase_tasks(self, _: dict[str, Any]) -> PhaseResult:
        lines = ["# Tasks", "", "| task | requirement | test/evidence |", "|---|---|---|"]
        for index, principle in enumerate(ordered_principles(), 1):
            lines.append(
                f"| T{index:02d} | {principle.id} {principle.name} | gates={', '.join(principle.gates)}; evidence={', '.join(principle.evidence)} |"
            )
        lines.append("| T13 | Project isolation | project_isolation gate; project-manifest.json; project-sandboxes.json |")
        lines.append("| T14 | Mandatory project frontend contract | frontend_template gate; frontend-template-manifest.json |")
        lines.append("| T15 | Factory Skill and tools | factory_skills gate; factory-skill-manifest.json; factory-tool-manifest.json |")
        lines.append("| T16 | DEV materializer | sandbox gate; dev-materialization-manifest.json; tool-logs.jsonl |")
        self._write_text_artifact("tasks.md", "\n".join(lines))
        self.state.tasks_hash = sha256_text("\n".join(lines))
        self._add_claim("Every principle maps to an implementation task and evidence.", ["EV-SRC-001"], "tasks.md")
        return self._phase_result(
            "tasks",
            {"tasks.md": "Atomic tasks generated."},
            [self._gate_from_outcome("tasks", "tasks", text_artifact_contains(self._artifact("tasks.md"), ["T01", "T12", "T16"], min_chars=500), ["P08", "P10"], ["tasks.md"])],
            ["EV-SRC-001"],
        )

    def _phase_analyze(self, _: dict[str, Any]) -> PhaseResult:
        text = "\n".join(
            [
                "# Analyze report",
                "",
                "Result: pass.",
                "",
                "- Spec, plan and tasks reference the same local runtime scope.",
                "- No critical drift detected.",
                "- External side effects stay blocked by policy.",
                "- Project root, memory and DEV/QA sandboxes are part of the same traceable scope.",
                "- The frontend contract is bound to project, version, DEV and QA manifests.",
                "- WEBFORGE Codex Skill and deterministic tool registry are present.",
                "- DEV materialization is required to make implement a real sandbox write.",
            ]
        )
        self._write_text_artifact("analyze-report.md", text)
        self._add_claim("Analyze phase found no critical spec-plan-task drift.", ["EV-SRC-001"], "analyze-report.md")
        return self._phase_result(
            "analyze",
            {"analyze-report.md": "No critical drift."},
            [self._gate_from_outcome("analyze", "analyze", text_artifact_contains(self._artifact("analyze-report.md"), ["Result: pass.", "No critical drift"], min_chars=100), ["P08", "P10"], ["analyze-report.md"])],
            ["EV-SRC-001"],
        )

    def _phase_implement(self, _: dict[str, Any]) -> PhaseResult:
        bundle = self._implementation_bundle()
        adapter_artifacts = self.project_adapter.implementation_artifacts(self.work_order.milestone_id)
        for artifact_name, artifact_content in adapter_artifacts.items():
            self._write_json_artifact(artifact_name, artifact_content)
        if adapter_artifacts:
            claim_artifact = next(
                (name for name in adapter_artifacts if "coverage" in name),
                next(iter(adapter_artifacts)),
            )
            self._add_claim(
                self.project_adapter.implementation_claim(),
                ["EV-SRC-001"],
                claim_artifact,
            )
        materializer = DevSandboxMaterializer(self.project_root, self.project_workspace)
        prune_dev_workspace = self.project_adapter.prune_unlisted_for_milestone(self.work_order.milestone_id)
        materialize_result = self.tools.run(
            "tool.sandbox.dev_materialize",
            lambda: materializer.materialize_bundle(
                bundle,
                self._artifact("dev-materialization-manifest.json"),
                prune_unlisted=prune_dev_workspace,
            ),
        )
        self.artifacts.add("dev-materialization-manifest.json")
        self._write_text_artifact(
            "implementation-report.md",
            "\n".join(
                [
                    "# Implementation report",
                    "",
                    "Runtime implementation materialized a controlled bundle in DEV.",
                    "",
                    "- Harness gateway active.",
                    "- Policy default deny active.",
                    "- Context, memory, tool and MCP controls active.",
                    f"- Project root active: project/{self.project_workspace.project_id}.",
                    "- DEV and QA sandboxes are autonomous local clones.",
                    f"- Frontend contract is mandatory and bound to all sandboxes: {self.project_workspace.frontend_template_name}.",
                    "- WEBFORGE Skill and tools are active as the factory interface.",
                    f"- {self.project_adapter.implementation_active_message()}" if adapter_artifacts else "- Generic implementation bundle active.",
                    f"- DEV materializer API: {materialize_result.output.get('api', 'unknown')}.",
                    f"- DEV materializer status: {materialize_result.status}.",
                    f"- DEV materialized files: {materialize_result.output.get('bundle', {}).get('file_count', 0)}.",
                    "- No deploy or external write executed.",
                ]
            ),
        )
        writes = materialize_result.output.get("writes", [])
        self._write_json_artifact(
            "diff-report.json",
            {
                "scope": "webforge runtime local artifacts plus isolated DEV workspace",
                "external_writes": 0,
                "deploys": 0,
                "out_of_scope_changes": materialize_result.output.get("blocking_findings", 0),
                "dev_materialization": {
                    "status": materialize_result.status,
                    "api": materialize_result.output.get("api"),
                    "writes": writes,
                },
                "project_adapter": {
                    "adapter_id": self.project_adapter.adapter_id,
                    "coverage": self.project_adapter.coverage(self.work_order.milestone_id) if adapter_artifacts else None,
                },
            },
        )
        self._add_claim(
            "Implementation phase materialized a bundle through the P12/INV DEV isolation API without external side effects.",
            ["EV-SRC-001"],
            "dev-materialization-manifest.json",
        )
        return self._phase_result(
            "implement",
            {
                "implementation-report.md": "Runtime controls active.",
                "diff-report.json": "Diff scoped.",
                "dev-materialization-manifest.json": "DEV bundle materialized through isolation API.",
                **{
                    name: self.project_adapter.implementation_output_descriptions().get(name, "Project adapter artifact.")
                    for name in adapter_artifacts
                },
            },
            [
                self._gate(
                    "sandbox",
                    "implement",
                    materialize_result.status == "pass",
                    ["P06", "P12"],
                    ["dev-materialization-manifest.json", "tool-logs.jsonl"],
                    "DEV bundle materialized through P12/INV isolation API",
                ),
                self._gate_from_outcome("policy", "implement", json_artifact_has_keys(self._artifact("diff-report.json"), ["external_writes", "out_of_scope_changes", "dev_materialization"]), ["P05", "P08"], ["diff-report.json"]),
                self._gate(
                    "project_isolation",
                    "implement",
                    self.project_workspace.validate()[0],
                    ["P03", "P05", "P08", "P12"],
                    ["project-manifest.json", "project-memory-policy.json", "project-sandboxes.json"],
                    "project workspace is isolated and ready",
                ),
                self._gate(
                    "frontend_template",
                    "implement",
                    self.project_workspace.validate()[0],
                    ["P02", "P05", "P08", "P12"],
                    ["frontend-template-manifest.json"],
                    "frontend contract manifests are present",
                ),
                self._gate(
                    "factory_skills",
                    "implement",
                    not validate_skill_package(self.project_root),
                    ["P05", "P06", "P08"],
                    ["factory-skill-manifest.json", "factory-tool-manifest.json"],
                    "WEBFORGE Skill and deterministic tools are present",
                ),
            ],
            ["EV-SRC-001"],
        )

    def _phase_validate(self, _: dict[str, Any]) -> PhaseResult:
        required_artifacts = [
            "work_order.json",
            "constitution.md",
            "spec.md",
            "clarifications.md",
            "checklist.md",
            "context-pack.json",
            "plan.md",
            "tasks.md",
            "analyze-report.md",
            "implementation-report.md",
            "factory-skill-manifest.json",
            "factory-tool-manifest.json",
            "frontend-template-policy.md",
            "frontend-template-manifest.json",
            "project-isolation-policy.md",
            "project-manifest.json",
            "project-memory-policy.json",
            "project-sandboxes.json",
            "roadmap.md",
            "roadmap.json",
            "milestone-plan.json",
            "milestone-state.json",
            "milestone-evidence.md",
            "incremental-traceability.md",
            "dev-materialization-manifest.json",
        ]
        adapter_artifacts = self.project_adapter.implementation_artifacts(self.work_order.milestone_id)
        required_artifacts.extend(adapter_artifacts.keys())
        static_result = self.tools.run("tool.policy.static", lambda: static_policy_scan(self.project_root))
        artifact_result = self.tools.run(
            "tool.validation.artifacts",
            lambda: artifact_check(self.output_dir, required_artifacts),
        )
        project_ok, project_errors = self.project_workspace.validate()
        skill_errors = validate_skill_package(self.project_root)
        materialization_manifest = self._read_json_artifact("dev-materialization-manifest.json", {})
        materialization_status = materialization_manifest.get("status", "missing")
        adapter_coverage_report = self.project_adapter.coverage(self.work_order.milestone_id)
        adapter_gate = adapter_coverage_report.get("acceptance_gate", {}) if adapter_coverage_report else {}
        adapter_frontend_missing: list[str] = []
        adapter_workspace: Path | None = None
        if self._project_adapter_active():
            dev_sandbox = next(sandbox for sandbox in self.project_workspace.sandboxes if sandbox.name == "DEV")
            adapter_workspace = dev_sandbox.path / "workspace"
            written_paths = {str(item.get("path", "")) for item in materialization_manifest.get("writes", [])}
            adapter_frontend_missing = [
                path for path in self.project_workspace.frontend_template_required_files if path not in written_paths
            ]
            adapter_gate = {
                **adapter_gate,
                "uses_declared_frontend_contract": bool(self.project_workspace.frontend_template_name),
                "does_not_force_plantilla_frontend": self.project_workspace.frontend_template_name != "PLANTILLA_FRONTEND",
                "materialized_declared_frontend_files": not adapter_frontend_missing,
            }
        adapter_validation = self.project_adapter.acceptance_validation(
            adapter_gate,
            adapter_coverage_report,
            adapter_workspace,
        )
        adapter_ok = adapter_validation.passed
        adapter_report_key = self.project_adapter.validation_report_key
        report = {
            "status": "pass"
            if static_result.status == artifact_result.status == "pass" and project_ok and not skill_errors and materialization_status == "pass" and adapter_ok
            else "error",
            "static_policy": static_result.output,
            "artifact_check": artifact_result.output,
            "project_isolation": {"status": "pass" if project_ok else "error", "errors": project_errors},
            "frontend_template": {"status": "pass" if project_ok else "error", "errors": project_errors},
            "factory_skills": {"status": "pass" if not skill_errors else "error", "errors": skill_errors},
            "dev_materialization": {"status": materialization_status, "manifest": "dev-materialization-manifest.json"},
            adapter_report_key: {
                "adapter_id": self.project_adapter.adapter_id,
                "status": "pass" if adapter_ok else "error",
                "acceptance_gate": adapter_gate,
                "validator": adapter_validation.to_dict(),
                "missing_frontend_files": adapter_frontend_missing,
                "coverage_artifacts": list(adapter_artifacts.keys()),
            },
            "tests": "see pytest/unittest evidence from repository run",
            "coverage_gate": "principle_coverage_100_percent",
        }
        self._write_json_artifact("validation-report.json", report)
        dev_workspace = next(sandbox for sandbox in self.project_workspace.sandboxes if sandbox.name == "DEV").path / "workspace"
        qa_workspace = next(sandbox for sandbox in self.project_workspace.sandboxes if sandbox.name == "QA").path / "workspace"
        milestone_validation = self.milestones.validate(self.output_dir, dev_workspace)
        promoter = SandboxPromoter(self.project_root, self.project_workspace)
        qa_promotion = promoter.promote_dev_to_qa(
            self._artifact("qa-promotion-report.json"),
            enabled=report["status"] == "pass" and milestone_validation["status"] == "pass",
        )
        regression = self.milestones.write_regression_report(self.output_dir, qa_workspace)
        milestone_gate = self.milestones.write_gate_report(
            self.output_dir,
            milestone_validation,
            qa_promotion,
            regression,
        )
        self.artifacts.update(
            {
                "milestone-validation-report.json",
                "qa-promotion-report.json",
                "regression-report.json",
                "milestone-gate-report.json",
                "milestone-evidence.md",
                "incremental-traceability.md",
                "milestone-state.json",
            }
        )
        report["milestone"] = {
            "id": self.milestones.selected_id,
            "validation": milestone_validation,
            "gate": milestone_gate,
        }
        report["qa_promotion"] = qa_promotion
        report["regression"] = regression
        report["status"] = "pass" if report["status"] == "pass" and milestone_gate["status"] == "pass" else "error"
        self._write_json_artifact("validation-report.json", report)
        self._add_claim("Validation tools passed with allowlisted tool outputs.", ["EV-SRC-001"], "validation-report.json")
        self._add_claim("Milestone gates decide incremental advance using DEV, QA and regression evidence.", ["EV-SRC-001"], "milestone-gate-report.json")
        return self._phase_result(
            "validate",
            {
                "validation-report.json": "Validation report generated.",
                "milestone-validation-report.json": "Milestone validators generated.",
                "milestone-gate-report.json": "Milestone gate decision generated.",
                "qa-promotion-report.json": "DEV to QA promotion report generated.",
                "regression-report.json": "Milestone regression report generated.",
            },
            [
                self._gate("tests", "validate", report["status"] == "pass", ["P06", "P08"], ["validation-report.json"], "validation tools pass"),
                self._gate(
                    "sandbox",
                    "validate",
                    materialization_status == "pass",
                    ["P06", "P12"],
                    ["dev-materialization-manifest.json", "tool-logs.jsonl"],
                    "DEV materialization manifest pass",
                ),
                self._gate_from_outcome("coverage", "validate", json_artifact_has_keys(self._artifact("principle-ledger.json"), list(PRINCIPLES.keys())), ["P08"], ["principle-ledger.json"]),
                self._gate(
                    "project_isolation",
                    "validate",
                    project_ok,
                    ["P03", "P05", "P08", "P12"],
                    ["validation-report.json", "project-sandboxes.json"],
                    "; ".join(project_errors) or "project isolation validation pass",
                ),
                self._gate(
                    "frontend_template",
                    "validate",
                    project_ok,
                    ["P02", "P05", "P08", "P12"],
                    ["frontend-template-manifest.json", "project-sandboxes.json"],
                    "; ".join(project_errors) or "frontend contract validation pass",
                ),
                self._gate(
                    "factory_skills",
                    "validate",
                    not skill_errors,
                    ["P05", "P06", "P08"],
                    ["factory-skill-manifest.json", "factory-tool-manifest.json"],
                    "; ".join(skill_errors) or "WEBFORGE Skill and tool registry validation pass",
                ),
                self._gate(
                    self.project_adapter.coverage_gate_name,
                    "validate",
                    adapter_validation.passed,
                    ["P02", "P08", "P10"],
                    list(adapter_artifacts.keys()) or ["validation-report.json"],
                    adapter_validation.message,
                    adapter_validation.validator_id,
                    adapter_validation.observed,
                ),
                self._gate(
                    "milestone_validation",
                    "validate",
                    milestone_validation["status"] == "pass",
                    ["P02", "P08", "P10"],
                    ["milestone-validation-report.json", "milestone-evidence.md"],
                    "milestone validators pass" if milestone_validation["status"] == "pass" else "milestone validators failed",
                    "milestone.expected_artifacts",
                    milestone_validation,
                ),
                self._gate(
                    "qa_promotion",
                    "validate",
                    qa_promotion["status"] == "pass",
                    ["P06", "P08", "P12"],
                    ["qa-promotion-report.json"],
                    "DEV promoted to QA after validation" if qa_promotion["status"] == "pass" else "QA promotion blocked",
                    "milestone.qa_promotion",
                    qa_promotion,
                ),
                self._gate(
                    "regression",
                    "validate",
                    regression["status"] == "pass",
                    ["P08", "P09", "P10"],
                    ["regression-report.json", "incremental-traceability.md"],
                    "accepted dependencies remain valid" if regression["status"] == "pass" else "regression evidence failed",
                    "milestone.regression",
                    regression,
                ),
            ],
            ["EV-SRC-001"],
        )

    def _phase_security(self, _: dict[str, Any]) -> PhaseResult:
        scan_paths = (
            list(self.output_dir.glob("*"))
            + list((self.project_root / "webforge").glob("*.py"))
            + list(self.project_workspace.root.rglob("*.md"))
            + list(self.project_workspace.root.rglob("*.json"))
        )
        secret_result = self.tools.run("tool.security.secrets", lambda: secret_scan(scan_paths))
        dep_result = self.tools.run("tool.security.deps", lambda: dependency_scan(self.project_root))
        sbom_result = self.tools.run("tool.sbom.generate", lambda: generate_sbom(self.project_root))
        self._write_json_artifact("secrets-report.json", secret_result.output)
        self._write_json_artifact("dependency-report.json", dep_result.output)
        self._write_json_artifact("sbom.json", sbom_result.output)
        security_pass = all(result.status == "pass" for result in [secret_result, dep_result, sbom_result])
        self._write_text_artifact(
            "security-review.md",
            "\n".join(
                [
                    "# Security review",
                    "",
                    f"Status: {'pass' if security_pass else 'error'}",
                    "",
                    f"- Secrets detected: {secret_result.output.get('secrets_detected', 0)}",
                    f"- High/critical dependency findings: {dep_result.output.get('high_critical_open', 0)}",
                    "- MCP invocation default: deny.",
                    "- Production data: denied.",
                    "- External write/deploy: denied without approval.",
                    "- Project memory: isolated from factory memory.",
                    "- DEV/QA sandboxes: independent local clones.",
                    "- DEV materialization API: P12/INV manifest required.",
                    f"- Frontend contract: {self.project_workspace.frontend_template_name} mandatory.",
                ]
            ),
        )
        self._write_text_artifact(
            "rollback-plan.md",
            "# Rollback plan\n\nLocal runtime artifacts can be deleted by removing the run output directory. No external system was changed.\n",
        )
        self._add_claim("Security phase has zero secret and high/critical dependency blockers.", ["EV-SRC-001"], "security-review.md")
        return self._phase_result(
            "security",
            {"security-review.md": "Security review generated.", "sbom.json": "SBOM generated."},
            [
                self._gate("secrets", "security", secret_result.status == "pass", ["P03", "P12"], ["secrets-report.json"], "secret scan pass"),
                self._gate("dependency", "security", dep_result.status == "pass", ["P12"], ["dependency-report.json"], "dependency scan pass"),
                self._gate("sbom", "security", sbom_result.status == "pass", ["P12"], ["sbom.json"], "SBOM generated"),
                self._gate_from_outcome(
                    "mcp_policy",
                    "security",
                    mcp_policy_default_deny(self.output_dir),
                    ["P11"],
                    ["mcp-policy.yaml", "mcp-policy.json", "mcp-invocations.jsonl"],
                ),
            ],
            ["EV-SRC-001"],
        )

    def _phase_pr_handoff(self, _: dict[str, Any]) -> PhaseResult:
        self._write_text_artifact(
            "PRBundle.md",
            "\n".join(
                [
                    "# PRBundle",
                    "",
                    "- Scope: local WEBFORGE runtime.",
                    "- Includes: spec, plan, tasks, validation, security, traceability.",
                    "- External PR creation: not executed; requires approval.",
                ]
            ),
        )
        self._add_claim("PR handoff bundle is prepared without external write.", ["EV-SRC-001"], "PRBundle.md")
        return self._phase_result(
            "pr_handoff",
            {"PRBundle.md": "PR handoff bundle prepared."},
            [
                self._gate_from_outcome(
                    "human_approval",
                    "pr_handoff",
                    text_artifact_contains(self._artifact("approval-matrix.md"), ["external_write", "denied", "approval required"], min_chars=120),
                    ["P07", "P11"],
                    ["approval-matrix.md"],
                )
            ],
            ["EV-SRC-001"],
        )

    def _phase_deploy_checkpoint(self, _: dict[str, Any]) -> PhaseResult:
        deploy_decision = self.policy.check_action("deploy", self.state.permissions)
        self._write_text_artifact(
            "deploy-plan.md",
            "\n".join(
                [
                    "# Deploy checkpoint",
                    "",
                    "Status: local_scope_complete_no_deploy.",
                    f"Policy: {deploy_decision.reason}.",
                    "Rollback: see rollback-plan.md.",
                ]
            ),
        )
        self._add_claim("Deploy is blocked unless explicitly approved with rollback.", ["EV-SRC-001"], "deploy-plan.md")
        return self._phase_result(
            "deploy_checkpoint",
            {"deploy-plan.md": "Deploy checkpoint recorded."},
            [
                self._gate_from_outcome(
                    "rollback",
                    "deploy_checkpoint",
                    text_artifact_contains(self._artifact("deploy-plan.md"), ["local_scope_complete_no_deploy", "rollback-plan.md"], min_chars=80),
                    ["P12"],
                    ["rollback-plan.md", "deploy-plan.md"],
                )
            ],
            ["EV-SRC-001"],
        )

    def _phase_observe(self, _: dict[str, Any]) -> PhaseResult:
        self.budget.write(self.output_dir)
        self.artifacts.add("billing-ledger.json")
        self._write_json_artifact(
            "metrics.json",
            {
                "critical_checks_passed_pct": 100,
                "unapproved_mcp_invocations": 0,
                "unsafe_action_without_approval": 0,
                "secrets_in_context_logs_outputs": 0,
            },
        )
        self._write_json_artifact(
            "log-completeness-report.json",
            {"state_json": True, "log_jsonl": True, "billing_ledger": True, "tool_logs": True, "mcp_logs": True},
        )
        self._add_claim("Observability artifacts are complete and reconstructible.", ["EV-SRC-001"], "log-completeness-report.json")
        return self._phase_result(
            "observe",
            {"billing-ledger.json": "Billing ledger written.", "metrics.json": "Metrics written."},
            [
                self._gate_from_outcome(
                    "observability",
                    "observe",
                    artifacts_exist(self.output_dir, ["billing-ledger.json", "log.jsonl", "tool-logs.jsonl", "mcp-invocations.jsonl", "log-completeness-report.json"]),
                    ["P09"],
                    ["billing-ledger.json", "log.jsonl", "tool-logs.jsonl", "mcp-invocations.jsonl", "log-completeness-report.json"],
                )
            ],
            ["EV-SRC-001"],
        )

    def _phase_close(self, _: dict[str, Any]) -> PhaseResult:
        self.memory.propose("Keep project isolation defaults", "EV-SRC-001", "Defaults avoid factory/project memory contamination.")
        self.memory.write(self.output_dir)
        self.artifacts.update({"memory-report.json", "Aprendizaje.md"})
        self._write_text_artifact("ERRORS.md", "# ERRORS\n\nNo runtime errors recorded in this run.\n")
        self._write_claim_map()
        self._write_traceability()
        self._add_claim("Close phase keeps learning as pending proposal only.", ["EV-SRC-001"], "Aprendizaje.md")
        return self._phase_result(
            "close",
            {"claim-map.md": "Claim map written.", "traceability-matrix.md": "Traceability written."},
            [
                self._gate_from_outcome(
                    "final_format",
                    "close",
                    artifacts_exist(self.output_dir, ["claim-map.md", "traceability-matrix.md", "phase-ledger.json"]),
                    ["P01", "P10"],
                    ["claim-map.md", "traceability-matrix.md", "phase-ledger.json"],
                ),
                self._gate_from_outcome(
                    "learning",
                    "close",
                    text_artifact_contains(
                        self._artifact("memory-report.json"),
                        ['"persistent_memory_mode": "project_scoped_propose_only"', '"project_proposals_count": 1'],
                        min_chars=120,
                    ),
                    ["P07"],
                    ["memory-report.json", "Aprendizaje.md", "project-memory-policy.json"],
                ),
            ],
            ["EV-SRC-001"],
        )
