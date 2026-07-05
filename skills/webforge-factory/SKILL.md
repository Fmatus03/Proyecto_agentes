---
name: webforge-factory
description: Run and govern the WEBFORGE SDD software factory. Use when Codex is asked to operate, implement, audit, repair, or explain the factory; enforce P01-P12; create project project-id workspaces; keep project memory isolated from factory memory; require DEV/QA sandboxes; require the project-specific frontend contract; run WEBFORGE tools/gates; or produce final evidence from runs/latest.
---

# WEBFORGE Factory

Use this skill to operate WEBFORGE as a deterministic local SDD factory, not as loose documentation.

## Scope Terms

- `webforge/` is the factory runtime.
- `project/<project_id>/` is generated project output: versions, DEV/QA sandboxes, isolated memory and generated MVP files.
- `legacy_artifacts/` is historical material and is not part of default scans or gates.
- `scaffold` means structure only; it is not enough for `complete`.
- `verifiable MVP` means local artifacts plus executable validators, generated tests, explicit API routes, real migrations, traceability and evidence.
- `production` is out of scope unless the user explicitly approves deploy, real data and external writes.

## Hard Rules

- Always run projects under `project/<project_id>/`.
- Never share project memory or learning with factory memory.
- Always create independent `sandboxes/DEV` and `sandboxes/QA`.
- Always require the project-specific frontend contract for every frontend project, version and sandbox. For BrewMaster this contract is React + Bootstrap, as defined by `projects/BrewMaster/brewmaster_especificacion_completa.md`.
- Never mark work complete unless `final-report.json` is `complete`, P01-P12 pass, every critical gate has executable evidence, and no required artifact is missing.
- For incremental project work, run one milestone at a time with `--milestone HITO-###`; every project must keep `ROADMAP.md`, persisted milestone state, DEV validation, QA promotion, regression evidence and incremental traceability.
- For BrewMaster, require a spec-derived blueprint with 30 screens, exactly 40 `/api/v1` endpoints, V001-V100, declared permissions, explicit FastAPI routes, a non-empty Alembic migration and passing generated tests.
- Treat external writes, PR creation, production data and deploy as denied until explicitly approved.

## Standard Workflow

1. Inspect the request and build or select a WorkOrder.
2. Run WEBFORGE through the script wrapper:

```bash
python3 skills/webforge-factory/scripts/webforge_run.py run --project-root . --work-order examples/work_order_factory.json --output runs/latest
```

For incremental runs:

```bash
python3 skills/webforge-factory/scripts/webforge_run.py run --project-root . --project brewmaster --milestone HITO-001 --objective "Implement BrewMaster milestone HITO-001"
```

3. Verify capabilities:

```bash
python3 skills/webforge-factory/scripts/webforge_run.py doctor --project-root .
python3 skills/webforge-factory/scripts/webforge_run.py skills --project-root .
python3 skills/webforge-factory/scripts/webforge_run.py tools --output runs/tool-preview
```

4. Inspect `runs/latest/final-report.json` and fail closed if status is not `complete`.
5. Inspect `runs/latest/validation-report.json`; gates must include `validator_id`, observed inputs/results and failure cause when applicable.
6. Inspect `runs/latest/traceability-matrix.md`; statuses must be derived from executed gates and present evidence.
7. For changed runtime behavior, run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
```

## Required Evidence

Every complete run must include:

- `factory-skill-manifest.json`
- `factory-tool-manifest.json`
- `project-isolation-policy.md`
- `project-manifest.json`
- `project-sandboxes.json`
- `frontend-template-manifest.json`
- `validation-report.json`
- `milestone-validation-report.json`
- `milestone-gate-report.json`
- `qa-promotion-report.json`
- `regression-report.json`
- `incremental-traceability.md`
- `security-review.md`
- `traceability-matrix.md`
- `final-report.json`

## References

Read `references/operating-rules.md` when changing policies, gates, tools, project isolation, sandbox behavior or frontend contract enforcement.
