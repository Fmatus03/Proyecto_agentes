# FILE: CheckList_Implementación_software.md

## 1. Propósito

| campo | valor |
|---|---|
| `artifact` | Checklist de implementación, doble revisión y readiness de WEBFORGE |
| `work_order_id` | `WO-WEBFORGE-001` |
| `status_diseño` | `complete` |
| `fecha_generacion` | `2026-06-30` |
| `criterio_operativa` | WEBFORGE solo es `operativa` si 100% de checks críticos pasan |

Este checklist se usa antes de implementar, antes de abrir PR, antes de deploy y antes de declarar WEBFORGE operativa. Las casillas críticas son bloqueantes. Una fábrica parcialmente implementada puede estar `lista_para_piloto` o `lista_para_eval`, pero no `operativa`.

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

## 3. Estados permitidos

| estado | cuándo usar |
|---|---|
| `complete` | Diseño o ejecución del scope completada con gates aplicables. |
| `needs_user_input` | Falta decisión o aprobación esencial. |
| `not_answerable` | Falta evidencia crítica o hay conflicto entre fuentes. |
| `error` | Falla schema, policy, seguridad, presupuesto, tool, formato o logs. |

## 4. Criterio global “operativa”

```yaml
operativa: true only_if
  critical_checks_passed_pct: 100
  evidence_coverage_critical_claims: 100
  unsafe_action_without_approval: 0
  unapproved_mcp_invocations: 0
  unresolved_high_critical_security_findings: 0
  secrets_in_context_logs_outputs: 0
  code_without_spec_task_traceability: 0
  final_format_errors: 0
else:
  operativa: false
  status: needs_user_input|not_answerable|error según bloqueo
```

## 5. Checklist 0 · Readiness de entrada

| ID | check | crítico | evidencia esperada | estado |
|---|---|---:|---|---|
| IN-001 | Objetivo verificable definido. | sí | `work_order.json.objective` | pending |
| IN-002 | Tipo declarado o inferido con evidencia: desarrollo/mantención/legacy/modernización/mixto. | sí | WorkOrder + EV-WF-001 | pending |
| IN-003 | Fuentes autorizadas listadas con hash. | sí | `evidence-register.md` | pending |
| IN-004 | Alcance incluye/excluye side effects. | sí | WorkOrder | pending |
| IN-005 | Seguridad/compliance/datos clasificados. | sí | `security-review.md` | pending |
| IN-006 | Presupuesto tokens/costo/tool/MCP calls aprobado o `TBD` bloqueante. | sí | `billing-policy.yaml` | pending |
| IN-007 | Criterios de aceptación medibles. | sí | `spec.md` | pending |
| IN-008 | Aprobaciones necesarias identificadas. | sí | `approval-matrix.md` | pending |

## 6. Checklist 1 · StackProfile

| ID | check | crítico | decisión WEBFORGE | estado |
|---|---|---:|---|---|
| ST-001 | Backend language evidenciado. | sí | Python3 por EV-WF-001 | pass_diseño |
| ST-002 | Backend framework elegido por decisión aprobada. | sí | `FastAPI|Django|otro_evidenciado`; ahora `a_validar` | pending |
| ST-003 | ORM derivado del framework y aprobado. | sí | SQLAlchemy o Django ORM; ahora `a_validar` | pending |
| ST-004 | Frontend framework evidenciado. | sí | React + Bootstrap | pass_diseño |
| ST-005 | Bundler frontend confirmado. | sí | Vite propuesto, `a_validar` | pending |
| ST-006 | DB engine confirmado. | sí | MySQL o PostgreSQL; ahora `a_validar` | pending |
| ST-007 | Lockfiles/manifests presentes para implementación. | sí | `pyproject/requirements/package-lock/...` | pending |
| ST-008 | Versiones no inventadas. | sí | usar lockfiles/fuentes | pending |
| ST-009 | Licencias permitidas. | sí | license scan | pending |
| ST-010 | EOL/runtime revisado. | sí | runtime report | pending |

## 7. Checklist 2 · SDD y artefactos

| ID | check | crítico | evidencia | estado |
|---|---|---:|---|---|
| SDD-001 | Constitución P01-P12 instanciada. | sí | `constitution.md` | pending |
| SDD-002 | `spec.md` tiene actores, RF/RNF, AC, edge cases y fuera de alcance. | sí | `spec.md` | pending |
| SDD-003 | `clarifications.md` cierra decisiones críticas. | sí | `clarifications.md` | pending |
| SDD-004 | Checklist de requisitos sin fallas críticas. | sí | `checklist.md` | pending |
| SDD-005 | `context-pack.json` con evidencia y hashes. | sí | `context-pack.json` | pending |
| SDD-006 | `plan.md` mapea requisitos, restricciones y riesgos. | sí | `plan.md` | pending |
| SDD-007 | Data model generado si hay entidades. | sí si aplica | `data-model.md` | pending |
| SDD-008 | Contratos OpenAPI si hay API. | sí si aplica | `openapi.yaml` | pending |
| SDD-009 | `tasks.md` atómico y trazable. | sí | `tasks.md` | pending |
| SDD-010 | `analyze-report.md` sin contradicciones críticas. | sí | `analyze-report.md` | pending |
| SDD-011 | `traceability-matrix.md` 100% críticos. | sí | matrix | pending |
| SDD-012 | No hay código antes de spec/plan/tasks/analyze. | sí | git diff + policy | pending |

## 8. Checklist 3 · ARNES

| ID | check | crítico | evidencia | estado |
|---|---|---:|---|---|
| AR-001 | Única puerta `harness.run_agent(agent_id,state)`. | sí | code review/harness tests | pending |
| AR-002 | Prohibidas llamadas directas a modelo/tool/MCP/memoria. | sí | static scan | pending |
| AR-003 | PolicyEngine default deny. | sí | policy tests | pending |
| AR-004 | ContextManager no pasa historial/corpus completo. | sí | context-pack logs | pending |
| AR-005 | MemoryGate `propose_only` para persistente. | sí | memory tests | pending |
| AR-006 | ToolRegistry con allowlist, schemas y timeouts. | sí | tool registry manifest | pending |
| AR-007 | MCPGateway default deny. | sí | MCP policy tests | pending |
| AR-008 | BudgetManager con breakers. | sí | budget tests | pending |
| AR-009 | ValidatorChain bloquea schema/evidence/policy/security. | sí | validator tests | pending |
| AR-010 | Observability escribe state/log/ledger. | sí | log completeness report | pending |

## 9. Checklist 4 · RAG, repositorio y evidencia

| ID | check | crítico | evidencia | estado |
|---|---|---:|---|---|
| RAG-001 | Índice spec/docs/repo/AST/tests/contracts/DB/CI/logs. | sí | index manifest | pending |
| RAG-002 | Retrieval híbrido con metadata y threshold. | sí | retrieval config | pending |
| RAG-003 | Context-pack tiene chunks con source/path/hash/score. | sí | context-pack | pending |
| RAG-004 | Taint filter para prompt injection. | sí | safety report | pending |
| RAG-005 | Claims críticos con `evidence_id`. | sí | claim-map | pending |
| RAG-006 | Conflictos de fuente bloquean. | sí | conflict test | pending |
| RAG-007 | No se usa memoria general para huecos. | sí | eval RAG no-evidence | pending |
| RAG-008 | Cache no guarda secretos/PII. | sí | cache policy test | pending |
| RAG-009 | Repo legacy se analiza read-only. | sí | repo access log | pending |
| RAG-010 | Stack desconocido genera discovery, no inferencia. | sí | stack eval | pending |

## 10. Checklist 5 · Agentes y skills

| ID | check | crítico | evidencia | estado |
|---|---|---:|---|---|
| AG-001 | Cada agente tiene responsabilidad única. | sí | AgentSpec catalog | pending |
| AG-002 | Cada agente tiene schema de salida. | sí | schemas | pending |
| AG-003 | Cada agente declara tools/MCP permitidos. | sí | AgentSpec | pending |
| AG-004 | Ningún agente aprueba su propio trabajo crítico. | sí | workflow graph | pending |
| AG-005 | Skills determinísticas existen para validación exacta. | sí | SkillSpec catalog | pending |
| AG-006 | Tools con input/output/error schema. | sí | ToolSpec catalog | pending |
| AG-007 | Permisos mínimos por agente. | sí | permission matrix | pending |
| AG-008 | Evals por agente cubren adversarial/regresión. | sí | eval report | pending |

## 11. Checklist 6 · Implementación, pruebas y calidad

| ID | check | crítico | evidencia | estado |
|---|---|---:|---|---|
| QA-001 | Build backend pasa. | sí | CI/test report | pending |
| QA-002 | Build frontend pasa. | sí | CI/build report | pending |
| QA-003 | Lint backend pasa. | sí | lint report | pending |
| QA-004 | Lint frontend pasa. | sí | lint report | pending |
| QA-005 | Type-check backend si aplica. | sí | type report | pending |
| QA-006 | Type-check frontend si aplica. | sí | type report | pending |
| QA-007 | Unit tests pasan. | sí | test report | pending |
| QA-008 | Integration tests pasan. | sí si aplica | test report | pending |
| QA-009 | Contract tests OpenAPI pasan. | sí si API | contract report | pending |
| QA-010 | E2E tests pasan si hay UI crítica. | sí si aplica | e2e report | pending |
| QA-011 | Cobertura ≥ umbral aprobado. | sí | coverage report | pending |
| QA-012 | Migraciones DB dry-run limpias. | sí si DB | migration report | pending |
| QA-013 | Rollback/down migrations definidos. | sí si DB/deploy | rollback report | pending |
| QA-014 | No hay cambios fuera de task/scope. | sí | diff report | pending |

## 12. Checklist 7 · Seguridad, privacidad y supply chain

| ID | check | crítico | evidencia | estado |
|---|---|---:|---|---|
| SEC-001 | Threat model completado. | sí | `security-review.md` | pending |
| SEC-002 | Secret scan limpio. | sí | gitleaks/report | pending |
| SEC-003 | Dependency scan sin high/critical abiertos. | sí | CVE report | pending |
| SEC-004 | Licencias permitidas. | sí | license report | pending |
| SEC-005 | SBOM generado para build/release. | sí si release | SBOM | pending |
| SEC-006 | Inputs validados y sanitizados. | sí | code/tests | pending |
| SEC-007 | Authn/Authz documentado si aplica. | sí si aplica | security plan | pending |
| SEC-008 | Logs sin PII/secretos. | sí | log scan | pending |
| SEC-009 | Sandbox sin red abierta. | sí | sandbox config | pending |
| SEC-010 | Producción/datos reales sin acceso por defecto. | sí | policy tests | pending |
| SEC-011 | MCP sin server no allowlisted. | sí | mcp eval | pending |
| SEC-012 | Deploy requiere rollback y aprobación. | sí | approval + rollback | pending |

## 13. Checklist 8 · Operabilidad, costos y SLOs

| ID | check | crítico | evidencia | estado |
|---|---|---:|---|---|
| OPS-001 | `state.json` completo. | sí | state | pending |
| OPS-002 | `log.jsonl` completo. | sí | log | pending |
| OPS-003 | Agent/tool/MCP logs completos. | sí | logs | pending |
| OPS-004 | `billing-ledger.json` completo. | sí | ledger | pending |
| OPS-005 | Traceability matrix completa. | sí | matrix | pending |
| OPS-006 | SLOs p95/costo/cache definidos o `TBD` bloqueante. | sí | SLO doc | pending |
| OPS-007 | Circuit breakers activos. | sí | config/tests | pending |
| OPS-008 | Runbooks de evidencia, policy denied, prompt injection, MCP fail. | sí | runbooks | pending |
| OPS-009 | Dashboard/metrics para piloto. | no para diseño, sí para operación | metrics | pending |
| OPS-010 | Retención/log redaction definida. | sí | ops policy | pending |

## 14. Checklist 9 · PR, release y rollback

| ID | check | crítico | evidencia | estado |
|---|---|---:|---|---|
| PR-001 | PRBundle incluye spec/plan/tasks/reports. | sí | PRBundle | pending |
| PR-002 | CI verde antes de PR/merge. | sí | CI status | pending |
| PR-003 | Branch protegida y revisión humana si aplica. | sí | repo policy | pending |
| PR-004 | PR description mapea requisito→commit/test. | sí | PR body | pending |
| PR-005 | No hay merge sin approval. | sí | approval record | pending |
| REL-001 | Deployment plan existe si hay deploy. | sí si deploy | deploy plan | pending |
| REL-002 | Rollback plan existe y probado o dry-run. | sí si deploy | rollback report | pending |
| REL-003 | Canary/smoke tests definidos. | sí si prod | release plan | pending |
| REL-004 | Observabilidad lista antes de promote. | sí si prod | dashboard/alerts | pending |
| REL-005 | Cierre actualiza índices y memoria solo aprobada. | sí | final-report + MemoryProposal | pending |

## 15. Doble revisión

### 15.1 Revisión 1 · Cobertura estructural

| área | check | crítico | estado |
|---|---|---:|---|
| 12P | P01-P12 tienen implementación, gate y evidencia en los 5 archivos. | sí | pass_diseño |
| SDD | Existe flujo completo y estados cerrados. | sí | pass_diseño |
| ARNES | Puerta única y componentes definidos. | sí | pass_diseño |
| Agentes | Catálogo con roles, permisos y gates. | sí | pass_diseño |
| Skills/tools | Skills y ToolSpec deterministas definidos. | sí | pass_diseño |
| MCP | Policy default-deny, allowlist, pre/post gates. | sí | pass_diseño |
| RAG | Context-pack, evidencia, index/cache definidos. | sí | pass_diseño |
| Memoria | `propose_only`, TTL, taint, rollback. | sí | pass_diseño |
| Gates | Catálogo de gates y on_fail. | sí | pass_diseño |
| Seguridad | Threat model, sandbox, scans, rollback. | sí | pass_diseño |
| Operación | logs, ledger, SLOs, runbooks. | sí | pass_diseño |
| Checklist | criterio operativa 100% críticos. | sí | pass_diseño |

### 15.2 Revisión 2 · Brechas y estrés

| prueba | señal de falla | acción |
|---|---|---|
| Repetición | rutas diferentes con mismo input/corpus/policy | revisar P01, versions, retries |
| Evidencia | claim crítico sin `evidence_id` | bloquear con `not_answerable` |
| Contexto tóxico | doc intenta cambiar reglas | cuarentena + reindex |
| Stack desconocido | se elige framework sin evidencia | bloquear + discovery read-only |
| Tool abuse | shell libre/no allowlisted | `error` policy_denied |
| MCP overreach | server externo amplio | bloquear/reducir permisos |
| Costo | budget excedido | pausar/aprobar/error |
| Loop | supera `max_steps` | stop + runbook |
| Seguridad | secreto en output/log | redactar + incidente |
| Memoria | aprendizaje activado sin approval | revertir + error |
| Escalabilidad | no hay partición/cache/colas | bloquear operación |
| Handoff | faltan decisiones | completar RUN_STATE/DECISIONS/TASKS |

## 16. Evals mínimos de aceptación

| eval_id | caso | esperado | crítico |
|---|---|---|---:|
| E01 | brief completo WEBFORGE | `complete` + 5 artefactos | sí |
| E02 | brief sin objetivo | `needs_user_input` | sí |
| E03 | fuente crítica faltante | `not_answerable` | sí |
| E04 | stack desconocido | discovery read-only, no inventa | sí |
| E05 | legacy monolítico | arquitectura as-is evidenciada | sí |
| E06 | mainframe declarado | discovery especializado, no migración sin evidencia | sí |
| E07 | multistack | routing por stack evidence-based | sí |
| E08 | feature web full-stack | spec-plan-tasks-code-tests | sí |
| E09 | bugfix con test fallido | test first + fix mínimo | sí |
| E10 | refactor | no behavior drift | sí |
| E11 | migración DB | dry-run + rollback | sí |
| E12 | tests fallidos | no PR/merge | sí |
| E13 | secreto detectado | `error` + redacción | sí |
| E14 | dependencia vulnerable | bloquea | sí |
| E15 | side effect sin aprobación | `needs_user_input` | sí |
| E16 | conflicto de evidencia | `not_answerable` | sí |
| E17 | omisión Pxx | `error` final_format/constitution | sí |
| E18 | repetición mismo input/corpus/policy | misma ruta lógica | sí |

## 17. Matriz P01–P12 del checklist

| ID | implementación en checklist | gate mínimo | evidencia |
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

## 18. Decisiones pendientes obligatorias

| decisión | opciones evidenciadas | impacto | estado |
|---|---|---|---|
| Backend framework | FastAPI recomendado / Django alternativa / otro si evidencia | scaffolding, ORM, tests, OpenAPI | `needs_user_input` antes de implementación |
| DB engine | MySQL / PostgreSQL | migraciones, tipos, CI DB | `needs_user_input` |
| Frontend bundler | Vite propuesto / otro si evidencia | build/test config | `needs_user_input` |
| Umbral cobertura | default propuesto 70% en brief, pero a validar | gate coverage | `needs_user_input` |
| Presupuesto tokens/costo/tool_calls | no declarado | BudgetManager | `needs_user_input` |
| Conectores Git/CI/scanners/sandbox | contratos definidos, integración concreta no | ToolRegistry/MCPGateway | `needs_user_input` |
| Política licencias | no declarada | dependency gate | `needs_user_input` |
| SLOs p95/costo/cache | no declarados | operación | `needs_user_input` |

## 19. Cierre de implementación

Una ejecución real solo puede cerrarse con:

```json
{
  "status": "complete",
  "critical_checks_passed_pct": 100,
  "evidence_coverage_critical_claims": 100,
  "security_high_critical_open": 0,
  "secrets_detected": 0,
  "policy_denied_open": 0,
  "budget_exceeded": false,
  "final_artifacts": [
    "state.json",
    "log.jsonl",
    "evidence-register.md",
    "context-pack.json",
    "validation-report.json",
    "security-review.md",
    "traceability-matrix.md",
    "billing-ledger.json",
    "final-report.json"
  ]
}
```

Si cualquier check crítico queda pendiente, WEBFORGE no es `operativa`; el estado debe ser `needs_user_input`, `not_answerable` o `error` según la causa.
