from __future__ import annotations

from pathlib import Path
from typing import Any

from .project_workspace import ProjectWorkspace, SandboxInfo
from .utils import ensure_dir, sha256_file, write_json


RESERVED_ROOT_FILES = {"FRONTEND_CONTRACT.md", "PLANTILLA_FRONTEND.md"}


class SandboxPromoter:
    def __init__(self, factory_root: Path, project_workspace: ProjectWorkspace) -> None:
        self.factory_root = factory_root.resolve()
        self.project_workspace = project_workspace
        self.dev = self._sandbox("DEV")
        self.qa = self._sandbox("QA")
        self.dev_workspace = (self.dev.path / "workspace").resolve()
        self.qa_workspace = (self.qa.path / "workspace").resolve()

    def promote_dev_to_qa(self, manifest_path: Path, enabled: bool) -> dict[str, Any]:
        if not enabled:
            report = self._report("blocked", [], [], [{"reason": "DEV validation did not pass"}])
            write_json(manifest_path, report)
            return report
        errors: list[dict[str, str]] = []
        writes: list[dict[str, Any]] = []
        deletions: list[dict[str, Any]] = []
        if not self.dev_workspace.exists():
            errors.append({"reason": "DEV workspace missing"})
        if not self.qa_workspace.exists():
            errors.append({"reason": "QA workspace missing"})
        if errors:
            report = self._report("error", writes, deletions, errors)
            write_json(manifest_path, report)
            return report

        dev_files = {
            source.relative_to(self.dev_workspace).as_posix()
            for source in self.dev_workspace.rglob("*")
            if source.is_file()
        }
        for target_file in sorted(path for path in self.qa_workspace.rglob("*") if path.is_file()):
            rel = target_file.relative_to(self.qa_workspace)
            rel_path = rel.as_posix()
            if len(rel.parts) == 1 and rel.parts[0] in RESERVED_ROOT_FILES:
                continue
            if rel_path not in dev_files:
                old_hash = sha256_file(target_file)
                target_file.unlink()
                deletions.append({"path": rel_path, "sha256": old_hash, "action": "deleted"})

        for source in sorted(path for path in self.dev_workspace.rglob("*") if path.is_file()):
            rel = source.relative_to(self.dev_workspace)
            if len(rel.parts) == 1 and rel.parts[0] in RESERVED_ROOT_FILES:
                continue
            target = self.qa_workspace / rel
            old_hash = sha256_file(target) if target.exists() else ""
            new_hash = sha256_file(source)
            action = "unchanged" if old_hash == new_hash else "updated" if old_hash else "created"
            if action != "unchanged":
                ensure_dir(target.parent)
                target.write_bytes(source.read_bytes())
            writes.append(
                {
                    "path": rel.as_posix(),
                    "sha256": new_hash,
                    "action": action,
                }
            )

        for directory in sorted(
            (path for path in self.qa_workspace.rglob("*") if path.is_dir()),
            key=lambda item: len(item.parts),
            reverse=True,
        ):
            if directory == self.qa_workspace:
                continue
            if any(directory.iterdir()):
                continue
            rel_path = directory.relative_to(self.qa_workspace).as_posix()
            directory.rmdir()
            deletions.append({"path": rel_path, "action": "deleted_empty_dir"})

        report = self._report("pass", writes, deletions, [])
        write_json(manifest_path, report)
        return report

    def _sandbox(self, name: str) -> SandboxInfo:
        for sandbox in self.project_workspace.sandboxes:
            if sandbox.name == name:
                return sandbox
        raise ValueError(f"missing sandbox {name}")

    def _report(
        self,
        status: str,
        writes: list[dict[str, Any]],
        deletions: list[dict[str, Any]],
        errors: list[dict[str, str]],
    ) -> dict[str, Any]:
        return {
            "status": status,
            "flow": "DEV->QA",
            "source": self.dev_workspace.relative_to(self.factory_root).as_posix(),
            "target": self.qa_workspace.relative_to(self.factory_root).as_posix(),
            "policy": {
                "promote_only_after_validation": True,
                "reserved_root_files_skipped": sorted(RESERVED_ROOT_FILES),
                "external_writes": 0,
            },
            "writes": writes,
            "deletions": deletions,
            "errors": errors,
            "blocking_findings": len(errors),
        }
