# Arquitectura BrewMaster HITO-008

Capas:

- FastAPI conserva exactamente el contrato acumulado HITO-007: rutas `/api/v1`, stores locales, reglas y pruebas.
- React + Bootstrap usa Vite (`frontend/index.html`, `frontend/src/main.jsx`) y un shell con navegacion hash para P-01..P-30.
- `frontend/src/api/client.js` encapsula fetch local, token JWT de sesion y errores normalizados sin inventar endpoints.
- `frontend/src/screens/ScreenViews.jsx` declara un componente por pantalla, con loading, error, vacio, datos y formularios validados.
- `frontend/src/routes.js` resuelve rutas estaticas y dinamicas declaradas en `frontend/src/screens/catalog.js`.

Controles:

- HITO-008 no cambia reglas de negocio ni entidades backend.
- Acciones de UI consumen solamente endpoints aprobados bajo `/api/v1`.
- Las pantallas mantienen datos de respaldo visual para no quedar vacias cuando el backend local no esta levantado, mostrando el error observado.
- DEV se promueve a QA solo despues de validadores, gate, build frontend y regresion HITO-001..HITO-007.
