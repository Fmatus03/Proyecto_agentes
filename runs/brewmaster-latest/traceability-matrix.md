# Traceability matrix

| principle | gates | evidence | status |
|---|---|---|---|
| P01 Maxima reproducibilidad practica | schema, budget, final_format | state.json:present, validation-report.json:present | pass |
| P02 No invencion | frontend_template, spec, clarification, evidence, plan_validation, frontend_template, frontend_template, frontend_template, brewmaster_functional_coverage | evidence-register.md:present, claim-map.md:present | pass |
| P03 Memoria/contexto limpio | project_isolation, context, project_isolation, project_isolation, secrets | memory-report.json:present, Aprendizaje.md:present | pass |
| P04 RAG/index/cache | context, evidence | context-pack.json:present, rag-index-manifest.json:present | pass |
| P05 ARNES/orquestador/agentes/skills | project_isolation, frontend_template, factory_skills, constitution, frontend_template, factory_skills, policy, project_isolation, frontend_template, factory_skills, project_isolation, frontend_template, factory_skills | agent-manifest.json:present, validation-report.json:present | pass |
| P06 Tools deterministas | factory_skills, sandbox, factory_skills, sandbox, factory_skills, tests, sandbox, factory_skills | tool-logs.jsonl:present, tool-registry.json:present | pass |
| P07 Aprendizaje gobernado | human_approval, learning | ERRORS.md:present, Aprendizaje.md:present | pass |
| P08 Gates por fase | schema, project_isolation, frontend_template, factory_skills, constitution, spec, clarification, checklist, context, plan_validation, frontend_template, factory_skills, tasks, analyze, policy, project_isolation, frontend_template, factory_skills, tests, coverage, project_isolation, frontend_template, factory_skills, brewmaster_functional_coverage | validation-report.json:present, phase-ledger.json:present | pass |
| P09 Logs/trazas | observability | state.json:present, log.jsonl:present, billing-ledger.json:present, traceability-matrix.md:present | pass |
| P10 Workflows SDD | constitution, tasks, analyze, brewmaster_functional_coverage, final_format | workflow.yaml:present, final-report.json:present | pass |
| P11 MCP gobernado | mcp_policy, human_approval | mcp-policy.yaml:present, mcp-invocations.jsonl:present | pass |
| P12 Seguridad/escalabilidad | budget, project_isolation, frontend_template, dependency, sandbox, frontend_template, sandbox, project_isolation, frontend_template, sandbox, project_isolation, frontend_template, secrets, dependency, sbom, rollback | security-review.md:present, rollback-plan.md:present, sbom.json:present | pass |
