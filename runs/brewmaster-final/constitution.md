# Constitution P01-P12

## P01 Maxima reproducibilidad practica
- Control: Workflow fijo, versiones, hashes y rutas cerradas de retry.
- Gates: schema, stability, budget, final_format
- Evidence: state.json, validation-report.json

## P02 No invencion
- Control: Todo claim critico requiere evidence_id o queda bloqueado.
- Gates: evidence, context, plan_validation
- Evidence: evidence-register.md, claim-map.md

## P03 Memoria/contexto limpio
- Control: Contexto minimo, redaccion, taint tracking y memoria propose_only.
- Gates: memory, safety, secrets
- Evidence: memory-report.json, Aprendizaje.md

## P04 RAG/index/cache
- Control: Context-pack con evidencia, hashes, snippets y cache por hash.
- Gates: context, budget, evidence
- Evidence: context-pack.json, rag-index-manifest.json

## P05 ARNES/orquestador/agentes/skills
- Control: Unica puerta harness.run_agent; agentes aislados por policy.
- Gates: policy, schema, constitution
- Evidence: agent-manifest.json, validation-report.json

## P06 Tools deterministas
- Control: ToolRegistry allowlisted con schemas, timeouts y logs.
- Gates: tool-output, sandbox, tests, security
- Evidence: tool-logs.jsonl, tool-registry.json

## P07 Aprendizaje gobernado
- Control: Errores producen MemoryProposal pendiente; nunca activacion automatica.
- Gates: learning, human_approval, regression_eval
- Evidence: ERRORS.md, Aprendizaje.md

## P08 Gates por fase
- Control: Cada fase declara gates criticos y no avanza si alguno falla.
- Gates: spec, context, plan_validation, tests, coverage
- Evidence: validation-report.json, phase-ledger.json

## P09 Logs/trazas
- Control: State, log JSONL, billing ledger y matriz req-task-test-evidence.
- Gates: observability
- Evidence: state.json, log.jsonl, billing-ledger.json, traceability-matrix.md

## P10 Workflows SDD
- Control: Constitution -> Specify -> Clarify -> Checklist -> Context -> Plan -> Tasks -> Analyze -> Implement -> Validate -> PR/Deploy -> Observe -> Close.
- Gates: tasks, analyze, final_format
- Evidence: workflow.yaml, final-report.json

## P11 MCP gobernado
- Control: MCP default-deny, allowlist explicita, pre/post gates y logs.
- Gates: mcp_policy, tool-output, human_approval
- Evidence: mcp-policy.yaml, mcp-invocations.jsonl

## P12 Seguridad/escalabilidad
- Control: Sandbox, dry-run, secret/dependency scans, SBOM, SLOs y rollback.
- Gates: security, dependency, secrets, budget, rollback
- Evidence: security-review.md, rollback-plan.md, sbom.json
