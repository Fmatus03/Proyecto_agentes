from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .models import EvidenceSource
from .utils import read_text, redact_secrets, sha256_text, stable_json, write_json, write_text


@dataclass
class ContextSnippet:
    evidence_id: str
    path: str
    sha256: str
    snippet: str
    redactions: int
    section_id: str = ""
    title: str = ""
    start_line: int = 1
    end_line: int = 1
    section_hash: str = ""


class EvidenceRegistry:
    def __init__(self) -> None:
        self._sources: dict[str, EvidenceSource] = {}

    def add_file(self, evidence_id: str, path: Path, summary: str, root: Path | None = None) -> EvidenceSource:
        source = EvidenceSource.from_path(evidence_id, path, summary, root=root)
        self._sources[source.evidence_id] = source
        return source

    def values(self) -> list[EvidenceSource]:
        return list(self._sources.values())

    def ids(self) -> list[str]:
        return list(self._sources)

    def write(self, path: Path) -> None:
        lines = ["# Evidence register", ""]
        lines.append("| evidence_id | source | sha256 | summary |")
        lines.append("|---|---|---|---|")
        for source in self.values():
            lines.append(f"| {source.evidence_id} | `{source.path}` | `{source.sha256}` | {source.summary} |")
        write_text(path, "\n".join(lines))


class ContextManager:
    def __init__(self, registry: EvidenceRegistry) -> None:
        self.registry = registry

    def build_minimal_context(self, agent_id: str, phase: str, source_root: Path) -> dict[str, Any]:
        snippets: list[ContextSnippet] = []
        section_index: list[dict[str, Any]] = []
        for source in self.registry.values():
            source_path_value = Path(source.path)
            source_path = source_path_value if source_path_value.is_absolute() else source_root / source_path_value
            if not source_path.exists():
                continue
            text = read_text(source_path)
            sections = self._markdown_sections(text)
            for section_number, section in enumerate(sections, start=1):
                redacted, redactions = redact_secrets(section["text"])
                section_hash = sha256_text(redacted)
                section_id = f"{source.evidence_id}#S{section_number:03d}"
                snippet = ContextSnippet(
                    evidence_id=source.evidence_id,
                    path=source.path,
                    sha256=source.sha256,
                    snippet=redacted[:1000],
                    redactions=redactions,
                    section_id=section_id,
                    title=section["title"],
                    start_line=section["start_line"],
                    end_line=section["end_line"],
                    section_hash=section_hash,
                )
                snippets.append(snippet)
                section_index.append(
                    {
                        "section_id": section_id,
                        "evidence_id": source.evidence_id,
                        "path": source.path,
                        "title": section["title"],
                        "start_line": section["start_line"],
                        "end_line": section["end_line"],
                        "section_hash": section_hash,
                    }
                )
        pack = {
            "context_pack_id": f"CTX-{phase.upper()}",
            "agent_id": agent_id,
            "phase": phase,
            "mode": "section_index_with_snippets",
            "sources": [asdict(snippet) for snippet in snippets],
            "source_count": len(self.registry.values()),
            "document_count": len(self.registry.values()),
            "section_index": section_index,
        }
        pack["context_pack_hash"] = sha256_text(stable_json(pack))
        return pack

    def _markdown_sections(self, text: str) -> list[dict[str, Any]]:
        lines = text.splitlines()
        if not lines:
            return [{"title": "document", "start_line": 1, "end_line": 1, "text": ""}]
        heading_indexes: list[tuple[int, str]] = []
        for index, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("**C A P"):
                title = stripped.lstrip("#").strip("* ").strip() or "section"
                heading_indexes.append((index, title))
        if not heading_indexes:
            return [{"title": "document", "start_line": 1, "end_line": len(lines), "text": text}]
        sections: list[dict[str, Any]] = []
        for position, (start_line, title) in enumerate(heading_indexes):
            end_line = (heading_indexes[position + 1][0] - 1) if position + 1 < len(heading_indexes) else len(lines)
            section_text = "\n".join(lines[start_line - 1 : end_line])
            sections.append({"title": title, "start_line": start_line, "end_line": end_line, "text": section_text})
        return sections

    def write_context_pack(self, output_dir: Path, agent_id: str, phase: str, source_root: Path) -> dict[str, Any]:
        pack = self.build_minimal_context(agent_id, phase, source_root)
        write_json(output_dir / "context-pack.json", pack)
        manifest = {
            "index_id": "rag-index.webforge.local.v1",
            "cache_key": pack["context_pack_hash"],
            "retrieval": "authorized_sources_section_index",
            "corpus_loaded_fully": False,
            "document_count": pack["document_count"],
            "section_count": len(pack["section_index"]),
            "source_count": pack["source_count"],
        }
        write_json(output_dir / "rag-index-manifest.json", manifest)
        return pack


class MemoryGate:
    def __init__(self, project_id: str, project_memory_root: Path, project_learning_root: Path) -> None:
        self.project_id = project_id
        self.project_memory_root = project_memory_root
        self.project_learning_root = project_learning_root
        self.proposals: list[dict[str, Any]] = []

    def read_filtered(self, agent_id: str, phase: str) -> dict[str, Any]:
        return {
            "agent_id": agent_id,
            "phase": phase,
            "project_id": self.project_id,
            "persistent_memory": "project_scoped_propose_only",
            "project_memory_root": str(self.project_memory_root),
            "factory_memory_read_allowed": False,
            "factory_learning_write_allowed": False,
            "shared_with_factory": False,
            "trusted_items": [],
            "tainted_items": [],
        }

    def propose(self, title: str, evidence_id: str, reason: str) -> None:
        self.proposals.append(
            {
                "title": title,
                "evidence_id": evidence_id,
                "reason": reason,
                "status": "pending_human_approval",
                "scope": "project_only",
                "ttl": "TBD",
                "rollback": "delete proposal before activation",
            }
        )

    def write(self, output_dir: Path) -> None:
        write_json(
            output_dir / "memory-report.json",
            {
                "project_id": self.project_id,
                "persistent_memory_mode": "project_scoped_propose_only",
                "factory_memory_read_allowed": False,
                "factory_learning_write_allowed": False,
                "shared_with_factory": False,
                "project_memory_root": str(self.project_memory_root),
                "project_learning_root": str(self.project_learning_root),
                "activated_items": [],
                "project_proposals_count": len(self.proposals),
                "tainted_items": [],
            },
        )
        lines = ["# Aprendizaje", "", "Modo persistente: project_scoped_propose_only.", ""]
        lines.append("Este artefacto de corrida no almacena aprendizaje del proyecto.")
        lines.append(f"Proyecto: {self.project_id}")
        lines.append(f"Ruta de aprendizaje del proyecto: `{self.project_learning_root}`")
        write_text(output_dir / "Aprendizaje.md", "\n".join(lines))

        project_lines = ["# Aprendizaje", "", f"Proyecto: {self.project_id}", "Scope: project_only.", ""]
        if not self.proposals:
            project_lines.append("No hay aprendizajes activados automaticamente.")
        else:
            for proposal in self.proposals:
                project_lines.append(f"- {proposal['title']} ({proposal['status']}) evidence_id={proposal['evidence_id']}")
        project_learning_file = self.project_learning_root / "Aprendizaje.md"
        if self.proposals or not project_learning_file.exists():
            write_text(project_learning_file, "\n".join(project_lines))
        project_memory_file = self.project_memory_root / "memory-report.json"
        if self.proposals or not project_memory_file.exists():
            write_json(
                project_memory_file,
                {
                    "project_id": self.project_id,
                    "persistent_memory_mode": "project_scoped_propose_only",
                    "shared_with_factory": False,
                    "activated_items": [],
                    "proposals": self.proposals,
                    "tainted_items": [],
                },
            )
