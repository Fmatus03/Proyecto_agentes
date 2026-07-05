from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .brewmaster import is_brewmaster_work_order
from .models import WorkOrder
from .project_workspace import ProjectWorkspace
from .utils import ensure_dir, read_text, sha256_text, stable_json, write_json, write_text


MILESTONE_STATES = {"pending", "in_progress", "validated", "approved", "rejected"}
MILESTONE_ARTIFACTS = {
    "roadmap.md",
    "roadmap.json",
    "milestone-plan.json",
    "milestone-state.json",
    "milestone-validation-report.json",
    "milestone-gate-report.json",
    "milestone-evidence.md",
    "regression-report.json",
    "incremental-traceability.md",
}


@dataclass(frozen=True)
class MilestoneSpec:
    milestone_id: str
    name: str
    objective: str
    scope: str
    inputs: list[str]
    outputs: list[str]
    dependencies: list[str]
    agents: list[str]
    allowed_tools: list[str]
    expected_artifacts: list[str]
    acceptance_criteria: list[str]
    validators: list[str]
    gates: list[str]
    risks: list[str]
    state: str = "pending"
    evidence: list[str] = field(default_factory=list)
    traceability: list[str] = field(default_factory=list)


def _spec(
    milestone_id: str,
    name: str,
    objective: str,
    scope: str,
    expected_artifacts: list[str],
    dependencies: list[str] | None = None,
    inputs: list[str] | None = None,
    outputs: list[str] | None = None,
    acceptance_criteria: list[str] | None = None,
    validators: list[str] | None = None,
    risks: list[str] | None = None,
) -> MilestoneSpec:
    return MilestoneSpec(
        milestone_id=milestone_id,
        name=name,
        objective=objective,
        scope=scope,
        inputs=inputs or ["WorkOrder", "authorized_sources", "project ROADMAP.md"],
        outputs=outputs or ["DEV implementation bundle", "QA promotion report", "milestone evidence"],
        dependencies=dependencies or [],
        agents=[
            "agent.intake",
            "agent.architect_planner",
            "agent.implementer",
            "agent.qa",
            "agent.security",
            "agent.close",
        ],
        allowed_tools=[
            "tool.sandbox.dev_materialize",
            "tool.policy.static",
            "tool.validation.artifacts",
            "tool.security.secrets",
            "tool.security.deps",
            "tool.sbom.generate",
        ],
        expected_artifacts=expected_artifacts,
        acceptance_criteria=acceptance_criteria
        or [
            "Expected artifacts exist in the run output or DEV workspace.",
            "Milestone validators pass with evidence.",
            "DEV workspace is promoted to QA only after validation passes.",
            "Regression evidence for accepted dependencies is present.",
        ],
        validators=validators
        or [
            "milestone.expected_artifacts",
            "milestone.dependencies",
            "milestone.qa_promotion",
            "milestone.regression",
        ],
        gates=["milestone_validation", "qa_promotion", "regression"],
        risks=risks or ["Milestone scope can drift if expected artifacts are not updated with implementation reality."],
        traceability=["requirement -> use_case -> milestone -> agent -> tool -> artifact -> validator -> gate -> report"],
    )


def default_milestones(work_order: WorkOrder) -> list[MilestoneSpec]:
    if is_brewmaster_work_order(work_order):
        return [
            _spec(
                "HITO-001",
                "Fundamentos",
                "Establecer Auth JWT, usuarios, roles, permisos, auditoria y estructura base del proyecto.",
                "J.12 Fundamentos",
                [
                    "contracts/permissions.json",
                    "backend/app/core/security.py",
                    "backend/app/main.py",
                    "frontend/src/App.jsx",
                    "tests/test_contracts.py",
                ],
                inputs=["J.12 Hito 1", "H", "J.4", "J.7", "J.8 RNF-01/RNF-02"],
            ),
            _spec(
                "HITO-002",
                "Maestros",
                "Implementar proveedores, insumos, bodegas, recetas y tipos de presentacion como maestros operativos.",
                "J.12 Maestros",
                [
                    "backend/app/domain/catalog.py",
                    "backend/app/services/inventory.py",
                    "contracts/domain-model.json",
                    "frontend/src/screens/catalog.js",
                    "docs/architecture.md",
                ],
                dependencies=["HITO-001"],
                inputs=["J.12 Hito 2", "UC-INS-*", "UC-REC-*", "P-04..P-13", "J.5"],
            ),
            _spec(
                "HITO-003",
                "Inventario",
                "Implementar entradas de insumos, Kardex, notificaciones por email y configuracion SMTP.",
                "J.12 Inventario",
                [
                    "backend/app/services/inventory.py",
                    "backend/app/services/notifications.py",
                    "backend/app/domain/rules.py",
                    "contracts/permissions.json",
                    "tests/test_domain_rules.py",
                ],
                dependencies=["HITO-002"],
                inputs=["J.12 Hito 3", "UC-INS-02", "UC-INS-03", "UC-ALT-01", "J.6", "J.13"],
            ),
            _spec(
                "HITO-004",
                "Produccion",
                "Construir lotes, control de calidad, mermas e inventario de productos terminados.",
                "J.12 Produccion",
                [
                    "backend/app/services/production.py",
                    "backend/app/domain/rules.py",
                    "contracts/coverage.json",
                    "docs/api-contract.md",
                    "tests/test_domain_rules.py",
                ],
                dependencies=["HITO-003"],
                inputs=["J.12 Hito 4", "UC-PROD-*", "UC-PRO-*", "P-14..P-19", "J.6"],
            ),
            _spec(
                "HITO-005",
                "Ventas",
                "Cerrar clientes, ventas, reservas de stock, precios por tipo de cliente y ordenes de compra.",
                "J.12 Ventas",
                [
                    "backend/app/services/sales.py",
                    "backend/app/services/purchasing.py",
                    "backend/app/services/inventory.py",
                    "docs/traceability.md",
                    "tests/test_domain_rules.py",
                ],
                dependencies=["HITO-004"],
                inputs=["J.12 Hito 5", "UC-VTA-*", "UC-COM-*", "P-20..P-25", "J.6", "J.14"],
            ),
            _spec(
                "HITO-006",
                "Dashboard",
                "Implementar KPIs reales, graficos, alertas operacionales y reportes exportables.",
                "J.12 Dashboard",
                [
                    "frontend/src/App.jsx",
                    "frontend/src/screens/catalog.js",
                    "backend/app/jobs/scheduler.py",
                    "docs/api-contract.md",
                    "tests/test_domain_rules.py",
                ],
                dependencies=["HITO-005"],
                inputs=["J.12 Hito 6", "UC-REP-*", "P-03", "P-29", "J.13"],
            ),
            _spec(
                "HITO-007",
                "Cierre",
                "Completar equipos, finanzas, metas, respaldos automaticos, documentacion y pruebas.",
                "J.12 Cierre",
                [
                    "backend/app/services/purchasing.py",
                    "backend/app/jobs/scheduler.py",
                    "docs/architecture.md",
                    "docs/traceability.md",
                    "docs/test-strategy.md",
                    "tests/test_contracts.py",
                ],
                dependencies=["HITO-006"],
                inputs=["J.12 Hito 7", "UC-EQU-*", "UC-FIN-*", "UC-ALT-*", "J.10", "J.15"],
            ),
        ]
    return [
        _spec(
            "HITO-001",
            "Base verificable del proyecto",
            "Materializar el primer incremento controlado del proyecto.",
            "generic project foundation",
            ["implementation/WEBFORGE_IMPLEMENTATION.md"],
        ),
        _spec(
            "HITO-002",
            "Validacion incremental",
            "Agregar validadores y evidencia sobre el incremento base.",
            "generic validation increment",
            ["validation-report.json", "traceability-matrix.md"],
            dependencies=["HITO-001"],
        ),
    ]


def synthetic_full_run_milestone(work_order: WorkOrder) -> MilestoneSpec:
    expected = [
        "implementation-report.md",
        "validation-report.json",
        "dev-materialization-manifest.json",
    ]
    if is_brewmaster_work_order(work_order):
        expected.extend(["brewmaster-blueprint.json", "brewmaster-coverage.json"])
    return _spec(
        "FULL-RUN",
        "Corrida completa compatible",
        "Mantener compatibilidad con el workflow completo mientras el proyecto adopta hitos incrementales.",
        "full workflow compatibility",
        expected,
        risks=["This is a compatibility mode; project delivery should prefer explicit HITO-* runs."],
    )


class MilestoneManager:
    def __init__(self, project_workspace: ProjectWorkspace, work_order: WorkOrder) -> None:
        self.project_workspace = project_workspace
        self.work_order = work_order
        self.project_root = project_workspace.root
        self.milestones_root = self.project_root / "milestones"
        self.roadmap_json_path = self.project_root / "roadmap.json"
        self.roadmap_md_path = self.project_root / "ROADMAP.md"
        self.milestones = self._load_or_default()
        requested = work_order.milestone_id.strip()
        self.selected = self._milestone_by_id(requested) if requested else synthetic_full_run_milestone(work_order)
        self.validation_errors = [] if self.selected else [f"unknown milestone {requested}"]
        if self.selected is None:
            self.selected = synthetic_full_run_milestone(work_order)

    @property
    def selected_id(self) -> str:
        return self.selected.milestone_id

    def prepare(self, output_dir: Path) -> dict[str, Any]:
        ensure_dir(self.milestones_root)
        roadmap = self.roadmap_dict()
        write_json(self.roadmap_json_path, roadmap)
        write_text(self.roadmap_md_path, self._roadmap_markdown())
        write_json(output_dir / "roadmap.json", roadmap)
        write_text(output_dir / "roadmap.md", self._roadmap_markdown())
        write_json(output_dir / "milestone-plan.json", asdict(self.selected))
        self._write_state(output_dir, "pending", "milestone prepared", [])
        self._write_evidence(output_dir, [], [], "pending")
        self._write_incremental_traceability(output_dir, "pending", {})
        return {"selected_milestone": asdict(self.selected), "roadmap": roadmap}

    def start(self, run_id: str, output_dir: Path) -> None:
        self._write_state(output_dir, "in_progress", f"started by {run_id}", [])

    def validate(self, output_dir: Path, dev_workspace: Path) -> dict[str, Any]:
        missing = []
        present = []
        for artifact in self.selected.expected_artifacts:
            candidates = [output_dir / artifact, dev_workspace / artifact]
            if any(candidate.exists() for candidate in candidates):
                present.append(artifact)
            else:
                missing.append(artifact)
        dependency_results = self._dependency_results()
        dependency_failures = [item for item in dependency_results if item["status"] not in {"validated", "approved"}]
        errors = list(self.validation_errors)
        status = "pass" if not missing and not dependency_failures and not errors else "error"
        report = {
            "milestone_id": self.selected_id,
            "status": status,
            "expected_artifacts": self.selected.expected_artifacts,
            "present_artifacts": present,
            "missing_artifacts": missing,
            "dependencies": dependency_results,
            "errors": errors,
            "validators": self.selected.validators,
            "acceptance_criteria": self.selected.acceptance_criteria,
            "observed_hash": sha256_text(stable_json({"present": present, "dependencies": dependency_results})),
        }
        write_json(output_dir / "milestone-validation-report.json", report)
        return report

    def write_regression_report(self, output_dir: Path, qa_workspace: Path) -> dict[str, Any]:
        checked = []
        for dependency in self.selected.dependencies:
            state = self._read_project_state(dependency)
            checked.append(
                {
                    "milestone_id": dependency,
                    "status": state.get("status", "pending"),
                    "state_file": str((self.milestones_root / dependency / "milestone-state.json").relative_to(self.project_workspace.factory_root)),
                }
            )
        missing_qa = []
        if self.selected.dependencies:
            for artifact in self.selected.expected_artifacts:
                if "/" in artifact and not (qa_workspace / artifact).exists():
                    missing_qa.append(artifact)
        status = "pass" if not missing_qa and all(item["status"] in {"validated", "approved"} for item in checked) else "error"
        if not self.selected.dependencies:
            status = "pass"
        report = {
            "milestone_id": self.selected_id,
            "status": status,
            "checked_dependencies": checked,
            "missing_qa_artifacts": missing_qa,
            "strategy": "accepted dependency milestones must remain validated or approved",
        }
        write_json(output_dir / "regression-report.json", report)
        return report

    def write_gate_report(
        self,
        output_dir: Path,
        milestone_validation: dict[str, Any],
        qa_promotion: dict[str, Any],
        regression: dict[str, Any],
    ) -> dict[str, Any]:
        gate_status = (
            "pass"
            if milestone_validation.get("status") == qa_promotion.get("status") == regression.get("status") == "pass"
            else "error"
        )
        report = {
            "milestone_id": self.selected_id,
            "status": gate_status,
            "gates": {
                "milestone_validation": milestone_validation.get("status"),
                "qa_promotion": qa_promotion.get("status"),
                "regression": regression.get("status"),
            },
            "decision": "advance" if gate_status == "pass" else "block",
            "evidence": [
                "milestone-validation-report.json",
                "qa-promotion-report.json",
                "regression-report.json",
            ],
        }
        write_json(output_dir / "milestone-gate-report.json", report)
        self._write_state(
            output_dir,
            "approved" if gate_status == "pass" else "rejected",
            f"milestone gate {gate_status}",
            report["evidence"],
        )
        self._write_evidence(
            output_dir,
            milestone_validation.get("present_artifacts", []),
            report["evidence"],
            "approved" if gate_status == "pass" else "rejected",
        )
        self._write_incremental_traceability(output_dir, gate_status, report["gates"])
        return report

    def roadmap_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_workspace.project_id,
            "version": "roadmap.webforge.incremental.v1",
            "selected_milestone": self.selected_id,
            "milestones": [asdict(milestone) for milestone in self.milestones],
        }

    def _load_or_default(self) -> list[MilestoneSpec]:
        if self.roadmap_json_path.exists():
            try:
                data = json.loads(read_text(self.roadmap_json_path))
                return [MilestoneSpec(**item) for item in data.get("milestones", [])]
            except Exception:
                return default_milestones(self.work_order)
        return default_milestones(self.work_order)

    def _milestone_by_id(self, milestone_id: str) -> MilestoneSpec | None:
        for milestone in self.milestones:
            if milestone.milestone_id == milestone_id:
                return milestone
        return None

    def _dependency_results(self) -> list[dict[str, str]]:
        results = []
        for dependency in self.selected.dependencies:
            state = self._read_project_state(dependency)
            results.append({"milestone_id": dependency, "status": str(state.get("status", "pending"))})
        return results

    def _read_project_state(self, milestone_id: str) -> dict[str, Any]:
        path = self.milestones_root / milestone_id / "milestone-state.json"
        if not path.exists():
            return {"status": "pending"}
        try:
            return json.loads(read_text(path))
        except Exception:
            return {"status": "rejected", "error": "invalid milestone state"}

    def _write_state(self, output_dir: Path, status: str, reason: str, evidence: list[str]) -> None:
        status = status if status in MILESTONE_STATES else "rejected"
        state = {
            "milestone_id": self.selected_id,
            "status": status,
            "reason": reason,
            "project_id": self.project_workspace.project_id,
            "version": self.project_workspace.version,
            "dependencies": self.selected.dependencies,
            "expected_artifacts": self.selected.expected_artifacts,
            "evidence": evidence,
            "persistent_state": str((self.milestones_root / self.selected_id / "milestone-state.json").relative_to(self.project_workspace.factory_root)),
        }
        ensure_dir(self.milestones_root / self.selected_id)
        write_json(self.milestones_root / self.selected_id / "milestone-state.json", state)
        write_json(output_dir / "milestone-state.json", state)

    def _write_evidence(self, output_dir: Path, artifacts: list[str], reports: list[str], status: str) -> None:
        lines = [
            "# Milestone evidence",
            "",
            f"- Milestone: `{self.selected_id}`",
            f"- Status: `{status}`",
            "",
            "## Artifacts",
        ]
        lines.extend(f"- `{artifact}`" for artifact in artifacts)
        lines.append("")
        lines.append("## Reports")
        lines.extend(f"- `{report}`" for report in reports)
        write_text(output_dir / "milestone-evidence.md", "\n".join(lines))

    def _write_incremental_traceability(self, output_dir: Path, status: str, gates: dict[str, Any]) -> None:
        lines = [
            "# Incremental traceability",
            "",
            "| requirement | use_case | milestone | agents | tools | artifacts | validators | gates | status |",
            "|---|---|---|---|---|---|---|---|---|",
            (
                f"| {self.selected.scope} | {', '.join(self.selected.inputs)} | {self.selected_id} | "
                f"{', '.join(self.selected.agents)} | {', '.join(self.selected.allowed_tools)} | "
                f"{', '.join(self.selected.expected_artifacts)} | {', '.join(self.selected.validators)} | "
                f"{', '.join(gates) if gates else ', '.join(self.selected.gates)} | {status} |"
            ),
        ]
        write_text(output_dir / "incremental-traceability.md", "\n".join(lines))

    def _roadmap_markdown(self) -> str:
        lines = [
            f"# ROADMAP {self.project_workspace.project_id}",
            "",
            "WEBFORGE incremental roadmap. Each milestone is independently planned, validated and traced.",
            "",
            "| id | name | dependencies | expected_artifacts | state |",
            "|---|---|---|---|---|",
        ]
        for milestone in self.milestones:
            state = self._read_project_state(milestone.milestone_id).get("status", milestone.state)
            lines.append(
                f"| {milestone.milestone_id} | {milestone.name} | {', '.join(milestone.dependencies) or '-'} | "
                f"{', '.join(milestone.expected_artifacts)} | {state} |"
            )
        return "\n".join(lines)
