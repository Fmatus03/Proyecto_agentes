from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from .context import ContextManager, EvidenceRegistry, MemoryGate
from .factory_phases import FactoryPhaseHandlersMixin
from .factory_support import FactorySupportMixin
from .harness import HarnessRunner
from .milestones import MilestoneManager
from .models import CycleState, PhaseResult, WorkOrder
from .policy import BudgetManager, MCPGateway, PolicyEngine, write_approval_matrix
from .project_workspace import ProjectWorkspace
from .tools import ToolRegistry
from .utils import discover_design_sources, ensure_dir, sha256_text, short_hash, stable_json, write_json, write_text
from .workflow import PHASE_AGENTS, WORKFLOW_PHASES, WORKFLOW_VERSION

class WebForgeFactory(FactoryPhaseHandlersMixin, FactorySupportMixin):
    def __init__(self, project_root: Path | str) -> None:
        self.project_root = Path(project_root).resolve()

    def run(
        self,
        work_order_data: dict[str, Any],
        output_dir: Path | str,
        sources: list[Path] | None = None,
    ) -> dict[str, Any]:
        self.output_dir = ensure_dir(Path(output_dir).resolve())
        self._clean_known_output_artifacts()
        self.phase_results: list[PhaseResult] = []
        self.claims: list[dict[str, Any]] = []
        self.artifacts: set[str] = set()
        self.source_root = self.project_root

        work_order = WorkOrder.from_dict(work_order_data)
        self.project_workspace = ProjectWorkspace(self.project_root, work_order)
        work_order.project_id = self.project_workspace.project_id
        work_order.project_version = self.project_workspace.version
        self.project_policy = self.project_workspace.prepare(self.output_dir)
        self.milestones = MilestoneManager(self.project_workspace, work_order)
        self.milestone_policy = self.milestones.prepare(self.output_dir)
        self.artifacts.update(
            {
                "roadmap.md",
                "roadmap.json",
                "milestone-plan.json",
                "milestone-state.json",
                "milestone-evidence.md",
                "incremental-traceability.md",
                "project-isolation-policy.md",
                "frontend-template-manifest.json",
                "frontend-template-policy.md",
                "project-manifest.json",
                "project-memory-policy.json",
                "project-sandboxes.json",
            }
        )
        if not work_order.authorized_sources:
            work_order.authorized_sources = [path.name for path in (sources or discover_design_sources(self.project_root))]
        sources = sources or [self.project_root / name for name in work_order.authorized_sources]

        registry = EvidenceRegistry()
        for index, source in enumerate(sources, start=1):
            source_path = source if source.is_absolute() else self.project_root / source
            if source_path.exists():
                registry.add_file(f"EV-SRC-{index:03d}", source_path, "Authorized WEBFORGE design source", root=self.project_root)
        if not registry.values():
            placeholder = self.output_dir / "source-placeholder.md"
            write_text(placeholder, "WEBFORGE runtime implementation request captured as local source.")
            registry.add_file("EV-SRC-001", placeholder, "Local fallback source")
            self.source_root = self.output_dir

        self.registry = registry
        self.context_manager = ContextManager(registry)
        self.memory = MemoryGate(
            self.project_workspace.project_id,
            self.project_workspace.memory_root,
            self.project_workspace.learning_root,
        )
        self.budget = BudgetManager(work_order.budget)
        self.mcp = MCPGateway(self.output_dir)
        self.policy = PolicyEngine({spec.agent_id for spec in PHASE_AGENTS.values()})
        self.tools = ToolRegistry(self.output_dir, self.budget)
        self.harness = HarnessRunner(self.policy, self.budget, self.context_manager, self.memory, self.mcp, self.tools)
        self.work_order = work_order
        self.run_id = "RUN-WEBFORGE-" + short_hash({"work_order": work_order.to_dict(), "sources": [asdict(s) for s in registry.values()]})
        self.milestones.start(self.run_id, self.output_dir)
        self.state = self._initial_state(work_order)
        self.state.outputs["project_root"] = self.project_policy["project_root"]
        self.state.outputs["project_version"] = self.project_policy["version"]
        self.state.outputs["milestone_id"] = self.milestones.selected_id

        registry.write(self._artifact("evidence-register.md"))
        self._add_claim("Authorized sources are hashed and registered.", ["EV-SRC-001"], "evidence-register.md")
        self._add_claim(
            "Every project is isolated under project/<project_id> with DEV and QA sandboxes.",
            ["EV-SRC-001"],
            "project-isolation-policy.md",
        )
        self._add_claim(
            "Every project and sandbox must declare the project frontend contract.",
            ["EV-SRC-001"],
            "frontend-template-policy.md",
        )
        self._add_claim(
            "Every project has an incremental roadmap and a persisted milestone state.",
            ["EV-SRC-001"],
            "roadmap.md",
        )
        self._write_workflow_yaml()
        self.mcp.write_policy()
        write_approval_matrix(self.output_dir)
        self.tools.write_manifest()
        self._write_factory_capability_manifests()
        self._write_agent_manifest()

        for phase in WORKFLOW_PHASES:
            self.state.phase = phase
            self.state.agent_id = PHASE_AGENTS[phase].agent_id
            result = self.harness.run_agent(PHASE_AGENTS[phase], self.state.to_dict(), lambda prompt, p=phase: self._run_phase(p, prompt))
            self.phase_results.append(result)
            self._record_phase(result)
            if not result.passed():
                self.state.status = "error"
                break

        if self.state.status != "error":
            self.state.status = "complete"
        self._write_supporting_close_artifacts()
        final_report = self._build_final_report()
        write_json(self._artifact("final-report.json"), final_report)
        self.artifacts.add("final-report.json")
        self._write_traceability()
        self._write_state()
        return final_report

    def _initial_state(self, work_order: WorkOrder) -> CycleState:
        input_hash = sha256_text(stable_json(work_order.to_dict()))
        return CycleState(
            run_id=self.run_id,
            cycle_id="CYC-001",
            workflow_version=WORKFLOW_VERSION,
            status="running",
            phase="intake",
            task_id="TASK-WEBFORGE-001",
            agent_id="agent.intake",
            input_hash=input_hash,
            spec_hash="sha256:TBD",
            plan_hash="sha256:TBD",
            tasks_hash="sha256:TBD",
            context_pack_id="CTX-TBD",
            context_pack_hash="sha256:TBD",
            repo_commit="not_applicable",
            policy_version=self.policy.version,
            tool_registry_version=self.tools.version,
            mcp_registry_version=self.mcp.version,
            memory_version=f"mem.webforge.project.{self.project_workspace.project_id}.v1",
            budget_remaining=self.budget.remaining,
            permissions={
                "read": ["authorized_sources", "workspace_runtime_files"],
                "write": ["output_artifacts", self.project_policy["project_root"]],
                "sandbox_write": ["project_sandbox_dev_workspace"],
                "external_write": self.work_order.side_effects == "approved_external_writes",
                "production_data": False,
                "deploy": self.work_order.side_effects == "approved_deploy",
                "factory_memory_read_allowed": False,
                "factory_learning_write_allowed": False,
                "milestone_id": self.milestones.selected_id,
            },
        )

    def _run_phase(self, phase: str, prompt_input: dict[str, Any]) -> PhaseResult:
        handlers = {
            "intake": self._phase_intake,
            "constitution": self._phase_constitution,
            "specify": self._phase_specify,
            "clarify": self._phase_clarify,
            "checklist": self._phase_checklist,
            "context": self._phase_context,
            "plan": self._phase_plan,
            "tasks": self._phase_tasks,
            "analyze": self._phase_analyze,
            "implement": self._phase_implement,
            "validate": self._phase_validate,
            "security": self._phase_security,
            "pr_handoff": self._phase_pr_handoff,
            "deploy_checkpoint": self._phase_deploy_checkpoint,
            "observe": self._phase_observe,
            "close": self._phase_close,
        }
        return handlers[phase](prompt_input)
