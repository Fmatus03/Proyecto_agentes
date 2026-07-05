# Spec

Objective: Implementar BrewMaster Hito 1 - Fundamentos: Auth JWT, usuarios, roles, auditoria y estructura de proyecto
Type: factory_runtime

## Actors
- Operator: runs the local factory.
- Reviewer: inspects artifacts and gates.

## Functional requirements
- RF01: Execute the complete SDD workflow with closed states.
- RF02: Produce required operational artifacts.
- RF03: Enforce P01-P12 gates before complete.
- RF04: Keep every project isolated under project/<project_id>.
- RF05: Create independent DEV and QA sandboxes cloned from the current project version.
- RF06: Use the project frontend contract declared by the specification or WorkOrder.
- RF07: Expose WEBFORGE as a Codex Skill with deterministic tools.
- RF08: Materialize implementation bundles into DEV only through the P12/INV isolation API.

## Non-functional requirements
- RNF01: No external writes or deploy by default.
- RNF02: Deterministic local execution with hashed evidence.
- RNF03: Logs must be reconstructible.
- RNF04: Project memory and learning never share state with factory memory.
- RNF05: Frontend work cannot use another template unless the factory policy is changed.
- RNF06: Skill and tool catalog must be present before complete.

## Acceptance criteria
- AC01: P01-P12 pass at 100 percent
- AC02: Required artifacts are generated

## Out of scope
- Real production deploy.
- External CI/PR creation without approval.
- Runtime activation of unapproved MCP servers.
