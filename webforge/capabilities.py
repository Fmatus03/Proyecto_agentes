from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FactorySkillSpec:
    skill_id: str
    name: str
    purpose: str
    phases: tuple[str, ...]
    gates: tuple[str, ...]
    evidence: tuple[str, ...]


FACTORY_SKILLS: dict[str, FactorySkillSpec] = {
    "skill.webforge.codex": FactorySkillSpec(
        "skill.webforge.codex",
        "Codex WEBFORGE Skill",
        "Expose the WEBFORGE SDD factory as a reusable Codex skill.",
        ("intake", "plan", "validate", "close"),
        ("schema", "final_format"),
        ("skills/webforge-factory/SKILL.md", "factory-skill-manifest.json"),
    ),
    "skill.constitution_12p": FactorySkillSpec(
        "skill.constitution_12p",
        "Constitution P01-P12",
        "Instantiate and verify the 12 operating principles.",
        ("constitution",),
        ("constitution",),
        ("constitution.md", "principle-ledger.json"),
    ),
    "skill.project_isolation": FactorySkillSpec(
        "skill.project_isolation",
        "Project Isolation",
        "Create project/<project_id> with private memory, learning, versions, DEV and QA.",
        ("intake", "implement", "validate"),
        ("project_isolation",),
        ("project-isolation-policy.md", "project-manifest.json", "project-sandboxes.json"),
    ),
    "skill.dev_materializer": FactorySkillSpec(
        "skill.dev_materializer",
        "DEV Bundle Materializer",
        "Write implementation bundles only through the P12/INV isolation API into the DEV workspace.",
        ("implement", "validate"),
        ("sandbox", "tool-output"),
        ("dev-materialization-manifest.json", "tool-logs.jsonl"),
    ),
    "skill.frontend_template": FactorySkillSpec(
        "skill.frontend_template",
        "Mandatory frontend contract",
        "Bind the declared project frontend contract to every project, version and sandbox.",
        ("intake", "plan", "implement", "validate"),
        ("frontend_template",),
        ("frontend-template-policy.md", "frontend-template-manifest.json"),
    ),
    "skill.context_rag": FactorySkillSpec(
        "skill.context_rag",
        "Evidence Context Pack",
        "Build minimal context packs from authorized hashed evidence.",
        ("context",),
        ("context", "evidence"),
        ("context-pack.json", "rag-index-manifest.json", "evidence-register.md"),
    ),
    "skill.validation_tools": FactorySkillSpec(
        "skill.validation_tools",
        "Deterministic Validation Tools",
        "Run allowlisted validators and artifact completeness checks.",
        ("validate",),
        ("tests", "coverage"),
        ("validation-report.json", "tool-registry.json", "tool-logs.jsonl"),
    ),
    "skill.security_supply_chain": FactorySkillSpec(
        "skill.security_supply_chain",
        "Security and Supply Chain",
        "Run secret/dependency/SBOM controls before closing.",
        ("security",),
        ("secrets", "dependency", "sbom"),
        ("security-review.md", "secrets-report.json", "dependency-report.json", "sbom.json"),
    ),
    "skill.release_observability": FactorySkillSpec(
        "skill.release_observability",
        "Release and Observability",
        "Block deploy without approval and emit logs, metrics and billing ledger.",
        ("deploy_checkpoint", "observe", "close"),
        ("rollback", "observability", "learning"),
        ("deploy-plan.md", "rollback-plan.md", "billing-ledger.json", "log.jsonl"),
    ),
}


def skill_manifest(project_root: Path) -> dict[str, Any]:
    skill_path = project_root / "skills" / "webforge-factory" / "SKILL.md"
    return {
        "version": "skills.webforge.v1",
        "codex_skill_path": str(skill_path.relative_to(project_root)) if skill_path.exists() else "missing",
        "codex_skill_present": skill_path.exists(),
        "skills": [asdict(skill) for skill in FACTORY_SKILLS.values()],
    }


def validate_skill_package(project_root: Path) -> list[str]:
    errors: list[str] = []
    skill_root = project_root / "skills" / "webforge-factory"
    required = [
        skill_root / "SKILL.md",
        skill_root / "agents" / "openai.yaml",
        skill_root / "scripts" / "webforge_run.py",
        skill_root / "references" / "operating-rules.md",
    ]
    for path in required:
        if not path.exists():
            errors.append(f"missing {path.relative_to(project_root)}")
    skill_md = skill_root / "SKILL.md"
    if skill_md.exists() and "TODO" in skill_md.read_text(encoding="utf-8", errors="replace"):
        errors.append("skills/webforge-factory/SKILL.md contains TODO")
    return errors
