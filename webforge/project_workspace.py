from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .domain_adapter import GenericProjectAdapter, ProjectAdapter
from .models import WorkOrder
from .utils import ensure_dir, sha256_text, stable_json, write_json, write_text


PROJECT_ROOT_NAME = "project"
SANDBOXES = ("DEV", "QA")
FRONTEND_TEMPLATE_NAME = "WEBFORGE_FRONTEND_CONTRACT"
FRONTEND_TEMPLATE_REQUIRED_FILES = ("FRONTEND_CONTRACT.md",)


def _rel_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def sanitize_project_id(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower()).strip("-._")
    return cleaned[:80] or "default-project"


def normalize_version(value: str) -> str:
    raw = value.strip().lower()
    if not raw:
        return "v0001"
    if re.fullmatch(r"v[0-9]{4}", raw):
        return raw
    if re.fullmatch(r"[0-9]+", raw):
        return f"v{int(raw):04d}"
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", raw).strip("-._")
    return cleaned or "v0001"


@dataclass(frozen=True)
class SandboxInfo:
    name: str
    sandbox_id: str
    path: Path
    clone_source: Path
    version: str
    memory_path: Path
    learning_path: Path
    frontend_template_name: str
    frontend_template_source: str
    frontend_template_hash: str
    frontend_template_required_files: tuple[str, ...]
    frontend_contract_filename: str

    def to_dict(self, root: Path) -> dict[str, str]:
        return {
            "name": self.name,
            "sandbox_id": self.sandbox_id,
            "path": _rel_posix(self.path, root),
            "clone_source": _rel_posix(self.clone_source, root),
            "version": self.version,
            "memory_path": _rel_posix(self.memory_path, root),
            "learning_path": _rel_posix(self.learning_path, root),
            "frontend_template": self.frontend_template_name,
            "frontend_template_source": self.frontend_template_source,
            "frontend_template_hash": self.frontend_template_hash,
            "frontend_template_required": "true",
            "frontend_contract": self.frontend_contract_filename,
            "frontend_required_files": ",".join(self.frontend_template_required_files),
            "autonomous": "true",
            "shared_with_factory": "false",
        }


class ProjectWorkspace:
    def __init__(self, factory_root: Path, work_order: WorkOrder, adapter: ProjectAdapter | None = None) -> None:
        self.factory_root = factory_root.resolve()
        objective_slug = sanitize_project_id(work_order.objective.split(".")[0])
        self.project_id = sanitize_project_id(work_order.project_id or objective_slug)
        self.version = normalize_version(work_order.project_version)
        self.project_adapter = adapter or GenericProjectAdapter()
        contract = self.project_adapter.frontend_contract(work_order)
        self.frontend_template_name = contract.template_name or FRONTEND_TEMPLATE_NAME
        self.frontend_template_source = contract.source or "work_order.frontend_contract"
        self.frontend_template_required_files = contract.required_files or FRONTEND_TEMPLATE_REQUIRED_FILES
        self.frontend_contract_filename = contract.contract_file or "FRONTEND_CONTRACT.md"
        self.frontend_template_hash = self._frontend_template_hash()
        self.root = self.factory_root / PROJECT_ROOT_NAME / self.project_id
        self.version_root = self.root / "versions" / self.version
        self.memory_root = self.root / "memory"
        self.learning_root = self.root / "learning"
        self.milestones_root = self.root / "milestones"
        self.sandbox_root = self.root / "sandboxes"
        self.sandboxes = [
            SandboxInfo(
                name=name,
                sandbox_id=f"{self.project_id}-{name.lower()}-{self.version}",
                path=self.sandbox_root / name,
                clone_source=self.version_root,
                version=self.version,
                memory_path=self.sandbox_root / name / "memory",
                learning_path=self.sandbox_root / name / "learning",
                frontend_template_name=self.frontend_template_name,
                frontend_template_source=self.frontend_template_source,
                frontend_template_hash=self.frontend_template_hash,
                frontend_template_required_files=self.frontend_template_required_files,
                frontend_contract_filename=self.frontend_contract_filename,
            )
            for name in SANDBOXES
        ]

    def prepare(self, output_dir: Path) -> dict[str, Any]:
        for path in [self.root, self.version_root, self.memory_root, self.learning_root, self.milestones_root, self.sandbox_root]:
            ensure_dir(path)
        self._write_root_policy()
        self._write_version_manifest()
        for sandbox in self.sandboxes:
            self._prepare_sandbox(sandbox)
        self._remove_stale_frontend_contracts()
        policy = self.policy_dict()
        write_json(output_dir / "project-manifest.json", self.manifest_dict())
        write_json(output_dir / "project-sandboxes.json", self.sandbox_manifest())
        write_json(output_dir / "project-memory-policy.json", self.memory_policy_dict())
        write_json(output_dir / "frontend-template-manifest.json", self.frontend_template_manifest())
        write_text(output_dir / "project-isolation-policy.md", self.policy_markdown())
        write_text(output_dir / "frontend-template-policy.md", self.frontend_template_policy_markdown())
        return policy

    def policy_dict(self) -> dict[str, Any]:
        return {
            "policy_id": "webforge.project_isolation.v1",
            "project_root_name": PROJECT_ROOT_NAME,
            "project_id": self.project_id,
            "project_root": _rel_posix(self.root, self.factory_root),
            "version": self.version,
            "rules": {
                "all_project_work_must_stay_under_project_root": True,
                "factory_memory_read_allowed": False,
                "factory_learning_write_allowed": False,
                "project_memory_shared_with_factory": False,
                "sandbox_dev_required": True,
                "sandbox_qa_required": True,
                "sandbox_dev_and_qa_must_be_independent": True,
                "sandbox_clone_source": _rel_posix(self.version_root, self.factory_root),
                "incremental_versions_root": _rel_posix(self.root / "versions", self.factory_root),
                "frontend_template_required": True,
                "frontend_template_name": self.frontend_template_name,
                "frontend_template_source": self.frontend_template_source,
                "frontend_template_hash": self.frontend_template_hash,
                "frontend_required_files": list(self.frontend_template_required_files),
                "frontend_contract": self.frontend_contract_filename,
            },
        }

    def manifest_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "project_root": _rel_posix(self.root, self.factory_root),
            "current_version": self.version,
            "memory_root": _rel_posix(self.memory_root, self.factory_root),
            "learning_root": _rel_posix(self.learning_root, self.factory_root),
            "milestones_root": _rel_posix(self.milestones_root, self.factory_root),
            "versions_root": _rel_posix(self.root / "versions", self.factory_root),
            "sandboxes_root": _rel_posix(self.sandbox_root, self.factory_root),
            "frontend_template": self.frontend_template_manifest(),
            "shared_with_factory": False,
        }

    def frontend_template_manifest(self) -> dict[str, Any]:
        return {
            "template_name": self.frontend_template_name,
            "mandatory": True,
            "source": self.frontend_template_source,
            "hash": self.frontend_template_hash,
            "required_files": list(self.frontend_template_required_files),
            "contract_file": self.frontend_contract_filename,
            "applies_to": "all_projects_all_versions_all_sandboxes",
        }

    def sandbox_manifest(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "current_version": self.version,
            "clone_source_hash": sha256_text(stable_json({"project_id": self.project_id, "version": self.version})),
            "sandboxes": [sandbox.to_dict(self.factory_root) for sandbox in self.sandboxes],
        }

    def memory_policy_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "mode": "project_scoped_propose_only",
            "factory_memory_read_allowed": False,
            "factory_learning_write_allowed": False,
            "shared_with_factory": False,
            "project_memory_root": _rel_posix(self.memory_root, self.factory_root),
            "project_learning_root": _rel_posix(self.learning_root, self.factory_root),
            "sandbox_memory_roots": {
                sandbox.name: _rel_posix(sandbox.memory_path, self.factory_root) for sandbox in self.sandboxes
            },
        }

    def validate(self) -> tuple[bool, list[str]]:
        errors: list[str] = []
        if self.root.parent.name != PROJECT_ROOT_NAME:
            errors.append("project root must be under project/<project_id>")
        for required in [self.root, self.version_root, self.memory_root, self.learning_root]:
            if not required.exists():
                errors.append(f"missing {required}")
        if not self.milestones_root.exists():
            errors.append(f"missing {self.milestones_root}")
        if not (self.root / "frontend-template-manifest.json").exists():
            errors.append("missing project frontend-template-manifest.json")
        if not (self.version_root / "frontend" / self.frontend_contract_filename).exists():
            errors.append("missing version frontend contract binding")
        sandbox_paths = [sandbox.path for sandbox in self.sandboxes]
        if len(set(sandbox_paths)) != len(SANDBOXES):
            errors.append("DEV and QA sandbox paths must be different")
        for sandbox in self.sandboxes:
            if not sandbox.path.exists():
                errors.append(f"missing sandbox {sandbox.name}")
            if not sandbox.memory_path.exists():
                errors.append(f"missing sandbox memory {sandbox.name}")
            if not sandbox.learning_path.exists():
                errors.append(f"missing sandbox learning {sandbox.name}")
            if not (sandbox.path / "frontend-template-manifest.json").exists():
                errors.append(f"missing sandbox frontend template manifest {sandbox.name}")
            if not (sandbox.path / "workspace" / self.frontend_contract_filename).exists():
                errors.append(f"missing sandbox frontend contract binding {sandbox.name}")
            if sandbox.path == self.root or sandbox.path == self.version_root:
                errors.append(f"sandbox {sandbox.name} is not isolated from project root/version")
        return not errors, errors

    def policy_markdown(self) -> str:
        return "\n".join(
            [
                "# Project isolation policy",
                "",
                "Esta politica es obligatoria para todos los proyectos WEBFORGE.",
                "",
                "- Todo proyecto vive bajo `project/<project_id>/`.",
                "- Ningun proyecto lee memoria ni aprendizaje persistente de la fabrica.",
                "- Ningun aprendizaje de proyecto se escribe en la memoria de la fabrica.",
                "- Cada proyecto tiene `sandboxes/DEV` y `sandboxes/QA` autonomos.",
                "- Cada proyecto tiene `ROADMAP.md` y estados de hito bajo `milestones/`.",
                "- DEV y QA son clones independientes de `versions/<version>`.",
                f"- Todo proyecto y sandbox declara un contrato frontend obligatorio (`{self.frontend_template_name}`).",
                "- Las pruebas incrementales salen de versiones `v0001`, `v0002`, ... dentro del proyecto.",
                "- Si falta DEV, QA, memoria aislada, version o contrato frontend, el gate falla.",
            ]
        )

    def root_policy_markdown(self) -> str:
        return "\n".join(
            [
                "# Project isolation policy",
                "",
                "Esta politica es obligatoria para todos los proyectos WEBFORGE.",
                "",
                "- Todo proyecto vive bajo `project/<project_id>/`.",
                "- Ningun proyecto lee memoria ni aprendizaje persistente de la fabrica.",
                "- Ningun aprendizaje de proyecto se escribe en la memoria de la fabrica.",
                "- Cada proyecto tiene `sandboxes/DEV` y `sandboxes/QA` autonomos.",
                "- Cada proyecto tiene `ROADMAP.md` y estados de hito bajo `milestones/`.",
                "- DEV y QA son clones independientes de `versions/<version>`.",
                "- Todo proyecto y sandbox declara su contrato frontend obligatorio.",
                "- Las pruebas incrementales salen de versiones `v0001`, `v0002`, ... dentro del proyecto.",
                "- Si falta DEV, QA, memoria aislada, version o contrato frontend, el gate falla.",
            ]
        )

    def frontend_template_policy_markdown(self) -> str:
        return "\n".join(
            [
                "# Frontend template policy",
                "",
                f"`{self.frontend_template_name}` es el contrato frontend obligatorio para este proyecto.",
                "",
                "- Ningun proyecto puede crear frontend desde una tecnologia distinta a su contrato declarado.",
                "- Todo sandbox DEV y QA debe declarar el mismo contrato y hash.",
                "- Las versiones incrementales deben clonar desde `versions/<version>` manteniendo este contrato.",
                "- Si falta el contrato, sus archivos requeridos o sus manifiestos, el gate `frontend_template` falla.",
            ]
        )

    def _write_root_policy(self) -> None:
        write_text(self.factory_root / PROJECT_ROOT_NAME / "README.md", self.root_policy_markdown())
        write_json(self.root / "project-manifest.json", self.manifest_dict())
        write_json(self.root / "project-memory-policy.json", self.memory_policy_dict())
        write_json(self.root / "frontend-template-manifest.json", self.frontend_template_manifest())

    def _write_version_manifest(self) -> None:
        write_json(
            self.version_root / "version-manifest.json",
            {
                "project_id": self.project_id,
                "version": self.version,
                "purpose": "immutable clone source for DEV and QA sandboxes",
                "shared_with_factory": False,
            },
        )
        write_text(
            self.version_root / "README.md",
            f"# {self.project_id} {self.version}\n\nFuente local para clonar DEV y QA sin compartir memoria con la fabrica.\n",
        )
        ensure_dir(self.version_root / "frontend")
        write_text(
            self.version_root / "frontend" / self.frontend_contract_filename,
            "\n".join(
                [
                    f"# {self.frontend_template_name}",
                    "",
                    "Contrato frontend obligatorio para esta version.",
                    f"Source: `{self.frontend_template_source}`",
                    f"Hash: `{self.frontend_template_hash}`",
                    f"Required files: `{', '.join(self.frontend_template_required_files)}`",
                ]
            ),
        )
        write_json(self.version_root / "frontend" / "frontend-template-manifest.json", self.frontend_template_manifest())

    def _prepare_sandbox(self, sandbox: SandboxInfo) -> None:
        for path in [sandbox.path, sandbox.memory_path, sandbox.learning_path, sandbox.path / "workspace"]:
            ensure_dir(path)
        manifest = sandbox.to_dict(self.factory_root)
        manifest["clone_mode"] = "independent_local_clone"
        manifest["factory_memory_read_allowed"] = "false"
        manifest["factory_learning_write_allowed"] = "false"
        write_json(sandbox.path / "sandbox-manifest.json", manifest)
        write_json(sandbox.path / "frontend-template-manifest.json", self.frontend_template_manifest())
        workspace_readme = sandbox.path / "workspace" / "README.md"
        if not workspace_readme.exists():
            write_text(
                workspace_readme,
                f"# {sandbox.name} sandbox\n\nClone autonomo de `{self.project_id}` `{self.version}`.\n",
            )
        write_text(
            sandbox.path / "workspace" / self.frontend_contract_filename,
            "\n".join(
                [
                    f"# {self.frontend_template_name}",
                    "",
                    f"Sandbox: {sandbox.name}",
                    "Uso: obligatorio.",
                    f"Source: `{self.frontend_template_source}`",
                    f"Hash: `{self.frontend_template_hash}`",
                    f"Required files: `{', '.join(self.frontend_template_required_files)}`",
                ]
            ),
        )
        write_text(
            sandbox.memory_path / "README.md",
            f"# {sandbox.name} memory\n\nMemoria privada del sandbox. No se comparte con la fabrica ni con otros proyectos.\n",
        )
        write_text(
            sandbox.learning_path / "Aprendizaje.md",
            f"# Aprendizaje {sandbox.name}\n\nAprendizaje privado del sandbox. Estado inicial limpio.\n",
        )

    def _remove_stale_frontend_contracts(self) -> None:
        stale_names = {"PLANTILLA_FRONTEND.md"} - {self.frontend_contract_filename}
        for stale_name in stale_names:
            candidates = [self.version_root / "frontend" / stale_name]
            candidates.extend(sandbox.path / "workspace" / stale_name for sandbox in self.sandboxes)
            for candidate in candidates:
                if candidate.exists() and candidate.is_file():
                    candidate.unlink()

    def _frontend_template_hash(self) -> str:
        return sha256_text(
            stable_json(
                {
                    "template_name": self.frontend_template_name,
                    "source": self.frontend_template_source,
                    "required_files": list(self.frontend_template_required_files),
                }
            )
        )
