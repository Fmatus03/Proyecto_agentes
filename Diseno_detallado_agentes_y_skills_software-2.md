# FILE: Diseno_detallado_agentes_y_skills_software.md

## 1. Propósito

| campo | valor |
|---|---|
| `artifact` | Diseño detallado de agentes, skills, herramientas y MCP para WEBFORGE |
| `work_order_id` | `WO-WEBFORGE-001` |
| `status_diseño` | `complete` |
| `fecha_generacion` | `2026-06-30` |
| `principio` | Crear agentes solo si separan responsabilidad, permisos, memoria, tools, riesgo o artefacto |

Este archivo define el catálogo operativo de agentes, skills determinísticas, tools, permisos, MCPPolicy y evals de WEBFORGE. El diseño evita “un agente gigante” y prefiere una línea de producción con agentes pequeños bajo ARNES.

## 2. Evidencia usada

| evidence_id | fuente local | uso | sha256 |
|---|---|---|---|
| EV-WF-001 | `Pegado text.txt` | Brief/especificación WEBFORGE adjunta | `4b808120b8874f21c4b9d06ac3ef0b0dd1b1921e389837aa8cfee2378e9ff23b` |
| EV-MASTER-001 | `PLANTILLAS_FABRICA_AGENTICA_12P_MASTER.md` | Plantilla maestra 12P | `88a9e2e87d6a510fcfafc65c3ae3a7873a17ef5ee519630fcd4ae6780ab4a919` |
| EV-MANIFEST-001 | `manifest.json` | Inventario/hashes de anexos | `612ecbfa949b2a4589eee3bab85b6ae17539273568e44facb22105788588b493` |
| EV-PROMPT-001 | `00_PROMPT_GPT_FABRICADOR.md` | Contrato del fabricador y estados cerrados | `f8c9bc88b86fcb7a67a91b33d36beb1ea21382658fcd988c5d76e482bc694381` |
| EV-CONST-001 | `01_CONSTITUCION_12_PRINCIPIOS.md` | Definiciones P01-P12 | `ce2149a010b3ec19d6d7d82cf036fb0e6a0440a6cc23509fdc5bf8dd97938662` |
| EV-WO-001 | `02_WORKORDER_SPEC_SDD.md` | WorkOrder y flujo SDD | `bb5888930d567df1843064863654049bfa4e508977933ccf023eb00bb65b0962` |
| EV-ARNES-001 | `03_ARQUITECTURA_ARNES_HARNESS.md` | ARNES/Harness de referencia | `61e091a107eb912d0204ea6d068e9f032ab4bed1f905d2db9018ef1cbc0cd738` |
| EV-AGENTS-001 | `04_AGENTES_SKILLS_HERRAMIENTAS_MCP.md` | AgentSpec, SkillSpec, ToolSpec, MCPPolicy | `8a1910e53d4ac8e4e9f7c03db567192a99206c88b2efddfcc4e94e9519ca0ce8` |
| EV-RAG-001 | `05_RAG_MEMORIA_CACHE_APRENDIZAJE.md` | RAG, memoria, cache y aprendizaje gobernado | `e85efbf155a4232a32ac85c8fbbe3bdbd53bac84e7c4df3bb0d7e9cbac86fcbe` |
| EV-GATES-001 | `06_GATES_VALIDADORES_EVALS_QA.md` | Catálogo de gates, validadores y evals | `4564e82c75bb2aafbe6c5ae686e9d1f3a3299efa6500254a02160b6c79ecd785` |
| EV-OPS-001 | `07_OPERABILIDAD_OBSERVABILIDAD_COSTOS.md` | Logs, ledger, SLOs y runbooks | `26e4b47ad779713bdaa6d95f5e2b5f64cb1f5cd58408dc8d464496346cd12eee` |
| EV-SEC-001 | `08_SEGURIDAD_ESCALABILIDAD_WORKFLOWS.md` | Seguridad, escalabilidad y workflows | `0725f7a2f12dbfa88d0a5c7a1bbd2e1ad86c01586d51f5d95feb56fc360921e9` |
| EV-CHECK-001 | `10_CHECKLIST_DOBLE_REVISION_Y_AUDITORIA.md` | Doble revisión y criterio de salida | `9359999a15db369d1f57820b904216b864fe440a969698d26f70d2efd84f57be` |
| EV-SDDV2-001 | `especificaciones_software_factory_spec_driven_v2.md` | Super fábrica SDD de software | `b57010c4764eb1e22aad8950079cdc9c535d4bb78fb9bd925dd54dbeef3661c4` |
| EV-DETERMINISM-001 | `prompting_deterministico_gpt_55_resumen.md` | Reproducibilidad práctica GPT-5.x/5.5 | `7518eeab11534d3011103e332bee3cfafc53319eec35b84781b5322cb0dac662` |
| EV-FRAME-001 | `marco_trabajo_asistente_gpt_55.md` | Marco de asistente GPT-5.x/5.5 | `8e430a313e71d465b2d3f3e7a4a2aed354d3bc653e87f1da8030dc3c7b9f477e` |

## 3. Reglas de diseño de agentes

1. Un agente tiene una responsabilidad única y salida validable.
2. Si una skill determinística resuelve la tarea, no se crea agente.
3. Ningún agente llama a otro agente.
4. Ningún agente ejecuta tools o MCP directamente; solicita capacidades al ARNES.
5. Ningún agente aprueba su propio output crítico.
6. Cada agente declara inputs, outputs, tools, MCP, permisos, gates, memoria y evals.
7. Cada salida tiene schema estricto o Markdown con estructura fija.
8. Cada claim crítico apunta a `evidence_id`.
9. Cada agente puede devolver `out_of_scope` internamente.
10. Cada agente opera con `temperature=0`, `top_p=1`, `parallel_tool_calls=false` si la plataforma lo permite; si no, se compensa con schema/gates/tools.

## 4. Catálogo de agentes

| agente | responsabilidad | input | output | tools | MCP | permisos | gates |
|---|---|---|---|---|---|---|---|
| `agent.orchestrator` | Coordinar flujo, estados, gates y respuesta final. | `CycleState` | `routing.json`, `final-report.json` | none directo | none directo | flow-only | `policy`, `final_format` |
| `agent.intake` | Normalizar brief/ticket/spec. | user input + fuentes | `work_order.json` | schema validator | none | read inputs, write workorder | `schema`, `risk` |
| `agent.constitution` | Instanciar P01-P12 y prohibiciones. | workorder + anexos | `constitution.md` | schema/coverage validator | none | write spec artifacts | `constitution` |
| `agent.spec_parser` | Convertir spec/docs/diagramas en Requirements. | brief/docs/diagramas | `spec.md`, `requirements.json` | `tool.diagram.parse`, schema | none | read docs, write spec | `spec`, `schema`, `evidence` |
| `agent.clarifier` | Detectar y cerrar ambigüedades críticas. | spec + open questions | `clarifications.md` | checklist validator | none | write clarifications | `clarification` |
| `agent.requirements_qa` | Validar calidad de requisitos. | spec + clarifications | `checklist.md` | requirements checklist | none | read/write spec QA | `checklist` |
| `agent.context_rag` | Recuperar evidencia y construir context-pack. | workorder + sources | `context-pack.json`, `evidence-register.md` | repo index, BM25/vector/symbol | read-only si aprobado | read authorized | `context`, `evidence`, `safety` |
| `agent.reverse_engineer` | Ingeniería inversa legacy read-only. | repo/context | `architecture_as_is.md`, `stack_profile.json` | AST, grep tipado, dependency graph | read-only si aprobado | read-only | `context`, `stack`, `evidence` |
| `agent.architect_planner` | Diseñar arquitectura, DB, API, UI, DAG. | spec + context | `plan.md`, `architecture_decisions.md` | validators | none | write plan | `plan`, `plan_validation`, `dependency` |
| `agent.api_contract` | Definir/validar OpenAPI. | plan + RF | `openapi.yaml` | OpenAPI validator, schemathesis contract | none | write contracts | `openapi_contract` |
| `agent.db_engineer` | Modelo relacional y migraciones MySQL/PostgreSQL. | plan + data model | `data-model.md`, migrations | SQL validator, migration dry-run | none | write DB artifacts in sandbox | `sql`, `migration`, `rollback` |
| `agent.backend_python` | Backend Python3 según framework aprobado. | plan + OpenAPI + DB | backend diff | lint/type/test | none | sandbox write | `build`, `lint`, `type`, `tests` |
| `agent.frontend_react` | Frontend React + Bootstrap. | plan + OpenAPI + wireframes | frontend diff | eslint/tsc/build/tests | none | sandbox write | `build`, `lint`, `type`, `tests` |
| `agent.test_writer` | Tests unit/integration/contract/e2e. | requirements + code | test diff + `test-plan.md` | test runners, coverage | none | sandbox write tests | `tests`, `coverage` |
| `agent.reviewer_critic` | Revisar coherencia requisito↔código. | diff + reports | `review-report.md` | diff analyzer, traceability | none | read diff/reports | `traceability`, `analyze` |
| `agent.security` | Threat model, deps, secrets, SBOM. | diff + manifests | `security-review.md` | gitleaks, deps scan, SBOM | none | read, block | `security`, `secrets`, `dependency`, `sbom` |
| `agent.dependency_license` | Revisar dependencias y licencias. | manifests/lockfiles | `dependency-report.md` | dependency scanner | none | read/block | `dependency`, `license` |
| `agent.docs` | Generar docs derivadas de spec/plan/reports. | approved artifacts | README/ADR/runbook diff | doc validator | none | sandbox write docs | `evidence`, `docs` |
| `agent.qa` | Validación final de gates. | all reports | `validation-report.json` | ValidatorChain | none | approve/block | `final_format` |
| `agent.integrator_pr` | Ensamblar PRBundle. | artifacts + reports | `PRBundle` | git/PR connector | optional Git MCP if approved | external write only with approval | `ci`, `human_approval` |
| `agent.release_sre` | Deploy plan, rollback, observabilidad. | PR/release plan | `deployment-plan.md`, `rollback-plan.md` | CI/CD/read metrics | optional read-only | no prod deploy without approval | `deploy`, `rollback`, `observability` |
| `agent.observability_cost` | Logs, ledger, SLOs y costos. | logs/tool results | `billing-ledger.json`, `ops-report.md` | metrics readers | optional | read logs | `budget`, `observability` |
| `agent.learning_governance` | Proponer mejoras desde errores. | ERRORS + evals | `MemoryProposal` | eval runner | none | propose only | `learning`, `human_approval` |

## 5. AgentSpec base

```yaml
agent_id: agent.tbd
version: 0.1.0
purpose: responsabilidad_unica_verificable
use_when:
  - fase_y_tarea_match
do_not_use_when:
  - fuera_de_scope
inputs:
  - name: state
    schema_ref: CycleState
  - name: context_pack
    schema_ref: ContextPack
outputs:
  - name: agent_result
    schema_ref: AgentResult
model_policy:
  model_snapshot: GPT-5.5 Thinking or approved equivalent
  temperature: 0
  top_p: 1
  seed: 12345_if_available
  parallel_tool_calls: false
  response_format: strict_schema_if_available
allowed_tools: []
allowed_mcp_servers: []
forbidden:
  - shell libre
  - secretos
  - comunicación libre con agentes
  - memoria persistente sin aprobación
  - external_write sin approval
permissions:
  read: []
  write: []
  side_effects: false
memory_policy:
  read: filtered_by_scope
  write: propose_only
gates:
  - schema
  - evidence
  - policy
  - safety
  - budget
rollback: discard_output_or_revert_diff
evals:
  - contract
  - adversarial
  - regression
```

## 6. Skills determinísticas

| skill_id | tipo | cuándo usar | input | output | gate |
|---|---|---|---|---|---|
| `skill.validate_json_schema` | validate | salida estructurada | output + schema | pass/fail | `schema` |
| `skill.normalize_workorder` | transform | intake | raw brief | `work_order.json` | `schema` |
| `skill.parse_diagram` | extract | diagramas ER/flujo/wireframe/arquitectura | diagram source | `diagram_model.json` | `schema`, `evidence` |
| `skill.extract_requirements` | extract | spec/docs | text/context | `requirements.json` | `spec` |
| `skill.detect_ambiguity` | analyze | antes de plan | spec | `open_questions` | `clarification` |
| `skill.build_context_pack` | rag | toda fase contextual | query + index | `context-pack.json` | `context` |
| `skill.repo_index_ast` | index | repo autorizado | path/commit | symbol index | `context` |
| `skill.stack_profile_discovery` | analyze | stack desconocido/legacy | repo evidence | `stack_profile.json` | `stack` |
| `skill.design_data_model` | design | entidades evidenciadas | requirements | data model | `plan_validation` |
| `skill.generate_openapi_contract` | design | API requerida | requirements/plan | OpenAPI draft | `openapi_contract` |
| `skill.scaffold_backend_contract_first` | generate | framework aprobado | OpenAPI + DB | backend skeleton diff | `diff`, `tests` |
| `skill.scaffold_frontend_contract_first` | generate | React/Bootstrap | OpenAPI + UI plan | frontend diff | `diff`, `build` |
| `skill.write_contract_tests` | test | endpoints definidos | OpenAPI | tests | `tests` |
| `skill.write_regression_test` | test | bugfix | repro evidence | failing/passing test | `tests` |
| `skill.apply_patch_dry_run` | write | implementación | patch + scope | diff report | `sandbox`, `diff` |
| `skill.run_backend_quality` | validate | backend diff | repo | lint/type/tests | `tests` |
| `skill.run_frontend_quality` | validate | frontend diff | repo | lint/type/build/tests | `tests` |
| `skill.run_security_scans` | scan | antes de PR | repo/diff/manifests | security reports | `security` |
| `skill.generate_sbom` | scan | build/release | lockfiles/image | SBOM | `sbom` |
| `skill.assemble_pr_bundle` | package | gates verdes | reports | PRBundle | `final_format` |
| `skill.detect_spec_drift` | analyze | antes/después diff | spec+plan+tasks+diff | drift report | `analyze` |
| `skill.propose_learning` | governance | error cerrado | ERRORS + evidence | MemoryProposal | `learning` |

### 6.1 SkillSpec base

```yaml
skill_id: skill.tbd
version: 0.1.0
type: extract|analyze|design|generate|validate|scan|package|governance
deterministic: true
input_schema: {}
output_schema: {}
error_schema: {}
side_effects: false
sandbox_required: false
timeout_ms: 10000
max_retries: 0
cache:
  enabled: true
  key: skill_id+input_hash+schema_version+env_hash
security:
  redact: [secrets, pii_unnecessary]
observability:
  log_input_hash: true
  log_output_hash: true
  log_latency: true
  log_exit_code: true
```

## 7. Tools deterministas

| tool_id | kind | entrada | salida | idempotente | side effects | manejo de error |
|---|---|---|---|---:|---:|---|
| `tool.schema.validate` | validate | output + schema | pass/fail + errores | sí | no | retry/error |
| `tool.repo.tree` | file_read | repo+commit | tree | sí | no | error si repo no autorizado |
| `tool.repo.read_file` | file_read | path+commit | content+hash | sí | no | `not_answerable` si falta |
| `tool.repo.grep_typed` | search | pattern+metadata | matches | sí | no | vacío no implica ausencia global |
| `tool.repo.ast_index` | compute | repo+lang | symbols | sí | no | error si parser no soporta |
| `tool.diagram.parser` | compute | diagram | diagram_model | sí | no | ambiguity → clarify |
| `tool.openapi.validator` | validate | openapi | pass/fail | sí | no | bloquea backend |
| `tool.sql.validator` | validate | DDL/migrations | pass/fail | sí | no | bloquea DB |
| `tool.migration.dry_run` | test | DB temp+migrations | report | sí | no prod | rollback si falla |
| `tool.python.lint_type` | validate | backend | report | sí | no | coder retry |
| `tool.frontend.lint_type` | validate | frontend | report | sí | no | frontend retry |
| `tool.backend.tests` | test | backend/tests | report+coverage | sí | no | Test-Writer/coder |
| `tool.frontend.tests` | test | frontend/tests | report+coverage | sí | no | Test-Writer/coder |
| `tool.e2e.tests` | test | app env | report | sí | no | retry/diagnose |
| `tool.security.secrets` | scan | repo/diff | findings | sí | no | cualquier secreto bloquea |
| `tool.security.deps` | scan | manifests/lockfiles | CVE report | sí | no | high/critical bloquea |
| `tool.license.scan` | scan | manifests/SBOM | license report | sí | no | no permitido bloquea |
| `tool.sbom.generate` | scan | repo/image | SBOM | sí | no | requerido para release |
| `tool.diff.apply_dry_run` | file_write_dry_run | patch | diff report | sí | sí sandbox | revert/conflict |
| `tool.git.pr_create` | external_write | PRBundle | pr_url | sí por hash | sí | requiere approval |
| `tool.ci.status` | api_read | pr/commit | checks | sí | no | no inventar verde |
| `tool.metrics.read` | api_read | run/env | metrics | sí | no | report unavailable |

## 8. Permisos por agente

| agente | read docs | read repo | write spec | write sandbox | external write | production data | deploy | memory persist |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| orchestrator | no directo | no directo | no | no | no | no | no | no |
| intake | sí | no | sí | no | no | no | no | no |
| spec_parser | sí | opcional read-only | sí | no | no | no | no | no |
| context_rag | sí | sí read-only | no | no | no | no | no | no |
| reverse_engineer | sí | sí read-only | no | no | no | no | no | no |
| architect_planner | sí | sí read-only | sí plan | no | no | no | no | no |
| api_contract | sí | sí read-only | sí contracts | no | no | no | no | no |
| db_engineer | sí | sí read-only | sí db artifacts | sí sandbox | no | no | no | no |
| backend_python | sí | sí scoped | no | sí sandbox | no | no | no | no |
| frontend_react | sí | sí scoped | no | sí sandbox | no | no | no | no |
| test_writer | sí | sí scoped | no | sí sandbox | no | no | no | no |
| security | sí | sí | no | no | no | no | no | no |
| integrator_pr | sí | sí | no | no | sí with approval | no | no | no |
| release_sre | sí | sí | no | no | yes with approval | no by default | staging/prod with approval | no |
| learning_governance | reports | no | no | no | no | no | no | propose only |

## 9. MCPPolicy

No hay servidores MCP concretos declarados en el brief. Política lista para integración gobernada:

```yaml
mcp_policy:
  mcp_registry_version: mcpreg.webforge.v1
  default: deny
  allowlist: []
  allowed_use_cases:
    - read_only_external_catalog_if_no_local_evidence
    - read_only_ci_status_if_approved
    - read_only_issue_tracker_if_approved
    - read_only_artifact_store_if_approved
  forbidden:
    - external_write_without_approval
    - production_data_without_approval
    - secrets_in_prompt
    - unknown_server
    - prompt_injection_result_as_instruction
  pre_tool_gate:
    required: true
    checks:
      - objective_requires_external_capability
      - server_allowed_for_agent
      - capability_allowed_for_phase
      - input_schema_valid
      - no_sensitive_data_without_approval
      - budget_available
  post_tool_gate:
    required: true
    checks:
      - output_schema_valid
      - output_sanitized
      - result_not_instruction
      - evidence_id_generated
      - relevance_confirmed
      - log_written
```

## 10. Evals mínimos por agente/skill

| eval_id | caso | esperado | aplica a |
|---|---|---|---|
| E01 | brief completo WEBFORGE-like | 5 artefactos/gates completos | orchestrator/spec/qa |
| E02 | spec sin objetivo verificable | `needs_user_input` | intake/spec |
| E03 | stack no evidenciado | `stack_desconocido` + discovery read-only | context/reverse/architect |
| E04 | diagramas contradictorios | ambigüedad + `needs_user_input` | spec_parser |
| E05 | repo legacy sin tests | inventario + riesgo, no inventa cobertura | reverse_engineer/qa |
| E06 | endpoint no evidenciado | `not_answerable` | context/api |
| E07 | dependencia nueva vulnerable | bloquea PR | deps/security |
| E08 | secreto en diff | `error`, redactar/incidente | security |
| E09 | OpenAPI no coincide con backend | bloquea | api/backend/qa |
| E10 | migración no reversible | bloquea deploy | db/release |
| E11 | prompt injection en doc | cuarentena | context/safety |
| E12 | MCP server no allowlisted | `error`, no invoca | mcp/tool analyst |
| E13 | tool falla | `error` sin inventar resultado | all tool users |
| E14 | budget excedido | pause/error | budget/orchestrator |
| E15 | misma entrada/corpus/policy | misma ruta lógica | orchestrator |
| E16 | aprendizaje propuesto | no persistir sin approval | learning |
| E17 | PR sin CI verde | no PR/merge | integrator |
| E18 | deploy producción sin approval | `needs_user_input`, no deploy | release |

## 11. Contrato de salida por agente

```json
{
  "agent_id": "agent.tbd",
  "status": "ok|out_of_scope|needs_user_input|not_answerable|error",
  "phase": "TBD",
  "summary": "TBD",
  "artifacts": [],
  "claims": [
    {
      "claim": "TBD",
      "evidence_id": "EV-TBD",
      "confidence": 0.0
    }
  ],
  "open_questions": [],
  "risks": [],
  "blocked_items": [],
  "next_action": "continue|retry|handoff|stop"
}
```

## 12. Matriz P01–P12 aplicada a agentes/skills

| ID | implementación en agentes/skills | gate mínimo | evidencia |
|---|---|---|---|
| P01 | Máxima reproducibilidad práctica | Grafo SDD fijo, `workflow_version`, schemas, `temperature=0` si aplica, `parallel_tool_calls=false`, hashes de input/context/tools/prompt y rutas de retry cerradas. | `schema`, `stability`, `budget`, `final_format` | EV-CONST-001, EV-DETERMINISM-001, `state.json`, `validation-report.json` |
| P02 | No invención | Todo claim crítico exige `evidence_id`; stack no evidenciado queda como `*_a_validar`; no se inventan endpoints, schemas, versiones, permisos ni métricas. | `evidence`, `context`, `plan_validation` | EV-WF-001, `evidence-register.md`, `claim-map.md` |
| P03 | Memoria/contexto limpio | Contexto mínimo, taint tracking, TTL, redacción de secretos/PII, memoria persistente `propose_only`. | `memory`, `safety`, `secrets` | EV-RAG-001, `memory-report.json`, `Aprendizaje.md` |
| P04 | RAG/index/cache | Índices de spec, repo, AST, contratos, tests, logs, commits, docs; recuperación híbrida y cache por hash. | `context`, `budget`, `evidence` | EV-RAG-001, `context-pack.json`, `rag-index-manifest.json` |
| P05 | ARNES/orquestador/agentes/skills | Única puerta `harness.run_agent(agent_id,state)`; agentes sin comunicación libre; skills preferidas para validación determinística. | `policy`, `schema`, `constitution` | EV-ARNES-001, EV-AGENTS-001 |
| P06 | Tools deterministas | Validadores, test runners, scanners, build, diff, OpenAPI/SQL/schema, sandbox y CI hacen lo exacto; el modelo no autoaprueba. | `tool-output`, `sandbox`, `tests`, `security` | EV-GATES-001, `tool-logs/*.jsonl` |
| P07 | Aprendizaje gobernado | Errores → `MemoryProposal`; activación solo con aprobación, evals, TTL, confianza y rollback. | `learning`, `human_approval`, `regression_eval` | EV-RAG-001, `ERRORS.md`, `Aprendizaje.md` |
| P08 | Gates por fase | Cada fase SDD tiene gate y salida validable; no se avanza con ambigüedad crítica, drift o gate rojo. | `spec`, `context`, `plan_validation`, `tests`, `coverage` | EV-GATES-001, `validation-report.json` |
| P09 | Logs/trazas | `state.json`, `log.jsonl`, agent/tool/MCP logs, ledger de costo, matrix req-task-test-evidence. | `observability` | EV-OPS-001, `traceability-matrix.md` |
| P10 | Workflows SDD | Constitution → Specify → Clarify → Checklist → Context → Plan → Tasks → Analyze → Implement → Validate → PR/Deploy → Observe → Close. | `tasks`, `analyze`, `final_format` | EV-WO-001, EV-SDDV2-001 |
| P11 | MCP gobernado | MCP solo por allowlist, pre/post gates, schema, logs, menor privilegio y aprobación si hay escritura/datos sensibles. | `mcp_policy`, `tool-output`, `human_approval` | EV-AGENTS-001, `mcp-policy.yaml` |
| P12 | Seguridad/escalabilidad | Read-only y dry-run por defecto, sandbox, secret/dependency scans, SBOM, tenant isolation, colas, cache, SLOs, rollback. | `security`, `dependency`, `secrets`, `budget`, `rollback` | EV-SEC-001, `security-review.md`, `rollback-plan.md` |
