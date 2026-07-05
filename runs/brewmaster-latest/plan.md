# Plan

1. Run SDD phases in fixed order.
2. Materialize required artifacts locally.
3. Enforce P01-P12 through phase gates and final coverage.
4. Keep external side effects denied until approval.
5. Keep project work under project/<project_id> with isolated memory.
6. Promote incremental work through independent DEV and QA sandboxes.
7. Use the declared project frontend contract instead of a global frontend template.
8. Use WEBFORGE Skill and deterministic tools as the factory interface.
9. Materialize implementation bundles into DEV through the P12/INV isolation API.
10. Close with validation, security, traceability and final report.

## Risks
- External CI and deploy remain intentionally blocked.
- Generated app stack choices are outside this local runtime implementation.
- Project contamination is blocked by project_isolation and memory gates.
- Frontend drift is blocked by frontend_template gate.
- Partial factory operation is blocked by factory_skills gate.
