from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .capabilities import skill_manifest, validate_skill_package
from .orchestrator import WebForgeFactory
from .principles import ordered_principles
from .policy import BudgetManager
from .tools import ToolRegistry


def _load_work_order(args: argparse.Namespace) -> dict:
    if args.work_order:
        data = json.loads(Path(args.work_order).read_text(encoding="utf-8"))
        if args.project_id:
            data["project_id"] = args.project_id
        if args.project_version:
            data["project_version"] = args.project_version
        if args.milestone:
            data["milestone_id"] = args.milestone
        return data
    if not args.objective:
        raise SystemExit("--objective or --work-order is required")
    return {
        "objective": args.objective,
        "project_id": args.project_id or "",
        "project_version": args.project_version or "v0001",
        "milestone_id": args.milestone or "",
        "type": args.type,
        "scope": "local_artifacts_only",
        "side_effects": "no_external_writes_no_deploy",
        "acceptance_criteria": args.acceptance or ["P01-P12 pass at 100 percent", "Required artifacts are generated"],
        "budget": {"tool_calls": args.max_tool_calls, "mcp_calls": 0, "cost_usd": 0},
    }


def run_command(args: argparse.Namespace) -> int:
    root = Path(args.project_root).resolve()
    output_dir = Path(args.output).resolve()
    work_order = _load_work_order(args)
    sources = [Path(item).resolve() for item in args.source] if args.source else None
    report = WebForgeFactory(root).run(work_order, output_dir, sources=sources)
    print(json.dumps({"status": report["status"], "run_id": report["run_id"], "output_dir": str(output_dir)}, indent=2))
    return 0 if report["status"] == "complete" else 1


def principles_command(_: argparse.Namespace) -> int:
    for principle in ordered_principles():
        print(f"{principle.id}: {principle.name} | gates={','.join(principle.gates)}")
    return 0


def skills_command(args: argparse.Namespace) -> int:
    root = Path(args.project_root).resolve()
    print(json.dumps(skill_manifest(root), indent=2, sort_keys=True))
    return 0


def tools_command(args: argparse.Namespace) -> int:
    output_dir = Path(args.output).resolve()
    registry = ToolRegistry(output_dir, BudgetManager({"tool_calls": 1}))
    print(json.dumps(registry.manifest(), indent=2, sort_keys=True))
    return 0


def doctor_command(args: argparse.Namespace) -> int:
    root = Path(args.project_root).resolve()
    errors = validate_skill_package(root)
    report = {
        "status": "pass" if not errors else "error",
        "skill_package_errors": errors,
        "skill_manifest": skill_manifest(root),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="webforge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the local WEBFORGE SDD factory.")
    run_parser.add_argument("--project-root", default=".")
    run_parser.add_argument("--output", default="runs/latest")
    run_parser.add_argument("--work-order")
    run_parser.add_argument("--objective")
    run_parser.add_argument("--project-id", "--project", dest="project_id", default="")
    run_parser.add_argument("--project-version", default="")
    run_parser.add_argument("--milestone", default="")
    run_parser.add_argument("--type", default="factory_runtime")
    run_parser.add_argument("--acceptance", action="append")
    run_parser.add_argument("--source", action="append", default=[])
    run_parser.add_argument("--max-tool-calls", type=int, default=200)
    run_parser.set_defaults(func=run_command)

    p_parser = subparsers.add_parser("principles", help="Print P01-P12 controls.")
    p_parser.set_defaults(func=principles_command)

    skills_parser = subparsers.add_parser("skills", help="Print WEBFORGE factory skill catalog.")
    skills_parser.add_argument("--project-root", default=".")
    skills_parser.set_defaults(func=skills_command)

    tools_parser = subparsers.add_parser("tools", help="Print WEBFORGE deterministic tool registry.")
    tools_parser.add_argument("--output", default="runs/tool-preview")
    tools_parser.set_defaults(func=tools_command)

    doctor_parser = subparsers.add_parser("doctor", help="Validate the WEBFORGE skill/tool package.")
    doctor_parser.add_argument("--project-root", default=".")
    doctor_parser.set_defaults(func=doctor_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
