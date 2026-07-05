# Frontend template policy

`BREWMASTER_REACT_BOOTSTRAP` es el contrato frontend obligatorio para este proyecto.

- Ningun proyecto puede crear frontend desde una tecnologia distinta a su contrato declarado.
- Todo sandbox DEV y QA debe declarar el mismo contrato y hash.
- Las versiones incrementales deben clonar desde `versions/<version>` manteniendo este contrato.
- Si falta el contrato, sus archivos requeridos o sus manifiestos, el gate `frontend_template` falla.
