# BrewMaster MVP

Implementacion base generada por WEBFORGE para el sistema web de gestion de cervecerias artesanales.

El alcance cubre autenticacion JWT, RBAC, auditoria, insumos, proveedores, recetas, produccion,
calidad, mermas, inventario de productos terminados, ventas, reservas, compras, equipos, finanzas,
dashboard, reportes y alertas por correo.

Todas las rutas de API viven bajo `/api/v1`, las eliminaciones son logicas y las acciones de cambio
de estado usan endpoints explicitos como `POST /api/v1/batches/{id}/complete`.
