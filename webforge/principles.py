from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Principle:
    id: str
    name: str
    operational_control: str
    gates: tuple[str, ...]
    evidence: tuple[str, ...]


PRINCIPLES: dict[str, Principle] = {
    "P01": Principle(
        "P01",
        "Maxima reproducibilidad practica",
        "Workflow fijo, versiones, hashes y rutas cerradas de retry.",
        ("schema", "stability", "budget", "final_format"),
        ("state.json", "validation-report.json"),
    ),
    "P02": Principle(
        "P02",
        "No invencion",
        "Todo claim critico requiere evidence_id o queda bloqueado.",
        ("evidence", "context", "plan_validation"),
        ("evidence-register.md", "claim-map.md"),
    ),
    "P03": Principle(
        "P03",
        "Memoria/contexto limpio",
        "Contexto minimo, redaccion, taint tracking y memoria propose_only.",
        ("memory", "safety", "secrets"),
        ("memory-report.json", "Aprendizaje.md"),
    ),
    "P04": Principle(
        "P04",
        "RAG/index/cache",
        "Context-pack con evidencia, hashes, snippets y cache por hash.",
        ("context", "budget", "evidence"),
        ("context-pack.json", "rag-index-manifest.json"),
    ),
    "P05": Principle(
        "P05",
        "ARNES/orquestador/agentes/skills",
        "Unica puerta harness.run_agent; agentes aislados por policy.",
        ("policy", "schema", "constitution"),
        ("agent-manifest.json", "validation-report.json"),
    ),
    "P06": Principle(
        "P06",
        "Tools deterministas",
        "ToolRegistry allowlisted con schemas, timeouts y logs.",
        ("tool-output", "sandbox", "tests", "security"),
        ("tool-logs.jsonl", "tool-registry.json"),
    ),
    "P07": Principle(
        "P07",
        "Aprendizaje gobernado",
        "Errores producen MemoryProposal pendiente; nunca activacion automatica.",
        ("learning", "human_approval", "regression_eval"),
        ("ERRORS.md", "Aprendizaje.md"),
    ),
    "P08": Principle(
        "P08",
        "Gates por fase",
        "Cada fase declara gates criticos y no avanza si alguno falla.",
        ("spec", "context", "plan_validation", "tests", "coverage"),
        ("validation-report.json", "phase-ledger.json"),
    ),
    "P09": Principle(
        "P09",
        "Logs/trazas",
        "State, log JSONL, billing ledger y matriz req-task-test-evidence.",
        ("observability",),
        ("state.json", "log.jsonl", "billing-ledger.json", "traceability-matrix.md"),
    ),
    "P10": Principle(
        "P10",
        "Workflows SDD",
        "Constitution -> Specify -> Clarify -> Checklist -> Context -> Plan -> Tasks -> Analyze -> Implement -> Validate -> PR/Deploy -> Observe -> Close.",
        ("tasks", "analyze", "final_format"),
        ("workflow.yaml", "final-report.json"),
    ),
    "P11": Principle(
        "P11",
        "MCP gobernado",
        "MCP default-deny, allowlist explicita, pre/post gates y logs.",
        ("mcp_policy", "tool-output", "human_approval"),
        ("mcp-policy.yaml", "mcp-invocations.jsonl"),
    ),
    "P12": Principle(
        "P12",
        "Seguridad/escalabilidad",
        "Sandbox, dry-run, secret/dependency scans, SBOM, SLOs y rollback.",
        ("security", "dependency", "secrets", "budget", "rollback"),
        ("security-review.md", "rollback-plan.md", "sbom.json"),
    ),
}


def ordered_principles() -> list[Principle]:
    return [PRINCIPLES[f"P{i:02d}"] for i in range(1, 13)]


def validate_principle_catalog() -> list[str]:
    errors: list[str] = []
    expected = [f"P{i:02d}" for i in range(1, 13)]
    if list(PRINCIPLES) != expected:
        errors.append(f"Principle ids must be exactly {expected}.")
    for principle in PRINCIPLES.values():
        if not principle.gates:
            errors.append(f"{principle.id} has no gates.")
        if not principle.evidence:
            errors.append(f"{principle.id} has no evidence artifacts.")
    return errors
