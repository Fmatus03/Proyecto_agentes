# Auditoria de evolucion incremental WEBFORGE

Fecha: 2026-07-05  
Objetivo: evolucionar WEBFORGE desde una fabrica SDD de corrida completa hacia una fabrica agentica incremental basada en hitos.

## 1. Auditoria previa

Capacidades existentes antes del cambio:

- Workflow SDD cerrado en `webforge/workflow.py`.
- Orquestador local en `webforge/orchestrator.py`.
- Harness obligatorio para agentes en `webforge/harness.py`.
- Proyecto aislado en `project/<project_id>` con versiones, memoria, aprendizaje y sandboxes DEV/QA.
- Materializador DEV con controles de ruta, tamano y secretos.
- Tool registry allowlisted.
- Trazabilidad por `state.json`, `log.jsonl`, `phase-ledger.json`, `traceability-matrix.md` y `final-report.json`.
- Integracion BrewMaster con blueprint, bundle, backend, frontend, docs y tests estructurales.

Brechas detectadas:

- No existia roadmap persistente por proyecto.
- No existia ejecucion seleccionable por hito.
- No habia estado persistente de hito.
- DEV y QA existian, pero no habia promocion DEV -> QA.
- `allowed_tools` estaba declarado en `AgentSpec`, pero no se aplicaba en runtime.
- No habia gate incremental que decidiera avance de hito.
- La regresion entre hitos no tenia representacion persistente.

## 2. Cambios implementados

### Roadmap e hitos

Se agrego `webforge/milestones.py`.

Responsabilidades:

- generar `ROADMAP.md` y `roadmap.json` por proyecto;
- modelar `MilestoneSpec`;
- seleccionar `--milestone`;
- persistir estado en `project/<project_id>/milestones/<hito>/milestone-state.json`;
- escribir evidencia de hito;
- validar artefactos esperados;
- registrar gate de hito;
- registrar trazabilidad incremental;
- producir reporte de regresion.

Artefactos nuevos por corrida:

- `roadmap.md`
- `roadmap.json`
- `milestone-plan.json`
- `milestone-state.json`
- `milestone-validation-report.json`
- `milestone-gate-report.json`
- `milestone-evidence.md`
- `regression-report.json`
- `incremental-traceability.md`

### CLI por hitos

Se extendio `webforge/cli.py`:

- `--project` como alias de `--project-id`;
- `--milestone HITO-001`;
- override de `project_id`, `project_version` y `milestone_id` sobre WorkOrders JSON cuando el usuario lo indica.

Ejemplo:

```bash
python -m webforge run --project-root . --project brewmaster --milestone HITO-001 --objective "Implementar BrewMaster por hitos"
```

### Estado persistente

Se extendio `WorkOrder` con `milestone_id`.

Se extendio `ProjectWorkspace` con:

- `milestones_root`;
- politica/documentacion indicando `ROADMAP.md`;
- validacion de existencia del directorio de hitos.

### DEV -> QA

Se agrego `webforge/sandbox_promotion.py`.

Responsabilidades:

- copiar archivos desde `sandboxes/DEV/workspace` hacia `sandboxes/QA/workspace`;
- bloquear promocion si la validacion previa falla;
- preservar archivos reservados de contrato frontend;
- emitir `qa-promotion-report.json`;
- mantener escrituras dentro del proyecto.

### Gobernanza de herramientas

Se reforzo `webforge/harness.py` y `webforge/tools.py`.

Antes:

- `AgentSpec.allowed_tools` existia, pero no se aplicaba.

Ahora:

- `HarnessRunner` activa un scope de agente en `ToolRegistry`;
- `ToolRegistry.run` bloquea herramientas fuera de `allowed_tools`;
- `tool-logs.jsonl` registra eventos `pre` y `post`;
- cada tool log incluye agente, fase y allowlist efectiva.

### Validacion y gates incrementales

Se extendio `webforge/factory_phases.py`:

- `intake` valida que el hito solicitado exista;
- `validate` ejecuta validacion de hito;
- si DEV pasa, promueve DEV -> QA;
- genera reporte de regresion;
- genera gate de hito;
- el estado final del hito queda `approved` o `rejected`.

## 3. Nueva arquitectura

```text
WorkOrder + --milestone
    |
    v
ProjectWorkspace
    |
    +--> project/<project_id>/ROADMAP.md
    +--> project/<project_id>/milestones/<hito>/milestone-state.json
    |
    v
Workflow SDD existente
    |
    v
Implementacion en DEV
    |
    v
Milestone validators
    |
    v
Milestone gate
    |
    +-- fail --> hito rejected, QA bloqueado
    |
    v
Promocion DEV -> QA
    |
    v
Regression report
    |
    v
Final report + incremental traceability
```

La arquitectura conserva el orquestador como coordinador. La logica nueva queda separada en modulos pequenos:

- `milestones.py` para roadmap/estado/gates;
- `sandbox_promotion.py` para DEV -> QA;
- `ToolRegistry` para enforcement de herramientas;
- `HarnessRunner` solo activa y desactiva el scope de ejecucion.

## 4. Evidencia de validacion

Pruebas ejecutadas:

```bash
python -m pytest -q -p no:cacheprovider
```

Resultado:

```text
20 passed
```

Pruebas nuevas relevantes:

- hito `HITO-001` crea roadmap, estado persistente y promociona a QA;
- hito desconocido falla cerrado en intake;
- harness bloquea herramientas no permitidas por `allowed_tools`.

## 5. Capacidades nuevas

- WEBFORGE puede representar proyectos como roadmap incremental.
- Una corrida puede seleccionar un hito concreto.
- El hito deja estado persistente.
- El cierre del hito depende de evidencia incremental.
- DEV -> QA existe como flujo real con reporte.
- El harness aplica permisos de herramientas por agente.
- Existe base de regresion entre hitos aceptados.
- La trazabilidad incremental relaciona requisito, hito, agentes, herramientas, artefactos, validadores y gates.

## 6. Limitaciones restantes

- La seleccion por hito todavia reutiliza el workflow SDD completo; no hay todavia un workflow fisicamente reducido por hito.
- BrewMaster todavia materializa un scaffold estructural amplio; falta modularizar el generador para producir bundles estrictamente acotados por hito funcional.
- La regresion por hito verifica estados/evidencia, no ejecuta aun suites historicas completas por modulo.
- El gate incremental decide avance por evidencia, pero los validadores funcionales profundos todavia deben crecer hito a hito.
- No se implemento aprobacion humana explicita entre `validated` y `approved`; `approved` significa aprobado por gate local de fabrica.

## 7. Evaluacion final

| Criterio | Nota |
|---|---:|
| Alineacion con `fabricas_agentes_ia.md` | 8.0 |
| Calidad arquitectonica | 8.0 |
| Mantenibilidad | 8.0 |
| Modularidad | 8.0 |
| Gobernanza | 8.5 |
| Trazabilidad | 8.5 |
| Desarrollo incremental de proyectos complejos | 8.5 |
| Preparacion para implementar BrewMaster por hitos | 8.3 |

Nota global: **8.3 / 10**.

Justificacion: WEBFORGE ya no es solo una fabrica de corrida completa. Ahora tiene las piezas operativas minimas para trabajar por hitos: roadmap, seleccion de hito, estado persistente, evidencia, gate incremental, promocion QA y enforcement real de herramientas. Para llegar a 10/10 aun falta modularizar la generacion de BrewMaster por hito funcional y convertir la regresion en suites ejecutables historicas por modulo.
