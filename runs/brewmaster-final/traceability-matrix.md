# Traceability matrix

| principle | gates | evidence | status |
|---|---|---|---|
| P01 Maxima reproducibilidad practica | schema, stability, budget, final_format | state.json, validation-report.json | pass |
| P02 No invencion | evidence, context, plan_validation | evidence-register.md, claim-map.md | pass |
| P03 Memoria/contexto limpio | memory, safety, secrets | memory-report.json, Aprendizaje.md | pass |
| P04 RAG/index/cache | context, budget, evidence | context-pack.json, rag-index-manifest.json | pass |
| P05 ARNES/orquestador/agentes/skills | policy, schema, constitution | agent-manifest.json, validation-report.json | pass |
| P06 Tools deterministas | tool-output, sandbox, tests, security | tool-logs.jsonl, tool-registry.json | pass |
| P07 Aprendizaje gobernado | learning, human_approval, regression_eval | ERRORS.md, Aprendizaje.md | pass |
| P08 Gates por fase | spec, context, plan_validation, tests, coverage | validation-report.json, phase-ledger.json | pass |
| P09 Logs/trazas | observability | state.json, log.jsonl, billing-ledger.json, traceability-matrix.md | pass |
| P10 Workflows SDD | tasks, analyze, final_format | workflow.yaml, final-report.json | pass |
| P11 MCP gobernado | mcp_policy, tool-output, human_approval | mcp-policy.yaml, mcp-invocations.jsonl | pass |
| P12 Seguridad/escalabilidad | security, dependency, secrets, budget, rollback | security-review.md, rollback-plan.md, sbom.json | pass |
