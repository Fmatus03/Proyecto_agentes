# Manual técnico completo de la fábrica WEBFORGE

Fecha de corte: 2026-07-05  
Repositorio documentado: `Nueva Fabrica Software Web`  
Estado observado: runtime local ejecutable con corrida BrewMaster reciente en `runs/brewmaster-latest`.

Este manual documenta la fábrica tal como está implementada hoy. No describe una arquitectura ideal ni una promesa futura. Cuando el código, los artefactos o la auditoría muestran una brecha entre lo esperado y lo real, la brecha se declara explícitamente.

## 1. Visión general

WEBFORGE es una fábrica local de desarrollo Spec-Driven Development (SDD) implementada en Python. Su propósito operativo es recibir una orden de trabajo (`WorkOrder`), preparar un workspace de proyecto aislado, ejecutar un workflow fijo de fases, producir artefactos técnicos auditables y cerrar con gates de evidencia, seguridad, trazabilidad y política.

El objetivo actual del runtime no es desplegar una aplicación productiva ni llamar servicios externos. El alcance real es local: escribir artefactos en un directorio de corrida (`runs/...`) y, cuando corresponde, materializar un bundle de implementación dentro del sandbox `DEV` del proyecto bajo `project/<project_id>/sandboxes/DEV/workspace`.

La filosofía de funcionamiento es fail-closed:

- toda ejecución se normaliza como `WorkOrder`;
- las fases son cerradas y ordenadas;
- los agentes declarados pasan por `HarnessRunner.run_agent`;
- los efectos de implementación se restringen al materializador DEV;
- MCP está default-deny;
- las herramientas están allowlisted en `ToolRegistry`;
- la memoria persistente es project-scoped y propose-only;
- el cierre `complete` depende de gates, artefactos y cobertura P01-P12.

Relación con `fabricas_agentes_ia.md`: ese documento es la fuente conceptual de la fábrica agéntica. Define la separación entre modelo, agente y fábrica; el principio "workflows primero, agentes después"; el rol del orquestador; el arnés como frontera; herramientas gobernadas; contexto con evidencia; trazabilidad y estados finales cerrados. WEBFORGE implementa una versión local y determinista de esos conceptos, pero todavía no cumple plenamente la visión madura del documento: los "agentes" son handlers Python deterministas, no especialistas autónomos con ejecución separada, y algunos gates validan presencia o conteos en vez de comportamiento funcional.

Relación con `projects/BrewMaster/brewmaster_especificacion_completa.md`: BrewMaster es el caso canónico de aceptación. La fábrica detecta órdenes BrewMaster y genera un blueprint, contratos, backend, frontend, migraciones, documentación y pruebas desde esa especificación. La corrida actual valida 30 pantallas, 40 endpoints `/api/v1`, 100 validaciones y permisos declarados. Sin embargo, el resultado generado es un scaffold verificable, no una aplicación BrewMaster funcional completa.

## 2. Arquitectura general

La arquitectura se organiza en capas locales:

```text
Usuario / CLI
    |
    v
WorkOrder normalizado
    |
    v
WebForgeFactory.run
    |
    +--> ProjectWorkspace prepara project/<project_id>
    +--> EvidenceRegistry registra fuentes autorizadas
    +--> ContextManager genera context-pack
    +--> PolicyEngine / BudgetManager / MCPGateway / ToolRegistry
    |
    v
HarnessRunner.run_agent por cada fase
    |
    v
Handlers deterministas en FactoryPhaseHandlersMixin
    |
    +--> Artefactos de run en runs/<run>
    +--> Bundle en DEV por DevSandboxMaterializer
    |
    v
Final report + traceability + state
```

Componentes principales:

| Componente | Archivo | Responsabilidad real |
|---|---|---|
| CLI | `webforge/cli.py`, `webforge/__main__.py` | Expone comandos `run`, `principles`, `skills`, `tools`, `doctor`. |
| Orquestador | `webforge/orchestrator.py` | Inicializa corrida, estado, políticas, workspace, herramientas y ejecuta fases. |
| Harness | `webforge/harness.py` | Valida agente allowlisted, prepara input con contexto/memoria/reglas y controla MCP permitido. |
| Workflow | `webforge/workflow.py` | Declara versión, fases, agentes por fase y artefactos requeridos. |
| Fases | `webforge/factory_phases.py` | Implementa los handlers reales de cada fase y sus gates. |
| Soporte de cierre | `webforge/factory_support.py` | Escribe estado, logs, claims, trazabilidad, manifests y final-report. |
| Proyecto | `webforge/project_workspace.py` | Crea proyecto, versión, memoria, aprendizaje, DEV/QA y contratos frontend. |
| Contexto/memoria | `webforge/context.py` | Registra evidencia, genera snippets por sección y memoria propose-only. |
| Política | `webforge/policy.py` | Allowlist de agentes, bloqueo de deploy/escrituras/datos productivos, presupuesto y MCP default-deny. |
| Herramientas | `webforge/tools.py` | Registry allowlisted y herramientas locales deterministas. |
| Materializador | `webforge/isolation.py` | Único camino aprobado para escribir bundles en DEV. |
| Validadores | `webforge/validators.py` | Validaciones de artefactos, MCP, Alembic, rutas y BrewMaster. |
| Principios | `webforge/principles.py` | Catálogo P01-P12, gates y evidencia requerida. |
| Capacidades | `webforge/capabilities.py` | Catálogo de skills internas y validación del paquete `skills/webforge-factory`. |
| BrewMaster | `webforge/brewmaster_*.py` | Parser de spec, blueprint, bundle, backend, frontend, docs y tests generados. |

Relaciones clave:

- `WebForgeFactory` hereda de `FactoryPhaseHandlersMixin` y `FactorySupportMixin`.
- `WORKFLOW_PHASES` define el orden único de ejecución.
- `PHASE_AGENTS` asocia cada fase a un `AgentSpec`.
- `HarnessRunner` llama un handler de fase provisto por el orquestador.
- Las herramientas se ejecutan por `ToolRegistry.run`.
- El bundle de implementación se materializa solo mediante `DevSandboxMaterializer`.
- El estado compartido vive en un `CycleState` serializado a `state.json`.

## 3. Harness

El harness está implementado por `HarnessRunner` y `AgentSpec` en `webforge/harness.py`.

Propósito:

El harness es la puerta de entrada para ejecutar cada agente/fase. Su contrato real es: recibir un `AgentSpec`, revisar que el agente esté permitido por `PolicyEngine`, preparar un `prompt_input` estructurado y ejecutar el handler asociado.

Ciclo de vida:

```text
AgentSpec + CycleState
    |
    v
policy.check_agent(agent_id)
    |
    +-- fail --> PhaseResult error con gate policy
    |
    v
memory.read_filtered(agent_id, phase)
    |
    v
MCP allowed_mcp_servers precheck
    |
    +-- fail --> PhaseResult error con gate mcp_policy
    |
    v
handler(prompt_input)
    |
    v
PhaseResult registrado
```

Responsabilidades reales:

- comprobar que `agent_id` esté en el set de agentes allowlisted;
- entregar un input estructurado con `task_id`, `phase`, `context_pack`, `memory_pack`, `previous_outputs` y reglas;
- forzar reglas declarativas como `no_inventar`, `usar_solo_evidencia`, `mcp_requires_pre_and_post_gate` y `memory_isolation`;
- bloquear MCP no allowlisted;
- registrar invocaciones de agentes en memoria del harness.

Contratos:

- Entrada: `AgentSpec`, `state: dict`, `handler`.
- Salida: `PhaseResult`.
- Error: `PhaseResult(status="error")` con un `GateResult` fallido.

Permisos:

- La política de agentes se aplica en `PolicyEngine.check_agent`.
- Los MCP servers se validan por `MCPGateway.invoke`.
- El estado inicial marca `external_write`, `deploy` y `production_data` como denegados salvo aprobación explícita en `side_effects`.

Trazabilidad:

- El harness devuelve `PhaseResult`; el orquestador lo pasa a `_record_phase`.
- `_record_phase` escribe `log.jsonl`, `phase-ledger.json` y `state.json`.

Relación con el orquestador:

- El orquestador decide el orden y llama `harness.run_agent(PHASE_AGENTS[phase], state, handler)`.
- El harness no decide fases ni cierre final.

Relación con agentes:

- Los agentes declarados no son procesos externos ni modelos vivos.
- Cada agente es una entrada `AgentSpec` y un handler Python en `FactoryPhaseHandlersMixin`.
- El harness prepara el input, pero el trabajo real ocurre dentro del handler.

Puntos de extensión:

- agregar campos a `AgentSpec`;
- fortalecer `run_agent` para validar schemas de salida;
- mover la ejecución de herramientas al harness para hacer cumplir `allowed_tools`;
- agregar pre-tool/post-tool gates reales;
- emitir trazas propias del harness más allá del `PhaseResult`.

Inconsistencia importante:

`AgentSpec.allowed_tools` existe y `workflow.py` declara tools permitidas para `implement`, `validate` y `security`, pero `HarnessRunner` no hace cumplir esa allowlist. Hoy las herramientas se invocan directamente desde los handlers con `self.tools.run(...)`. Esto significa que el permiso mínimo por agente está parcialmente declarado, no plenamente impuesto por el arnés.

## 4. Orquestador

El orquestador principal es `WebForgeFactory` en `webforge/orchestrator.py`.

Cómo funciona:

1. Recibe `work_order_data`, `output_dir` y fuentes opcionales.
2. Limpia artefactos conocidos previos del directorio de salida.
3. Normaliza el `WorkOrder`.
4. Prepara `ProjectWorkspace`.
5. Registra fuentes autorizadas con hashes.
6. Inicializa contexto, memoria, presupuesto, MCP, política, herramientas y harness.
7. Calcula `run_id`.
8. Escribe artefactos base: workflow, políticas MCP, matriz de aprobación, manifests de skills/tools/agentes.
9. Recorre `WORKFLOW_PHASES`.
10. Por cada fase, actualiza `state.phase` y `state.agent_id`, ejecuta el agente por harness y registra resultados.
11. Si una fase falla, marca `state.status = "error"` y detiene la secuencia.
12. Si no falla, marca estado candidato `complete`.
13. Escribe artefactos de cierre, final-report, trazabilidad y estado final.

Qué controla:

- directorio de salida;
- workspace del proyecto;
- selección de fuentes autorizadas;
- estado compartido;
- orden de fases;
- creación de registros y manifests globales;
- cierre de corrida.

Qué no debe hacer según la arquitectura conceptual:

- no debería producir contenido funcional de cada fase;
- no debería ejecutar herramientas directamente;
- no debería mezclar validación, documentación, seguridad y generación en un mismo componente.

Qué hace realmente:

- `WebForgeFactory` mantiene el flujo, pero al heredar mixins queda acoplado a handlers extensos.
- `FactoryPhaseHandlersMixin` concentra generación de especificación, plan, tareas, implementación, validación, seguridad y cierre.
- La arquitectura es operativa, pero todavía monolítica.

Interacción con workflows:

- Usa `WORKFLOW_PHASES` como única ruta.
- Usa `PHASE_AGENTS` como catálogo de agentes por fase.
- Escribe `workflow.yaml` con `workflow_id: wf.webforge.sdd.v1`.

Interacción con agentes:

- Cada fase se ejecuta con `HarnessRunner.run_agent`.
- El handler se selecciona en `_run_phase` por nombre de fase.

## 5. Workflows

Solo existe un workflow operativo: `wf.webforge.sdd.v1`.

Orden de fases:

```text
intake -> constitution -> specify -> clarify -> checklist -> context
-> plan -> tasks -> analyze -> implement -> validate -> security
-> pr_handoff -> deploy_checkpoint -> observe -> close
```

Tabla de fases:

| Fase | Propósito | Entradas | Salidas principales | Gates relevantes |
|---|---|---|---|---|
| `intake` | Normalizar y validar la orden. | `WorkOrder`, workspace, skill package. | `work_order.json`. | `schema`, `budget`, `project_isolation`, `frontend_template`, `factory_skills`. |
| `constitution` | Instanciar P01-P12. | Catálogo de principios. | `constitution.md`, `principle-ledger.json`. | `constitution`. |
| `specify` | Generar spec runtime local. | Objetivo y criterios del WorkOrder. | `spec.md`. | `spec`. |
| `clarify` | Cerrar decisiones operativas. | Scope, side effects, proyecto. | `clarifications.md`. | `clarification`. |
| `checklist` | Registrar checklist crítico. | Controles esperados. | `checklist.md`. | `checklist`. |
| `context` | Construir contexto autorizado. | EvidenceRegistry y fuentes. | `context-pack.json`, `rag-index-manifest.json`. | `context`, `evidence`. |
| `plan` | Escribir plan, políticas de costo y sandbox. | Spec y estado. | `plan.md`, `billing-policy.yaml`, `slo-policy.md`, `sandbox-policy.md`. | `plan_validation`, `dependency`, `sandbox`, `frontend_template`, `factory_skills`. |
| `tasks` | Mapear principios a tareas. | P01-P12. | `tasks.md`. | `tasks`. |
| `analyze` | Revisar drift spec-plan-tasks. | Spec, plan, tasks. | `analyze-report.md`. | `analyze`. |
| `implement` | Materializar bundle en DEV. | Bundle genérico o BrewMaster. | `implementation-report.md`, `diff-report.json`, `dev-materialization-manifest.json`, y BrewMaster artifacts si aplica. | `sandbox`, `policy`, `project_isolation`, `frontend_template`, `factory_skills`. |
| `validate` | Ejecutar validaciones de artefactos, política y BrewMaster. | Artefactos generados, workspace DEV. | `validation-report.json`. | `tests`, `sandbox`, `coverage`, `project_isolation`, `frontend_template`, `factory_skills`, `brewmaster_functional_coverage`. |
| `security` | Escanear secretos/dependencias/SBOM/MCP. | Run, runtime y proyecto. | `security-review.md`, `secrets-report.json`, `dependency-report.json`, `sbom.json`, `rollback-plan.md`. | `secrets`, `dependency`, `sbom`, `mcp_policy`. |
| `pr_handoff` | Preparar handoff sin PR externo. | Artefactos de corrida. | `PRBundle.md`. | `human_approval`. |
| `deploy_checkpoint` | Registrar bloqueo de deploy. | Permisos del estado. | `deploy-plan.md`. | `rollback`. |
| `observe` | Escribir costos, métricas y completitud de logs. | Budget y logs. | `billing-ledger.json`, `metrics.json`, `log-completeness-report.json`. | `observability`. |
| `close` | Proponer aprendizaje y cerrar trazabilidad. | Estado, claims, memoria. | `memory-report.json`, `Aprendizaje.md`, `ERRORS.md`, `claim-map.md`, `traceability-matrix.md`. | `final_format`, `learning`. |

Dependencias:

- `context` depende de fuentes autorizadas registradas.
- `implement` depende de workspace DEV preparado.
- `validate` depende de artefactos de fases anteriores y del manifiesto de materialización.
- `security` depende de artefactos ya escritos y del árbol de proyecto.
- `close` depende del ledger de fases y claims acumulados.

## 6. Agentes

Los agentes existentes están declarados en `PHASE_AGENTS`. Cada agente existe para representar una estación de trabajo trazable, aunque su implementación actual sea un handler determinista.

| Agente | Fase | Objetivo | Entrada | Salida | Tools declaradas |
|---|---|---|---|---|---|
| `agent.intake` | `intake` | Validar orden y capacidades base. | WorkOrder, presupuesto, workspace. | `work_order.json`. | Ninguna. |
| `agent.constitution` | `constitution` | Instanciar P01-P12. | Catálogo `PRINCIPLES`. | `constitution.md`, `principle-ledger.json`. | Ninguna. |
| `agent.spec_parser` | `specify` | Convertir la orden en spec local. | WorkOrder. | `spec.md`. | Ninguna. |
| `agent.clarifier` | `clarify` | Cerrar decisiones de alcance. | WorkOrder, proyecto, políticas. | `clarifications.md`. | Ninguna. |
| `agent.requirements_qa` | `checklist` | Verificar controles mínimos. | Estado y reglas. | `checklist.md`. | Ninguna. |
| `agent.context_rag` | `context` | Generar contexto mínimo con evidencia. | EvidenceRegistry. | `context-pack.json`, `rag-index-manifest.json`. | Ninguna. |
| `agent.architect_planner` | `plan` | Definir plan y políticas locales. | Spec y estado. | `plan.md`, políticas. | Ninguna. |
| `agent.task_planner` | `tasks` | Convertir principios en tareas. | P01-P12. | `tasks.md`. | Ninguna. |
| `agent.consistency_reviewer` | `analyze` | Revisar coherencia spec-plan-tasks. | Spec, plan, tasks. | `analyze-report.md`. | Ninguna. |
| `agent.implementer` | `implement` | Materializar bundle en DEV. | Bundle, workspace, contrato frontend. | `dev-materialization-manifest.json`, `implementation-report.md`. | `tool.sandbox.dev_materialize`. |
| `agent.qa` | `validate` | Validar artefactos, política y BrewMaster. | Run artifacts, workspace DEV. | `validation-report.json`. | `tool.policy.static`, `tool.validation.artifacts`. |
| `agent.security` | `security` | Ejecutar controles de seguridad. | Run, runtime, proyecto. | `security-review.md`, reports. | `tool.security.secrets`, `tool.security.deps`, `tool.sbom.generate`. |
| `agent.integrator_pr` | `pr_handoff` | Preparar handoff sin escribir PR externo. | Artefactos. | `PRBundle.md`. | Ninguna. |
| `agent.release_sre` | `deploy_checkpoint` | Bloquear o documentar deploy. | Permisos. | `deploy-plan.md`. | Ninguna. |
| `agent.observability_cost` | `observe` | Registrar costos, métricas y logs. | Budget y logs. | `billing-ledger.json`, `metrics.json`. | Ninguna. |
| `agent.close` | `close` | Cerrar memoria, claims y trazabilidad. | Estado, claims, memoria. | `final-report.json`, trazabilidad. | Ninguna. |

Restricciones comunes:

- todos los agentes deben estar allowlisted;
- todos reciben memoria filtrada project-scoped;
- MCP está denegado por defecto;
- no hay escritura externa ni deploy por defecto;
- los claims críticos deben estar asociados a evidencia registrada.

Interacción entre agentes:

- No se comunican entre sí de forma directa.
- Intercambian información por `CycleState.outputs`, artefactos escritos y el orden de fases.
- El orquestador pasa `previous_outputs` en el `prompt_input`, pero los handlers actuales leen principalmente estado y archivos internos.

## 7. Herramientas

Las herramientas están definidas en `ToolRegistry` con `default: deny_unregistered_tools`.

| Tool | Propósito | Quién la usa | Entrada | Salida | Limitaciones |
|---|---|---|---|---|---|
| `tool.sandbox.dev_materialize` | Materializar bundles de texto en DEV vía P12/INV. | `agent.implementer`. | Lista de archivos `{path, content}`. | `dev-materialization-manifest.json`. | Máximo 100 archivos, 250 KB por archivo, 1 MB total, solo texto, sin paths absolutos/traversal/backslash/reservados/secretos. |
| `tool.security.secrets` | Detectar patrones locales de secretos. | `agent.security`. | Lista de paths. | `secrets-report.json`. | Heurístico local; no reemplaza scanner empresarial. |
| `tool.security.deps` | Revisar manifiestos de dependencias. | `agent.security`. | Root del repo. | `dependency-report.json`. | No consulta CVE externas; reporta 0 high/critical por política local. |
| `tool.sbom.generate` | Generar SBOM local mínimo. | `agent.security`. | Root del repo. | `sbom.json`. | SBOM simplificado, no CycloneDX/SPDX completo. |
| `tool.policy.static` | Buscar marcadores de política prohibidos en `webforge/*.py`. | `agent.qa`. | Root del repo. | Bloqueantes en `validation-report.json`. | Busca marcadores literales, no hace análisis estático profundo. |
| `tool.validation.artifacts` | Verificar existencia de artefactos requeridos. | `agent.qa`. | Directorio de corrida y lista requerida. | Resultado de completitud. | Presencia de archivos, no semántica profunda. |

Todas las herramientas pasan por `ToolRegistry.run`, que:

- verifica que el tool id esté registrado;
- revisa presupuesto de tool calls;
- ejecuta la función;
- marca `pass` si no hay `blocking_findings`;
- descuenta presupuesto;
- escribe `tool-logs.jsonl`.

## 8. Estado compartido

El estado compartido principal es `CycleState` en `webforge/models.py`. Se serializa continuamente en `state.json`.

Estructura relevante:

| Campo | Uso |
|---|---|
| `run_id`, `cycle_id` | Identidad de corrida y ciclo. |
| `workflow_version`, `phase`, `task_id`, `agent_id` | Ubicación dentro del flujo. |
| `input_hash`, `spec_hash`, `plan_hash`, `tasks_hash` | Hashes de insumos lógicos. |
| `context_pack_id`, `context_pack_hash` | Identidad del contexto autorizado. |
| `policy_version`, `tool_registry_version`, `mcp_registry_version`, `memory_version` | Versiones de controles. |
| `budget_remaining` | Presupuesto restante. |
| `permissions` | Permisos efectivos para lectura/escritura/deploy/memoria. |
| `outputs` | Artefactos producidos por fase. |
| `evidence`, `open_risks`, `blocked_items` | Evidencia acumulada y riesgos. |

Ciclo de vida:

1. `_initial_state` crea estado con permisos default-deny.
2. Antes de cada fase, el orquestador actualiza `phase` y `agent_id`.
3. Cada `PhaseResult` pasa por `_record_phase`.
4. `_record_phase` actualiza `outputs`, evidencia, budget y escribe `state.json`.
5. `_build_final_report` ajusta `state.status` a `complete` o `error`.

Quién escribe:

- solo el orquestador y los mixins de soporte escriben `state.json`;
- los agentes/handlers devuelven `PhaseResult`, no mutan directamente todos los campos;
- algunas fases actualizan hashes específicos (`spec_hash`, `plan_hash`, `tasks_hash`, `context_pack_hash`).

Quién lee:

- el harness lee el estado como dict;
- los handlers consultan `self.state`, `self.work_order`, `self.project_workspace` y artefactos;
- final-report y trazabilidad derivan de `phase_results` y estado.

Reglas de consistencia:

- fase fallida detiene el workflow;
- `complete` requiere fases pass, P01-P12 pass y artefactos finales presentes;
- la memoria compartida con fábrica está denegada;
- los side effects externos están denegados salvo aprobación.

## 9. Gestión de artefactos

La fábrica produce tres familias de artefactos.

Artefactos de corrida (`runs/<run>`):

- estado y trazas: `state.json`, `log.jsonl`, `phase-ledger.json`, `tool-logs.jsonl`, `mcp-invocations.jsonl`;
- evidencia y contexto: `evidence-register.md`, `context-pack.json`, `rag-index-manifest.json`, `claim-map.md`;
- SDD: `constitution.md`, `spec.md`, `clarifications.md`, `checklist.md`, `plan.md`, `tasks.md`, `analyze-report.md`;
- políticas: `approval-matrix.md`, `billing-policy.yaml`, `mcp-policy.yaml`, `mcp-policy.json`, `sandbox-policy.md`, `slo-policy.md`;
- proyecto: `project-isolation-policy.md`, `project-manifest.json`, `project-memory-policy.json`, `project-sandboxes.json`, `frontend-template-policy.md`, `frontend-template-manifest.json`;
- implementación: `implementation-report.md`, `diff-report.json`, `dev-materialization-manifest.json`;
- validación/seguridad: `validation-report.json`, `security-review.md`, `secrets-report.json`, `dependency-report.json`, `sbom.json`;
- entrega/cierre: `PRBundle.md`, `deploy-plan.md`, `rollback-plan.md`, `metrics.json`, `billing-ledger.json`, `memory-report.json`, `Aprendizaje.md`, `ERRORS.md`, `traceability-matrix.md`, `final-report.json`.

Artefactos de proyecto (`project/<project_id>`):

```text
project/<project_id>/
  project-manifest.json
  project-memory-policy.json
  frontend-template-manifest.json
  memory/
  learning/
  versions/<version>/
    version-manifest.json
    frontend/FRONTEND_CONTRACT.md
  sandboxes/
    DEV/
      sandbox-manifest.json
      workspace/
      memory/
      learning/
    QA/
      sandbox-manifest.json
      workspace/
      memory/
      learning/
```

Artefactos BrewMaster generados en DEV:

- documentación: `README.md`, `docs/architecture.md`, `docs/api-contract.md`, `docs/traceability.md`, `docs/test-strategy.md`;
- contratos: `contracts/brewmaster-blueprint.json`, `contracts/coverage.json`, `contracts/permissions.json`, `contracts/domain-model.json`;
- backend: FastAPI, dominio, servicios, modelos SQLAlchemy, Alembic, jobs;
- frontend: React + Bootstrap, catálogo de pantallas y rutas;
- pruebas: `tests/test_domain_rules.py`, `tests/test_contracts.py`.

Validación de artefactos:

- `artifact_check` verifica presencia;
- `json_artifact_has_keys` verifica claves;
- `text_artifact_contains` verifica términos mínimos;
- `markdown_table_status` verifica estados de tablas;
- `final-report.json` vuelve a comprobar artefactos finales requeridos.

## 10. Gates y validadores

Los gates se ejecutan dentro de cada fase. Un `GateResult` incluye:

- `name`;
- `status`;
- `phase`;
- principios P01-P12 asociados;
- evidencia;
- mensaje;
- `validator_id`;
- datos observados.

Consecuencia de falla:

- la fase devuelve `status="error"`;
- el orquestador marca `state.status = "error"`;
- el loop de fases se detiene;
- `final-report.json` queda en `error`.

Validadores implementados:

| Validador | Qué verifica |
|---|---|
| `artifact.text_contains` | Archivo textual existe, supera tamaño mínimo y contiene términos requeridos. |
| `artifact.json_keys` | JSON válido y claves requeridas presentes. |
| `artifact.exists` | Archivos requeridos existentes. |
| `markdown.table_status` | Estados de tablas Markdown están en conjunto permitido. |
| `mcp.default_deny` | Política MCP con `default=deny` y allowlist vacía. |
| `api.no_catch_all_routes` | Ausencia de rutas catch-all `/api/v1/{resource}`. |
| `alembic.operations` | Migración Alembic con `op.create_table` y sin `upgrade(): pass`. |
| `brewmaster.acceptance_gate` | Cobertura BrewMaster y validadores de rutas/migración. |
| `budget.remaining_non_negative` | Presupuesto no negativo. |

Limitación central:

Muchos gates validan estructura, presencia, conteos o marcadores textuales. No prueban comportamiento completo de negocio. Por eso una corrida BrewMaster puede cerrar `complete` aunque el backend generado devuelva metadatos de endpoints en vez de ejecutar casos de uso reales.

## 11. Trazabilidad

La trazabilidad se registra en varias capas:

| Artefacto | Contenido |
|---|---|
| `evidence-register.md` | Fuentes autorizadas con `evidence_id`, path, SHA-256 y resumen. |
| `context-pack.json` | Secciones y snippets redacted de fuentes autorizadas. |
| `rag-index-manifest.json` | Hash/cache del índice de contexto. |
| `log.jsonl` | Una línea por fase con agente, estado y gates. |
| `phase-ledger.json` | Ledger completo de fases, salidas, gates y evidencia. |
| `tool-logs.jsonl` | Tool id, status, gate y hash de salida. |
| `mcp-invocations.jsonl` | Invocaciones MCP permitidas o denegadas. |
| `claim-map.md` | Claims generados y evidencia asociada. |
| `traceability-matrix.md` | Principios P01-P12, gates, evidencia presente/faltante y status. |
| `final-report.json` | Estado final, cobertura de principios, artefactos, proyecto, sandboxes y tools. |

Reconstruir una ejecución completa:

1. Abrir `final-report.json` para conocer status, `run_id`, fases y artefactos finales.
2. Revisar `phase-ledger.json` para ver cada fase, agente, gates y evidencia.
3. Revisar `log.jsonl` para orden cronológico plano.
4. Abrir `evidence-register.md` y `context-pack.json` para saber qué fuentes alimentaron la corrida.
5. Revisar `tool-logs.jsonl` y `mcp-invocations.jsonl` para efectos automatizados.
6. Revisar `dev-materialization-manifest.json` para archivos escritos en DEV.
7. Revisar `traceability-matrix.md` para cobertura P01-P12.

## 12. Integración BrewMaster

La fábrica implementa BrewMaster cuando `is_brewmaster_work_order` encuentra "brewmaster" en objetivo, `project_id`, tipo o `metadata.blueprint`.

Flujo BrewMaster:

```text
WorkOrder BrewMaster
    |
    v
load_brewmaster_spec()
    |
    v
brewmaster_blueprint()
    |
    v
brewmaster_bundle()
    |
    v
DevSandboxMaterializer -> project/brewmaster/sandboxes/DEV/workspace
    |
    v
brewmaster_acceptance_gate()
```

Módulos generadores:

| Módulo | Responsabilidad |
|---|---|
| `brewmaster_spec.py` | Carga y parsea la especificación oficial; extrae casos de uso, pantallas, reglas, validaciones, endpoints, permisos, entidades y RNF. |
| `brewmaster_catalog.py` | Catálogos base de módulos, pantallas, recursos CRUD y endpoints de acción. |
| `brewmaster_blueprint.py` | Construye blueprint canónico y coverage gate. |
| `brewmaster_bundle.py` | Ensambla los archivos generados en un bundle. |
| `brewmaster_backend.py` | Genera FastAPI, respuestas, seguridad básica, dominio, servicios, modelos, sesión, jobs y Alembic. |
| `brewmaster_frontend.py` | Genera React + Bootstrap mínimo, cliente API, rutas y catálogo de pantallas. |
| `brewmaster_docs.py` | Genera README, arquitectura, contrato API, trazabilidad, estrategia de pruebas y permisos. |
| `brewmaster_tests.py` | Genera tests de reglas puras y contratos de rutas/pantallas. |

Backend generado:

- `backend/pyproject.toml` con FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic, PyMySQL, APScheduler, jose, passlib, openpyxl y reportlab.
- `backend/app/main.py` con FastAPI, middleware `X-Request-ID`, health, catálogo de rutas y 40 rutas explícitas.
- `backend/app/domain/rules.py` con reglas puras: stock disponible, positivos/no negativos, ganancia, alerta de stock y costo de lote.
- Servicios simples para inventario, producción, ventas, compras y notificaciones.
- `backend/app/db/models.py` con modelos SQLAlchemy derivados de entidades.
- `backend/alembic/versions/0001_brewmaster_schema.py` con `op.create_table` por entidad e índices básicos.

Limitación backend:

Las rutas explícitas de `main.py` devuelven un payload `ok({...metadata...})` con handler/method/path/source. No llaman servicios, no validan payloads, no abren sesiones SQLAlchemy, no aplican JWT/RBAC real y no persisten cambios.

Frontend generado:

- `frontend/package.json` con Vite, React, Bootstrap, lucide-react.
- `frontend/src/App.jsx` renderiza un índice de módulos y pantallas.
- `frontend/src/routes.js` mapea `SCREENS` a rutas.
- `frontend/src/screens/catalog.js` declara 30 pantallas.

Limitación frontend:

No existen componentes funcionales para las 30 pantallas, formularios, tablas, filtros, routing protegido ni estados de carga/error. El frontend actual es un catálogo visual básico.

Pruebas generadas:

- `test_domain_rules.py`: stock disponible, alerta de stock, ganancia y costo de lote.
- `test_contracts.py`: 40 rutas, `/api/v1`, ausencia de catch-all y 30 pantallas.

Validación BrewMaster actual:

- `runs/brewmaster-latest/brewmaster-coverage.json` reporta 11 módulos, 30 pantallas, 40 endpoints, 40 entidades, 100 validaciones y 42 permisos.
- `runs/brewmaster-latest/dev-materialization-manifest.json` reporta 32 archivos materializados y 0 bloqueantes.
- `runs/brewmaster-latest/validation-report.json` reporta `brewmaster.status = pass`.

Inconsistencias BrewMaster:

- El gate usa los 40 endpoints de la sección F, pero la especificación contiene secciones K con cobertura ampliada. El runtime no genera todos los endpoints complementarios K.6.
- La documentación generada dice que hay rutas protegidas, RBAC, jobs y formularios validados, pero el código generado no implementa esas capacidades.
- La auditoría indica un mapeo incorrecto de pantallas P-25/P-26/P-27 entre spec y catálogo base.
- `complete` para BrewMaster significa "scaffold local con cobertura estructural validada", no "MVP funcional de negocio".

## 13. Flujo completo de ejecución

Ejecución desde una especificación hasta proyecto final:

1. El usuario invoca CLI o script de skill con un WorkOrder.
2. `_load_work_order` carga JSON o construye uno desde argumentos.
3. `WebForgeFactory.run` crea el directorio de salida.
4. Se limpian artefactos conocidos en esa salida.
5. `WorkOrder.from_dict` normaliza objetivo, proyecto, versión, alcance, side effects, criterios, fuentes y presupuesto.
6. `ProjectWorkspace.prepare` crea `project/<project_id>`, versión, memoria, aprendizaje, DEV, QA y contratos frontend.
7. Se registran fuentes autorizadas en `EvidenceRegistry`; si no hay fuente válida, se crea `source-placeholder.md`.
8. Se inicializan `ContextManager`, `MemoryGate`, `BudgetManager`, `MCPGateway`, `PolicyEngine`, `ToolRegistry` y `HarnessRunner`.
9. Se calcula `run_id` por hash estable del WorkOrder y fuentes.
10. Se crea `CycleState` con permisos default-deny.
11. Se escriben artefactos base: evidence register, workflow, MCP policy, approval matrix, tool registry, skill manifest, agent manifest.
12. El orquestador recorre las 16 fases.
13. En cada fase, el harness valida agente y MCP, prepara input y ejecuta handler.
14. El handler escribe artefactos y gates.
15. `_record_phase` actualiza logs, phase ledger y state.
16. Si una fase falla, se detiene el flujo y final-report queda error.
17. En `implement`, si es BrewMaster, se genera blueprint/coverage y se materializan 32 archivos en DEV.
18. En `validate`, se revisan artefactos, política, workspace, skills y aceptación BrewMaster.
19. En `security`, se escanean secretos, dependencias, SBOM y MCP default-deny.
20. En `observe`, se escriben costos, métricas y completitud de logs.
21. En `close`, se propone aprendizaje project-only y se escribe trazabilidad.
22. `_build_final_report` calcula cobertura P01-P12 y artefactos faltantes.
23. Se escribe `final-report.json`, `traceability-matrix.md` y `state.json`.

Comando típico:

```bash
python -m webforge run --project-root . --work-order examples/work_order_factory.json --output runs/latest
```

Comando desde skill:

```bash
python skills/webforge-factory/scripts/webforge_run.py run --project-root . --work-order examples/work_order_factory.json --output runs/latest
```

## 14. Extensibilidad

Agregar un nuevo agente:

1. Agregar una fase nueva a `WORKFLOW_PHASES` o asociarlo a una fase existente.
2. Agregar `AgentSpec` en `PHASE_AGENTS`.
3. Implementar el handler `_phase_<nombre>` en `FactoryPhaseHandlersMixin` o extraer un módulo nuevo.
4. Registrar el handler en `_run_phase`.
5. Definir outputs, gates, principios y evidencia.
6. Agregar pruebas que verifiquen orden, gates, artefactos y final-report.
7. Si usa herramientas, declarar `allowed_tools` y endurecer el harness para hacer cumplir esa lista.

Agregar un workflow:

Hoy el runtime asume un único workflow global. Para agregar otro correctamente habría que:

- parametrizar `WORKFLOW_VERSION`, `WORKFLOW_PHASES`, `PHASE_AGENTS` y `REQUIRED_FINAL_ARTIFACTS`;
- evitar referencias directas a constantes globales en el orquestador;
- separar handlers por workflow;
- versionar `workflow.yaml`;
- agregar tests de compatibilidad y cierre.

Agregar una herramienta:

1. Crear la función determinista.
2. Agregar `ToolSpec` en `ToolRegistry.specs`.
3. Definir gate, timeout y si escribe.
4. Hacer que retorne `blocking_findings`.
5. Loguear por `ToolRegistry.run`.
6. Asociarla a una fase y gate.
7. Actualizar `factory-tool-manifest.json` esperado y tests.

Agregar una nueva fábrica/proyecto específico:

1. Definir cómo se detecta el WorkOrder.
2. Crear módulos tipo `brewmaster_spec`, `blueprint`, `bundle`, `backend`, `frontend`, `docs`, `tests`.
3. Hacer que `_implementation_bundle` seleccione el bundle correcto.
4. Definir contrato frontend obligatorio en `ProjectWorkspace`.
5. Agregar gates de aceptación específicos.
6. Validar que DEV/QA, memoria y manifests sigan aislados.

Modificar el harness correctamente:

- mantener `run_agent` como única puerta de ejecución de agentes;
- no agregar side effects directos;
- mover enforcement de herramientas al harness;
- registrar pre-tool y post-tool gates;
- validar schema de salida de `PhaseResult`;
- propagar evidencia observada en gates;
- actualizar tests de política y trazabilidad.

## 15. Decisiones arquitectónicas

Decisiones principales:

| Decisión | Justificación | Consecuencia |
|---|---|---|
| Runtime local sin dependencias externas root. | Reducir costo, riesgo y variabilidad. | Scans y SBOM son locales y limitados. |
| Workflow fijo SDD. | Reproducibilidad y trazabilidad. | Extender workflows requiere refactor. |
| P01-P12 como principios ejecutables. | Convertir filosofía en gates y evidencia. | Algunos principios se satisfacen por presencia, no por semántica profunda. |
| Project isolation bajo `project/<project_id>`. | Evitar contaminación entre fábrica y proyectos. | Todo proyecto debe aceptar estructura fija. |
| DEV/QA obligatorios. | Separar materialización y revisión. | QA se prepara, pero no recibe promoción automatizada real. |
| Frontend contract obligatorio. | Evitar drift de tecnología frontend. | BrewMaster queda atado a React + Bootstrap. |
| MCP default-deny. | Minimizar efectos externos. | No hay integración MCP real en el flujo actual. |
| ToolRegistry allowlisted. | Herramientas trazables y presupuestadas. | El enforcement por agente aún no está en harness. |
| Materializador DEV único. | Controlar escrituras. | Solo soporta archivos de texto y tamaños acotados. |
| BrewMaster como caso canónico. | Probar fábrica contra una spec concreta. | Se mezcla generación estructural con afirmaciones funcionales. |

La arquitectura funciona como fábrica documental y scaffold local porque todos los pasos tienen rutas, artefactos y gates. Todavía no funciona como fábrica de producto funcional completo porque los gates de negocio y la implementación generada son superficiales.

## 16. Riesgos, deuda técnica y mejoras futuras

Limitaciones actuales:

- BrewMaster generado no implementa funcionalidad real completa.
- Los endpoints FastAPI devuelven metadatos en vez de ejecutar casos de uso.
- El frontend BrewMaster es un índice de pantallas, no una SPA funcional.
- Los modelos SQLAlchemy carecen de relaciones, constraints y checks de dominio.
- Los validadores son mayoritariamente estructurales.
- `HarnessRunner` no hace cumplir `allowed_tools`.
- `FactoryPhaseHandlersMixin` concentra demasiadas responsabilidades.
- Las dependencias generadas usan `latest` o no fijan versiones.
- `dependency_scan` y `secret_scan` son controles locales heurísticos.
- QA sandbox se crea, pero no hay promoción/validación funcional independiente.
- `.git` existe como directorio vacío/incompleto; `git status` falla.
- `runs/brewmaster-final` es histórico y puede no reflejar el estado actual; `runs/brewmaster-latest` es la referencia más reciente observada.

Deuda técnica prioritaria:

1. Cambiar el gate BrewMaster para ejecutar pruebas reales de J.10 contra endpoints, DB y frontend.
2. Implementar auth JWT, RBAC y auditoría reales.
3. Generar CRUD/transacciones con SQLAlchemy sessions.
4. Modelar FKs, uniques, checks, enums e índices funcionales.
5. Corregir catálogo de pantallas P-25/P-26/P-27 y derivar rutas desde spec.
6. Dividir `factory_phases.py` por fase o bounded context.
7. Mover enforcement de tools al harness.
8. Fijar versiones y lockfiles.
9. Introducir tests de integración y E2E.
10. Separar "scaffold verificado" de "MVP funcional" en el status final.

Mejoras futuras posibles:

- workflows versionados y configurables;
- validadores semánticos por módulo;
- sistema de promoción DEV -> QA;
- ejecución opcional de build frontend y migraciones reales;
- SBOM estándar;
- scanner CVE real;
- plantillas o builders tipados en lugar de strings largos;
- interfaz de reporte HTML;
- repo git real con baseline auditable.

## Anexo A. Mapa de archivos del runtime

| Archivo | Rol |
|---|---|
| `webforge/models.py` | Dataclasses de evidencia, WorkOrder, gates, fases y estado. |
| `webforge/workflow.py` | Workflow, agentes y artefactos requeridos. |
| `webforge/orchestrator.py` | WebForgeFactory y ciclo principal. |
| `webforge/harness.py` | AgentSpec y HarnessRunner. |
| `webforge/factory_phases.py` | Handlers de las 16 fases. |
| `webforge/factory_support.py` | Utilidades de artifacts, logs, final-report y trazabilidad. |
| `webforge/project_workspace.py` | Proyecto, versiones, sandboxes y contrato frontend. |
| `webforge/context.py` | Evidencia, context pack y memoria. |
| `webforge/policy.py` | Política, presupuesto, MCP y aprobación. |
| `webforge/tools.py` | Tool registry y herramientas. |
| `webforge/isolation.py` | Materializador DEV. |
| `webforge/validators.py` | Validadores. |
| `webforge/principles.py` | P01-P12. |
| `webforge/capabilities.py` | Skills internas y validación del paquete skill. |
| `webforge/cli.py` | CLI. |
| `webforge/brewmaster_*.py` | Integración BrewMaster. |
| `skills/webforge-factory/SKILL.md` | Skill Codex para operar la fábrica. |
| `skills/webforge-factory/references/operating-rules.md` | Invariantes operativos. |
| `tests/test_webforge_runtime.py` | Suite de regresión del runtime. |

## Anexo B. Comandos útiles

Ejecutar tests del runtime:

```bash
python -m pytest -q -p no:cacheprovider
```

Ver principios:

```bash
python -m webforge principles
```

Ver skills:

```bash
python -m webforge skills --project-root .
```

Ver tools:

```bash
python -m webforge tools --output runs/tool-preview
```

Validar paquete skill:

```bash
python -m webforge doctor --project-root .
```

Ejecutar fábrica:

```bash
python -m webforge run --project-root . --work-order examples/work_order_factory.json --output runs/latest
```

## Anexo C. Interpretación correcta de `complete`

En el runtime actual, `complete` significa:

- todas las fases ejecutadas terminaron en `pass`;
- P01-P12 tienen gates asociados en pass;
- los artefactos finales requeridos existen;
- no se detectaron secretos por el scanner local;
- MCP no tuvo invocaciones no aprobadas;
- el materializador DEV no reportó bloqueantes;
- para BrewMaster se cumplieron conteos y validadores estructurales.

`complete` no significa:

- que BrewMaster esté listo para producción;
- que las rutas ejecuten lógica real de negocio;
- que el frontend tenga pantallas funcionales;
- que la base de datos tenga integridad suficiente;
- que existan pruebas E2E completas;
- que el análisis de supply-chain sea exhaustivo.

Esta distinción es crítica para futuros desarrolladores: WEBFORGE hoy es una base valiosa de fábrica local trazable, con buen marco de control inicial, pero BrewMaster debe tratarse como scaffold avanzado hasta que los gates funcionales y la implementación de dominio sean reforzados.
