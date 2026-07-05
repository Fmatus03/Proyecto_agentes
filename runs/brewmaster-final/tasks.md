# Tasks

| task | requirement | test/evidence |
|---|---|---|
| T01 | P01 Maxima reproducibilidad practica | gates=schema, stability, budget, final_format; evidence=state.json, validation-report.json |
| T02 | P02 No invencion | gates=evidence, context, plan_validation; evidence=evidence-register.md, claim-map.md |
| T03 | P03 Memoria/contexto limpio | gates=memory, safety, secrets; evidence=memory-report.json, Aprendizaje.md |
| T04 | P04 RAG/index/cache | gates=context, budget, evidence; evidence=context-pack.json, rag-index-manifest.json |
| T05 | P05 ARNES/orquestador/agentes/skills | gates=policy, schema, constitution; evidence=agent-manifest.json, validation-report.json |
| T06 | P06 Tools deterministas | gates=tool-output, sandbox, tests, security; evidence=tool-logs.jsonl, tool-registry.json |
| T07 | P07 Aprendizaje gobernado | gates=learning, human_approval, regression_eval; evidence=ERRORS.md, Aprendizaje.md |
| T08 | P08 Gates por fase | gates=spec, context, plan_validation, tests, coverage; evidence=validation-report.json, phase-ledger.json |
| T09 | P09 Logs/trazas | gates=observability; evidence=state.json, log.jsonl, billing-ledger.json, traceability-matrix.md |
| T10 | P10 Workflows SDD | gates=tasks, analyze, final_format; evidence=workflow.yaml, final-report.json |
| T11 | P11 MCP gobernado | gates=mcp_policy, tool-output, human_approval; evidence=mcp-policy.yaml, mcp-invocations.jsonl |
| T12 | P12 Seguridad/escalabilidad | gates=security, dependency, secrets, budget, rollback; evidence=security-review.md, rollback-plan.md, sbom.json |
| T13 | Project isolation | project_isolation gate; project-manifest.json; project-sandboxes.json |
| T14 | Mandatory project frontend contract | frontend_template gate; frontend-template-manifest.json |
| T15 | Factory Skill and tools | factory_skills gate; factory-skill-manifest.json; factory-tool-manifest.json |
| T16 | DEV materializer | sandbox gate; dev-materialization-manifest.json; tool-logs.jsonl |
