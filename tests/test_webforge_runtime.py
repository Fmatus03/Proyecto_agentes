from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from webforge import PRINCIPLES, WORKFLOW_PHASES, WebForgeFactory
from webforge.brewmaster import brewmaster_bundle, brewmaster_coverage, load_brewmaster_spec
from webforge.capabilities import FACTORY_SKILLS, validate_skill_package
from webforge.context import ContextManager, EvidenceRegistry, MemoryGate
from webforge.harness import AgentSpec, HarnessRunner
from webforge.milestones import default_milestones
from webforge.models import PhaseResult, WorkOrder
from webforge.policy import BudgetManager, MCPGateway, PolicyEngine
from webforge.principles import validate_principle_catalog
from webforge.tools import ToolRegistry, secret_scan
from webforge.validators import alembic_has_operations, no_catch_all_routes


ROOT = Path(__file__).resolve().parents[1]


def work_order() -> dict:
    return json.loads((ROOT / "examples" / "work_order_factory.json").read_text(encoding="utf-8"))


def write_sample_frontend_contract(root: Path) -> None:
    template = root / "sample-frontend-contract"
    template.mkdir(parents=True, exist_ok=True)
    for name in ["README.md", "CONTRACT.md"]:
        (template / name).write_text(f"# {name}\n", encoding="utf-8")


def write_minimal_skill_package(root: Path) -> None:
    skill = root / "skills" / "webforge-factory"
    (skill / "agents").mkdir(parents=True, exist_ok=True)
    (skill / "scripts").mkdir(parents=True, exist_ok=True)
    (skill / "references").mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(
        "---\nname: webforge-factory\ndescription: Minimal WEBFORGE test skill.\n---\n\n# WEBFORGE\n",
        encoding="utf-8",
    )
    (skill / "agents" / "openai.yaml").write_text("interface:\n  display_name: WEBFORGE\n", encoding="utf-8")
    (skill / "scripts" / "webforge_run.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    (skill / "references" / "operating-rules.md").write_text("# Rules\n", encoding="utf-8")


class WebForgeRuntimeTests(unittest.TestCase):
    def test_principle_catalog_is_complete(self) -> None:
        self.assertEqual([f"P{i:02d}" for i in range(1, 13)], list(PRINCIPLES))
        self.assertEqual([], validate_principle_catalog())
        for principle in PRINCIPLES.values():
            self.assertTrue(principle.gates)
            self.assertTrue(principle.evidence)

    def test_factory_run_generates_complete_operational_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "factory"
            tmp_root.mkdir()
            write_minimal_skill_package(tmp_root)
            report = WebForgeFactory(tmp_root).run(
                work_order(),
                Path(tmp) / "run",
                sources=[ROOT / "Diseno_detallado_fabrica_software_SDD-2.md"],
            )
            output = Path(tmp) / "run"
            self.assertEqual("complete", report["status"])
            self.assertEqual(100, report["critical_checks_passed_pct"])
            self.assertEqual(100, report["evidence_coverage_critical_claims"])
            self.assertEqual(0, report["secrets_detected"])
            self.assertEqual(WORKFLOW_PHASES, report["workflow_phases"])
            self.assertEqual([], report["missing_final_artifacts"])
            self.assertEqual("project/webforge-factory-runtime", report["project_workspace"]["project_root"])
            self.assertFalse(report["project_workspace"]["shared_with_factory"])
            self.assertEqual("WEBFORGE_FRONTEND_CONTRACT", report["frontend_template"]["template_name"])
            self.assertTrue(report["frontend_template"]["mandatory"])
            self.assertTrue(report["factory_skills"]["codex_skill_present"])
            self.assertGreaterEqual(len(report["factory_skills"]["skills"]), len(FACTORY_SKILLS))
            tool_ids = {tool["tool_id"] for tool in report["factory_tools"]["tools"]}
            self.assertIn("tool.validation.artifacts", tool_ids)
            self.assertIn("tool.security.secrets", tool_ids)
            self.assertIn("tool.sandbox.dev_materialize", tool_ids)
            sandbox_names = {item["name"] for item in report["project_sandboxes"]["sandboxes"]}
            self.assertEqual({"DEV", "QA"}, sandbox_names)
            for sandbox in report["project_sandboxes"]["sandboxes"]:
                self.assertEqual("WEBFORGE_FRONTEND_CONTRACT", sandbox["frontend_template"])
                self.assertEqual("true", sandbox["frontend_template_required"])
            for pid, coverage in report["principle_coverage"].items():
                self.assertEqual("pass", coverage["status"], pid)
                self.assertTrue(coverage["gates"], pid)
            for artifact in report["final_artifacts"]:
                self.assertTrue((output / artifact).exists(), artifact)
            traceability = (output / "traceability-matrix.md").read_text(encoding="utf-8")
            self.assertIn("state.json:present", traceability)
            self.assertIn("validation-report.json:present", traceability)

    def test_skill_package_and_cli_catalogs_exist(self) -> None:
        self.assertEqual([], validate_skill_package(ROOT))
        skill_md = ROOT / "skills" / "webforge-factory" / "SKILL.md"
        self.assertTrue(skill_md.exists())
        self.assertNotIn("TODO", skill_md.read_text(encoding="utf-8"))

        skills = json.loads(
            subprocess.check_output(
                [sys.executable, "-m", "webforge", "skills", "--project-root", str(ROOT)],
                cwd=ROOT,
                text=True,
            )
        )
        self.assertTrue(skills["codex_skill_present"])
        self.assertIn("skill.webforge.codex", {item["skill_id"] for item in skills["skills"]})

        tools = json.loads(
            subprocess.check_output(
                [sys.executable, "-m", "webforge", "tools", "--output", str(ROOT / "runs" / "tool-preview")],
                cwd=ROOT,
                text=True,
            )
        )
        self.assertEqual("deny_unregistered_tools", tools["default"])
        self.assertIn("tool.policy.static", {item["tool_id"] for item in tools["tools"]})
        self.assertIn("tool.sandbox.dev_materialize", {item["tool_id"] for item in tools["tools"]})

        doctor = json.loads(
            subprocess.check_output(
                [sys.executable, "skills/webforge-factory/scripts/webforge_run.py", "doctor", "--project-root", str(ROOT)],
                cwd=ROOT,
                text=True,
            )
        )
        self.assertEqual("pass", doctor["status"])

    def test_policy_and_mcp_are_default_deny(self) -> None:
        policy = PolicyEngine({"agent.intake"})
        self.assertTrue(policy.check_agent("agent.intake").allowed)
        self.assertFalse(policy.check_agent("agent.unknown").allowed)
        self.assertFalse(policy.check_action("external_write", {"external_write": False}).allowed)
        with tempfile.TemporaryDirectory() as tmp:
            mcp = MCPGateway(Path(tmp))
            decision = mcp.invoke("server.not_allowed", "read")
            self.assertFalse(decision.allowed)
            self.assertTrue((Path(tmp) / "mcp-invocations.jsonl").exists())

    def test_repeated_runs_have_same_logical_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "factory"
            tmp_root.mkdir()
            write_minimal_skill_package(tmp_root)
            sources = [ROOT / "Diseno_detallado_fabrica_software_SDD-2.md"]
            first = WebForgeFactory(tmp_root).run(work_order(), Path(tmp) / "one", sources=sources)
            second = WebForgeFactory(tmp_root).run(work_order(), Path(tmp) / "two", sources=sources)
            self.assertEqual(first["run_id"], second["run_id"])
            self.assertEqual(first["workflow_phases"], second["workflow_phases"])
            self.assertEqual(first["principle_coverage"], second["principle_coverage"])

    def test_project_memory_is_not_shared_with_factory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "factory"
            tmp_root.mkdir()
            write_minimal_skill_package(tmp_root)
            output = Path(tmp) / "run"
            report = WebForgeFactory(
                tmp_root,
            ).run(work_order(), output, sources=[ROOT / "Diseno_detallado_fabrica_software_SDD-2.md"])
            memory_report = json.loads((output / "memory-report.json").read_text(encoding="utf-8"))
            self.assertFalse(memory_report["factory_memory_read_allowed"])
            self.assertFalse(memory_report["factory_learning_write_allowed"])
            self.assertFalse(memory_report["shared_with_factory"])
            self.assertNotIn("Keep project isolation defaults", (output / "Aprendizaje.md").read_text(encoding="utf-8"))
            project_learning = tmp_root / report["project_workspace"]["learning_root"] / "Aprendizaje.md"
            self.assertIn("Keep project isolation defaults", project_learning.read_text(encoding="utf-8"))

    def test_independent_project_sandboxes_and_incremental_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "factory"
            tmp_root.mkdir()
            write_sample_frontend_contract(tmp_root)
            write_minimal_skill_package(tmp_root)
            wo = work_order()
            wo["project_id"] = "client-alpha"
            wo["project_version"] = "2"
            report = WebForgeFactory(tmp_root).run(
                wo,
                Path(tmp) / "run",
                sources=[ROOT / "Diseno_detallado_fabrica_software_SDD-2.md"],
            )
            self.assertEqual("complete", report["status"])
            self.assertEqual("project/client-alpha", report["project_workspace"]["project_root"])
            self.assertEqual("v0002", report["project_workspace"]["current_version"])
            sandboxes = {item["name"]: item for item in report["project_sandboxes"]["sandboxes"]}
            self.assertNotEqual(sandboxes["DEV"]["path"], sandboxes["QA"]["path"])
            self.assertNotEqual(sandboxes["DEV"]["sandbox_id"], sandboxes["QA"]["sandbox_id"])
            self.assertEqual("project/client-alpha/versions/v0002", sandboxes["DEV"]["clone_source"])
            self.assertEqual("project/client-alpha/versions/v0002", sandboxes["QA"]["clone_source"])
            for sandbox in sandboxes.values():
                self.assertEqual("false", sandbox["shared_with_factory"])
                self.assertEqual("WEBFORGE_FRONTEND_CONTRACT", sandbox["frontend_template"])
                self.assertEqual("true", sandbox["frontend_template_required"])
                self.assertTrue((tmp_root / sandbox["path"] / "sandbox-manifest.json").exists())
                self.assertTrue((tmp_root / sandbox["path"] / "frontend-template-manifest.json").exists())

    def test_missing_legacy_frontend_template_does_not_block_contract_based_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "factory"
            tmp_root.mkdir()
            write_minimal_skill_package(tmp_root)
            report = WebForgeFactory(tmp_root).run(
                work_order(),
                Path(tmp) / "run",
                sources=[ROOT / "Diseno_detallado_fabrica_software_SDD-2.md"],
            )
            self.assertEqual("complete", report["status"])
            self.assertEqual("WEBFORGE_FRONTEND_CONTRACT", report["frontend_template"]["template_name"])

    def test_secret_scan_blocks_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            secret_file = Path(tmp) / "secret.txt"
            secret_file.write_text("api_key=abcdefghijklmnop1234567890", encoding="utf-8")
            result = secret_scan([secret_file])
            self.assertEqual(1, result["blocking_findings"])
            self.assertEqual(1, result["secrets_detected"])

    def test_phase_order_reaches_implementation_after_analyze(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "factory"
            tmp_root.mkdir()
            write_minimal_skill_package(tmp_root)
            WebForgeFactory(tmp_root).run(
                work_order(),
                Path(tmp) / "run",
                sources=[ROOT / "Diseno_detallado_fabrica_software_SDD-2.md"],
            )
            lines = (Path(tmp) / "run" / "log.jsonl").read_text(encoding="utf-8").strip().splitlines()
            phases = [json.loads(line)["phase"] for line in lines]
            self.assertEqual(WORKFLOW_PHASES, phases)
            self.assertLess(phases.index("analyze"), phases.index("implement"))

    def test_nested_sources_are_loaded_into_context_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "factory"
            nested = tmp_root / "projects" / "uno"
            nested.mkdir(parents=True)
            write_sample_frontend_contract(tmp_root)
            write_minimal_skill_package(tmp_root)
            source = nested / "spec.md"
            source.write_text("# Nested spec\n\nRequirement from nested source.\n", encoding="utf-8")
            wo = work_order()
            wo["project_id"] = "nested-source-check"
            report = WebForgeFactory(tmp_root).run(wo, Path(tmp) / "run", sources=[source])
            context_pack = json.loads((Path(tmp) / "run" / "context-pack.json").read_text(encoding="utf-8"))
            self.assertEqual("complete", report["status"])
            self.assertEqual(1, context_pack["source_count"])
            self.assertEqual("section_index_with_snippets", context_pack["mode"])
            self.assertGreaterEqual(len(context_pack["section_index"]), 1)
            self.assertEqual(1, context_pack["document_count"])
            self.assertEqual("projects/uno/spec.md", context_pack["sources"][0]["path"])
            self.assertEqual(1, context_pack["sources"][0]["start_line"])
            rag_manifest = json.loads((Path(tmp) / "run" / "rag-index-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("authorized_sources_section_index", rag_manifest["retrieval"])
            self.assertEqual(len(context_pack["section_index"]), rag_manifest["section_count"])

    def test_dev_materializer_writes_work_order_bundle_to_dev_sandbox(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "factory"
            tmp_root.mkdir()
            write_sample_frontend_contract(tmp_root)
            write_minimal_skill_package(tmp_root)
            wo = work_order()
            wo["project_id"] = "materializer-demo"
            wo["metadata"] = {
                "implementation_bundle": [
                    {"path": "src/app.py", "content": "print('hola webforge')\n"},
                    {"path": "docs/README.md", "content": "# DEV bundle\n"},
                ]
            }
            report = WebForgeFactory(tmp_root).run(
                wo,
                Path(tmp) / "run",
                sources=[ROOT / "Diseno_detallado_fabrica_software_SDD-2.md"],
            )
            self.assertEqual("complete", report["status"])
            dev = next(item for item in report["project_sandboxes"]["sandboxes"] if item["name"] == "DEV")
            workspace = tmp_root / dev["path"] / "workspace"
            self.assertEqual("print('hola webforge')\n", (workspace / "src" / "app.py").read_text(encoding="utf-8"))
            self.assertEqual("# DEV bundle\n", (workspace / "docs" / "README.md").read_text(encoding="utf-8"))
            manifest = json.loads((Path(tmp) / "run" / "dev-materialization-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("webforge.isolation.p12_inv.v1", manifest["api"])
            self.assertEqual("pass", manifest["status"])
            self.assertEqual(2, manifest["bundle"]["file_count"])

    def test_milestone_run_creates_roadmap_state_and_promotes_to_qa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "factory"
            tmp_root.mkdir()
            write_minimal_skill_package(tmp_root)
            report = WebForgeFactory(tmp_root).run(
                {
                    "objective": "Build incremental alpha.",
                    "project_id": "alpha",
                    "project_version": "v0001",
                    "milestone_id": "HITO-001",
                    "acceptance_criteria": ["HITO-001 can close with evidence"],
                    "budget": {"tool_calls": 200, "mcp_calls": 0, "cost_usd": 0},
                },
                Path(tmp) / "run",
                sources=[ROOT / "Diseno_detallado_fabrica_software_SDD-2.md"],
            )
            self.assertEqual("complete", report["status"])
            self.assertEqual("HITO-001", report["milestone"]["milestone_id"])
            project_root = tmp_root / "project" / "alpha"
            self.assertTrue((project_root / "ROADMAP.md").exists())
            state = json.loads((project_root / "milestones" / "HITO-001" / "milestone-state.json").read_text(encoding="utf-8"))
            self.assertEqual("approved", state["status"])
            qa_workspace = project_root / "sandboxes" / "QA" / "workspace"
            self.assertTrue((qa_workspace / "implementation" / "WEBFORGE_IMPLEMENTATION.md").exists())
            gate = json.loads((Path(tmp) / "run" / "milestone-gate-report.json").read_text(encoding="utf-8"))
            self.assertEqual("advance", gate["decision"])

    def test_unknown_milestone_blocks_at_intake(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "factory"
            tmp_root.mkdir()
            write_minimal_skill_package(tmp_root)
            report = WebForgeFactory(tmp_root).run(
                {
                    "objective": "Build incremental alpha.",
                    "project_id": "alpha",
                    "milestone_id": "HITO-999",
                    "acceptance_criteria": ["Unknown milestone must fail closed"],
                },
                Path(tmp) / "run",
                sources=[ROOT / "Diseno_detallado_fabrica_software_SDD-2.md"],
            )
            self.assertEqual("error", report["status"])
            self.assertEqual("error", report["phase_status"]["intake"])

    def test_harness_enforces_agent_allowed_tools(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            budget = BudgetManager({"tool_calls": 10})
            tools = ToolRegistry(root, budget)
            harness = HarnessRunner(
                PolicyEngine({"agent.limited"}),
                budget,
                ContextManager(EvidenceRegistry()),
                MemoryGate("alpha", root / "memory", root / "learning"),
                MCPGateway(root),
                tools,
            )

            def handler(_: dict) -> PhaseResult:
                result = tools.run("tool.security.secrets", lambda: {"blocking_findings": 0})
                return PhaseResult("limited", "agent.limited", result.status, {}, [], [])

            result = harness.run_agent(AgentSpec("agent.limited", "limited", "Limited", allowed_tools=()), {"task_id": "T1"}, handler)
            self.assertEqual("error", result.status)
            tool_log = (root / "tool-logs.jsonl").read_text(encoding="utf-8")
            self.assertIn("tool_permission", tool_log)

    def test_dev_materializer_blocks_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "factory"
            tmp_root.mkdir()
            write_sample_frontend_contract(tmp_root)
            write_minimal_skill_package(tmp_root)
            wo = work_order()
            wo["project_id"] = "materializer-block"
            wo["metadata"] = {"implementation_bundle": [{"path": "../escape.txt", "content": "no\n"}]}
            report = WebForgeFactory(tmp_root).run(
                wo,
                Path(tmp) / "run",
                sources=[ROOT / "Diseno_detallado_fabrica_software_SDD-2.md"],
            )
            self.assertEqual("error", report["status"])
            self.assertEqual("error", report["phase_status"]["implement"])
            self.assertFalse((tmp_root / "project" / "materializer-block" / "sandboxes" / "DEV" / "escape.txt").exists())

    def test_brewmaster_work_order_materializes_mvp_blueprint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wo = {
                "objective": "Implementar BrewMaster segun especificacion completa.",
                "project_id": "BrewMaster",
                "project_version": "v0001",
                "type": "brewmaster_mvp",
                "scope": "local_artifacts_only",
                "side_effects": "no_external_writes_no_deploy",
                "authorized_sources": [
                    "fabricas_agentes_ia.md",
                    "projects/BrewMaster/brewmaster_especificacion_completa.md",
                ],
                "acceptance_criteria": [
                    "BrewMaster declara los modulos MVP de la especificacion.",
                    "BrewMaster declara exactamente 30 pantallas.",
                    "BrewMaster usa endpoints /api/v1 y acciones REST consistentes.",
                    "BrewMaster materializa backend, frontend, contratos y pruebas en DEV.",
                ],
                "budget": {"tool_calls": 200, "mcp_calls": 0, "cost_usd": 0},
                "metadata": {"blueprint": "brewmaster"},
            }
            tmp_root = Path(tmp) / "factory"
            tmp_root.mkdir()
            write_minimal_skill_package(tmp_root)
            report = WebForgeFactory(tmp_root).run(
                wo,
                Path(tmp) / "run",
                sources=[
                    ROOT / "fabricas_agentes_ia.md",
                    ROOT / "projects" / "BrewMaster" / "brewmaster_especificacion_completa.md",
                ],
            )
            self.assertEqual("complete", report["status"])
            self.assertEqual("BREWMASTER_REACT_BOOTSTRAP", report["frontend_template"]["template_name"])
            self.assertNotEqual("PLANTILLA_FRONTEND", report["frontend_template"]["template_name"])
            coverage = json.loads((Path(tmp) / "run" / "brewmaster-coverage.json").read_text(encoding="utf-8"))
            self.assertEqual(30, coverage["screen_count"])
            self.assertTrue(all(coverage["acceptance_gate"].values()))
            validation = json.loads((Path(tmp) / "run" / "validation-report.json").read_text(encoding="utf-8"))
            self.assertEqual("pass", validation["brewmaster"]["status"])
            self.assertTrue(validation["brewmaster"]["acceptance_gate"]["uses_react_bootstrap_contract"])
            self.assertTrue(validation["brewmaster"]["acceptance_gate"]["does_not_force_plantilla_frontend"])
            self.assertTrue(validation["brewmaster"]["acceptance_gate"]["materialized_react_bootstrap_files"])
            dev = next(item for item in report["project_sandboxes"]["sandboxes"] if item["name"] == "DEV")
            self.assertEqual("BREWMASTER_REACT_BOOTSTRAP", dev["frontend_template"])
            workspace = tmp_root / dev["path"] / "workspace"
            self.assertTrue((workspace / "backend" / "app" / "main.py").exists())
            self.assertTrue((workspace / "frontend" / "src" / "App.jsx").exists())
            self.assertTrue((workspace / "contracts" / "brewmaster-blueprint.json").exists())
            self.assertEqual(40, coverage["endpoint_count"])
            self.assertEqual(100, coverage["validation_count"])
            self.assertEqual(42, coverage["permission_count"])
            self.assertEqual(40, brewmaster_coverage()["endpoint_count"])
            self.assertTrue(no_catch_all_routes(workspace / "backend" / "app" / "main.py").passed)
            self.assertTrue(alembic_has_operations(workspace / "backend" / "alembic" / "versions" / "0001_brewmaster_schema.py").passed)
            env = dict(os.environ)
            env["PYTHONPATH"] = str(workspace / "backend")
            subprocess.check_call(
                [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(workspace / "tests")],
                cwd=workspace,
                env=env,
            )

    def test_brewmaster_default_milestones_match_j12(self) -> None:
        wo = work_order()
        wo["objective"] = "Implementar BrewMaster por hitos J.12."
        wo["project_id"] = "BrewMaster"
        wo["type"] = "brewmaster_mvp"
        milestones = default_milestones(WorkOrder.from_dict(wo))
        self.assertEqual(
            [
                "Fundamentos",
                "Maestros",
                "Inventario",
                "Produccion",
                "Ventas",
                "Dashboard",
                "Cierre",
            ],
            [milestone.name for milestone in milestones],
        )
        self.assertEqual([f"HITO-{index:03d}" for index in range(1, 8)], [milestone.milestone_id for milestone in milestones])
        self.assertEqual([], milestones[0].dependencies)
        for index, milestone in enumerate(milestones[1:], start=1):
            self.assertEqual([milestones[index - 1].milestone_id], milestone.dependencies)
            self.assertIn(f"J.12 Hito {index + 1}", milestone.inputs)

    def test_brewmaster_spec_model_matches_official_contract(self) -> None:
        spec = load_brewmaster_spec()
        self.assertTrue(spec.parsed)
        self.assertEqual(30, len(spec.screens))
        self.assertEqual(40, len(spec.endpoints))
        self.assertEqual(100, len(spec.validations))
        self.assertEqual(42, len(spec.permissions))
        self.assertEqual({f"V{index:03d}" for index in range(1, 101)}, {item["id"] for item in spec.validations})
        self.assertEqual(
            ("POST", "/api/v1/auth/login"),
            (spec.endpoints[0]["method"], spec.endpoints[0]["path"]),
        )

    def test_brewmaster_bundle_has_explicit_routes_and_real_migration(self) -> None:
        files = {item["path"]: item["content"] for item in brewmaster_bundle()}
        main_py = files["backend/app/main.py"]
        migration = files["backend/alembic/versions/0001_brewmaster_schema.py"]
        self.assertNotIn('/api/v1/{resource}', main_py)
        self.assertIn("@app.post('/api/v1/auth/login')", main_py)
        self.assertIn("op.create_table(", migration)
        self.assertNotIn("def upgrade():\n    pass", migration)

    def test_validators_fail_on_catch_all_and_empty_migration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            main_py = root / "main.py"
            migration = root / "0001.py"
            main_py.write_text('@app.api_route("/api/v1/{resource}", methods=["GET"])\ndef route():\n    pass\n', encoding="utf-8")
            migration.write_text("def upgrade():\n    pass\n", encoding="utf-8")
            self.assertFalse(no_catch_all_routes(main_py).passed)
            self.assertFalse(alembic_has_operations(migration).passed)


if __name__ == "__main__":
    unittest.main()
