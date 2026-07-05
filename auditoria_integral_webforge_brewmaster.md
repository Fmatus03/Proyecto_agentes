# Auditoria integral de WEBFORGE / BrewMaster

Fecha: 2026-07-05  
Alcance auditado: `fabricas_agentes_ia.md`, `projects/BrewMaster/brewmaster_especificacion_completa.md`, runtime `webforge/`, skill `skills/webforge-factory/`, pruebas, runs y sandbox generado `project/brewmaster/sandboxes/DEV/workspace`.

## 1. Resumen ejecutivo

El repositorio no esta preparado para una evolucion productiva de largo plazo sin redisenio y endurecimiento de gates. La base arquitectonica de la fabrica existe: workflow cerrado, arnes de entrada, politica default-deny, materializador aislado, trazas, manifests y sandboxes DEV/QA. Sin embargo, el resultado BrewMaster es mayormente un scaffold verificable por conteos y presencia de archivos, no una implementacion funcional del dominio definido por la especificacion.

La principal brecha es que los reportes declaran `complete` y cobertura al 100%, pero el codigo generado no implementa autenticacion JWT, RBAC real, CRUD transaccional, persistencia operativa, reportes, jobs ni pantallas funcionales. Esto contradice `brewmaster_especificacion_completa.md`, especialmente J.2, J.4, J.6, J.8, J.9 y J.10.

Pruebas ejecutadas durante la auditoria:

- `python -m pytest -q -p no:cacheprovider`: 17 tests pass.
- `python -m pytest -q -p no:cacheprovider project/brewmaster/sandboxes/DEV/workspace/tests`: 5 tests pass.

Interpretacion: las pruebas pasan, pero su cobertura es insuficiente para sostener las afirmaciones funcionales del sistema.

## 2. Evaluacion arquitectonica

La arquitectura esperada en `fabricas_agentes_ia.md` exige separar modelo, agente y fabrica; mantener un orquestador que enruta y vigila; obligar a que todo efecto pase por arnes; usar estado compartido estructurado; agentes especializados; herramientas deterministicamente gobernadas; validacion independiente; reproducibilidad y handoff auditable.

Cumplimientos relevantes:

- `webforge/orchestrator.py:102-105` ejecuta fases por `HarnessRunner.run_agent(...)`.
- `webforge/workflow.py:6-23` define una ruta SDD cerrada.
- `webforge/isolation.py:124-143` bloquea rutas absolutas, traversal y escapes del workspace DEV.
- `webforge/policy.py:73-114` deja MCP default-deny y registra invocaciones.
- `webforge/project_workspace.py:134-149` crea proyecto, version, DEV/QA, manifests y politicas.

Incumplimientos relevantes:

- `webforge/factory_phases.py:26-792` concentra 767 lineas de generacion, validacion, seguridad, reportes y cierre en una sola clase. Esto mezcla estaciones de trabajo con coordinacion.
- `webforge/factory_phases.py:367-478` y `480-610` materializan y validan desde handlers internos; los "agentes" no son componentes especializados autonomos, sino funciones del mixin.
- `webforge/harness.py:36-98` verifica agente y MCP, pero no hace cumplir `allowed_tools`; las herramientas se invocan directamente desde phase handlers mediante `self.tools.run(...)`.
- `webforge/validators.py:136-157` valida BrewMaster por booleans de cobertura, ausencia de catch-all y migracion no vacia; no valida comportamiento funcional del dominio.

Conclusion arquitectonica: hay una buena armazon operativa, pero todavia no una fabrica agentica madura segun el propio libro. La estructura coordina artefactos; no gobierna trabajo especializado real con contratos de salida suficientemente fuertes.

## 3. Evaluacion funcional BrewMaster

La especificacion oficial exige un sistema web integral: insumos, recetas, produccion, calidad, mermas, inventario, ventas, reservas, compras, equipos, finanzas, dashboard, reportes, alertas, usuarios, roles, permisos, auditoria, jobs y exportaciones.

Brechas criticas:

- `project/brewmaster/sandboxes/DEV/workspace/backend/app/main.py:34-231` define rutas que devuelven metadatos del endpoint; no ejecutan casos de uso, no validan payloads, no abren sesiones, no aplican RBAC y no escriben auditoria.
- No hay rutas reales en `main.py` para `purchase-orders`, `reservations`, `equipment`, `expenses`, `reports`, `settings`, `waste`, `smtp` o `monthly-goals`, aunque la especificacion los exige en casos de uso y J.2/J.9.
- `project/brewmaster/sandboxes/DEV/workspace/frontend/src/App.jsx:5-37` solo lista modulos y pantallas; no existen las 30 pantallas funcionales con formularios, tablas, filtros, estados ni rutas protegidas.
- `project/brewmaster/sandboxes/DEV/workspace/backend/app/services/production.py` devuelve `{"state": "completado", "kardex": "SALIDA_PRODUCCION"}`; no descuenta insumos, no crea producto terminado, no calcula transaccion atomica ni persiste Kardex como exige J.6.
- `project/brewmaster/sandboxes/DEV/workspace/backend/app/services/sales.py` calcula stock restante en memoria, pero no registra venta, lineas, Kardex, auditoria ni locks transaccionales.

Conclusion funcional: BrewMaster esta en estado scaffold/documental avanzado, no MVP funcional verificable.

## 4. Evaluacion del codigo

Fortalezas:

- Uso razonable de dataclasses para contratos internos (`models.py`, `harness.py`, `tools.py`).
- Serializacion estable y hashes para trazabilidad (`utils.py`).
- Materializador con controles de ruta y secreto bien localizados (`isolation.py`).
- Separacion basica entre runtime, politica, herramientas, contexto y workspace.

Deuda principal:

- Clases demasiado grandes: `FactoryPhaseHandlersMixin` 767 lineas, `ProjectWorkspace` 302, `FactorySupportMixin` 285.
- Funciones extensas: `_phase_validate` 131 lineas, `_phase_implement` 112, `WebForgeFactory.run` 99.
- Generacion por strings en `brewmaster_backend.py` y `brewmaster_frontend.py` dificulta testear semantica, formatos y regresiones.
- Los modelos SQLAlchemy generados tienen casi todo nullable y sin relaciones, constraints ni checks.
- Hay documentacion que afirma capacidades no implementadas, por ejemplo `brewmaster_docs.py:12-25` y `28-49`.

## 5. Buenas practicas

SOLID/SRP: incumplido parcialmente. `factory_phases.py` mezcla especificacion, plan, implementacion, validacion, seguridad y cierre.

DRY/KISS: parcialmente cumplido en utilidades y manifests; incumplido en generadores por strings largos y duplicacion conceptual entre blueprint, docs, contracts y workspace.

Clean Architecture: incumplida en BrewMaster generado. La API no llama servicios ni repositorios; no hay capa de aplicacion ni transacciones reales.

Dependency Inversion: debil. El runtime acopla fase concreta a escritura de artefactos; BrewMaster generado no abstrae persistencia ni casos de uso.

Separation of Concerns: parcialmente en runtime; baja en generadores y nula en handlers de API generados.

## 6. Hallazgos por severidad

### Critico

1. Estado `complete` no equivale a implementacion funcional.  
Evidencia: `runs/brewmaster-latest/validation-report.json` marca BrewMaster pass por conteos y archivos; `main.py:34-231` solo devuelve metadatos.  
Impacto: falso positivo de liberacion, riesgo de entregar scaffold como MVP.  
Principio incumplido: evidencia verificable, gates por fase, no invencion.  
Correccion: cambiar los gates para ejecutar endpoints reales, migraciones, pruebas de integracion y E2E de J.10.

2. BrewMaster no implementa el alcance MVP oficial.  
Evidencia: J.2 exige 12 bloques funcionales; `main.py` no contiene compras, reservas, equipos, finanzas, reportes, settings, mermas ni SMTP.  
Impacto: la fabrica no puede resolver la problematica BrewMaster.  
Correccion: implementar hitos J.12 con casos de uso reales, no solo catalogos.

3. Persistencia sin integridad de dominio.  
Evidencia: `models.py:7-492` no usa `ForeignKey`, `UniqueConstraint` ni `CheckConstraint`; la migracion solo crea tablas e indices por estado/created_at.  
Impacto: permite datos invalidos, rompe reglas V001-V100 y transacciones criticas.  
Correccion: generar modelo relacional con FKs, uniques por empresa, checks numericos, enums de estado e indices especificados.

### Alto

4. Autenticacion, RBAC y auditoria no estan cableados.  
Evidencia: `main.py` no usa dependencias de seguridad; `security.py` tiene helpers aislados; `auth/login` solo retorna metadata.  
Impacto: incumple RNF-01, RNF-02 y permisos por endpoint.  
Correccion: implementar JWT, refresh, password hashing, middleware de usuario, dependencias RBAC y audit logs.

5. Frontend no materializa las 30 pantallas.  
Evidencia: `App.jsx:21-34` lista pantallas; no hay formularios, tablas, filtros ni routing real.  
Impacto: incumple pantallas P-01..P-30 y RNF-07.  
Correccion: generar componentes por pantalla con formularios, validaciones, navegacion y estados.

6. Mapeo incorrecto P-25/P-26/P-27.  
Evidencia: spec define P-25 formulario orden, P-26 recepcion, P-27 gestion equipos; `catalog.js:147-162` asigna P-25 a `/purchase-orders/:id/receive`, P-26 al modulo Equipos y P-27 a historial.  
Impacto: navegacion y trazabilidad pantalla-requisito quedan corruptas.  
Correccion: derivar rutas desde la especificacion o corregir catalogo base.

7. El arnes no hace cumplir allowlist de herramientas por agente.  
Evidencia: `AgentSpec.allowed_tools` existe en `workflow.py:36-52`, pero `HarnessRunner.run_agent` no valida herramientas; las fases invocan `self.tools.run`.  
Impacto: la politica de minimo privilegio queda declarativa.  
Correccion: mover ejecucion de tools al arnes o exigir contexto de agente al `ToolRegistry`.

8. Validadores demasiado superficiales.  
Evidencia: `validators.py` revisa presencia, strings y conteos; las pruebas generadas solo verifican 40 rutas, 30 pantallas y tres reglas.  
Impacto: defectos funcionales pasan con status pass.  
Correccion: validators semanticos por modulo y suite J.10 ejecutable.

### Medio

9. RAG/contexto es indice de secciones, no recuperacion hibrida.  
Evidencia: `ContextManager.build_minimal_context` recorre todas las secciones y guarda snippets; no hay consulta, ranking, BM25/vectorial ni dedupe.  
Impacto: no cumple plenamente capitulos 9 y 17 de la arquitectura esperada.  
Correccion: implementar recuperador por query/fase con scoring y evidencia minima.

10. Dependencias no reproducibles.  
Evidencia: `frontend/package.json` usa `"latest"`; backend generado declara dependencias sin version; root `pyproject.toml` no declara pytest.  
Impacto: builds futuros pueden romperse o no ser reproducibles.  
Correccion: fijar rangos/versiones y lockfiles por sandbox.

11. Documentacion generada sobredeclara capacidades.  
Evidencia: `docs/architecture.md` afirma rutas protegidas, RBAC, formularios validados y jobs; el codigo no los implementa.  
Impacto: handoff enganoso.  
Correccion: documentar estado real o bloquear cierre si doc y codigo divergen.

12. `runs/brewmaster-final` esta obsoleto frente a `runs/brewmaster-latest`.  
Evidencia: `brewmaster-final/brewmaster-coverage.json` reporta 123 endpoints y fallback; `brewmaster-latest` reporta 40.  
Impacto: confunde auditoria y reproducibilidad.  
Correccion: limpiar/archivar runs historicos o marcar version, fecha y compatibilidad.

13. `.git` esta incompleto.  
Evidencia: no existen `.git/HEAD`, `.git/config` ni `.git/objects`; `git status` falla.  
Impacto: no hay historia local auditable ni baseline de cambios.  
Correccion: inicializar repo real o eliminar `.git` vacio y documentar control de version externo.

### Bajo / Observacion

14. Secret scan y dependency scan son heuristicas locales, no analisis supply-chain real.  
Evidencia: `dependency_scan` declara 0 hallazgos sin consultar base CVE.  
Impacto: util para laboratorio, insuficiente para produccion.  
Correccion: integrar scanner real o etiquetar como control local limitado.

15. Los estados finales cerrados existen, pero casi todo falla como `error`; no se observa `needs_user_input` o `not_answerable` en flujos reales.  
Impacto: menor expresividad operacional.  
Correccion: agregar rutas de bloqueo por falta de evidencia y falta de datos criticos.

## 7. Archivos que requieren refactorizacion

- `webforge/factory_phases.py`: dividir en phase handlers por modulo y validators especializados.
- `webforge/factory_support.py`: separar reporting, traceability, claims y artifact IO.
- `webforge/project_workspace.py`: separar policy/manifests/sandbox preparation.
- `webforge/brewmaster_backend.py`: reemplazar generacion monolitica por templates o builders testeables por tipo de artefacto.
- `webforge/brewmaster_catalog.py`: corregir rutas y evitar fallback como fuente de verdad cuando la spec existe.
- `project/brewmaster/sandboxes/DEV/workspace/backend/app/main.py`: reemplazar handlers metadata por endpoints reales.
- `project/brewmaster/sandboxes/DEV/workspace/backend/app/db/models.py`: redisenar modelo relacional.
- `project/brewmaster/sandboxes/DEV/workspace/frontend/src/App.jsx`: reemplazar indice por aplicacion navegable.

## 8. Componentes que requieren redisenio

- Gates BrewMaster: de conteos a comportamiento.
- Arnes/tool policy: enforce por agente, no solo ToolRegistry global.
- Backend BrewMaster: casos de uso transaccionales, repositorios, DTOs, RBAC, auditoria.
- Frontend BrewMaster: rutas protegidas, pantallas P-01..P-30, formularios y tablas.
- Persistencia: constraints, FKs, enums, indices funcionales y migraciones reales.
- Pruebas: suite J.10 completa con unit, integration y E2E.

## 9. Riesgos tecnicos

- Riesgo de falso cumplimiento por reportes `complete`.
- Riesgo de corrupcion de datos si se usa el schema actual.
- Riesgo de regresiones invisibles por tests de humo.
- Riesgo de drift entre spec, catalogos, docs y codigo generado.
- Riesgo de build no reproducible por dependencias sin version.
- Riesgo de baja escalabilidad del runtime por clases monoliticas.

## 10. Fortalezas

- Buen marco conceptual y documentos fuente completos.
- Workflow SDD cerrado y trazable.
- Proyecto y sandboxes aislados con manifests.
- Materializador DEV con controles de path traversal y secretos.
- MCP default-deny y aprobaciones documentadas.
- Pruebas existentes pasan y cubren invariantes basicos.
- Migracion no vacia y rutas explicitas sin catch-all.

## 11. Recomendaciones priorizadas

1. Cambiar el gate de cierre de BrewMaster: `complete` solo si pasan pruebas de J.10 contra endpoints reales, migracion aplicada y frontend build.
2. Implementar hito 1 de J.12 completo: auth JWT, usuarios, roles, permisos y auditoria.
3. Redisenar schema SQL con constraints y relaciones antes de agregar mas servicios.
4. Implementar casos transaccionales J.6 con SQLAlchemy sessions y tests de integracion.
5. Corregir catalogo de pantallas P-25/P-26/P-27 y generar rutas desde la spec.
6. Dividir `factory_phases.py` en handlers pequenos y validators dedicados.
7. Mover enforcement de `allowed_tools` al arnes.
8. Fijar dependencias y agregar lockfiles.
9. Marcar/limpiar runs obsoletos y recuperar un repositorio git real.

## 12. Nota final

| Area | Nota |
|---|---:|
| Arquitectura | 5.0 |
| Harness | 6.0 |
| Orquestador | 5.0 |
| Agentes | 3.0 |
| Workflows | 7.0 |
| Herramientas | 5.0 |
| Codigo | 5.0 |
| Buenas practicas | 4.0 |
| Mantenibilidad | 4.0 |
| Escalabilidad | 4.0 |
| Calidad general | 4.0 |
| Alineacion con `fabricas_agentes_ia.md` | 5.0 |
| Alineacion con `brewmaster_especificacion_completa.md` | 2.0 |

Nota global: 4.3 / 10.

Justificacion: el repo tiene una base de fabrica local valiosa y varios controles operativos bien encaminados, pero el principal entregable funcional no implementa el dominio BrewMaster. La arquitectura declara los principios correctos, aunque varios gates prueban presencia y conteos en vez de comportamiento. La calidad global es la de un scaffold SDD con buena trazabilidad inicial, no la de un MVP productivo ni la de una fabrica lista para duplicar tamano sin redisenio.
