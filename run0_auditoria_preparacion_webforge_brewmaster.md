# RUN 0 - Auditoria y preparacion WEBFORGE / BrewMaster

Fecha: 2026-07-05  
Alcance: preparar la fabrica para ejecutar BrewMaster por hitos, sin implementar BrewMaster en este run.

## Fuentes revisadas

- `fabricas_agentes_ia.md`: arquitectura de fabrica agentica ARNES-SDD, WorkOrder, orquestador, HarnessRunner, contexto, memoria, politicas, validadores, observabilidad y estados cerrados.
- `projects/BrewMaster/brewmaster_especificacion_completa.md`: alcance MVP, arquitectura objetivo, dominio canonico, API, RNF, pruebas, trazabilidad y ciclo J.12.
- `README.md`, `pyproject.toml`, `webforge/*.py`, `tests/test_webforge_runtime.py`.
- Artefactos historicos en `runs/brewmaster-final` y `runs/brewmaster-latest`.

## Resultado ejecutivo

La fabrica esta operativa y la suite local pasa. La arquitectura principal cumple el modelo ARNES-SDD: el orquestador coordina, el harness es la puerta unica, las herramientas estan allowlisted, MCP queda default-deny, la memoria es project-scoped propose-only, y los proyectos se aislan bajo `project/<project_id>` con sandboxes `DEV` y `QA`.

Durante la auditoria se encontro una desviacion relevante: el runtime tenia 5 hitos BrewMaster, mientras J.12 exige 7. En este RUN 0 se corrigio solo la fabrica, no la app BrewMaster. `webforge/milestones.py` ahora declara los 7 hitos J.12 y la suite incluye una prueba que bloquea regresiones.

## Cumplimiento arquitectonico

| Area | Estado | Evidencia |
|---|---|---|
| WorkOrder y estados cerrados | Cumple | `webforge/models.py` |
| Orquestador separado de ejecucion | Cumple | `webforge/orchestrator.py`, `webforge/workflow.py` |
| Entrada unica por harness | Cumple | `webforge/harness.py` |
| P01-P12 con gates y evidencia | Cumple | `webforge/principles.py`, tests |
| Contexto autorizado y evidencia hash | Cumple parcial | `webforge/context.py`; falta recuperacion semantica top-k real |
| Memoria gobernada | Cumple | `MemoryGate`, project-only propose-only |
| Tools deterministas | Cumple | `webforge/tools.py`; scanners son locales |
| MCP default-deny | Cumple | `webforge/policy.py` |
| Aislamiento proyecto/DEV/QA | Cumple | `webforge/project_workspace.py`, `webforge/isolation.py`, `webforge/sandbox_promotion.py` |
| Contrato frontend BrewMaster | Cumple | React + Bootstrap como contrato obligatorio |
| Validacion BrewMaster | Cumple parcial | conteos, rutas explicitas, Alembic y tests; falta validacion semantica profunda |
| J.12 por hitos | Corregido en RUN 0 | 7 hitos en `default_milestones` |

## Deuda tecnica detectada

1. Los artefactos historicos `runs/brewmaster-final` y `runs/brewmaster-latest` no reflejan todos los artefactos incrementales del codigo actual, por ejemplo `roadmap.json`. Deben regenerarse cuando se inicie la ejecucion real por hitos.
2. La carpeta `.git` existe, pero `git status` desde la raiz no reconoce un repositorio valido. Esto limita trazabilidad por commit y debe resolverse fuera del codigo de fabrica.
3. La validacion BrewMaster aun es principalmente estructural: verifica conteos, endpoints `/api/v1`, ausencia de catch-all, migracion no vacia, contrato frontend y tests generados. Falta validar comportamiento funcional profundo por modulo.
4. El bundle BrewMaster actual es monolitico: una corrida BrewMaster materializa un conjunto amplio de archivos. Para una implementacion estrictamente incremental conviene que cada hito materialice solo su delta o que el gate distinga "presente" de "aceptado".
5. El `dependency_scan` es una revision local de manifiestos, no un analisis CVE real. Es coherente con modo local sin red, pero debe declararse como limitacion.
6. El contexto se indexa por secciones y snippets; no hay ranking semantico/hibrido real todavia.
7. Pytest pasa, pero no puede escribir cache bajo `.pytest_cache` por permisos del entorno. No bloquea la suite.

## Preparacion realizada en RUN 0

- Alineado `webforge/milestones.py` con los 7 hitos oficiales de J.12:
  `Fundamentos`, `Maestros`, `Inventario`, `Produccion`, `Ventas`, `Dashboard`, `Cierre`.
- Agregada prueba de regresion para asegurar IDs `HITO-001` a `HITO-007`, nombres J.12 y dependencias lineales.
- Ejecutada suite local con runtime empaquetado: `21 passed`.

## Plan de implementacion basado en J.12

| Hito | Nombre | Objetivo de implementacion | Gate minimo antes de avanzar |
|---|---|---|---|
| HITO-001 | Fundamentos | Auth JWT, usuarios, roles, permisos, auditoria y estructura base | contratos de seguridad, rutas base, tests de contratos |
| HITO-002 | Maestros | Proveedores, insumos, bodegas, recetas y tipos de presentacion | dominio canonico, catalogos, pantallas y API trazadas |
| HITO-003 | Inventario | Entradas de insumos, Kardex, notificaciones email y SMTP | transacciones de stock, cola de notificaciones, reglas de alerta |
| HITO-004 | Produccion | Lotes, calidad, mermas e inventario de productos terminados | descuento atomico, costos, snapshots y pruebas de reglas |
| HITO-005 | Ventas | Clientes, ventas, reservas, precios por tipo de cliente y ordenes de compra | stock disponible, Kardex, ganancias, compras/recepcion |
| HITO-006 | Dashboard | KPIs reales, graficos, alertas operacionales y reportes exportables | consultas agregadas, exports diferidos, permisos |
| HITO-007 | Cierre | Equipos, finanzas, metas, backups, documentacion y pruebas | evidencia integral, regresion, documentacion y cierre SDD |

## Gate de salida RUN 0

Estado: listo para iniciar HITO-001, con reservas.

No se implemento BrewMaster en este run. La siguiente corrida debe seleccionar explicitamente `project_id=BrewMaster` y `milestone_id=HITO-001`, regenerar evidencia incremental actualizada, y no declarar avance a HITO-002 hasta que el gate de HITO-001 quede aprobado.
