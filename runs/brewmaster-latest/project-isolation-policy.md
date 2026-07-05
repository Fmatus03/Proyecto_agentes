# Project isolation policy

Esta politica es obligatoria para todos los proyectos WEBFORGE.

- Todo proyecto vive bajo `project/<project_id>/`.
- Ningun proyecto lee memoria ni aprendizaje persistente de la fabrica.
- Ningun aprendizaje de proyecto se escribe en la memoria de la fabrica.
- Cada proyecto tiene `sandboxes/DEV` y `sandboxes/QA` autonomos.
- DEV y QA son clones independientes de `versions/<version>`.
- Todo proyecto y sandbox declara un contrato frontend obligatorio (`BREWMASTER_REACT_BOOTSTRAP`).
- Las pruebas incrementales salen de versiones `v0001`, `v0002`, ... dentro del proyecto.
- Si falta DEV, QA, memoria aislada, version o contrato frontend, el gate falla.
