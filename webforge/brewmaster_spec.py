from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .brewmaster_catalog import (
    ACTION_ENDPOINTS,
    BREWMASTER_MODULES,
    BREWMASTER_SCREENS,
    CRUD_RESOURCES,
    TRANSACTIONAL_RESOURCES,
)
from .models import WorkOrder
from .utils import read_text

@dataclass(frozen=True)
class BrewMasterSpecModel:
    source_path: str
    parsed: bool
    modules: list[dict[str, Any]]
    use_cases: list[dict[str, Any]]
    screens: list[dict[str, Any]]
    business_rules: list[dict[str, Any]]
    validations: list[dict[str, Any]]
    endpoints: list[dict[str, Any]]
    permissions: list[str]
    entities: list[dict[str, Any]]
    non_functional: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_brewmaster_spec(spec_path: Path | None = None) -> BrewMasterSpecModel:
    path = spec_path or _default_brewmaster_spec_path()
    if not path.exists():
        return _fallback_brewmaster_spec(path, parsed=False)
    text = read_text(path)
    screens = _parse_spec_screens(text) or BREWMASTER_SCREENS
    endpoints = _parse_spec_endpoints(text) or _fallback_endpoints()
    entities = _parse_spec_entities(text)
    return BrewMasterSpecModel(
        source_path=str(path),
        parsed=True,
        modules=BREWMASTER_MODULES,
        use_cases=_parse_spec_use_cases(text),
        screens=screens,
        business_rules=_parse_numbered_section(text, "## 60 reglas de negocio"),
        validations=_parse_spec_validations(text),
        endpoints=endpoints,
        permissions=_parse_spec_permissions(text),
        entities=entities or _fallback_entities(),
        non_functional=_parse_spec_non_functional(text),
    )


def _default_brewmaster_spec_path() -> Path:
    return Path(__file__).resolve().parents[1] / "projects" / "BrewMaster" / "brewmaster_especificacion_completa.md"


def _fallback_brewmaster_spec(path: Path, parsed: bool) -> BrewMasterSpecModel:
    return BrewMasterSpecModel(
        source_path=str(path),
        parsed=parsed,
        modules=BREWMASTER_MODULES,
        use_cases=[],
        screens=BREWMASTER_SCREENS,
        business_rules=[],
        validations=[],
        endpoints=_fallback_endpoints(),
        permissions=[],
        entities=_fallback_entities(),
        non_functional=[],
    )


def _fallback_entities() -> list[dict[str, Any]]:
    return [
        {"name": entity, "purpose": "fallback entity", "fields": ["id", "estado", "created_at", "updated_at"]}
        for entity in sorted({entity for module in BREWMASTER_MODULES for entity in module["entities"]})
    ]


def _fallback_endpoints() -> list[dict[str, Any]]:
    endpoints = []
    for resource in CRUD_RESOURCES:
        base = f"/api/v1/{resource}"
        endpoints.extend(
            [
                {"method": "GET", "path": base, "handler": f"{resource}.list", "paginated": True},
                {"method": "POST", "path": base, "handler": f"{resource}.create", "transactional": resource in TRANSACTIONAL_RESOURCES},
                {"method": "GET", "path": f"{base}/{{id}}", "handler": f"{resource}.get"},
                {"method": "PUT", "path": f"{base}/{{id}}", "handler": f"{resource}.update", "audit": True},
                {"method": "DELETE", "path": f"{base}/{{id}}", "handler": f"{resource}.soft_delete", "physical_delete": False},
            ]
        )
    endpoints.extend({"method": method, "path": path, "handler": handler, "action_endpoint": True} for method, path, handler in ACTION_ENDPOINTS)
    return endpoints


def _section(text: str, start_marker: str, end_marker: str | None = None) -> str:
    start = text.find(start_marker)
    if start == -1:
        return ""
    if end_marker is None:
        return text[start:]
    end = text.find(end_marker, start + len(start_marker))
    return text[start:] if end == -1 else text[start:end]


def _parse_spec_use_cases(text: str) -> list[dict[str, Any]]:
    block = _section(text, "# A.", "# B.")
    use_cases: list[dict[str, Any]] = []
    for match in re.finditer(r"^###\s+(UC-[A-Z]+-\d{2})\s+(.+?)\s*$", block, flags=re.MULTILINE):
        use_cases.append({"id": match.group(1), "name": match.group(2).strip()})
    return use_cases


def _parse_spec_screens(text: str) -> list[dict[str, Any]]:
    block = _section(text, "## 30 pantallas", "# C.")
    fallback_by_id = {screen["id"]: screen for screen in BREWMASTER_SCREENS}
    screens: list[dict[str, Any]] = []
    for match in re.finditer(r"^###\s+(P-\d{2})\s+(.+?)\s*$", block, flags=re.MULTILINE):
        screen_id = match.group(1)
        fallback = fallback_by_id.get(screen_id, {})
        screens.append(
            {
                "id": screen_id,
                "name": match.group(2).strip(),
                "module": fallback.get("module", "BrewMaster"),
                "route": fallback.get("route", f"/screens/{screen_id.lower()}"),
            }
        )
    return screens


def _parse_numbered_section(text: str, start_marker: str) -> list[dict[str, Any]]:
    block = _section(text, start_marker, "\n---")
    rows: list[dict[str, Any]] = []
    for match in re.finditer(r"^(\d+)\.\s+(.+?)\s*$", block, flags=re.MULTILINE):
        rows.append({"id": int(match.group(1)), "text": match.group(2).strip()})
    return rows


def _parse_spec_validations(text: str) -> list[dict[str, Any]]:
    block = _section(text, "## 100 validaciones", "\n---")
    validations: list[dict[str, Any]] = []
    for match in re.finditer(r"^\d+\.\s+(V\d{3}):\s+(.+?)\s*$", block, flags=re.MULTILINE):
        validations.append({"id": match.group(1), "text": match.group(2).strip()})
    return validations


def _parse_spec_endpoints(text: str) -> list[dict[str, Any]]:
    block = _section(text, "## 40 endpoints", "\n---")
    endpoints: list[dict[str, Any]] = []
    for match in re.finditer(r"^\d+\.\s+`(GET|POST|PUT|PATCH|DELETE)\s+([^`]+)`\s*(.*)$", block, flags=re.MULTILINE):
        method = match.group(1)
        path = match.group(2).strip()
        description = match.group(3).strip().lstrip("-").lstrip("\u2014").strip()
        endpoints.append(
            {
                "method": method,
                "path": path,
                "handler": _handler_name(method, path),
                "description": description,
                "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
                "transactional": method in {"POST", "PUT", "PATCH", "DELETE"},
                "action_endpoint": _is_action_endpoint(path),
            }
        )
    return endpoints


def _handler_name(method: str, path: str) -> str:
    parts = [part for part in path.removeprefix("/api/v1/").split("/") if part and not part.startswith("{")]
    resource = parts[0].replace("-", "_") if parts else "root"
    has_id = "{id}" in path
    if method == "GET" and not has_id:
        action = "list"
    elif method == "GET":
        action = "detail"
    elif method == "POST" and not has_id and len(parts) == 1:
        action = "create"
    elif method == "PUT":
        action = "update"
    elif method == "PATCH":
        action = parts[-1].replace("-", "_") if len(parts) > 1 else "patch"
    elif method == "DELETE":
        action = "delete"
    else:
        action = parts[-1].replace("-", "_") if len(parts) > 1 else method.lower()
    if action == resource:
        action = method.lower()
    return f"{resource}.{action}"


def _is_action_endpoint(path: str) -> bool:
    return bool(re.search(r"\{id\}/[a-z-]+$", path)) or any(part in path for part in ["/auth/", "/change-password"])


def _parse_spec_permissions(text: str) -> list[str]:
    block = _section(text, "# H.", "\n---")
    return [match.group(1).strip() for match in re.finditer(r"^\d+\.\s+`([^`]+)`", block, flags=re.MULTILINE)]


def _parse_spec_entities(text: str) -> list[dict[str, Any]]:
    block = _section(text, "## J.5 Modelo de dominio canonico", "## J.6")
    if not block:
        block = _section(text, "## J.5 Modelo de dominio can", "## J.6")
    entities: list[dict[str, Any]] = []
    for line in block.splitlines():
        if not line.startswith("|") or "`" not in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3 or not cells[0].startswith("`"):
            continue
        name = cells[0].strip("`")
        fields = [_field_name(field) for field in re.findall(r"`([^`]+)`", cells[2])]
        fields = [field for field in fields if field]
        if "id" not in fields:
            fields.insert(0, "id")
        if "created_at" not in fields:
            fields.append("created_at")
        if "updated_at" not in fields:
            fields.append("updated_at")
        entities.append({"name": name, "purpose": cells[1], "fields": fields})
    return entities


def _field_name(value: str) -> str:
    first = value.split()[0].strip().strip(",")
    cleaned = re.sub(r"[^0-9A-Za-z_]", "_", first)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned if cleaned and not cleaned[0].isdigit() else ""


def _parse_spec_non_functional(text: str) -> list[dict[str, Any]]:
    block = _section(text, "## J.8 Requisitos no funcionales", "## J.9")
    rows: list[dict[str, Any]] = []
    for line in block.splitlines():
        if not line.startswith("| RNF-"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) >= 3:
            rows.append({"id": cells[0], "category": cells[1], "criterion": cells[2]})
    return rows


def is_brewmaster_work_order(work_order: WorkOrder) -> bool:
    haystack = " ".join(
        [
            work_order.objective,
            work_order.project_id,
            work_order.type,
            str(work_order.metadata.get("blueprint", "")),
        ]
    ).lower()
    return "brewmaster" in haystack
