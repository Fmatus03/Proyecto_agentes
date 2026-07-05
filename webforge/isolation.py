from __future__ import annotations

from pathlib import Path
from typing import Any

from .project_workspace import ProjectWorkspace, SandboxInfo
from .utils import ensure_dir, find_secret_hits, sha256_file, sha256_text, write_json, write_text


MATERIALIZER_API_VERSION = "webforge.isolation.p12_inv.v1"
RESERVED_WORKSPACE_FILES = {"FRONTEND_CONTRACT.md", "PLANTILLA_FRONTEND.md"}


class DevSandboxMaterializer:
    max_files = 100
    max_file_bytes = 250_000
    max_total_bytes = 1_000_000

    def __init__(self, factory_root: Path, project_workspace: ProjectWorkspace) -> None:
        self.factory_root = factory_root.resolve()
        self.project_workspace = project_workspace
        self.dev_sandbox = self._sandbox("DEV")
        self.workspace_root = (self.dev_sandbox.path / "workspace").resolve()

    def materialize_bundle(self, bundle: list[dict[str, Any]], manifest_path: Path) -> dict[str, Any]:
        errors: list[dict[str, Any]] = []
        normalized = self._normalize_bundle(bundle, errors)
        if errors:
            report = self._report("error", [], errors)
            write_json(manifest_path, report)
            return report

        writes: list[dict[str, Any]] = []
        for item in normalized:
            target = item["target"]
            content = item["content"]
            normalized_content = content.rstrip() + "\n"
            new_hash = sha256_text(normalized_content)
            old_hash = sha256_file(target) if target.exists() else ""
            action = "unchanged" if old_hash == new_hash else "updated" if old_hash else "created"
            if action != "unchanged":
                ensure_dir(target.parent)
                write_text(target, content)
            writes.append(
                {
                    "path": item["path"],
                    "bytes": len(normalized_content.encode("utf-8")),
                    "sha256": new_hash,
                    "action": action,
                }
            )

        report = self._report("pass", writes, [])
        write_json(manifest_path, report)
        return report

    def _normalize_bundle(self, bundle: list[dict[str, Any]], errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not isinstance(bundle, list):
            errors.append({"reason": "bundle must be a list of file descriptors"})
            return []
        if not bundle:
            errors.append({"reason": "bundle must contain at least one file"})
            return []
        if len(bundle) > self.max_files:
            errors.append({"reason": "bundle exceeds max file count", "max_files": self.max_files})
            return []

        normalized: list[dict[str, Any]] = []
        seen_paths: set[str] = set()
        total_bytes = 0
        for index, item in enumerate(bundle, start=1):
            if not isinstance(item, dict):
                errors.append({"index": index, "reason": "bundle item must be an object"})
                continue
            raw_path = item.get("path")
            content = item.get("content")
            if not isinstance(raw_path, str) or not raw_path.strip():
                errors.append({"index": index, "reason": "path is required"})
                continue
            if not isinstance(content, str):
                errors.append({"index": index, "path": raw_path, "reason": "content must be text"})
                continue
            mode = str(item.get("mode", "text"))
            if mode != "text":
                errors.append({"index": index, "path": raw_path, "reason": "only text mode is allowed"})
                continue

            target, path_error = self._target_for(raw_path)
            if path_error:
                errors.append({"index": index, "path": raw_path, "reason": path_error})
                continue
            assert target is not None

            rel_path = target.relative_to(self.workspace_root).as_posix()
            if rel_path in seen_paths:
                errors.append({"index": index, "path": raw_path, "reason": "duplicate bundle path"})
                continue
            seen_paths.add(rel_path)

            byte_count = len((content.rstrip() + "\n").encode("utf-8"))
            total_bytes += byte_count
            if byte_count > self.max_file_bytes:
                errors.append(
                    {
                        "index": index,
                        "path": raw_path,
                        "reason": "file exceeds max byte size",
                        "max_file_bytes": self.max_file_bytes,
                    }
                )
                continue
            if total_bytes > self.max_total_bytes:
                errors.append({"index": index, "path": raw_path, "reason": "bundle exceeds max total bytes"})
                continue

            secret_hits = find_secret_hits(content)
            if secret_hits:
                errors.append({"index": index, "path": raw_path, "reason": "secret pattern detected", "matches": secret_hits})
                continue

            normalized.append({"path": rel_path, "target": target, "content": content})
        return normalized

    def _target_for(self, relative_path: str) -> tuple[Path | None, str]:
        value = relative_path.strip()
        if "\\" in value:
            return None, "backslash paths are not allowed"
        if value in {"", "."}:
            return None, "path must name a file"
        candidate = Path(value)
        if candidate.is_absolute():
            return None, "absolute paths are not allowed"
        if any(part in {"", ".", ".."} for part in candidate.parts):
            return None, "path traversal is not allowed"
        if len(candidate.parts) == 1 and candidate.parts[0] in RESERVED_WORKSPACE_FILES:
            return None, "reserved sandbox workspace file"

        target = (self.workspace_root / candidate).resolve()
        try:
            target.relative_to(self.workspace_root)
        except ValueError:
            return None, "target escapes DEV workspace"
        return target, ""

    def _sandbox(self, name: str) -> SandboxInfo:
        for sandbox in self.project_workspace.sandboxes:
            if sandbox.name == name:
                return sandbox
        raise ValueError(f"missing sandbox {name}")

    def _report(self, status: str, writes: list[dict[str, Any]], errors: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "api": MATERIALIZER_API_VERSION,
            "status": status,
            "sandbox": "DEV",
            "sandbox_id": self.dev_sandbox.sandbox_id,
            "workspace_root": self.workspace_root.relative_to(self.factory_root).as_posix(),
            "policy": {
                "target_scope": "project_sandbox_dev_workspace_only",
                "path_traversal_denied": True,
                "absolute_paths_denied": True,
                "reserved_workspace_files_denied": sorted(RESERVED_WORKSPACE_FILES),
                "secrets_denied": True,
                "external_writes": 0,
                "production_data": False,
            },
            "bundle": {
                "file_count": len(writes),
                "total_bytes": sum(int(item["bytes"]) for item in writes),
            },
            "writes": writes,
            "errors": errors,
            "blocking_findings": len(errors),
        }
