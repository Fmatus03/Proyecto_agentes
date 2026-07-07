from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .utils import read_text


@dataclass(frozen=True)
class ValidationOutcome:
    validator_id: str
    passed: bool
    message: str
    observed: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def text_artifact_contains(path: Path, required_terms: Iterable[str], min_chars: int = 1) -> ValidationOutcome:
    terms = list(required_terms)
    if not path.exists():
        return ValidationOutcome("artifact.text_contains", False, f"missing {path.name}", {"path": path.name})
    text = read_text(path)
    missing = [term for term in terms if term not in text]
    passed = len(text.strip()) >= min_chars and not missing
    return ValidationOutcome(
        "artifact.text_contains",
        passed,
        "text artifact contains required terms" if passed else "text artifact is incomplete",
        {"path": path.name, "chars": len(text), "missing_terms": missing},
    )


def json_artifact_has_keys(path: Path, required_keys: Iterable[str]) -> ValidationOutcome:
    keys = list(required_keys)
    if not path.exists():
        return ValidationOutcome("artifact.json_keys", False, f"missing {path.name}", {"path": path.name})
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        return ValidationOutcome("artifact.json_keys", False, "invalid json", {"path": path.name, "error": str(exc)})
    missing = [key for key in keys if key not in data]
    return ValidationOutcome(
        "artifact.json_keys",
        not missing,
        "json artifact has required keys" if not missing else "json artifact missing keys",
        {"path": path.name, "missing_keys": missing},
    )


def artifacts_exist(root: Path, names: Iterable[str]) -> ValidationOutcome:
    required = list(names)
    missing = [name for name in required if not (root / name).exists()]
    return ValidationOutcome(
        "artifact.exists",
        not missing,
        "all required artifacts exist" if not missing else "required artifacts missing",
        {"required": required, "missing": missing},
    )


def markdown_table_status(path: Path, allowed_statuses: set[str] | None = None) -> ValidationOutcome:
    allowed = allowed_statuses or {"pass"}
    if not path.exists():
        return ValidationOutcome("markdown.table_status", False, f"missing {path.name}", {"path": path.name})
    rows = [line for line in read_text(path).splitlines() if line.startswith("|") and not set(line.strip()) <= {"|", "-", " "}]
    statuses: list[str] = []
    for row in rows:
        cells = [cell.strip().lower() for cell in row.strip("|").split("|")]
        if cells and cells[-1] in {"pass", "fail", "error", "partial", "missing"}:
            statuses.append(cells[-1])
    unexpected = [status for status in statuses if status not in allowed]
    return ValidationOutcome(
        "markdown.table_status",
        bool(statuses) and not unexpected,
        "markdown table statuses are acceptable" if statuses and not unexpected else "markdown table status check failed",
        {"path": path.name, "statuses": statuses, "unexpected": unexpected},
    )


def mcp_policy_default_deny(output_dir: Path) -> ValidationOutcome:
    policy = output_dir / "mcp-policy.json"
    invocations = output_dir / "mcp-invocations.jsonl"
    if not policy.exists() or not invocations.exists():
        return ValidationOutcome(
            "mcp.default_deny",
            False,
            "MCP policy or invocation log missing",
            {"policy_exists": policy.exists(), "invocations_exists": invocations.exists()},
        )
    try:
        data = json.loads(read_text(policy))
    except json.JSONDecodeError as exc:
        return ValidationOutcome("mcp.default_deny", False, "invalid MCP policy json", {"error": str(exc)})
    allowed = data.get("default") == "deny" and data.get("allowlist", []) == []
    return ValidationOutcome(
        "mcp.default_deny",
        allowed,
        "MCP default deny active" if allowed else "MCP policy is not default deny",
        {"default": data.get("default"), "allowlist": data.get("allowlist")},
    )


def no_catch_all_routes(path: Path) -> ValidationOutcome:
    if not path.exists():
        return ValidationOutcome("api.no_catch_all_routes", False, f"missing {path.name}", {"path": str(path)})
    text = read_text(path)
    patterns = ["/api/v1/{resource}", "/api/v1/{resource}/{item_id}", "api_route(\"/api/v1/{resource}"]
    findings = [pattern for pattern in patterns if pattern in text]
    return ValidationOutcome(
        "api.no_catch_all_routes",
        not findings,
        "no catch-all API routes found" if not findings else "catch-all API routes found",
        {"path": str(path), "findings": findings},
    )


def alembic_has_operations(path: Path) -> ValidationOutcome:
    if not path.exists():
        return ValidationOutcome("alembic.operations", False, f"missing {path.name}", {"path": str(path)})
    text = read_text(path)
    has_create = "op.create_table(" in text
    empty_upgrade = re.search(r"def\s+upgrade\(\):\s*\n\s+pass\b", text) is not None
    return ValidationOutcome(
        "alembic.operations",
        has_create and not empty_upgrade,
        "Alembic migration creates tables" if has_create and not empty_upgrade else "Alembic migration is not materialized",
        {"path": str(path), "has_create_table": has_create, "empty_upgrade": empty_upgrade},
    )


def alembic_versions_have_operations(versions_dir: Path) -> ValidationOutcome:
    if not versions_dir.exists():
        return ValidationOutcome(
            "alembic.versions_operations",
            False,
            "missing Alembic versions directory",
            {"path": str(versions_dir)},
        )
    outcomes = [
        alembic_has_operations(path)
        for path in sorted(versions_dir.glob("*.py"))
        if path.name != "__init__.py"
    ]
    passed = any(outcome.passed for outcome in outcomes)
    return ValidationOutcome(
        "alembic.versions_operations",
        passed,
        "Alembic versions include a materialized migration" if passed else "No materialized Alembic migration found",
        {"path": str(versions_dir), "migrations": [outcome.to_dict() for outcome in outcomes]},
    )


def project_acceptance_gate(
    gate: dict[str, Any],
    expected_endpoint_count: int,
    generated_workspace: Path | None = None,
    validator_id: str = "project.acceptance_gate",
    success_message: str = "Project adapter acceptance gate passed",
    failure_message: str = "Project adapter acceptance gate failed",
) -> ValidationOutcome:
    observed = dict(gate)
    observed["expected_endpoint_count"] = expected_endpoint_count
    passed = all(bool(value) for value in gate.values())
    if generated_workspace is not None:
        main_outcome = no_catch_all_routes(generated_workspace / "backend" / "app" / "main.py")
        migration_outcome = alembic_versions_have_operations(generated_workspace / "backend" / "alembic" / "versions")
        observed["no_catch_all_routes"] = main_outcome.to_dict()
        observed["alembic_has_operations"] = migration_outcome.to_dict()
        passed = passed and main_outcome.passed and migration_outcome.passed
    return ValidationOutcome(
        validator_id,
        passed,
        success_message if passed else failure_message,
        observed,
    )


def tool_budget_available(remaining: dict[str, int | float]) -> ValidationOutcome:
    tool_calls = int(remaining.get("tool_calls", 0))
    mcp_calls = int(remaining.get("mcp_calls", 0))
    cost = float(remaining.get("cost_usd", 0))
    passed = tool_calls >= 0 and mcp_calls >= 0 and cost >= 0
    return ValidationOutcome(
        "budget.remaining_non_negative",
        passed,
        "budget counters are non-negative" if passed else "budget counters are invalid",
        {"remaining": remaining},
    )
