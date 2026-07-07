from __future__ import annotations

from typing import Any

from webforge.domain_adapter import FrontendContract, ProjectAdapter
from webforge.models import WorkOrder
from webforge.validators import ValidationOutcome, project_acceptance_gate

from .blueprint import brewmaster_blueprint, brewmaster_coverage
from .bundle import brewmaster_bundle
from .spec import is_brewmaster_work_order


def _milestone(
    milestone_id: str,
    name: str,
    objective: str,
    scope: str,
    expected_artifacts: list[str],
    dependencies: list[str] | None = None,
    inputs: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "milestone_id": milestone_id,
        "name": name,
        "objective": objective,
        "scope": scope,
        "inputs": inputs or ["WorkOrder", "authorized_sources", "project ROADMAP.md"],
        "outputs": ["DEV implementation bundle", "QA promotion report", "milestone evidence"],
        "dependencies": dependencies or [],
        "agents": [
            "agent.intake",
            "agent.architect_planner",
            "agent.implementer",
            "agent.qa",
            "agent.security",
            "agent.close",
        ],
        "allowed_tools": [
            "tool.sandbox.dev_materialize",
            "tool.policy.static",
            "tool.validation.artifacts",
            "tool.security.secrets",
            "tool.security.deps",
            "tool.sbom.generate",
        ],
        "expected_artifacts": expected_artifacts,
        "acceptance_criteria": [
            "Expected artifacts exist in the run output or DEV workspace.",
            "Milestone validators pass with evidence.",
            "DEV workspace is promoted to QA only after validation passes.",
            "Regression evidence for accepted dependencies is present.",
        ],
        "validators": [
            "milestone.expected_artifacts",
            "milestone.dependencies",
            "milestone.qa_promotion",
            "milestone.regression",
        ],
        "gates": ["milestone_validation", "qa_promotion", "regression"],
        "risks": ["Milestone scope can drift if expected artifacts are not updated with implementation reality."],
        "state": "pending",
        "evidence": [],
        "traceability": ["requirement -> use_case -> milestone -> agent -> tool -> artifact -> validator -> gate -> report"],
    }


class BrewMasterAdapter(ProjectAdapter):
    adapter_id = "brewmaster"
    validation_report_key = "brewmaster"
    coverage_gate_name = "brewmaster_functional_coverage"

    def matches(self, work_order: WorkOrder) -> bool:
        return is_brewmaster_work_order(work_order)

    def frontend_contract(self, work_order: WorkOrder) -> FrontendContract:
        return FrontendContract(
            template_name="BREWMASTER_REACT_BOOTSTRAP",
            source="projects/BrewMaster/brewmaster_especificacion_completa.md#J.4",
            required_files=(
                "frontend/package.json",
                "frontend/src/App.jsx",
                "frontend/src/routes.js",
                "frontend/src/screens/catalog.js",
            ),
            contract_file="FRONTEND_CONTRACT.md",
        )

    def default_milestones(self, work_order: WorkOrder) -> list[dict[str, Any]]:
        return [
            _milestone(
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
            _milestone(
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
            _milestone(
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
            _milestone(
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
            _milestone(
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
                inputs=["J.12 Hito 5", "UC-VTA-*", "UC-COM-*", "P-20..P-26", "J.6", "J.14"],
            ),
            _milestone(
                "HITO-006",
                "Dashboard",
                "Implementar KPIs reales, graficos, alertas operacionales y reportes exportables.",
                "J.12 Dashboard",
                [
                    "frontend/src/App.jsx",
                    "frontend/src/screens/catalog.js",
                    "backend/app/jobs/scheduler.py",
                    "docs/api-contract.md",
                    "docs/traceability.md",
                    "docs/test-strategy.md",
                    "contracts/coverage.json",
                    "tests/test_domain_rules.py",
                ],
                dependencies=["HITO-005"],
                inputs=["J.12 Hito 6", "UC-REP-*", "P-03", "P-29", "J.13"],
            ),
            _milestone(
                "HITO-007",
                "Cierre",
                "Completar equipos, finanzas, metas, respaldos automaticos, dockerizacion, deploy EC2, documentacion y pruebas.",
                "J.12 Cierre",
                [
                    "backend/app/services/purchasing.py",
                    "backend/app/jobs/scheduler.py",
                    "docker-compose.yml",
                    "deploy/nginx.conf",
                    "docs/deployment.md",
                    "docs/architecture.md",
                    "docs/traceability.md",
                    "docs/test-strategy.md",
                    "tests/test_contracts.py",
                ],
                dependencies=["HITO-001", "HITO-002", "HITO-003", "HITO-004", "HITO-005", "HITO-006"],
                inputs=["J.12 Hito 7", "UC-EQU-*", "UC-FIN-*", "UC-ALT-*", "J.10", "J.15", "J.16"],
            ),
            _milestone(
                "HITO-008",
                "Pantallas interactivas",
                "Completar las 30 pantallas como vistas React + Bootstrap separadas, navegables, agradables y conectadas al backend aprobado.",
                "J.12 Pantallas interactivas",
                [
                    "frontend/index.html",
                    "frontend/src/main.jsx",
                    "frontend/src/App.jsx",
                    "frontend/src/routes.js",
                    "frontend/src/api/client.js",
                    "frontend/src/screens/catalog.js",
                    "frontend/src/screens/ScreenViews.jsx",
                    "docs/traceability.md",
                    "docs/test-strategy.md",
                    "tests/test_contracts.py",
                ],
                dependencies=["HITO-001", "HITO-002", "HITO-003", "HITO-004", "HITO-005", "HITO-006", "HITO-007"],
                inputs=["J.12 Hito 8", "SCR-001..SCR-030", "P-01..P-30", "J.4", "J.7", "J.8", "J.13"],
            ),
        ]

    def synthetic_full_run_expected_artifacts(self, work_order: WorkOrder) -> list[str]:
        return ["brewmaster-blueprint.json", "brewmaster-coverage.json"]

    def build_bundle(self, milestone_id: str | None = None) -> list[dict[str, Any]]:
        return brewmaster_bundle(milestone_id)

    def implementation_artifacts(self, milestone_id: str | None = None) -> dict[str, Any]:
        return {
            "brewmaster-blueprint.json": brewmaster_blueprint(milestone_id),
            "brewmaster-coverage.json": brewmaster_coverage(milestone_id),
        }

    def coverage(self, milestone_id: str | None = None) -> dict[str, Any]:
        return brewmaster_coverage(milestone_id)

    def acceptance_validation(
        self,
        gate: dict[str, Any],
        coverage: dict[str, Any],
        generated_workspace,
    ) -> ValidationOutcome:
        return project_acceptance_gate(
            gate,
            int(coverage.get("endpoint_count", 40)),
            generated_workspace,
            validator_id="brewmaster.acceptance_gate",
            success_message="BrewMaster acceptance gate passed",
            failure_message="BrewMaster acceptance gate failed",
        )

    def implementation_claim(self) -> str:
        return "BrewMaster project pack covers modules, screens, entities, API v1 endpoints and critical transactional rules."

    def implementation_active_message(self) -> str:
        return "BrewMaster project pack active."

    def implementation_output_descriptions(self) -> dict[str, str]:
        return {
            "brewmaster-blueprint.json": "Canonical BrewMaster architecture and functional blueprint.",
            "brewmaster-coverage.json": "BrewMaster coverage gates.",
        }

    def prune_unlisted_for_milestone(self, milestone_id: str | None = None) -> bool:
        return bool((milestone_id or "").upper().startswith("HITO-"))


def get_adapter() -> ProjectAdapter:
    return BrewMasterAdapter()
