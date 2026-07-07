from __future__ import annotations

import importlib.util
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import WorkOrder
from .utils import read_text
from .validators import ValidationOutcome


@dataclass(frozen=True)
class FrontendContract:
    template_name: str = "WEBFORGE_FRONTEND_CONTRACT"
    source: str = "work_order.frontend_contract"
    required_files: tuple[str, ...] = ("FRONTEND_CONTRACT.md",)
    contract_file: str = "FRONTEND_CONTRACT.md"


class ProjectAdapter:
    adapter_id = "generic"
    validation_report_key = "project_adapter"
    coverage_gate_name = "project_functional_coverage"

    def matches(self, work_order: WorkOrder) -> bool:
        return False

    def frontend_contract(self, work_order: WorkOrder) -> FrontendContract:
        return FrontendContract()

    def default_milestones(self, work_order: WorkOrder) -> list[dict[str, Any]]:
        return []

    def synthetic_full_run_expected_artifacts(self, work_order: WorkOrder) -> list[str]:
        return []

    def build_bundle(self, milestone_id: str | None = None) -> list[dict[str, Any]]:
        return []

    def implementation_artifacts(self, milestone_id: str | None = None) -> dict[str, Any]:
        return {}

    def coverage(self, milestone_id: str | None = None) -> dict[str, Any]:
        return {}

    def acceptance_validation(
        self,
        gate: dict[str, Any],
        coverage: dict[str, Any],
        generated_workspace: Path | None = None,
    ) -> ValidationOutcome:
        return ValidationOutcome(
            "project_adapter.not_applicable",
            True,
            "no project-specific adapter validation",
            {},
        )

    def implementation_claim(self) -> str:
        return "Project adapter blueprint, coverage and implementation artifacts are generated from project-owned code."

    def implementation_active_message(self) -> str:
        return f"Project adapter active: {self.adapter_id}."

    def implementation_output_descriptions(self) -> dict[str, str]:
        return {name: "Project adapter artifact." for name in self.implementation_artifacts().keys()}

    def prune_unlisted_for_milestone(self, milestone_id: str | None = None) -> bool:
        return False


class GenericProjectAdapter(ProjectAdapter):
    adapter_id = "generic"


def load_project_adapter(factory_root: Path, work_order: WorkOrder) -> ProjectAdapter:
    for adapter in discover_project_adapters(factory_root):
        if adapter.matches(work_order):
            return adapter
    return GenericProjectAdapter()


def discover_project_adapters(factory_root: Path) -> list[ProjectAdapter]:
    adapters: list[ProjectAdapter] = []
    candidate_roots = [
        factory_root / "projects",
        Path(__file__).resolve().parents[1] / "projects",
    ]
    seen: set[Path] = set()
    for projects_root in candidate_roots:
        if not projects_root.exists():
            continue
        for pack_dir in sorted(projects_root.glob("*/webforge_pack")):
            resolved = pack_dir.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            adapter_path = pack_dir / "adapter.py"
            if not adapter_path.exists():
                continue
            adapter = _load_adapter_from_pack(pack_dir)
            if adapter is not None:
                adapters.append(adapter)
    return adapters


def _load_adapter_from_pack(pack_dir: Path) -> ProjectAdapter | None:
    manifest = _read_pack_manifest(pack_dir)
    project_key = manifest.get("project_id") or pack_dir.parent.name
    package_name = "webforge_project_pack_" + re.sub(r"[^0-9A-Za-z_]+", "_", str(project_key)).strip("_").lower()
    init_path = pack_dir / "__init__.py"
    if init_path.exists():
        package_spec = importlib.util.spec_from_file_location(
            package_name,
            init_path,
            submodule_search_locations=[str(pack_dir)],
        )
        if package_spec and package_spec.loader:
            package = importlib.util.module_from_spec(package_spec)
            sys.modules[package_name] = package
            package_spec.loader.exec_module(package)
    adapter_spec = importlib.util.spec_from_file_location(f"{package_name}.adapter", pack_dir / "adapter.py")
    if adapter_spec is None or adapter_spec.loader is None:
        return None
    module = importlib.util.module_from_spec(adapter_spec)
    sys.modules[f"{package_name}.adapter"] = module
    adapter_spec.loader.exec_module(module)
    factory = getattr(module, "get_adapter", None)
    if callable(factory):
        adapter = factory()
        if isinstance(adapter, ProjectAdapter):
            return adapter
    adapter_cls = getattr(module, "Adapter", None)
    if adapter_cls is not None:
        adapter = adapter_cls()
        if isinstance(adapter, ProjectAdapter):
            return adapter
    return None


def _read_pack_manifest(pack_dir: Path) -> dict[str, Any]:
    path = pack_dir / "manifest.json"
    if not path.exists():
        return {}
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError:
        return {}
