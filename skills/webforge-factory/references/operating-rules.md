# WEBFORGE Operating Rules

## Invariants

- `project/<project_id>/` is the only valid project root.
- `memory/` and `learning/` inside a project are project-scoped only.
- `sandboxes/DEV` and `sandboxes/QA` are mandatory independent clones from `versions/<version>`.
- A project-specific frontend contract is mandatory and must be declared by hash in project, version and sandbox manifests.
- BrewMaster must use the React + Bootstrap contract from `projects/BrewMaster/brewmaster_especificacion_completa.md`; no legacy static template may override that specification.
- BrewMaster must remain a spec-derived verifiable MVP: 30 screens, exactly 40 `/api/v1` endpoints, V001-V100, declared permissions, explicit FastAPI routes, non-empty Alembic operations and passing generated tests.
- `factory-skill-manifest.json` and `factory-tool-manifest.json` must be present in every complete run.
- Every project must maintain an incremental `ROADMAP.md` and machine-readable `roadmap.json`.
- Milestone state must persist under `project/<project_id>/milestones/<milestone_id>/milestone-state.json`.
- A milestone can advance only after DEV validation, milestone gate evidence, QA promotion and regression evidence pass.

## Tool Surface

WEBFORGE tools are allowlisted through `ToolRegistry`; unknown tools are denied. Current deterministic tools:

- `tool.security.secrets`
- `tool.security.deps`
- `tool.sbom.generate`
- `tool.policy.static`
- `tool.validation.artifacts`
- `tool.sandbox.dev_materialize`

`tool.sandbox.dev_materialize` is the only approved implementation side-effect path. It must write text bundles only under `project/<project_id>/sandboxes/DEV/workspace` through the P12/INV isolation API, reject traversal/absolute/reserved paths, reject detected secrets, emit `dev-materialization-manifest.json`, and leave external writes at zero.

`AgentSpec.allowed_tools` is enforced at runtime. `HarnessRunner` scopes each agent execution and `ToolRegistry` must deny tool calls outside the current agent allowlist while logging pre/post tool events.

## Closure

`complete` requires executable validator-backed gates, 100 percent critical evidence coverage, zero detected secrets, no unsafe unapproved actions, no missing required artifacts, derived traceability, and P01-P12 all `pass`.

Incremental closure also requires `milestone-validation-report.json`, `milestone-gate-report.json`, `qa-promotion-report.json`, `regression-report.json` and `incremental-traceability.md`.
