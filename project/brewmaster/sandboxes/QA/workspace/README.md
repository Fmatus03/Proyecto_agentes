# BrewMaster HITO-008 Pantallas interactivas

Implementacion incremental generada por WEBFORGE sobre HITO-007.

Alcance conservado: fundamentos, maestros, inventario, Kardex, SMTP local seguro, produccion,
lotes, calidad, mermas, productos terminados, clientes, ventas, reservas, precios por tipo de
cliente, compras, dashboard, reportes, scheduler, equipos, finanzas, metas, respaldos locales,
Docker Compose, proxy Nginx y documentacion EC2/TLS.

Alcance nuevo: las 30 pantallas P-01..P-30 quedan como vistas React + Bootstrap separadas,
navegables, responsivas y conectadas a endpoints `/api/v1` ya aprobados. No se crean endpoints
backend nuevos, no se ejecuta deploy real, no se usan secretos reales ni integraciones externas.
