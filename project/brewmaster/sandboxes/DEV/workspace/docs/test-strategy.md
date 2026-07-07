# Estrategia de pruebas HITO-008

Regresion HITO-001..HITO-007:

- Hash de contrasena, JWT, RBAC, usuarios, permisos y auditoria siguen activos.
- Maestros, inventario, Kardex, SMTP local, produccion, calidad, mermas y productos terminados siguen activos.
- Clientes, ventas, anulaciones, reservas, precios por tipo, compras, dashboard, reportes, scheduler, equipos y finanzas siguen activos.
- Respaldos automaticos locales y artefactos Docker/proxy/TLS siguen presentes sin deploy real.

Contratos HITO-008:

- ROUTE_CATALOG conserva el acumulado HITO-007 sin endpoints backend nuevos.
- SCREEN_CATALOG declara P-01..P-30 y cada pantalla tiene componente especifico en `ScreenViews.jsx`.
- `App.jsx` usa navegacion hash sobre `routes.js`; rutas dinamicas se materializan con IDs locales de ejemplo.
- `api/client.js` usa exclusivamente `/api/v1`, token local y errores normalizados.
- No existe `GenericScreen` ni fallback placeholder para pantallas declaradas.

Frontend:

- `pnpm build` debe compilar Vite.
- Las 30 pantallas renderizan cabecera, estado de endpoint, datos o vacio profesional y acciones relacionadas.
- Formularios validan campos requeridos y numeros positivos antes de llamar a endpoints aprobados.
- Los errores de backend se muestran sin dejar la pantalla vacia.
